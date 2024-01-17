import pygame, math, sys

# Skjermøppløsning til pygame (modulet som animerer)
SKJERM_BREDDE = 900
SKJERM_HØYDE = 700

astronomisk_enhet = 1.50 * 10**11

# Skalaen på animasjonen av programmet
SKALA = 200/astronomisk_enhet

#Masser
SOL_MASSE = 1.9891 * 10**30 
MARS_MASSE = 6.39 * 10**23 
JORD_MASSE = 5.9742 * 10**24 

#Andre konstanter
GRAVITASJONS_KONSTANT = 6.67e-11 
TIDS_STEG = 60*24*30 #Programmet kjører i steg per dag


#Farger
HVIT = (255,255,255)
SVART = (0,0,0)


class Legeme(pygame.sprite.Sprite):

    def __init__(self,x_posisjon,y_posisjon,masse,radius,farge):
        self.x_posisjon = x_posisjon
        self.y_posisjon = y_posisjon
        self.masse = masse
        self.radius = radius
        self.x_fart = 0
        self.y_fart = 0
        self.farge = farge
        self.collision = False

    # metode for å finne summen av kreftene
    def tyngdekraft(self,annet_legeme):
        # x og y posisjonen til det andre legemet
        x2_posisjon, y2_posisjon = annet_legeme.x_posisjon, annet_legeme.y_posisjon
        
        # avstanden mellom legemene
        x_avstand = x2_posisjon - self.x_posisjon
        y_avstand = y2_posisjon - self.y_posisjon
        avstand = math.sqrt(x_avstand**2 + y_avstand**2)

        # tyngdekraften som virker på legemet ved bruk av formel for tyngdekraft
        tyngdekraft = (GRAVITASJONS_KONSTANT * self.masse * annet_legeme.masse) / avstand**2
        theta = math.atan2(y_avstand,x_avstand)
        x_tyngdekraft = math.cos(theta) * tyngdekraft
        y_tyngdekraft = math.sin(theta) * tyngdekraft

        return x_tyngdekraft,y_tyngdekraft
    
    # metode for å oppdatere posisjon i forhold til andre legemer i rommet
    def oppdaterPosisjon(self,legemer):

        if not self.collision:
            x_totalKrefter = y_totalKrefter = 0

            # kjører for hvert legeme i lista
            for legeme in legemer:
                if self == legeme:
                    continue
                x_krefter, y_krefter = self.tyngdekraft(legeme)
                x_totalKrefter += x_krefter
                y_totalKrefter += y_krefter

                
            # bruker at farten er F/m * t
            self.x_fart += x_totalKrefter / self.masse * TIDS_STEG
            self.y_fart += y_totalKrefter / self.masse * TIDS_STEG

            # endrer posisjonen utifra det
            self.x_posisjon += self.x_fart * TIDS_STEG
            self.y_posisjon += self.y_fart * TIDS_STEG

    
    def tegn(self,vindu):
        x = self.x_posisjon * SKALA + SKJERM_BREDDE / 2
        y = self.y_posisjon * SKALA + SKJERM_HØYDE / 2
        pygame.draw.circle(vindu, self.farge, (x,y), self.radius)
        


class Rakett(Legeme):

    def førsteBoost(self, radius1, radius2, startsfart):
        # Finner farten som trengs for å sende ut i bane (Vj formelen)
        nødvendigFart = math.sqrt(2 * GRAVITASJONS_KONSTANT * SOL_MASSE * (1/radius1 - 1/(radius1+radius2)))
        
        # Finner faktoren som trengs for å multiplisere x og y komponentene ved å bruke den nåværende farten
        fartsFaktor = nødvendigFart / startsfart

        # Multipliserer farten til romskipet med denne faktoren
        self.x_fart = self.x_fart * fartsFaktor
        self.y_fart = self.y_fart * fartsFaktor

    def sisteBoost(self,radius1,radius2,sluttFart):
        # Finner farten som trengs for å sende inn i bane (Vm formelen)
        nødvendigFart = math.sqrt(2 * GRAVITASJONS_KONSTANT * SOL_MASSE * (1/radius2 - 1/(radius1+radius2)))

        # Finner faktoren som trengs for å multiplisere x og y komponentene ved å bruke den nåværende farten
        fartsFaktor = sluttFart / nødvendigFart

        # Multipliserer farten til romskipet med denne faktoren
        self.x_fart = self.x_fart * fartsFaktor
        self.y_fart = self.y_fart * fartsFaktor


def orbitalfart(masse,avstand):
    # Kalkulerer orbitalfarten
    return math.sqrt((GRAVITASJONS_KONSTANT * masse)/avstand) 


