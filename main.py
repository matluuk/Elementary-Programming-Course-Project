import random
import math
import json
import ikkunasto
from os import listdir
import haravasto2

IKKUNAN_LEVEYS = 1200
IKKUNAN_KORKEUS = 600
PUTOAMISKIIHTYVYYS = 0.8
PAIVITYSNOPEUS = 1/60
PELIN_0_TASO = 72
LAUKAISUETAISYYS = 320

peli = {
    "spritet": [],
    "kentta": {
        "x_laukaisu": 120,
        "y_laukaisu": 170,
        "vihollisia": 0,
        "sorsia": 0,
        "kentan_numero": 0,
        "seuraava_kentta": "",
        "nykyinen_kentta": "",
        },
    "asetukset": {
        "voitto": False,
        "havio": False,
        "sorsa_lennossa": False,
        "nopeustarkistus": 0,
        "nykyinen_kentta": 1,
        "hiiri_x": 0,
        "hiiri_y": 0,
        "hiiri_nakyvissa": False,
        },
    "ammututsorsat": [],
    "suuntapallot": [],
    "sorsa_kopio": {},
}

valikko_muuttujat = {
    "kentat": [],
    "valittu_kentta": None,
    "kenttalaatikko": [],
    "tekstilaatikko": [],
}

tilastot = {}

def lataa_tiedosto(tiedostonnimi, polku=""):
    """
    Lataa kentän halutusta tiedostosta
    """
    if polku == "":
        tiedostopolku = tiedostonnimi
    else:
        tiedostopolku = polku + "/" + tiedostonnimi
    kohde = None
    
    try:
        with open(tiedostopolku) as lahde:
            kohde = json.load(lahde)
    except (IOError, json.JSONDecodeError):
        print(f"Tiedoston {tiedostopolku} avaaminen ei onnistunut.")
    return kohde

def tallenna_tiedosto(tiedostonnimi, komponentti):
    """
    Tallentaa .json tiedoston.
    """
    try:
        with open(tiedostonnimi, "w") as kohde:
            json.dump(komponentti, kohde)
            print(f"tallensi tiedoston nimellä {tiedostonnimi}")
    except (IOError, json.JSONDecodeError):
        print("Kohdetiedostoa ei voitu avata. Tallennus epäonnistui")

def luo_kentta(kentta_nimi):
    """
    Luo kentän.
    """
    #asettaa tarvittavat tiedot nollatilaan
    peli["ammututsorsat"].clear()
    peli["spritet"].clear()
    peli["asetukset"]["voitto"] = False
    peli["asetukset"]["havio"] = False
    luo_sorsa()

    #luo satunnaisen kentän
    if kentta_nimi == "satunnainen":
        peli["kentta"]["y_laukaisu"] = random.randint(155,190)
        peli["kentta"]["x_laukaisu"] = random.randint(100,200)
        peli["kentta"]["vihollisia"] = random.randint(3,6)
        peli["kentta"]["sorsia"] = random.randint(
            int(peli["kentta"]["vihollisia"] * 0.7), int(peli["kentta"]["vihollisia"] * 1.2)
            )
        peli["kentta"]["kentan_numero"] = 0
        peli["kentta"]["seuraava_kentta"] = "satunnainen"
        luo_laatikot(10, PELIN_0_TASO, 300)
        luo_viholliset(peli["kentta"]["vihollisia"], IKKUNAN_KORKEUS - 300, IKKUNAN_KORKEUS)
    #lataa kentän tiedostosta
    else:
        kentta = lataa_tiedosto(kentta_nimi + ".json", "kentat")
        if kentta != None:
            peli["kentta"] = kentta[1]
            peli["kentta"]["kentan_numero"] = int(kentta_nimi[-1])
            peli["spritet"].extend(kentta[0])
        else:
            ikkunasto.avaa_viesti_ikkuna(
                "Virhe!", "Kentan avaaminen ei onnistu.\nTarkista tiedosto {}!".format(kentta_nimi), virhe=True
                )

    peli["kentta"]["nykyinen_kentta"] = kentta_nimi

    alkutila(peli["spritet"][0])

