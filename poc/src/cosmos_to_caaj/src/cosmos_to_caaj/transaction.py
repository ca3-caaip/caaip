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

  def get_caaj(self, subject_address):
    try:
      action = self.get_action()
    except Exception as e:
      return
    if action == 'withdraw_delegator_reward':
      print(action)
    elif action == 'delegate':
      print(action)
    elif action == 'send':
      print(action)
    elif action == 'swap_within_batch':
      print(action)
    elif action == 'deposit_within_batch':
      print(action)
    else:
      print(action)
      logger.info(json.dumps(self.transaction, indent=2))


  def __as_withdraw_delegator_reward(self, subject_address):
    event = Transaction.get_event_value(self.events, 'withdraw_rewards')
    amount = Transaction.get_attribute_value(event['attributes'], 'amount')
    amount = str(Transaction.convert_uamount_amount(amount))

    caajs = [{
      'time':           self.time.strftime('%Y-%m-%d %H:%M:%S'),
      'platform':       Transaction.PLATFORM,
      'transaction_id': self.transaction['data']['txhash'].lower(),
      'debit_title':    'SPOT',
      'debit_amount':   {'ATOM': amount},
      'debit_from':     'cosmos_staking_reward',
      'debit_to':       subject_address,
      'credit_title':   'STAKINGREWARD',
      'credit_amount':  {'ATOM': amount},
      'credit_from':    subject_address,
      'credit_to':      'cosmos_staking_reward',
      'comment':        'cosmos staking reward'
    }]
    return caajs

  def __as_transaction_fee(self, subject_address):
    if self.chain_id == 'cosmoshub-4':
      amount = str(Transaction.convert_uamount_amount(self.transaction['data']['tx']['auth_info']['fee']['amount'][0]['amount']))
    else:
      amount = str(Transaction.convert_uamount_amount(self.transaction['data']['tx']['value']['fee']['amount'][0]['amount']))
    caajs = [{
      'time':           self.time.strftime('%Y-%m-%d %H:%M:%S'),
      'platform':       Transaction.PLATFORM,
      'transaction_id': self.transaction['data']['txhash'].lower(),
      'debit_title':    'FEE',
      'debit_amount':   {'ATOM': amount},
      'debit_from':     'cosmos_fee',
      'debit_to':       subject_address,
      'credit_title':   'SPOT',
      'credit_amount':  {'ATOM': amount},
      'credit_from':    subject_address,
      'credit_to':      'cosmos_fee',
      'comment':        'cosmos transaction fee'
    }]
    return caajs

  def __as_delegate(self, subject_address):
    event = Transaction.get_event_value(self.events, 'delegate')
    amount = Transaction.get_attribute_value(event['attributes'], 'amount')
    amount = str(Transaction.convert_uamount_amount(amount))

    caajs = [{
      'time':           self.time.strftime('%Y-%m-%d %H:%M:%S'),
      'platform':       Transaction.PLATFORM,
      'transaction_id': self.transaction['data']['txhash'].lower(),
      'debit_title':    'STAKING',
      'debit_amount':   {'ATOM': amount},
      'debit_from':     'cosmos_validator',
      'debit_to':       subject_address,
      'credit_title':   'SPOT',
      'credit_amount':  {'ATOM': amount},
      'credit_from':    subject_address,
      'credit_to':      'cosmos_validator',
      'comment':        'cosmos staking reward'
    }]
    # try to find delegate reward
    event = Transaction.get_event_value(self.events, 'transfer')
    if event != None:
      amount = Transaction.get_attribute_value(event['attributes'], 'amount')
      amount = str(Transaction.convert_uamount_amount(amount))          
      caajs.append({
        'time':           self.time.strftime('%Y-%m-%d %H:%M:%S'),
        'platform':       Transaction.PLATFORM,
        'transaction_id': self.transaction['data']['txhash'].lower(),
        'debit_title':    'SPOT',
        'debit_amount':   {'ATOM': amount},
        'debit_from':     'cosmos_staking_reward',
        'debit_to':       subject_address,
        'credit_title':   'STAKINGREWARD',
        'credit_amount':  {'ATOM': amount},
        'credit_from':    subject_address,
        'credit_to':      'cosmos_staking_reward',
        'comment':        'cosmos staking reward'
      })
    return caajs

  def __as_send(self, subject_address):
    transfer_event = Transaction.get_event_value(self.events, 'transfer')
    amount = Transaction.get_attribute_value(transfer_event['attributes'], 'amount')
    amount = str(Transaction.convert_uamount_amount(amount))
    recipient = Transaction.get_attribute_value(transfer_event['attributes'], 'recipient')

    message_event = Transaction.get_event_value(self.events, 'message')
    sender = Transaction.get_attribute_value(message_event['attributes'], 'sender')

    if subject_address not in [recipient, sender]:
      raise ValueError(f'subject_address not in recipient and sender. transaction:{self.transaction["data"]["txhash"]}')
    if subject_address == recipient:
      caajs = [{
        'time':           self.time.strftime('%Y-%m-%d %H:%M:%S'),
        'platform':       Transaction.PLATFORM,
        'transaction_id': self.transaction['data']['txhash'].lower(),
        'debit_title':    'SPOT',
        'debit_amount':   {'ATOM': amount},
        'debit_from':     sender,
        'debit_to':       recipient,
        'credit_title':   'RECEIVE',
        'credit_amount':  {'ATOM': amount},
        'credit_from':    recipient,
        'credit_to':      sender,
        'comment':        f'{recipient} receive {amount} from {sender}'
      }]
    elif subject_address == sender:
      caajs = [{
        'time':           self.time.strftime('%Y-%m-%d %H:%M:%S'),
        'platform':       Transaction.PLATFORM,
        'transaction_id': self.transaction['data']['txhash'].lower(),
        'debit_title':    'SEND',
        'debit_amount':   {'ATOM': amount},
        'debit_from':     recipient,
        'debit_to':       sender,
        'credit_title':   'SPOT',
        'credit_amount':  {'ATOM': amount},
        'credit_from':    sender,
        'credit_to':      recipient,
        'comment':        f'{sender} send {amount} to {recipient}'
      }]

    return caajs

  def __as_swap_within_batch(self, subject_address, swap_transacted):
    swap_within_batch_event = Transaction.get_event_value(self.events, 'swap_within_batch')
    offer_coin = Transaction.get_attribute_value(swap_within_batch_event['attributes'], 'offer_coin_denom')
    offer_coin = 'ATOM' if offer_coin == 'uatom' else offer_coin
    offer_amount = Transaction.get_attribute_value(swap_transacted['attributes'], 'exchanged_offer_coin_amount')
    offer_amount = str(Transaction.convert_uamount_amount(offer_amount))

    demand_coin = Transaction.get_attribute_value(swap_within_batch_event['attributes'], 'demand_coin_denom')
    demand_coin = 'ATOM' if demand_coin == 'uatom' else demand_coin

    #pool_id = Transaction.get_attribute_value(swap_within_batch_event['attributes'], 'pool_id')
    #batch_index = Transaction.get_attribute_value(swap_within_batch_event['attributes'], 'batch_index')
    #msg_index = Transaction.get_attribute_value(swap_within_batch_event['attributes'], 'msg_index')
    
    demand_amount = Transaction.get_attribute_value(swap_transacted['attributes'], 'exchanged_demand_coin_amount')
    demand_amount = str(Transaction.convert_uamount_amount(demand_amount))
    fee_amount = Transaction.get_attribute_value(swap_transacted['attributes'], 'offer_coin_fee_amount')
    fee_amount = str(Transaction.convert_uamount_amount(fee_amount))

    caajs = [{
      'time':           self.time.strftime('%Y-%m-%d %H:%M:%S'),
      'platform':       Transaction.PLATFORM,
      'transaction_id': self.transaction['data']['txhash'].lower(),
      'debit_title':    'SPOT',
      'debit_amount':   {demand_coin: demand_amount},
      'debit_from':     'cosmos_liquidity',
      'debit_to':       subject_address,
      'credit_title':   'SPOT',
      'credit_amount':  {offer_coin: offer_amount},
      'credit_from':    subject_address,
      'credit_to':      'cosmos_liquidity',
      'comment':        f'buy {demand_coin} {demand_amount} sell {offer_coin} {offer_amount}'
    },
    {
      'time':           self.time.strftime('%Y-%m-%d %H:%M:%S'),
      'platform':       Transaction.PLATFORM,
      'transaction_id': self.transaction['data']['txhash'].lower(),
      'debit_title':    'FEE',
      'debit_amount':   {offer_coin: fee_amount},
      'debit_from':     'cosmos_liquidity',
      'debit_to':       subject_address,
      'credit_title':   'SPOT',
      'credit_amount':  {offer_coin: fee_amount},
      'credit_from':    subject_address,
      'credit_to':      'cosmos_liquidity',
      'comment':        f'pay {fee_amount} {offer_amount} as swap fee'
    }]

    return caajs

  def __as_deposit_within_batch(self, subject_address, deposit_to_pool):
    deposit_within_batch_event = Transaction.get_event_value(self.events, 'deposit_within_batch')
    #print(json.dumps(deposit_to_pool))
    pool_coin = Transaction.get_attribute_value(deposit_to_pool['attributes'], 'pool_coin_denom')
    pool_amount = Transaction.get_attribute_value(deposit_to_pool['attributes'], 'pool_coin_amount')
    accepted_coins = Transaction.get_attribute_value(deposit_to_pool['attributes'], 'accepted_coins').split(',')
    liquidity_coin = {}
    for accepted_coin in accepted_coins:
      amount = re.findall(r'\d+', accepted_coin)[0]
      coin = accepted_coin[len(amount):]
      coin = 'ATOM' if coin == 'uatom' else coin
      liquidity_coin[coin] = str(Transaction.convert_uamount_amount(amount))

    caajs = [{
      'time':           self.time.strftime('%Y-%m-%d %H:%M:%S'),
      'platform':       Transaction.PLATFORM,
      'transaction_id': self.transaction['data']['txhash'].lower(),
      'debit_title':    'LIQUIDITY',
      'debit_amount':   {pool_coin: pool_amount},
      'debit_from':     'cosmos_liquidity',
      'debit_to':       subject_address,
      'credit_title':   'SPOT',
      'credit_amount':  liquidity_coin,
      'credit_from':    subject_address,
      'credit_to':      'cosmos_liquidity',
      'comment':        f'provide liquidity {liquidity_coin} receive {pool_amount} {pool_coin}'
    }]    
    return caajs