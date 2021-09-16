from etherscan import Etherscan
from decimal import *
import json
from web3 import Web3,HTTPProvider
import sys
from datetime import datetime as dt
import pandas as pd
from hexbytes import HexBytes
import os

settings = json.loads(open('%s/../settings.json' % os.path.dirname(__file__)).read())

UNISWAP_V2_STAKING_POOL_CONTRACT_ADDRESSES = ['0x6c3e4cb2e96b01f4b866965a91ed4437839a121a', '0x7fba4b8dc5e7616e59622806932dbea72537a56b', '0xa1484c3aa22a66c62b77e0ae78e15258bd0cb711', '0xca35e32e7926b96a9988f61d510e038108d8068e']
UNISWAP_V2_SWAP_CONTRASCT_ADDRESS = ['0x7a250d5630b4cf539739df2c5dacb4c659f2488d']
UNISWAP_V3_SWAP_CONTRASCT_ADDRESS = ['0xe592427a0aece92de3edee1f18e0157c05861564', '0xc36442b4a4522e871399cd717abdd847ab11fe88']

WETH_CONTRACT_ADDRESS = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
WETH_DEPOSIT_TOPIC =    '0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c'
WETH_WITHDRAWAL_TOPIC = '0x7fcf532c15f0a6db0bd6d0e038bea71d30d808c7d98cb3bf7268a95bf5081b65'

V2_MINT_TOPIC =  '0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f'
V2_BURN_TOPIC =  '0xdccd412f0b1252819cb1fd330b93224ca42612892bb3f4f789976e6d81936496'
V2_STAKE_TOPIC = '0x9e71bc8eea02a63969f509818f2dafb9254532904319f9dbda79b67bd34a5f3d'
V2_WITHDRAW_TOPIC = '0x7084f5476618d8e60b11ef0d7d3f06914655adb8793e28ff7f018d4c76d505d5'
V2_REWARDPAID_TOPIC = '0xe2403640ba68fed3a2f88b7557551d1993f84b99bb10ff833f0cf8db0c5e0486'

V3_INCREASELIQUIDITY_TOPIC = '0x3067048beee31b25b2f1681f88dac838c8bba36af25bfb2b7cf7473a5847e35f'
V3_DECREASELIQUIDITY_TOPIC = '0x26f6a048ee9138f2c0ce266f322cb99228e8d619ae2bff30c67f8dcf9d2377b4'
V3_COLLECT_TOPIC =           '0x70935338e69775456a85ddef226c395fb668b63fa0115f5f20610b388e6ca9c0'

ERC20_TRANSFER_TOPIC = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
ERC20_APPROVE_TOPIC = '0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925'

DATA_EACH_LENGTH = 64

UNI_CONTRACT_ADDRESS = '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984'
WEI = Decimal('1000000000000000000')
PLATFORM = 'ethereum_uniswap'

web3 = Web3(HTTPProvider('https://mainnet.infura.io/v3/%s' % settings['infra_key']))
ethscan = Etherscan(settings['etherscan_key'])
erc20_abi = json.loads(open('%s/erc20_abi.json' % os.path.dirname(__file__)).read())

def is_uniswap(to):
  result = False
  if to in UNISWAP_V2_STAKING_POOL_CONTRACT_ADDRESSES or to in UNISWAP_V2_SWAP_CONTRASCT_ADDRESS or to in UNISWAP_V3_SWAP_CONTRASCT_ADDRESS:
    result = True
    
  return result

