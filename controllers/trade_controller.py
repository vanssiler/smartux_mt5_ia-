from services import mt5_service
import MetaTrader5 as mt5

def place_order(symbol, action_type, usd_volume, usd_sl, usd_tp, deviation, comment):
    # 1. Ativa o símbolo via mt5 (direto)
    if not mt5.symbol_select(symbol, True):
        print(f"[ERRO] Não foi possível ativar o símbolo: {symbol}")
        # MAS: tenta seguir com o symbol_info mesmo assim
    else:
        print(f"[INFO] Símbolo '{symbol}' ativado com sucesso")

    # 2. Busca informações
    symbol_info = mt5_service.get_symbol_info(symbol)
    tick = mt5_service.get_tick(symbol)

    if not symbol_info:
        return False, f"❌ Não foi possível obter symbol_info de '{symbol}'"
    if not tick or tick.ask == 0 or tick.bid == 0:
        return False, f"❌ Cotação inválida para '{symbol}'"

    # 3. Parâmetros principais
    price = tick.ask if action_type == mt5_service.get_constants()["ORDER_TYPE_BUY"] else tick.bid
    point = symbol_info.point
    digits = symbol_info.digits

    # 4. Calcula valor do pip
    if symbol.endswith("USD"):
        pip_value_per_lot = 10.0
    elif symbol.startswith("USD"):
        pip_value_per_lot = 10.0 / price
    else:
        pip_value_per_lot = 10.0 * price

    try:
        volume = usd_volume / pip_value_per_lot
        volume = round(volume, 2)
        volume = max(symbol_info.volume_min, min(symbol_info.volume_max, volume))

        sl_pips = usd_sl / (pip_value_per_lot * volume) if usd_sl > 0 else 0
        tp_pips = usd_tp / (pip_value_per_lot * volume) if usd_tp > 0 else 0

        points_per_pip = 10 if digits in [3, 5] else 1
        sl_points = int(sl_pips * points_per_pip)
        tp_points = int(tp_pips * points_per_pip)
    except ZeroDivisionError:
        return False, "Erro: cálculo de pip ou volume inválido."

    # 5. Stop Level mínimo
    min_points = symbol_info.trade_stops_level + 5
    min_price_distance = min_points * point

    if action_type == mt5_service.get_constants()["ORDER_TYPE_BUY"]:
        sl_price = round(price - sl_points * point, digits) if sl_points > 0 else 0
        tp_price = round(price + tp_points * point, digits) if tp_points > 0 else 0
    else:
        sl_price = round(price + sl_points * point, digits) if sl_points > 0 else 0
        tp_price = round(price - tp_points * point, digits) if tp_points > 0 else 0

    # Valida distâncias
    if sl_price and abs(price - sl_price) < min_price_distance:
        return False, f"❌ SL muito próximo ({min_points} pts mínimo)"
    if tp_price and abs(tp_price - price) < min_price_distance:
        return False, f"❌ TP muito próximo ({min_points} pts mínimo)"

    # 6. Envia a ordem
    request = {
        "action": mt5_service.get_constants()["TRADE_ACTION_DEAL"],
        "symbol": symbol,
        "volume": volume,
        "type": action_type,
        "price": price,
        "sl": sl_price,
        "tp": tp_price,
        "deviation": deviation,
        "magic": 123456,
        "comment": comment,
        "type_time": mt5_service.get_constants()["ORDER_TIME_GTC"],
        "type_filling": symbol_info.filling_mode  # melhor que forçar IOC
    }

    print("[DEBUG] Ordem:", request)

    result = mt5_service.send_order(request)
    if result is None:
        return False, "❌ Ordem não enviada"

    if result.retcode == mt5_service.get_constants()["TRADE_RETCODE_DONE"]:
        return True, f"✅ Ordem executada: {volume:.2f} lots @ {price:.{digits}f}"
    else:
        return False, f"❌ Erro na ordem: {result.retcode} - {result.comment}"
