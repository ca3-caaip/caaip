import requests
import time
import json
import sys
import logging
from caaj_plugin.caaj_plugin import *
from block import *
from transaction import *
from decimal import *
from datetime import datetime as dt

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
getcontext().prec = 50

def set_root_logger():
  root_logget = logging.getLogger(name=None)
  root_logget.setLevel(logging.INFO)
  stream_handler = logging.StreamHandler()
  stream_handler.setLevel(logging.INFO)
  root_logget.addHandler(stream_handler)

class CosmosPlugin(CaajPlugin):
  def can_handle(self, transaction):
    try:
      chain_id = transaction['header']['chain_id']
      if 'cosmos' in chain_id:
        return True
      else:
        return False
    except e:
      return False

    return True

  def get_caajs(self, transaction, subject_address):
    transaction = Transaction(transaction)
    caaj = transaction.get_caaj(subject_address)


def main():
  cosmos = CosmosPlugin()
  caajs = []
  print('hjoge')
  
  address = sys.argv[1]
  num_transactions = 50 
  last_id = 0
  f = open('transactions.txt', 'w')
  while num_transactions >= 50:
    time.sleep(5)
    response = requests.get(
        'https://api.cosmostation.io/v1/account/new_txs/%s' % address,
        params={'from': last_id, 'limit': 50})
    transactions = response.json()
    num_transactions = len(transactions) 
    #print(num_transactions)
    for transaction in transactions:
      if cosmos.can_handle(transaction) == False:
        raise ValueError('not cosmos transaction')
      cosmos.get_caajs(transaction, address)
      f.write(json.dumps(transaction)+"\n")
  f.close()

if __name__== '__main__':
  set_root_logger()
  main()