def v2_liquidity_add_to_caaj(logs, time, transaction_id, contract_address, user_address):
  # try to fine input
  input_transfers = list(filter(lambda item: (item['topics'][0].hex().lower() == ERC20_TRANSFER_TOPIC and '0x' + item['topics'][1].hex().lower()[26:] == user_address) or (item['address'].lower() == WETH_CONTRACT_ADDRESS and item['topics'][0].hex().lower() == WETH_DEPOSIT_TOPIC), logs))
  input_a_transfer = input_transfers[0]
  input_b_transfer = input_transfers[1]

  # try to fine output
  output_transfer = list(filter(lambda item: (item['topics'][0].hex().lower() == ERC20_TRANSFER_TOPIC and '0x' + item['topics'][2].hex().lower()[26:] == user_address) or (item['address'].lower() == WETH_CONTRACT_ADDRESS and item['topics'][0].hex().lower() == WETH_WITHDRAWAL_TOPIC), logs))[0]

  input_a_token = input_a_transfer['address'].lower() if input_a_transfer['address'].lower() != WETH_CONTRACT_ADDRESS else 'ETH'
  input_a_token_decimal = get_erc20_decimals(input_a_transfer['address'].lower())
  input_a_amount = Decimal(int(input_a_transfer['data'], 0)) / pow(10, input_a_token_decimal)

  input_b_token = input_b_transfer['address'].lower() if input_b_transfer['address'].lower() != WETH_CONTRACT_ADDRESS else 'ETH'
  input_b_token_decimal = get_erc20_decimals(input_b_transfer['address'].lower())
  input_b_amount = Decimal(int(input_b_transfer['data'], 0)) / pow(10, input_b_token_decimal)

  output_token = output_transfer['address'].lower() if output_transfer['address'].lower() != WETH_CONTRACT_ADDRESS else 'ETH'
  output_token_decimal = get_erc20_decimals(output_transfer['address'].lower())
  output_amount = Decimal(int(output_transfer['data'], 0)) / pow(10, output_token_decimal)

  debit_title = 'LIQUIDITY' 
  debit_from = contract_address
  debit_to =  user_address
  debit_amount = {f'{output_token}': str(output_amount)}
  credit_title = 'SPOT'
  credit_from = user_address
  credit_to = contract_address
  credit_amount = {f'{input_a_token}': str(input_a_amount), f'{input_b_token}': str(input_b_amount)}
  comment = 'uniswap add liquidity'

  caaj = {
        'time':           time,
        'platform':       PLATFORM,
        'transaction_id': transaction_id,
        'debit_title':    debit_title,
        'debit_amount':   debit_amount,
        'debit_from':     debit_from,
        'debit_to':       debit_to,
        'credit_title':   credit_title,
        'credit_amount':  credit_amount,
        'credit_from':    credit_from,
        'credit_to':      credit_to,
        'comment':        comment
      }
  return caaj

def v2_liquidity_remove_to_caaj(logs, time, transaction_id, contract_address, user_address):
  # try to find input
  input_transfer = list(filter(lambda item: (item['topics'][0].hex().lower() == ERC20_TRANSFER_TOPIC and '0x' + item['topics'][1].hex().lower()[26:] == user_address), logs))[0]

  # try to find output
  output_transfers = list(filter(lambda item: (item['topics'][0].hex().lower() == ERC20_TRANSFER_TOPIC and '0x' + item['topics'][2].hex().lower()[26:] == user_address) or (item['address'].lower() == WETH_CONTRACT_ADDRESS and item['topics'][0].hex().lower() == WETH_WITHDRAWAL_TOPIC), logs))

  output_a_transfer = output_transfers[0]
  output_b_transfer = output_transfers[1]

  input_token = input_transfer['address'].lower() if input_transfer['address'].lower() != WETH_CONTRACT_ADDRESS else 'ETH'
  input_decimal = get_erc20_decimals(input_transfer['address'].lower())
  input_amount = Decimal(int(input_transfer['data'], 0)) / pow(10, input_decimal)

  output_a_token = output_a_transfer['address'].lower() if output_a_transfer['address'].lower() != WETH_CONTRACT_ADDRESS else 'ETH'
  output_a_decimal = get_erc20_decimals(output_a_transfer['address'].lower())
  output_a_amount = Decimal(int(output_a_transfer['data'], 0)) / pow(10, output_a_decimal)

  output_b_token = output_b_transfer['address'].lower() if output_b_transfer['address'].lower() != WETH_CONTRACT_ADDRESS else 'ETH'
  output_b_decimal = get_erc20_decimals(output_b_transfer['address'].lower())
  output_b_amount = Decimal(int(output_b_transfer['data'], 0)) / pow(10, output_b_decimal)

  debit_title = 'SPOT'
  debit_from = user_address
  debit_to = contract_address
  debit_amount = {f'{output_a_token}': str(output_a_amount), f'{output_b_token}': str(output_b_amount)}
  credit_title = 'LIQUIDITY' 
  credit_from = contract_address
  credit_to =  user_address
  credit_amount = {f'{input_token}': str(input_amount)}
  comment = 'uniswap remove liquidity'

  caaj = {
        'time':           time,
        'platform':       PLATFORM,
        'transaction_id': transaction_id,
        'debit_title':    debit_title,
        'debit_amount':   debit_amount,
        'debit_from':     debit_from,
        'debit_to':       debit_to,
        'credit_title':   credit_title,
        'credit_amount':  credit_amount,
        'credit_from':    credit_from,
        'credit_to':      credit_to,
        'comment':        comment
      }

  return caaj