def alkutila(sorsa):
    """
    Asettaa sorsan laukaisualustalle, jos sorsia on jäljellä.
    """
    if peli["kentta"]["sorsia"] > 0:
        sorsa["x"] = peli["kentta"]["x_laukaisu"]
        sorsa["y"] = peli["kentta"]["y_laukaisu"]
    sorsa["vx"] = 0
    sorsa["vy"] = 0
    peli["asetukset"]["sorsa_lennossa"] = False
    peli["asetukset"]["nopeustarkistus"] = 0
    peli["sorsa_kopio"] = sorsa

def luo_laatikot(kpl, raja_y1, raja_y2):
    """
    Luo halutun määrän laatikoita ja asettaa ne satunnaisiin kohtiin määritetyn
    alueen sisälle. Siirää sisäkkäiset laatikot toistensa päälle.
    """
    for i in range(kpl):
        vari = random.randint(50,255)
        width = random.randint(50, 100)
        height = random.randint(50, 100)
        peli["spritet"].append({
            "x": random.randint(300, IKKUNAN_LEVEYS - 80),
            "y": random.randint(raja_y1, IKKUNAN_KORKEUS - raja_y2 - height),
            "w": width,
            "h": height,
            "vy": 0.1,
            "vx": 0.1,
            "m": width*height / 900,
            "vari": (vari, vari, vari),
            "hp": 2,
            "tyyppi": "laatikko",
        })

def luo_viholliset(kpl, raja_y1, raja_y2):
    """
    Luo halutun määrän laatikoita ja asettaa ne satunnaisiin kohtiin määritetyn
    alueen sisälle.
    """
    for i in range(kpl):

        peli["spritet"].append({
            "x": random.randint(300, IKKUNAN_LEVEYS - 80),
            "y": random.randint(raja_y1, raja_y2 - 50),
            "w": 50,
            "h": 50,
            "vy": 0,
            "vx": 0,
            "m": 40 * 40 / 900,
            "vari": (200, 0, 40),
            "tyyppi": "vihollinen",
        })

def luo_sorsa():
    """
    Luo sorsan spritet listan ensimmäiselle paikalle.
    """
    peli["spritet"].insert(0, {
        "x": 0,
        "y": 0,
        "kulma": 0,
        "voima": 0,
        "w": 40,
        "h": 40,
        "vx": 0,
        "vy": 0,
        "m": 40 * 40 / 900,
        "vari": (255, 120, 120),
        "tyyppi": "sorsa",
        })
    peli["sorsa_kopio"] = peli["spritet"][0].copy()

def ammu(sorsa):
    """
    Funktio lähettää sorsan liikkeelle ja laskee sille lähtönopeuden, sijoittaen x- ja
    y-nopeusvektorit globaaliin sanakirjaan.
    """
    sorsa["vx"] = float(sorsa["voima"] * math.cos(math.radians(sorsa["kulma"])))
    sorsa["vy"] = float(sorsa["voima"] * math.sin(math.radians(sorsa["kulma"])))

def suuntapallot():
    """
    Laskee sorsan lentoradan ennen sorsan ampumista
    """
    if (not peli["asetukset"]["sorsa_lennossa"] and (
        peli["sorsa_kopio"]["kulma"] != peli["spritet"][0]["kulma"] or
        peli["sorsa_kopio"]["voima"] != peli["spritet"][0]["voima"])):

        #tyhjentää suuntapallot listan
        peli["suuntapallot"] = []

        #tekee kopion sorsasta, jotta sorsan kopio voidaan ampua
        peli["sorsa_kopio"] = peli["spritet"][0].copy()

        ammu(peli["sorsa_kopio"])
        for i in range(50):
            peli["sorsa_kopio"]["x"] += peli["sorsa_kopio"]["vx"]
            peli["sorsa_kopio"]["y"] += peli["sorsa_kopio"]["vy"]

            peli["sorsa_kopio"]["vy"] -= PUTOAMISKIIHTYVYYS

            peli["suuntapallot"].append({
                    "x": peli["sorsa_kopio"]["x"] + peli["sorsa_kopio"]["w"] / 2,
                    "y": peli["sorsa_kopio"]["y"] + peli["sorsa_kopio"]["h"] / 2,
                })
        #poistaa välistä pisteitä
        peli["suuntapallot"] = peli["suuntapallot"][1::3]

    #tekee kopion sorsasta seuraavaa kierrosta varten
    peli["sorsa_kopio"] = peli["spritet"][0].copy()

