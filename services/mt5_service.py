import MetaTrader5 as mt5
import time
import pandas as pd
from datetime import datetime, timedelta  # ✅ Import necessário

def initialize():
    if not mt5.initialize():
        print(f"MT5 initialization failed: {mt5.last_error()}")
        return False
    return True

def shutdown():
    mt5.shutdown()

def is_connected():
    return mt5.terminal_info() is not None

def reconnect():
    shutdown()
    time.sleep(1)
    return initialize()

def get_account_info():
    if not is_connected() and not initialize():
        return None
    return mt5.account_info()

def get_symbol_info(symbol):
    if not is_connected():
        initialize()
    return mt5.symbol_info(symbol)

def get_tick(symbol):
    return mt5.symbol_info_tick(symbol)

def select_symbol(symbol):
    return mt5.symbol_select(symbol, True)

def copy_rates(symbol, timeframe, bars):
    if not mt5.initialize():
        print("[MT5] Falha ao inicializar MT5.")
        return None

    # Seleciona o símbolo
    info = mt5.symbol_info(symbol)
    if info is None:
        print(f"[MT5] Símbolo '{symbol}' não encontrado.")
        return None

    if not info.visible:
        print(f"[MT5] Símbolo '{symbol}' não está visível. Tentando ativar...")
        if not mt5.symbol_select(symbol, True):
            print(f"[MT5] Não foi possível ativar '{symbol}'.")
            return None

    utc_from = datetime.now() - timedelta(minutes=bars * 5)
    rates = mt5.copy_rates_from(symbol, timeframe, utc_from, bars)

    if rates is None or len(rates) == 0:
        print(f"[MT5] Nenhum dado recebido para {symbol}.")
        return None

    return rates


def send_order(request):
    return mt5.order_send(request)

def get_last_error():
    return mt5.last_error()

def get_constants():
    return {
        "ORDER_TYPE_BUY": mt5.ORDER_TYPE_BUY,
        "ORDER_TYPE_SELL": mt5.ORDER_TYPE_SELL,
        "TRADE_ACTION_DEAL": mt5.TRADE_ACTION_DEAL,
        "ORDER_TIME_GTC": mt5.ORDER_TIME_GTC,
        "ORDER_FILLING_IOC": mt5.ORDER_FILLING_IOC,
        "TRADE_RETCODE_DONE": mt5.TRADE_RETCODE_DONE,
        "TRADE_RETCODE_REQUOTE": mt5.TRADE_RETCODE_REQUOTE,
    }

def get_open_positions():
    if not mt5.initialize():
        return []
    positions = mt5.positions_get()
    mt5.shutdown()
    return positions if positions else []

def close_position(ticket):
    position = mt5.positions_get(ticket=ticket)
    if not position or len(position) == 0:
        return False, f"Position {ticket} not found."

    pos = position[0]
    symbol = pos.symbol
    volume = pos.volume
    order_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
    price = mt5.symbol_info_tick(symbol).bid if order_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(symbol).ask

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "position": ticket,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "deviation": 20,
        "magic": 123456,
        "comment": "Closed by SmartUx",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        return True, f"Position {ticket} closed successfully."
    else:
        return False, f"Failed to close position {ticket}: {result.comment}"

# ✅ Método atualizado para análise com IA + compatível com gráfico
def get_symbol_data(symbol, timeframe=mt5.TIMEFRAME_M5, n=100):
    if not mt5.initialize():
        print("[MT5] Erro ao inicializar:", mt5.last_error())
        return pd.DataFrame()

    # Verifica se o símbolo existe
    info = mt5.symbol_info(symbol)
    if info is None:
        print(f"[MT5] Símbolo '{symbol}' não encontrado.")
        return pd.DataFrame()

    # Seleciona o símbolo
    if not info.visible:
        print(f"[MT5] Símbolo '{symbol}' não está visível. Tentando ativar...")
        if not mt5.symbol_select(symbol, True):
            print(f"[MT5] Não foi possível ativar '{symbol}'.")
            return pd.DataFrame()
        else:
            print(f"[MT5] Símbolo '{symbol}' ativado com sucesso.")

    print(f"[MT5] Buscando dados para '{symbol}'...")

    utc_from = datetime.now() - timedelta(minutes=n * 5)
    rates = mt5.copy_rates_from(symbol, timeframe, utc_from, n)

    if rates is None or len(rates) == 0:
        print(f"[MT5] Nenhum dado retornado para '{symbol}' ({mt5.last_error()})")
        return pd.DataFrame()

    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    print(f"[MT5] Recebidos {len(df)} candles para '{symbol}'")

    return df