def swap_to_caaj(logs, time, transaction_id, contract_address, user_address):
  # try to find input
  input_transfer = list(filter(lambda item: (item['topics'][0].hex().lower() == ERC20_TRANSFER_TOPIC and '0x' + item['topics'][1].hex().lower()[26:] == user_address) or (item['address'].lower() == WETH_CONTRACT_ADDRESS and item['topics'][0].hex().lower() == WETH_DEPOSIT_TOPIC), logs))[0]
  
  # try to find output
  output_transfer = list(filter(lambda item: (item['topics'][0].hex().lower() == ERC20_TRANSFER_TOPIC and '0x' + item['topics'][2].hex().lower()[26:] == user_address) or (item['address'].lower() == WETH_CONTRACT_ADDRESS and item['topics'][0].hex().lower() == WETH_WITHDRAWAL_TOPIC), logs))[0]

  output_token = output_transfer['address'].lower() if output_transfer['address'].lower() != WETH_CONTRACT_ADDRESS else 'ETH'
  output_token_decimal = get_erc20_decimals(output_transfer['address'].lower())
  output_amount = Decimal(int(output_transfer['data'], 0)) / pow(10, output_token_decimal)

  input_token = input_transfer['address'].lower() if input_transfer['address'].lower() != WETH_CONTRACT_ADDRESS else 'ETH'
  input_token_decimal = get_erc20_decimals(input_transfer['address'].lower())
  input_amount = Decimal(int(input_transfer['data'], 0)) / pow(10, input_token_decimal)

  debit_title = 'SPOT' 
  debit_amount = {f'{output_token}': str(output_amount)}
  debit_from = contract_address
  debit_to =  user_address
  credit_title = 'SPOT'
  credit_amount = {f'{input_token}': str(input_amount)}
  credit_from = user_address
  credit_to = contract_address
  comment = 'uniswap swap'

  caaj = {
        'time':           time,
        'platform':       PLATFORM,
        'transaction_id': transaction_id,
        'debit_title':    debit_title,
        'debit_amount':   debit_amount,
        'debit_from':     debit_from,
        'debit_to':       debit_to,
        'credit_title':   credit_title,
        'credit_amount':  credit_amount,
        'credit_from':    credit_from,
        'credit_to':      credit_to,
        'comment':        comment
      }

  return caaj

def v2_swap_liquidity_to_caaj(tx, user_address):
  abis = []
  tx_hash = tx['hash']
  print(tx_hash)

  tx_detail = web3.eth.waitForTransactionReceipt(tx_hash)
  logs = tx_detail['logs']

  time = str(dt.fromtimestamp(int(tx['timeStamp'])))
  transaction_id = tx_hash


  time = str(dt.fromtimestamp(int(tx['timeStamp'])))
  transaction_id = tx_hash 

  contract_address = tx['to'].lower()

  caaj = None
  if len(list(filter(lambda item: item['topics'][0].hex() == V2_MINT_TOPIC, logs))) > 0:
    caaj = v2_liquidity_add_to_caaj(logs, time, transaction_id, contract_address, user_address)
  elif len(list(filter(lambda item: item['topics'][0].hex() == V2_BURN_TOPIC, logs))) > 0:
    caaj = v2_liquidity_remove_to_caaj(logs, time, transaction_id, contract_address, user_address)
  else:
    caaj = swap_to_caaj(logs, time, transaction_id, contract_address, user_address)
  return caaj

