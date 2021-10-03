import unittest
from unittest.mock import *
import os
from cosmos_to_caaj.message import *
from cosmos_to_caaj.block import *
import json
from pathlib import Path

class TestMessage(unittest.TestCase):
  """verify get_caaj works fine"""

  def test_get_result(self):
    v4_withdraw_delegator_reward = json.loads(Path('%s/../testdata/withdraw_delegator_reward_v4.json' % os.path.dirname(__file__)).read_text())
    message = Message(v4_withdraw_delegator_reward['data']['logs'][0]['events'], v4_withdraw_delegator_reward['data']['height'])
    result = message.get_result()
    self.assertEqual(result['action'], 'withdraw_delegator_reward')

    v3_delegate = json.loads(Path('%s/../testdata/delegate_v3.json' % os.path.dirname(__file__)).read_text())
    message = Message(v3_delegate['data']['logs'][0]['events'], v3_delegate['data']['height'])
    result = message.get_result()
    self.assertEqual(result['action'], 'delegate')

    v3_send = json.loads(Path('%s/../testdata/send_v3.json' % os.path.dirname(__file__)).read_text())
    message = Message(v3_send['data']['logs'][0]['events'], v3_send['data']['height'])
    result = message.get_result()
    self.assertEqual(result['action'], 'send')

  def test_as_withdraw_delegator_reward(self):
    v4_withdraw_delegator_reward = json.loads(Path('%s/../testdata/withdraw_delegator_reward_v4.json' % os.path.dirname(__file__)).read_text())
    message = Message(v4_withdraw_delegator_reward['data']['logs'][0]['events'], v4_withdraw_delegator_reward['data']['height'])

    result = message._Message__as_withdraw_delegator_reward()
    self.assertEqual(result['action'], 'withdraw_delegator_reward')
    self.assertEqual(result['result'], {'reward_coin': 'ATOM', 'reward_amount': '0.888455'})

  def test_as_delegate(self):
    v3_delegate = json.loads(Path('%s/../testdata/delegate_v3.json' % os.path.dirname(__file__)).read_text())
    message = Message(v3_delegate['data']['logs'][0]['events'], v3_delegate['data']['height'])
    result = message._Message__as_delegate()
  
    self.assertEqual(result['action'], 'delegate')
    self.assertEqual(result['result'], {'staking_coin': 'ATOM', 'staking_amount': '15.799646', 'reward_coin': 'ATOM', 'reward_amount': '0.000016'})


  def test_as_send(self):
    v3_send = json.loads(Path('%s/../testdata/send_v3.json' % os.path.dirname(__file__)).read_text())
    message = Message(v3_send['data']['logs'][0]['events'], v3_send['data']['height'])
    result = message._Message__as_send()
    self.assertEqual(result['action'], 'send')
    self.assertEqual(result['result'], {'sender': 'cosmos1t5u0jfg3ljsjrh2m9e47d4ny2hea7eehxrzdgd', 'recipient': 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7', 'coin': 'ATOM', 'amount': '1'})

  @classmethod
  def mock_get_block_swap_transacted(cls, height):
    block_json = json.loads(Path('%s/../testdata/block_swap_within_batch_v4.json' % os.path.dirname(__file__)).read_text())
    block = Block(block_json)
    return block

  def test_as_swap_within_batch(self):
    v4_swap_within_batch = json.loads(Path('%s/../testdata/swap_within_batch_v4.json' % os.path.dirname(__file__)).read_text())
    message = Message(v4_swap_within_batch['data']['logs'][0]['events'], v4_swap_within_batch['data']['height'])

    with patch.object(Block, 'get_block', new=TestMessage.mock_get_block_swap_transacted):
      result = message._Message__as_swap_within_batch()
    self.assertEqual(result['action'], 'swap_within_batch')
    self.assertEqual(result['result'], {'offer_coin': 'ibc/14F9BC3E44B8A9C1BE1FB08980FAB87034C9905EF17CF2F5008FC085218811CC', 'offer_amount': '39.940057', 'demand_coin': 'ATOM', 'demand_amount': '6.039087', 'fee_amount': '0.05991'})

  @classmethod
  def mock_get_block_deposit_to_pool(cls, height):
    block_json = json.loads(Path('%s/../testdata/block_deposit_within_batch_v4.json' % os.path.dirname(__file__)).read_text())
    block = Block(block_json)
    return block

  def test_as_deposit_within_batch(self):
    v4_deposit_within_batch = json.loads(Path('%s/../testdata/deposit_within_batch_v4.json' % os.path.dirname(__file__)).read_text())
    message = Message(v4_deposit_within_batch['data']['logs'][0]['events'], v4_deposit_within_batch['data']['height'])

    with patch.object(Block, 'get_block', new=TestMessage.mock_get_block_deposit_to_pool):
      result = message._Message__as_deposit_within_batch()
    self.assertEqual(result['action'], 'deposit_within_batch')
    self.assertEqual(result['result'], {'liquidity_coin': {'ATOM': '0.863882', 'ibc/2181AAB0218EAC24BC9F86BD1364FBBFA3E6E3FCC25E88E3E68C15DC6E752D86': '9'}, 'pool_coin': 'pool32DD066BE949E5FDCC7DC09EBB67C7301D0CA957C2EF56A39B37430165447DAC', 'pool_amount': '0.000022'})


if __name__ == '__main__':
  unittest.main()