avstandJord = astronomisk_enhet # Avstanden fra jorda til sol
avstandMars = astronomisk_enhet * 1.52 #Avstanden fra mars til sola
rakettStartsOrbitalFart = orbitalfart(SOL_MASSE,avstandJord)
rakettSluttOrbitalFart = orbitalfart(SOL_MASSE,avstandMars)

# Lager planet objektene
# Her ble det gitt uproposjonale radiuser, men det er kun for å modellere, det påvirker ikke utregningen
sola = Legeme(0,0,SOL_MASSE,16, "yellow")
mars = Legeme(avstandMars, 0, MARS_MASSE, 8, "red")
rakett = Rakett(0,avstandJord, 500, 3, "green")

# Snur fortegnet på mars sin startsfart for en rotasjon mot klokken
mars.y_fart = -1 * orbitalfart(SOL_MASSE,avstandMars)

# Setter startfarten på raketten
rakett.x_fart = rakettStartsOrbitalFart


legemer = [sola,rakett,mars]


pygame.init()
vindu = pygame.display.set_mode((SKJERM_BREDDE,SKJERM_HØYDE))
pygame.display.set_caption("Hohmann-bane")

romBilde = pygame.image.load("rommet.png")  # 
romBilde = pygame.transform.scale(romBilde, (SKJERM_BREDDE, SKJERM_HØYDE))




def main():

    # Nødvendig for pygame-vinduet
    font = pygame.font.Font(None,50)
    clock = pygame.time.Clock()
    teller = 0

    # En feilmargin for når den siste "boosten" skal bli brukt
    feilMargin = (0.1*astronomisk_enhet) / 200
    # Teller for å sette spor etter raketten for å demonstrere en halv ellipse og en liste for den
    sporTeller = 0
    koordinatListe=[]

    # Boolske variabler som skal brukes
    tegnSpor = False
    førsteBoost = True
    sisteBoost = True

    while True:
        # Nødvendig for pygame-vinduet
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if førsteBoost:
            rakett.førsteBoost(avstandJord,avstandMars,math.sqrt(rakett.x_fart**2+rakett.y_fart**2))
            førsteBoost = False
            tegnSpor = True

        vindu.blit(romBilde, (0, 0))



        
        # Bestemmer om raketten har nådd målet sitt ved bruk av failmarginen
        if math.sqrt(rakett.x_posisjon** 2 + rakett.y_posisjon**2) >= (avstandMars - feilMargin) and math.sqrt(rakett.x_posisjon** 2 + rakett.y_posisjon**2) <= (avstandMars + feilMargin) and sisteBoost:
            rakett.sisteBoost(avstandJord,avstandMars,rakettSluttOrbitalFart)
            sisteBoost = False
            print("Hei")
        
        # Tegner spor etter raketten:
        if tegnSpor:
            if sporTeller % 25 == 0 and sisteBoost:
                koordinatListe.append([rakett.x_posisjon * SKALA, rakett.y_posisjon * SKALA])
                sporTeller = 0
            
            sporTeller+=1

            for koordinat in koordinatListe:
                pygame.draw.circle(vindu,"grey", (int(koordinat[0] + SKJERM_BREDDE/2), int(koordinat[1] + SKJERM_HØYDE/2)), 2)

        # Tegner banene til jorda og mars
        pygame.draw.circle(vindu, "blue", ( 0+SKJERM_BREDDE/2, 0+SKJERM_HØYDE/2), avstandJord * SKALA, 1)
        pygame.draw.circle(vindu, "red", ( 0+SKJERM_BREDDE/2, 0+SKJERM_HØYDE/2), avstandMars * SKALA, 1)

        # Sola skal stå stille
        sola.x_fart, sola.y_fart = 0, 0 

        # Tegner legemene og oppdaterer deres posisjoner:       
        for legeme in legemer:
            legeme.tegn(vindu)
            legeme.oppdaterPosisjon(legemer)

        
        rakett.tegn(vindu)
        rakettFart = math.sqrt(rakett.x_fart**2 + rakett.y_fart ** 2)

        # Skriver farten og tiden på vinduet:
        vindu.blit(font.render("Farten til raketten: " + str(int(rakettFart)) + " m/s",True,"White"),(10,10))

        if sisteBoost:
            teller += TIDS_STEG
        
        vindu.blit(font.render("Tid: " + str(int(teller/(60*60*24))) + " dager",True,"White"),(10,70))
    
        pygame.display.update()

        clock.tick(60)
          
        
main()
