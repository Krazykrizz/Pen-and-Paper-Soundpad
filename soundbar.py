import pygame
from pygame import mixer
import time

pygame.init()

breite = 0 # 1500 bei Fenster-Modus
hoehe = 0 # 760 bei Fenster-Modus

screen = pygame.display.set_mode([breite, hoehe])
mixer.set_num_channels(32)

pygame.display.set_caption("PnP-GameMaster's SoundBar")

soundlist = f = open("soundlist1.txt", "r") # vorbelegte Sounds laden
soundlist = f.read().split(",")

soundset_geladen = 1
soundset_gespeichert = 3

buttons = []
button_ls = []
button_quick_vol = []

click_pos = (-1, -1)
soundexplorer_offen = False
fade = False

# Methode "Blasse Farbe" - generiert automatisch Farbvarianten

def blasse_farbe(col, faktor, hell):
    col_blass = (
        int(min(255, (col[0] / faktor + hell))), 
        int(min(255, (col[1] / faktor + hell))),
        int(min(255, (col[2] / faktor + hell))))
    return col_blass

# Methode Rahmen und Hintergrund

def rahmen_malen(titel, titel_x, titel_y, farbe, x , y, breite, hoehe):
    
    pygame.draw.rect(screen, farbe, [x, y, breite, hoehe], 0, 8)
    pygame.draw.rect(screen, blasse_farbe(farbe, 2, 100), [x, y, breite, hoehe], 5, 8)
    screen.blit(pygame.font.SysFont("arial.ttf", 48).render(titel, True, 
                                                  (blasse_farbe(farbe, 2, 200))), [titel_x, titel_y -5])
    
def alle_rahmen_malen():
    rahmen_malen("Melodien", 665, 25, (20, 20, 100), 3, 3, 1490, 250)
    rahmen_malen("Ambient Sounds", 605, 285, (20, 100, 20), 3, 263, 1490, 250)
    rahmen_malen("Effekte", 340, 545, (130, 110, 20), 3, 523, 800, 230)
    rahmen_malen("Globale Steuerung", 980, 545, (100, 100, 100), 813, 523, 680, 230)

# Methode Sound-Explorer

