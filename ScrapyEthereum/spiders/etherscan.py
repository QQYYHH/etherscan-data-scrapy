import scrapy
from ..items import BlockItem
from ..items import Block_target_keys

"""
normal: xpath('./div[1]/text()')[0].strip()
"""
# 要爬取的起始 区块号
start_blocknum = 13008648

class EtherscanSpider(scrapy.Spider):
    name = 'etherscan'
    allowed_domains = ['etherscan.io']

    # util p = 520346
    root_url = 'https://etherscan.io/'
    first_url = 'https://etherscan.io/block/'
    start_urls = ['https://etherscan.io/block/' + str(start_blocknum)]
    # start_urls = ['https://etherscan.io/block/' + '232323']

    # 待处理的 url列表
    def start_requests(self):
        urls = []
        cnt = 10 # 控制爬多少条数据
        for i in range(start_blocknum):
            urls.append(self.first_url + str(start_blocknum - i))
            cnt -= 1
            if cnt == 0:
                break
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # 首先获取 区块数据
        item = self.get_block_data(response)
        return item

        
    def get_block_data(self, response):
        print(response)
        item = BlockItem()
        # 返回只有一个元素的列表，获取第一个元素即可
        # // 表示递归查找
        content = response.xpath('//div[@id="ContentPlaceHolder1_maintable"]')[0]
        div_items = content.xpath('.//div[contains(@class, "row align-items-center")]')

        for div_item in div_items:
            key = div_item.xpath('./div[1]/text()').extract()[0].strip()
            if key in Block_target_keys.keys():
                key = Block_target_keys[key]
                if key == 'ts':
                    val = div_item.xpath('./div[2]/text()').extract()[1].strip()
                    item[key] = val
                elif key == 'block_height':
                    val = div_item.xpath('./div[2]/div[1]/span[1]/text()').extract()[0].strip()
                    item[key] = val
                elif key == 'miner':
                    val = div_item.xpath('./div[2]/a/text()').extract()[0].strip()
                    item[key] = val
                elif key in ['block_reward', 'uncle_reward', 'basefee_pergas']:
                    text = div_item.xpath('./div[2]/text()').extract()
                    val = text[0].strip()
                    b = div_item.xpath('./div[2]/b')
                    if len(b) > 0:
                        val += '.' + text[1]
                    item[key] = val
                elif key == 'tx': # 获取 普通交易数 & 内部交易数
                    tx = div_item.xpath('./div[2]/a/text()').extract()
                    tx_num, interal_tx_num = '0', '0'
                    if len(tx) > 0:
                        tx_num = tx[0]
                    if len(tx) > 1:
                        interal_tx_num = tx[1]
                    item['tx_num'] = tx_num
                    item['interal_tx_num'] = interal_tx_num
                elif key == 'pre_hash':
                    val = div_item.xpath('./div[2]/a/text()').extract()[0].strip()
                    item[key] = val
                else:
                    val = div_item.xpath('./div[2]/text()').extract()[0].strip()
                    item[key] = val
        return item 