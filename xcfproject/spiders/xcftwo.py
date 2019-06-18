# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import re
from scrapy_redis.spiders import RedisCrawlSpider
from xcfproject.items import XcfprojectCaiPuItem,XcfprojectCategoryItem
# CrawlSpider:继承自spider,可以定制规则，从页面源码中提取目标地址,
# 内部会自动构建Request请求对象，交给调度器，最终交给下载器执行下载任务

# 1.地址url的提取规则
# 2.设置回调的解析函数
#  - 拦截提取到的url地址
#  - 拦截Request请求对象


class XcftwoSpider(RedisCrawlSpider):
    #爬虫名称
    name = 'xcftwo'
    #设置允爬取的域
    allowed_domains = ['xiachufang.com']
    #设置起始url地址
    # start_urls = ['http://www.xiachufang.com/category/']
    redis_key = 'xcftwo:start_urls'
    #rules：列表或元组，存放的是Rule对象
       #  Rule：
       #   link_extractor, 是一个对象，定义链接的提取规则和提取范围,符合
       #   规则的url地址会被提取出来,并且scrapy会自动发起请求
       #   callback = None, 回调函数,设置任务下载完成后的回调
       #   follow = None, 是否跟进
       #   process_links = None, 设置函数,拦截提取到的url地址
       #   process_request = identity,设置函数,拦截Request请求对象

       # link_extractor
       #   allow = (), 元组或列表,定义正则规则，提取url地址，发起请求
       #   deny = (), 元组或列表,定义正则规则，提取url地址,提取的url地址一定不会请求
       #   allow_domains = (),#元组或列表,设置允爬取的域
       #   deny_domains = (), #元组或列表,设置不允爬取的域
       #   restrict_xpaths = () #根据xpath路径，确定提取链接的模块（范围）
       #   restrict_css=()


    rules = (
        #定义规则，提取分类的url地址
        #http://www.xiachufang.com/category/20167/
        Rule(
            LinkExtractor(
                allow=r'.*?/category/\d+/$',
                restrict_xpaths='//div[@class="block-bg p40 font16"]'
            ),
           # callback='parse_item',
            process_links= 'get_links',
            process_request= 'get_request',

            follow=True,
        ),
        #提取分类列表页中的菜谱详情url地址
        #http://www.xiachufang.com/recipe/100232976/
        #http://www.xiachufang.com/recipe/102228399/
        Rule(
            LinkExtractor(
                allow=r'.*?/recipe/\d+/$',
            ),
            callback='parse_caipu_detail',
            follow=True
        ),
        # 提取分类中下一页的url地址
        # http://www.xiachufang.com/category/52411/?page=3
        Rule(
            LinkExtractor(
                allow=r'.*?category/\d+/?page=\d+'
            ),
            follow=True
        )
    )

    def get_links(self,links):
        #可以在这里拦截links，提取到的url地址
        # print(links)
        for link in links:
            link.url = link.url + ''
        #print(links)
        return links

    def get_request(self,request):
        #可以在这过滤Request对象
        # print(type(request))
        # print(request.url)
        return request

    def parse_start_url(self, response):
        """在这个函数中可以获取起始任务的响应结果"""
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
            # print(item)

            yield item


    def parse_item(self, response):
        print(response.status)
        print(response.url)

    def parse_caipu_detail(self,response):
        print(response.request.headers)
        print('菜谱详情请求',response.status)
        print(response.url)
        #解析菜谱详情数据
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
        # item['tagId'] = response.meta['tagId']

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
        item['tipNote'] = ''.join(response.css('.tip-container > div ::text').extract()).replace('\n', '').replace(' ',
                                                                                                                   '')
        # 详情的url地址
        item['url'] = response.url
        # 将item交给管道
        yield item




