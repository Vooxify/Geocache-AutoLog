import sys, time, random


class Loading:
    def __init__(self, before_time=0.5, after_time=3.8, type_load=["Adding"]):
        self.before_time = before_time
        self.after_time = after_time
        self.type_load = type_load
        self.liste_decimals = [0.03, 0.04, 0.05, 0.06, 0.07]

    def animate_loading(self):
        time.sleep(self.before_time)
        symbols = [
            "|=>                   |",
            "|==>                  |",
            "|===>                 |",
            "|====>                |",
            "|=====>               |",
            "|======>              |",
            "|=======>             |",
            "|========>            |",
            "|=========>           |",
            "|==========>          |",
            "|===========>         |",
            "|============>        |",
            "|=============>       |",
            "|==============>      |",
            "|===============>     |",
            "|================>    |",
            "|=================>   |",
            "|==================>  |",
            "|===================> |",
            "|====================>|",
        ]
        time.time()

        for element in self.type_load:
            for symbol in symbols:
                sys.stdout.write('\r' + f'{element}... {symbol}' + ' ' * (len(symbols[-1]) + len(element) + 4))
                sys.stdout.flush()

                time.sleep(random.choice(self.liste_decimals))

            time.sleep(0.5)

        print("\nSuccessful operation !")
