# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
import re
import json
from urllib.parse import urlencode, urljoin
from copy import deepcopy
from instparser.items import InstItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    graphql_url = 'https://www.instagram.com/graphql/query/?'  # url для формирования ссылки на пользователя в правильном виде
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    variables_base = {'fetch_mutual': 'false', "include_reel": 'true', "first": 100}
    followers = {}  # Словарь для подписчиков

    def __init__(self, user_links, login, pswrd, *args, **kwargs):
        self.user_links = user_links
        self.login = login
        self.pswrd = pswrd
        self.query_hash = 'c76146de99bb02f6415203be841dd25a'  # Секретный хеш :)
        super().__init__(*args, **kwargs)  # Супер класс

    def parse(self, response: HtmlResponse):  # Точка входа, отсюда начинаем
        csrf_token = self.fetch_csrf_token(response.text)  # Форимруем другой токен из логина,пароля и секретного хеша
        yield scrapy.FormRequest(
            'https://www.instagram.com/accounts/login/ajax/',  # Запрос сюда чтобы авторизоваться
            method='POST',
            callback=self.parse_users,  # Идем на 2-ой шаг
            formdata={'username': self.login, 'password': self.pswrd},
            headers={'X-CSRFToken': csrf_token}
        )

    # 2-ой шаг проверяем авторизацию и переходим по ссылке из списка пользователей
    def parse_users(self, response: HtmlResponse):
        j_body = json.loads(response.body)
        if j_body.get('authenticated'):
            for user in self.user_links:  # Перебираем список user_links
                # Формируем ссылку на пользователя и переходим по ней
                yield response.follow(urljoin(self.start_urls[0], user),
                                      callback=self.parse_user,  # 3-ий шаг
                                      cb_kwargs={'user': user})

    # 3-ий шаг, делаем копию полученного пользователя
    def parse_user(self, response: HtmlResponse, user):
        #post = response.css('div.Nnq7C div.v1Nh3').extract()
        #post = response.xpath('//div[contains(@class, "v1Nh3")]').getall()
        user_id = self.fetch_user_id(response.text, user)  # Получаем id пользователя
        user_vars = deepcopy(self.variables_base)  # Копия здесь
        user_vars.update({'id': user_id})  # Добавляем id в контейнер пользователя
        yield response.follow(self.make_graphql_url(user_vars),  # Форимруем ссылку на пользователя с помощью graphql
                              callback=self.parse_followers,  # 4-ый шаг
                              cb_kwargs={'user_vars': user_vars, 'user': user})

    # Собираем информацию о подписчиках
    def parse_followers(self, response: HtmlResponse, user_vars, user):
        data = json.loads(response.body)
        # Проверяем повторно ли обращаемся к followers
        if not self.followers.get(user):  # Если первый раз
            self.followers[user] = {'followers': data.get('data').get('user').get('edge_followed_by').get('edges'),
                                    'count': data.get('data').get('user').get('edge_followed_by').get('count'),
                                    }
        else:  # Если повторно
            self.followers[user]['followers'].extend(data.get('data').get('user').get('edge_followed_by').get('edges'))

        # Проверяем на наличие следующей страницы подписчиков
        if data.get('data').get('user').get('edge_followed_by').get('page_info').get('has_next_page'):
            user_vars.update(
                {'after': data.get('data').get('user').get('edge_followed_by').get('page_info').get('end_cursor')})
            next_page = self.make_graphql_url(user_vars)  # Формируем новую ссылку на следующую страницу

            yield response.follow(next_page, callback=self.parse_followers,  # Продолжаем собирать подписчиков
                                  cb_kwargs={'user_vars': user_vars, 'user': user})

        # Ели собрали всех подписчиков
        if self.followers.get(user) and self.followers.get(user).get('count') == len(
                self.followers.get(user).get('followers')):
            yield InstItem(name=user, url=urljoin(self.start_urls[0], user))

    def fetch_user_id(self, text, username):
        """Используя регулярные выражения парсит переданную строку на наличие
        `id` нужного пользователя и возвращет его."""
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')

    def fetch_csrf_token(self, text):
        """Используя регулярные выражения парсит переданную строку на наличие
        `csrf_token` и возвращет его."""
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def make_graphql_url(self, user_vars):
        """Возвращает `url` для `graphql` запроса"""
        result = '{url}query_hash={hash}&{variables}'.format(
            url=self.graphql_url, hash=self.query_hash,
            variables=urlencode(user_vars)
        )
        return result
