import requests
import time
import sys
import logging
from caaj_plugin.caaj_plugin import *
from cosmos_plugin import *
from transaction import *
from decimal import *
from datetime import datetime as dt
import pandas as pd
import os

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
getcontext().prec = 50

def set_root_logger():
  root_logget = logging.getLogger(name=None)
  root_logget.setLevel(logging.INFO)
  stream_handler = logging.StreamHandler()
  stream_handler.setLevel(logging.INFO)
  root_logget.addHandler(stream_handler)

def output_caaj(caajs, address):
  df = pd.DataFrame(caajs)
  df = df.sort_values('time')
  result_file_name = f'{os.path.dirname(__file__)}/../../output/cosmos_caaj_{address}.csv'
  df.to_csv(result_file_name, index=False, columns=['time', 'platform', 'transaction_id', 'debit_title', 'debit_amount', 'debit_from', 'debit_to', 'credit_title', 'credit_amount', 'credit_from', 'credit_to', 'comment'])

def main():
  cosmos = CosmosPlugin()
  caajs = []
  print('hjoge')
  
  address = sys.argv[1]
  num_transactions = 50 
  last_id = 0
  while num_transactions >= 50:
    time.sleep(5)
    response = requests.get(
        'https://api.cosmostation.io/v1/account/new_txs/%s' % address,
        params={'from': last_id, 'limit': 50})
    transactions = response.json()
    num_transactions = len(transactions)
    for transaction in transactions:
      last_id = transaction['header']['id']
      if cosmos.can_handle(transaction) == False:
        raise ValueError('not cosmos transaction')
      caajs.extend(cosmos.get_caajs(transaction, address))

  output_caaj(caajs, address)

if __name__== '__main__':
  set_root_logger()
  main()

