import json
from cosmos_to_caaj.message import *
from decimal import *
from datetime import datetime as dt
import logging
import re

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
getcontext().prec = 50

def set_root_logger():
  root_logget = logging.getLogger(name=None)
  root_logget.setLevel(logging.INFO)
  stream_handler = logging.StreamHandler()
  stream_handler.setLevel(logging.INFO)
  root_logget.addHandler(stream_handler)

class Transaction:
  PLATFORM = 'cosmos'
  set_root_logger()

  def __init__(self, transaction):
    self.transaction = transaction
    self.chain_id = transaction['header']['chain_id']
    self.fail = False
    self.time = dt.strptime(self.transaction['header']['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
    if (self.chain_id == 'cosmoshub-4' and transaction['data']['code'] != 0) or (self.chain_id in ['cosmoshub-3', 'cosmoshub-2', 'cosmoshub-1'] and transaction['data']['logs'][0]['success'] != True):
      logger.info(f'transaction: {transaction["data"]["txhash"]} is failed')
      self.fail = True
      return

  def get_messages(self):
    return list(map(lambda x: Message(x['events'], self.transaction['data']['height']), self.transaction['data']['logs']))

  def get_transfers(self, recipient):
    transfers = list(filter(lambda x: x['type'] == 'transfer' and x['recipient'] == recipient, self.events))
    return transfers

  def get_fail(self):
    return self.fail
  
  def get_transaction_id(self):
    return self.transaction['data']['txhash'].lower()

  def get_time(self):
    return self.time.strftime('%Y-%m-%d %H:%M:%S')

  def get_fee(self):
    if self.chain_id == 'cosmoshub-4':
      amount = str(CosmosUtil.convert_uamount_amount(self.transaction['data']['tx']['auth_info']['fee']['amount'][0]['amount']))
    else:
      amount = str(CosmosUtil.convert_uamount_amount(self.transaction['data']['tx']['value']['fee']['amount'][0]['amount']))
    return amount