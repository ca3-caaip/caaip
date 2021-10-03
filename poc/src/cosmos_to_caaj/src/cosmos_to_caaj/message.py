import json
from decimal import *
from datetime import datetime as dt
import logging
import re
from cosmos_to_caaj.cosmos_util import *
from cosmos_to_caaj.block import *

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
getcontext().prec = 50

def set_root_logger():
  root_logget = logging.getLogger(name=None)
  root_logget.setLevel(logging.INFO)
  stream_handler = logging.StreamHandler()
  stream_handler.setLevel(logging.INFO)
  root_logget.addHandler(stream_handler)

class Message:
  PLATFORM = 'cosmos'
  set_root_logger()

  def __init__(self, event, height):
    self.events = event
    self.height = height

  def get_result(self):
    event = CosmosUtil.get_event_value(self.events, 'message')
    action = CosmosUtil.get_attribute_value(event['attributes'], 'action')    

    result = {'action': None, 'result': None}
    if action == 'withdraw_delegator_reward':
      result = self.__as_withdraw_delegator_reward()
    elif action == 'delegate':
      result = self.__as_delegate()
    elif action == 'send':
      result = self.__as_send()
    elif action == 'swap_within_batch':
      result = self.__as_swap_within_batch()
    elif action == 'deposit_within_batch':
      result = self.__as_deposit_within_batch()

    return result

  def __as_withdraw_delegator_reward(self):
    event = CosmosUtil.get_event_value(self.events, 'withdraw_rewards')
    amount = CosmosUtil.get_attribute_value(event['attributes'], 'amount')
    amount = str(CosmosUtil.convert_uamount_amount(amount))
    return {'action': 'withdraw_delegator_reward', 'result': {'reward_coin': 'ATOM', 'reward_amount': amount}}

  def __as_delegate(self):
    event = CosmosUtil.get_event_value(self.events, 'delegate')
    amount = CosmosUtil.get_attribute_value(event['attributes'], 'amount')
    amount = str(CosmosUtil.convert_uamount_amount(amount))

    result = {'staking_coin': 'ATOM', 'staking_amount': amount, 'reward_coin': 'ATOM', 'reward_amount': 0}
    # try to find delegate reward
    event = CosmosUtil.get_event_value(self.events, 'transfer')
    if event != None:
      amount = CosmosUtil.get_attribute_value(event['attributes'], 'amount')
      amount = str(CosmosUtil.convert_uamount_amount(amount))          
      result['reward_amount'] = amount

    return {'action': 'delegate', 'result': result}

  def __as_send(self):
    transfer_event = CosmosUtil.get_event_value(self.events, 'transfer')
    amount = CosmosUtil.get_attribute_value(transfer_event['attributes'], 'amount')
    amount = str(CosmosUtil.convert_uamount_amount(amount))
    recipient = CosmosUtil.get_attribute_value(transfer_event['attributes'], 'recipient')

    message_event = CosmosUtil.get_event_value(self.events, 'message')
    sender = CosmosUtil.get_attribute_value(message_event['attributes'], 'sender')

    return {'action': 'send', 'result': {'sender': sender, 'recipient': recipient, 'coin': 'ATOM', 'amount': amount}}

  def __as_swap_within_batch(self):
    swap_within_batch_event = CosmosUtil.get_event_value(self.events, 'swap_within_batch')

    block = Block.get_block(self.height)
    pool_id = CosmosUtil.get_attribute_value(swap_within_batch_event['attributes'], 'pool_id')
    batch_index = CosmosUtil.get_attribute_value(swap_within_batch_event['attributes'], 'batch_index')
    msg_index = CosmosUtil.get_attribute_value(swap_within_batch_event['attributes'], 'msg_index')        
    swap_transacted = block.get_swap_transacted(pool_id, batch_index, msg_index)

    offer_coin = CosmosUtil.get_attribute_value(swap_within_batch_event['attributes'], 'offer_coin_denom')
    offer_coin = 'ATOM' if offer_coin == 'uatom' else offer_coin
    offer_amount = CosmosUtil.get_attribute_value(swap_transacted['attributes'], 'exchanged_offer_coin_amount')
    offer_amount = str(CosmosUtil.convert_uamount_amount(offer_amount))

    demand_coin = CosmosUtil.get_attribute_value(swap_within_batch_event['attributes'], 'demand_coin_denom')
    demand_coin = 'ATOM' if demand_coin == 'uatom' else demand_coin
    
    demand_amount = CosmosUtil.get_attribute_value(swap_transacted['attributes'], 'exchanged_demand_coin_amount')
    demand_amount = str(CosmosUtil.convert_uamount_amount(demand_amount))
    fee_amount = CosmosUtil.get_attribute_value(swap_transacted['attributes'], 'offer_coin_fee_amount')
    fee_amount = str(CosmosUtil.convert_uamount_amount(fee_amount))

    return {'action': 'swap_within_batch', 'result': {'offer_coin': offer_coin, 'offer_amount': offer_amount, 'demand_coin': demand_coin, 'demand_amount': demand_amount, 'fee_amount': fee_amount}}

  def __as_deposit_within_batch(self):
    deposit_within_batch_event = CosmosUtil.get_event_value(self.events, 'deposit_within_batch')

    block = Block.get_block(self.height)
    pool_id = CosmosUtil.get_attribute_value(deposit_within_batch_event['attributes'], 'pool_id')
    batch_index = CosmosUtil.get_attribute_value(deposit_within_batch_event['attributes'], 'batch_index')
    msg_index = CosmosUtil.get_attribute_value(deposit_within_batch_event['attributes'], 'msg_index')        
    deposit_to_pool = block.get_deposit_to_pool(pool_id, batch_index, msg_index)

    pool_coin = CosmosUtil.get_attribute_value(deposit_to_pool['attributes'], 'pool_coin_denom')
    pool_amount = CosmosUtil.get_attribute_value(deposit_to_pool['attributes'], 'pool_coin_amount')
    pool_amount = str(CosmosUtil.convert_uamount_amount(pool_amount))
    accepted_coins = CosmosUtil.get_attribute_value(deposit_to_pool['attributes'], 'accepted_coins').split(',')
    liquidity_coin = {}
    for accepted_coin in accepted_coins:
      amount = re.findall(r'\d+', accepted_coin)[0]
      coin = accepted_coin[len(amount):]
      coin = 'ATOM' if coin == 'uatom' else coin
      liquidity_coin[coin] = str(CosmosUtil.convert_uamount_amount(amount))

    return {'action': 'deposit_within_batch', 'result': {'liquidity_coin': liquidity_coin, 'pool_coin': pool_coin, 'pool_amount': pool_amount}}