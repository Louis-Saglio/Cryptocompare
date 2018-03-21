import json
import threading
import time
from typing import Iterable, Tuple

import requests


# todo : remove default values in core lib
# todo : data display return string
# todo : unittest
# todo : resource
# todo : sigterm sigint


class CryptoNameError(BaseException):
    pass


# Data acquisition

def get_crypto_list() -> Tuple[str]:
    return tuple(json.loads(requests.get("https://www.cryptocompare.com/api/data/coinlist/").content)["Data"].keys())


def get_crypto_price(crypto: str, convert_to: str='EUR') -> float:
    # noinspection SpellCheckingInspection
    data = json.loads(requests.get(f"https://min-api.cryptocompare.com/data/price?fsym={crypto}&tsyms={convert_to}").content)
    if data.get("Response") == "Error":
        raise CryptoNameError(f"CryptoCompare does not have data for {crypto}")
    try:
        return data[convert_to]
    except KeyError as e:
        raise CryptoNameError(f"Bad crypto name, {e}")


# Data displaying

def print_crypto_list(crypto_list: Iterable[str]) -> None:
    crypto_list = sorted(crypto_list, key=lambda x: x.lower())
    rep = str()
    max_size = len(max(crypto_list, key=lambda x: len(x)))
    for crypto in crypto_list:
        if len(rep) < 160:
            rep += crypto.ljust(max_size + 2)
        else:
            print(rep)
            rep = str()


def print_crypto_price(from_crypto: str, price: float, to_crypto: str="EUR") -> None:
    print(f"On {time.strftime('%D at %H:%M:%S')}\t 1 {from_crypto} = {price} {to_crypto}")


# User data acquisition

def input_action() -> str:
    action = input("-" * 50 + "\nChoose an action :\n1) Display crypto list\n2) Choose a crypto\n3) Exit\n>>> ")
    if action in "123":
        return action
    print("Bad action chosen")
    input_action()


def input_crypto() -> str:
    crypto_list = set()
    thread = threading.Thread(target=lambda mutable: mutable.add(get_crypto_list()), args=(crypto_list,))
    thread.start()
    crypto = input("Choose a crypto >>> ")
    thread.join()
    if crypto in crypto_list.pop():
        return crypto
    print(f"Crypto not available : {crypto}")
    input_crypto()


def main():
    action = input_action()
    if action == "1":
        print_crypto_list(get_crypto_list())
    elif action == "2":
        from_crypto = input_crypto()
        to_crypto = "EUR"
        try:
            price = get_crypto_price(from_crypto, to_crypto)
        except CryptoNameError:
            print("An error occured, please try again")
            return
        print_crypto_price(from_crypto, price, to_crypto)
    elif action == "3":
        exit(0)


if __name__ == '__main__':
    while True:
        main()
