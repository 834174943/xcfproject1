# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class XcfprojectCategoryItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class XcfprojectCategoryItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 名称
    title = scrapy.Field()
    # url
    url = scrapy.Field()
    # id
    id = scrapy.Field()

    def get_sql_and_data(self,data):
        """
        data字典类型的数据
        :param data:
        :return:
        """
        # sql = """
        # INSERT INTO category (%s)
        # VALUES (%s)
        # """ % (
        #     ','.join(data.keys()),
        #     ','.join(['%s']*len(data))
        # )
        # insert_data = list(data.values())
        #
        # return sql,insert_data
        return sql_and_data(data,'category')



class XcfprojectCaiPuItem(scrapy.Item):
    # 菜谱名称
    name = scrapy.Field()
    # 封面图片
    coverImage = scrapy.Field()
    # 分类id
    tagId = scrapy.Field()
    # 评分
    score = scrapy.Field()
    # 多少人做过
    doitnum = scrapy.Field()
    # 发布人
    author = scrapy.Field()
    # 用料
    used = scrapy.Field()
    # 做法
    methodway = scrapy.Field()
    # 详情url
    url = scrapy.Field()
    # 小贴士
    tipNote = scrapy.Field()


    def get_sql_and_data(self, data):
        """
        data字典类型的数据
        :param data:
        :return:
        """
        # sql = """
        # INSERT INTO caipu (%s)
        # VALUES (%s)
        # """ % (
        #     ','.join(data.keys()),
        #     ','.join(['%s'] * len(data))
        # )
        # insert_data = list(data.values())
        #
        # return sql, insert_data
        return sql_and_data(data,'caipu')

def sql_and_data(data,tablename):

    sql = """
    INSERT INTO %s (%s)
    VALUES (%s)
    """ % (
        tablename,
        ','.join(data.keys()),
        ','.join(['%s'] * len(data))
    )
    insert_data = list(data.values())

    return sql, insert_data