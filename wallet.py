# Import dependencies
import subprocess
import json
from dotenv import load_dotenv
import os
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI
from constants import *

# Load and set environment variables
load_dotenv()
mnemonic = os.getenv('mnemonic', 'filter ugly hazard moral hollow joke moment width settle silver shove crush')

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))


#Derviving the wallet keys
def derive_wallets(mnemonic, coin, numderive):
    
    command = f'./derive -g --mnemonic="{mnemonic}" --coin="{coin}" --numderive="{numderive}" --cols=address,index,path,address,privkey,pubkey,pubkeyhash,xprv,xpub --format=json'
    
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    return json.loads(output)
    
coins = {
    "btc-test" : derive_wallets(mnemonic, BTCTEST, 3),
    "eth": derive_wallets(mnemonic, ETH, 3)
    }

#Linking the transaction signing libraries

def priv_key_to_account(coin, priv_key):
    
    if(coin == 'eth'):
        return Account.privateKeyToAccount(priv_key)
    elif(coin == 'btc-test'):
        return PrivateKeyTestnet(priv_key)

    


def create_tx(coin, account, to, amount):
    
    if(coin =='eth'):
        gas_estimate = w3.eth.estimateGas({'from': account.address, 'to': to, 'value': amount})
        
        return {'from': account.address, 'to': to, 'value': amount, 'gasPrice': w3.eth.gasPrice, 'gas': gas_estimate, 'nonce': w3.eth.getTransactionCount(account.address)}
    
    elif(coin == 'btc-test'):
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])

    
    
    

def send_tx(coin, account, to, amount):
    raw_tx = create_tx(coin, account, to, amount)
    signed = account.sign_transaction(raw_tx)
    if(coin == 'eth'):
        return w3.eth.sendRawTransaction(signed.rawTransaction)
    elif(coin == 'btc-test'):
        return NetworkAPI.broadcast_tx_testnet(signed)
   

    
eth_sender_account = priv_key_to_account(ETH,coins["eth"][0]['privkey'])
eth_recipient_address = coins["eth"][1]["address"]


send_tx(ETH, eth_sender_account, eth_recipient_address, 2)

btctest_sender_account = priv_key_to_account(BTCTEST,coins["btc-test"][0]['privkey'])
btctest_recipient_address = coins["btc-test"][1]["address"]

send_tx(BTCTEST, btctest_sender_account, btctest_recipient_address, .0001)
    
    