def jos_vihollinen(sprite):
    """
    Tarkistaa, onko sprite vihollinen.
    """
    if sprite["tyyppi"] == "vihollinen":
        peli["kentta"]["vihollisia"] -= 1
        return True
    else:
        return False

def tormaystarkistus(i, i2):
    """
    Tarkistaa tuleeko sprite i törmäämään spriteen i2. Palauttaa spriten i2 sivun, johon törmää.
    vy > 0, kun liikutaan ylöspäin ja
    vx > 0, kun liikutaan oikealle
    """
    if (i["y"] + i["h"] + i["vy"] > i2["y"] and
        i["y"] + i["vy"] <= i2["y"] + i2["h"] and
        i["x"] + i["w"] + i["vx"] > i2["x"] and
        i["x"] + i["vx"] <= i2["x"] + i2["w"]):

        if i["vy"] < 0 and i["vx"] <= 0:
            if abs(i["x"] - (i2["x"] + i2["w"])) < abs(i["y"] - (i2["y"] + i2["h"])) and i["vx"] != 0:
                return "oikea"
            else:
                return "yla"
        elif i["vy"] < 0 and i["vx"] > 0:
            if abs((i["x"] + i["w"]) - i2["x"]) < abs(i["y"] - (i2["y"] + i2["h"])):
                return "vasen"
            else:
                return "yla"
        elif i["vy"] >= 0 and i["vx"] <= 0:
            if abs(i["x"] - (i2["x"] + i2["w"])) < abs((i["y"] + i["h"]) - i2["y"]) and i["vx"] != 0:
                return "oikea"
            else:
                return "ala"
        elif i["vy"] >= 0 and i["vx"] > 0:
            if abs((i["x"] + i["w"]) - i2["x"]) < abs((i["y"] + i["h"]) - i2["y"]):
                return "vasen"
            else:
                return "ala"

def kitka(sprite):
    """
    Funktio kitkalle
    """
    sprite["vx"] *= 0.9
    if abs(sprite["vx"]) < 0.3:
        sprite["vx"] = 0

def fysiikat(spritet):
    """
    Pelin fysiikat törmäyksineen.
    """
    poistettavat = []
    for k, i in enumerate(spritet[:]):
        if i["tyyppi"] == "sorsa" and not peli["asetukset"]["sorsa_lennossa"]:
            pass
        else:
            i["vy"] -= PUTOAMISKIIHTYVYYS
            for k2, i2 in enumerate(spritet[:]):
                #ei tarkista törmäystä itsensä kanssa
                if k2 != k:
                    #tarkistaa tuleeko i törmäämään y suunnassa
                    tormays = tormaystarkistus(i, i2)
                    if tormays == "yla" or tormays =="ala":
                        if i["tyyppi"] == "sorsa":
                            i["vy"] *= -0.3
                            #lisää spriten poistettavien listaan, jos on vihollinen
                            if jos_vihollinen(i2):
                                poistettavat.append(k2)
                        #poistaa harvinaisen bugin, jossa laatikot menevät sorsan päälle
                        elif i2["tyyppi"] == "sorsa":
                            pass
                        #siirtää spriten i spriten i2 päälle
                        elif tormays == "yla":
                            i["y"] = i2["y"] + i2["h"]
                            i["vy"] = 0

                        kitka(i)

                    #tarkistaa tuleeko i törmäämään x suunnassa
                    if tormays == "oikea" or tormays =="vasen":

                        #asettaa i2 nopeuden ja i:n nopeuden
                        i2["vx"] += i["vx"] / i2["m"]
                        i["vx"] *= -0.3

                        #lisää spriten poistettavien listaan, jos on vihollinen
                        if i["tyyppi"] == "sorsa" and jos_vihollinen(i2):
                            poistettavat.append(k2)

            #tarkistaa tuleeko i törmäämään ikkunan laitoihin
            if i["x"] + i["vx"] < 0 or i["x"] + i["w"] + i["vx"] > IKKUNAN_LEVEYS:
                i["vx"] *= -0.3

            #tarkistaa törmääkö i lattiaan tai kattoon
            if i["y"] + i["vy"] < PELIN_0_TASO or i["y"] + i["h"] + i["vy"] > IKKUNAN_KORKEUS:
                if i["tyyppi"] == "sorsa":
                    i["vy"] *= -0.3
                else:
                    i["y"] = PELIN_0_TASO
                    i["vy"] = 0
                kitka(i)

            #liikuttaa laatikoita x ja y suunnissa
            i["y"] += i["vy"]
            i["x"] += i["vx"]

    #poistaa poistettavat viholliset
    if poistettavat:
        for indeksi in sorted(poistettavat, reverse=True):
            del peli["spritet"][indeksi]

