# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HousePriceDetail(scrapy.Item):
    """
    詳細ページにある情報を保存する
    """
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    madori_detail = scrapy.Field()
    ekitoho = scrapy.Field()
    syozaiti = scrapy.Field()
    kaidate = scrapy.Field()
    sonpo = scrapy.Field()
    nyukyo = scrapy.Field()
    zyoken = scrapy.Field()
    keiyaku_kikan = scrapy.Field()
    tyukai_tesuryo = scrapy.Field()
    syokihi = scrapy.Field()
    syohiyo = scrapy.Field()
    kozo = scrapy.Field()
    tikunengetu = scrapy.Field()
    tyusyazyo = scrapy.Field()
    others = scrapy.Field()

class HousePriceList(scrapy.Item):
    """
    リストページにある情報を保存する
    """
    # title = scrapy.Field()
    url = scrapy.Field()
    detail_url=scrapy.Field()
    madori = scrapy.Field()
    menseki = scrapy.Field()
    yatin = scrapy.Field()
    shikikin = scrapy.Field()
    reikin = scrapy.Field()
    kanrihi = scrapy.Field()
