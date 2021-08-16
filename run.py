from scrapy import cmdline
import sys

if len(sys.argv) <= 1 or sys.argv[1] == 'block':
    cmdline.execute('scrapy crawl etherscan -s LOG_FILE=block-error.log -O block.json'.split())
else:
    cmdline.execute('scrapy crawl get_tx -s LOG_FILE=tx-error.log -O tx.csv'.split())
