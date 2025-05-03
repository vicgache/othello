import tkinter as tk
from tkinter.colorchooser import askcolor

from game import *

from time import sleep
from PIL import Image, ImageTk, ImageSequence


def on_click(event):
    """
    Fonction centralisant tous ce qui se passe quand un clic est effectué
    :param event: permet de récupérer l'objet qui a émis la commande et ses méthodes (également son widget parent)
    :return:
    """
    if event.widget.master.game.in_process or event.widget.color != EMPTY or event.widget.master.game.gameover:
        return -1  # teste si un processus n'est pas déjà en cours et si la case cliquée est vide
    event.widget.master.game.in_process = True  # indique qu'un processus est en cours

    x, y = event.widget.get_pos()
    # récupère les coordonées x et y de la case cliquée

    toswitch = event.widget.master.game.table.process(x, y)
    # récupères les cases à modifier
    if not len(toswitch) == 0:
        action(event.widget.master, (x, y), toswitch)  # modifie les cases si cette action est valide (= si les au moins
        # une case est affectée par le coup

        if event.widget.master.options["showRewards"]:
            event.widget.master.update_rewards()

    event.widget.master.game.in_process = False  # indique qu'aucune action n'est plus en cours


def on_hover(event):
    """
    fonction activée quand on passe sur une case, affiche si on peut placer un pion ici ou non
    :param event:
    :return:
    """
    if event.widget.color == EMPTY and not event.widget.master.game.in_process \
            and event.widget.master.options["showPrevisions"] and not event.widget.master.game.gameover:
        # si la case est vide et qu'aucun processus n'est en cours
        x, y = event.widget.get_pos()
        if not event.widget.master.game.table.move_possibility(x, y):  # si aucun move n'est possible sur cette case
            event.widget.display_possiblility(0, EMPTY)  # afficher la croix
        else:
            event.widget.display_possiblility(1, event.widget.master.game.get_whosturn())  # afficher un pion à moitié
            # transparent de la couleur du joueur à qui s'est le tour


def on_leave(event):
    """
    fonction activée quand on quitte une case, retire l'affichage (= la preview)
    :param event:
    :return:
    """
    if event.widget.prevision is not None:  # si une preview est affiché sur cette case
        event.widget.delete(event.widget.prevision)  # efface cette preview
        event.widget.prevision = None  # indique que plus aucune preview est affichée sur cette case


class Cell(tk.Canvas):

    def __init__(self, master, x, y, images, color):
        """
        Classe gèrant les actions possibles par les cases individuelles du plateau.
        :param master: plateau contenant les cases
        :param x: abscisse de la case sur le plateau
        :param y: ordonée de la case sur le plateau
        :param images: reference vers les images à afficher sur les cases
        """
        super().__init__(master, bg=color, height='20m', width='20m', highlightbackground="black", highlightthickness=1)
        self.size = self.winfo_pixels('20m')
        self.x = x
        self.y = y
        self.color = EMPTY
        self.grid(row=y, column=x)
        # initialise la case pour qu'elle ne contienne pas de pion et qu'elle soit placée au bon endroit
        self.bind('<Button-1>', on_click)  # appelle la fonction on_click quand on clique gauche sur la case
        self.bind('<Enter>', on_hover)
        self.bind('<Leave>', on_leave)
        self.prevision = None  # affichage indiquant si oui ou non on peut placer un pion ici lorsqu'on passe sur la
        # case (methode de canvas)
        self.reward = None  # affichage indiquand le nombre de case qu'un coup sur cette case retournerait (methode
        # de canvas)
        self.images = images  # dictionnaire d'images passé depuis Board

    def get_pos(self):
        return self.x, self.y  # renvoie la position de la case dans la grille sous forme de liste

    def display_possiblility(self, possibility, turn):
        """
        fonction affichant une croix ou un pion semi-transparent lorsqu'on passe sur une case selon que placer ici est
        possible ou non
        :param possibility: true si il est possible de placer, false sinon
        :param turn: à qui c'est le tour de jouer, détermine la couleur du pion affiché
        :return:
        """

        if possibility:
            if turn == -1:
                self.prevision = super().create_image(self.size/2, self.size/2, image=self.images['halfblackpawn'])
            elif turn == 1:
                self.prevision = super().create_image(self.size/2, self.size/2, image=self.images['halfwhitepawn'])
        else:
            self.prevision = super().create_image(self.size/2, self.size/2, image=self.images['impossiblecross'])

    def update_display(self):
        """
        mets à jour l'affichage selon la valeur de la "couleur" de la case (associée à une valeur numérique), n'est
        appelée que dans les autres méthodes de la fonction
        :return:
        """
        super().delete('all')  # vide le canvas de tous ses éléments précédents
        if self.color == BLACK:
            super().create_image(self.size/2, self.size/2, image=self.images['blackpawn'])
        elif self.color == WHITE:
            super().create_image(self.size/2, self.size/2, image=self.images['whitepawn'])
        self.update()

    def play_gif(self, source):
        """
        Joue un gif (selectionnalbe en entrant son chemin dans source) sur la case en séparant ses images de 15
        centièmes de secondes, utilisé pour jouer les animations d'apparition d'une pièce ou son retournement
        :param source: liste d'objets tkImages contenant les images du gif
        :return:
        """

        for image in source:  # pour chaque image du gif
            super().delete('all')  # supprimer tout ce qui se trouve sur la case

            super().create_image(self.size/2, self.size/2, image=image)
            self.update()
            # affiche l'image

            sleep(150 / 1000)  # attends 15 centièmes de secondes (avant de jouer l'image suivante)


