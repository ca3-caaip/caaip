import csv
import json
import pandas as pd
from decimal import Decimal
from web3 import Web3,HTTPProvider
import os

settings = json.loads(open('%s/../settings.json' % os.path.dirname(__file__)).read())

web3 = Web3(HTTPProvider('https://mainnet.infura.io/v3/%s' % settings['infra_key']))
erc20_abi = json.loads(open('%s/erc20_abi.json' %  os.path.dirname(__file__)).read())

TIME           = 0
PLATFORM       = 1
TRANSACTION_ID = 2
DEBIT_TITLE    = 3
DEBIT_AMOUNT   = 4
DEBIT_FROM     = 5
DEBIT_TO       = 6
CREDIT_TITLE   = 7
CREDIT_AMOUNT  = 8
CREDIT_FROM    = 9
CREDIT_TO      = 10
COMMENT        = 11


def ouput(results):
  df = pd.DataFrame(results)
  df = df.sort_values('Timestamp')
  #print(df)
  result_file_name = '%s/../output/cryptact.csv' %  os.path.dirname(__file__)
  df.to_csv(result_file_name, index=False, columns=['Timestamp', 'Action', 'Source', 'Base', 'Volume', 'Price', 'Counter', 'Fee', 'FeeCcy', 'Comment'])

def get_erc20_symbol(address):
  if address == 'ETH': return address
  contract = web3.eth.contract(address=Web3.toChecksumAddress(address), abi=erc20_abi)
  symbol = contract.functions.symbol().call()

  return symbol

def main():
  f = open('%s/../output/uniswap_caaj.csv' %  os.path.dirname(__file__), 'r')
  reader = csv.reader(f)
  header = next(reader)

  cryptacts = []
  liquidity = {}
  
  for i, row in enumerate(reader):
    print(row[TIME])
    if 'FEE' in row[DEBIT_TITLE] and 'SPOT' in row[CREDIT_TITLE]:
      base =  list(json.loads(row[CREDIT_AMOUNT].replace("'", '"')).keys())[0]
      volume =  list(json.loads(row[CREDIT_AMOUNT].replace("'", '"')).values())[0]
      # fee
      cryptacts.append({'Timestamp': row[TIME], 'Source': row[PLATFORM], 'Action': 'SENDFEE', 'Base': base, 'Volume': volume, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': base, 'Comment': row[COMMENT]})
    elif 'LIQUIDITY' in row[DEBIT_TITLE] and 'SPOT' in row[CREDIT_TITLE]:
      # add liquidity
      liquidity_token =  list(json.loads(row[DEBIT_AMOUNT].replace("'", '"')).keys())[0]
      liquidity_amount =  Decimal(list(json.loads(row[DEBIT_AMOUNT].replace("'", '"')).values())[0])
      collateral = json.loads(row[CREDIT_AMOUNT].replace("'", '"'))
      for k, v in collateral.items():
        collateral[k] = Decimal(v)

      if liquidity_token in liquidity: # same liquidity is already exist
        liquidity_amount += liquidity[liquidity_token]['liquidity_amount']
        for k, v in collateral.items():
          liquidity[liquidity_token]['collateral'][k] = liquidity[liquidity_token]['collateral'][k] + v if k in liquidity[liquidity_token]['collateral'] else v
        collateral = liquidity[liquidity_token]['collateral']

      liquidity[liquidity_token] = {'liquidity_amount': liquidity_amount, 'collateral': collateral}
    elif 'LIQUIDITY' in row[CREDIT_TITLE] and 'SPOT' in row[DEBIT_TITLE]:
      # remove liquidity
      # ignore exception case in this time
      collects = json.loads(row[DEBIT_AMOUNT].replace("'", '"'))
      if len(list(json.loads(row[CREDIT_AMOUNT].replace("'", '"')).keys())) > 0:
        # remove collateral
        liquidity_token = list(json.loads(row[CREDIT_AMOUNT].replace("'", '"')).keys())[0]
        liquidity_amount =  list(json.loads(row[CREDIT_AMOUNT].replace("'", '"')).values())[0]
      else:
        # without remove collateral
        for k, v in collects.items():
          collect_token = get_erc20_symbol(k)
          cryptacts.append({'Timestamp': row[TIME], 'Source': row[PLATFORM], 'Action': 'BONUS', 'Base': collect_token, 'Volume': v, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'ETH', 'Comment': row[COMMENT]})
        continue

      for k, v in collects.items():
        collects[k] = Decimal(v)
      
      if liquidity[liquidity_token]['liquidity_amount'] - Decimal(liquidity_amount) == 0:
        for k, v in collects.items():
          collect_token = get_erc20_symbol(k)
          diff = v - liquidity[liquidity_token]['collateral'][k] if k in liquidity[liquidity_token]['collateral'] else v
          if diff > 0:
            cryptacts.append({'Timestamp': row[TIME], 'Source': row[PLATFORM], 'Action': 'BONUS', 'Base': collect_token, 'Volume': diff, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'ETH', 'Comment': row[COMMENT]})
          elif diff < 0:
            cryptacts.append({'Timestamp': row[TIME], 'Source': row[PLATFORM], 'Action': 'SELL', 'Base': collect_token, 'Volume': abs(diff), 'Price': 0, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'ETH', 'Comment': row[COMMENT]})
        print('removed!!!!!')
      else:
        # ToDo
        removed_collateral = {}
        collateral = liquidity[liquidity_token]['collateral']
        remove_liquidity_ratio = Decimal(liquidity_amount) / liquidity[liquidity_token]['liquidity_amount']
        for k, v in collects.items():
          collect_token = get_erc20_symbol(k)
          removed_collateral[k] = Decimal(v) * remove_liquidity_ratio
          diff = v - removed_collateral[k] if k in removed_collateral else v
          if diff > 0:
            cryptacts.append({'Timestamp': row[TIME], 'Source': row[PLATFORM], 'Action': 'BONUS', 'Base': collect_token, 'Volume': diff, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'ETH', 'Comment': row[COMMENT]})
          elif diff < 0:
            cryptacts.append({'Timestamp': row[TIME], 'Source': row[PLATFORM], 'Action': 'SELL', 'Base': collect_token, 'Volume': abs(diff), 'Price': 0, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'ETH', 'Comment': row[COMMENT]})
 
        print('not removed yet!!!!!')

      liquidity[liquidity_token]['liquidity_amount'] -= Decimal(liquidity_amount)


    elif 'SPOT' in row[DEBIT_TITLE] and 'SPOT' in row[CREDIT_TITLE] :
      # swap
      sell_token_address = list(json.loads(row[CREDIT_AMOUNT].replace("'", '"')).keys())[0]
      sell_token = get_erc20_symbol(sell_token_address)
      sell_amount = Decimal(list(json.loads(row[CREDIT_AMOUNT].replace("'", '"')).values())[0])

      buy_token_address = list(json.loads(row[DEBIT_AMOUNT].replace("'", '"')).keys())[0]
      buy_token = get_erc20_symbol(buy_token_address)
      buy_amount = Decimal(list(json.loads(row[DEBIT_AMOUNT].replace("'", '"')).values())[0])

      cryptacts.append({'Timestamp': row[TIME], 'Source': row[PLATFORM], 'Action': 'SELL', 'Base': sell_token, 'Volume': sell_amount, 'Price': buy_amount/sell_amount, 'Counter': buy_token, 'Fee': 0, 'FeeCcy': 'ETH', 'Comment': row[COMMENT]})
    else:
      raise ValueError('this record is unknown. line: %s' % i)
  
  f.close()
 
  ouput(cryptacts)

if __name__== '__main__':
    main()