def nopeustarkistus(sorsa):
    """
    Tarkistaa, onko sorsa pysähtynyt
    """
    #lisää yhden nopeustarkistus muuttujaan, kun sorsan nopeus on tarpeeksi pieni
    if (abs(sorsa["vy"]) < 2 and
        abs(sorsa["vx"]) < 2) and peli["asetukset"]["sorsa_lennossa"]:
        peli["asetukset"]["nopeustarkistus"] += 1
    else:
        peli["asetukset"]["nopeustarkistus"] = 0

    #asettaa sorsan laukaisupaikalle, jos sorsa liikkuu liian hitaasti tarpeeksi kauan.
    if peli["asetukset"]["nopeustarkistus"] > 25:
        peli["ammututsorsat"].append({
            "x": sorsa["x"],
            "y": sorsa["y"],
            "w": sorsa["w"],
            "h": sorsa["h"],
        })
        alkutila(sorsa)

def muunna_xy_koordinaateiksi(kulma, vektorin_pituus):
    """
    Muuntaa napakoordinaatit x, y koordinaateiksi
    """
    x = vektorin_pituus * math.cos(kulma)
    y = vektorin_pituus * math.sin(kulma)
    return x, y

def muunna_napakoordinaateiksi(x, y):
    """
    Muuntaa x, y koordinaatit napakoordinaateiksi
    """
    pituus = (x ** 2 + y ** 2) ** (1/2)
    kulma = math.atan2(y, x)
    return kulma, pituus

def raahaus_kasittelija(x, y, dx, dy, nappi, muokkausnapit):
    """
    Ajetaan liikutettaessa hiirtä.
    """

    if not peli["asetukset"]["sorsa_lennossa"] and peli["kentta"]["sorsia"] > 0:

        #asettaa hiiren pisteen näkyviin
        peli["asetukset"]["hiiri_nakyvissa"] = True

        #laskee voimavektorin napakoordinaatit
        x_pituus = x - peli["asetukset"]["hiiri_x"]
        y_pituus = y - peli["asetukset"]["hiiri_y"]
        kulma, pituus = muunna_napakoordinaateiksi(x_pituus, y_pituus)

        #muuttaa pituuden, kun on liian suuri
        if pituus > LAUKAISUETAISYYS:
            pituus = LAUKAISUETAISYYS

        x_napa, y_napa = muunna_xy_koordinaateiksi(kulma, pituus / 4)

        #asettaa sorsan lähtöpaikkaan
        peli["spritet"][0]["x"] = peli["kentta"]["x_laukaisu"] + x_napa
        peli["spritet"][0]["y"] = peli["kentta"]["y_laukaisu"] + y_napa

        #asettaa sorsalle kulman ja voiman
        peli["spritet"][0]["kulma"] = math.degrees(kulma + math.pi)
        peli["spritet"][0]["voima"] = pituus / 8

