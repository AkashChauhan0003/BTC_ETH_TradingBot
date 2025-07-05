from utils.binance_data import get_binance_data
from backtest.backtest_utils import simulate_backtest  # <-- Make sure simulate_backtest is saved there
import pandas as pd

if __name__ == "__main__":
    print("📊 Starting backtest with 5000 candles...")

    df = get_binance_data("ETHUSDT", interval="5m", limit=5000)
    if df is None or df.empty:
        print("❌ Failed to fetch data.")
    else:
        print(f"✅ Fetched {len(df)} candles.")
        result_df = simulate_backtest(asset="ETHUSDT", interval="5m", limit=5000)

        if result_df.empty:
            print("⚠️ No trades matched the criteria.")
        else:
            wins = result_df[result_df['hit'] == "TP"]
            losses = result_df[result_df['hit'] == "SL"]
            total_net = result_df['net_pnl'].sum()

            print(f"📈 Total Trades: {len(result_df)}")
            print(f"✅ Wins: {len(wins)} | ❌ Losses: {len(losses)}")
            print(f"💰 Net P&L: {total_net:.2f} USD")
            print("\n🔍 Sample Trades:")
            print(result_df.head(10).to_string(index=False))

            # Optionally save to Excel
            result_df.to_csv("scalp_5m_backtest_result.csv", index=False)
            print("📁 Results saved to 'scalp_5m_backtest_result.csv'")