def soundexplorer(explorer_nr):
    
    global explorer
    
    if explorer_nr == 1: # optionale Sounds laden
        explorer = f = open("soundexplorer_mel.txt", "r", encoding='utf-8')
    elif explorer_nr == 2:
        explorer = f = open("soundexplorer_amb.txt", "r", encoding='utf-8')
    else:    
        explorer = f = open("soundexplorer_eff.txt", "r", encoding='utf-8')
        
    explorer = f.read().split(",")
    explorer.sort()
    
    pygame.draw.rect(screen, (40, 40, 40), [250, 50, 1000, 680], 0, 8)
    pygame.draw.rect(screen, (150, 150, 150), [250, 50, 1000, 680], 6, 8)
    
    global explorer_x, explorer_y, rect_list, abbrechen # Sound-Liste erstellen
    explorer_x = []
    explorer_y = []
    rect_list = []
    abbrechen = [600, 660, 300, 50]
        
    for item in range(len(explorer)): # Einträge in Spalten und Zeilen anordnen
        explorer_x.append(item % 4)
        explorer_y.append(item // 4)
        rect_list.append([explorer_x[item] * 245 + 266,  explorer_y[item] * 42 + 68, 230, 24])
        pygame.draw.rect(screen, (100, 100, 100), rect_list[item])
        screen.blit(pygame.font.SysFont("arial.ttf", 28).render(explorer[item], True, (200, 200, 200)), [explorer_x[item] * 245 + 270,  explorer_y[item] * 42 + 70])
        
    pygame.draw.rect(screen, (150, 150, 150), abbrechen, 0, 5)
    pygame.draw.rect(screen, (200, 200, 200), abbrechen, 4, 5)
    
    screen.blit(pygame.font.SysFont("arial.ttf", 32).render("Abbrechen", True, 
                                                  (0, 0, 0)), [690, 675])
    
    pygame.display.flip()

# Klassendefinition für Buttons

class Button:
    def __init__(self, pos_x, pos_y, breite, hoehe):
        self.pos_x = pos_x               # int
        self.pos_y = pos_y               # int
        self.breite = breite             # int
        self.hoehe = hoehe               # int
        
    def button_malen(self):
        pygame.draw.rect(screen, (self.farbe), 
                         [self.pos_x, self.pos_y, 
                          self.breite, self.hoehe], 0, 4)
        if self.is_pressed == 1:
            pygame.draw.rect(screen, (255, 0, 0), 
                             [self.pos_x, self.pos_y, 
                              self.breite, self.hoehe], 5, 4)
        
        size = 26
        schrift = pygame.font.SysFont("arial.ttf", size)
        text_surface = schrift.render(self.Beschriftung, True, self.schriftfarbe)
        text_rect = text_surface.get_rect()
        text_rect.center = (int(self.pos_x + self.breite / 2), 
                            int(self.pos_y + 25))
        screen.blit(text_surface, text_rect)
        
        size = 18
        schrift = pygame.font.Font(None, size)
        text_surface = schrift.render("Loop", True, self.schriftfarbe)
        text_rect = text_surface.get_rect()
        text_rect.center = (int(self.pos_x + self.breite - 44), 
                            int(self.pos_y + self.hoehe - 18))
        screen.blit(text_surface, text_rect)
        
    def vol_malen(self):
        pygame.draw.rect(screen, (220, 220, 220), self.vol_rect)
        for v in range(10):
            pygame.draw.rect(screen, (20 + (self.volume <= v) * 160, 
                                      20 + (self.volume <= v) * 160, 
                                      20 + (self.volume <= v) * 160), self.vol_box[v])
        
    def loop_malen(self):
        pygame.draw.rect(screen, (150 + self.loop * 90, 
                                  100 - self.loop * 40, 
                                  100 - self.loop * 40), self.loop_rect, 0, 3)
        pygame.draw.rect(screen, (0, 0, 0), self.loop_rect, 2, 3)
        
# Buttons aus Klasse erstellen

for i in range(24): # Knöpfe 0 bis 23
    buttons.append(Button((i % 6) * 245 + 18, 
                          (i // 6) * 90 + (i // 12) * 80 + 67,
                          235, 
                          80))
    if i < 12:
        buttons[i].farbe = (50, 50, 220)
        buttons[i].schriftfarbe = (240, 240, 240)
    else:   
        buttons[i].farbe = (30, 210, 30)
        buttons[i].schriftfarbe = (40, 40, 40)
    buttons[i].loop = 1
    buttons[i].fade_start = 99999999
    buttons[i].fade_aktiv = False

for i in range(8): # Knöpfe 24 bis 31
    buttons.append(Button((i % 4) * 195 + 18, 
                          (i // 4) * 80 + (i // 12) * 80 + 590,
                          185, 
                          70))
    buttons[i + 24].farbe = (220, 200, 0)
    buttons[i + 24].schriftfarbe = (40, 40, 40)
    buttons[i + 24].loop = -1
    buttons[i].fade_aktiv = False

# Titel und Ladebalken

pygame.draw.rect(screen, (200, 200, 200), [300, 500, 900, 80], 4, 5)
screen.blit(pygame.font.SysFont("arial.ttf", 60).render("Soundpad wird gestartet...", True, (200, 200, 200)), [480, 295])
pygame.display.flip()

for i in range(32): # Allgemeine Variablen zuweisen
    buttons[i].Beschriftung = soundlist[i]
    buttons[i].vol_rect = [buttons[i].pos_x + 9, 
                          buttons[i].pos_y + buttons[i].hoehe - 26, 
                          113, 
                          14]
    buttons[i].vol_box = []
    buttons[i].volume = 5
    buttons[i].fade_in = 0
    for v in range(10):
        buttons[i].vol_box.append([buttons[i].vol_rect[0] + 11 * v + 2, 
                                  buttons[i].vol_rect[1] + 2, 
                                  10, 10])
    
    buttons[i].loop_rect = [buttons[i].pos_x + buttons[i].breite - 27, 
                          buttons[i].pos_y + buttons[i].hoehe - 27, 
                          20, 
                          20]
    
    buttons[i].is_pressed = -1
    buttons[i].repeat = False
    
    buttons[i].sound = mixer.Sound("Musik\Empty.mp3")
    pygame.time.delay(40)
    buttons[i].sound_eingelesen = False
    
    pygame.draw.rect(screen, (60 + i * 5, 60 + i * 5, 60 + i * 5), [i * 27 + 310, 510, 24, 60], 0, 4)
    pygame.display.flip()
    
pygame.draw.rect(screen, (0, 0, 0), [0, 0, 3840, 2160])
pygame.display.flip()
    
# Globale Steuerung

button_stop = Button(825, 590, 200, 70) # Stop-Button

button_exit = Button(825, 670, 200, 70) # Exit-Button

for quick in range(9): # Quick-Volume-Buttons
    
    button_quick_vol.append(Button(1103 + (quick % 3) * 46, 620 + (quick // 3) * 28, 41, 20))

button_fade = Button(1130, 709, 70, 26) # Fade-Button

def globale_steuerung_malen():
    pygame.draw.rect(screen, (80, 80, 80), [button_stop.pos_x, button_stop.pos_y, button_stop.breite, button_stop.hoehe], 0, 5)
    pygame.draw.rect(screen, (0, 0, 0), [button_stop.pos_x, button_stop.pos_y, button_stop.breite, button_stop.hoehe], 4, 5)
    screen.blit(pygame.font.SysFont("arial.ttf", 48).render("Stop", True, 
                                                  (0, 0, 0)), [885, 610])
    
    pygame.draw.rect(screen, (110, 0, 0), [button_exit.pos_x, button_exit.pos_y, button_exit.breite, button_exit.hoehe], 0, 5)
    pygame.draw.rect(screen, (250, 0, 0), [button_exit.pos_x, button_exit.pos_y, button_exit.breite, button_exit.hoehe], 6, 5)
    screen.blit(pygame.font.SysFont("arial.ttf", 48).render("EXIT", True, 
                                                  (250, 0, 0)), [882, 690])
    
    for ls in range(10): # Laden- und Speichern-Buttons malen
        pygame.draw.rect(screen, (80, 80, 80), [button_ls[ls].pos_x,                                                 button_ls[ls].pos_y, button_ls[ls].breite, button_ls[ls].hoehe], 0, 5)
        if ls == soundset_geladen - 1:
            pygame.draw.rect(screen, (200, 200, 200), [button_ls[ls].pos_x,                                                 button_ls[ls].pos_y, button_ls[ls].breite, button_ls[ls].hoehe], 0, 5)
            
        pygame.draw.rect(screen, (0, 0, 0), [button_ls[ls].pos_x,                                                 button_ls[ls].pos_y, button_ls[ls].breite, button_ls[ls].hoehe], 2, 5)
        
        screen.blit(pygame.font.SysFont("arial.ttf", 28).render(f"{(ls % 5) + 1}", True, (0, 0, 0)), pygame.font.SysFont("arial.ttf", 28).render(f"{(ls % 5) + 1}", True, (0, 0, 0)).get_rect(center=(button_ls[ls].pos_x + 20, button_ls[ls].pos_y + 20)))
        
    screen.blit(pygame.font.SysFont("arial.ttf", 28).render("Soundset laden", True, (240, 240, 240)), [1283, 595])
    screen.blit(pygame.font.SysFont("arial.ttf", 28).render("Soundset speichern", True, (240, 240, 240)), [1270, 675])
    
    # Quick Volume
    quick_vol_farbe = [[20, 20, 220], [0, 220, 0], [220, 220, 0]]
    screen.blit(pygame.font.SysFont("arial.ttf", 28).render("Quick Volume", True, (240, 240, 240)), [1065, 595])
    for quick in range(3):
        pygame.draw.rect(screen, (quick_vol_farbe[quick]), [1035,                                                 620 + quick * 28, 60, 20], 0, 5)
        
    quick_vol_beschriftung = ["-1", "5", "+1"]
    for q in range(9): # Quick-Volume-Buttons malen
        pygame.draw.rect(screen, (80, 80, 80), [button_quick_vol[q].pos_x,                                                 button_quick_vol[q].pos_y, button_quick_vol[q].breite, button_quick_vol[q].hoehe], 0, 5)
        pygame.draw.rect(screen, (0, 0, 0), [button_quick_vol[q].pos_x,                                                 button_quick_vol[q].pos_y, button_quick_vol[q].breite, button_quick_vol[q].hoehe], 2, 5)
        screen.blit(pygame.font.SysFont("arial.ttf", 22).render(quick_vol_beschriftung[q % 3], True, (0, 0, 0)), [1118 + (q % 3) * 46 + (2 * (q % 3 == 1)) + (-3 * (q % 3 == 2)), 624 + (q // 3) * 28])
        
    # Fade-Option
    screen.blit(pygame.font.SysFont("arial.ttf", 28).render("Fade", True, (240, 240, 240)), [1065, 712])
    pygame.draw.rect(screen, (80 + 60 * fade, 80 + 60 * fade, 80 + 60 * fade), [1130, 709, 70, 26], 0, 20)
    pygame.draw.rect(screen, (0, 0, 0), [1130, 709, 70, 26], 2, 20)
    pygame.draw.circle(screen, (200 + fade * 55, 200 - fade * 180, 200 - fade * 180), (1130 + 10 + (fade * 50), 709 + 13), 16)
    pygame.draw.circle(screen, (0, 0, 0), (1130 + 10 + (fade * 50), 709 + 13), 16, width=3)
        
# Buttons Laden und Speichern

for ls in range(10):
    button_ls.append(Button(1248 + (ls % 5) * 48, 620 + (ls // 5) * 80 , 40, 40))
    
# Bildschirm aktualisieren

def alles_malen():

    alle_rahmen_malen()
    for i in range(32):        
        buttons[i].button_malen()
        buttons[i].loop_malen()
        buttons[i].vol_malen()
    globale_steuerung_malen()
    pygame.display.flip()
    
alles_malen()

### GAME LOOP ###

run = True
while run:
    
    for fading in range(24): # Prüfen, ob Sound ausgefadet werden soll
        if fade and not buttons[fading].repeat and not buttons[fading].loop == 1:
            print(buttons[fading].loop)
            if buttons[fading].fade_aktiv == False:
                if pygame.time.get_ticks() > buttons[fading].fade_start:
                    buttons[fading].sound.fadeout(buttons[fading].fade_in)
                    buttons[fading].fade_aktiv = True
    
    for repeat in range(32): # Sound neustarten, wenn Loop nach Start aktiviert wurde
        if not pygame.mixer.Channel(repeat).get_busy() and buttons[repeat].repeat:
            w = int((buttons[repeat].loop + 1) / -2)
            buttons[repeat].repeat = False
            buttons[repeat].is_pressed = 1
            buttons[repeat].button_malen()
            buttons[repeat].vol_malen()
            buttons[repeat].loop_malen()
            pygame.display.flip()
            pygame.mixer.Channel(repeat).play(buttons[repeat].sound, w, 0, buttons[repeat].fade_in)
    
    for z in range(32): # bei ausgelaufenen Sounds Button deaktivieren
        if buttons[z].is_pressed == 1 and not pygame.mixer.Channel(z).get_busy():
            buttons[z].is_pressed *= -1
            buttons[z].fade_aktiv = False
            buttons[z].button_malen()
            buttons[z].vol_malen()
            buttons[z].loop_malen()
            pygame.display.flip()
           
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            click = pygame.mouse.get_pressed()
            click_pos = pygame.mouse.get_pos()
            
            if click  == (1, 0, 0): # Nutzer hat linke Maustaste gedrückt
                
                for soundset in range(5): # Buttons "laden" geklickt
                    
                    if pygame.Rect([button_ls[soundset].pos_x, 
                                    button_ls[soundset].pos_y, 
                                    button_ls[soundset].breite, 
                                    button_ls[soundset].hoehe]).collidepoint(click_pos):
                        for stopsound in range(32): 
                            buttons[stopsound].repeat = False
                            buttons[stopsound].sound_eingelesen = False
                            buttons[stopsound].sound.stop()
                        
                        pygame.draw.rect(screen, (30, 30, 30), [410, 300, 700, 200], 0, 5)
                        screen.blit(pygame.font.SysFont("arial.ttf", 48).render(f"Soundset {soundset + 1} wird geladen...", True, (200, 200, 200)), [540, 380])
                        pygame.display.flip()
                        soundset_geladen = soundset + 1
                        liste_laden = f = open(f"soundlist{soundset_geladen}.txt", "r")
                        liste_laden = f.read().split(",")
                       
                        for i in range(32): 
                            start = pygame.time.get_ticks()
                            if buttons[i].Beschriftung != liste_laden[i]:
                                buttons[i].Beschriftung = liste_laden[i]
                        pygame.time.delay(1000)
                                
                        pygame.draw.rect(screen, (0, 0, 0), [0, 0, breite, hoehe])
                        alles_malen()
                
                for soundset in range(5,10): # Buttons "speichern" geklickt
                    
                    if pygame.Rect([button_ls[soundset].pos_x, 
                                    button_ls[soundset].pos_y, 
                                    button_ls[soundset].breite, 
                                    button_ls[soundset].hoehe]).collidepoint(click_pos):
                        pygame.draw.rect(screen, (30, 30, 30), [410, 300, 700, 200], 0, 5)
                        screen.blit(pygame.font.SysFont("arial.ttf", 48).render(f"Soundset {soundset -4} wird gespeichert...", True, (200, 200, 200)), [520, 380])
                        pygame.display.flip()
                        
                        liste_speichern = open(f"soundlist{soundset - 4}.txt", "w")
                        
                        pygame.time.delay(500)
                        
                        savelist = []
                        
                        for z in range(32):
                            savelist.append(buttons[z].Beschriftung)
                        
                        savelist = str(savelist)
                        savelist = savelist.replace(", ", ",")
                        savelist = savelist.replace("'", "")
                        savelist = savelist.replace("[", "")
                        savelist = savelist.replace("]", "")
                                             
                        liste_speichern.write(savelist)
                        liste_speichern.close()
                        
                        pygame.draw.rect(screen, (0, 0, 0), [0, 0, breite, hoehe])
                        alles_malen()
                
                for quick_vol in range(9): # Buttons Quick-Volume geklickt
                    
                    if pygame.Rect([button_quick_vol[quick_vol].pos_x, 
                                    button_quick_vol[quick_vol].pos_y, 
                                    button_quick_vol[quick_vol].breite, 
                                    button_quick_vol[quick_vol].hoehe]).collidepoint(click_pos):
                        pygame.draw.rect(screen, (200, 200, 200), [button_quick_vol[quick_vol].pos_x,                                                 button_quick_vol[quick_vol].pos_y, button_quick_vol[quick_vol].breite, button_quick_vol[quick_vol].hoehe], 0, 5)
                        pygame.draw.rect(screen, (0, 0, 0), [button_quick_vol[quick_vol].pos_x,                                                 button_quick_vol[quick_vol].pos_y, button_quick_vol[quick_vol].breite, button_quick_vol[quick_vol].hoehe], 2, 5)
                        pygame.display.flip()
                        
                        if quick_vol // 3 == 0:
                            bereich = [0, 11]
                        elif quick_vol // 3 == 1:
                            bereich = [12, 23]
                        else: bereich = [24, 31]
                                                
                        if quick_vol % 3 == 0:
                            vol_neu = -1
                        elif quick_vol % 3 == 1:
                            vol_neu = 5
                        else: vol_neu = 1
                        
                        for vol_setzen in range(bereich[0], bereich[1] + 1):
                            if vol_neu == -1:
                                buttons[vol_setzen].volume = max(1, buttons[vol_setzen].volume -1)
                            elif vol_neu == 1:
                                buttons[vol_setzen].volume = min(10, buttons[vol_setzen].volume +1)
                            else: buttons[vol_setzen].volume = 5
                            buttons[vol_setzen].sound.set_volume(buttons[vol_setzen].volume / 10)
                            
                        pygame.draw.rect(screen, (0, 0, 0), [0, 0, breite, hoehe])
                        alles_malen()
                
                if pygame.Rect([button_stop.pos_x, # Stop-Button gedrückt
                                button_stop.pos_y, 
                                button_stop.breite, 
                                button_stop.hoehe]).collidepoint(click_pos):
                    
                    pygame.draw.rect(screen, (180, 180, 180), [button_stop.pos_x, button_stop.pos_y, button_stop.breite, button_stop.hoehe], 0, 5)
                    pygame.draw.rect(screen, (0, 0, 0), [button_stop.pos_x, button_stop.pos_y, button_stop.breite, button_stop.hoehe], 4, 5)
                    screen.blit(pygame.font.SysFont("arial.ttf", 48).render("Stop", True, 
                                                                  (0, 0, 0)), [885, 610])
                    pygame.display.flip()
                    
                    for i in range(32):
                        buttons[i].repeat = False
                        buttons[i].sound.fadeout(buttons[i].fade_in * fade)
                    
                    pygame.draw.rect(screen, (0, 0, 0), [0, 0, 3840, 2160])
                    alles_malen()
                        
                if pygame.Rect([button_exit.pos_x, # Exit-Button gedrückt
                                button_exit.pos_y, 
                                button_exit.breite, 
                                button_exit.hoehe]).collidepoint(click_pos):
                    
                    pygame.draw.rect(screen, (200, 50, 50), [button_exit.pos_x, button_exit.pos_y, button_exit.breite, button_exit.hoehe], 0, 5)
                    pygame.draw.rect(screen, (100, 0, 0), [button_exit.pos_x, button_exit.pos_y, button_exit.breite, button_exit.hoehe], 6, 5)
                    screen.blit(pygame.font.SysFont("arial.ttf", 48).render("EXIT", True, 
                                                                  (100, 0, 0)), [882, 690])
                    pygame.display.flip()
                    pygame.time.delay(500)
                    run = False
                
                if pygame.Rect([button_fade.pos_x, # Fade-Button gedrückt
                                button_fade.pos_y, 
                                button_fade.breite, 
                                button_fade.hoehe]).collidepoint(click_pos):
                    fade = not fade
                    for f in range(24):
                        buttons[f].fade_in = 8000 * fade
                    
                    alles_malen()
                
                for i in range(32): # Loop geklickt
                    if pygame.Rect(buttons[i].loop_rect).collidepoint(click_pos) and not soundexplorer_offen:
                        buttons[i].loop *= -1
                        if buttons[i].is_pressed == 1 and buttons[i].loop == 1:
                            buttons[i].repeat = True
                            buttons[i].fade_start = 99999999
                            buttons[i].fade_in = 0
                        else:
                            buttons[i].repeat = False
                        buttons[i].loop_malen()
                        pygame.display.flip()
                    
                    elif pygame.Rect(buttons[i].vol_rect).collidepoint(click_pos) and not soundexplorer_offen:
                        for v in range(10): # Volume geklickt
                            if pygame.Rect(buttons[i].vol_box[v]).collidepoint(click_pos):
                                buttons[i].volume = v + 1
                                buttons[i].sound.set_volume(buttons[i].volume / 10)
                                buttons[i].vol_malen()
                                globale_steuerung_malen()
                                pygame.display.flip()
                                
                    elif pygame.Rect([buttons[i].pos_x, # Sound-Button gedrückt -> Play/Stop
                                      buttons[i].pos_y, 
                                      buttons[i].breite, 
                                      buttons[i].hoehe]).collidepoint(click_pos) and not soundexplorer_offen:
                        buttons[i].is_pressed *= -1
                        
                        if buttons[i].is_pressed == 1:
                            if buttons[i].sound_eingelesen == False:
                                buttons[i].sound = mixer.Sound(f"Musik\{buttons[i].Beschriftung}.mp3")
                                buttons[i].sound_eingelesen = True
                            buttons[i].sound.set_volume(buttons[i].volume / 10)
                            w = int((buttons[i].loop + 1) / -2)
                            pygame.mixer.Channel(i).play(buttons[i].sound, w, 0, buttons[i].fade_in)
                            buttons[i].fade_start = pygame.time.get_ticks() + buttons[i].sound.get_length() * 1000 - buttons[i].fade_in
                            buttons[i].repeat = w
                                
                        else:
                            buttons[i].sound.fadeout(buttons[i].fade_in * fade)
                            buttons[i].repeat = False
                            buttons[i].fade_aktiv = False
                        
                        alles_malen()
            
            if click  == (0, 0, 1): # Rechtsklick für Sound-Explorer
                for i in range(32):
                    if pygame.Rect([buttons[i].pos_x, 
                                    buttons[i].pos_y, 
                                    buttons[i].breite, 
                                    buttons[i].hoehe]).collidepoint(click_pos):
                        soundexplorer_offen = True
                        
                        if i < 12:
                            explorer_nr = 1
                        elif i < 24:
                            explorer_nr = 2
                        else:
                            explorer_nr = 3
                        
                        soundexplorer(explorer_nr)
                        
                        click = (0, 0, 0)
                        click_pos = (0, 0)
                        nichts_gewaehlt = True
                        while nichts_gewaehlt:
                            if pygame.Rect(abbrechen).collidepoint(click_pos):
                                nichts_gewaehlt = False
                                soundexplorer_offen = False
                                click = (0, 0, 0)
                                click_pos = (0, 0)
                            
                            for aktion in pygame.event.get():
                                if aktion.type == pygame.QUIT:
                                    pygame.quit()
                                if aktion.type == pygame.MOUSEBUTTONDOWN:
                                    click_pos= pygame.mouse.get_pos()
                                    for item in range(len(explorer)):
                                        if pygame.Rect(rect_list[item]).collidepoint(click_pos):
                                            buttons[i].Beschriftung = explorer[item]
                                            buttons[i].sound.stop()
                                            buttons[i].sound = mixer.Sound(f"Musik\{explorer[item]}.mp3")
                                            buttons[i].sound_eingelesen = True
                                            soundset_geladen = 0
                                            soundexplorer_offen = False
                                            nichts_gewaehlt = False
                                            buttons[i].is_pressed = -1
                                        if nichts_gewaehlt == False: click_pos = (0, 0)
                                        
                        pygame.draw.rect(screen, (0, 0, 0), [0, 0, 3840, 2160])
                        alles_malen()

pygame.quit()