class Board(tk.Frame):

    def __init__(self, master, gamemode, options):
        """
        Classe regroupant les actions agissants sur toutes les cases et les regroupant toutes dans une grille. Initalise
        les cases sur le modèle d'un tableau de valeurs fourni. Contient les images et les animations à affichier sur le
        plateau
        :param master: widget Gui : gui global
        :param gamemode: 2 si on doit charger la sauvegarde, 1 si joueur contre ordinateur, 0 si joueur contre joueur
        (à passer à board)
        :param options: options de options.json chargées dans le GUI et passées plus bas
        """
        super().__init__(master, height='161m', width='161m', highlightbackground="black", highlightthickness=2)

        self.options = options  # récupère les options passés par Gui

        self.game = Othello(gamemode, self.options['cpuColor'])  # initialise le système de jeu avec le bon gamemode et
        # l'indication de quelle couleur joue l'ordinateur
        size = self.winfo_pixels('20m')

        self.images = {
            'blackpawn': ImageTk.PhotoImage(Image.open("./images/board/fullblack.png").resize((size, size))),
            'whitepawn': ImageTk.PhotoImage(Image.open("./images/board/fullwhite.png").resize((size, size))),
            'halfblackpawn': ImageTk.PhotoImage(Image.open("./images/board/halfblack.png").resize((size, size))),
            'halfwhitepawn': ImageTk.PhotoImage(Image.open("./images/board/halfwhite.png").resize((size, size))),
            'impossiblecross': ImageTk.PhotoImage(Image.open("./images/board/notpossible.png").resize((size, size))),
            'boarddecoration': ImageTk.PhotoImage(Image.open("./images/board/dot.png").resize((round(size / 12),
                                                                                               round(size / 12))))

        }
        # contient les images utilisées sur le plateau

        self.animations = {
            'blacktowhiteflip': [ImageTk.PhotoImage(frame.resize((size, size)))
                                 for frame in ImageSequence.Iterator(Image.open("./images/animations/btw.gif"))],
            'whitetoblackflip': [ImageTk.PhotoImage(frame.resize((size, size)))
                                 for frame in ImageSequence.Iterator(Image.open("./images/animations/wtb.gif"))],
            'placeblack': [ImageTk.PhotoImage(frame.resize((size, size)))
                           for frame in ImageSequence.Iterator(Image.open("./images/animations/placeblack.gif"))],
            'placewhite': [ImageTk.PhotoImage(frame.resize((size, size)))
                           for frame in ImageSequence.Iterator(Image.open("./images/animations/placewhite.gif"))]
        }  # utilise la librairie PIL pour extraire les différentes images d'un gif et les stocker dans une liste,
        # continent les animations jouées sur le plateau

        self.cells = []
        for x in range(0, 8):
            tmp_cell_list = []
            for y in range(0, 8):
                tmp_cell_list.append(
                    Cell(self, x, y, self.images, self.options['background']))
            self.cells.append(tmp_cell_list)
        # initalise toutes les cases du plateau (8x8) et les répértories dans sa grille

        self.board_decorations = self.create_board_decoration()  # crée les petits points décorant le plateau

        self.match_table()  # fait correspondre les valeurs des cases à celles du tableau de valeurs du système de jeu

        if self.options["showRewards"] and (gamemode == 2 or self.options['cpuColor'] != -1):
            self.update_rewards()  # affiche les previsions (combien de pions on retourne si on place ici)

    def create_board_decoration(self):
        """
        Crée et place au bon endroit les quatre petits points décorant le plateau de jeu
        :return: la liste de ces points pour pouvoir être initialisés en temps que variable
        """

        size = self.winfo_pixels('20m') / 12
        decorations = [
            tk.Label(self, image=self.images['boarddecoration'], height=size, width=size,
                     background=self.options['background'], borderwidth=0, highlightthickness=0),
            tk.Label(self, image=self.images['boarddecoration'], height=size, width=size,
                     background=self.options['background'], borderwidth=0, highlightthickness=0),
            tk.Label(self, image=self.images['boarddecoration'], height=size, width=size,
                     background=self.options['background'], borderwidth=0, highlightthickness=0),
            tk.Label(self, image=self.images['boarddecoration'], height=size, width=size,
                     background=self.options['background'], borderwidth=0, highlightthickness=0)
        ]
        # liste de l'initialisation des points avec la bonne couleur de fond et l'image stockée dans images
        decorations[0].place(relx=(2/8), rely=(2/8), anchor=tk.CENTER)
        decorations[1].place(relx=(2/8), rely=(6/8), anchor=tk.CENTER)
        decorations[2].place(relx=(6/8), rely=(2/8), anchor=tk.CENTER)
        decorations[3].place(relx=(6/8), rely=(6/8), anchor=tk.CENTER)
        # placement des points au bon endroit

        return decorations

    def match_table(self):
        """
        Fait correspondre les valeurs des cases de Board (c'est-à dire ce qui est affiché) aux valeurs du tableau des
        pions de l'objet Table principal
        :return:
        """
        for x in range(0, 8):
            for y in range(0, 8):
                self.cells[x][y].color = self.game.table.get_tile(x, y)
                self.cells[x][y].update_display()

    def update_animation(self, x, y, toswitch, color):
        """
        Joue les animations  une fois qu'un coup est posé
        :param x: abscicce du coup posé
        :param y: ordonée du coup posé
        :param toswitch: liste des coups à modifier
        :param color: couleur qui vient de jouer
        :return:
        """
        for liste in self.cells:
            for cell in liste:
                if cell.reward is not None:
                    cell.delete(cell.reward)
        # pour toutes les cases, efface les previsions s'il y en a

        cells_to_switch = [self.cells[element[0]][element[1]] for element in toswitch]  # récupère les cells à modifier
        # à partir de leur coordonées

        if self.options['showAnimations']:  # si l'option showanimation est activée
            source = self.animations['placeblack'] if color == BLACK else self.animations['placewhite']
            self.cells[x][y].play_gif(source)
            self.cells[x][y].color = color
            # joue l'animation de pose de la bonne couleur selon la couleur qui vient de jouer puis confirme sa couleur

            for cell in cells_to_switch:
                if cell.color == BLACK:
                    cell.play_gif(self.animations['blacktowhiteflip'])
                    cell.color = WHITE
                elif cell.color == WHITE:
                    cell.play_gif(self.animations['whitetoblackflip'])
                    cell.color = BLACK
            # pour chauque cell à modifier, joue l'animation de retournement de la bonne couleur puis confirme sa
            # couleur.
        else:
            self.cells[x][y].color = color
            self.cells[x][y].update_display()
            sleep(0.5)
            for cell in cells_to_switch:
                if cell.color == BLACK:
                    cell.color = WHITE
                elif cell.color == WHITE:
                    cell.color = BLACK
                cell.update_display()
            # affiche le pions posé puis change la couleur des pions retournés après un petit délai (pour la clarté du
            # jeu)

    def update_rewards(self):
        """
        Update les prevision pour chaque case, c'est à dire le nombre de pions retourné si on joue sur la case
        :return:
        """
        for liste in self.cells:
            for cell in liste:
                if cell.color == EMPTY:  # si la case est vide
                    if cell.reward is not None:
                        cell.delete(cell.reward)
                    # si la case a déjà une prévision, l'effacer

                    x, y = cell.get_pos()
                    would_switch = self.game.table.move_possibility(x, y)
                    if would_switch > 0:
                        cell.reward = cell.create_text(cell.size * .95, cell.size * .1, text=would_switch,
                                                       font=('Arial', 10), fill='black', anchor=tk.E)
                    # si le nombre de pions n'est pas nul, alors on l'affiche en haut à droite de la case

    def start_cpu(self):
        """
        Fait jouer l'odrinateur sur une case arbitraire (utilisé quand c'est son tour de commencer)
        :return:
        """
        sleep(.5)  # attend un court délai pour une transition fluide depuis le menu du jeu
        self.game.in_process = True
        action(self, [5, 4])  # pose le pion
        if self.options["showRewards"]:
            self.update_rewards()  # si l'option est activée, update les previsions
        self.game.in_process = False


