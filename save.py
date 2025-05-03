from json import loads, dumps

DEFAULT_OPTIONS = {
    'showCoordinates': False,
    'showRewards': True,
    'showPrevisions': True,
    'showAnimations': True,
    'background': 'green',
    'allowCancel': True,
    'cpuColor': 1

}


def load_options():
    """
    renvoie le dictionnaire contenu dans options.json si le fichier existe, sinon les valeurs par défaut
    :return:
    """
    try:
        with open("savefiles/options.json", "r") as f:
            data = f.read()
            return loads(data)  # renvoie le dictionnaire décryté d'un string format json
    except IOError:
        return DEFAULT_OPTIONS


def dump_options(json_object):
    """
    sauvegarde le dictionnaire passé dans json_objet dans le fichier options.json
    :param json_object: dictionnaire à sauvegarder
    :return:
    """

    data = dumps(json_object, indent=1)  # transforme le fichier en string au format json

    with open("savefiles/options.json", "w") as f:
        f.write(data)


def check_save_aviability():
    """
    Controle si une save est bien disponible
    :return: True si une save est disponible, False sinon
    """

    aviability = False
    try:
        with open("savefiles/save.json", "r") as save_file:  # si le fichier save.json existe
            data = save_file.read()
            values = loads(data)  # transforme le string au format json en dictionnaire
            if values['saveAviable'] and values['turnsPassed'] is not None and values['gamemode'] is not None \
                    and values['cpuColor'] is not None:  # et si les valeurs indiquent qu'une save existe
                try:
                    f = open("savefiles/states.pickle", "rb")  # et si le fichier de sauvegarde existe
                except IOError:
                    pass
                else:
                    f.close()
                    aviability = True  # alros on peut dire qu'une save est disponible
    finally:
        return aviability


def delete_save():
    """
    indique dans le fichier save.json qu'aucune sauvegarde n'est disponible
    :return:
    """
    values = {
        'saveAbviable': False,
        'turnsPassed': None,
        'gamemode': None,
        'cpuColor': None
    }
    data = dumps(values, indent=1)  # transforme le dictionnaire en string au format json
    with open("savefiles/save.json", "w") as f:
        f.write(data)