def v2_staking_to_caaj(tx, user_address):
  caajs = []
  tx_hash = tx['hash']

  tx_detail = web3.eth.waitForTransactionReceipt(tx_hash)
  logs = tx_detail['logs']

  time = str(dt.fromtimestamp(int(tx['timeStamp'])))
  transaction_id = tx_hash 

  contract_address = tx['to'].lower()

  if len(list(filter(lambda item: item['topics'][0].hex() == V2_STAKE_TOPIC, logs))) > 0:
    try:
      stake_transfer = list(filter(lambda item: (item['topics'][0].hex().lower() == ERC20_TRANSFER_TOPIC and '0x' + item['topics'][1].hex().lower()[26:] == user_address and item['address'].lower() != UNI_CONTRACT_ADDRESS), logs))[0]
    except IndexError as e:
      print('Cant find staked token transfer')
      raise e

    stake_token = stake_transfer['address'].lower()
    stake_decimal = get_erc20_decimals(stake_transfer['address'].lower())
    stake_amount = Decimal(int(stake_transfer['data'], 0)) / pow(10, stake_decimal)

    debit_title = 'STAKING' 
    debit_amount = {f'{stake_token}': str(stake_amount)}
    debit_from = contract_address
    debit_to =  user_address
    credit_title = 'SPOT'
    credit_amount = {f'{stake_token}': str(stake_amount)}
    credit_from = user_address
    credit_to = contract_address
    comment = 'uniswap staking'

    caaj = {
          'time':           time,
          'platform':       PLATFORM,
          'transaction_id': transaction_id,
          'debit_title':    debit_title,
          'debit_amount':   debit_amount,
          'debit_from':     debit_from,
          'debit_to':       debit_to,
          'credit_title':   credit_title,
          'credit_amount':  credit_amount,
          'credit_from':    credit_from,
          'credit_to':      credit_to,
          'comment':        comment
        }
    caajs.append(caaj)

  if len(list(filter(lambda item: item['topics'][0].hex() == V2_WITHDRAW_TOPIC, logs))) > 0:
    try:
      withdraw_transfer = list(filter(lambda item: (item['topics'][0].hex().lower() == ERC20_TRANSFER_TOPIC and '0x' + item['topics'][2].hex().lower()[26:] == user_address and item['address'].lower() != UNI_CONTRACT_ADDRESS), logs))[0]
    except IndexError as e:
      print('Cant find withdraw token transfer')
      raise e

    withdraw_token = withdraw_transfer['address'].lower()
    withdraw_decimal = get_erc20_decimals(withdraw_transfer['address'].lower())
    withdraw_amount = Decimal(int(withdraw_transfer['data'], 0)) / pow(10, withdraw_decimal)

    debit_title = 'SPOT' 
    debit_amount = {f'{withdraw_token}': str(withdraw_amount)}
    debit_from = contract_address
    debit_to =  user_address
    credit_title = 'STAKING'
    credit_amount = {f'{withdraw_token}': str(withdraw_amount)}
    credit_from = user_address
    credit_to = contract_address
    comment = 'uniswap staking withdraw'

    caaj = {
          'time':           time,
          'platform':       PLATFORM,
          'transaction_id': transaction_id,
          'debit_title':    debit_title,
          'debit_amount':   debit_amount,
          'debit_from':     debit_from,
          'debit_to':       debit_to,
          'credit_title':   credit_title,
          'credit_amount':  credit_amount,
          'credit_from':    credit_from,
          'credit_to':      credit_to,
          'comment':        comment
        }
    caajs.append(caaj)

  if len(list(filter(lambda item: item['topics'][0].hex() == V2_REWARDPAID_TOPIC, logs))) > 0:
    try:
      reward_transfer = list(filter(lambda item: (item['topics'][0].hex().lower() == ERC20_TRANSFER_TOPIC and '0x' + item['topics'][2].hex().lower()[26:] == user_address and item['address'].lower() == UNI_CONTRACT_ADDRESS), logs))[0]
    except IndexError as e:
      print('Cant find reward token transfer')
      raise e

    reward_amount = Decimal(int(reward_transfer['data'], 0)) / WEI

    debit_title = 'SPOT' 
    debit_amount = {f'{UNI_CONTRACT_ADDRESS}': str(reward_amount)}
    debit_from = contract_address
    debit_to =  user_address
    credit_title = 'STAKINGREWARD'
    credit_amount = {f'{UNI_CONTRACT_ADDRESS}': str(reward_amount)}
    credit_from = user_address
    credit_to = contract_address
    comment = 'uniswap staking reward'

    caaj = {
          'time':           time,
          'transaction_id': transaction_id,
          'platform':       PLATFORM,
          'debit_title':    debit_title,
          'debit_amount':   debit_amount,
          'debit_from':     debit_from,
          'debit_to':       debit_to,
          'credit_title':   credit_title,
          'credit_amount':  credit_amount,
          'credit_from':    credit_from,
          'credit_to':      credit_to,
          'comment':        comment
        }
    caajs.append(caaj)

  return caajs

