import os
from os.path import join, dirname
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instparser import settings
from instparser.spiders.instagram import InstagramSpider

do_env = join(dirname(__file__), '.env')
dotenv.load_dotenv(do_env)

#Загружаем переменные из окружения
INST_LOGIN = os.getenv('INST_LOGIN')
INST_PSWRD = os.getenv('INST_PSWRD')

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)

    #Передаем параметры при запуске паука
    process.crawl(InstagramSpider,['geekbrains','andreykirichenko'],INST_LOGIN,INST_PSWRD)
    process.start()