class Gui(tk.Frame):

    def __init__(self, master, gamemode, assets):
        """
        Regroupe les éléments liés à  l'interface graphique à l'extérieur du plateau
        (contient également l'objet plateau). Créée une correspondance entre les options du jeu et l'affichage des
        settings. Contient les images qui vont être utilisé dans l'interface de jeu. Continent certains boutons du GUI.
        :param master: root (fenêtre de base de tkinter)
        :param gamemode: 2 si on doit charger la sauvegarde, 1 si joueur contre ordinateur, 0 si joueur contre joueur
        (à passer à board)
        """
        super().__init__(master, bg=BG)
        self.pack(fill=tk.BOTH, expand=1)
        # initialise la frame et la place sur toute la fenêtre
        self.options = load_options()  # récupère les options du fichier options.json
        self.assets = assets  # récupère les images passées à la création de la fenêtre (par la classe Menu)

        self.board = Board(self, gamemode, self.options)
        self.board.place(x='12m', y='12m')
        # initialise le plateau à la bonne place

        self.black_scores, self.white_scores, self.turns_passed = self.create_scores()  # crée le visuel des scores
        self.update_scores()  # met les scores à jour (les fait refleter la situation du plateau)

        self.x_coordinates, self.y_coordinates = self.create_coordinates()  # crée le visuel des coordonées.
        if self.options['showCoordinates']:
            self.show_coordinates()
        # si l'option showCoordinates est affiché, affiche les coordonées

        tk.Label(self, image=self.assets['shrinkedlogo'], bg=BG, highlightthickness=0)\
            .place(x='180m', y='179m', anchor=tk.SW)  # affiche le logo

        self.main_buttons, self.go_back_button, self.start_again_button = self.create_main_buttons()
        # crée les boutons principaux

        self.tooltip = None
        self.create_sub_buttons()
        # crée les boutons secondaires

        self.settings = {}  # référence le dictionnaire settings utilisée plus tard dans le menu des règlages

        if gamemode == 0 and self.options['cpuColor'] == BLACK:
            self.board.start_cpu()
        # si on joue contre l'IA et que l'option cpuColor indique que l'ordinateur devrait commencer, fait jouer
        # l'ordinateur

    def end_game_animation(self):
        """
        Mofidife l'UI quand la partie est terminé pour indiquer qui a gagné ou perdu
        :return:
        """

        if self.go_back_button is not None:
            self.go_back_button.destroy()
        # si le bouton de retour en arrière existe, on le supprime pour faire de la place au bandeau de victoire/défaite

        color = "grey"  # Couleur par défaut = gris
        if self.board.game.winner == EMPTY:  # si il n'y a pas de gagnant
            text = "Egalité !"
        else:
            if self.board.game.gamemode == 0:  # si on joue contre l'IA
                if self.board.game.winner == self.options["cpuColor"]:  # si le gagnant est l'ordi
                    color = "red"
                    text = "Vous avez\nperdu !"
                else:
                    color = "green"
                    text = "Vous avez\ngagné"
            else:
                if self.board.game.winner == BLACK:  # si les noirs on gagné
                    text = "Le joueur noir\na gagné !"
                else:
                    text = "Le joueur blanc\na gagné"

        victory_banner = tk.Label(self.main_buttons, width=15, height=3, text=text, font=("Arial", 15), bg=color,
                                  highlightthickness=5, highlightbackground="black")
        victory_banner.place(relx=.5, y=0, anchor=tk.N)
        # Affiche le bandeau de victoire à la place du bouton de retour en arrière

        num_black_score, num_white_score, turn_count = self.board.game.get_scores()  # récupère les scores actuels

        m = self.winfo_pixels('1m')
        self.turns_passed.create_oval(1, 1, m * 9, m * 9, width=3, fill=BG, outline='black')
        self.turns_passed.create_text(m * 4.5, m * 4.5, text=str(turn_count), font=('Arial', 18), anchor=tk.CENTER)
        self.black_scores.create_oval(m, m, m * 42, m * 42, width=5, fill="black", outline="white")
        self.black_scores.create_text(m * 21.5, m * 21.5, text=str(num_black_score), font=('Arial', 52), fill="white",
                                      anchor=tk.CENTER)
        self.white_scores.create_oval(m, m, m * 42, m * 42, width=5, fill="white", outline="black")
        self.white_scores.create_text(m * 21.5, m * 21.5, text=str(num_white_score), font=('Arial', 52), fill='black',
                                      anchor=tk.CENTER)

        self.update()  # rend les modifications visibles

    def go_back(self):
        """
        Centralise les actions à effectuer quand on revient en arrière en utilisant le bouton
        :return:
        """

        self.board.game.load_state()  # charge la sauvegarde

        self.update_scores()  # modifie les scores
        self.board.match_table()  # update le plateau
        if self.options['showRewards']:
            self.board.update_rewards()
        # update les previsions de pions retournés si l'option showRewards est activée.

    def exit_window(self):
        """
        Ferme la fenêtre
        La croix de fermeture active aussi cette fonction
        :return:
        """
        if not self.board.game.file_protection:  # si aucun fichier n'est ouvert
            self.master.destroy()  # détruit la fenêtre de base (root)

    def create_settings(self):
        """
        Charge les options à partir du fichier options.py puis créé les valeurs d'affihcages correspondantes
        :return: le dictionnaires des valeurs d'affichages qui sera sauvegardé comme
        attribut
        """
        settings = {
            'showCoordinates': tk.BooleanVar(value=self.options['showCoordinates']),
            'showAnimations': tk.BooleanVar(value=self.options['showAnimations']),
            'allowCancel': tk.BooleanVar(value=self.options['allowCancel']),
            'background': tk.StringVar(value=self.options['background'])
        }
        # associe une option à une valeur grâce à un objet du bon type

        if self.options['showRewards']:
            settings['showHelp'] = tk.StringVar(value="Pions retournables")
        elif self.options['showPrevisions']:
            settings['showHelp'] = tk.StringVar(value="Possibilité de placer")
        else:
            settings['showHelp'] = tk.StringVar(value="Aucune")
        # combine les deux options showPrevision et showRewards en une seule valeur d'affichage

        return settings

    def dump_settings(self, windowtoclose):
        """
        Converti les settings affichés en les valeurs à rentrer dans le dictionnaire options puis enregistre celui-ci
        dans le fichier options.json
        :param windowtoclose: widget qu'il faut détruire une fois le processus fini
        :return:
        """
        for key, value in self.settings.items():
            if key in self.options:
                self.options[key] = value.get()
        # Si la clé d'un item existe dans les deux dictionnaires, simplement passer la valeur de settings à options

        if self.settings['showHelp'].get() == "Pions retournables":
            self.options['showRewards'] = True
            self.options['showPrevisions'] = True
        elif self.settings['showHelp'].get() == "Possibilité de placer":
            self.options['showRewards'] = False
            self.options['showPrevisions'] = True
        else:
            self.options['showRewards'] = False
            self.options['showPrevisions'] = False
        # converti le settings showHelp (trois possibilités) en deux valeurs booleens de self.options

        for liste in self.board.cells:
            for cell in liste:
                cell.config(bg=self.options['background'])
        # modifie la couleur du plateau selon la nouvelle couleur choisie

        if self.options['showRewards']:
            self.board.update_rewards()
        else:
            for liste in self.board.cells:
                for cell in liste:
                    if cell.reward is not None:
                        cell.delete(cell.reward)
                        cell.reward = None
        # affiche ou fait disparaitre les previsions de combien de pièces peuvent être retournés sur chaque case selon
        # l'option séléctionnée

        if self.options['showCoordinates']:
            self.show_coordinates()
        else:
            self.hide_coordinates()
        # affiche ou fait disparaitre les coordonées selon l'options séléctionnée

        self.update_scores()

        self.board.board_decorations = self.board.create_board_decoration()  # fait réaparaitre les points du plateau
        self.update()

        self.board.game.file_protection = True
        dump_options(self.options)
        self.board.game.file_protection = False
        # enregistre les valeurs de self.options dans le fichier options.json

        windowtoclose.destroy()  # ferme la fenêtre des règlages

    def exit_menu(self, windowtoclose):
        self.board.board_decorations = self.board.create_board_decoration()
        windowtoclose.destroy()

    def settings_menu(self):
        """
        Affiche la fenêtre des règlages (depuis l'interface de jeu) et crée les boutons permettant de les modifier
        :return:
        """
        if self.board.game.in_process:
            return  # n'affiche pas le menu si une action est en cours

        self.settings = self.create_settings()  # charge l'affichage des règlages à partir des options brutes

        for element in self.board.board_decorations:
            element.destroy()
        # supprime les décorations du plateau qui viendraient gener l'affichage

        window = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        window.place(x=0, y=0, relheight=1, relwidth=1)
        #  initialise le widget du menu et le fait occuper toute la fenêtre

        window.update()
        w = window.winfo_width()
        h = window.winfo_height()
        # récupère la taille de la fenêtre en pixels pour afficher l'interface en fonction

        window.create_image(.5 * w, .5 * h, image=self.assets['settingsbackground'])
        # affiche le fond stocké dans les assets

        window.create_text(.5 * w, .1 * h, text="Règlages d'affichage", font=("Arial", 35))

        window.create_text(10, .2 * h, text="Afficher les coordonées:", font=("Arial", 20), anchor=tk.W)
        window.create_text(10, .3 * h, text="Afficher les informations:", font=("Arial", 20), anchor=tk.W)
        window.create_text(10, .4 * h, text="Jouer les animations:", font=("Arial", 20), anchor=tk.W)
        window.create_text(10, .5 * h, text="Couleur du plateau:", font=("Arial", 20), anchor=tk.W)
        # affiche les intitulés des règlages d'affichage

        background_pevisualisation = tk.Frame(window, width='20m', height='12m', bg=self.settings['background'].get(),
                                              highlightthickness=3, highlightbackground='black')
        background_pevisualisation.place(relx=.725, rely=.5, anchor=tk.W)

        # affiche la previsualisation de la couleur du plateau

        def set_color():
            value = askcolor(self.settings['background'].get())[1]
            color = value if value is not None else self.settings['background'].get()
            self.settings['background'].set(color)
            background_pevisualisation.config(bg=color)

        # change si la couleur du fond si l'utilisateur a entré une couleur sinon garde la même et modifie la preview

        tk.Checkbutton(window, variable=self.settings['showCoordinates'], onvalue=True, offvalue=False,
                       image=self.assets['uncheckedbox'], selectimage=self.assets['checkedbox'],
                       indicatoron=False, width='10m', height='10m').place(relx=.8, rely=.2, anchor=tk.W)
        tk.OptionMenu(window, self.settings['showHelp'], "Aucune", "Possibilité de placer", "Pions retournables") \
            .place(relx=.8, rely=.3, anchor=tk.W)
        tk.Checkbutton(window, variable=self.settings['showAnimations'], onvalue=True, offvalue=False,
                       image=self.assets['uncheckedbox'], selectimage=self.assets['checkedbox'],
                       indicatoron=False, width='10m', height='10m').place(relx=.8, rely=.4, anchor=tk.W)
        tk.Button(window, command=set_color, text="Choisir", font=("Arial", 20), height=1, width=9, bg=THIRDCOLOR) \
            .place(relx=.8, rely=.5, anchor=tk.W)
        # crée les widgets permettant de regler les options d'affichage

        tk.Button(window, command=lambda: self.exit_menu(window), text="Annuler", font=("Arial", 20), width=9, height=1,
                  bg=THIRDCOLOR, highlightthickness=0, borderwidth=3).place(relx=.65, rely=.9, anchor=tk.E)
        tk.Button(window, command=lambda: self.dump_settings(window), text="Enregistrer", font=("Arial", 20), width=13,
                  height=1, bg=THIRDCOLOR, highlightthickness=0, borderwidth=3).place(relx=.9, rely=.9, anchor=tk.E)

        # crée les boutons de sauvegarde et de retour en arrière

    def create_scores(self):
        """
        Mets en place l'affichage des scores sur le GUI
        :return: Les canvas des scores pour être initialisées comme attribut
        """
        scores = tk.Frame(self, width='108m', height='50m',  bg=BG, highlightthickness=0)
        scores.place(x='185m', y='12m')
        # crée l'espace ou les scores seront affichés et le positionne en haut à droite du plateau

        black_scores = tk.Canvas(scores, width='48m', height='48m', bg=BG, highlightthickness=0, borderwidth=0)
        white_scores = tk.Canvas(scores, width='48m', height='48m', bg=BG, highlightthickness=0, borderwidth=0)
        turns_passed = tk.Canvas(scores, width='12m', height='12m', bg=BG, highlightthickness=0, borderwidth=0)
        black_scores.pack(side=tk.LEFT)
        turns_passed.pack(side=tk.LEFT, anchor=tk.S)
        white_scores.pack(side=tk.LEFT)
        # crée les canvas ou seront "dessinées" les interfaces des scores et les positionnes cote à cote

        m = self.winfo_pixels('1m')
        turns_passed.create_oval(1, 1, m * 9, m * 9, width=3, fill=BG, outline='black')
        turns_passed.create_text(m * 4.5, m * 4.5, text="1", font=('Arial', 18), anchor=tk.CENTER)
        black_scores.create_oval(m, m, m * 42, m * 42, width=5, fill="black", outline=self.options['background'])
        black_scores.create_text(m * 21.5, m * 21.5, text="2", font=('Arial', 52), fill="white", anchor=tk.CENTER)
        white_scores.create_oval(m, m, m * 42, m * 42, width=5, fill="white", outline="black")
        white_scores.create_text(m * 21.5, m * 21.5, text="2", font=('Arial', 52), fill='black', anchor=tk.CENTER)
        # dessine l'interface des scores avec leurs valeurs par défaut au centre de ces toiles

        return black_scores, white_scores, turns_passed

    def update_scores(self):
        """
        Mets les scores à jour selon l'état du plateau et de la partie
        :return:
        """
        num_black_score, num_white_score, turn_count = self.board.game.get_scores()  # récupère les valeurs des scores
        # pour chaque joueur et le nombre de tours joués

        if self.board.game.table.turn == WHITE:
            color_white = self.options['background']
            color_black = "white"
        else:
            color_white = "black"
            color_black = self.options['background']
        # Choisis la couleur de contur de la bulle de score de chaque joueur en fonction du tour (
        # si c'est son tour : rouge, sinon : couleur adverse)

        m = self.winfo_pixels('1m')
        self.turns_passed.create_oval(1, 1, m * 9, m * 9, width=3, fill=BG, outline='black')
        self.turns_passed.create_text(m * 4.5, m * 4.5, text=str(turn_count), font=('Arial', 18), anchor=tk.CENTER)
        self.black_scores.create_oval(m, m, m * 42, m * 42, width=5, fill="black", outline=color_black)
        self.black_scores.create_text(m * 21.5, m * 21.5, text=str(num_black_score), font=('Arial', 52), fill="white",
                                      anchor=tk.CENTER)
        self.white_scores.create_oval(m, m, m * 42, m * 42, width=5, fill="white", outline=color_white)
        self.white_scores.create_text(m * 21.5, m * 21.5, text=str(num_white_score), font=('Arial', 52), fill='black',
                                      anchor=tk.CENTER)
        # dessine les nouveaux scores par dessus les anciens

        self.update()  # rend les changements visibles
        if self.board.game.gamemode == 0 and self.board.game.table.turn == self.board.game.cpu_color:
            sleep(1)
        # si c'est au tour de l'ordinateur de jouer, attends un court délai (pour marquer le changement de tour)

    def create_coordinates(self):
        """
        Crée les widgets destinés à accueillir le système de coordonées
        :return: les frames crées pour être initialisées comme attribut
        """
        x_coordinates = tk.Frame(self, width='161m', height='12m', bg=BG)
        x_coordinates.place(x='12m', y=0)
        y_coordinates = tk.Frame(self, width='12m', height='161m', bg=BG)
        y_coordinates.place(x=0, y='12m')
        # crée et place les widgets au bon endroit

        self.update()  # rend les changements visibles

        return x_coordinates, y_coordinates

    def hide_coordinates(self):
        """
        Détruit les coordonées si elles existent (laisse les widgets les contentant)
        :return:
        """
        for letter in self.x_coordinates.winfo_children():
            letter.destroy()
        for digit in self.y_coordinates.winfo_children():
            digit.destroy()

        self.update()

    def show_coordinates(self):
        """
        Affiche le set the coordones dans les emplacements créés précédemments
        :return:
        """
        self.hide_coordinates()  # s'assure qu'il n'y ait plus de coordonées déjà en place
        m = self.winfo_pixels('1m')
        for i in range(8):  # itère les chiffres de 1 à 8 et les lettres de A à F
            letter = tk.Canvas(self.x_coordinates, width='20m', height='12m', bg=BG, highlightthickness=0)
            letter.pack(side=tk.LEFT)
            letter.create_text(m * 10, m * 8, text=chr(65 + i), font=("Arial", 25))

            digit = tk.Canvas(self.y_coordinates, width='12m', height='20m', bg=BG, highlightthickness=0)
            digit.pack(side=tk.TOP)
            digit.create_text(m * 8, m * 10, text=i + 1, font=("Arial", 25))

        self.update()

    def create_main_buttons(self):
        """
        Affiche les boutons principaux (retour en arrière et recommencer la partie) du GUI
        :return: les widgets de boutons pour être initialisés comme attributs
        """
        main_buttons = tk.Frame(self, width='108m', height='80m', bg=BG, highlightthickness=0)
        main_buttons.place(x='185m', y='65m')
        # crée le widget contentnant les boutons à droite du plateau

        if self.options['allowCancel']:
            go_back_button = tk.Button(main_buttons, command=lambda: self.go_back(), text="Retour en arrière",
                                       font=("Arial", 17), width=15, height=3, bg=SUBCOLOR,
                                       highlightthickness=0, borderwidth=5)
            go_back_button.place(relx=.5, rely=.3, anchor=tk.CENTER)
        else:
            go_back_button = None
        # Si l'option allowCancel est activée, crée le bouton permettant de retourner en arrière

        start_again_button = tk.Button(main_buttons, command=lambda: main_game(self, self.board.game.gamemode),
                                       text="Recommencer\nla partie", font=("Arial", 17), width=15, height=3,
                                       bg=SUBCOLOR, highlightthickness=0, borderwidth=5)
        start_again_button.place(relx=.5, rely=.7, anchor=tk.CENTER)
        # crée le bouton permettant de recommencer la partie

        self.update()  # rend les changements visibles

        return main_buttons, go_back_button, start_again_button

    def show_menu_tooltip(self, event, text):
        """
        Affiche un petit bandeau expliquant la fonction du bouton
        :param event: sert à determiner la position du widget
        :param text: texte à afficher
        :return:
        """
        if self.tooltip is None:  # s'il n'existe pas de bandeau
            x, y = event.widget.winfo_x(), event.widget.winfo_y()  # position du bouton
            self.tooltip = tk.Label(event.widget.master, text=text, font=("Arial", 8), bg='#ffffe0',
                                    highlightthickness=1,
                                    highlightbackground='black')
            self.tooltip.place(x=x, y=y)  # affichage et placement du label

    def hide_menu_tooltip(self, event):
        """
        Cache le petit bandeau
        :param event: sert à determiner la root
        :return:
        """
        root = event.widget.master.master.master
        x, y = root.winfo_pointerxy()
        widget = root.winfo_containing(x, y)  # determine le widget dans lequel on est
        if self.tooltip is not None and widget is not self.tooltip:  # si le widget dans lequel n'est pas le bandeau
            self.tooltip.destroy()  # on l'efface
            self.tooltip = None

    def create_sub_buttons(self):
        """
        Crée et affiche les boutons secondaires (options, retour au menu et quitter) du GUI
        :return:
        """
        sub_buttons = tk.Frame(self, width='30m', height='30m', bg=BG, highlightthickness=0)
        sub_buttons.place(x='255m', y='178m', anchor=tk.SW)
        # crée le widget contentnant les boutons en bas à droite du plateau

        settings_button = tk.Button(sub_buttons, command=self.settings_menu, image=self.assets['settings'],
                                    width='30m', height='15m', bg=SUBCOLOR, highlightthickness=0, borderwidth=3)
        settings_button.grid(row=0, column=0, columnspan=2, pady=2)
        homescreen_button = tk.Button(sub_buttons, command=lambda: back_to_menu(self), image=self.assets['homescreen'],
                                      width='15m', height='15m', bg=SUBCOLOR, highlightthickness=0, borderwidth=3)
        homescreen_button.grid(row=1, column=0, padx=1, pady=3)
        kill_button = tk.Button(sub_buttons, command=self.exit_window, image=self.assets['quit'],
                                width='15m', height='15m', bg=SUBCOLOR, highlightthickness=0, borderwidth=3)
        kill_button.grid(row=1, column=1, pady=3, padx=1)

        settings_button.bind("<Enter>", lambda event: self.show_menu_tooltip(event, "Paramètres"))
        settings_button.bind("<Leave>", lambda event: self.hide_menu_tooltip(event))
        homescreen_button.bind("<Enter>", lambda event: self.show_menu_tooltip(event, "Menu du jeu"))
        homescreen_button.bind("<Leave>", lambda event: self.hide_menu_tooltip(event))
        kill_button.bind("<Enter>", lambda event: self.show_menu_tooltip(event, "Quitter le jeu"))
        kill_button.bind("<Leave>", lambda event: self.hide_menu_tooltip(event))
        # on bind des event à ces boutons afin d'afficher un bandeau quand on passe dessus avec la souris

        self.update()  # rend les changements visibles


