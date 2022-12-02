import random
import time
import logging
import logging_loki
logging_loki.emitter.LokiEmitter.level_tag = "level"
# assign to a variable named handler 
handler = logging_loki.LokiHandler(
        url="http://localhost:3100/loki/api/v1/push",
        tags={"application": "martingale"},
        version="1",
)
# create a new logger instance, name it whatever you want
LOKI_FORMAT = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
handler.setFormatter(LOKI_FORMAT)
logger = logging.getLogger("my-logger")

class Player:
    def __init__(self, budget=15000):
        self._budget = budget

    def check(self, bet):
        return self._budget >= bet

    def bet(self, value):
        if self.check(value):
            self._budget -= value

    def deposit(self, value):
        self._budget += value

class Cassino(Player):
    def __init__(self, budget=1_000_000_000):
        self._budget = budget

class Better(Player):
    def __init__(self, budget=15_000):
        self._budget = budget


def simulate():
    logger.addHandler(handler)
    cassino = Cassino()
    count = 0
    win = 0
    loss = 0
    winvalue = 0
    while True:
        better = Better()
        count += 1
        for i in range(16):
            value = 2**i
            if random.random()>=.5:
                if better.check(value):
                    better.bet(value)
                    cassino.deposit(value)
                    loss += 1
                else: break
            else:
                cassino.bet(value)
                better.deposit(value)
                win += 1
                break
        if count % 1000 == 0:
            logger.error(
                    f"budget={cassino._budget} step={count}",
                    extra={"tags": {"service": "cassino"}}
                    )

if __name__ == "__main__":
    simulate()
