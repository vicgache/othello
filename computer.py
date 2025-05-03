from copy import deepcopy  # pour effectuer des copies par valeur et non par référence
from constants import *
from math import copysign


def get_parity_value(grid):
    """
    calcule le nombre de pions que chaque joueur possède sur le tableau actuel
    :param grid: tableau actuel
    :return: pourcentage de domination en terme de pions (positif ou negatif selon le joueur qui domine)
    """
    sum_max = 0
    sum_min = 0
    for ligne in grid:
        for element in ligne:
            if element == MAX:
                sum_max += 1
            elif element == MIN:
                sum_min += 1
    return ((sum_max - sum_min) / (sum_max + sum_min)) * 100


def get_mobility_value(aviable_moves_max, aviable_moves_min):
    """
    calcule la valeur de mobilité à partir des coups disponibles de chaque joueur
    :param aviable_moves_max: coups disopnibles du joueur max
    :param aviable_moves_min: coups disponibles du joueur min
    :return: pourcentage de domination de la mobilité (positif ou negatif selon le joueur qui domine)
    """
    mobility_max = len(aviable_moves_max)
    mobility_min = len(aviable_moves_min)
    return ((mobility_max - mobility_min) / (mobility_max + mobility_min)) * 100 \
        if mobility_min + mobility_max != 0 else 0


def get_corners_value(grid, aviable_moves_max, aviable_moves_min):
    """
    calcule les coins effectifs et potentiels que possède chaque joueur et en déduit une valeur de domination des coins.
    Chaque coins effectif vaut quatre points et chaque coins potentiel un point. Les coins potentiels sont défins comme
    des coins pouvant être retournés au prochain tour par le joueur.
    :param grid: tableau actuel
    :param aviable_moves_max: coups disopnibles du joueur max
    :param aviable_moves_min: coups disponibles du joueur min
    :return: pourcentage de domination des coins (positif ou negatif selon le joueur qui domine)
    """
    corners_coordinates = [[0, 0], [0, 7], [7, 0], [7, 7]]
    potential_corners_max = [element for element in aviable_moves_max if element in corners_coordinates]
    potential_corners_min = [element for element in aviable_moves_min if element in corners_coordinates]
    corners_max = (int(grid[0][0] + .1) + int(grid[7][0] + .1) + int(grid[0][7] + .1) + int(grid[7][7] + .1)) * 4 \
        + len(potential_corners_max)
    corners_min = (int(grid[0][0] - .1) + int(grid[0][0] - .1) + int(grid[0][0] - .1) + int(grid[0][0] - .1)) * -4\
        + len(potential_corners_min)
    return ((corners_max - corners_min) / (corners_max + corners_min)) * 100 \
        if corners_max + corners_min != 0 else 0