class Menu(tk.Frame):

    def __init__(self, master):
        """
        Cette classe va s'occuper d'afficher le menu et de faire fonctionner tous ses éléments.
        Crée une correspondance entre l'affichage des settings et les options. Continent les images utilisées dans le
        menu ET dans l'interface de jeu.
        :param master: root  (fenêtre de base de tkinter)
        """
        super().__init__(master)
        self.pack(fill=tk.BOTH, expand=1)

        self.assets = {
            'shrinkedlogo': ImageTk.PhotoImage(Image.open("./images/UI/othello.png")
                                               .resize((self.winfo_pixels('68.44m'), self.winfo_pixels('22m')))),
            'quit': ImageTk.PhotoImage(Image.open("./images/UI/quitter.png")
                                       .resize((self.winfo_pixels('15m'), self.winfo_pixels('15m')))),
            'homescreen': ImageTk.PhotoImage(Image.open("./images/UI/homescreen.png")
                                             .resize((self.winfo_pixels('15m'), self.winfo_pixels('15m')))),
            'settings': ImageTk.PhotoImage(Image.open("./images/UI/menu.png")
                                           .resize((self.winfo_pixels('30m'), self.winfo_pixels('15m')))),
            'checkedbox': ImageTk.PhotoImage(Image.open("./images/UI/checked.png")
                                             .resize((self.winfo_pixels('10m'), self.winfo_pixels('10m')))),
            'uncheckedbox': ImageTk.PhotoImage(Image.open("./images/UI/unchecked.png")
                                               .resize((self.winfo_pixels('10m'), self.winfo_pixels('10m')))),
            'settingsbackground': tk.PhotoImage(file='./images/backgrounds/settings.png'),
        }
        # images qui seront plus tard passés à la partie jeu

        self.exclusive_assets = {
            'logo': tk.PhotoImage(file='./images/UI/othello.png'),
            'infos': ImageTk.PhotoImage(Image.open("./images/UI/infos.png")
                                        .resize((self.winfo_pixels('15m'), self.winfo_pixels('15m')))),
            'mainbackground': tk.PhotoImage(file='./images/backgrounds/main.png'),
            'infosbackground': tk.PhotoImage(file='./images/backgrounds/infos.png'),
            'example1': ImageTk.PhotoImage(Image.open("./images/examples/1.png")
                                           .resize((self.winfo_pixels('60m'), self.winfo_pixels('40m')))),
            'example2': ImageTk.PhotoImage(Image.open("./images/examples/2.png")
                                           .resize((self.winfo_pixels('60m'), self.winfo_pixels('40m')))),
            'example3': ImageTk.PhotoImage(Image.open("./images/examples/1.png")
                                           .resize((self.winfo_pixels('60m'), self.winfo_pixels('40m'))))
        }
        # images exclusives au menu

        self.window = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.window.place(x=0, y=0, relheight=1, relwidth=1)
        # création et affichage de la fenêtre de sorte à ce qu'elle prenne tous l'écran

        self.file_protection = False  # variable de controle servant à éviter que la fenêtre soit fermée durant
        # l'écriture d'un fichier

        self.options, self.settings = self.create_settings()
        # création de dictionnaires en vue de l'affichage du menu des réglages (le premier continent les valeurs
        # stockées dans le fichier options.json, le second les valeurs affichées)

        self.tooltip = None  # initialisation du tooltip
        self.resume_button = self.main_menu()  # affichage du menu principal

    def exit_window(self):
        """
        S'assure qu'aucun fichier ne soit ouvert avant de fermer la fenêtre
        :return:
        """
        if not self.file_protection:
            self.master.destroy()

    def create_settings(self):
        """
        Charge les options à partir du fichier options.py puis créé les valeurs d'affihcages correspondantes
        :return: le dictionnaire des options et le dictionnaires des valeurs d'affichages qui seront sauvegardés comme
        attributs
        """
        self.file_protection = True
        options = load_options()  # dictionnaire d'options est chargé à partir du fichier options.json
        self.file_protection = False

        settings = {
            'showCoordinates': tk.BooleanVar(value=options['showCoordinates']),
            'showAnimations': tk.BooleanVar(value=options['showAnimations']),
            'allowCancel': tk.BooleanVar(value=options['allowCancel']),
            'cpuColorStr': tk.StringVar(value="Blanc") if options['cpuColor'] == 1 else tk.StringVar(value="Noir"),
            'background': tk.StringVar(value=options['background']),
            'deleteSave': tk.BooleanVar(value=False)
        }
        # associe une option à une valeur grâce à un objet du bon type et en convertissant du nombre au texte si
        # nécessaire

        if options['showPrevisions'] and options['showRewards']:
            settings['showHelp'] = tk.StringVar(value="Pions retournables")
        elif options['showPrevisions'] and not options['showRewards']:
            settings['showHelp'] = tk.StringVar(value="Possibilité de placer")
        else:
            settings['showHelp'] = tk.StringVar(value="Aucune")
        # combine les deux options showPrevision et showRewards en une seule valeur d'affichage

        return options, settings

    def delete_save(self):
        """
        Marque la sauvegarde comme indisponible dans le fichier save.json et supprime le bouton permettant de la charger
        :return:
        """
        delete_save()  # modifie save.json
        self.resume_button.destroy()  # supprime le bouton

    def dump_settings(self, windowtoclose):
        """
        Converti les settings affichés en les valeurs à rentrer dans le dictionnaire options puis enregistre celui-ci
        dans le fichier options.json
        :param windowtoclose: widget qu'il faut détruire une fois le processus fini
        :return:
        """
        for key, value in self.settings.items():
            if key in self.options:
                self.options[key] = value.get()
        # Si la clé d'un item existe dans les deux dictionnaires, simplement passer la valeur de settings à options

        self.options['cpuColor'] = 1 if self.settings['cpuColorStr'].get() == "Blanc" else -1
        # Converti le texte du settings en nombre (-1 si "Noir" et 1 si "Blanc") pour le charger dans l'option

        if self.settings['showHelp'].get() == "Pions retournables":
            self.options['showRewards'] = True
            self.options['showPrevisions'] = True
        elif self.settings['showHelp'].get() == "Possibilité de placer":
            self.options['showRewards'] = False
            self.options['showPrevisions'] = True
        else:
            self.options['showRewards'] = False
            self.options['showPrevisions'] = False
        # converti le settings showHelp (trois possibilités) en deux valeurs booleens de self.options

        if self.settings['deleteSave'].get():
            self.delete_save()

        self.file_protection = True
        dump_options(self.options)
        self.file_protection = False
        # enregistre les valeurs de self.options dans le fichier options.json

        windowtoclose.destroy()  # ferme la fenêtre des settings

    def settings_menu(self):
        """
        Affiche le menu des options par-dessus le menu principal
        :return:
        """

        window = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        window.place(x=0, y=0, relheight=1, relwidth=1)
        # intialise le widget principal du menu et la place sur toute la fenêtre

        window.update()
        w = window.winfo_width()
        h = window.winfo_height()
        # récupère la taille de la fenêtre en pixels pour afficher l'interface en fonction

        window.create_image(.5*w, .5*h, image=self.assets['settingsbackground'])
        # affiche le fond stocké dans les assets

        window.create_text(.5*w, .1*h, text="Règlages d'affichage", font=("Arial", 35))

        window.create_text(10, .2*h, text="Afficher les coordonées:", font=("Arial", 20), anchor=tk.W)
        window.create_text(10, .3*h, text="Afficher les informations:", font=("Arial", 20), anchor=tk.W)
        window.create_text(10, .4*h, text="Jouer les animations:", font=("Arial", 20), anchor=tk.W)
        window.create_text(10, .5*h, text="Couleur du plateau:", font=("Arial", 20), anchor=tk.W)
        # affiche les intitulés des règlages d'affichage

        background_pevisualisation = tk.Frame(window, width='20m', height='12m', bg=self.settings['background'].get(),
                                              highlightthickness=3, highlightbackground='black')
        background_pevisualisation.place(relx=.725, rely=.5, anchor=tk.W)

        # affiche la previsualisation de la couleur du plateau

        def set_color():
            value = askcolor(self.settings['background'].get())[1]
            color = value if value is not None else self.settings['background'].get()
            self.settings['background'].set(color)
            background_pevisualisation.config(bg=color)
        # change si la couleur du fond si l'utilisateur a entré une couleur sinon garde la même et modifie la preview

        tk.Checkbutton(window, variable=self.settings['showCoordinates'], onvalue=True, offvalue=False,
                       image=self.assets['uncheckedbox'], selectimage=self.assets['checkedbox'],
                       indicatoron=False, width='10m', height='10m').place(relx=.8, rely=.2, anchor=tk.W)
        tk.OptionMenu(window, self.settings['showHelp'], "Aucune", "Possibilité de placer", "Pions retournables") \
            .place(relx=.8, rely=.3, anchor=tk.W)
        tk.Checkbutton(window, variable=self.settings['showAnimations'], onvalue=True, offvalue=False,
                       image=self.assets['uncheckedbox'], selectimage=self.assets['checkedbox'],
                       indicatoron=False, width='10m', height='10m').place(relx=.8, rely=.4, anchor=tk.W)
        tk.Button(window, command=set_color, text="Choisir", font=("Arial", 20), height=1, width=9, bg=THIRDCOLOR) \
            .place(relx=.8, rely=.5, anchor=tk.W)
        # crée les widgets permettant de regler les options d'affichage

        window.create_text(.5*w, .6*h, text="Règlages du jeu", font=("Arial", 35), anchor=tk.CENTER)

        window.create_text(10, .7*h, text="Autorisier le retour en arrière:", font=("Arial", 20), anchor=tk.W)
        window.create_text(10, .8*h, text="Couleur du CPU:", font=("Arial", 20), anchor=tk.W)
        # affiche les intitulés des règlages du jeu.

        tk.Checkbutton(window, variable=self.settings['allowCancel'], onvalue=True, offvalue=False,
                       image=self.assets['uncheckedbox'], selectimage=self.assets['checkedbox'],
                       indicatoron=False, width='10m', height='10m').place(relx=.8, rely=.7, anchor=tk.W)
        tk.OptionMenu(window, self.settings['cpuColorStr'], "Blanc", "Noir").place(relx=.8, rely=.8, anchor=tk.W)
        # crée les widgets permettant de règler les options du jeu

        if check_save_aviability():  # si une sauvegarde est disponible
            window.create_text(10, .9*h, text="Effacer la sauvegarde:", font=("Arial", 20), anchor=tk.W)
            tk.Checkbutton(window, variable=self.settings['deleteSave'], onvalue=True, offvalue=False,
                           image=self.assets['uncheckedbox'], selectimage=self.assets['checkedbox'],
                           indicatoron=False, width='10m', height='10m').place(relx=.4, rely=.9, anchor=tk.W)
        # crée les widgets pour effacer la sauvegarde

        tk.Button(window, command=window.destroy, text="Annuler", font=("Arial", 20), width=9, height=1, bg=THIRDCOLOR,
                  highlightthickness=0, borderwidth=3).place(relx=.65, rely=.9, anchor=tk.E)
        tk.Button(window, command=lambda: self.dump_settings(window), text="Enregistrer", font=("Arial", 20), width=13,
                  height=1, bg=THIRDCOLOR, highlightthickness=0, borderwidth=3).place(relx=.9, rely=.9, anchor=tk.E)

        # crée les boutons de sauvegarde et de retour en arrière

    def infos_menu(self):
        """
        Affiche le menu des règles et crédits par-dessur le menu principal
        :return:
            """
        window = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        window.place(x=0, y=0, relheight=1, relwidth=1)
        # intialise le widget principal du menu et la place sur toute la fenêtre

        window.update()
        w = window.winfo_width()
        h = window.winfo_height()
        # récupère la taille de la fenêtre en pixels pour afficher l'interface en fonction

        window.create_image(.5 * w, .5 * h, image=self.exclusive_assets['infosbackground'])  # affiche le fond stocké
        # dans les assets exclusifs

        window.create_text(.5*w, .1*h, text="Règles", font=("Arial", 30), fill="white")
        window.create_text(.5*w, .25*h, text="Dans ce jeu, les joueurs placent à tour de rôle un pion sur le plateau "
                                             "de 8x8 cases.\nSi ils encadrent grâce à cela un ou plusieurs pions de la "
                                             "couleur adverse,\nceux-ci sont retournés et changent donc de couleur.\n"
                                             "(Les pions retournés ne déclenchent pas le retournement d'autres pions).",
                           font=("Arial", 20), fill="white")
        window.create_image(.15 * w, .5 * h, image=self.exclusive_assets['example1'])
        window.create_image(.5 * w, .5 * h, image=self.exclusive_assets['example2'])
        window.create_image(.85 * w, .5 * h, image=self.exclusive_assets['example3'])
        window.create_text(.5 * w, .8*h, text="Un joueur ne peut placer un pion qu'aux endroit ou cela permettrait de\n"
                                              "retourner au moins un pion. S'il ne peut pas jouer, il doit passer son "
                                              "tour.\n\nLe jeu se termine lorsque le plateau est entièrement recouvers "
                                              "ou lorsqu'aucun joueur\nne peut jouer. C'est alors le joueur qui a le ",
                           font=("Arial", 20), fill="white")
        # affiche les textes et images servant à l'explication des règles

        tk.Button(window, command=window.destroy, image=self.assets['homescreen'], bg=THIRDCOLOR, highlightthickness=0,
                  borderwidth=3, width='15m', height='15m').place(relx=.9, rely=.9)
        # crée le bouton de retour en arrière

    def show_menu_tooltip(self, event, text):
        """
        Affiche un petit bandeau expliquant la fonction du bouton
        :param event: sert à determiner la position du widget
        :param text: texte à afficher
        :return:
        """
        if self.tooltip is None:  # s'il n'existe pas de bandeau
            x, y = event.widget.winfo_x(), event.widget.winfo_y()  # position du bouton
            self.tooltip = tk.Label(event.widget.master, text=text, font=("Arial", 8), bg='#ffffe0',
                                    highlightthickness=1, highlightbackground='black')
            self.tooltip.place(x=x, y=y)  # affichage et placement du label

    def hide_menu_tooltip(self, event):
        """
        Cache le petit bandeau
        :param event: sert à determiner la root
        :return:
        """
        root = event.widget.master.master.master
        x, y = root.winfo_pointerxy()
        widget = root.winfo_containing(x, y)  # determine le widget dans lequel on est
        if self.tooltip is not None and widget is not self.tooltip:  # si le widget dans lequel n'est pas le bandeau
            self.tooltip.destroy()  # on l'efface
            self.tooltip = None

    def main_menu(self):
        """
        affiche les éléments de la page principale du menu
        :return: le bouton de chargment de la sauvegarde pour qu'il soit sauvegardé comme attribut et ainsi supprimable
        facilement (si la sauvegarde n'est pas accessible)
        """
        window = self.window  # déclaration d'une variable pour raccourcir les commandes suivantes

        window.create_image(640, 440, image=self.exclusive_assets['mainbackground'])
        window.create_image(150, 90, image=self.exclusive_assets['logo'])
        # affiche le fond et le logo du jeu

        play_vs_computer = tk.Button(window, command=lambda: main_game(self, 0), text="Jouer contre\nl'ordinateur",
                                     font=("Arial", 25), width=11, height=2, bg=THIRDCOLOR, highlightthickness=0,
                                     borderwidth=5)
        play_vs_computer.place(relx=.85, rely=.4, anchor=tk.CENTER)
        play_vs_human = tk.Button(window, command=lambda: main_game(self, 1), text="Jouer contre\nun humain",
                                  font=("Arial", 25), width=11, height=2, bg=THIRDCOLOR, highlightthickness=0,
                                  borderwidth=5)
        play_vs_human.place(relx=.85, rely=.6, anchor=tk.CENTER)
        # crée les boutons permettant de jouer contre l'humain et contre l'ordinateur

        if check_save_aviability():
            resume_button = tk.Button(window, command=lambda: main_game(self, 2), text="Reprendre\nla partie",
                                      font=("Arial", 25), width=11, height=2, bg=THIRDCOLOR, highlightthickness=0,
                                      borderwidth=5)
            resume_button.place(relx=.85, rely=.2, anchor=tk.CENTER)
        else:
            resume_button = None
        # si une sauvegarde est disponible, créee le bouton pour de la charger

        sub_buttons = tk.Frame(window, width='62m', height='24m', highlightthickness=0)
        sub_buttons.place(relx=.85, rely=.8, anchor=tk.CENTER)
        info = tk.Button(sub_buttons, command=self.infos_menu, image=self.exclusive_assets['infos'], width='15m',
                         height='15m', bg=THIRDCOLOR, highlightthickness=0, borderwidth=3)
        info.pack(side=tk.LEFT)
        settings = tk.Button(sub_buttons, command=self.settings_menu, image=self.assets['settings'],
                             width='30m', height='15m', bg=THIRDCOLOR, highlightthickness=0, borderwidth=3)
        settings.pack(side=tk.LEFT)
        kill = tk.Button(sub_buttons, command=self.exit_window, image=self.assets['quit'], width='15m', height='15m',
                         bg=THIRDCOLOR, highlightthickness=0, borderwidth=3)
        kill.pack(side=tk.LEFT)
        # crée les boutons secondaires affichant le menu des règlages et des règles et cérdits et celui quittant le jeu

        info.bind("<Enter>", lambda event: self.show_menu_tooltip(event, "Règles du jeu"))
        info.bind("<Leave>", lambda event: self.hide_menu_tooltip(event))
        settings.bind("<Enter>", lambda event: self.show_menu_tooltip(event, "Paramètres"))
        settings.bind("<Leave>", lambda event: self.hide_menu_tooltip(event))
        kill.bind("<Enter>", lambda event: self.show_menu_tooltip(event, "Quitter le jeu"))
        kill.bind("<Leave>", lambda event: self.hide_menu_tooltip(event))
        # on bind des event à ces boutons afin d'afficher un bandeau quand on passe dessus avec la souris

        return resume_button


