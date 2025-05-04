import asyncio
import json
import os
from collections import defaultdict
from datetime import datetime
from typing import List, Tuple

import aiohttp
from web3 import AsyncHTTPProvider, AsyncWeb3

from core.conf.environ import env

# === Конфигурация ===
RPC_URL = "https://polygon-rpc.com"
POLYGONSCAN_API_KEY = env("POLYGONSCAN_API_KEY")
TOKEN_ADDRESS = AsyncWeb3.to_checksum_address("0x1a9b54a3075119f1546c52ca0940551a6ce5d2d0")

# === Загрузка ABI ===
ABI_PATH = os.path.join(os.path.dirname(__file__), "abi", "erc20.json")
if not os.path.exists(ABI_PATH):
    raise FileNotFoundError(f"Файл ABI не найден: {ABI_PATH}")
with open(ABI_PATH, "r") as f:
    ERC20_ABI = json.load(f)

# === Настройка Web3 ===
web3 = AsyncWeb3(AsyncHTTPProvider(RPC_URL)) 
token_contract = web3.eth.contract(address=TOKEN_ADDRESS, abi=ERC20_ABI)

async def format_balance(balance_raw: int) -> float:
    """
    Преобразует баланс из "сырого" формата в удобочитаемый, учитывая десятичные знаки токена.
    :param balance_raw: Баланс в "сыром" формате (целое число).
    :return: Баланс в удобочитаемом формате (дробное число с учётом десятичных знаков).
    """
    try:
        decimals = await token_contract.functions.decimals().call()
        return balance_raw / (10 ** decimals)
    except Exception as e:
        raise ValueError(f"Ошибка при получении десятичных знаков токена: {str(e)}")

class BlockchainService:
    """
    Сервис для взаимодействия с блокчейном Polygon.
    """

    @staticmethod
    async def get_balance(address: str) -> float:
        """
        Асинхронно получает баланс токена для указанного адреса.
        :param address: Адрес Polygon (строка в формате '0x...').
        :return: Баланс в удобочитаемом формате (с учетом десятичных знаков).
        """
        try:
            checksum_address = AsyncWeb3.to_checksum_address(address)
            balance_raw = await token_contract.functions.balanceOf(checksum_address).call()
            return await format_balance(balance_raw)
        except Exception as e:
            raise ValueError(f"Ошибка при получении баланса: {str(e)}")

    @staticmethod
    async def get_balances_batch(addresses: List[str]) -> List[float]:
        """
        Асинхронно получает балансы токенов для списка адресов.
        :param addresses: Список адресов Polygon (List[str]).
        :return: Список балансов в удобочитаемом формате.
        """
        try:
            tasks = [BlockchainService.get_balance(addr) for addr in addresses]
            return await asyncio.gather(*tasks)
        except Exception as e:
            raise ValueError(f"Ошибка при получении балансов пакета: {str(e)}")

    @staticmethod
    async def get_top_holders(n: int) -> List[Tuple[str, float]]:
        """
        Получает топ N адресов по балансам токенов через PolygonScan.
        :param n: Количество топовых адресов.
        :return: Список кортежей (адрес, баланс).
        """
        url = "https://api.polygonscan.com/api"
        params = {
            "module": "account",
            "action": "tokentx",
            "contractaddress": TOKEN_ADDRESS,
            "startblock": 0,
            "endblock": 99999999,
            "sort": "asc",
            "apikey": POLYGONSCAN_API_KEY,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()

        if data["status"] != "1":
            raise ValueError(f"Ошибка получения данных из PolygonScan: {data.get('message')}")

        txs = data["result"]
        balances = defaultdict(int)
        last_transactions = {}

        for tx in txs:
            sender = tx["from"]
            receiver = tx["to"]
            value = int(tx["value"])
            timestamp = int(tx["timeStamp"])

            if sender != "0x" * 40:
                balances[sender] -= value
            if receiver != "0x" * 40:
                balances[receiver] += value
                last_transactions[receiver] = max(last_transactions.get(receiver, 0), timestamp)

        non_zero_balances = {addr: bal for addr, bal in balances.items() if bal > 0}
        sorted_balances = sorted(non_zero_balances.items(), key=lambda x: x[1], reverse=True)[:n]
        formatted_balances = [(addr, await format_balance(bal)) for addr, bal in sorted_balances]
        return formatted_balances

    @staticmethod
    async def get_top_holders_with_transactions(n: int) -> List[Tuple[str, float, str]]:
        """
        Получает топ N адресов по балансам токенов с датами последних транзакций.
        :param n: Количество топовых адресов.
        :return: Список кортежей (адрес, баланс, дата последней транзакции).
        """
        top_holders = await BlockchainService.get_top_holders(n)
        top_addresses = [addr for addr, _ in top_holders]
        
        url = "https://api.polygonscan.com/api"
        params = {
            "module": "account",
            "action": "tokentx",
            "contractaddress": TOKEN_ADDRESS,
            "startblock": 0,
            "endblock": 99999999,
            "sort": "asc",
            "apikey": POLYGONSCAN_API_KEY,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()

        if data["status"] != "1":
            raise ValueError(f"Ошибка получения данных из PolygonScan: {data.get('message')}")

        txs = data["result"]
        last_transactions = {}
        for tx in txs:
            addr = tx["to"]
            timestamp = int(tx["timeStamp"])
            if addr in top_addresses:
                last_transactions[addr] = max(last_transactions.get(addr, 0), timestamp)

        result = []
        for addr, bal in top_holders:
            last_tx_time = last_transactions.get(addr)
            if last_tx_time:
                last_tx_time = datetime.utcfromtimestamp(last_tx_time)
            else:
                last_tx_time = None  

            result.append((addr, bal, last_tx_time))

        return result

    @staticmethod
    async def get_token_info() -> dict:
        """
        Получает информацию о токене.
        :return: Словарь с информацией о токене.
        """
        name = await token_contract.functions.name().call()
        symbol = await token_contract.functions.symbol().call()
        total_supply = await token_contract.functions.totalSupply().call()
        return {
            "name": name,
            "symbol": symbol,
            "totalSupply": await format_balance(total_supply),
        }