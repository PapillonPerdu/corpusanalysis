import wget
import json
import os

#Retrieve data from Thamous database.


def thamous_dic(id_thm,table):
    """Dictionary with Thamous data"""
    url = "https://thamous.univ-rennes1.fr/php/plain.php?table=t" + table + "&id_ref=" + id_thm
    filename = wget.download(url)
    with open(filename) as json_file:
        thm_dic = json.load(json_file)
        if os.path.exists(filename):
            os.remove(filename)
    return thm_dic

def thamous_ref_biblio(id_thm):
    thm_dic = thamous_dic(id_thm,'biblio')
    type = thm_dic['type']
    str = ''
    if type == 'Article':
        str = thm_dic['nom'] + ", \"" + thm_dic['titre'] + "\", " + thm_dic['editeur'] + ", " \
              + thm_dic['volume']
        if thm_dic['tomaison']: str += "(" + thm_dic['tomaison'] + "), "
        str += thm_dic['pages'] + ", " + thm_dic['annee']
    elif type == 'Livre' or type == 'Thèse' :
        str = thm_dic['nom'] + ", " + thm_dic['titre'] + ", " + thm_dic['editeur'] + ": " + thm_dic['lieu'] + ", " \
              + thm_dic['annee']
    return str

def thamous_ref_personnes(id_thm):
    thm_dic = thamous_dic(id_thm, 'biblio')
    str = thm_dic['nom'] + "(" + thm_dic['naissance'] + '-' + thm_dic['mort'] +')'
    return str

def thamous_ref_institutions(id_thm):
    thm_dic = thamous_dic(id_thm, 'biblio')
    str = thm_dic['nom']
    return str

def thamous_ref_revues(id_thm):
    thm_dic = thamous_dic(id_thm, 'biblio')
    str = thm_dic['titre']
    return str

def thamous_ref(id_thm,table):
    if table == 'biblio':
        thm_ref = thamous_ref_biblio(id_thm)
    elif table == 'personnes':
        thm_ref = thamous_ref_personnes(id_thm)
    elif table == 'institutions':
        thm_ref = thamous_ref_institutions(id_thm)
    elif table == 'revues':
        thm_ref = thamous_ref_revues(id_thm)
    else:
        print('Table ' + table + "is unrecognised.")
    return thm_ref

