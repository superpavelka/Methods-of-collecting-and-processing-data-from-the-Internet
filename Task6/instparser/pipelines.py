# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient

class InstparserPipeline(object):  #pipeline (обработчик) item'ов
    def __init__(self):     #Инициализируем подключение к монго
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.instagram #Создаем БД

    def process_item(self, item, spider): #обрабатываем наш item
        collection = self.mongo_base[spider.name] #создаем коллекцию по имени паука
        collection.insert_one(item) #Добавляем item в коллекцию
        return item