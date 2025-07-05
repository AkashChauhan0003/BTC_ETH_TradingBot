from strategies.scalp_strategy import generate_scalp_signal
from utils.binance_data import get_binance_data
from config import eth_config
from core.forward_test_logger import log_forward_test

def simulate_backtest(asset="ETHUSDT", interval="5m", limit=5000):
    print(f"📊 Starting backtest for {asset} with {limit} candles on {interval} interval...")
    df = get_binance_data(asset, interval=interval, limit=limit)
    if df is None or df.empty:
        print("❌ Failed to fetch historical data.")
        return

    win_count = 0
    loss_count = 0
    total_profit = 0
    total_loss = 0
    trades = 0

    for i in range(100, len(df) - 1):
        sample_df = df.iloc[:i+1].copy()
        signal, sl, tp = generate_scalp_signal(sample_df, eth_config, asset_name=asset)

        if signal:
            trades += 1
            entry = sample_df.iloc[-1]['close']
            next_candle = df.iloc[i + 1]  # Simulate next candle movement
            high = next_candle['high']
            low = next_candle['low']
            close = next_candle['close']

            hit_tp = False
            hit_sl = False

            if signal == "BUY":
                hit_tp = high >= tp
                hit_sl = low <= sl
            elif signal == "SELL":
                hit_tp = low <= tp
                hit_sl = high >= sl

            if hit_tp and not hit_sl:
                win_count += 1
                reward = abs(tp - entry)
                total_profit += reward
            elif hit_sl and not hit_tp:
                loss_count += 1
                risk = abs(entry - sl)
                total_loss += risk
            elif hit_tp and hit_sl:
                # Both hit: assume SL hit first (worst case)
                loss_count += 1
                total_loss += abs(entry - sl)

            log_forward_test(
                asset=asset,
                signal=signal,
                trend="-",  # Optional: add real trend detection if needed
                rsi=0,
                macd=0,
                signal_line=0,
                volume_spike=False,
                pattern="Backtest",
                decision="Simulated",
                reason="Backtest Mode",
                candle_time=str(sample_df.index[-1]),
                candle_price=entry,
                confidence_score=75  # placeholder
            )

    total_trades = win_count + loss_count
    win_rate = (win_count / total_trades) * 100 if total_trades else 0

    print(f"\n📈 Backtest Summary for {asset}")
    print(f"✅ Trades: {total_trades} | 🟢 Wins: {win_count} | 🔴 Losses: {loss_count}")
    print(f"💰 Total Profit: {round(total_profit, 2)} | ❌ Total Loss: {round(total_loss, 2)}")
    print(f"📊 Win Rate: {round(win_rate, 2)}%")

