# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstItem(scrapy.Item):
    # Структура единицы информации (item'a) в scrapy
    _id = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
