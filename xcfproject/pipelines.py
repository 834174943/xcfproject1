# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

class XcfprojectPipeline(object):
    def __init__(self, host, user, pwd, db, port, charset):
        # mysql链接
        # self.client = pymysql.Connect(
        #     '127.0.0.1','root','ljh1314',
        #     'class1809',port=3306,charset='utf8'
        # )
        self.client = pymysql.Connect(
            host, user, pwd,
            db, port=port, charset=charset
        )
        # 游标
        self.cursor = self.client.cursor()

    @classmethod
    def from_settings(cls, settings):
        """
        from_settings类方法实现的目的：为了从settings.py文件中获取设置信息
        :param settings:
        :return:
        """
        MYSQL_HOST = settings['MYSQL_HOST']
        MYSQL_USER = settings['MYSQL_USER']
        MYSQL_PWD = settings['MYSQL_PWD']
        MYSQL_DB = settings['MYSQL_DB']
        MYSQL_PORT = settings['MYSQL_PORT']
        MYSQL_CHARSET = settings['MYSQL_CHARSET']

        return cls(MYSQL_HOST, MYSQL_USER, MYSQL_PWD,
                   MYSQL_DB, MYSQL_PORT, MYSQL_CHARSET)

    # 最优解
    def process_item(self, item, spider):
        data = dict(item)
        sql, insert_data = item.get_sql_and_data(data)

        try:
            self.cursor.execute(sql, list(data.values()))
            self.client.commit()
            print('插入成功')
        except Exception as err:
            print(err)
            self.client.rollback()

        return item

