import time
from datetime import datetime
from services import mt5_service
from controllers.ml_controller import MLController


class AutoTrader:
    def __init__(self, symbol, ml_controller, smartux_agent):
        self.symbol = symbol
        self.model = ml_controller
        self.agent = smartux_agent
        self.active = False
        self.last_trade_time = None
        self.cooldown_minutes = 3  # Tempo entre trades

    def start(self):
        self.active = True
        print("🚀 AutoTrader ativado")

    def stop(self):
        self.active = False
        print("🛑 AutoTrader desativado")

    def run_cycle(self):
        if not self.active:
            return

        # Respeita cooldown
        if self.last_trade_time and (datetime.now() - self.last_trade_time).total_seconds() < self.cooldown_minutes * 60:
            return

        # Verifica se já há posição aberta
        positions = mt5_service.get_open_positions()
        if any(p.symbol == self.symbol for p in positions):
            return

        # Coleta dados recentes
        df = mt5_service.get_symbol_data(self.symbol, n=150)
        if df is None or df.empty:
            print("[AutoTrade] Sem dados para análise")
            return

        try:
            result = self.agent.analyze(self.symbol, df)
            label = result["label"]
            confidence = float(result["confidence"].replace("%", ""))

            if confidence < 60:
                print(f"[AutoTrade] Confiança insuficiente: {confidence:.1f}%")
                return

            # Define direção
            direction = "buy" if label == "Buy" else "sell" if label == "Sell" else None
            if not direction:
                return

            # Calcula SL/TP com base em ATR
            atr = df["atr"].iloc[-1] if "atr" in df.columns else 0.001
            usd_sl = atr * 10000 * 2  # Ajustável
            usd_tp = atr * 10000 * 3

            print(f"[AutoTrade] Sinal IA: {label} ({confidence:.1f}%) - SL: {usd_sl:.2f}, TP: {usd_tp:.2f}")

            from controllers import trade_controller
            constants = mt5_service.get_constants()
            order_type = constants["ORDER_TYPE_BUY"] if direction == "buy" else constants["ORDER_TYPE_SELL"]

            success, msg = trade_controller.place_order(
                symbol=self.symbol,
                action_type=order_type,
                usd_volume=1.0,
                usd_sl=usd_sl,
                usd_tp=usd_tp,
                deviation=10,
                comment="AutoTrader"
            )

            if success:
                print(f"✅ Trade executado com sucesso: {label} @ {datetime.now().strftime('%H:%M:%S')}")
                self.last_trade_time = datetime.now()
            else:
                print(f"❌ Erro ao executar trade: {msg}")

        except Exception as e:
            print(f"[AutoTrade] Erro ao analisar ou executar: {e}")
