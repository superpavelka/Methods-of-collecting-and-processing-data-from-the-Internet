# -*- coding: utf-8 -*-

import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem
import re


class SjSpider(scrapy.Spider):
    name = 'sj'
    allowed_domains = ['https://www.superjob.ru']
    start_urls = ['https://www.superjob.ru/vakansii/programmist.html']

    def parse(self, response: HtmlResponse):  # Метод парсинга - точка входа для паука
        next_page = response.css('a.f-test-link-dalshe::attr(href)').extract_first()  # Ссылка у кнопки "Далее"
        yield response.follow(next_page, callback=self.parse,
                              dont_filter=True)  # Переход на следующую страницу и вызов самой себя
        # Как только дошли до последней страницы идем дальше по коду
        vacancy = response.css(
            'a.icMQ_._3dPok._1QIBo::attr(href)').extract()
        for link in vacancy:  # Переходим по ссылкам на вакансии из полученного списка
            link = 'https://www.superjob.ru' + link
            yield response.follow(link, callback=self.vacansy_parse,
                                  dont_filter=True)  # Вызываем метод для сбора инф-ции со страницы

    def vacansy_parse(self, response: HtmlResponse):
        name = response.css('h1.rFbjy::text').extract_first()  # Наименование вакансии
        salary = response.css('span._2Wp8I').extract_first()  # Зарплата
        url = response.request.url
        source = 'superjob.ru'
        yield JobparserItem(name=name, min_salary=salary, max_salary=salary, url=url,
                            source=source)  # Передаем сформированный item в pipeline
