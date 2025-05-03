from computer import *
from save import *

from multiprocessing import Process, Queue
import pickle


class Table:

    def __init__(self):
        """
        Classe contenant un tableau des valeurs du plateau et différentes méthodes pour agir dessus. Continent aussi les
        le joueur à qui ça devrait être le tour et les coups postentiels (cases libres) du plateau.
        """

        self.__grid = []
        for i in range(0, 8):
            tmp_list_board = []
            for j in range(0, 8):
                tmp_list_board.append(0)
            self.__grid.append(tmp_list_board)
        # initialise la vide pour que le plateau soit vide
            
        self.turn = -1  # ce sont les noirs qui commencent
        
        self.__potential_moves = []
        for i in range(0, 8):
            for j in range(0, 8):
                self.__potential_moves.append([i, j])
        # puisque toutes les cases sont vides, toutes les cases sont dans les coups potentiels

        self.set_tile(3, 3, WHITE)
        self.set_tile(3, 4, BLACK)
        self.set_tile(4, 3, BLACK)
        self.set_tile(4, 4, WHITE)
        # initialisation des valeurs de base du tableau

    def get_grid(self):
        return self.__grid  # renvoie la grille des valeurs complète

    def get_tile(self, x, y):
        """
        :param x: abscisse de la case
        :param y: ordonnée de la case
        :return: valeur d'une case de la grille
        """
        return self.__grid[x][y]

    def set_tile(self, x, y, value):
        """
        Change la valeur d'une case dans le tableau des valeurs et modifie la liste des cases vides en conséquence
        :param x:
        :param y:
        :param value:
        :return:
        """
        if x in range(8) and y in range(8) and value in range(-1, 2):
            if self.__grid[x][y] != value:
                self.__grid[x][y] = value

                if value:
                    self.__potential_moves.pop(self.__potential_moves.index([x, y]))
                else:
                    self.__potential_moves.append([x, y])

    def switch_turn(self):
        self.turn = -self.turn  # indique que c'est à l'autre joueur de jouer sur ce plateau

    def switch_color(self, to_switch):
        """
        Change la couleur de toutes les cases dont la coordonées est listée dans to_switch
        :param to_switch: liste des cases à modifier la couleur
        :return:
        """
        for element in to_switch:
            self.__grid[element[0]][element[1]] = -self.__grid[element[0]][element[1]]

    def process(self, x, y, color=None):
        """
        détermine l'effet d'un coup aux coorodnées (x,y)
        :param x: abcisse de la case où le coup est joué
        :param y: ordonée de la case où le coup est joué
        :param color: couleur du coup joué, par défaut la valeur du tour du tableau
        :return: liste des coordonées des cases à modifier
        """
        our_color = color if color is not None else self.turn
        opponent_color = -our_color

        to_switch = []  # liste des pions à modifier
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                # on répète l'opération pour toutes les directions à partir de case initiale (ligne, colonne et
                # diagonales), si (0, 0) alors on n'avancerait pas, donc on l'exclut
                pos_x = x + i
                pos_y = y + j
                coins_in_direction = []  # liste des pions à modifier dans une direction
                while pos_x in range(0, 8) and pos_y in range(0, 8):
                    if self.__grid[pos_x][pos_y] == opponent_color:
                        coins_in_direction.append([pos_x, pos_y])
                    else:
                        break
                    pos_x = pos_x + i
                    pos_y = pos_y + j
                # tant qu'on est dans la grille et qu'on rencontre des pions adverses,on liste ces pions et on passe à
                # la case suivante dans la direction
                if pos_x in range(0, 8) and pos_y in range(0, 8):
                    if not len(coins_in_direction) == 0 and self.__grid[pos_x][pos_y] == our_color:
                        for element in coins_in_direction:
                            to_switch.append(element)
                # si le dernier pions est de notre couleur, on compte tous les pions de la couleur inverse listés comme
                # à modifier

        return to_switch

    def play(self, x, y):
        """
        déclenche les effets dans le tableau d'un coup aux coordonées (x,y) par le joueur à qui c'est le tour dans le
        tableau
        :param x: abcisse de la case où le coup est joué
        :param y: ordonée de la case où le coup est joué
        :return:
        """
        self.set_tile(x, y, self.turn)  # place la pièce aux coordonées
        coins_list = self.process(x, y)  # détermine les pièces qui vont être retournées
        self.switch_color(coins_list)  # retourne les pièces

    def move_possibility(self, x, y, color=None):
        return len(self.process(x, y, color))  # détermine si un coup est possible en déterminant si
        # il retournerait des pions

    def aviable_moves(self, whos_turn=None):
        """
        détermine les coups jouables dans cet état du tableau
        :param whos_turn: pour que joueur les coups possibles vont être calculés, par défaut le joueur dont c'est le
        tour dans le tableau
        :return: liste des cooordonées des coups jouables
        """
        turn = whos_turn if whos_turn is not None else self.turn

        return [move for move in self.__potential_moves if self.move_possibility(move[0], move[1], turn)]
        # verifie si la fonction process évaluée avec chaque case libre donne un résultat (signifie que le coup est
        # valide). Si oui, ajoute le coup à la liste puis renvoie cette dernière

    def play_possibility(self, whos_turn=None):
        """
        Teste si le joueur whosturn peut jouer dans cette situation du tableau, puis teste si l'autre joueur peut jouer.
        Si whosturn est vide, alors teste pour le joueur à qui c'est le tour dans le tableau
        :param whos_turn: joueur à tester la possibilité de jouer
        :return: 0 si le joueur spécifié peut jouer, 1 si il ne peut pas mais l'autre oui, 2 si aucun ne peut jouer
        """
        turn = whos_turn if whos_turn is not None else self.turn
        if len(self.aviable_moves(turn)) == 0:
            if len(self.aviable_moves(-turn)) == 0:
                return 2
            else:
                return 1
        else:
            return 0


