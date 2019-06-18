# -*- coding: utf-8 -*-
import scrapy,re
from xcfproject.items import XcfprojectCaiPuItem,XcfprojectCategoryItem

class XcfoneSpider(scrapy.Spider):
    name = 'xcfone'
    allowed_domains = ['xiachufang.com']
    start_urls = ['https://www.xiachufang.com/category/']

    # 这里使用custom_settings自定义每一个爬虫文件
    # 设置项，会覆盖掉settings.py文件中的设置参数
    custom_settings = {
        'ROBOTSTXT_OBEY': False
    }

    def parse(self, response):
        """
        目标：
        :param response:
        :return:
        """
        print(response.status, response.url)
        # 获取菜单单分类的url地址
        category_as = response.xpath('//div[@class="cates-list clearfix has-bottom-border pb20 mb20"]//ul/li/a')
        # （url, 名称，分类的id）
        for a_tag in category_as:
            item = XcfprojectCategoryItem()
            # 名称
            item['title'] = a_tag.xpath('./text()').extract_first('')
            # url
            item['url'] = response.urljoin(a_tag.xpath('./@href').extract_first(''))
            # 分类的id
            # http://www.xiachufang.com/category/1807/
            pattern = re.compile('\d+', re.S)
            item['id'] = int(re.search(pattern, item['url']).group())

            yield item

            yield scrapy.Request(
                url=item['url'],
                callback=self.parse_category_page_list,
                meta={'tagId': item['id']}
            )

    def parse_category_page_list(self, response):

        # 获取菜单列表数据，提取详情url地址
        caipu_urls = response.xpath('//ul[@class="list"]/li//p[@class="name"]/a/@href').extract()
        for caipu_url in caipu_urls:
            caipu_url = response.urljoin(caipu_url)
            yield scrapy.Request(
                url=caipu_url,
                callback=self.parse_caipu_detail,
                meta={'tagId': response.meta['tagId']}
            )

    def parse_caipu_detail(self, response):
        # 详情页我们还需要获取如下字段
        """
        标题
        封面
        综合评分
        做菜人数
        菜谱发布人
        菜谱的用料 (获取到后，拼接为一个字符串）
        菜谱的做法（将步骤拼接为一个字符串）
        小贴士内容
        菜谱详情url地址
        :param response:
        :return:
        """
        # 分类id
        item = XcfprojectCaiPuItem()
        item['tagId'] = response.meta['tagId']
        # print(item['tagId'],'在这里解析菜谱详情',response.url)

        # 标题
        # title = response.xpath('//h1[@class="page-title"]/text()').extract_first('')
        item['name'] = response.css('h1.page-title ::text').extract_first('').replace('\n', '').replace(' ', '')

        # 图片地址
        # coverImage = response.xpath('//div[@class="cover image expandable block-negative-margin"]/img/@src').extract_first('')
        item['coverImage'] = response.css(
            'div.cover.image.expandable.block-negative-margin > img ::attr(src)').extract_first('')

        # 综合评分
        item['score'] = float(
            response.xpath('//div[@class="score float-left"]/span[@class="number"]/text()').extract_first(
                '0.0'))

        # 做菜人数
        item['doitnum'] = int(response.xpath(
            '//div[@class="cooked float-left"]/span[@class="number"]/text()').extract_first('0'))

        # 菜谱发布人
        item['author'] = response.xpath('//div[@class="author"]/a[1]/span/text()').extract_first('')

        # 菜谱的用料
        # 对吓：8只;对吓：8只;对吓：8只;对吓：8只;对吓：8只
        tr_list = response.css('div.ings tr')
        used_list = []
        for tr in tr_list:
            name = ''.join(tr.css('td.name ::text').extract()).replace('\n', '').replace(' ', '')
            value = ''.join(tr.css('td.unit ::text').extract()).replace('\n', '').replace(' ', '')
            if len(value) == 0:
                value = '若干'
            used_list.append(name + ':' + value)
        item['used'] = '; '.join(used_list)

        # 菜谱的做法
        item['methodway'] = '->'.join(response.css('div.steps p.text ::text').extract())

        # 小贴士内容
        item['tipNote'] = ''.join(response.css('.tip-container > div ::text').extract()).replace('\n', '').replace(' ','')
        # 详情的url地址
        item['url'] = response.url
        # 将item交给管道
        yield item