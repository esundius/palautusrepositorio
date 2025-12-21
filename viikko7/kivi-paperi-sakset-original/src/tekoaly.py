class Tekoaly:
    def __init__(self):
        self._siirto = 0
        self._siirrot = {0: 'k', 1: 'p', 2: 's'}

    def anna_siirto(self):
        self._siirto = (self._siirto + 1) % 3
        return self._siirrot[self._siirto]

    def aseta_siirto(self, siirto):
        # ei tehdä mitään
        pass