class Othello:

    def __init__(self, gamemode, cpu_color):
        """
        Classe à instance unique gérant toutes les fonctions ayant lieu au jeu se déroulant devant le joueur, p. ex
        les scores, le joueur qui doit jouer, le nombre de tour écoulé, la fin de partie.
        :param gamemode: 0 = joueur contre ordi, 1 = joueur contre joueur, 2 = chargement d'une sauvegarde
        :param cpu_color: couleur que va jouer l'ordinateur
        """

        self.file_protection = False  # empeche le joueur de quitter si cette valeur est True, evite de corrompre les
        # fichiers

        if gamemode == 2:  # si on souhaite charger la sauvegarde
            self.file_protection = True
            with open("savefiles/states.pickle", "rb") as statesfile:
                data = pickle.load(statesfile)
                states = data
            with open("savefiles/save.json", "r") as savefile:
                data = savefile.read()
                values = loads(data)
            self.file_protection = False
            # récupération des données de sauvegarde

            self.table = deepcopy(states[len(states) - 1])
            self.gamemode = values["gamemode"]
            self.turn_count = values["turnsPassed"]
            self.cpu_color = values['cpuColor']
            # initialisation des valeurs selon les données optenues
            self.__states = states
        else:
            self.table = Table()
            self.gamemode = gamemode  # 0 = pve, 1 = pvp
            self.turn_count = 1
            self.cpu_color = cpu_color
            first_state = deepcopy(self.table)
            self.__states = [first_state]
            # enregistre le premier state dans la liste mais ne crée pas encore de sauvegarde

        self.__whosturn = self.table.turn  # C'est aux noirs de commencer
        self.in_process = False  # détermine si une action est en cours
        self.gameover = False
        self.winner = None

    def get_whosturn(self):  # renvoie la valeur de la couleur qui doit jouer
        return self.__whosturn

    def switch_whosturn(self):  # change de couleur qui doit jouer
        self.__whosturn = -self.__whosturn
        self.table.switch_turn()

    def get_scores(self):
        """
        calcule le score actuel de chaque joueur et le nombre de tours écoulés
        :return: score des noirs, score des blancs, nombre de tours écoulés
        """
        grid = self.table.get_grid()
        score_black = []
        score_white = []
        for ligne in grid:
            for element in ligne:
                score_black.append(- int(element - .1))  # ajoute 1 si l'élément est -1 et 0 s'il est 0 ou 1
                score_white.append(int(element + .1))  # ajoute 1 si l'élément est 1 et 0 s'il est 0 ou -1

        return sum(score_black), sum(score_white), self.turn_count

    def save_states_file(self):
        """
        Sauvegarde la liste d'état du jeu dans le fichier states.pickle et les variables du jeu dans le fichier
        save.json
        :return:
        """
        self.file_protection = True
        with open("savefiles/states.pickle", "wb") as states_file:
            pickle.dump(self.__states, states_file)
        # sauvegarde la liste des états
        with open("savefiles/save.json", "w") as save_file:
            values = {
                'saveAviable': True,
                'turnsPassed': self.turn_count,
                'gamemode': self.gamemode,
                'cpuColor': self.cpu_color
            }
            data = dumps(values, indent=1)
            save_file.write(data)
            # crée un dictionaire json des valeurs et le sauvegarde
        self.file_protection = False

    def save_state(self):
        """
        sauvegarde l'état actuel du tableau dans la liste des états et sauvegarde la liste dans une fichier
        :return:
        """
        state = deepcopy(self.table)
        self.__states.append(state)
        self.save_states_file()

    def load_state(self):
        """
        récupère le dernier état pertinent de la liste et modifie le plateau selon ses valeurs
        :return: 0 si la maneouvre à aboutit, 1 si elle n'a pas aboutit
        """
        if not self.in_process:
            turns_to_skip = 1 if self.gamemode == 1 else 2  # on doit aller 2 tours en arrière si on joue contre l'ordi
            # mais seulement un tour si on joue contre un joueur
            if len(self.__states) >= turns_to_skip + 1:  # on controle si il assez de tours sont passés pour revenir en
                # arrière (on ne peut pas retourner avant le premier tour du jeu)
                self.table = deepcopy(self.__states[len(self.__states) - turns_to_skip - 1])  # récupère l'état
                for i in range(turns_to_skip):
                    self.__states.pop()
                # supprime les tours après celui qu'on vient de charger de la liste

                self.__whosturn = self.table.turn  # adapte le tour du jeu au tour de l'état
                if self.gamemode == 0 or self.__whosturn == WHITE:
                    self.turn_count -= 1  # si on a enlevé deux tours (pve) ou que dans l'état actuel c'est aux blancs
                    # de jouer (pvp), on retire un au décompte des tours
                self.save_states_file()  # on sauvegarde la nouvelle liste des états dans le fichier

    def end_game(self):
        """
        fonction se déclenchant lorsque le jeu est fini
        :return:
        """

        self.gameover = True

        score = simple_evaluation(self.table)  # récupère les scores

        self.winner = WHITE if score > 0 else BLACK if score < 0 else EMPTY  # indique le gagnant

        self.file_protection = True
        with open("savefiles/save.json", "w") as savefile:
            values = {
                "saveAviable": False,
                "turnsPassed": None,
                "gamemode": None,
                "cpuColor": None
            }
            data = dumps(values)
            savefile.write(data)
        self.file_protection = False
        # rend la sauvegarde inaccessible


