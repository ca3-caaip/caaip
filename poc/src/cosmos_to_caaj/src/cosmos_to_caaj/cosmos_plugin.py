import logging
from caaj_plugin.caaj_plugin import *
from cosmos_to_caaj.block import *
from cosmos_to_caaj.transaction import *
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
  PLATFORM = 'cosmos'
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
    print(transaction.get_transaction_id())
    for message in messages:
      try:
        result = message.get_result()
      except Exception as e:
        logger.info('message.get_result() is failed. transaction:')        
        logger.info(json.dumps(transaction.transaction))
        raise e
      if result['action'] == 'withdraw_delegator_reward':
        caajs.extend(CosmosPlugin.__as_withdraw_delegator_reward(transaction, result['result'], subject_address))
      elif result['action'] == 'delegate':
        caajs.extend(CosmosPlugin.__as_delegate(transaction, result['result'], subject_address))
      elif result['action'] == 'begin_redelegate':
        caajs.extend(CosmosPlugin.__as_delegate(transaction, result['result'], subject_address))
      elif result['action'] == 'begin_unbonding':
        caajs.extend(CosmosPlugin.__as_begin_unbonding(transaction, result['result'], subject_address))
      elif result['action'] == 'send':
        caajs.extend(CosmosPlugin.__as_send(transaction, result['result'], subject_address))
      elif result['action'] == 'swap_within_batch':
        caajs.extend(CosmosPlugin.__as_swap_within_batch(transaction, result['result'], subject_address))
      elif result['action'] == 'deposit_within_batch':
        caajs.extend(CosmosPlugin.__as_deposit_within_batch(transaction, result['result'], subject_address))
      elif result['action'] == 'withdraw_within_batch':
        caajs.extend(CosmosPlugin.__as_withdraw_within_batch(transaction, result['result'], subject_address))
      elif result['action'] == 'transfer':
        caajs.extend(CosmosPlugin.__as_send(transaction, result['result'], subject_address))
      elif result['action'] == 'update_client':
        pass
      elif result['action'] == 'recv_packet':
        caajs.extend(CosmosPlugin.__as_send(transaction, result['result'], subject_address))
      elif result['action'] == 'vote':
        pass
      else:
        logger.info(json.dumps('undefined action in CosmosPlugin'))
        logger.info(json.dumps(transaction.transaction))


    fee = transaction.get_fee()
    caajs.extend(CosmosPlugin.__as_transaction_fee(transaction, fee, subject_address))
    return caajs

  @classmethod
  def __as_withdraw_delegator_reward(cls, transaction: Transaction, result, subject_address: str):
    caajs = [{
      'time':           transaction.get_time(),
      'platform':       CosmosPlugin.PLATFORM,
      'transaction_id': transaction.get_transaction_id(),
      'debit_title':    'SPOT',
      'debit_amount':   {result['reward_coin']: result['reward_amount']},
      'debit_from':     'cosmos_staking_reward',
      'debit_to':       subject_address,
      'credit_title':   'STAKINGREWARD',
      'credit_amount':  {result['reward_coin']: result['reward_amount']},
      'credit_from':    subject_address,
      'credit_to':      'cosmos_staking_reward',
      'comment':        f'staking reward {result["reward_amount"]} {result["reward_coin"]}'
    }]
    return caajs

  @classmethod
  def __as_transaction_fee(cls, transaction: Transaction, amount: str, subject_address: str):
    caajs = [{
      'time':           transaction.get_time(),
      'platform':       CosmosPlugin.PLATFORM,
      'transaction_id': transaction.get_transaction_id(),
      'debit_title':    'FEE',
      'debit_amount':   {'ATOM': amount},
      'debit_from':     'cosmos_fee',
      'debit_to':       subject_address,
      'credit_title':   'SPOT',
      'credit_amount':  {'ATOM': amount},
      'credit_from':    subject_address,
      'credit_to':      'cosmos_fee',
      'comment':        f'transaction fee {amount} ATOM'
    }]
    return caajs

  @classmethod
  def __as_delegate(cls, transacton: Transaction, result, subject_address: str):
    caajs = []
    if Decimal(result['staking_amount']) != Decimal('0'):
      caajs.append({
        'time':           transacton.get_time(),
        'platform':       CosmosPlugin.PLATFORM,
        'transaction_id': transacton.get_transaction_id(),
        'debit_title':    'STAKING',
        'debit_amount':   {result['staking_coin']: result['staking_amount']},
        'debit_from':     'cosmos_validator',
        'debit_to':       subject_address,
        'credit_title':   'SPOT',
        'credit_amount':  {result['staking_coin']: result['staking_amount']},
        'credit_from':    subject_address,
        'credit_to':      'cosmos_validator',
        'comment':        f'staking {result["staking_amount"]} {result["staking_coin"]}'
      })
    # try to find delegate reward
    if Decimal(result['reward_amount']) != Decimal('0'):
      caajs.append({
        'time':           transacton.get_time(),
        'platform':       CosmosPlugin.PLATFORM,
        'transaction_id': transacton.get_transaction_id(),
        'debit_title':    'SPOT',
        'debit_amount':   {result['reward_coin']: result['reward_amount']},
        'debit_from':     'cosmos_staking_reward',
        'debit_to':       subject_address,
        'credit_title':   'STAKINGREWARD',
        'credit_amount':  {result['reward_coin']: result['reward_amount']},
        'credit_from':    subject_address,
        'credit_to':      'cosmos_staking_reward',
        'comment':        f'staking reward {result["reward_amount"]} {result["reward_coin"]}'
      })
    return caajs

  @classmethod
  def __as_begin_unbonding(cls, transacton: Transaction, result, subject_address: str):
    caajs = [{
      'time':           transacton.get_time(),
      'platform':       CosmosPlugin.PLATFORM,
      'transaction_id': transacton.get_transaction_id(),
      'debit_title':    'SPOT',
      'debit_amount':   {result['unbonding_coin']: result['unbonding_amount']},
      'debit_from':     'cosmos_validator',
      'debit_to':       subject_address,
      'credit_title':   'STAKING',
      'credit_amount':  {result['unbonding_coin']: result['unbonding_amount']},
      'credit_from':    subject_address,
      'credit_to':      'cosmos_validator',
      'comment':        f'unstaking {result["unbonding_amount"]} {result["unbonding_coin"]}'
    }]
    # try to find delegate reward
    if Decimal(result['reward_amount']) != Decimal('0'):
      caajs.append({
        'time':           transacton.get_time(),
        'platform':       CosmosPlugin.PLATFORM,
        'transaction_id': transacton.get_transaction_id(),
        'debit_title':    'SPOT',
        'debit_amount':   {result['reward_coin']: result['reward_amount']},
        'debit_from':     'cosmos_staking_reward',
        'debit_to':       subject_address,
        'credit_title':   'STAKINGREWARD',
        'credit_amount':  {result['reward_coin']: result['reward_amount']},
        'credit_from':    subject_address,
        'credit_to':      'cosmos_staking_reward',
        'comment':        f'staking reward {result["reward_amount"]} {result["reward_coin"]}'
      })
    return caajs

  @classmethod
  def __as_send(cls, transaction:Transaction, result, subject_address:str):
    recipient = result['recipient']
    sender = result['sender']

    if subject_address not in [recipient, sender]:
      raise ValueError(f'subject_address not in recipient and sender. transaction:{transaction["data"]["txhash"]}')
    if subject_address == recipient:
      caajs = [{
        'time':           transaction.get_time(),
        'platform':       CosmosPlugin.PLATFORM,
        'transaction_id': transaction.get_transaction_id(),
        'debit_title':    'SPOT',
        'debit_amount':   {result['coin']: result['amount']},
        'debit_from':     sender,
        'debit_to':       recipient,
        'credit_title':   'RECEIVE',
        'credit_amount':  {result['coin']: result['amount']},
        'credit_from':    recipient,
        'credit_to':      sender,
        'comment':        f'{recipient} receive {result["amount"]} {result["coin"]} from {sender}'
      }]
    elif subject_address == sender:
      caajs = [{
        'time':           transaction.get_time(),
        'platform':       CosmosPlugin.PLATFORM,
        'transaction_id': transaction.get_transaction_id(),
        'debit_title':    'SEND',
        'debit_amount':   {result['coin']: result['amount']},
        'debit_from':     recipient,
        'debit_to':       sender,
        'credit_title':   'SPOT',
        'credit_amount':  {result['coin']: result['amount']},
        'credit_from':    sender,
        'credit_to':      recipient,
        'comment':        f'{sender} send {result["amount"]} {result["coin"]} to {recipient}'
      }]

    return caajs

  @classmethod
  def __as_swap_within_batch(cls, transaction:Transaction, result, subject_address:str):
    caajs = []
    if not (Decimal(result['demand_amount']) == Decimal('0') and Decimal(result['offer_amount']) == Decimal('0')):
      caajs.extend([{
        'time':           transaction.get_time(),
        'platform':       CosmosPlugin.PLATFORM,
        'transaction_id': transaction.get_transaction_id(),
        'debit_title':    'SPOT',
        'debit_amount':   {result['demand_coin']: result['demand_amount']},
        'debit_from':     'cosmos_liquidity',
        'debit_to':       subject_address,
        'credit_title':   'SPOT',
        'credit_amount':  {result['offer_coin']: result['offer_amount']},
        'credit_from':    subject_address,
        'credit_to':      'cosmos_liquidity',
        'comment':        f'buy {result["demand_amount"]} {result["demand_coin"]} sell {result["offer_amount"]} {result["offer_coin"]}'
      },
      {
        'time':           transaction.get_time(),
        'platform':       CosmosPlugin.PLATFORM,
        'transaction_id': transaction.get_transaction_id(),
        'debit_title':    'FEE',
        'debit_amount':   {result['offer_coin']: result['fee_amount']},
        'debit_from':     'cosmos_liquidity',
        'debit_to':       subject_address,
        'credit_title':   'SPOT',
        'credit_amount':  {result['offer_coin']: result['fee_amount']},
        'credit_from':    subject_address,
        'credit_to':      'cosmos_liquidity',
        'comment':        f'pay {result["fee_amount"]} {result["offer_coin"]} as swap fee'
      }])
  
    return caajs

  @classmethod
  def __as_deposit_within_batch(cls, transaction:Transaction, result, subject_address:str):
    caajs = [{
      'time':           transaction.get_time(),
      'platform':       CosmosPlugin.PLATFORM,
      'transaction_id': transaction.get_transaction_id(),
      'debit_title':    'LIQUIDITY',
      'debit_amount':   {result['pool_coin']: result['pool_amount']},
      'debit_from':     'cosmos_liquidity',
      'debit_to':       subject_address,
      'credit_title':   'SPOT',
      'credit_amount':  result['liquidity_coin'],
      'credit_from':    subject_address,
      'credit_to':      'cosmos_liquidity',
      'comment':        f'deposit liquidity send {result["liquidity_coin"]} receive {result["pool_amount"]} {result["pool_coin"]}'
    }]    
    return caajs

  @classmethod
  def __as_withdraw_within_batch(cls, transaction:Transaction, result, subject_address:str):
    caajs = [{
      'time':           transaction.get_time(),
      'platform':       CosmosPlugin.PLATFORM,
      'transaction_id': transaction.get_transaction_id(),
      'debit_title':    'SPOT',
      'debit_amount':   result['liquidity_coin'],
      'debit_from':     'cosmos_liquidity',
      'debit_to':       subject_address,
      'credit_title':   'LIQUIDITY',
      'credit_amount':  {result['pool_coin']: result['pool_amount']},
      'credit_from':    subject_address,
      'credit_to':      'cosmos_liquidity',
      'comment':        f'withdraw liquidity send {result["pool_amount"]} {result["pool_coin"]} receive {result["liquidity_coin"]}'
    }]    
    return caajs