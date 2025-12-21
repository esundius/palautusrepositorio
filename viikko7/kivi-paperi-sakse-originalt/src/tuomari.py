# Luokka pitää kirjaa ensimmäisen ja toisen pelaajan pisteistä sekä tasapelien määrästä.
class Tuomari:
    def __init__(self):
        self._voittaa = {'k': 's', 's': 'p', 'p': 'k'}
        self.ekan_pisteet = 0
        self.tokan_pisteet = 0
        self.tasapelit = 0

    def kirjaa_siirto(self, ekan_siirto, tokan_siirto):
        if ekan_siirto == tokan_siirto:
            self.tasapelit += 1
        elif self._voittaa[ekan_siirto] == tokan_siirto:
            self.ekan_pisteet += 1
        else:
            self.tokan_pisteet += 1

    def __str__(self):
        msg = f"""Pelitilanne: {self.ekan_pisteet} - {self.tokan_pisteet}
        Tasapelit: {self.tasapelit}"""
        return msg