def action(board, move, to_switch=None):
    """
    Fonction centralisant toutes les actions se passant une fois qu'un case est selectionnées pour être jouée
    :param board:
    :param move: coordonées ou le coup est joué
    :param to_switch: si la liste des pions à tourner à déjà été calculée, on peut la passer, sinon elle est calculée à
    partir des valeurs du tableau
    :return:
    """
    x, y = move
    game = board.game

    to_switch = game.table.process(x, y) if to_switch is None else to_switch

    game.table.play(x, y)  # modifie le tableau
    animation_color = game.get_whosturn()

    play_possiblity = game.table.play_possibility(-board.game.table.turn)

    if play_possiblity == 2:  # si aucun des deux joueurs peu jouer, le jeu s'arrête
        game.end_game()
        board.update_animation(x, y, to_switch, animation_color)  # joue la dernière animation
        board.master.end_game_animation()  # affiche le bandeau de fin de partie
        return
    elif play_possiblity == 1:
        pass  # on ne change pas de tour si l'autre ne peut pas jouer
    elif play_possiblity == 0:
        game.switch_whosturn()  # si le joueur suivant peut jouer, on change la valeur d' à qui c'est le tour,
        # c'est donc à lui de jouer
        if game.get_whosturn() == BLACK:
            game.turn_count += 1
        # si c'est maintenant le tour du joueur noir, augmenter de 1 le décompte des tours

    game.save_state()  # sauvegarde l'état du jeu

    if game.gamemode == 0 and game.get_whosturn() == board.game.cpu_color and not game.gameover:
        # si on est en mode "contre l'ordinateur" et que c'est le tour de l'ordinateur, faire jouer l'ordinateur
        movetoplay = Queue()
        computer = Process(target=move_ordinateur, args=[game.table, board.game.cpu_color, movetoplay])
        computer.start()
        # initialisation d'un processus multithread pour calculer coup de l'ordi en même temps que l'animation se joue
        board.update_animation(x, y, to_switch, animation_color)  # fait se jouer l'animation
        board.master.update_scores()  # update les scores
        computer.join()  # attends le réultat du calcul pour le coup de l'ordinateur
        action(board, movetoplay.get())  # effectue le coup (pas besoin de
        # controller la validité car le coup optimal est forcément valide)
    else:
        board.update_animation(x, y, to_switch, animation_color)  # fait se jouer l'animation
        board.master.update_scores()  # update l'action