def hiiri_kasittelija(x, y, nappi, muokkausnapit):
    """
    Ajetaan painettaessa hiiren nappia
    """
    peli["asetukset"]["hiiri_x"] = x
    peli["asetukset"]["hiiri_y"] = y

def vapautus_kasittelija(x, y, nappi, muokkausnapit):
    """
    Ajetaan vapautettaessa hiiren nappi
    """
    if not peli["asetukset"]["sorsa_lennossa"]:
        if (abs(peli["asetukset"]["hiiri_x"] - x) < 5 and
            abs(peli["asetukset"]["hiiri_y"] - y) < 5):
            peli["spritet"][0]["x"] = peli["kentta"]["x_laukaisu"]
            peli["spritet"][0]["y"] = peli["kentta"]["y_laukaisu"]

        elif peli["kentta"]["sorsia"] > 0:
            #ampuu sorsan vapauttaessa hiiren
            ammu(peli["spritet"][0])
            peli["asetukset"]["sorsa_lennossa"] = True
            peli["kentta"]["sorsia"] -= 1
            peli["suuntapallot"] = []

    #asettaa hiiren pisteen pois näkyvistä
    peli["asetukset"]["hiiri_nakyvissa"] = False

def nappain(sym, mods):
    """
    Tämä funktio hoitaa näppäinsyötteiden käsittelyn.
    Pohja otettu sorsa_lentorata harjoitustehtävän tehtävänannosta.
    """
    key = haravasto2.pyglet.window.key

    if sym == key.Q:
        sulje_peli()

    if sym == key.R:
        alkutila(peli["spritet"][0])

    if sym == key.SPACE:
        if (peli["asetukset"]["voitto"] and
            peli["kentta"]["seuraava_kentta"] != ""):
            luo_kentta(peli["kentta"]["seuraava_kentta"])
        elif peli["asetukset"]["havio"]:
            #muuta nykyiseksi kentäksi
            luo_kentta(peli["kentta"]["nykyinen_kentta"])

# kenttien luontia varten satunnaisista kentistä

#    if sym == key.S:
 #       i = 11
  #      tiedostonnimi = "%s.json" % ("kentat/kentta" + str(i))
#
 #       kentta = [peli["spritet"][1:], peli["kentta"]]
  #      print(kentta)
   #     tallenna_tiedosto(tiedostonnimi, kentta)

#virheenetsintää varten

 #   if sym == key.N:
  #      luo_kentta(peli["kentta"]["nykyinen_kentta"])

