
from tkinter import *
import random

# la class Menu est la classe qui gère le menu
class Menu():
    def __init__(self) -> None:
        self.menu = Tk()
        self.menu.title("Menu")
        self.menu.geometry("400x400")
        self.canvas_menu = Canvas(self.menu, width=400, height=400, bg='#b19cd9', highlightthickness=0,)
        self.canvas_menu.pack()
        self.menu.resizable(width=False, height=False)


        play = PhotoImage(file="play.png")
        quit = PhotoImage(file="quit.png")

        self.menu.bind("<Escape>", self.quit)
        self.menu.bind("<space>", self.jouer)

        self.canvas_menu.create_text(200, 55, text='AVALANCHE', fill="Black", font=("Impact", 50), anchor=CENTER)
        self.canvas_menu.create_text(200, 100, text='HAVE FUN !', fill="Black", font=("Impact", 20), anchor=CENTER)
        Button(self.canvas_menu, image=play, width=95, height=44, border=0, command=self.jouer).place(x =200, y= 160, anchor=N)
        Button(self.canvas_menu, image= quit, width=95, height=44, border=0, command=self.menu.destroy).place(x =200, y =220, anchor=N)

        self.menu.configure(background="white")
        self.menu.eval('tk::PlaceWindow . center' )
        self.menu.mainloop()
    
#Methode jouer permet de lancer la classe main dans une nouvelle fenetre

    def jouer(self, event=None) -> None:
        self.jeux = Jeux()
        self.jeux.fenetre_de_jeux.mainloop()
    
    def quit(self, event=None):
        self.menu.destroy()

#La class BouleDeNeige est la classe qui gère la position des boules de neige
#Elle contient les attributs x, y, et la taille de la boule de neige
#Elle contient la méthode MouvementBoules qui permet de déplacer les boules de neige
#Elle contient aussi les méthodes pour obtenir la position, le rayon de la boule de neige

class BouleDeNeige:
    def __init__(self, rayon, largeur_ecran, hauteur_ecran) -> None:
        
        self.largeur_ecran = largeur_ecran*0.95
        self.hauteur_ecran = hauteur_ecran*0.95
        
        self.x = random.randint(10, int(self.largeur_ecran))
        self.y = 64

        self.rayon = rayon

        self.torf = False

        self.VitesseX = random.randint(-10, 10)
        self.VitesseY = random.randint(4, 8)

    def MouvementBouleDeNeige(self, event=None):

#Definition des nouvelles coordonnées de la boule de neige
        self.x = self.x + self.VitesseX
        self.y = self.y + self.VitesseY

#Si la boule de neige sort de l'écran, on inverse la vitesse de la boule de neige
        if self.x > self.largeur_ecran or self.x < 0:
            self.VitesseX = -self.VitesseX

        if self.y + self.rayon*2 < 0:
            self.VitesseY = -self.VitesseY
        
#Si la boule de neige touche le bas de l'écran, on divise le rayon par 2
#On divise la vitesse de la boule de neige par 2
#Enfin on appellera la méthode MiseAJour pour que la boule de neige soit mise à jour
        if self.y + self.rayon*2 >= self.hauteur_ecran:
            self.rayon= int(self.rayon / 2)
            self.y -= self.VitesseY//2
            self.VitesseY = -self.VitesseY//2
            self.MiseAJour()
            
    def MiseAJour(self):
        return not self.torf

    def getRayon(self):
        return self.rayon

    def getPosition(self):
        return [self.x, self.y]

#La class Jeux est la classe qui gère le jeu
#Cette class contient la bouvle principale, nommée loop
#Elle contient une méthode pour créer les boules de neige
#Elle contient les méthodes pour gérer le temps, et les deplacements du pere noel

class Jeux:
    def __init__(self):
        self.fenetre_de_jeux = Toplevel()

        self.fenetre_de_jeux.title("Batailles de neige")
#Permet de mettre la fenetre de jeux en plein écran
        #self.fenetre_de_jeux.attributes('-fullscreen', True)

        self.largeur_ecran = self.fenetre_de_jeux.winfo_screenwidth()
        self.hauteur_ecran = self.fenetre_de_jeux.winfo_screenheight()

        self.canvas_fenetre_de_jeux = Canvas(self.fenetre_de_jeux, width=self.largeur_ecran, height=self.hauteur_ecran, bg='#5a99ad', highlightthickness=0)
        self.canvas_fenetre_de_jeux.pack()
#Creation d'un dictionnaire qui contient les images des boules de neige et les charges une seule fois
        self.image = {
                    4: [PhotoImage(file='boule4.gif'), 4],
                    8: [PhotoImage(file='boule8.gif'), 8],
                    16: [PhotoImage(file='boule16.gif'), 16],
                    32: [PhotoImage(file='boule32.gif'), 32],
                    64: [PhotoImage(file='boule64.gif'), 64]}
        
        self.ListeDesBoules={}
        
#Ici on crée les variables pour le temps avant la creation des boules de neige, et celui qui gere la fluidité du jeu

        self.FPS = 60
        self.chrono = 60
        self.compteurFrame = 0
        self.bouleTime = 0
        self.invincibleTime = 2
        self.invincible = False

        self.santa_image = PhotoImage(file='NoelG.gif')

        self.canvas_fenetre_de_jeux.create_text(self.largeur_ecran*0.8, self.hauteur_ecran*0.2, text=str(self.chrono), fill="white", font=("Helvetica", 100))
        self.santa = self.canvas_fenetre_de_jeux.create_image(self.largeur_ecran*0.5, self.hauteur_ecran*0.75, anchor=NW, image=self.santa_image)

