# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

# name --> filed
Block_target_keys = {'Block Height:': 'block_height', 'Timestamp:': 'ts', 'Transactions:': 'tx', 'Mined by:': 'miner', \
    'Block Reward:': 'block_reward', 'Uncles Reward:': 'uncle_reward', 'Difficulty:': 'difficulty', 'Total Difficulty:': 'total_difficulty', 'Size:': 'size', \
    'Gas Used:': 'gas_used', 'Gas Limit:': 'gas_limit', 'Base Fee Per Gas:': 'basefee_pergas', 'Hash:': 'block_hash', 'Parent Hash:': 'pre_hash', \
    'Sha3Uncles:': 'sha3uncles', 'StateRoot:': 'state_root', 'Nonce:': 'nonce'}

# 区块数据对象
class BlockItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    block_height = scrapy.Field()
    ts = scrapy.Field() # 时间戳
    tx_num = scrapy.Field()
    interal_tx_num = scrapy.Field()
    miner = scrapy.Field()
    block_reward = scrapy.Field()
    uncle_reward = scrapy.Field()
    difficulty = scrapy.Field()
    total_difficulty = scrapy.Field()
    size = scrapy.Field()
    gas_used = scrapy.Field()
    gas_limit = scrapy.Field()
    basefee_pergas = scrapy.Field()
    # burnt_fees = scrapy.Field()
    block_hash = scrapy.Field()
    pre_hash = scrapy.Field()
    sha3uncles = scrapy.Field()
    state_root = scrapy.Field()
    nonce = scrapy.Field()


Tx_target_keys = {'Transaction Hash:': 'tx_hash', 'Status:': 'status', 'Block:': 'block', 'Timestamp:': 'ts', 'From:': 'fm', \
    'To:': 'to', 'Interacted With (To):': 'to', 'Tokens Transferred:': 'tk_transfer', \
    'Value:': 'value', 'Transaction Fee:': 'tx_fee', 'Gas Price:': 'gas_price', 'Txn Type:': 'tx_type', 'Gas Limit:': 'gas_limit', \
    'Gas Used by Transaction:': 'gas_used', 'Base Fee Per Gas:': 'basefee_pergas', 'Burnt Fees:': 'burnt_fee', 'Nonce': 'nonce'}

# 交易数据对象
class TxItem(scrapy.Item):
    # 0 - 基本交易
    # 1 - 合约调用交易
    # 2 - 合约内部交易
    # 3 - Token交易
    id = scrapy.Field()
    tx_hash = scrapy.Field() # 如果是interal tx | token tx, 这个字段记录 父交易的 hash
    status = scrapy.Field()
    block = scrapy.Field()
    ts = scrapy.Field()

    fm = scrapy.Field() # 如果是token转账，代表token发送地址
    to = scrapy.Field() # 如果是token转账，代表token接收地址

    # 合约执行过程中的一些event, 这些event可以通过 Token transferred 完全追踪
    # 所以这个属性是可以去掉的
    # tx_action = scrapy.Field()  'Transaction Action:': 'tx_action'
    # Token 相关
    token_address = scrapy.Field() # token的官方地址 etherscan.io/token/address
    token_name = scrapy.Field() # token币的名字
    
    # 如果token transfer 交易的是NFT，那么该字段代表NFT代号
    # 可以在 https://etherscan.io/token/tk_address?a=NFTID 地址访问NFT具体数据
    ntf = scrapy.Field() 


    value = scrapy.Field()
    tx_fee = scrapy.Field()
    gas_price = scrapy.Field() # 每单位汽油费
    tx_type = scrapy.Field() # 交易代币遵守哪种 ERC/EIP 规范
    gas_limit = scrapy.Field()
    gas_used = scrapy.Field()
    basefee_pergas = scrapy.Field()
    burnt_fee = scrapy.Field()
    nonce = scrapy.Field()
    position = scrapy.Field() # 一笔交易在区块中的位次（排序后区块中的第几笔交易）