def piirra():
    """
    Piirtää kaikki grafiikat ikkunaan.
    """
    haravasto2.tyhjaa_ikkuna ()
    haravasto2.piirra_tausta ()
    haravasto2.aloita_ruutujen_piirto ()

    #piirtää laatikot
    for i in peli["spritet"]:
        if i["tyyppi"] == "laatikko" or i["tyyppi"] == "vihollinen":
            haravasto2.lisaa_piirrettava_nelikulmio(i["x"], i["y"], i["w"], i["h"], i["vari"])

    #piirtää suuntapallot
    for i in peli["suuntapallot"]:
        haravasto2.lisaa_piirrettava_ympyra(i["x"], i["y"], 10, (200, 200, 200), 170)

    #piirtää ritsan
    haravasto2.lisaa_piirrettava_ruutu(
        "ritsa",
        peli["kentta"]["x_laukaisu"] - 20,
        peli["kentta"]["y_laukaisu"] - 200)

    #piirtää sorsan
    haravasto2.lisaa_piirrettava_ruutu("sorsa", peli["spritet"][0]["x"], peli["spritet"][0]["y"])
    #piirtää ammutut sorsat
    for i in peli["ammututsorsat"]:
        haravasto2.lisaa_piirrettava_ruutu("sorsa", i["x"], i["y"])

    #piirtää hiiren pisteen laukaistaessa
    if peli["asetukset"]["hiiri_nakyvissa"]:
        haravasto2.lisaa_piirrettava_ympyra(
            peli["asetukset"]["hiiri_x"],
            peli["asetukset"]["hiiri_y"],
            LAUKAISUETAISYYS, (200, 200, 200), 50)
        haravasto2.lisaa_piirrettava_ympyra(
            peli["asetukset"]["hiiri_x"],
            peli["asetukset"]["hiiri_y"],
            50, (200, 200, 200), 80)

    haravasto2.piirra_ruudut ()

    #piirtää voittotekstin
    if peli["asetukset"]["voitto"]:
        haravasto2.piirra_tekstia(
            "Voitit kentän.",
            IKKUNAN_LEVEYS / 2, IKKUNAN_KORKEUS * 0.7, tasaus_x="center", tasaus_y="center")
        if peli["kentta"]["seuraava_kentta"] != "":
            haravasto2.piirra_tekstia(
                "Siirry seuraavaan kenttään painamlla Space.",
                IKKUNAN_LEVEYS / 2, IKKUNAN_KORKEUS * 0.7 - 30, koko=20, tasaus_x="center", tasaus_y="center")
        else:
            haravasto2.piirra_tekstia(
                "Pääsit läpi viimeisen kentän. Palaa valikkoon painamalla Q.",
                IKKUNAN_LEVEYS / 2, IKKUNAN_KORKEUS * 0.7 - 30, koko=20, tasaus_x="center", tasaus_y="center")
    #piirtää häviötekstin
    if peli["asetukset"]["havio"]:
        haravasto2.piirra_tekstia(
            "Hävisit kentän.",
            IKKUNAN_LEVEYS / 2, IKKUNAN_KORKEUS * 0.7, tasaus_x="center", tasaus_y="center")
        haravasto2.piirra_tekstia(
            "Kokeile uudestaan painamalla Space",
            IKKUNAN_LEVEYS / 2, IKKUNAN_KORKEUS * 0.7 - 30, koko=20, tasaus_x="center", tasaus_y="center")
        haravasto2.piirra_tekstia(
            "tai palaa päävalikkoon painamalla Q",
            IKKUNAN_LEVEYS / 2, IKKUNAN_KORKEUS * 0.7 - 50, koko=20, tasaus_x="center", tasaus_y="center")

    #info tekstit ikkunan ylälaitaan
    haravasto2.piirra_tekstia(
        "Sorsien määrä: {}, vihollisten määrä: {}".format(
            peli["kentta"]["sorsia"], peli["kentta"]["vihollisia"]), 10, 505)
    haravasto2.piirra_tekstia(
        "Q: Palaa päävalikkoon  | "
        "R: Siirrä sorsa ritsalle",
        10, 560, koko=20)
    haravasto2.piirra_tekstia(
        "Laukaise sorsa vetämällä ruutua hiirellä ",
        10, 480, koko=20)
    #kentän nimi alanurkkaan
    haravasto2.piirra_tekstia(
        "Kentän nimi: {}".format(peli["kentta"]["nykyinen_kentta"]),
        10, 5, koko=20)
    haravasto2.piirra_tekstia("Voittoputki ennätys: {}".format(tilastot["voittoputki_ennatys"]),
        IKKUNAN_LEVEYS - 10, IKKUNAN_KORKEUS - 10, koko=20, tasaus_x="right", tasaus_y="top")
    haravasto2.piirra_tekstia("Voittoputki: {}".format(tilastot["voittoputki"]),
        IKKUNAN_LEVEYS - 10, IKKUNAN_KORKEUS - 40, koko=20, tasaus_x="right", tasaus_y="top")

