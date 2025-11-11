import os
import json
from dotenv import load_dotenv
from binance.client import Client
from binance import ThreadedWebsocketManager
from binance.enums import *

class GridBotLogic:
    def __init__(self, settings_path='../settings.json'):
        load_dotenv()
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET')
        self.client = Client(self.api_key, self.api_secret)
        self.settings = self.load_settings(settings_path)
        self.ws_manager = None
        self.live_prices = {symbol: None for symbol in self.settings['symbols']}

    def load_settings(self, path):
        with open(path, 'r') as f:
            return json.load(f)

    def get_current_price(self, symbol):
        ticker = self.client.get_symbol_ticker(symbol=symbol)
        return float(ticker['price'])

    def get_open_orders(self, symbol):
        return self.client.get_open_orders(symbol=symbol)

    def get_klines(self, symbol, interval=None, limit=100):
        if interval is None:
            interval = self.settings['kline_interval']
        return self.client.get_klines(symbol=symbol, interval=interval, limit=limit)

    def start_price_websocket(self, on_message):
        self.ws_manager = ThreadedWebsocketManager(api_key=self.api_key, api_secret=self.api_secret)
        self.ws_manager.start()
        for symbol in self.settings['symbols']:
            self.ws_manager.start_symbol_ticker_socket(callback=lambda msg, s=symbol: on_message(s, msg), symbol=symbol)

    def stop_websocket(self):
        if self.ws_manager:
            self.ws_manager.stop()

    # Add grid trading logic here (place orders, manage grid, etc.)

# Example usage:
# logic = GridBotLogic()
# print(logic.get_current_price('BTCUSDT'))
