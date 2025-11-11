import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QDockWidget, QListWidget, QWidget, QVBoxLayout, QLabel, QMenuBar, QAction, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
import pyqtgraph as pg
from trade_logic import GridBotLogic

class SymbolListWidget(QListWidget):
    def __init__(self, logic):
        super().__init__()
        self.logic = logic
        self.symbols = logic.settings['symbols']
        self.refresh()

    def refresh(self):
        self.clear()
        for symbol in self.symbols:
            price = self.logic.live_prices.get(symbol, '...')
            self.addItem(f"{symbol}: {price}")

class KlineChartWidget(QWidget):
    def __init__(self, logic, symbol):
        super().__init__()
        self.logic = logic
        self.symbol = symbol
        self.plot_widget = pg.PlotWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)
        self.refresh_chart()

    def refresh_chart(self):
        klines = self.logic.get_klines(self.symbol, limit=60)
        prices = [float(k[4]) for k in klines]  # close prices
        self.plot_widget.clear()
        self.plot_widget.plot(prices, pen='g')
        # TODO: Draw gridlines for buy/sell orders

class TradesOverviewWidget(QWidget):
    def __init__(self, logic):
        super().__init__()
        self.logic = logic
        self.label = QLabel("Live Trades:")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.refresh()

    def refresh(self):
        # TODO: Show live trades from logic
        self.label.setText("Live Trades: (not implemented)")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logic = GridBotLogic()
        self.setWindowTitle("Binance Grid Bot")
        self.resize(1200, 800)
        self.init_ui()
        self.logic.start_price_websocket(self.on_price_update)
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_ui)
        self.timer.start(2000)

    def init_ui(self):
        # Symbol List Dock
        self.symbol_list = SymbolListWidget(self.logic)
        dock_symbols = QDockWidget("Symbols", self)
        dock_symbols.setWidget(self.symbol_list)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock_symbols)

        # Kline Chart Dock(s)
        self.kline_charts = []
        for symbol in self.logic.settings['symbols']:
            chart = KlineChartWidget(self.logic, symbol)
            dock_chart = QDockWidget(f"Kline Chart: {symbol}", self)
            dock_chart.setWidget(chart)
            self.addDockWidget(Qt.BottomDockWidgetArea, dock_chart)
            self.kline_charts.append(chart)

        # Trades Overview Dock
        self.trades_overview = TradesOverviewWidget(self.logic)
        dock_trades = QDockWidget("Live Trades", self)
        dock_trades.setWidget(self.trades_overview)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_trades)

        # Menu
        menubar = self.menuBar()
        settings_menu = menubar.addMenu('Settings')
        timeframe_action = QAction('Set Chart Timeframe', self)
        settings_menu.addAction(timeframe_action)
        # TODO: Connect menu actions

    def on_price_update(self, symbol, msg):
        if 'c' in msg:
            self.logic.live_prices[symbol] = msg['c']

    def refresh_ui(self):
        self.symbol_list.refresh()
        for chart in self.kline_charts:
            chart.refresh_chart()
        self.trades_overview.refresh()

    def closeEvent(self, event):
        self.logic.stop_websocket()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