def tarkista_voitto():
    """
    Asettaa kentän voitetuksi tai hävityksi, jos on tarpeen.
    """
    if (peli["asetukset"]["voitto"] is False and
        peli["asetukset"]["voitto"] is False):
        if peli["kentta"]["vihollisia"] <= 0:
            peli["asetukset"]["voitto"] = True
            tilastot["voittoputki"] += 1

            #muuttaa vopittoputki tilaston, jos on tarpeen
            if tilastot["voittoputki"] > tilastot["voittoputki_ennatys"]:
                tilastot["voittoputki_ennatys"] = tilastot["voittoputki"]

        elif (peli["kentta"]["sorsia"] <= 0 and
            peli["asetukset"]["sorsa_lennossa"] is False):
            peli["asetukset"]["havio"] = True
            tilastot["voittoputki"] = 0

            #muuttaa vopittoputki tilaston, jos on tarpeen
            if tilastot["voittoputki"] > tilastot["voittoputki_ennatys"]:
                tilastot["voittoputki_ennatys"] = tilastot["voittoputki"]

def paivita(kulunut_aika):
    """
    Päivitä funktio peliä ajettaessa.
    """
    suuntapallot()
    fysiikat(peli["spritet"])
    nopeustarkistus(peli["spritet"][0])
    tarkista_voitto()

def luo_peliikkuna(kentta_nimi):
    """
    Luo peli-ikkunan.
    """
    luo_kentta(kentta_nimi)
    haravasto2.lataa_kuvat("spritet")
    haravasto2.lataa_sorsa("spritet")
    haravasto2.luo_ikkuna(IKKUNAN_LEVEYS, IKKUNAN_KORKEUS, "tausta", "Sorsapeli")
    haravasto2.aseta_piirto_kasittelija(piirra)
    haravasto2.aseta_toistuva_kasittelija(paivita, PAIVITYSNOPEUS)
    haravasto2.aseta_nappain_kasittelija(nappain)
    haravasto2.aseta_raahaus_kasittelija(raahaus_kasittelija)
    haravasto2.aseta_hiiri_kasittelija(hiiri_kasittelija)
    haravasto2.aseta_vapautus_kasittelija(vapautus_kasittelija)

    #sulkee pyglet ikunan oikein ikkunan sulkeutuessa väkisin.
    def on_close():
        sulje_peli()
    haravasto2.grafiikka["ikkuna"].on_close = on_close

    haravasto2.aloita()

def sulje_peli():
    """
    Sulkee pyglet ikkunan ja tekee tarvittavat toimenpiteet sulkemisen yhteydessä
    """
    if (peli["asetukset"]["voitto"] and
        tilastot["pelattava_kentta"] < peli["kentta"]["kentan_numero"] + 1):
        #asettaa oikean kentän pelattavaksi kentäksi
        tilastot["pelattava_kentta"] = peli["kentta"]["kentan_numero"] + 1

    elif tilastot["pelattava_kentta"] < peli["kentta"]["kentan_numero"]:
        #asettaa oikean kentän pelattavaksi kentäksi
        tilastot["pelattava_kentta"] = peli["kentta"]["kentan_numero"]

    tilastot["voittoputki"] = 0

    tallenna_tiedosto("tilastot.json", tilastot)

    haravasto2.lopeta()
    piirra_tilastot()

#Valikon funktion alkaa tästä

def luo_kentat_listan():
    """
    Luo listan kentistä valikkoa varten.
    """
    kentat_str = listdir("kentat")
    for i in kentat_str:
        kentta_nimi = ""
        for j in i:
            kentta_nimi += j
        if kentta_nimi.endswith('.json'):
            kentta_tiedot = lataa_tiedosto(kentta_nimi, "kentat")
            #tarvitsee virheenkäsittelyn
            try:
                if (isinstance(kentta_tiedot[0][0], dict) and
                    isinstance(kentta_tiedot[1], dict)):
                    kentta_nimi = kentta_nimi.rstrip(".json")
                    kentta_valikko = [kentta_nimi, int(kentta_nimi[-1])]
                    valikko_muuttujat["kentat"].append(kentta_valikko)
            except (IndexError, TypeError):
                ikkunasto.avaa_viesti_ikkuna(
                    "Virhe!", "Tiedosto {} ei ole oikeassa muodossa. \nTarkista tiedosto!".format(kentta_nimi), virhe=True
                    )
    valikko_muuttujat["kentat"].append(["satunnainen", 0])

