import time
import requests
from hexbytes import HexBytes
from constant import *
import csv


def get_eth_balance(wallet_address):
    try:
        eth_balance = ETH_WEB3.eth.getBalance(wallet_address)
        eth_balance = ETH_WEB3.fromWei(eth_balance, 'ether')
        return float(eth_balance)
    except Exception as e:
        print("get_eth_balance:" + str(e))
        return 0


def get_gas_price(level):
    while True:
        try:
            res = requests.get(ETH_GAS_URL).json()
            return int(res[level] / 10)
        except Exception as e:
            print("get_gas_price:" + str(e))
            time.sleep(1)


def transfer_eth(source_address, source_private_key, dest_address, amount, gas_limit, gas_price, wait=False):
    result = {'code': -1, 'tx': None, 'message': ''}
    try:
        # ---------- sign and do transaction ---------- #
        signed_txn = ETH_WEB3.eth.account.signTransaction(dict(
                        nonce=ETH_WEB3.eth.getTransactionCount(source_address),
                        gasPrice=ETH_WEB3.toWei(gas_price, 'gwei'),
                        gas=gas_limit,
                        to=dest_address,
                        value=amount
                      ), private_key=source_private_key)
        txn_hash = ETH_WEB3.eth.sendRawTransaction(signed_txn.rawTransaction)

        if wait is True:
            txn_receipt = ETH_WEB3.eth.waitForTransactionReceipt(txn_hash, ETH_LIMIT_WAIT_TIME)
            if txn_receipt is None or 'status' not in txn_receipt or txn_receipt['status'] != 1 or 'transactionIndex' not in txn_receipt:
                result['code'] = -4
                result['message'] = 'waiting failed'
                result['tx'] = txn_hash.hex()
                return result
        result['code'] = 0
        result['message'] = ''
        result['tx'] = txn_hash.hex()
        return result
    except Exception as e:
        # print("transfer_eth:" + str(e))
        result['code'] = -2
        result['message'] = str(e)
        result['tx'] = None
        return result


def get_address_from_csv(filename):
    result = []
    try:
        with open(filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                    continue
                else:
                    address = {'address': row[0], 'private': row[1]}
                    result.append(address)
                    line_count += 1
    except Exception as e:
        print("get_address_from_csv exception: " + str(e))
    return result


def calc_exact_eth_dst_amount(address, gas_price):
    while True:
        try:
            eth_balance = ETH_WEB3.eth.getBalance(address)
            eth_limit = ETH_GAS_MIN_LIMIT * ETH_WEB3.toWei(gas_price, 'gwei')
            eth_dst_wei = eth_balance - eth_limit
            if eth_dst_wei <= 0:
                print("source address:" + address + " not enough balance, eth:" + str(eth_balance) + " wei, gas_limit:" + str(eth_limit) + " wei skipping...")
                return 0
            # dst_amt = float(ETH_WEB3.fromWei(eth_dst_wei, 'ether'))
            return eth_dst_wei
        except Exception as e:
            print("calc_exact_eth_dst_amount:" + str(e))
            time.sleep(1)


def send_multi_addresses():
    try:
        gas_price = get_gas_price(ETH_GAS_LEVEL)
        print("send_multi_addresses: gas_price: " + str(gas_price))
        addresses = get_address_from_csv(SOURCE_FILE_NAME)
        if len(addresses) <= 0:
            print("send_multi_addresses: source address list is empty")
            return
        if DEST_ADDRESS == '':
            print("send_multi_addresses: destination address doesn't defined")
            return
        for item in addresses:
            value = 0
            try:
                value = calc_exact_eth_dst_amount(item['address'], gas_price)
                if value <= 0:
                    time.sleep(SLEEP_TIME_PER_ADDRESS)
                    continue
                print('send_multi_addresses: source_private:' + item['private'] + ', amount:' + str(
                    value) + ' wei, gas_price:' + str(gas_price))
                res = transfer_eth(item['address'], HexBytes(item['private']), DEST_ADDRESS, value, ETH_GAS_MIN_LIMIT, gas_price,
                                   IS_WAIT_FOR_CONFIRM)
                if res['code'] != 0:
                    print('send_multi_addresses:' + res['message'])
                else:
                    print('send_multi_addresses: tx:' + res['tx'])
            except Exception as e:
                print('send_multi_addresses: source_private:' + item['private'] + ', amount:' + str(
                        value) + ', gas_price:' + str(gas_price) + " exception:" + str(e))
            time.sleep(SLEEP_TIME_PER_ADDRESS)
    except Exception as e:
        print("send_multi_addresses exception:" + str(e))


if __name__ == '__main__':
    send_multi_addresses()