#Creation des différent bindings pour les touches du clavier, quitter, faire bouger le père noel

        self.fenetre_de_jeux.bind("<Right>", self.move_right)
        self.fenetre_de_jeux.bind("<Left>", self.move_left)
        self.fenetre_de_jeux.bind("<space>", self.power)
        self.fenetre_de_jeux.bind("<Escape>", self.quit)

#appel des methodes pour lancer le jeux 

        self.loop()
        self.chronometre()
        
        self.fenetre_de_jeux.mainloop()

#Ces deux methodes permettent de faire bouger le père noel à droite et à gauche

    def move_left(self, event = None):
        self.check(1)
        x = -50
        y = 0
        self.santa_image.config(file='NoelG.gif')
        self.canvas_fenetre_de_jeux.move(self.santa, x, y)

    def move_right(self, event=None):
        self.check(1)
        x = 50
        y = 0
        self.santa_image.config(file='NoelD.gif')
        self.canvas_fenetre_de_jeux.move(self.santa, x, y)

#Cette méthode permet de gerer le temps du chronometre
#De plus, elle permet d'arreter le jeux si le temps est écoulé, le joeur a gagner
#Elle s'arrete si le joeur a touché une boule de neige

    def chronometre(self):
        if self.chrono <= 1:
            self.chrono -= 1
            self.canvas_fenetre_de_jeux.itemconfigure(1, text=str(self.chrono))
            return True

        if self.check(2):
            return
        
        else:
            self.chrono -= 1
            self.canvas_fenetre_de_jeux.itemconfigure(1, text=str(self.chrono))

#Cette méthode verrifier si le père noel sort de l'ecran et donc de l'arreter
#On dissocie tous les bind et on les remet si le perme noel peut bouger et n'est pas a une extremité de l'ecran

    def check(self, event):
        v = self.canvas_fenetre_de_jeux.coords(self.santa)
        if event == 1 :
            if v[0] < 30:
                self.fenetre_de_jeux.unbind("<Left>")
            if v[0] > 30:
                self.fenetre_de_jeux.bind("<Left>", self.move_left)

            if v[0] < self.largeur_ecran - 110:
                self.fenetre_de_jeux.bind("<Right>", self.move_right)
            if v[0] > self.largeur_ecran - 110:
                self.fenetre_de_jeux.unbind("<Right>")
        if event == 2:
            if len(self.canvas_fenetre_de_jeux.find_overlapping(v[0], v[1], v[0]+88, v[1]+155)) > 1 and self.invincible == False:
                self.fenetre_de_jeux.unbind("<Left>")
                self.fenetre_de_jeux.unbind("<Right>")
                return True

    def power(self, event=None):
        self.invincible = True
        self.canvas_fenetre_de_jeux.create_text(self.largeur_ecran*0.5, self.hauteur_ecran*0.2, text="INVINCIBLE", fill="black", font=("Impact", 50, ), tag="invincible")

#La methodes loop est la boucle primaire du jeux sans elle rien ne se passe

    def loop(self):

        if self.check(2):
            self.fenetre_de_jeux.unbind("<space>")
            self.canvas_fenetre_de_jeux.create_text(self.largeur_ecran*0.5, self.hauteur_ecran*0.5, text='PERDU', fill="black", font=("Impact", 300))
            self.fenetre_de_jeux.after(1500, self.fenetre_de_jeux.destroy)
            return


        if self.compteurFrame >= self.FPS:
            self.compteurFrame = 0
            
            if self.invincible == True:
                self.invincibleTime -= 1
                if self.invincibleTime <= 0:
                    self.canvas_fenetre_de_jeux.delete("invincible")
                    self.invincible = False
                    self.invincibleTime = 2

            if self.chronometre():
                self.canvas_fenetre_de_jeux.create_text(self.largeur_ecran*0.5, self.hauteur_ecran*0.5, text='GAGNÉ', fill="black", font=("Impact", 300))
                self.fenetre_de_jeux.after(1500, self.fenetre_de_jeux.destroy)
                return

        if len(self.ListeDesBoules) < 10 and self.bouleTime <= 0:
            self.bouleTime = 30
            self.creerboule()
        
        MiseAJourDesBoules=[]
        for key in self.ListeDesBoules:
            self.ListeDesBoules[key].MouvementBouleDeNeige()
            
            position = self.ListeDesBoules[key].getPosition()

            self.canvas_fenetre_de_jeux.moveto(key, x=position[0], y=position[1])
            
            if self.ListeDesBoules[key].MiseAJour() :
                MiseAJourDesBoules.append(key)

        for key in MiseAJourDesBoules: 
            if self.ListeDesBoules[key].rayon/2 < 4:
                self.canvas_fenetre_de_jeux.itemconfigure(key, state='hidden')
                del self.ListeDesBoules[key]
            else:
                self.canvas_fenetre_de_jeux.itemconfigure(key, image=self.image[self.ListeDesBoules[key].rayon][0])

        self.bouleTime -= 1
        self.compteurFrame += 1
        
        self.fenetre_de_jeux.after(1000//self.FPS, self.loop)

#methode pour creer une boule de neige
#elle permet d'associe un objet boule de neige a une image 

    def creerboule(self,event=None):

        RayonDesBoules=[4, 8, 16, 32, 64]
        Rayon = random.choice(RayonDesBoules)
        boule = self.canvas_fenetre_de_jeux.create_image(0,0)
    
        self.ListeDesBoules[boule] = BouleDeNeige(Rayon , self.largeur_ecran, self.hauteur_ecran)
        
        self.canvas_fenetre_de_jeux.itemconfigure(boule, image=self.image[Rayon][0] )
        self.canvas_fenetre_de_jeux.moveto(boule, x=self.ListeDesBoules[boule].getPosition()[0], y=self.ListeDesBoules[boule].getPosition()[1])
            
    def quit(self, event=None):
        self.fenetre_de_jeux.destroy()

menu = Menu()