def get_stability_value(table, aviable_moves_max, aviable_moves_min):
    """
    Calcule les cases stables de chaque joueur et en déduit une valeur de domination de stabilité. Une case est
    considérée totalement stable s'il n'est pas possible de la retourner (ce genre de case se construisent à partir de
    coins), potentiellement stable s'il n'est pas possible de la retourner au prochain tour et instable s'il est
    possible de la retourner au prochain tour. Seules les cases totalement stables et instables sont importantes dans ce
    calcul.
    :param table: tableau actuel avec ses méthodes
    :param aviable_moves_max: coups disopnibles du joueur max
    :param aviable_moves_min: coups disponibles du joueur min
    :return: pourcentage de domination de stabilité (positif ou negatif selon le joueur qui domine)
    """
    grid = table.get_grid()
    corners_coordinates = [[0, 0], [0, 7], [7, 0], [7, 7]]

    stability_grid_template = []
    for i in range(0, 10):
        tmp_line = []
        for j in range(0, 10):
            if i in [1, 9] or j in [1, 9]:
                tmp_line.append(1)
            else:
                tmp_line.append(0)
        stability_grid_template.append(tmp_line)
    # création d'une "grille de stabilité" 10x10 avec les bords faits de 0 et l'intérieur fait de 1. 1 signifie que le
    # pion est retournable et 0 signifie qu'ils ne sont pas retournables. Ici les cases 1 représentent le plateau de jeu
    # et les cases 0 sont bord immédiat

    has_corner_max = False
    stability_grid_max = deepcopy(stability_grid_template)  # crée une grille de stabilité pour max à partir du modèle
    for element in corners_coordinates:
        if grid[element[0]][element[1]] == MAX:
            has_corner_max = True
            stability_grid_max[element[0] + 1][element[1] + 1] = 1
    # controlle si max a capturé un coint et si oui modifie sa grille en conséquence
    # (les coins ne sont pas retournables)

    if has_corner_max:  # si max a des coints, sinon cela ne sert à rien de jouer la boucle car aucune de ses cases ne
        # sera totalement stable
        while True:
            change_made = False

            for i in range(0, 8):
                for j in range(0, 8):
                    x, y = (i + 1, j + 1)
                    if grid[i][j] == MAX and stability_grid_max[x][y] == 0:
                        if (stability_grid_max[x - 1][y - 1] or stability_grid_max[x + 1][y + 1]) \
                                and (stability_grid_max[x][y - 1] or stability_grid_max[x][y + 1]) \
                                and (stability_grid_max[x - 1][y] or stability_grid_max[x + 1][y]) \
                                and (stability_grid_max[x + 1][y - 1] or stability_grid_max[x - 1][y + 1]):
                            stability_grid_max[x][y] = 1
                            change_made = True
            if not change_made:
                break
        # pour chaque case instable que max possède, on controle si elle est bordée d'au moins un pion stable de même
        # couleur ou d'un bord sur au moins 1 coté de chaque diagonale pouvant le traverser. Si oui elle est considérée
        # comme stable. On répète le processus jusqu'à ce que plus aucun changement ne soit effectué. Cela veut dire que
        # toutes les cases stables ont été trouvées.

    unstable_max = []
    for element in aviable_moves_min:
        for new_item in table.process(element[0], element[1], MIN):
            if new_item not in unstable_max:
                unstable_max.append(new_item)
    # calcule toutes les cases instables différentes de max à partir des cases que pourraient retourner les coups
    # disponibles de min

    stabilty_max = len(stability_grid_max) - len(unstable_max)
    # la valeur de stabilité de max = les cases totalement stables de max - les cases instables de max

    has_corner_min = False
    stability_grid_min = deepcopy(stability_grid_template)
    for element in corners_coordinates:
        if grid[element[0]][element[1]] == MIN:
            has_corner_min = True
            stability_grid_min[element[0] + 1][element[1] + 1] = 1
    # controlle si min a capturé un coint et si oui modifie sa grille en conséquence
    # (les coins ne sont pas retournables)

    if has_corner_min:  # si min a des coints, sinon cela ne sert à rien de jouer la boucle car aucune de ses cases ne
        # sera totalement stable
        while True:
            change_made = False

            for i in range(0, 8):
                for j in range(0, 8):
                    x, y = (i + 1, j + 1)
                    if grid[i][j] == MIN and stability_grid_min[x][y] == 0:
                        if (stability_grid_min[x - 1][y - 1] or stability_grid_min[x + 1][y + 1]) \
                                and (stability_grid_min[x][y - 1] or stability_grid_min[x][y + 1]) \
                                and (stability_grid_min[x - 1][y] or stability_grid_min[x + 1][y]) \
                                and (stability_grid_min[x + 1][y - 1] or stability_grid_min[x - 1][y + 1]):
                            stability_grid_min[x][y] = 1
                            change_made = True
            if not change_made:
                break
        # pour chaque case instable que min possède, on controle si elle est bordée d'au moins un pion stable de même
        # couleur ou d'un bord sur au moins 1 coté de chaque diagonale pouvant le traverser. Si oui elle est considérée
        # comme stable. On répète le processus jusqu'à ce que plus aucun changement ne soit effectué. Cela veut dire que
        # toutes les cases stables ont été trouvées.

    unstable_min = []
    for element in aviable_moves_max:
        for new_item in table.process(element[0], element[1], MAX):
            if new_item not in unstable_min:
                unstable_min.append(new_item)
    # calcule toutes les cases instables différentes de min à partir des cases que pourraient retourner les coups
    # disponibles de max

    stabilty_min = len(stability_grid_min) - len(unstable_min)
    # la valeur de stabilité de max = les cases totalement stables de max - les cases instables de max

    return ((stabilty_max - stabilty_max) / (stabilty_max + stabilty_min)) * 100 \
        if stabilty_max + stabilty_min != 0 else 0


def heuristic_evaluation(table):

    """
    Fonction visant à calculer la valeur d'un état précis du jeu, selon le modèle proposé par Sannidhanam et Annamalai.
    Les coefficients associés à chaque valeur proviennent aussi de Sannidhanam et Annamalai
    :param table: tableau en l'état actuel
    :return: Valeur de l'état
    """
    aviable_moves_max = table.aviable_moves(MAX)
    aviable_moves_min = table.aviable_moves(MIN)

    grid = table.get_grid()

    parity_value = get_parity_value(grid)

    mobility_value = get_mobility_value(aviable_moves_max, aviable_moves_min)

    corners_value = get_corners_value(grid, aviable_moves_max, aviable_moves_min)

    stability_value = get_stability_value(table, aviable_moves_max, aviable_moves_min)

    return stability_value * 25 + parity_value * 25 + corners_value * 30 + mobility_value * 5