def v3_liquidity_add_to_caaj(logs, time, transaction_id, contract_address, user_address):
  increaseliquidity = list(filter(lambda item: item['topics'][0].hex()  == V3_INCREASELIQUIDITY_TOPIC, logs))[0]

  transfers = list(filter(lambda item: (item['topics'][0].hex().lower() == ERC20_TRANSFER_TOPIC and '0x' + item['topics'][1].hex().lower()[26:] == user_address) or (item['address'].lower() == WETH_CONTRACT_ADDRESS and item['topics'][0].hex().lower() == WETH_DEPOSIT_TOPIC), logs))

  credit_amount = {}
  for transfer in transfers:
    token = transfer['address'].lower() if transfer['address'].lower() != WETH_CONTRACT_ADDRESS else 'ETH'
    decimal = get_erc20_decimals(transfer['address'].lower())
    amount = Decimal(int(transfer['data'], 0)) / pow(10, decimal)
    credit_amount[f'{token}'] = str(amount)

  increaseliquidity_data = increaseliquidity['data'].replace('0x', '')
  increaseliquidity_data = [increaseliquidity_data[i: i+DATA_EACH_LENGTH] for i in range(0, len(increaseliquidity_data), DATA_EACH_LENGTH)]
  increaseliquidity_data = list(map(lambda item: '0x' + item, increaseliquidity_data))

  liquidity_token =  increaseliquidity['address'].lower() + '_' + str(int(increaseliquidity['topics'][1].hex(), 0))
  liquidity_amount = int(increaseliquidity_data[0], 0)

  debit_title = 'LIQUIDITY' 
  debit_from = contract_address
  debit_to =  user_address
  debit_amount = {f'{liquidity_token}': str(liquidity_amount)}
  credit_title = 'SPOT'
  credit_from = user_address
  credit_to = contract_address
  credit_amount = credit_amount #{f'{input_a_token}': str(input_a_amount), f'{input_b_token}': str(input_b_amount)}
  comment = 'uniswap add liquidity'

  caaj = {
        'time':           time,
        'platform':       PLATFORM,
        'transaction_id': transaction_id,
        'debit_title':    debit_title,
        'debit_amount':   debit_amount,
        'debit_from':     debit_from,
        'debit_to':       debit_to,
        'credit_title':   credit_title,
        'credit_amount':  credit_amount,
        'credit_from':    credit_from,
        'credit_to':      credit_to,
        'comment':        comment
      }
  return caaj

def v3_liquidity_remove_to_caaj(logs, time, transaction_id, contract_address, user_address):
  try:
    decreaseliquidity = list(filter(lambda item: item['topics'][0].hex()  == V3_DECREASELIQUIDITY_TOPIC, logs))[0]
  except IndexError:
    decreaseliquidity = None

  transfers = list(filter(lambda item: (item['topics'][0].hex().lower() == ERC20_TRANSFER_TOPIC and '0x' + item['topics'][2].hex().lower()[26:] == user_address) or (item['address'].lower() == WETH_CONTRACT_ADDRESS and item['topics'][0].hex().lower() == WETH_WITHDRAWAL_TOPIC), logs))

  debit_amount = {}
  for transfer in transfers:
    token = transfer['address'].lower() if transfer['address'].lower() != WETH_CONTRACT_ADDRESS else 'ETH'
    decimal = get_erc20_decimals(transfer['address'].lower())
    amount = Decimal(int(transfer['data'], 0)) / pow(10, decimal)
    debit_amount[f'{token}'] = str(amount)

  if decreaseliquidity != None:
    decreaseliquidity_data = decreaseliquidity['data'].replace('0x', '')
    decreaseliquidity_data = [decreaseliquidity_data[i: i+DATA_EACH_LENGTH] for i in range(0, len(decreaseliquidity_data), DATA_EACH_LENGTH)]
    decreaseliquidity_data = list(map(lambda item: '0x' + item, decreaseliquidity_data))
    liquidity_token =  decreaseliquidity['address'].lower() + '_' + str(int(decreaseliquidity['topics'][1].hex(), 0))
    liquidity_amount = int(decreaseliquidity_data[0], 0) 

  debit_title = 'SPOT'
  debit_from = user_address
  debit_to = contract_address
  debit_amount = debit_amount #{f'{a_token}': str(a_amount), f'{b_token}': str(b_amount)}
  credit_title = 'LIQUIDITY' 
  credit_from = contract_address
  credit_to =  user_address
  credit_amount = {f'{liquidity_token}': str(liquidity_amount)} if decreaseliquidity != None else {}
  comment = 'uniswap remove liquidity'

  caaj = {
        'time':           time,
        'platform':       PLATFORM,
        'transaction_id': transaction_id,
        'debit_title':    debit_title,
        'debit_amount':   debit_amount,
        'debit_from':     debit_from,
        'debit_to':       debit_to,
        'credit_title':   credit_title,
        'credit_amount':  credit_amount,
        'credit_from':    credit_from,
        'credit_to':      credit_to,
        'comment':        comment
      }

  return caaj


