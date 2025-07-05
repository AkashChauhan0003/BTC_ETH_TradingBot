from collections import deque
import pandas as pd
import ta

class SmartAIV2:
    def __init__(self, sl=10, rr=6, min_confidence=50):
        self.last_3 = deque(maxlen=3)
        self.sl = sl
        self.rr = rr
        self.min_confidence = min_confidence

    def add_candle(self, candle):
        self.last_3.append(candle)

    def generate_signal(self, trend_direction=None):  # Optional trend_direction: "UP", "DOWN"
        if len(self.last_3) < 3:
            return None

        c1, c2, c3 = self.last_3

        # === Volume Spike ===
        volume_avg = sum(c['volume'] for c in [c1, c2, c3]) / 3
        volume_spike = c3['volume'] > (1.5 * volume_avg)

        # === RSI & MACD Scoring ===
        closes = pd.Series([c['close'] for c in [c1, c2, c3]])
        rsi = ta.momentum.RSIIndicator(closes, window=3).rsi().iloc[-1]
        macd_line = ta.trend.macd(closes).iloc[-1]
        macd_signal = ta.trend.macd_signal(closes).iloc[-1]

        strategies = [
            self._three_candle_momentum,
            self._two_of_three_momentum,
            self._inside_bar_breakout
        ]

        final_signal = None
        best_score = 0

        for strategy_fn in strategies:
            signal = strategy_fn(c1, c2, c3, volume_spike)

            if signal:
                # === Scoring Extras ===
                score = signal['confidence_score']

                if signal['type'] == 'BUY':
                    if rsi > 50: score += 10
                    if macd_line > macd_signal: score += 10
                    if trend_direction == "UP": score += 10
                elif signal['type'] == 'SELL':
                    if rsi < 50: score += 10
                    if macd_line < macd_signal: score += 10
                    if trend_direction == "DOWN": score += 10

                signal['confidence_score'] = score
                signal['reason'] += f" | RSI:{round(rsi, 2)} MACD:{round(macd_line - macd_signal, 2)}"

                if score >= self.min_confidence:
                    return signal
                elif score > best_score:
                    final_signal = signal
                    best_score = score

        return final_signal if final_signal and final_signal['confidence_score'] >= self.min_confidence else None

    def _build_signal(self, candle, direction, reason, score=100, volume_spike=False):
        if volume_spike:
            score += 20
            reason += " + Volume Spike"

        entry = candle['close']
        sl = entry - self.sl if direction == 'BUY' else entry + self.sl
        tp = entry + (self.sl * self.rr) if direction == 'BUY' else entry - (self.sl * self.rr)

        return {
            'timestamp': candle['timestamp'],
            'type': direction,
            'entry': round(entry, 2),
            'sl': round(sl, 2),
            'tp': round(tp, 2),
            'reason': reason,
            'confidence_score': score
        }

    def _three_candle_momentum(self, c1, c2, c3, volume_spike=False):
        if all(c['close'] > c['open'] for c in [c1, c2, c3]):
            return self._build_signal(c3, 'BUY', '3-Candle Momentum', score=40, volume_spike=volume_spike)
        elif all(c['close'] < c['open'] for c in [c1, c2, c3]):
            return self._build_signal(c3, 'SELL', '3-Candle Momentum', score=40, volume_spike=volume_spike)
        return None

    def _two_of_three_momentum(self, c1, c2, c3, volume_spike=False):
        bullish = sum(1 for c in [c1, c2, c3] if c['close'] > c['open'])
        bearish = sum(1 for c in [c1, c2, c3] if c['close'] < c['open'])

        if bullish >= 2:
            return self._build_signal(c3, 'BUY', '2-of-3 Candle Momentum', score=30, volume_spike=volume_spike)
        elif bearish >= 2:
            return self._build_signal(c3, 'SELL', '2-of-3 Candle Momentum', score=30, volume_spike=volume_spike)
        return None

    def _inside_bar_breakout(self, c1, c2, c3, volume_spike=False):
        if c2['high'] < c1['high'] and c2['low'] > c1['low']:
            if c3['close'] > c1['high']:
                return self._build_signal(c3, 'BUY', 'Inside Bar Breakout', score=30, volume_spike=volume_spike)
            elif c3['close'] < c1['low']:
                return self._build_signal(c3, 'SELL', 'Inside Bar Breakout', score=30, volume_spike=volume_spike)
        return None