def tulosta(kentat):
    """
    Tulostaa kentat valikon listaan.
    """
    for i, kentta in enumerate(kentat):
        ikkunasto.lisaa_rivi_laatikkoon(valikko_muuttujat["kenttalaatikko"],
            ("{}. {}, kentan numero:{}".format(i + 1, kentta[0], kentta[1])))

def pelaa_nappi():
    """
    Ajetaan painettaessa pelaa-nappia valikossa.
    """
    #tutkii valitun kentan
    valittu_rivi = ikkunasto.lue_valittu_rivi(valikko_muuttujat["kenttalaatikko"])

    #Tarkastaa, onko ikkunaa valittu
    if valittu_rivi[0] is None:
        ikkunasto.avaa_viesti_ikkuna("Huom!", "Valitse kenttä.", virhe=False)
    #tarkistaa minkälainen kenttä on kyseessä
    elif valikko_muuttujat["kentat"][valittu_rivi[0]][1] == 0:
        luo_peliikkuna("satunnainen")

    elif valikko_muuttujat["kentat"][valittu_rivi[0]][1] <= tilastot["pelattava_kentta"]:
        luo_peliikkuna(valikko_muuttujat["kentat"][valittu_rivi[0]][0])

    elif valikko_muuttujat["kentat"][valittu_rivi[0]][1] > tilastot["pelattava_kentta"]:
        ikkunasto.avaa_viesti_ikkuna(
            "Huom!", "valitse pienempi kenttä, kuin {}".format(tilastot["pelattava_kentta"]), virhe=False)

def resetoi_tilastot():
    """
    resetoi tilastot.
    """
    tilastot.clear()
    tilastot.update({"pelattava_kentta": 1, "voittoputki_ennatys": 0, "voittoputki": 0})
    piirra_tilastot()

def piirra_tilastot():
    """
    Piirtää tilastot tekstilaatikkoon.
    """
    ikkunasto.kirjoita_tekstilaatikkoon(valikko_muuttujat["tekstilaatikko"],
        "Seuraavan kentän numero on {}".format(tilastot["pelattava_kentta"]), True)
    ikkunasto.kirjoita_tekstilaatikkoon(valikko_muuttujat["tekstilaatikko"],
        "Paras voittoputki on {}.".format(tilastot["voittoputki_ennatys"]), False)

def valikko():
    """
    Luo valikon ikkunasto-moduulilla.
    """
    ikkuna = ikkunasto.luo_ikkuna("Sorsapeli")
    nappikehys = ikkunasto.luo_kehys(ikkuna, ikkunasto.OIKEA)
    kenttakehys = ikkunasto.luo_kehys(ikkuna, ikkunasto.VASEN)
    ikkunasto.luo_nappi(nappikehys, "Pelaa", pelaa_nappi)
    ikkunasto.luo_nappi(nappikehys, "lopeta", ikkunasto.lopeta)
    valikko_muuttujat["tekstilaatikko"] = ikkunasto.luo_tekstilaatikko(nappikehys, 30, 1)
    valikko_muuttujat["kenttalaatikko"] = ikkunasto.luo_listalaatikko(kenttakehys, leveys=40, korkeus=20)
    ikkunasto.luo_nappi(nappikehys, "Resetoi tilastot", resetoi_tilastot)

    luo_kentat_listan()
    #virheenkäsittelyn palautus tarvitaan tiedostojen lataamiselle.
    tilasto_nimi = "tilastot.json"
    tilasto = lataa_tiedosto(tilasto_nimi)
    if tilasto != None:
        tilastot.update(tilasto)
    else:
        ikkunasto.avaa_viesti_ikkuna(
                    "Virhe!", "Tilastojen avaaminen ei onnistu.\nTarkista tiedosto {}!".format(tilasto_nimi), virhe=True
                    )
    tulosta(valikko_muuttujat["kentat"])
    piirra_tilastot()
    ikkunasto.kaynnista()

if __name__ == "__main__":
    try:
        valikko()
    except KeyboardInterrupt:
        print("Peli keskeytettiin väkisin.")