def v3_swap_liquidity_to_caaj(tx, user_address):
  tx_hash = tx['hash']
  print(tx_hash)

  tx_detail = web3.eth.waitForTransactionReceipt(tx_hash)
  logs = tx_detail['logs']

  time = str(dt.fromtimestamp(int(tx['timeStamp'])))
  transaction_id = tx_hash


  time = str(dt.fromtimestamp(int(tx['timeStamp'])))
  transaction_id = tx_hash 

  contract_address = tx['to'].lower()

  caaj = None
  if len(list(filter(lambda item: item['topics'][0].hex() == V3_INCREASELIQUIDITY_TOPIC, logs))) > 0:
    caaj = v3_liquidity_add_to_caaj(logs, time, transaction_id, contract_address, user_address)
  elif len(list(filter(lambda item: item['topics'][0].hex() == V3_COLLECT_TOPIC, logs))) > 0:
    caaj = v3_liquidity_remove_to_caaj(logs, time, transaction_id, contract_address, user_address)
  else:
    caaj = swap_to_caaj(logs, time, transaction_id, contract_address, user_address)
  return caaj

def uniswap_to_caaj(tx, user_address):
  to = tx['to']
  transaction_id = tx['hash']
  caajs = []

  time = str(dt.fromtimestamp(int(tx['timeStamp'])))
  transaction_fee = str(Decimal(tx['gasUsed']) * Decimal(tx['gasPrice']) / WEI)
  
  if to in UNISWAP_V2_STAKING_POOL_CONTRACT_ADDRESSES:
    caajs.extend(v2_staking_to_caaj(tx, user_address))
  elif to in UNISWAP_V2_SWAP_CONTRASCT_ADDRESS:
    caajs.append(v2_swap_liquidity_to_caaj(tx, user_address))
  elif to in UNISWAP_V3_SWAP_CONTRASCT_ADDRESS:
    caajs.append(v3_swap_liquidity_to_caaj(tx, user_address))

  caajs.append(get_fee_caaj(time, user_address, transaction_id, transaction_fee, 'uniswap transaction fee'))

  return caajs

def output_caaj(caajs):
  df = pd.DataFrame(caajs)
  df = df.sort_values('time')
  print(df)
  result_file_name = '%s/../output/uniswap_caaj.csv' %  os.path.dirname(__file__)
  df.to_csv(result_file_name, index=False, columns=['time', 'platform', 'transaction_id', 'debit_title', 'debit_amount', 'debit_from', 'debit_to', 'credit_title', 'credit_amount', 'credit_from', 'credit_to', 'comment'])

def get_erc20_decimals(address):
  contract = web3.eth.contract(address=Web3.toChecksumAddress(address), abi=erc20_abi)
  decimal = contract.functions.decimals().call()

  return Decimal(decimal)

def is_approve(tx):
  tx_detail = web3.eth.waitForTransactionReceipt(tx['hash'])
  logs = tx_detail['logs']
  result = False
  if len(logs) == 1 and logs[0]['topics'][0].hex().lower() == ERC20_APPROVE_TOPIC:
    result = True

  return result

def get_fee_caaj(time, user_address, transaction_id, transaction_fee, comment):
  caaj = {
        'time':           time,
        'platform':       PLATFORM,
        'transaction_id': transaction_id,
        'debit_title':    'FEE',
        'debit_amount':   {'ETH': transaction_fee},
        'debit_from':     '0x0000000000000000000000000000000000000000',
        'debit_to':       user_address,
        'credit_title':   'SPOT',
        'credit_amount':  {'ETH': transaction_fee},
        'credit_from':    user_address,
        'credit_to':      '0x0000000000000000000000000000000000000000',
        'comment':         comment
      }
  return caaj


def main():
  caajs = []

  address = sys.argv[1].lower()

  txs = ethscan.get_normal_txs_by_address(address=address, startblock=0, endblock='latest', sort='asc')

  for tx in txs:
    if '1' in tx['isError']:
      continue
    elif is_uniswap(tx['to']):
      caajs.extend(uniswap_to_caaj(tx, address))
    elif is_approve(tx):
      caaj = get_fee_caaj(str(dt.fromtimestamp(int(tx['timeStamp']))), address, tx['hash'], str(Decimal(tx['gasUsed']) * Decimal(tx['gasPrice']) / WEI), 'approve transaction fee')
      caajs.append(caaj)

  output_caaj(caajs)
  #print(caajs)

if __name__== '__main__':
    main()

