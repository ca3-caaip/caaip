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
    except Exception as e:
      return False

    return True

  def get_caajs(self, transaction, subject_address):
    caajs = []
    transaction = Transaction(transaction)
    messages = transaction.get_messages()
    for message in messages:
      result = message.get_result()
      logger.info(result['action'])      
      if result['action'] == 'withdraw_delegator_reward':
        caajs.extend(CosmosPlugin.__as_withdraw_delegator_reward(transaction, result['result'], subject_address))

    return caajs

  @classmethod
  def __as_withdraw_delegator_reward(cls, transaction: Transaction, result, subject_address: str):
    caajs = [{
      'time':           transaction.get_time(),
      'platform':       Transaction.PLATFORM,
      'transaction_id': transaction.get_transaction_id(),
      'debit_title':    'SPOT',
      'debit_amount':   {result['reward_coin']: result['reward_amount']},
      'debit_from':     'cosmos_staking_reward',
      'debit_to':       subject_address,
      'credit_title':   'STAKINGREWARD',
      'credit_amount':  {result['reward_coin']: result['reward_amount']},
      'credit_from':    subject_address,
      'credit_to':      'cosmos_staking_reward',
      'comment':        'cosmos staking reward'
    }]
    return caajs