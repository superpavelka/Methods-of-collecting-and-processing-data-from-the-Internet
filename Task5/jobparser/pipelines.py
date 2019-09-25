# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
import re


class JobparserPipeline(object):  # pipeline (обработчик) item'ов
    def __init__(self):  # Инициализируем подключение к монго
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy  # Создаем БД

    def hh_get_min_salary(self, salary):
        sal_min_1 = re.compile('от [0-9]+')
        # создаем список нижней границы зарплат
        if re.findall(sal_min_1, salary):
            min_salary = re.findall(sal_min_1, salary)
        else:
            min_salary = ''
        return min_salary

    def hh_get_max_salary(self, salary):
        sal_max_1 = re.compile('до [0-9]+')
        # создаем список верхней границы зарплат
        if re.findall(sal_max_1, salary):
            max_salary = re.findall(sal_max_1, salary)
        else:
            max_salary = ''
        return max_salary

    def hh_clean_min_salary_text(self, salary):
        # чистим список нижней границы от ненужных символов
        min_salary = re.sub('от ', "", str(salary))
        return min_salary

    def hh_clean_max_salary_text(self, salary):
        # чистим список верхней границы от ненужных символов
        max_salary = re.sub('до ', "", str(salary))
        return max_salary

    def sj_get_min_salary(self,salary_lst):
        if (len(salary_lst) > 0):
            min_salary = re.sub('\xa0', "", salary_lst[0])
            min_salary = re.sub('<span>', '', min_salary)
        else:
            min_salary = '0'
        return min_salary

    def sj_get_max_salary(self,salary_lst,min_salary):
        if (len(salary_lst) > 1):
            max_salary = re.sub('\xa0', "", salary_lst[1])
            max_salary = re.sub('<span>', '', max_salary)
        else:
            max_salary = min_salary
        return max_salary

    def process_item(self, item, spider):  # обрабатываем наш item
        # создаем список элементов с информациям по зарплатам
        if (item['source']== 'hh.ru'):
            salary = re.sub('\xa0', "", item['min_salary'])
            min_salary = self.hh_get_min_salary(salary)
            max_salary = self.hh_get_max_salary(salary)
            item['min_salary'] = self.hh_clean_min_salary_text(min_salary)
            item['max_salary']= self.hh_clean_max_salary_text(max_salary)
        elif (item['source']== 'superjob.ru'):
            salary = re.findall('<span>[0-9]+\s[0-9]+', item['min_salary'])
            item['min_salary'] = self.sj_get_min_salary(salary)
            item['max_salary'] = self.sj_get_max_salary(salary, item['min_salary'])

        collection = self.mongo_base[spider.name]  # создаем коллекцию по имени паука
        collection.insert_one(item)  # Добавляем item в коллекцию
        return item
