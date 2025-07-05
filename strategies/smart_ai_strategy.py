from collections import deque

class SmartAIStrategy:
    def __init__(self, sl=10, rr=6):
        self.last_3_candles = deque(maxlen=3)
        self.sl = sl
        self.rr = rr

    def add_candle(self, candle):
        self.last_3_candles.append(candle)

    def generate_signal(self):
        if len(self.last_3_candles) < 3:
            return None

        c1, c2, c3 = self.last_3_candles

        if all(c['close'] > c['open'] for c in [c1, c2, c3]):
            entry = c3['close']
            return {
                'timestamp': c3['timestamp'],
                'type': 'BUY',
                'entry': round(entry, 2),
                'sl': round(entry - self.sl, 2),
                'tp': round(entry + self.sl * self.rr, 2)
            }

        if all(c['close'] < c['open'] for c in [c1, c2, c3]):
            entry = c3['close']
            return {
                'timestamp': c3['timestamp'],
                'type': 'SELL',
                'entry': round(entry, 2),
                'sl': round(entry + self.sl, 2),
                'tp': round(entry - self.sl * self.rr, 2)
            }

        return None
