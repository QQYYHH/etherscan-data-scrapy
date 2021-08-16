# ethersan-data-scrapy
通过scrapy爬取etherscan主网的以太坊数据，包括区块&amp;各种类型交易

# 思路
官方API获取交易，或内部交易列表，必须指定相关账户，且一次性获取交易数有限，因此不使用官方API <br>
暴力网页抓取  https://etherscan.io/blocks?p=1 <br>
从区块入手，因为区块可追溯的时间跨度很大，提取区块中的交易和内部交易 <br>

# block
由 spider/etherscan.py 爬取

# 依赖环境
`pip3 install scrapy`

# transaction
由 spider/get_tx 爬取 <br>
交易类型较为复杂：分成4类：<br>
普通交易、合约调用交易、contract internal tx、Token tx, Token就是基于以太坊智能合约开发的新型代币 <br>
在爬取普通交易的过程中，就能顺便 抽取contract interal tx & Token tx <br>

# run
爬取block `scrapy crawl etherscan -O block.json` or `python run.py block` <br>
爬取一个block内的所有类型的交易  `scrapy crawl get_tx -O tx.json` or `python run.py tx`



