import scrapy
from scrapy_splash import SplashRequest
from ..items import TxItem
from ..items import Tx_target_keys

start_blocknum = 13034570
default_page_size = 50 # 区块中每页默认交易数


class GetTxSpider(scrapy.Spider):
    name = 'get_tx'
    allowed_domains = ['etherscan.io']
    # splash_args = {'wait': 1, 'proxy': 'http://127.0.0.1:12333'}
    splash_args = {'wait': 0.5}
    first_url = 'https://etherscan.io/txs?block='
    root_txurl = 'https://etherscan.io/tx/'
    # start_urls = ['http://etherscan.io/txs?block=' + str(start_blocknum)]
    start_urls = ['https://etherscan.io/txs?block=13035028&p=1']



    # 调试 交易页面的简单接口
    # def start_requests(self):
    #     url = 'https://etherscan.io/tx/0x70a0d0819acc4d775ec8589a1409a64baa0c230b4b8fdd476dedea862198f5e9/advanced'
    #     yield scrapy.Request(url=url, callback=self.parse_tx)

    def start_requests(self):
        urls = []
        for i in range(start_blocknum):
            urls.append(self.first_url + str(start_blocknum - i) + '&p=1')
        
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    # 第一个parse 获取一个block内每一页的交易列表
    def parse(self, response):
        current_url = response.url
        cur_pgnum = self.get_pgnum(current_url)
        mainrows = response.xpath('//div[@id="ContentPlaceHolder1_mainrow"]')
        if len(mainrows) > 0:
            # 如果获取到，继续
            mainrow = mainrows[0]
            tot_tx_str = mainrow.xpath('.//div[@id="ContentPlaceHolder1_topPageDiv"]/p/span/text()').extract()[1].strip()
            tot_tx = self.get_tx_totalnum(tot_tx_str.split()[3])
            print(current_url, 'total tx num:', tot_tx)
            if tot_tx > 0:
                table = mainrow.xpath('.//div[contains(@class, "table-responsive")]/table/tbody')[0]
                trs = table.xpath('./tr')
                # 遍历每一行 具体的交易hash在 第二列
                txhash_list = []
                # 判断当前页是否还有数据
                if len(trs[0].xpath('./td')) > 1:
                    for tr in trs:
                        td = tr.xpath('./td')[1]
                        if len(td.xpath('./span[@class="text-danger"]')) > 0:
                            continue
                        txhash = td.xpath('./span[contains(@class, "hash-tag")]/a/text()').extract()[0].strip()
                        txhash_list.append(txhash)
                    print('current pagenum: ', cur_pgnum, 'txhash_list size is: ', len(txhash_list))

                # 这里 将tx hash列表提取出来，通过 request(url, callback) 回调处理函数                
                for txhash in txhash_list:
                    txurl = self.root_txurl + txhash + '/advanced' # advanced 为了获取全部的interal tx列表
                    yield scrapy.Request(url=txurl, callback=self.parse_tx, dont_filter=True)
                
                # 如果当前页面数据正好有 default_page_size，说明可能仍有下一页数据
                if len(txhash_list) >= default_page_size:
                    yield scrapy.Request(url=self.get_newurl(current_url, cur_pgnum + 1), callback=self.parse, dont_filter=True)
        else:
            # 如果没有获取到，重新获取
            yield scrapy.Request(url=current_url, callback=self.parse, dont_filter=True)
        

        # 可以什么都不返回
        

    # 解析具体交易页面的函数 生成所需的Item
    # special: To, Tokens Transferred
    def parse_tx(self, response):
        url = response.url
        contents = response.xpath('//div[@id="ContentPlaceHolder1_maintable"]')
        if len(contents) > 0:
            content = contents[0]
            rows = content.xpath('./div')
            # 最后两个 div 标签行不用获取
            length = len(rows)
            txitem = TxItem()
            txitem['id'] = 0 # 默认类型为 普通交易
            for i in range(length - 2):
                # 抓取每一行下所有文本信息
                tmp = rows[i].xpath('.//text()').extract()
                res = []
                for s in tmp:
                    s_after = s.strip()
                    if s_after is not '':
                        res.append(s_after)
                for key in Tx_target_keys.keys():
                    if key in res:
                        key = Tx_target_keys[key]
                        if key == 'to':
                            internal_tx_list = self.handle_to(txitem, rows[i], res)
                            # 填充每个interal tx的父亲交易hash，并提交
                            for interal_tx in internal_tx_list:
                                interal_tx['tx_hash'] = txitem['tx_hash']
                                yield interal_tx
                        elif key == 'tk_transfer':
                            token_tx_list = self.handle_token_transfer(rows[i])
                            # 填充每个 token tx 的父亲tx hash 并提交
                            for token_tx in token_tx_list:
                                token_tx['tx_hash'] = txitem['tx_hash']
                                yield token_tx
                        
                        elif key in ['value', 'tx_fee', 'gas_price']:
                            # 需要考虑到小数点
                            if len(res) >= 4 and res[2] == '.':
                                txitem[key] = res[1] + res[2] + res[3]
                            else:
                                txitem[key] = res[1]
                        else:
                            # 正常情况，直接从字符串list - res中读取
                            txitem[key] = res[1]
                        break

            #  还差扩展的 标签没有处理 click to see more !!!!
            ext_rows = content.xpath('./div[@id="ContentPlaceHolder1_collapseContent"]/div')
            for ext_row in ext_rows:
                tmp = ext_row.xpath('.//text()').extract()
                res = []
                for s in tmp:
                    s_after = s.strip()
                    if s_after is not '':
                        res.append(s_after)
                for key in Tx_target_keys.keys():
                    if key in res:
                        key = Tx_target_keys[key]
                        if key in ['basefee_pergas', 'burnt_fee']:
                            # 需要考虑到小数点
                            if len(res) >= 4 and res[2] == '.':
                                txitem[key] = res[1] + res[2] + res[3]
                            else:
                                txitem[key] = res[1]
                        elif key == 'nonce':
                            txitem[key] = res[2]
                            txitem['position'] = res[3] # 收集交易在当前区块中的排名
                        else:
                            txitem[key] = res[1]
                        break

            # 最后提交 txitem
            yield txitem
        else:
            # 如果当前页面没有获取到内容
            # 重新获取
            yield scrapy.Request(url=url, callback=self.parse_tx, dont_filter=True)

    # 将tx 总数转换为 int
    # 当tx总数过多，比如 1,067 不能直接强转
    def get_tx_totalnum(self, tot_tx_str):
        tot_tx_str = tot_tx_str.replace(',', '')
        return int(tot_tx_str)

    # 从url 中获取 页数
    # https://etherscan.io/txs?block=13008648&p=1 也就是获取p
    def get_pgnum(self, url):
        url = str(url).strip()
        i = len(url) - 1
        res = ''
        while i >= 0 and url[i] != '=':
            res += url[i]
            i -= 1
        ans = ''
        i = len(res) - 1
        while i >= 0:
            ans += res[i]
            i -= 1
        return int(ans)

    # 提取最后一个等号之后的字符串
    # 因为 token 接收或者发送账户地址在 href最后一个等号后面
    # 比如：href="/token/0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2?a=0x03f7724180aa6b939894b5ca4314783b0b36b329"
    # 最后 a = xxx，xxx代表是token的 收发地址
    def get_token_account(self, url):
        url = str(url).strip()
        i = len(url) - 1
        res = ''
        while i >= 0 and url[i] != '=':
            res += url[i]
            i -= 1
        ans = ''
        i = len(res) - 1
        while i >= 0:
            ans += res[i]
            i -= 1
        return ans 

    # 生成下一页的url
    def get_newurl(self, url, p):
        i = len(url) - 1
        while i >= 0 and url[i] != '=':
            i -= 1
        return url[0:i] + '=' + str(p)


    # 获取某个标签下的 文本信息
    # 单独写一个函数为了避免 \n等符号的影响
    def get_label_text(self, label):
        str_list = label.xpath('./text()').extract()
        for s in str_list:
            s_after = s.strip()
            if s_after != '':
                return s_after
        return ''

    # 递归获取某个标签下所有的文本信息
    # @ret text list
    def get_recursive_label_text(self, label):
        str_list = label.xpath('.//text()').extract()
        ans = []
        for s in str_list:
            s_after = s.strip()
            if s_after != '':
                ans.append(s_after)
        return ans


    # 填充txitem中的 to字段，同时如果有interal tx，则返回interal tx列表
    # row 代表当前 html中to对应的div标签
    # str_list 是当前row中 提取出来的 所有字符串文本
    # ret 如果有 interal tx，则返回interal tx对应的Item对象列表，否则返回 一个长度为0的列表
    # interal tx返回时，在parse_tx中 填充其 父交易的hash
    def handle_to(self, txitem, row, str_list):
        body = row.xpath('./div')[1]
        if 'Contract' in str_list:
            # 说明是合约调用交易
            txitem['id'] = 1
        
        # 获取当前交易的 to字段
        txitem['to'] = self.get_label_text(body.xpath('./a[@id="contractCopy"]')[0])
        interal_tx_list = []
        # 说明有 interal tx
        # 则切换到 Internal txn 选项卡提取所有internal tx
        if len(body.xpath('./ul')) > 0:
            internal_tx_div = row.xpath('../../../div[2]/div[2]/div[2]')[0]
            trs = internal_tx_div.xpath('./table/tbody/tr')
            for tr in trs:
                internal_tx = TxItem()
                tds = tr.xpath('./td')
                internal_tx['invoke_type'] = self.get_recursive_label_text(tds[0])[0]
                internal_tx['fm'] = self.get_recursive_label_text(tds[1])[0]
                internal_tx['to'] = self.get_recursive_label_text(tds[3])[0]
                tmp = tds[4].xpath('.//text()').extract()
                val = ''
                for s in tmp:
                    s_after = s.strip()
                    if s_after != '':
                        val += s_after
                internal_tx['value'] = val
                internal_tx['gas_limit'] = self.get_label_text(tds[5])
                interal_tx_list.append(internal_tx)
        return interal_tx_list

    # 处理 token tx，返回token tx列表
    # row 代表当前 token tx的行标签
    def handle_token_transfer(self, row):
        # 有时候交易很多，采用滑动查看的格式，这个时候，ul == NULL
        uls = row.xpath('./div[2]/ul')
        if len(uls) == 0:
            # 滑动格式
            uls = row.xpath('.//ul[@id="wrapperContent"]')
        ul = uls[0]
        lis = ul.xpath('./li')
        token_tx_list = []
        for li in lis:
            token_tx = TxItem()
            token_tx['id'] = 3
            spans = li.xpath('./div[1]/span')
            # 从超链接中提取 收发方的账户地址
            token_tx['fm'] = self.get_token_account(spans[1].xpath('./a/@href').extract()[0])
            token_tx['to'] = self.get_token_account(spans[3].xpath('./a/@href').extract()[0])
            # token transfer 有两种情况，一种是交易常规的token
            # 另一种是交易NFT，通常NFT的数量唯一
            if len(spans) <= 5:
                # 交易NFT
                tmp = spans[-1].xpath('./text()').extract()
                ntf_name = ""
                for s in tmp:
                    s_after = s.strip()
                    if s_after is not '':
                        if s_after[-1] == '[':
                            s_after = s_after[:-1]
                        if s_after not in ['[', ']']:
                            ntf_name += s_after
                ntf_name += spans[-1].xpath('./a[1]/text()').extract()[0]
                token_tx['ntf'] = ntf_name
                a = spans[-1].xpath('./a')[1]
                token_tx['token_address'] = a.xpath('./@href').extract()[0][len('/token/'):]
                token_tx['token_name'] = a.xpath('./text()').extract()[0].strip()
                pass
            else:
                token_tx['value'] = spans[5].xpath('.//text()').extract()[0]
                # 填充 token币的官方地址 & 名字
                a = li.xpath('./div/a')[0]
                token_tx['token_address'] = a.xpath('./@href').extract()[0][len('/token/'):]
                token_tx['token_name'] = a.xpath('./text()').extract()[0].strip()
                
            token_tx_list.append(token_tx)
        return token_tx_list

