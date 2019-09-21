# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem
import re

class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?text=pilot&area=113&st=searchVacancy']

    def get_min_salary(self, salary):
        sal_min_1 = re.compile('от [0-9]+')
        # создаем список нижней границы зарплат
        if re.findall(sal_min_1, salary):
            min_salary = re.findall(sal_min_1, salary)
        else:
            min_salary = ''
        return min_salary

    def get_max_salary(self, salary):
        sal_max_1 = re.compile('до [0-9]+')
        # создаем список верхней границы зарплат
        if re.findall(sal_max_1, salary):
            max_salary = re.findall(sal_max_1, salary)
        else:
            max_salary = ''
        return max_salary

    def clean_min_salary_text(self, salary):
        # чистим список нижней границы от ненужных символов
        min_salary = re.sub('от ', "", str(salary))
        return min_salary

    def clean_max_salary_text(self, salary):
        # чистим список верхней границы от ненужных символов
        max_salary = re.sub('до ', "", str(salary))
        return max_salary

    def parse(self, response: HtmlResponse):  # Метод парсинга - точка входа для паука
        next_page = response.css('a.HH-Pager-Controls-Next::attr(href)').extract_first()  # Ссылка у кнопки "Далее"
        yield response.follow(next_page, callback=self.parse)  # Переход на следующую страницу и вызов самой себя
        # Как только дошли до последней страницы идем дальше по коду
        vacancy = response.css(  # Ищем ссылку на вакансию и добавляем ее в наш список
            'div.vacancy-serp div.vacancy-serp-item div.vacancy-serp-item__row_header a.bloko-link::attr(href)').extract()
        for link in vacancy:  # Переходим по ссылкам на вакансии из полученного списка
            yield response.follow(link, callback=self.vacansy_parse)  # Вызываем метод для сбора инф-ции со страницы

    def vacansy_parse(self, response: HtmlResponse):
        name = response.css('div.vacancy-title h1.header::text').extract_first()  # Наименование вакансии
        salary = response.css('div.vacancy-title p.vacancy-salary::text').extract_first()  # Зарплата
        # создаем список элементов с информациям по зарплатам
        salary = re.sub('\xa0', "", salary)
        min_salary = self.get_min_salary(salary)
        max_salary = self.get_max_salary(salary)
        min_salary = self.clean_min_salary_text(min_salary)
        max_salary = self.clean_max_salary_text(max_salary)
        yield JobparserItem(name=name, min_salary=min_salary,
                            max_salary=max_salary)  # Передаем сформированный item в pipeline