def simple_evaluation(table):
    """
    Compte le nombre de pions que chaque joueur à sur le plateau et calcule la différence (avec le signe du joueur qui
    en a le plus
    :param table: le tableau en l'état actuel
    :return: différence de pions sur le plateau avec le signe du joueur qui en a le plus
    """
    grid = table.get_grid()  # récupère la grille des pions
    value = 0
    for line in grid:
        for element in line:
            value = value + element
    return value


def minimax(table, turns, alpha=-10000, beta=10000):
    """
    Cette commande sert à déterminer le meilleur score qui va advernir si les deux jouers jouent de manière optimale à
    partir d'un tableau donné.
    :param table: le tableau tel que modifié par une série d'action possible
    :param turns: tours restant avant d'atteindre la limite
    :param alpha: meilleur score possible actuel du joueur MAX
    :param beta: meilleur score possible actuel du joueur MIN
    :return: score meilleur score possible pour le joueur is_maximizing avec ce tableau
    """
    if turns <= 0:  # si on a atteint le dernier tour
        return heuristic_evaluation(table)  # renvoie la valeur de du tableau selon le mode
        # d'évaluation choisi

    else:

        move_possiblity = table.play_possibility()

        if move_possiblity == 2:  # si aucun des deux joueurs peut jouer, c'est à dire si la partie est fini
            winner = simple_evaluation(table)
            return 0 if winner == 0 else copysign(10000, winner)
            # on calcule la valeur finale du plateau selon une évaluation simple (qui a le plus de pions) et on lui
            # donne beaucoup de points pour qu'elle surpasse tous les états où la partie n'est pas finie
        elif move_possiblity == 1:  # si le joueur actuel ne peut pas jouer
            copy_table = deepcopy(table)
            table.switch_turn()
            return minimax(copy_table, turns - 1)
            # rien ne se passe et on passe au joueur suivant
        score = -10000 if table.turn == MAX else 10000  # défini le score de base a une valeur plus petite que
        # le minimum possbile pour max et plus grande que la valeur maximale pour min

        for element in table.aviable_moves():  # pour chaque coup possible à ce stade du jeu

            copy_table = deepcopy(table)
            copy_table.play(element[0], element[1])
            copy_table.switch_turn()
            # copie le tableau et lui applique le coup

            score = max(score, minimax(copy_table, turns - 1, alpha, beta)) if table.turn == MAX \
                else min(score, minimax(copy_table, turns - 1, alpha, beta))

            # reappelles la commande minimax qui va renvoyer évaluer le score si les deux joueurs jouent de manière
            # optimale à partir de ce coup jusqu'à la limite prévue  puis le compare au meilleur score actuel pour
            # déterminer s'il doit être le nouveau meilleur score

            if table.turn == MAX:
                if beta <= score:
                    break
                alpha = max(alpha, score)
            else:
                if alpha >= score:
                    break
                beta = min(beta, score)
            # si cette branche donne au joueur adverse un coup moins bon pour le joueur en train de minimax que son
            # meileur coup, alors elle est abandonée puisqu'on suppose que le joueur adverse va forcément prendre cette
            # option (puisqu'on suppose qu'il joue de manière optimale) (alpha-beta pruning)

        return score


def best_move(table, player):
    """
    établi une liste des coups possibles et de leur résultat selon l'algorithme minimax puis choisi celui donnant le
    meilleur score pour l'ordinateur.
    :param table: le tableau en l'état actuel
    :param player: le joueur cherachant son meilleur coup
    :return: coordonées de la case du meilleur coup
    """

    scores = []  # initialisation de la liste des coups
    aviable_moves = table.aviable_moves()
    for element in aviable_moves:  # Pour chaque coup possible
        board_copy = deepcopy(table)
        board_copy.play(element[0], element[1])
        board_copy.switch_turn()
        # crée une copie du tableau et lui applique le coup pour ensuite évaluer celui-ci avec minimax

        scores.append(minimax(board_copy, 3))
        # évalue minimax pour les tableaux résultant de chaque coup possible et les ajoute à la liste

    return aviable_moves[scores.index(max(scores))] if player == MAX \
        else aviable_moves[scores.index(min(scores))]
    # renvoie coup provoquant le meilleur score de la liste pour l'ordinateur (le maximum s'il est joueur 1 et le
    # minimum s'il est joueur -1)


def move_ordinateur(table, player, q):
    """
    crée une copie du tableau et la transmet à la fonction chargée de trouver le meilleur coup
    :param table: le tableau en l'état actuel
    :param player: le joueur cherchant son meilleur coup
    :param q: la queue (objet multiprocessing) par laquelle on va transmettre le resultat à la fonction principal
    (agit comme return)
    :return: coordonées de la case du meilleur coup
    """
    table_copy = deepcopy(table)

    x = tuple(best_move(table_copy, player))
    q.put(x)  # agit comme return
