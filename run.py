from scrapy import cmdline
import sys

if len(sys.argv) <= 1 or sys.argv[1] == 'block':
    cmdline.execute('scrapy crawl etherscan -O block.json'.split())
else:
    cmdline.execute('scrapy crawl get_tx -O tx.json'.split())