def main_game(widget, gamemode):
    """
    Commence le jeu en détruisant l'interface actuelle et en créant une nouvelle interface de jeu
    :param widget: widget depuis lequel est appelé la fonction, sert à determiner la fenetre principale de tkinter et à
    détruire l'interface actuelle
    :param gamemode: indication sur le mode de jeu (2 = chargement de la sauvegarde, 1 = joueur contre joueur,
    0 = contre l'ordinateur)
    :return:
    """

    root = widget.master  # récupère la fenêtre principale
    assets = widget.assets  # récupère les images à afficher dans l'interface de jeu
    widget.destroy()  # détruit l'interface actuelle
    gui = Gui(root, gamemode, assets)  # création de l'interface de jeu
    root.protocol("WM_DELETE_WINDOW", lambda: gui.exit_window())  # assignation de la croix pour quitter à une fonction
    # spéciale (pour éviter la corruption des fichiers)
    gui.mainloop()  # lancement du jeu


def back_to_menu(widget):
    """
    retourne au menu après avoir détruit l'interface principale
    :param widget: fenêtre actuelle
    :return:
    """
    root = widget.master  # récupère la fenêtre principale
    widget.destroy()  # détruit l'interface actuelle
    menu = Menu(root)  # création de l'interface du menu
    menu.mainloop()  # lancement du menu
