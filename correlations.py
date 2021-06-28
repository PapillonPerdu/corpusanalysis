# # Introduction

# Le programme ci-dessous offre quelques fonctions pour l'analyse et la représentation des corrélations entre les textes d'un corpus présentées dans un tableau.
# pour activer les widgets, exécuter avant le lancement de jupyter :
# jupyter nbextension enable --py widgetsnbextension --sys-prefix
# # Le programme

from __future__ import print_function
import numpy as np
import pandas as pd
from sympy import *
import csv
import networkx as nx
import matplotlib.pyplot as plt
from scipy.spatial import distance_matrix
from sklearn import manifold
from matplotlib.collections import LineCollection
import matplotlib.colors as colors
import matplotlib.cm as cmx
import re
import sys
import operator
from operator import itemgetter
import itertools
from mpl_toolkits.mplot3d import axes3d
import collections
from collections import defaultdict
import ipywidgets as widgets
from ipywidgets import interact, interactive, fixed, interact_manual, Layout
from ipywidgets import Layout, Button, Box, FloatText, Textarea, Dropdown, Label, IntSlider
from IPython.display import display, HTML
try:
    from tqdm.notebook import tqdm
except:
    print("Le module tqdm.notebook n'a pu être importé.")
    print("Les fonctions sushoivantes ne seront pas utilisables : ")
    print("     decomposition")
    print("     noms_base_complete")
    print("     vars_base")
    print("     vars_base_first")


# source : https://stackoverflow.com/questions/31581425
def getCombinations(lst, max):
    for L in range(1, max + 1):
        for subset in itertools.combinations(lst, L):
            yield list(subset)


# test si la liste l contient une liste de la liste M
def includes(l, M):
    for m in M :
        if len(set(l) - set(m)) == len(l) - len(m):
            # print(l,' contient un ',M)
            return True
    # print(l,' ne contient pas un ',M)
    return False


# test si la liste l est contenue dans une liste de la liste M
def inList(l, M):
    for m in M:
        if len(set(m) - set(l)) == len(m) - len(l):
            # print(l,' contient un ',M)
            return True
    # print(l,' ne contient pas un ',M)
    return False


# entrée : une liste, et une fonction teste sur les éléments de la liste
# sortie : vrai si tous les éléments de la liste vérifient la condition, faux sinon

def testAll(l, condition):
    for x in l:
        if not condition(x):
            return False
            break
    return True


# entrée : une liste, et une fonction teste sur les éléments de la liste
# sortie : vrai si un élément de la liste vérifie la condition, faux sinon

def testOne(l, condition):
    for x in l:
        if condition(x):
            return True
            break
    return False


# union d'une liste de listes
def merge(lists):
    m = []
    for l in lists:
        m += l
    return m


def subIntervalles(l, M):
    for m in M:
        if l[0] >= m[0] and l[1] <= m[1]:
            # print(l,' contient un ',M)
            return True
    # print(l,' ne contient pas un ',M)
    return False


def allEmpty(vals, indexesVars):
    for n in indexesVars:
        if not vals[n] == '':
            return False
    return True


def liset(L):
    liset = [{i} for i in L]
    return liset


class color:
    purple = '\033[95m'
    cyan = '\033[96m'
    darkcyan = '\033[36m'
    blue = '\033[94m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    bold = '\033[1m'
    underline = '\033[4m'
    end = '\033[0m'


##########################################################################################
### Fonctions lexique
######################################################################################


# Une identification est une liste commençant par un mot, suivie
# d'expressions régulières décrivant les identifications à ce mot
# Une orbite est une liste de mots (identifiés)
# Une orbiteFreq est une liste de couples [mot, fréquence]
# Un lexiqueFreq est une liste d'orbiteFreq


# entrée : texte sous forme d'une chaîne
# sortie : liste des mots du texte
def textToWords(text):
    return re.sub("[^\w]", " ", text).split()


# teste si un mot est dans l'orbite donnée par une identification,
# pouvant comprendre des expressions régulières
def inOrbite(word, identification):
    boole = False
    idsx = ["^" + id + "$" for id in identification]
    ids_reg = '|'.join(idsx)
    if re.match(ids_reg, word):
        boole = True
    return boole


# entrée : liste de termes identifiés (avec reg exp.)
# sortie : orbite (relative à une liste de mots).
def identificationToOrbite(identification, words):
    orbite = [word for word in words if inOrbite(word, identification)]
    orbite = list(set(orbite))
    return orbite


# retourne la fréquence totale d'une orbiteFreq (somme des fréquences)
def orbiteFreqTotal(orbiteFreq):
    freq = sum([f for w, f in orbiteFreq])
    return freq


# Transforme une liste d'orbites en lexiqueFreq
def orbitesToLexiqueFreq(orbites, words):
    dictFreq = {word: words.count(word) for word in words}
    lexiqueFreq = []
    for orbite in orbites:
        orbiteFreq = [[word, dictFreq[word]] for word in orbite]
        lexiqueFreq.append(orbiteFreq)
    return lexiqueFreq


# Représentation sous forme de chaîne d'une orbiteFreq
def orbiteFreqToStr(orbiteFreq):
    res = ', '.join([str(w) + ' (' + str(f) + ')' for w, f in orbiteFreq])
    return res


# Trie un lexiqueFreq
def sortLexiqueFreq(lexiqueFreq, ordre, reverse):
    if ordre == 'freq':
        frequences = [orbiteFreqTotal(orbiteFreq) for orbiteFreq in lexiqueFreq]
        lexiqueFreq = [orbiteFreq for freq, orbiteFreq in sorted(zip(frequences, lexiqueFreq), reverse=reverse)]

    if ordre == 'alpha':
        lexiqueFreq = sorted(lexiqueFreq, reverse=reverse)

    return lexiqueFreq


def wordsToOrbites(words, identifications):
    '''Transforme une liste de mots en une liste d'orbite'''
    from itertools import groupby
    words = [w.lower() for w in words]
    words_uniques = list(set(words))

    # dictionnaire des orbites définies par identification
    dictOrbites = {str(identification[0]): identificationToOrbite(identification, words_uniques) for identification in
                   identifications}

    # liste des mots dans une orbites
    motsInOrbites = list(set(merge(list(dictOrbites.values()))))
    representants = list(dictOrbites.keys())

    # Substitution du représentant aux mots identifiés
    orbites = []
    for word in words_uniques:
        if word in representants:
            # word est le représentant d'une identification. On enregistre son orbite
            orbites.append(dictOrbites[word])
        else:
            # word n'est pas le représentant d'une identification
            if not word in motsInOrbites:
                # si word est dans une orbite, on ne l'enregistre pas dans le lexique
                # sinon, on enregistre son orbite réduite à lui-même
                orbites.append([word])

    return orbites


# Réduction de la liste des orbites
# conditions sur :
# -- la longueur des mots
# -- mots exclus
# -- mots forcés
def orbitesReduction(orbites, mots, motSauf, min, max):
    def minmax(x):
        return (min <= len(x) <= max or x in mots)

    def exclus(x):
        return x in motSauf

    def forces(x):
        return x in mots

    orbitesRed = [orbite for orbite in orbites if testOne(orbite, forces) or
                  (testAll(orbite, minmax) and not testAll(orbite, exclus))]

    return orbitesRed


#########################################################
#### Interactivité - fonctions communes
#########################################################
# entrée : "a,b"
# sortie : [a,b]
# les blancs au début des éléments sont supprimés
def strToList(strList):
    L = strList.split(',')
    L = list(map(str.strip, L))
    return L


# entrée : "a,b;c,d;e,f"
# sortie : [[a,b],[c,d],[e,f]]
# les blancs sont supprimés de l'entrée
def strListToLists(strList):
    strList.replace(' ', '')
    L = strList.split(';')
    res = []
    for l in L:
        res.append(l.split(','))
    return res


titre_layout = Layout(
    display='flex',
    flex_flow='row',
    justify_content='space-around'
)

sous_titres_layout = Layout(
    display='flex',
    flex_flow='row',
    justify_content='space-around'
)

formule_layout = Layout(
    display='flex',
    flex_flow='row',
    justify_content='center'
)

textArea_layout = Layout(
    flex='0 1 auto', height='30px', width='auto'
)

textAreaFormule_layout = Layout(
    flex='0 1 auto', height='30px', width='400px'
)

nomsDonnes_layout = Layout(flex='0 1 auto', height='40px', width='400px')


class Correlations:
    """Classe pour l'analyse d'un tableau de variables

    :fileIn : nom du fichier csv contenant les données
    :baseName : chaîne qui sera ajoutée aux noms des données dans les sorties

    Propriétés :
    data : affiche le tableau des données
    poids : affiche les poids
    noms : affiche les noms
    vars : affiche les variables
    card : affiche le nombre d'entrées
    distMax : affiche la distance maximale possible
    distance_matrice : affiche la matrice des distances. Cette matrice mesure l'éloignement des données.
    proximite_matrice : affiche la matrice des proximités. Cette matrice mesure la proximité des données.
    distance_matrice_csv : enregistre la matrice des distances dans un fichier csv
    proximite_matrice_csv : enregistre la matrice des proximités dans un fichier csv
    distance_matrice_coordonnees : affiche les coordons le plan des données à partir de leurs distances
    proximite_matrice_coordonnees : affiche les coordonnées dans le plan des données à partir de leurs proximité
    graphe_distance_show : affiche le graphe à partir de la matrice des distances
    graphe_distance_save : enregistre le graphe à partir de la matrice des distances
    graphe_proximite_show: affiche le graphe à partir de la matrice de proximité
    graphe_proximite_save : enregistre le graphe à partir de la matrice de proximité
    find : liste des noms ayant pour le critère j la valeur donnée
    contains : liste des noms ayant contenant pour le critère j la chaîne donnée
    like : listes des noms ayant pour le critère j la même valeur que celle du nom donné
     """

    def __init__(self,
                 fileIn, baseName = '', varsTypes = [], nomsTypes = [],
                 varsTypesRegles = '', nomsTypesRegles = ''):
        self.__baseName = baseName
        # Pour que les lignes des tableaux ne soient pas tronquées
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_colwidth', -1)
        np.set_printoptions(threshold=sys.maxsize)

        if type(fileIn) == str: fileIn = [fileIn]

        frames = []
        noms = []
        variables = []
        poids = []
        for f in fileIn:
            try:
                ar = np.array(pd.read_csv(open(f,encoding="UTF-8"), delimiter=","))
            except:
                print("Impossible d\'ouvrir le fichier \"" + f + "\"")
                sys.exit(1)

                # Suppression des colonnes (resp. lignes) dont le nom est vide
            j = 1
            while j < np.size(ar, 1):
                if str(ar[1, j]) == 'nan':
                    ar = np.delete(ar, j, 1)
                else:
                    j += 1
            i = 2
            while i < np.size(ar, 0):
                if str(ar[i, 0]) == 'nan':
                    ar = np.delete(ar, i, 0)
                else:
                    i += 1

            if not len(frames):
                noms = ar[2:, 0].tolist()

            variables += ar[1, 1:].tolist()
            poids += ar[0, 1:].tolist()
            frames.append(pd.DataFrame(ar[2:, 1:]).replace(np.nan, ''))

        self.__array = pd.concat(frames, axis=1, join='inner')
        data = np.array(self.__array)

        variables = [str(x) for x in variables]
        self.__vars = variables
        self.__selectedVars = variables
        self.__selectedIndexesVars = [i for i in range(len(self.__selectedVars))]

        # initialisation des types de variables
        if varsTypes: self.set_vars_types(varsTypes, varsTypesRegles = varsTypesRegles)

        try:
            poids = list(map(int, poids))
        except:
            poids = [1] * (len(variables))
            print("Les poids ont tous été fixés à 1.")
        self.__poids = poids
        self.__selectedPoids = poids

        noms = [str(x) for x in noms]
        self.__noms = noms
        self.__selectedNoms = noms
        self.__selectedIndexesNoms = [i for i in range(len(self.__selectedNoms))]

        # initialisation des types de noms
        if nomsTypes: self.set_noms_types(nomsTypes, nomsTypesRegles = nomsTypesRegles)

        self.__data = data
        self.__selectedData = data

        self.__card = len(self.__data)
        self.__selectedCard = len(self.__selectedData)
        self.__selectedVarsCard = len(self.__selectedVars)
        self.__distMax = sum(self.__poids)
        self.__selectedDistMax = sum(self.__selectedPoids)

        self.__exclus = ['','*', '?', '#']
        self.__coches = ['*', '#', '-']
        self.__logicalOperatorsBinary = ['|', '&']
        self.__logicalOperatorsUnary = ['~']
        self.__logicalOperators = self.__logicalOperatorsBinary + self.__logicalOperatorsUnary

        # self.prox_matrices(indexesVars=self.__selectedIndexesVars,indexesNoms=self.__selectedIndexesNoms)

        mds = manifold.MDS(n_components=2, dissimilarity="precomputed", random_state=6)

        # paramètres graphes de déviation
        self.__colorMap = 'gist_heat'
        self.__font_size = 14
        self.__font_color = 'black'
        self.__font_weight = 'normal'
        self.__node_color = 'black'
        self.__node_size = 20
        self.__graph_width = 20
        self.__graph_height = 20
        self.__label_posX = .1
        self.__label_posY = .1

        # paramètres graphes matrice de coordonnées
        self.__gmc_font_size = 10
        self.__gmc_font_color = 'black'
        self.__gmc_node_size = 5
        self.__gmc_node_color = 'black'
        self.__gmc_label_pos = .5
        self.__gmc_width = 20
        self.__gmc_height = 20
        self.__gmc_label_posX = .1
        self.__gmc_label_posY = .1

    ##########################################################################################
    ### Méthodes communes
    ######################################################################################
    def get_langues(self):
        try:
            res = self.__data[0:, self.varToIndex('langue')].tolist()
            return list(set(res))
        except:
            return []

    @property
    def baseName(self):
        return self.__baseName

    def set_baseName(self, baseName):
        self.__baseName = baseName

    @property
    def array(self):
        return self.__array

    @property
    def print(self):
        print(pd.DataFrame(self.__data, columns=self.__vars, index=self.__noms))

    @property
    def data(self):
        return self.__data

    def show_data(self,
                  noms=None, nomSauf=None, vars=None, varSauf=None,
                  varsTypes=None, varsTypeSauf=None, varsTypesFormule='',
                  nomsTypes=None, nomsTypeSauf=None, nomsTypesFormule='',
                  pasColonne=10, pasLigne=10):

        if nomsTypeSauf is None:
            nomsTypeSauf = []
        if nomsTypes is None:
            nomsTypes = []
        if varsTypeSauf is None:
            varsTypeSauf = []
        if varsTypes is None:
            varsTypes = []
        if varSauf is None:
            varSauf = []
        if vars is None:
            vars = []
        if nomSauf is None:
            nomSauf = []
        if noms is None:
            noms = []
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        lines = [[self.__data[i][k] for k in indexesVars] for i in indexesNoms]
        resNoms = [self.__noms[i] for i in indexesNoms]
        resVars = [self.__vars[i] for i in indexesVars]

        if pasColonne:
            res = self.repeteIndex(pasColonne, lines, resVars, resNoms)
            lines = res[0]
            resVars = res[1]

        if pasLigne:
            res = self.repeteColumns(pasLigne, lines, resVars, resNoms)
            lines = res[0]
            resNoms = res[1]

        print('Variables : ' + str(len(indexesVars)))
        df = pd.DataFrame(lines, columns=resVars, index=resNoms)
        display(df)
        # return pd.DataFrame(self.__data, columns=self.__vars, index=self.__noms)

    @property
    def selectedData(self):
        return pd.DataFrame(self.__selectedData, columns=self.__selectedVars, index=self.__selectedNoms)

    @property
    def poids(self):
        print(self.__poids)

    def show_noms(self,
                  noms=[], nomSauf=[], nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):

        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
        listNoms = ['Noms'] + [self.__noms[n] for n in indexesNoms]
        display(pd.DataFrame(columns=listNoms))

    @property
    def noms(self, noms=[]):
        return self.__noms

    @property
    def selectedNoms(self):
        return self.__selectedNoms

    @property
    def selectedIndexesNoms(self):
        return self.__selectedIndexesNoms

    @property
    def selectedPoids(self):
        return self.__selectedPoids


    @property
    def vars(self):
        return self.__vars

    def get_vars(self,
                  vars=[], varSauf=[],
                  varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        listVars = [self.__vars[v] for v in indexesVars]
        return listVars

    def show_vars(self,
                  vars=[], varSauf=[],
                  varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        listVars = ['Variables'] + [self.__vars[v] for v in indexesVars]
        print('Variables : ' + str(len(indexesVars)))
        display(pd.DataFrame(columns=listVars))

    @property
    def selectedVars(self):
        return self.__selectedVars

    @property
    def show_selectedVars(self):
        print(color.bold + 'Variables sélectionnées : ' + color.end)
        for var in self.__selectedVars:
            print(var)
            print()

    @property
    def show_selected(self):
        self.show_selectedNoms
        self.show_selectedVars

    @property
    def selectedDistMax(self):
        return self.__selectedDistMax

    def indexToVar(self, num):
        return self.__vars[num]

    def indexToNom(self, num):
        return self.__noms[num]

    def indexToSelectedNom(self, num):
        return self.__selectedNoms[num]

    def varToIndex(self, chain):
        try:
            return self.__vars.index(chain)
        except:
            print("\"" + str(chain) + "\" n'est pas le nom d'une variable.")
            sys.exit(1)

    def nomToIndex(self, nom):
        # index1=np.where(self.__noms == nom)

        if type(nom) == str:
            try:
                return self.__noms.index(nom)
            except:
                sys.exit(color.bold + "Le nom \"" + nom + "\" n'est pas reconnu." + color.end)

        if type(nom) == int:
            try:
                return self.__noms[nom]
            except:
                print(color.bold + "Le nom \"" + nom + "\" n'est pas reconnu." + color.end)
                sys.exit(1)

    def indexNomToRedindex(self,
                           num, indexesNoms):
        return indexesNoms.index(num)

    def redindexNomToIndex(self,
                           num, indexesNoms):
        return self.__noms.index(self.__selectedNoms[num])

    def redindexVarToIndex(self,
                           num, indexesVars):
        return self.__vars.index(self.__selectedVars[num])

    def redindexNomToNom(self,
                         num, indexesNoms):
        return self.__noms[indexesNoms[num]]

    def nomToRedindex(self,
                      nom, indexesNoms):
        return self.indexNomToRedindex(self.__noms.index(nom), indexesNoms)

    def nomsToIndexes(self, noms):
        indexes = [self.nomToIndex(nom) for nom in noms]
        return indexes

    def varToNum(self, chain):
        vars = [i for i in range(len(self.__vars)) if
                str(chain).replace('\n', '').strip() in str(self.__vars[i]).replace('\n', '').strip()]
        for v in vars:
            print(v + 1)
            print(self.__vars[v].replace('\n', ' '))
            print()

    def interVars(self,
                  var1, var2=''):
        if var2 == '': var2 = var1
        try:
            index1 = self.__selectedVars.index(var1)
        except:
            print("La variable \"" + var1 + "\" n'est pas sélectionnée.")
            exit(1)

        try:
            index2 = self.__selectedVars.index(var2) + 1
        except:
            print("La variable \"" + var2 + "\" n'est pas sélectionnée.")
            exit(1)

        if index1 > index2:
            print("La variable \"" + var1 + "\" doit être avant \"" + var2 + "\"")
            exit(1)
        else:
            return self.__selectedVars[index1:index2]

    def interNoms(self,
                  nom1, nom2=''):
        if nom2 == '': nom2 = nom1
        try:
            index1 = self.__noms.index(nom1)
        except:
            print("L'édition \"" + nom1 + "\" n'existe pas.")
        try:
            index2 = self.__noms.index(nom2) + 1
        except:
            print("L'édition \"" + nom2 + "\" n'existe pas.")

        if index1 > index2:
            print("L'édition \"" + nom1 + "\" doit être avant \"" + nom2 + "\"")
        else:
            return self.__noms[index1:index2]

    def nomsApres(self, nom):
        try:
            index = self.__noms.index(nom)
            return self.__noms[index:len(self.__noms)]
        except:
            print("Le nom \"" + nom + "\" n'est pas reconnu")

    def nomsApresStrict(self, nom):
        try:
            index = self.__noms.index(nom)
            return self.__noms[index + 1:len(self.__noms)]
        except:
            print("Le nom \"" + nom + "\" n'est pas reconnu")

    def nomsAvant(self, nom):
        try:
            indexNom = self.nomToIndex(nom)
            return self.__noms[0:indexNom + 1]
        except:
            print("Le nom \"" + nom + "\" n'est pas reconnu")

    def nomsAvantStrict(self, nom):
        try:
            indexNom = self.nomToIndex(nom)
            return self.__noms[0:indexNom]
        except:
            print("Le nom \"" + nom + "\" n'est pas reconnu")

    def varsAvant(self, var):
        try:
            index = self.__vars.index(var)
            return self.__vars[0:index + 1]
        except:
            print("La variable \"" + var + "\" n'est pas reconnue")

    def varsApres(self, var):
        try:
            index = self.__vars.index(var)
            return self.__vars[index:len(self.__vars)]
        except:
            print("La variable \"" + var + "\" n'est pas reconnue")

    def set_selectedIndexesVars(self, indexesVars):
        self.__selectedIndexesVars = indexesVars
        self.__selectedVarsCard = len(self.__selectedIndexesVars)
        self.__selectedVars = [self.__vars[v] for v in self.__selectedIndexesVars]
        self.__selectedPoids = [self.__poids[i] for i in self.__selectedIndexesVars]
        self.__selectedDistMax = sum(self.__selectedPoids)

    def set_selectedIndexesNoms(self, indexesNoms):
        self.__selectedIndexesNoms = indexesNoms
        self.__selectedNomsCard = len(self.__selectedIndexesNoms)
        self.__selectedNoms = [self.__noms[n] for n in self.__selectedIndexesNoms]

    def set_selectedVars(self, vars):
        self.__selectedVars = vars
        self.__selectedVarsCard = len(self.__selectedVars)
        self.__selectedIndexesVars = [self.varToIndex(var) for var in self.__selectedVars]
        self.__selectedPoids = [self.__poids[i] for i in self.__selectedIndexesVars]
        self.__selectedDistMax = sum(self.__selectedPoids)
        self.matrices()
        self.show_selectedVars

    def set_selectedNoms(self, noms):
        self.__selectedNoms = noms
        self.__selectedNomsCard = len(self.__selectedNoms)
        self.__selectedIndexesNoms = [self.nomToIndex(nom) for nom in self.__selectedNoms]
        self.matrices()
        self.show_selectedNoms

    @property
    def card(self):
        print(self.__card)

    # variables pour lesquelles une édition a une vraie valeur (i.e. n'a pas une valeur exclue)
    def indexesVarsDefiniesNom(self,
                               indexNom, indexesVars):
        trueVars = [i for i in indexesVars if not self.__data[indexNom][i] in self.__exclus]
        return trueVars

    # variables pour lesquelles des éditions ont une vraie valeur (i.e. n'a pas une valeur exclue)
    def indexesVarsDefinies(self,
                            indexesNoms, indexesVars):
        trueVars = []
        for n in indexesNoms:
            trueVars += self.indexesVarsDefiniesNom(n, indexesVars)

        trueVars = sorted(list(set(trueVars)))
        return trueVars

    # nombre de variables pour lesquelles l'édition a une vraie valeur (i.e. n'a pas une valeur exclue)
    def totalVarsNom(self,
                     indexNom, indexesVars):
        trueVars = self.indexesVarsDefiniesNom(indexNom, indexesVars)
        return len(trueVars)

    # nombre de variables pour lesquelles une liste d'éditions ont une vraie valeur (i.e. n'a pas une valeur exclue)
    def totalVarsDefinies(self,
                          indexesNoms, indexesVars):
        trueVars = self.indexesVarsDefinies(indexesNoms, indexesVars)
        return len(trueVars)

    # nombre total des variables (différentes) dans un dictionnaire/collection de listes de variables
    def collTotal(self, coll):
        vals = []
        for k, l in coll.items():
            vals += l
        vals = set(vals)
        return len(vals)

        # indexes des variables d'un type, parmi une liste d'indexes de variables,

    # sur lesquelles deux éditions données
    # ont des valeurs définies
    def indexesVarsDefiniesConjointes(self,
                                      indexNom1, indexNom2, indexesVars):
        indexesVarsDef = []
        for i in indexesVars:
            if self.__data[indexNom1][i] not in self.__exclus and \
                    self.__data[indexNom2][i] not in self.__exclus:
                indexesVarsDef.append(i)
        return indexesVarsDef

    # nombre des variables d'un type, parmi une liste d'indexes de variables,
    # sur lesquelles deux éditions données
    # ont des valeurs définies
    def totalVarsDefiniesConjointes(self,
                                    indexNom1, indexNom2, indexesVars):
        indexesVarsDef = self.indexesVarsDefiniesConjointes(indexNom1, indexNom2, indexesVars)
        return len(indexesVarsDef)

    # somme pondérée de variables d'un type, parmi une liste d'indexes de variables,
    # sur lesquelles deux éditions données
    # ont des valeurs définies
    def totalPondereVarsDefiniesConjointes(self,
                                           indexNom1, indexNom2, indexesVars):
        indexesVarsDef = self.indexesVarsDefiniesConjointes(indexNom1, indexNom2, indexesVars)
        sum = 0
        for v in indexesVarsDef:
            sum += self.__poids[v]
        return sum

    def varsToIndexesVars(self,
                          listVars, listVarSauf):
        indexesVars = []
        if type(listVars) == int:
            try:
                v = self.indexToVar(listVars)
            except:
                print(color.bold + "La variable n°", listVars, " n'est pas reconnue." + color.end)
                sys.exit(1)
            listVars = [v]

        if type(listVars) == str:
            try:
                v = self.__vars.index(listVars)
            except:
                print(color.bold + "La variable \"", listVars, "\" n'est pas reconnue." + color.end)
                sys.exit(1)
            listVars = [listVars]

        # if len(listVars) == 0: listVars = self.__vars
        if listVars :
            indexesVars = [self.varToIndex(v) for v in listVars if v not in listVarSauf]
            indexesVars = sorted(list(set(indexesVars)))
        return indexesVars

    # détermination d'indexesVars à partir de
    # vars,varSauf,varsTypes,varsTypeSauf,varsTypesFormule
    def getIndexesVarsStrict(self,
                       vars=[], varSauf=[],
                       varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):

        varsT = []
        if varsTypesFormule:
            varsT = self.varsTypesFormulaToVars('self.typeToIndexesVars', varsTypesFormule)

        if varsTypes:
            if varsT:
                varsT = list(set(self.typesToVars(varsTypes)).intersection(set(varsT)))
            else:
                varsT = self.typesToVars(varsTypes)

        if vars:
            if varsT:
                vars = list(set(vars).intersection(set(varsT)))
        else:
            vars = varsT

        varsTSauf = []
        if varsTypeSauf:
            varsTSauf = self.typesToVars(varsTypeSauf)

        if varSauf:
            if varsTSauf:
                varSauf = list(set(varSauf)).union(set(varsTSauf))
        else:
            varSauf = varsTSauf

        indexesVars = self.varsToIndexesVars(vars, varSauf)

        return indexesVars

    def getIndexesVars(self,
                       vars=[], varSauf=[],
                       varsTypes=[], varsTypeSauf=[], varsTypesFormule='') :

        indexesVars = self.getIndexesVarsStrict(vars=vars, varSauf=varSauf,
                       varsTypes=varsTypes, varsTypeSauf=varsTypeSauf, varsTypesFormule=varsTypesFormule)

        if not indexesVars :
            indexesVars=[i for i in range(len(self.__vars))]

        return indexesVars

    def getIndexesNoms(self,
                       noms, nomSauf,
                       nomsTypes, nomsTypeSauf, nomsTypesFormule):

        nomsT = []
        if nomsTypesFormule:
            nomsT = self.nomsTypesFormulaToNoms('self.typeToIndexesNoms', nomsTypesFormule)

        if nomsTypes:
            if nomsT:
                nomsT = list(set(self.typesToNoms(nomsTypes)).intersection(set(nomsT)))
            else:
                nomsT = self.typesToNoms(nomsTypes)

        if noms:
            if nomsT:
                noms = list(set(noms).intersection(set(nomsT)))
        else:
            noms = nomsT

        nomsTSauf = []
        if nomsTypeSauf:
            nomsTSauf = self.typesToNoms(nomsTypeSauf)

        if nomSauf:
            if nomsTSauf:
                nomSauf = list(set(nomSauf)).union(set(nomsTSauf))
        else:
            nomSauf = nomsTSauf

        indexesNoms = self.nomsToIndexesNoms(noms, nomSauf)

        return indexesNoms

    def nomsToIndexesNoms(self,
                          listNoms, listNomSauf):
        if type(listNoms) == str:
            try:
                n = self.__noms.index(listNoms)
            except:
                print(color.bold + "Le nom \"" + listNoms + "\" ne fait pas partie des noms sélectionnés." + color.end)
                sys.exit(1)
            listNoms = [listNoms]

        if len(listNoms) == 0: listNoms = self.__noms

        indexesNoms = [self.nomToIndex(n) for n in listNoms if n not in listNomSauf]
        indexesNoms = sorted(list(set(indexesNoms)))
        return indexesNoms

    def updateProxMatrices(self,
                           indexesVars, indexesNoms):
        if not indexesVars == self.__selectedIndexesVars or not indexesNoms == self.__selectedIndexesNoms:
            self.prox_matrices(indexesNoms, indexesVars)

    def updateDistMatrices(self,
                           indexesVars, indexesNoms):
        if not indexesVars == self.__selectedIndexesVars or not indexesNoms == self.__selectedIndexesNoms:
            self.dist_matrices(indexesNoms, indexesVars)

        # test d'égalité avec des valeurs pouvant contenir un &

    # Ex. :
    # a & b = b & d est vrai
    def equal(self,
              str1, str2):
        str1 = str(str1)
        str2 = str(str2)
        str1 = str1.replace(" ", "")
        str2 = str2.replace(" ", "")
        ar1 = str1.split('&')
        ar2 = str2.split('&')
        inter = np.intersect1d(ar1, ar2)
        return len(inter) > 0

    def equalStrict(self,
                    str1, str2):
        str1 = str(str1)
        str2 = str(str2)
        str1 = str1.replace(" ", "")
        str2 = str2.replace(" ", "")
        return str1 == str2

    # test d'égalité entre deux listes à un pourcentage entier donné pour une liste d'indexes
    def listsEqual(self,
                   L1, L2, indexesVars, precision=100):
        if (type(precision) != int): precision = 100
        sum = 0
        for i in indexesVars:
            if (self.equal(L1[i], L2[i])): sum += 1
        return sum / len(indexesVars) * 100 >= precision

    # Pourcentage d'égalité de deux listes sur une liste de variables
    def listsEqualPourcent(self,
                           L1, L2, indexesVars):
        sum = 0
        for i in indexesVars:
            if (self.equal(L1[i], L2[i])): sum += 1
        try:
            return round(sum / len(indexesVars) * 100)
        except:
            return 0

    # fait la somme d'une liste de listes et et retourne le pourcentage d'égalité
    # avec une liste donnée
    def sumEqualPourcent(self,
                         ListeL, L, indexesVars):
        sum = 0
        for i in indexesVars:
            ok = False
            for l in ListeL:
                if self.equal(l[i], L[i]):
                    ok = True
                    break
            if ok: sum += 1

        return round(sum / len(indexesVars) * 100)

    # fait la somme d'une liste de listes et teste s'il y une égalité, à un pourcentage près
    # avec une liste donnée

    def sumEqualPourcentTest(self,
                             ListeL, L, indexesVars, pourcent):
        sum = 0
        for i in indexesVars:
            ok = False
            for l in ListeL:
                if self.equal(l[i], L[i]):
                    ok = True
                    break
            if ok: sum += 1

        return sum / len(indexesVars) * 100 >= pourcent

    # nombre de variables pour lesquelles l'édition a une vraie valeur (i.e. n'a pas une valeur exclue)
    def totalVars(self, indexNom, indexesVars):
        trueVars = [i for i in indexesVars if not self.__data[indexNom][i] in self.__exclus]
        return len(trueVars)

    # NON UTILISE
    # fonction de calcul de la proximité
    def prox(L1, L2, poids):
        prox = 0
        for i in range(len(L1)):
            if L1[i] != '*' and L2[i] != '*' and L1[i] != '?' and L2[i] != '?':
                prox += (self.equal(L1[i], L2[i])) * poids[i]
        return prox
    # Ne semble pas utilisé
    # def intersect(self, listeNoms):
    #     indexesNoms = self.nomsToIndexes(noms)
    #     inter = []
    #     res = [self.__selectedVars[i] for i in range(len(self.__selectedVars)) if
    #            chain in str(self.__SelectedData[i][v])]
    #     for k in range(len(self.__selectedVars)):
    #         if data[i][k] != '*' and data[j][k] != '*' and self.equal(data[i][k], data[j][k]):
    #             inter.append(data[i][k])
    #         else:
    #             inter.append('')
    #     return inter

    # Liste des variables sur lesquelles une éditions diffèrent d'une liste d'éditions
    def vars_difference_relative(self,
                                 nom, noms=None, nomSauf=None,
                                 vars=None, varSauf=None,
                                 varsTypes=None, varsTypeSauf=None, varsTypesFormule='',
                                 nomsTypes=None, nomsTypeSauf=None, nomsTypesFormule=''):
        if nomsTypeSauf is None:
            nomsTypeSauf = []
        if nomsTypes is None:
            nomsTypes = []
        if varsTypeSauf is None:
            varsTypeSauf = []
        if varsTypes is None:
            varsTypes = []
        if varSauf is None:
            varSauf = []
        if vars is None:
            vars = []
        if nomSauf is None:
            nomSauf = []
        if noms is None:
            noms = []
        indexNom = self.nomToIndex(nom)

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        ListeL = [self.__data[i] for i in indexesNoms]
        indexesVarsDiff = []
        for i in indexesVars:
            equal = False
            for l in ListeL:
                if self.equal(l[i], self.__data[indexNom][i]):
                    equal = True
                    break
            if not equal: indexesVarsDiff.append(i)

        indexesVarsDiff = sorted(indexesVarsDiff)
        varsDiff = [self.indexToVar(i) for i in indexesVarsDiff]

        return varsDiff

    def show_difference_relative(self,
                                 nom, noms=[], nomSauf=[],
                                 vars=[], varSauf=[],
                                 varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                 nomsTypes=[], nomsTypeSauf=[]):
        varsDiff = self.vars_difference_relative(nom, noms, nomSauf,
                                                 vars, varSauf,
                                                 varsTypes, varsTypeSauf, varsTypesFormule,
                                                 nomsTypes, nomsTypeSauf)
        display(pd.DataFrame(columns=varsDiff))

    # Liste des variables sur lesquelles une éditions est à égale à une édition d'une liste d'éditions
    def vars_somme_relative(self,
                            nom, noms=[], nomSauf=[],
                            vars=[], varSauf=[],
                            varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                            nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):

        indexNom = self.nomToIndex(nom)

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        ListeL = [self.__data[i] for i in indexesNoms]
        varsSum = []
        for i in indexesVars:
            equal = False
            for l in ListeL:
                if self.equal(l[i], self.__data[indexNom][i]):
                    equal = True
                    break
            if equal: varsSum.append(self.indexToVar(i))

        return varsSum

    def show_somme_relative(self,
                            nom, noms=None, nomSauf=None,
                            vars=None, varSauf=None,
                            varsTypes=None, varsTypeSauf=None, varsTypesFormule='',
                            nomsTypes=None, nomsTypeSauf=None, nomsTypesFormule=''):
        if nomsTypeSauf is None:
            nomsTypeSauf = []
        if nomsTypes is None:
            nomsTypes = []
        if varsTypeSauf is None:
            varsTypeSauf = []
        if varsTypes is None:
            varsTypes = []
        if varSauf is None:
            varSauf = []
        if vars is None:
            vars = []
        if nomSauf is None:
            nomSauf = []
        if noms is None:
            noms = []
        varsSum = self.vars_somme_relative(
            nom, noms, nomSauf,
            vars, varSauf,
            varsTypes, varsTypeSauf, varsTypesFormule,
            nomsTypes, nomsTypeSauf, nomsTypesFormule)
        display(pd.DataFrame(columns=varsSum))

    # répète la colonne de noms pour un pas donné
    def repeteIndex(self, pas, data, columns, index):
        i = pas
        while i < len(columns):
            columns.insert(i, '')
            for j in range(len(index)):
                data[j].insert(i, index[j])
            i += pas + 1
        return [data, columns]

    # répète la ligne de critères pour un pas donné
    def repeteColumns(self, pas, data, columns, index):
        i = pas
        while i < len(index):
            index.insert(i, '')
            data.insert(i, columns)
            i += pas + 1
        return [data, index]

    def bold(x):
        return ['font-weight: bold' if v == x.loc['Livre 1'] else ''
                for v in x]

    ##########################################################################################
    ### types variables
    ##########################################################################################

    @property
    def vars_types_types(self):
        return self.__vars_types_types

    # complète le tableau de types (data)
    # à partir d'un dictionnaire de règles (regles)
    # pour les types (types)
    def applyRegles(self,data, types, regles) :
        #print(types)
        # parcours des types ayant une regle
        for type, regle in regles.items() :
            typesRegle=list(map(str.strip,regle.split('&')))
            if type in types and typesRegle != [''] :
                indexType = types.index(type)
                for ssType in typesRegle :
                    neg = False
                    if ssType[0]=='~' :
                        neg=True
                        ssType=ssType[1:].strip()

                    testssType = False
                    try :
                        index_ssType = types.index(ssType)
                        testssType =  True
                    except :
                        print('\"'+color.bold+ssType+color.end+'\" dans la règle de \"'+color.bold+types[indexType]+color.end+'\" n\'est pas un type reconnu.')

                    if testssType :
                        for i in range(len(self.__vars)) :
                            if data[indexType][i] != '':
                                    if (data[index_ssType][i] == '' and neg == False) or (
                                            data[index_ssType][i] != '' and neg == True):
                                        data[index_ssType][i] = '*'

        return data


    def set_vars_types(self, fileIn, varsTypesRegles = '',pasColonne=10, pasLigne=10):
        if type(fileIn) == str: fileIn = [fileIn]
        fr = pd.DataFrame([])
        types=[]
        for f in fileIn:
            try:
                ar = np.array(pd.read_csv(open(f,encoding="UTF-8"), delimiter=","))
            except:
                print("Impossible d\'ouvrir le fichier des types \"" + f + "\"")
                sys.exit(1)
            # Suppression des colonnes (resp. lignes) dont le nom est vide
            j = 1
            while j < np.size(ar, 1):
                if str(ar[0, j]) == 'nan':
                    ar = np.delete(ar, j, 1)
                else:
                    j += 1
            i = 2
            while i < np.size(ar, 0):
                if str(ar[i, 0]) == 'nan':
                    ar = np.delete(ar, i, 0)
                else:
                    i += 1

            index = ar[1:, 0].tolist()
            cols = ar[0, 1:].tolist()
            ar=ar[1:,1:]
            fr_new = pd.DataFrame(ar, index=index, columns=cols)
            fr = pd.concat([fr_new, fr], axis=1)
            #pour préserver l'ordre des types
            types = types + [str(x) for x in index if x not in types]

        #remplace les nan par des ''
        fr = pd.DataFrame(fr).replace(np.nan, '')

        variables = [str(x) for x in fr.columns.tolist()]


        #variables sans types et variables typées non reconnues
        varsTypesError = sorted(list(set(variables) - set(self.__vars)))
        varSansType = sorted(list(set(self.__vars) - set(variables)))

        if varsTypesError:
            print('')
            print('')
            print(color.bold + str(len(varsTypesError))+' variables typées non reconnues : ' + color.end)
            display(pd.DataFrame(columns=varsTypesError))

        if varSansType:
            print('')
            print('')
            print(color.bold  + str(len(varSansType))+ ' variables ayant des valeurs sans type : ' + color.end)
            display(pd.DataFrame(columns=varSansType))

        if varsTypesError or varSansType : sys.exit(1)

        # L'ensemble des variables des tableaux de valeurs et des types coïncident
        #contrôle des doublons

        if len(variables) != len(set(self.__vars)):
            print(color.bold + 'Variables ayant le même nom :' + color.end)
            doubles = [item for item, count in collections.Counter(variables).items() if count > 1]
            print('')
            print(','.join(map(str, doubles)))
            sys.exit(1)

        #réordonnement des variables des types
        fr = fr[self.__vars]
        #réordonnement des types
        fr = fr.reindex(index=types)


        ar = fr.values
        self.__vars_types_data = ar.tolist()
        self.__vars_types_vars = fr.columns.tolist()
        self.__vars_types_types = [tp for tp in types if not tp == '']


        # application des règles
        if varsTypesRegles :
            reglesListe = []
            if type(varsTypesRegles) == str :
                varsTypesRegles = [varsTypesRegles]

            for file in varsTypesRegles :
                try:
                    array_regles = np.array(pd.read_csv(open(file,encoding="UTF-8"),
                                                        delimiter=","))
                    ar = pd.DataFrame(array_regles).replace(np.nan, '')
                    reglesListe=reglesListe+ar.values.tolist()
                except:
                    print("Impossible d\'ouvrir le fichier des règles \"" + file + "\"")
                    sys.exit(1)

            # dictionnaire des règles : type : règle
            regles = {r[0] : r[1] for r in reglesListe}
            self.__vars_types_data = self.applyRegles(self.__vars_types_data,
                                                      self.__vars_types_types,
                                                      regles)


        # nombre de valeurs d'une liste différentes de ''

    def show_vars_types(self,types = [], pasColonne=0,pasLigne=0):
        print(color.bold + 'Tableau des types de variables : ' + color.end)


        columns = self.__vars_types_vars
        if types :
            indexesTypes = self.varsTypesToIndexesTypes(types, [])
            index = types
            lines = [self.__vars_types_data[t] for t in indexesTypes]
        else :
            index = self.__vars_types_types
            lines = self.__vars_types_data

        if pasColonne:
            res = self.repeteIndex(pasColonne, lines, columns, index)
            lines = res[0]
            columns = res[1]

        if pasLigne:
            res = self.repeteColumns(pasLigne, lines, columns, index)
            lines = res[0]
            index = res[1]

        display(pd.DataFrame(lines, columns=columns, index=index))


    def totalNotNull(self, l):
        total = len(l) - l.count('')
        return total

    def indexesVarsDefiniesTypeNom(self,
                                   indexNom, indexesVars, tp):
        indexesVarsType = self.typeToIndexesVars(tp)
        indexesVarsT = sorted(list(set(indexesVarsType).intersection(set(indexesVars))))
        trueVars = [i for i in indexesVarsT if not self.__data[indexNom][i] in self.__exclus]
        return trueVars

    # nombre de variables d'un type donné pour lesquelles l'édition
    # a une vraie valeur (i.e. n'a pas une valeur exclue)
    def totalVarsDefiniesTypeNom(self,
                                 indexNom, indexesVars, tp):
        trueVars = self.indexesVarsDefiniesTypeNom(indexNom, indexesVars, tp)
        return len(trueVars)

    # variables d'un type donné pour lesquelles les éditions d'une liste ont une vraie valeur (i.e. n'a pas une valeur exclue)
    def indexesVarsDefiniesType(self,
                                indexesNoms, indexesVars, tp):
        trueVars = []
        for n in indexesNoms:
            trueVars += self.indexesVarsDefiniesTypeNom(n, indexesVars, tp)

        trueVars = sorted(list(set(trueVars)))
        return trueVars

    # nombre de variables d'un type donné pour lesquelles l'édition a une vraie valeur (i.e. n'a pas une valeur exclue)
    def totalVarsDefiniesType(self,
                              indexesNoms, indexesVars, tp):
        trueVars = self.indexesVarsDefiniesType(indexesNoms, indexesVars, tp)
        return len(trueVars)


    def varToTypes(self, var):
        tps = [tp for tp in self.__vars_types_types if var in self.typeToVars(tp)]
        return tps

    def varToindexesTypes(self, var):
        indexesTypes = [self.__vars_types_types.index(tp) \
                        for tp in self.__vars_types_types \
                        if var in self.typeToVars(tp)]
        return indexesTypes

    # types d'une variable
    def show_var_types(self, var):
        types = self.varToTypes(var)
        typesL = [[tp] for tp in types]

        display(pd.DataFrame(typesL, columns=[var]))

    # variables d'un type donné
    def show_vars_type(self, tp):
        varsT = self.typeToVars(tp)
        print('Variables : ' + str(len(varsT)))
        display(pd.DataFrame(columns=[tp + ':'] + varsT))

    def indexVarToTypes(self, indexVar):
        return self.varToTypes(self.__vars[indexVar])

    def indexVarToIndexesTypes(self, indexVar):
        indexesTypes = [self.__vars_types_types.index(tp) \
                        for tp in self.__vars_types_types \
                        if indexVar in self.typeToIndexesVars(tp)]
        return indexesTypes

    def indexesVarsToIndexesTypes(self, indexesVars):
        indexesTypes = []
        for v in indexesVars:
            indexesTypes += self.indexVarToIndexesTypes(v)

        indexesTypes = sorted(list(set(indexesTypes)))
        return indexesTypes

    def indexesVarsToDictTypesIndexesVars(self,
                                          indexesVars, indexesVarsTypes):
        types = defaultdict(list)
        #On met dans le dictionnaire des types les types dans indexesVarsTypes
        for t in indexesVarsTypes :
            types[self.__vars_types_types[t]]=[]

        for v in indexesVars:
            for tp in self.indexVarToTypes(v):
                types[tp].append(v)
        return types

    def indexesVarsToDictTypesVars(self, indexesVars):
        types = defaultdict(list)

        for v in indexesVars:
            for tp in self.indexVarToTypes(v):
                types[tp].append(self.__vars[v])
        return types

        # indexes des variables pour lesquelles une liset a des valeurs

    def lisetToIndexesVars(self, liset, indexesVars):
        indexesVars = [indexesVars[i] for i in range(len(indexesVars)) \
                       if len(liset[i] - set(self.__exclus))]
        return indexesVars

    ## Doublon
        # def typeToIndexesVars(self,
        #                  tp, indexesVars):
        # indexesVarsType = [v for v in indexesVars if v in self.typeToIndexesVars(tp)]
        # return indexesVarsType

    def indexTypeToIndexesVars(self, indexType):

        indexesVarsType = [self.varToIndex(self.__vars_types_vars[i]) for i in range(len(self.__vars_types_vars)) if
                           self.__vars_types_data[indexType][i] in self.__coches]
        return indexesVarsType

    def typeToIndexesVars(self, tp):
        try:
            indexType = self.__vars_types_types.index(tp)
        except:
            print("Le type \"" + tp + "\" n'est pas reconnu")
            sys.exit(1)

        indexesVarsType = [self.varToIndex(self.__vars_types_vars[i]) for i in range(len(self.__vars_types_vars)) if
                           self.__vars_types_data[indexType][i] in self.__coches]
        return indexesVarsType

    def typesToIndexesVars(self, tps):
        indexesVars = []
        for tp in tps:
            indexesVars += self.typeToIndexesVars(tp)
        indexesVars = sorted(list(set(indexesVars)))
        return indexesVars

    def typeToVars(self, tp):
        try:
            indexType = self.__vars_types_types.index(tp)
        except:
            print("Le type \"" + tp + "\" n'est pas reconnu")
            sys.exit(1)

        varsType = [self.__vars_types_vars[i] for i in range(len(self.__vars_types_vars)) if
                    self.__vars_types_data[indexType][i] in self.__coches]
        return varsType

    def typesToVars(self, tps):
        if not type(tps) == list:
            tps = list(tps)

        indexesVarsTypes = []
        for tp in tps:
            indexesVarsTypes += self.typeToIndexesVars(tp)

        indexesVarsTypes = sorted(list(set(indexesVarsTypes)))
        varsTypes = [self.__vars[i] for i in indexesVarsTypes]
        return varsTypes

    # retourne la liste des valeurs (avec répétition) d'une édition
    # pour une liste d'indexes de variable donnée
    def indexesVarsToValsSimple(self, indexNom, indexesVars):
        values = [str(self.__data[indexNom][v]) for v in indexesVars]
        return sorted(values)

    def indexesVarsToVals(self, indexesNoms, indexesVars):
        values = [str(self.__data[n][v]) for v in indexesVars for n in indexesNoms]
        return sorted(values)

    # retourne la liste des valeurs (avec répétition) d'une édition
    # sur les variables d'un même type
    def typeToVals(self, indexNom, tp):
        indexesVarsType = self.typeToIndexesVars(tp)
        values = [str(self.__data[indexNom][v]) for v in indexesVarsType]
        return sorted(values)

    def indexesTypesToIndexesVars(self, indexesVarsTypes):
        types = [self.__vars_types_types[i] for i in indexesVarsTypes]
        return self.typesToIndexesVars(types)

    ##indexes des variables d'un type, parmi une liste d'indexes de variables,
    # sur lesquelles deux éditions données
    # ont des valeurs définies
    def indexesVarsDefiniesConjointesType(self,
                                          indexNom1, indexNom2, tp, indexesVars):
        indexesVarsDef = []
        indexesV = list(set(self.typeToIndexesVars(tp)).intersection(set(indexesVars)))
        for i in indexesV:
            if self.__data[indexNom1][i] not in self.__exclus and \
                    self.__data[indexNom2][i] not in self.__exclus:
                indexesVarsDef.append(i)

        return indexesVarsDef

    ##nombre de variables d'un type, parmi une liste d'indexes de variables,
    # sur lesquelles deux éditions données
    # ont des valeurs définies
    def totalVarsDefiniesConjointesType(self,
                                        indexNom1, indexNom2, tp, indexesVars):
        indexesVarsDef = self.indexesVarsDefiniesConjointesType(
            indexNom1, indexNom2, tp, indexesVars)
        return len(indexesVarsDef)

    def varsTypesToIndexesTypes(self,
                                varsTypes, varsTypeSauf):

        for tp in varsTypes:
            try:
                v = self.__vars_types_types.index(tp)
            except:
                print(color.bold + "Le type \"", tp, "\" n'est pas reconnu." + color.end)
                sys.exit(1)

        if len(varsTypes) == 0: varsTypes = self.__vars_types_types

        indexesVarsTypes = [self.__vars_types_types.index(v) for v in varsTypes if v not in varsTypeSauf]
        indexesVarsTypes = sorted(list(set(indexesVarsTypes)))
        return indexesVarsTypes

    # reduit un tableau sur l'ensemble des types au tableau sur
    # une liste de types donnés
    # il peut y avoir d'autre données au début, start est l'indice du premier type
    def reduceLinesByVarsTypes(self, lines, varsTypes, start=0):
        redLines = []
        for line in lines:
            redLine = line[0:start]
            for tp in varsTypes:
                print('line : ', line, ' - indexe du type ',
                      self.__vars_types_types.index(tp), ' valeur : ',
                      line[start + self.__vars_types_types.index(tp)])
                redLine.append(line[start + self.__vars_types_types.index(tp)])
            redLines.append(redLine)
        return redLines

    # Affiche  le nombres de valeurs égales d'une liste d'éditions
    # sur les variables indiquées
    def show_coherence(self, noms=None, nomSauf=None, vars=None, varSauf=None,
                                varsTypes=None, varsTypeSauf=None, varsTypesFormule='',
                                nomsTypes=None, nomsTypeSauf=None, nomsTypesFormule='',
                                pasColonne=10, pasLigne=10):

        if nomsTypeSauf is None:
            nomsTypeSauf = []
        if nomsTypes is None:
            nomsTypes = []
        if varsTypeSauf is None:
            varsTypeSauf = []
        if varsTypes is None:
            varsTypes = []
        if varSauf is None:
            varSauf = []
        if vars is None:
            vars = []
        if nomSauf is None:
            nomSauf = []
        if noms is None:
            noms = []
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        resNoms = [self.__noms[i] for i in indexesNoms]
        valuesCompletes = self.indexesVarsToVals(indexesNoms, indexesVars)

        total = len(indexesVars)
        valsCompletes = sorted(list(set(valuesCompletes)))
        lines = []
        for n in indexesNoms:
            cardValues = []
            values = self.indexesVarsToVals([n], indexesVars)
            for val in valsCompletes:
                card = values.count(val)
                cardValues.append(card)
            lines.append(cardValues)

        listVars = ['Variables'] + [self.__vars[v] for v in indexesVars]
        print('Variables : ' + str(len(indexesVars)))
        display(pd.DataFrame(columns=listVars))
        display(pd.DataFrame(lines, columns=valsCompletes, index=resNoms))

        # Affiche  le pourcentage de valeurs égales d'une liste d'éditions
        # sur les variables indiquées
    def show_coherence_pourcent(self, noms=None, nomSauf=None, vars=None, varSauf=None,
                  varsTypes=None, varsTypeSauf=None, varsTypesFormule='',
                  nomsTypes=None, nomsTypeSauf=None, nomsTypesFormule='',
                  pasColonne=10, pasLigne=10) :

        if nomsTypeSauf is None:
            nomsTypeSauf = []
        if nomsTypes is None:
            nomsTypes = []
        if varsTypeSauf is None:
            varsTypeSauf = []
        if varsTypes is None:
            varsTypes = []
        if varSauf is None:
            varSauf = []
        if vars is None:
            vars = []
        if nomSauf is None:
            nomSauf = []
        if noms is None:
            noms = []
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        resNoms = [self.__noms[i] for i in indexesNoms]
        valuesCompletes = self.indexesVarsToVals(indexesNoms,indexesVars)

        total = len(indexesVars)
        valsCompletes = sorted(list(set(valuesCompletes)))
        lines = []
        for n in indexesNoms :
            pourcent = []
            values = self.indexesVarsToVals([n],indexesVars)
            for val in valsCompletes:
                card = values.count(val)
                pourcent.append(round(card / total * 100))
            lines.append(pourcent)

        listVars = ['Variables'] + [self.__vars[v] for v in indexesVars]
        print('Variables : ' + str(len(indexesVars)))
        display(pd.DataFrame(columns=listVars))
        display(pd.DataFrame(lines, columns=valsCompletes, index=resNoms))

    # Affiche le nombre et le pourcentages de valeurs égales d'une édition
    # sur les variables d'un même type
    def show_coherence_type(self, nom, tp):
        indexNom = self.nomToIndex(nom)
        values = self.typeToVals(indexNom, tp)
        indexesVars = self.typeToIndexesVars(tp)
        total = len(indexesVars)
        vals = sorted(list(set(values)))
        effectifs = [total]
        pourcent = ['']
        for val in vals:
            effectifs.append(values.count(val))
            pourcent.append(round(values.count(val) / total * 100))

        print(color.bold + nom + ': ' + tp + color.end)
        display(pd.DataFrame([effectifs, pourcent], columns=['total'] + vals, index=['effectifs', '%']))

    # Affiche le nombre et le pourcentages de valeurs égales d'une édition
    # sur les variables d'une liste de types
    def show_coherence_types(self, nom, varsTypes):
        for tp in varsTypes:
            self.show_coherence_type(nom, tp)

    ##########################################################################################
    ### types noms
    ##########################################################################################

    def set_noms_types(self, fileIn, nomsTypesRegles='',
                       pasColonne=10, pasLigne=10):
        if type(fileIn) == str: fileIn = [fileIn]
        fr = pd.DataFrame([])
        types = []
        for f in fileIn:
            try:
                ar = np.array(pd.read_csv(open(f,encoding="UTF-8"), delimiter=","))
            except:
                print("Impossible d\'ouvrir le fichier des types \"" + f + "\"")
                sys.exit(1)
            # Suppression des colonnes (resp. lignes) dont le nom est vide
            j = 1
            while j < np.size(ar, 1):
                if str(ar[0, j]) == 'nan':
                    ar = np.delete(ar, j, 1)
                else:
                    j += 1
            i = 2
            while i < np.size(ar, 0):
                if str(ar[i, 0]) == 'nan':
                    ar = np.delete(ar, i, 0)
                else:
                    i += 1

            index = ar[1:, 0].tolist()
            cols = ar[0, 1:].tolist()
            ar = ar[1:, 1:]
            fr_new = pd.DataFrame(ar, index=index, columns=cols)
            fr = pd.concat([fr_new, fr], axis=1)
            # pour préserver l'ordre des types
            types = types + [str(x) for x in cols if x not in types]

        # remplace les nan par des ''
        fr = pd.DataFrame(fr).replace(np.nan, '')

        noms = [str(x) for x in fr.index.tolist()]

        # noms sans types et noms typées non reconnues
        nomsTypesError = sorted(list(set(noms) - set(self.__noms)))
        nomSansType = sorted(list(set(self.__noms) - set(noms)))

        if nomsTypesError:
            print('')
            print('')
            print(color.bold + str(len(nomsTypesError)) + ' noms typées non reconnus : ' + color.end)
            display(pd.DataFrame(columns=nomsTypesError))

        if nomSansType:
            print('')
            print('')
            print(color.bold + str(len(nomSansType)) + ' noms ayant des valeurs sans type : ' + color.end)
            display(pd.DataFrame(columns=nomSansType))

        if nomsTypesError or nomSansType: sys.exit(1)

        # L'ensemble des noms des tableaux de valeurs et des types coïncident
        # contrôle des doublons
        if len(noms) != len(set(self.__noms)):
            print(color.bold + 'Noms répétés :' + color.end)
            doubles = [item for item, count in collections.Counter(noms).items() if count > 1]
            print('')
            print(','.join(map(str, doubles)))
            sys.exit(1)

        # réordonnement des variables des types
        fr = fr[types]
        # réordonnement des types
        fr = fr.reindex(index=noms)

        ar = fr.values
        self.__noms_types_data = ar.tolist()
        self.__noms_types_noms = fr.index.tolist()
        self.__noms_types_types = [tp for tp in types if not tp == '']

        # application des règles
        if nomsTypesRegles:
            try:
                array_regles = np.array(pd.read_csv(open(nomsTypesRegles,encoding="UTF-8"), delimiter=","))
            except:
                print("Impossible d\'ouvrir le fichier des règles \"" + f + "\"")
                sys.exit(1)
            ar = pd.DataFrame(array_regles).replace(np.nan, '')

            reglesListe = ar.values
            # dictionnaire des règles : type : règle
            regles = {r[0]: r[1] for r in reglesListe}
            self.__noms_types_data = self.applyRegles(self.__noms_types_data,
                                                      self.__noms_types_types,
                                                      regles)
    def show_noms_types(self,pasColonne=10,pasLigne=10):
        print(color.bold + 'Tableau des types de noms : ' + color.end)

        lines = self.__noms_types_data
        index = self.__noms_types_noms
        columns = self.__noms_types_types
        if pasColonne:
            res = self.repeteIndex(pasColonne, lines, columns, index)
            lines = res[0]
            columns = res[1]

        if pasLigne:
            res = self.repeteColumns(pasLigne, lines, columns, index)
            lines = res[0]
            index = res[1]

        display(pd.DataFrame(lines, columns=columns, index=index))

    def nomToTypes(self, var):
        tps = [tp for tp in self.__noms_types_types if var in self.typeToNoms(tp)]
        return tps

    def nomToindexesTypes(self, nom):
        indexesTypes = [self.__noms_types_types.index(tp) \
                        for tp in self.__noms_types_types \
                        if var in self.typeToNoms(tp)]
        return indexesTypes

    # types d'un nom
    def show_nom_types(self, nom):
        types = self.nomToTypes(nom)
        typesL = [[tp] for tp in types]

        display(pd.DataFrame(typesL, columns=[var]))

    # variables d'un type donné
    def show_noms_type(self, tp):
        nomsT = self.typeToNoms(tp)
        print('Noms : ' + str(len(nomsT)))
        display(pd.DataFrame(columns=[tp + ':'] + nomsT))

    def indexNomToTypes(self, indexNom):
        return self.nomToTypes(self.__noms[indexNom])

    def indexNomToIndexesTypes(self, indexNom) :
        indexesTypes = [self.__noms_types_types.index(tp) \
                        for tp in self.__noms_types_types \
                        if indexNom in self.typeToIndexesNoms(tp)]
        return indexesTypes

    def indexesNomsToIndexesTypes(self, indexesNoms):
        indexesTypes = []
        for v in indexesNoms:
            indexesTypes += self.indexNomToIndexesTypes(v)

        indexesTypes = sorted(list(set(indexesTypes)))
        return indexesTypes

    def indexesNomsToDictTypesIndexesNoms(self,
                                          indexesNoms, indexesNomsTypes) :
        types = defaultdict(list)

        for v in indexesNoms:
            for tp in self.indexNomToTypes(v):
                types[tp].append(v)
        return types


    def indexesNomsToDictTypesNoms(self, indexesNoms):
        types = defaultdict(list)

        for v in indexesNoms:
            for tp in self.indexNomToTypes(v):
                types[tp].append(self.__noms[v])
        return types

        # indexes des variables pour lesquelles une liset a des valeurs

    def lisetToIndexesNoms(self, liset, indexesNoms):
        indexesNoms = [indexesNoms[i] for i in range(len(indexesNoms)) \
                       if len(liset[i] - set(self.__exclus))]
        return indexesNoms

    def typeToIndexesNoms(self, tp):
        try:
            indexType = self.__noms_types_types.index(tp)
        except:
            print("Le type \"" + tp + "\" n'est pas reconnu")
            sys.exit(1)
        for i in range(len(self.__noms_types_noms)) :
            indexesNomsType = [self.nomToIndex(self.__noms_types_noms[i]) for i in range(len(self.__noms_types_noms)) if
                           self.__noms_types_data[i][indexType] in self.__coches]
        return indexesNomsType

    def typesToIndexesNoms(self, tps):
        indexesNoms = []
        for tp in tps:
            indexesNoms += self.typeToIndexesNoms(tp)
        indexesNoms = sorted(list(set(indexesNoms)))
        return indexesNoms

    def typeToNoms(self, tp):
        try:
            indexType = self.__noms_types_types.index(tp)
        except:
            print("Le type \"" + tp + "\" n'est pas reconnu")
            sys.exit(1)

        nomsType = [self.__noms_types_noms[i] for i in range(len(self.__noms_types_noms)) if
                    self.__noms_types_data[indexType][i] in self.__coches]
        return nomsType


    def typesToNoms(self, tps):
        if not type(tps) == list:
            tps = list(tps)

        indexesNomsTypes = []
        for tp in tps:
            indexesNomsTypes += self.typeToIndexesNoms(tp)

        indexesNomsTypes = sorted(list(set(indexesNomsTypes)))
        nomsTypes = [self.__noms[i] for i in indexesNomsTypes]
        return nomsTypes

    def indexes_noms_type(self, tp):
        try:
            indexType = self.__noms_types_types.index(tp)
        except:
            print("Le type \"" + tp + "\" n'est pas reconnu")
            sys.exit(1)

        indexesNomsType = [self.nomToIndex(self.__noms_types_noms[i]) \
                           for i in range(len(self.__noms_types_noms)) \
                           if self.__noms_types_data[i][indexType] in self.__coches]
        return indexesNomsType

    def indexesTypesToIndexesNoms(self, indexesNomsTypes):
        types = [self.__noms_types_types[i] for i in indexesNomsTypes]
        return self.typesToIndexesNoms(types)

    def nomsTypesToIndexesTypes(self,
                                nomsTypes, nomsTypeSauf):

        for tp in nomsTypes:
            try:
                v = self.__noms_types_types.index(tp)
            except:
                print(color.bold + "Le type \"", tp, "\" n'est pas reconnu." + color.end)
                sys.exit(1)

        if len(nomsTypes) == 0: nomsTypes = self.__noms_types_types

        indexesNomsTypes = [self.__noms_types_types.index(v) for v in nomsTypes if v not in nomsTypeSauf]
        indexesNomsTypes = sorted(list(set(indexesNomsTypes)))
        return indexesNomsTypes

    # reduit un tableau sur l'ensemble des types au tableau sur
    # une liste de types donnés
    # il peut y avoir d'autre données au début, start est l'indice du premier type
    def reduceLinesByNomsTypes(self, lines, nomsTypes, start=0):
        redLines = []
        for line in lines:
            redLine = line[0:start]
            for tp in nomsTypes:
                print('line : ', line, ' - indexe du type ',
                      self.__noms_types_types.index(tp), ' valeur : ',
                      line[start + self.__noms_types_types.index(tp)])
                redLine.append(line[start + self.__noms_types_types.index(tp)])
            redLines.append(redLine)
        return redLines

    def typeToNom(self, tp):
        try:
            indexType = self.__noms_types_types.index(tp)
        except:
            print("Le type \"" + tp + "\" n'est pas reconnu")
            sys.exit(1)

        nomsType = [self.__noms_types_vars[i] \
                    for i in range(len(self.__noms_types_noms)) \
                    if self.__noms_types_data[indexType][i] in self.__coches]
        return nomsType

    def typesToNoms(self, tps):
        if not type(tps) == list:
            tps = list(tps)

        indexesNomsTypes = []
        for tp in tps:
            indexesNomsTypes += self.indexes_noms_type(tp)

        indexesNomsTypes = sorted(list(set(indexesNomsTypes)))
        nomsTypes = [self.__noms[i] for i in indexesNomsTypes]
        return nomsTypes

    def nomsTypesToIndexesNomsTypes(self,
                                    nomsTypes, nomsTypeSauf):

        if type(nomsTypes) == str:
            try:
                v = self.__noms.index(nomsTypes)
            except:
                print(color.bold + "Le type \"", nomsTypes, "\" n'est pas reconnu." + color.end)
                sys.exit(color.bold + "Le type \"", nomsTypes, "\" n'est pas reconnu." + color.end)
            nomsTypes = [nomsTypes]

        if len(nomsTypes) == 0: nomsTypes = self.__noms_types_types

        indexesNomsTypes = [self.__noms_types_types.index(n) for n in nomsTypes if n not in nomsTypeSauf]
        return indexesNomsTypes

    ##########################################################################################
    ### Formules de types
    ### pour les variables
    ##########################################################################################

    def orVarsTypes(self, f, *args):
        self.f = f
        args = list(args)
        a = args.pop(0)
        if not type(a) == list:
            res = set(self.f(a))
        else:
            res = set(a)

        while args:
            b = args.pop(0)
            if not type(b) == list:
                b = self.f(b)
            res = res.union(set(b))
        return sorted(list(res))

    def andVarsTypes(self, f, *args):
        self.f = f
        args = list(args)
        a = args.pop(0)
        if not type(a) == list:
            res = set(self.f(a))
        else:
            res = set(a)

        while args:
            b = args.pop(0)
            if not type(b) == list:
                b = self.f(b)
            res = res.intersection(set(b))
        return sorted(list(res))

    def notVarsTypes(self, f, a):
        self.f = f
        if not type(a) == list:
            a = set(self.f(a))
        else:
            a = set(a)
        neg = [v for v in range(len(self.__vars)) if not v in a]
        return sorted(neg)

    # Etant donnée une formule propositionnelle sur les types,
    # retourne les variables correspondantes
    def varsTypesFormulaToIndexesVars(self, f, expr):
        import re
        # suppression des opérateurs unaires
        pat = "|".join(["\s*\\" + op + '\s*' for op in self.__logicalOperatorsUnary])
        reg = re.compile(pat)
        exprReduite = reg.sub('', expr)
        # suppression des parenthèses
        pat = "\s*\(\s*"
        reg = re.compile(pat)
        exprReduite = reg.sub('', exprReduite)
        pat = "\s*\)\s*"
        reg = re.compile(pat)
        exprReduite = reg.sub('', exprReduite)
        # extraction des types
        pat2 = "|".join(["\s*\\" + op + '\s*' for op in self.__logicalOperatorsBinary])
        listTypes = re.split(pat2, exprReduite)
        indexesTypes = self.varsTypesToIndexesTypes(listTypes, [])
        # Problème des types qui sont des sous-chaînes d'un type...
        # substitution des types par des symboles : type i -> xi
        numbered_symbols(prefix='x', start=0)
        exprS = expr
        for i in indexesTypes:
            pat = "\s*" + self.__vars_types_types[i] + "\s*"
            reg = re.compile(pat)
            exprS = reg.sub('x' + str(i), exprS)
        exprSymb = sympify(exprS)

        if exprSymb.is_Atom:
            return self.indexTypeToIndexesVars(indexesTypes[0])
        else:
            sexpr = srepr(exprSymb)
            sexpr = sexpr.replace('Or(', 'self.orVarsTypes(' + f + ',')
            sexpr = sexpr.replace('And(', 'self.andVarsTypes(' + f + ',')
            sexpr = sexpr.replace('Not(', 'self.notVarsTypes(' + f + ',')

            for i in indexesTypes:
                sexpr = sexpr.replace("Symbol('x" + str(i) + "')", "'" + self.__vars_types_types[i] + "'")
            return eval(sexpr)

    def varsTypesFormulaToVars(self, f, expr):
        indexesVars = self.varsTypesFormulaToIndexesVars(f, expr)
        vars = [self.__vars[i] for i in indexesVars]
        return vars


    ##########################################################################################
    ### Formules de types
    ### pour les noms
    ##########################################################################################

    def notNomsTypes(self, f, a):
        self.f = f
        if not type(a) == list:
            a = set(self.f(a))
        else:
            a = set(a)
        neg = [v for v in range(len(self.__noms)) if not v in a]
        return sorted(neg)

        # Etant donnée une formule propositionnelle sur les types,
        # retourne les noms correspondants
    def nomsTypesFormulaToIndexesNoms(self, f, expr):
                import re
                # suppression des opérateurs unaires
                pat = "|".join(["\s*\\" + op + '\s*' for op in self.__logicalOperatorsUnary])
                reg = re.compile(pat)
                exprReduite = reg.sub('', expr)
                # suppression des parenthèses
                pat = "\s*\(\s*"
                reg = re.compile(pat)
                exprReduite = reg.sub('', exprReduite)
                pat = "\s*\)\s*"
                reg = re.compile(pat)
                exprReduite = reg.sub('', exprReduite)
                # extraction des types
                pat2 = "|".join(["\s*\\" + op + '\s*' for op in self.__logicalOperatorsBinary])
                listTypes = re.split(pat2, exprReduite)
                indexesTypes = self.nomsTypesToIndexesTypes(listTypes, [])

                # Problème des types qui sont des sous-chaînes d'un type...

                # substitution des types par des symboles : type i -> xi
                numbered_symbols(prefix='x', start=0)
                exprS = expr
                for i in indexesTypes:
                    pat = "\s*" + self.__noms_types_types[i] + "\s*"
                    reg = re.compile(pat)
                    exprS = reg.sub('x' + str(i), exprS)
                exprSymb = sympify(exprS)

                if exprSymb.is_Atom:
                    return self.typeToIndexesNoms(self.__noms_types_types[indexesTypes[0]])
                else:
                    sexpr = srepr(exprSymb)
                    sexpr = sexpr.replace('Or(', 'self.orVarsTypes(' + f + ',')
                    sexpr = sexpr.replace('And(', 'self.andVarsTypes(' + f + ',')
                    sexpr = sexpr.replace('Not(', 'self.notNomsTypes(' + f + ',')

                    for i in indexesTypes:
                        sexpr = sexpr.replace("Symbol('x" + str(i) + "')", "'" + self.__noms_types_types[i] + "'")
                    return eval(sexpr)

    def nomsTypesFormulaToNoms(self, f, expr):
        indexesNoms = self.nomsTypesFormulaToIndexesNoms(f, expr)
        noms = [self.__noms[i] for i in indexesNoms]
        return noms

    ##########################################################################################
    ### Recherches dans tableau
    ##########################################################################################

    def findVarsIndexes(self,
                        cars, indexesVars):
        if type(cars) == list:
            indexes = []
            for c in cars:
                indexes = indexes + self.findVarsIndexes(c, indexesVars)

            indexes = sorted(list(set(indexes)))
            return indexes


        else:
            indexes = [v for v in indexesVars if
                       str(cars).lower() in str(self.__vars[v]).lower()]
            return indexes

    def findVars(self,
                 cars, vars=[], varSauf=[]):
        indexesVars = self.varsToIndexesVars(vars, varSauf)

        indexes = self.findVarsIndexes(cars, indexesVars)
        listVars = [self.__vars[i] for i in indexes]
        return listVars

    def findNomsIndexes(self,
                        cars, indexesNoms):
        if type(cars) == list:
            indexes = []
            for c in cars:
                indexes = indexes + self.findNomsIndexes(c, indexesNoms)

            indexes = sorted(list(set(indexes)))
            return indexes


        else:
            indexes = [v for v in indexesNoms if
                       str(cars).lower() in str(self.__noms[v]).lower()]
            return indexes

    def findNoms(self,
                 cars, noms=[], nomSauf=[]):
        indexesNoms = self.nomsToIndexesNoms(noms, nomSauf)

        indexes = self.findNomsIndexes(cars, indexesNoms)
        listNoms = [self.__noms[i] for i in indexes]
        return listNoms

    # Recherche les variables ayant une valeur donnée d'une édition
    def findVarsValue(self,
                      nom, cars,
                      vars=[], varSauf=[],
                      varsTypes=[], varsTypeSauf=[],
                      varsTypesFormule='',
                      nomsTypes=[], nomsTypeSauf=[]):

        indexNom = self.nomToIndex(nom)
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

        listVars = [self.__vars[i] for i in indexesVars if str(cars).lower() in str(self.__data[indexNom][i]).lower()]
        return listVars

    # Recherche les éditions ayant une valeur donnée
    def find(self,
             val, listVars):
        """
        val : str, chaîne recherchée
        var : int ou str. Si str cherche les critères contenant str.
        """
        # if type(indexesVars)==int and indexesVars in self.__selectedIndexesVars :
        #   indexesVars=[indexesVars]

        # cas où un index est donné
        if type(listVars) == int: listVars = [self.indexToVar(listVars)]

        for var in listVars:
            print(color.bold + var.replace('\n', ' ') + " : " + color.end)
            res = [self.__noms[i] for i in self.__selectedIndexesNoms if self.__data[i][self.varToIndex(var)] == val]
            print(res)
            print()

    # Liste des indexes des éditions ayant les mêmes valeurs qu'une édition donnée, à un pourcentage près,
    # sur un domaine de variables donné
    def indexes_like(self,
                     indexNom, indexesNoms, indexesVars, pourcent):
        # print(color.bold+str(self.__vars[start-1]).replace('\n',' ')+ ", précision "+str(pourcent)+"% : "+color.end)

        indexesNomsRes = [i for i in indexesNoms if \
                          self.listsEqual(self.__data[indexNom], self.__data[i], indexesVars, pourcent)]

        return indexesNomsRes

    # Liste des indexes des éditions ayant les mêmes valeurs qu'une édition donnée, à un pourcentage près,
    # sur un domaine de variables donné
    def like(self,
             nom, noms=[], nomSauf=[],
             vars=[], varSauf=[],
             varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
             nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
             pourcent=100):
        # print(color.bold+str(self.__vars[start-1]).replace('\n',' ')+ ", précision "+str(pourcent)+"% : "+color.end)

        try:
            indexNom = self.__noms.index(nom)
        except:
            print(color.bold + "Le nom \"" + nom + "\" ne fait pas partie des noms reconnus." + color.end)
            sys.exit(1)

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesVars = self.indexesVarsDefiniesNom(indexNom, indexesVars)

        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        indexesNomsRes = self.indexes_like(indexNom, indexesNoms, indexesVars, pourcent)
        nomsRes = [self.indexToNom(n) for n in indexesNomsRes]
        return nomsRes

    # Recherche les éditions ayant les mêmes valeurs qu'une édition donnée, à un pourcentage près,
    # sur un domaine de variables donné par leur nom
    def show_like(self,
                  nom, noms=[], nomSauf=[],
                  vars=[], varSauf=[],
                  varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                  nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                  pourcent=0):

        try:
            indexNom = self.__noms.index(nom)
        except:
            print(color.bold + "Le nom \"" + nom + "\" ne fait pas partie des noms reconnus." + color.end)
            sys.exit(1)

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesVars = self.indexesVarsDefiniesNom(indexNom, indexesVars)

        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        indexesNomsRes = self.indexes_like(indexNom, indexesNoms, indexesVars, pourcent)

        resNomsLignes = [
            [self.__noms[i]] + self.stats(self.communs(indexNom, i, indexesVars), indexesVars) + [self.__data[i][k] for
                                                                                                  k in indexesVars] for
            i in indexesNomsRes]
        resNomsLignes = sorted(resNomsLignes, key=itemgetter(1), reverse=True)
        resNoms = []
        resLignes = []
        for L in resNomsLignes:
            resNoms.append(L[0])
            del L[0]
            resLignes.append(L)

        resVars = ['%', 'total\ncommuns'] + [self.__vars[i] for i in indexesVars]

        display(pd.DataFrame(resLignes, columns=resVars, index=resNoms))

    # indexes des variables pour lesquelles les valeurs manquent
    def manque(self, indexesVars, indexNom):
        return [i for i in indexesVars if self.__data[indexNom][i] in ['','?']]


    def show_manque(self, nom,
                    vars=[], varSauf=[],
                    varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                    pasColonne=10):
        indexNom = self.nomToIndex(nom)
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesVarsManque = self.manque(indexesVars, indexNom)
        varsManque=[self.indexToVar(v) for v in indexesVarsManque]

        print('Valeurs manquantes pour '+nom+' : ' + str(len(varsManque)))
        display(pd.DataFrame(columns=varsManque))

    # Regroupe les éditions ayant les mêmes valeurs sur un ensemble de variable donné
    def repartitionList(self,
                        indexesVars, indexesNoms):
        """
        val : str, chaîne recherchée
        var : int ou str. Si str cherche les critères contenant str.
        """
        # if type(indexesVars)==int and indexesVars in self.__selectedIndexesVars :
        #   indexesVars=[indexesVars]

        indexesEditions = [] + indexesNoms
        resultats = []
        # Valeurs des critères ayant des éditions ayant ces valeurs
        while indexesEditions:
            indexEdition = indexesEditions[0]
            resIndexesNoms = self.indexes_like(indexEdition, indexesNoms, indexesVars, 100)
            resVals = [self.__data[indexEdition][j] for j in indexesVars]
            indexesEditions = [i for i in indexesEditions if i not in resIndexesNoms]
            resultats.append([[self.indexToNom(i) for i in resIndexesNoms], resVals])

        return resultats

    def show_repartition(self,
                         vars=[], varSauf=[],
                         noms=[], nomSauf=[],
                         varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                         nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        listVars = [self.__vars[v] for v in indexesVars]
        partitions = self.repartitionList(indexesVars, indexesNoms)
        res = [couple[1] + [", ".join(couple[0])] for couple in partitions]
        display(pd.DataFrame(res, columns=listVars + ['noms']))

    def contains(self,
                 chain, vars=[], varSauf=[],
                 noms=[], nomSauf=[],
                 varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                 nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        resData = []
        resNoms = []
        for i in indexesNoms:
            l = []
            ok = False
            for v in indexesVars:
                if str(chain).lower() in \
                        str(self.__data[i][v]).replace('[', '').replace(']', '').lower():
                    l.append(self.__data[i][v])
                    ok = True
                else:
                    l.append('')
            if ok:
                resData.append(l)
                resNoms.append(self.__noms[i])

        resVars = [self.__vars[i] for i in indexesVars]

        return pd.DataFrame(resData, columns=resVars, index=resNoms)

    def decomposition(self,
                      indexNom, indexesNomsBaseIncomplete, indexesVars, indexesNoms, max, pourcent, Pourcent):

        decomp = []
        prcs = []
        indexesNomsReste = list(set(indexesNoms) - set(indexesNomsBaseIncomplete))
        if not max: max = len(indexesNoms)

        for indexes in tqdm(sorted(getCombinations(indexesNomsReste,
                                                   max - len(indexesNomsBaseIncomplete)), key=len)):

            if not includes(indexes, decomp):
                # print('indexes : ',indexesNoms)
                ListeL = [self.__data[i] for i in indexes + indexesNomsBaseIncomplete]
                prc = self.sumEqualPourcent(ListeL, self.__data[indexNom], indexesVars)
                if pourcent <= prc <= Pourcent:
                    prcs.append(prc)
                    decomp.append(indexes)

        return [prcs, decomp]

    def show_decomposition(self,
                           nom,
                           nomsBaseIncomplete=[], nomsBaseIncompleteSauf=[],
                           vars=[], varSauf=[],
                           noms=[], nomSauf=[],
                           max=0, pourcent=100, Pourcent=100,
                           varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                           nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                           pasColonne=10, pasLigne=10):

        indexNom = self.nomToIndex(nom)
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesVars = self.indexesVarsDefiniesNom(indexNom, indexesVars)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        if nomsBaseIncomplete or nomsBaseIncompleteSauf:
            indexesNomsBaseIncomplete = self.nomsToIndexesNoms(nomsBaseIncomplete, nomsBaseIncompleteSauf)
        else:
            indexesNomsBaseIncomplete = []

        if indexNom in indexesNoms: indexesNoms.remove(indexNom)

        if max == 0:
            max = 4
            print("Le nombre de termes d'une décomposition a été limité à 4.")

        resDecomp = self.decomposition(indexNom,
                                       indexesNomsBaseIncomplete,
                                       indexesVars,
                                       indexesNoms,
                                       max,
                                       pourcent,
                                       Pourcent)
        prcs = resDecomp[0]
        decomp = resDecomp[1]

        resVars = ['%'] + [self.__vars[i] for i in indexesVars]
        print('Variables : ' + str(len(resVars)))

        if not len(decomp) == 0:
            for i in range(len(decomp)):
                indexes = decomp[i]
                prcTotal = prcs[i]
                ligne = [100] + [self.__data[indexNom][j] for j in indexesVars]
                resData = [ligne]
                # Ajout des indexes des noms de la base incomplète
                indexesComplet = sorted(indexesNomsBaseIncomplete + indexes)
                for i in indexesComplet:
                    prc = self.listsEqualPourcent(self.__data[indexNom], self.__data[i], indexesVars)
                    ligne = [prc]
                    for j in indexesVars:
                        if self.equal(self.__data[i][j], self.__data[indexNom][j]):
                            ligne.append('')
                        else:
                            ligne.append(self.__data[i][j])
                    resData.append(ligne)

                resNoms = [self.__noms[i] for i in indexesComplet]
                lines = resData
                columns = resVars
                index = [nom] + resNoms
                print('')
                print(color.bold + str(prcTotal) + "% : " + ', '.join(resNoms) + color.end)
                display(pd.DataFrame(lines, columns=columns, index=index))
        else:
            print('Aucune décomposition.')

    def vars_data_pourcent(self,
                           nom, noms=[], nomSauf=[],
                           vars=[], varSauf=[],
                           pourcent=0, Pourcent=100,
                           varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                           nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):
        indexNom = self.nomToIndex(nom)
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesVars = self.indexesVarsDefiniesNom(indexNom, indexesVars)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        if indexNom in indexesNoms: indexesNoms.remove(indexNom)

        resVals = []
        resVars = []
        pourcents = []
        totaux = []
        for v in indexesVars:
            exclus = self.__exclus
            if not self.__data[indexNom][v] in exclus:
                total = len(self.indexes_like(indexNom, indexesNoms, [v], 100))
                try:
                    prc = round(100 * total / len(indexesNoms))
                except:
                    break
                if Pourcent >= prc >= pourcent:
                    resVars.append(self.__vars[v])

        return resVars

    def show_data_pourcent(self,
                           nom, noms=[], nomSauf=[],
                           vars=[], varSauf=[],
                           pourcent=0, Pourcent=100,
                           varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                           nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                           pasColonne=10, pasLigne=10):
        indexNom = self.nomToIndex(nom)

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesVars = self.indexesVarsDefiniesNom(indexNom, indexesVars)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        if indexNom in indexesNoms: indexesNoms.remove(indexNom)

        resVals = []
        resVars = []

        pourcents = []
        totaux = []
        for v in indexesVars:
            total = len(self.indexes_like(indexNom, indexesNoms, [v], 100))
            prc = round(100 * total / len(indexesNoms))
            if Pourcent >= prc >= pourcent:
                resVars.append(self.__vars[v])
                resVals.append(self.__data[indexNom][v])
                totaux.append(total)
                pourcents.append(prc)

        lines = [resVals, totaux, pourcents]
        columns = resVars
        index = [nom, 'total', '%']

        if pasColonne:
            res = self.repeteIndex(pasColonne, lines, columns, index)
            lines = res[0]
            columns = res[1]

        if pasLigne:
            res = self.repeteColumns(pasLigne, lines, columns, index)
            lines = res[0]
            index = res[1]

        display(pd.DataFrame([resVals, totaux, pourcents], columns=columns, index=index))

    def noms_data_pourcent(self,
                           nom, noms=[], nomSauf=[],
                           vars=[], varSauf=[],
                           pourcent=0, Pourcent=100,
                           varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                           nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):
        indexNom = self.nomToIndex(nom)
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesVars = self.indexesVarsDefiniesNom(indexNom, indexesVars)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        if indexNom in indexesNoms: indexesNoms.remove(indexNom)

        resVals = []
        resNoms = []

        for v in indexesVars:
            total = len(self.indexes_like(indexNom, indexesNoms, [v], 100))
            prc = round(100 * total / len(indexesNoms))
            if Pourcent >= prc >= pourcent:
                for n in indexesNoms:
                    if self.equal(self.__data[n][v], self.__data[indexNom][v]):
                        resNoms.append(self.__noms[n])

        return list(set(resNoms))

    def show_noms_data_pourcent(self,
                                nom, noms=[], nomSauf=[],
                                vars=[], varSauf=[],
                                pourcent=0, Pourcent=100,
                                varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):
        nomsSel = self.noms_data_pourcent(
            nom, noms=noms, nomSauf=nomSauf,
            vars=vars, varSauf=varSauf, varsTypesFormule=varsTypesFormule,
            pourcent=pourcent,
            Pourcent=Pourcent,
            varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
            nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
            nomsTypesFormule=nomsTypesFormule)
        varsSel = self.vars_data_pourcent(
            nom, noms=noms, nomSauf=nomSauf,
            vars=vars, varSauf=varSauf,
            pourcent=pourcent,
            Pourcent=Pourcent,
            varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
            varsTypesFormule=varsTypesFormule,
            nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
            nomsTypesFormule=nomsTypesFormule)
        self.show_data(noms=[nom] + nomsSel, vars=varsSel)

    def vars_only(self,
                  nom, noms=[], nomSauf=[],
                  vars=[], varSauf=[],
                  varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                  nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):
        return self.vars_data_pourcent(
            nom, noms=noms, nomSauf=nomSauf,
            vars=vars, varSauf=varSauf,
            Pourcent=0,
            varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
            varsTypesFormule=varsTypesFormule,
            nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf, nomsTypesFormule=nomsTypesFormule)

    def show_varsOnly(self,
                      nom, noms=[], nomSauf=[],
                      vars=[], varSauf=[],
                      varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                      nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):
        varsO = self.vars_only(
            nom, noms=noms, nomSauf=nomSauf,
            vars=vars, varSauf=varSauf,
            varsTypes=varsTypes, varsTypeSauf=varsTypeSauf, varsTypesFormule=varsTypesFormule,
            nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf, nomsTypesFormule=nomsTypesFormule)
        display(pd.DataFrame(columns=varsO))

    def show_data_only(self,
                       nom, noms=[], nomSauf=[],
                       vars=[], varSauf=[],
                       varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                       nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):
        varsO = self.vars_only(nom, noms=noms, nomSauf=nomSauf,
                               vars=vars, varSauf=varSauf,
                               varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                               varsTypesFormule=varsTypesFormule,
                               nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf, nomsTypesFormule=nomsTypesFormule)
        if varsO:
            self.show_data(noms=[nom], vars=varsO)
        else:
            print('Aucun résultat')

    def vars_innove(self,
                    noms=[], nomSauf=[],
                    vars=[], varSauf=[],
                    varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                    nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):

        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        varsInnove = []
        for i in indexesNoms:
            nom = self.__noms[i]
            varsInnove += self.vars_only(nom, noms=self.nomsAvant(nom), nomSauf=[nom],
                                         vars=vars, varSauf=varSauf,
                                         varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                         varsTypesFormule=varsTypesFormule,
                                         nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                                         nomsTypesFormule=nomsTypesFormule)

        varsInnove = list(set(varsInnove))
        indexesVarsInnove = sorted([self.varToIndex(v) for v in varsInnove])
        varsInnove = [self.__vars[i] for i in indexesVarsInnove]

        return varsInnove

    def show_vars_innove(self,
                         noms=None, nomSauf=None,
                         vars=None, varSauf=None,
                         varsTypes=None, varsTypeSauf=None, varsTypesFormule='',
                         nomsTypes=None, nomsTypeSauf=None, nomsTypesFormule=''):
        if nomsTypeSauf is None:
            nomsTypeSauf = []
        if nomsTypes is None:
            nomsTypes = []
        if varsTypeSauf is None:
            varsTypeSauf = []
        if varsTypes is None:
            varsTypes = []
        if varSauf is None:
            varSauf = []
        if vars is None:
            vars = []
        if nomSauf is None:
            nomSauf = []
        if noms is None:
            noms = []
        self.show_vars(self.vars_innove(
            noms=noms, nomSauf=nomSauf,
            vars=vars, varSauf=varSauf,
            varsTypes=varsTypes, varsTypeSauf=varsTypeSauf, varsTypesFormule=varsTypesFormule,
            nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf, nomsTypesFormule=nomsTypesFormule))

    def show_tableau_innove(self,
                            noms=[], nomSauf=[],
                            vars=[], varSauf=[],
                            varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                            nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                            pasColonne=10, pasLigne=10):
        if type(noms) == str:
            noms = [noms]

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        #indexesNomsDonnes = sorted(self.nomsToIndexesNoms(nomsDonnes, []))
        noms = [self.__noms[n] for n in indexesNoms]
        varsInnove = []
        varsInnoveComplet = []
        for nom in noms:
            varsIn = self.vars_innove(noms=[nom], nomSauf=nomSauf,
                                      vars=vars, varSauf=varSauf,
                                      varsTypes=varsTypes, varsTypeSauf=varsTypeSauf, varsTypesFormule=varsTypesFormule,
                                      nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf, nomsTypesFormule=nomsTypesFormule)
            varsInnove.append(varsIn)
            varsInnoveComplet += varsIn

        varsInnoveComplet = list(set(varsInnoveComplet))
        indexesVarsInnoveComplet = sorted(self.varsToIndexesVars(varsInnoveComplet, []))
        lines = []
        for n in range(len(indexesNoms)):
            try:
                prc = round(len(varsInnove[n]) / self.totalVarsNom(indexesNoms[n], indexesVars) * 100)
            except:
                prc = '0'
            line = [prc]
            for i in indexesVarsInnoveComplet:
                if self.indexToVar(i) in varsInnove[n]:
                    line.append(self.__data[indexesNoms[n]][i])
                else:
                    line.append('')
            lines.append(line)

        varsInnoveComplet = [self.indexToVar(v) for v in indexesVarsInnoveComplet]

        columns = ['%'] + varsInnoveComplet
        index = noms
        if pasColonne:
            res = self.repeteIndex(pasColonne, lines, columns, index)
            lines = res[0]
            columns = res[1]

        if pasLigne:
            res = self.repeteColumns(pasLigne, lines, columns, index)
            lines = res[0]
            index = res[1]
        print("Variables : "+str(len(indexesVars)))
        display(pd.DataFrame(lines, columns=columns, index=index))

    def show_tableau_innove_types(self,
                                  noms=[], nomSauf=[],
                                  vars=[], varSauf=[],
                                  varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                  varsTypeSortie=[], varsTypeSortieSauf=[],
                                  nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                    effectif=0, Effectif=0,
                                   pasColonne=10, pasLigne=10):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
        indexesVarsTypeSortie = self.varsTypesToIndexesTypes(varsTypeSortie, varsTypeSortieSauf)

        # typesRetenus = [tp for tp in varsTypes if not tp in varsTypeSauf]

        #indexesNomsDonnes = sorted(self.nomsToIndexesNoms(nomsDonnes, []))
        noms = [self.__noms[n] for n in indexesNoms]
        dictNomsIndexesVarsInnove = defaultdict(list)
        indexesVarsInnoveComplet = []
        for nom in tqdm(noms):
            varsIn = self.vars_innove(noms=[nom], nomSauf=nomSauf, \
                                      vars=vars, varSauf=varSauf, \
                                      varsTypes=varsTypes, varsTypeSauf=varsTypeSauf, \
                                      nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,)

            indexesVarsIn = self.varsToIndexesVars(varsIn, [])
            dictNomsIndexesVarsInnove[nom] = indexesVarsIn
            indexesVarsInnoveComplet += indexesVarsIn

        indexesVarsInnoveComplet = sorted(list(set(indexesVarsInnoveComplet)))

        collTypes = self.indexesVarsToDictTypesIndexesVars(
            indexesVarsInnoveComplet,
            indexesVarsTypeSortie)

        lines = []
        indexesTypesInnoveComplet = sorted([t for t in indexesVarsTypeSortie \
                                            if self.__vars_types_types[t] in collTypes])

        typesInnoveComplet = [self.__vars_types_types[i] for i in indexesTypesInnoveComplet]

        effectifs = self.effectifsTypes(indexesNoms, indexesVars, indexesTypesInnoveComplet)

        if effectif or Effectif:
            # restriction de indexesVarsTypes
            if Effectif == 0: Effectif = len(self.__vars)
            indexesTypesInnoveComplet = [indexesTypesInnoveComplet[i] \
                                         for i in range(len(indexesTypesInnoveComplet)) \
                                         if Effectif >= effectifs[i + 1] >= effectif]
            typesInnoveComplet = [self.__vars_types_types[i] for i in indexesTypesInnoveComplet]
            effectifs = [e for e in effectifs if Effectif >= e >= effectif]
        if not effectifs :
            print('Aucun résultat.')
        else :
            # première ligne avec l'effectif total et pour chaque type
            lines.append(effectifs)
            totalVars = len(indexesVars)
            for nom in noms:
                line = []
                totalNom = len(set(dictNomsIndexesVarsInnove[nom]). \
                               intersection(set(indexesVarsInnoveComplet)). \
                               intersection(set(indexesVars)))
                #total = len(set(dictNomsIndexesVarsInnove[nom]).intersection(set(indexesVars)))
                line.append(totalNom)
                for tp in typesInnoveComplet:
                    communs = list(set(dictNomsIndexesVarsInnove[nom]).\
                                   intersection(set(collTypes[tp])).\
                                   intersection(set(indexesVars)))
                    val = len(communs)
                    if val:
                        line.append(val)
                    else:
                        line.append('')
                lines.append(line)

            columns = ['Total'] + typesInnoveComplet
            index = ['Effectifs'] + noms

            if pasColonne:
                res = self.repeteIndex(pasColonne, lines, columns, index)
                lines = res[0]
                columns = res[1]

            if pasLigne:
                res = self.repeteColumns(pasLigne, lines, columns, index)
                lines = res[0]
                index = res[1]

            display(pd.DataFrame(lines, columns=columns, index=index))

    #
    def show_tableau_innove_types_pourcent(self,
                                           noms=[], nomSauf=[],
                                           vars=[], varSauf=[],
                                           varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                           varsTypeSortie=[], varsTypeSortieSauf=[],
                                           nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                           pourcenType=0, PourcenType=100,
                                           effectif=0, Effectif=0,
                                           pasColonne=10, pasLigne=10):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
        indexesVarsTypeSortie = self.varsTypesToIndexesTypes(varsTypeSortie, varsTypeSortieSauf)
        #indexesNomsDonnes = sorted(self.nomsToIndexesNoms(nomsDonnes, []))
        #indexesNomsDonnes = self.getIndexesNoms(nomsDonnes, nomsDonneSauf, nomsDonnesTypes, nomsDonnesTypeSauf, nomsDonnesTypesFormule)

        noms = [self.__noms[n] for n in indexesNoms]

        dictNomsIndexesVarsInnove = defaultdict(list)
        indexesVarsInnoveComplet = []
        for nom in tqdm(noms):
            varsIn = self.vars_innove(noms=[nom], nomSauf=nomSauf,
                                      vars=vars, varSauf=varSauf,
                                      varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                      varsTypesFormule=varsTypesFormule,
                                      nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf)
            indexesVarsIn = self.varsToIndexesVars(varsIn, [])
            dictNomsIndexesVarsInnove[nom] = indexesVarsIn
            indexesVarsInnoveComplet += indexesVarsIn

        indexesVarsInnoveComplet = sorted(list(set(indexesVarsInnoveComplet)))
        collTypes = self.indexesVarsToDictTypesIndexesVars(
            indexesVarsInnoveComplet,
            indexesVarsTypeSortie)

        lines = []

        indexesTypesInnoveComplet = sorted([t for t in indexesVarsTypeSortie \
                                            if self.__vars_types_types[t] in collTypes])

        # On met d'office les varsTypeSortie demandés :
        typesInnoveComplet = [self.__vars_types_types[i] for i in indexesTypesInnoveComplet]

        effectifs = self.effectifsTypes(indexesNoms, indexesVars, indexesTypesInnoveComplet)

        if effectif or Effectif:
            # restriction de indexesVarsTypes
            if Effectif == 0: Effectif = len(self.__vars)
            indexesTypesInnoveComplet = [indexesTypesInnoveComplet[i] \
                                         for i in range(len(indexesTypesInnoveComplet)) \
                                         if Effectif >= effectifs[i + 1] >= effectif]
            typesInnoveComplet = [self.__vars_types_types[i] for i in indexesTypesInnoveComplet]
            effectifs = [e for e in effectifs if Effectif >= e >= effectif]



        totalVars = len(indexesVars)
        # pourcentage d'innovation total pour chaque nom
        lines.append([effectifs[0]])  # effectif total
        for nom in noms:
            totalNom = len(set(dictNomsIndexesVarsInnove[nom]).\
                           intersection(set(indexesVarsInnoveComplet)).\
                            intersection(set(indexesVars)))
            prcNom = str(round(totalNom / totalVars * 100))+'%'

            lines.append([prcNom]) # pourcentage total

        # application condition sur les pourcentages
        typesReduit = []
        i = 1
        for tp in typesInnoveComplet:
            linesTemp = list(map(list,lines))
            typeReduit =  False
            linesTemp[0].append(effectifs[i])
            for n in range(len(noms)) :
                indexNom = self.__noms.index(noms[n])
                val = len(set(dictNomsIndexesVarsInnove[noms[n]]).intersection(set(collTypes[tp])).intersection(set(indexesVars)))
                totalType = self.totalVarsDefiniesTypeNom(indexNom, indexesVars, tp)
                try:
                    prc = round(val / totalType * 100)
                except:
                    prc = 0
                if PourcenType >= prc >= pourcenType :
                    typeReduit = True
                    linesTemp[1+n].append(str(prc) + '%')
                else:
                    linesTemp[1+n].append('-')
            if typeReduit :
                lines = list(map(list,linesTemp))
                typesReduit.append(tp)
            i+=1


        columns = ['Total'] + typesReduit
        index = ['Effectifs'] + noms

        if pasColonne:
            res = self.repeteIndex(pasColonne, lines, columns, index)
            lines = res[0]
            columns = res[1]

        if pasLigne:
            res = self.repeteColumns(pasLigne, lines, columns, index)
            lines = res[0]
            index = res[1]
        print("Variables : " + str(len(indexesVars)))
        display(pd.DataFrame(lines, columns=columns, index=index))

    def test_traduction(self,noms,vars=[], varSauf=[],
                        varsTypes = [], varsTypeSauf = [], varsTypesFormule = '') :

        if isinstance(noms, str) :
            noms = [noms]

        return self.show_tableau_innove_types_pourcent(noms = noms, vars =  vars, varSauf = varSauf,
                                            varsTypes = varsTypes, varsTypeSauf = varsTypeSauf, varsTypesFormule = varsTypesFormule,
                                            varsTypeSortie = ['traduction', 'citation'])

    ##########################################################################################
    ### Tableaux de corrélations
    ##########################################################################################

    def communs(self,
                indexNom1, indexNom2, indexesVars):
        comp = []
        for k in indexesVars:
            if not self.__data[indexNom1][k] in self.__exclus and \
                    not self.__data[indexNom2][k] in self.__exclus and \
                    self.equal(self.__data[indexNom1][k], self.__data[indexNom2][k]):
                comp.append(self.__data[indexNom2][k])
            else:
                comp.append('')

        return comp

    def communsStrict(self,
                      indexNom1, indexNom2, indexesVars):
        comp = []
        for k in indexesVars:
            if not self.__data[indexNom1][k] in self.__exclus and \
                    not self.__data[indexNom2][k] in self.__exclus and \
                    self.equalStrict(self.__data[indexNom1][k], self.__data[indexNom2][k]):
                comp.append(self.__data[indexNom2][k])
            else:
                comp.append('')

        return comp

    def difference(self,
                   indexNom1, indexNom2, indexesVars):
        diff = []
        for k in indexesVars:
            if not self.__data[indexNom1][k] in self.__exclus and \
                    not self.__data[indexNom2][k] in self.__exclus and \
                    not self.equal(self.__data[indexNom1][k], self.__data[indexNom2][k]):
                diff.append(self.__data[indexNom1][k])
            else:
                diff.append('')

        return diff

    def differenceStrict(self,
                         indexNom1, indexNom2, indexesVars):
        diff = []
        for k in indexesVars:
            if not self.__data[indexNom1][k] in self.__exclus and \
                    not self.__data[indexNom2][k] in self.__exclus and \
                    not self.equalStrict(self.__data[indexNom1][k], self.__data[indexNom2][k]):
                diff.append(self.__data[indexNom1][k])
            else:
                diff.append('')

        return diff

        # Liste des variables sur lesquelles deux éditions diffèrent

    def vars_difference(self,
                        nom1, nom2, vars=[], varSauf=[],
                        varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
        indexNom1 = self.nomToIndex(nom1)
        indexNom2 = self.nomToIndex(nom2)

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

        diff = self.differenceStrict(indexNom1, indexNom2, indexesVars)
        vars_diff = [self.indexToVar(indexesVars[i]) for i in range(len(indexesVars)) if not diff[i] == '']

        return vars_diff

    def show_difference(self,
                        nom1, nom2, vars=[], varSauf=[],
                        varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
        indexNom1 = self.nomToIndex(nom1)
        indexNom2 = self.nomToIndex(nom2)

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

        diff = [self.differenceStrict(indexNom1, indexNom2, indexesVars),
                self.difference(indexNom2, indexNom1, indexesVars)]

        # ligne avec les critères
        varsL = [self.indexToVar(v) for v in indexesVars]
        nomsL = [nom1, nom2]
        display(pd.DataFrame(diff, columns=varsL, index=nomsL))

    def show_difference_types(self,
                              nom1, nom2, vars=[], varSauf=[],
                              varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                              varsTypeSortie=[], varsTypeSortieSauf=[],
                              effectif=0, Effectif=0,
                              pourcenType=0, PourcenType=100):
        indexNom1 = self.nomToIndex(nom1)
        indexNom2 = self.nomToIndex(nom2)

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesVarsTypeSortie = self.varsTypesToIndexesTypes(varsTypeSortie, varsTypeSortieSauf)

        indexesVarsDifference = self.indexesVarsDifferenceStrict(indexNom1, indexNom2,
                                                                 indexesVars)

        collTypes = self.indexesVarsToDictTypesIndexesVars(indexesVarsDifference, indexesVarsTypeSortie)

        lines = []

        indexesTypesDifferenceComplet = sorted([t for t in indexesVarsTypeSortie
                                                if self.__vars_types_types[t] in collTypes])
        typesDifferenceComplet = [self.__vars_types_types[i] for i in indexesTypesDifferenceComplet]
        effectifs = self.effectifsTypes([indexNom1, indexNom2], indexesVars, indexesTypesDifferenceComplet)

        if effectif or Effectif:
            # restriction de indexesVarsTypes
            if Effectif == 0: Effectif = len(self.__vars)
            indexesTypesDifferenceComplet = [indexesTypesDifferenceComplet[i] \
                                             for i in range(len(indexesTypesDifferenceComplet)) \
                                             if Effectif >= effectifs[i + 1] >= effectif]
            typesDifferenceComplet = [self.__vars_types_types[i] for i in indexesTypesDifferenceComplet]

            total = effectifs[0]
            effectifs.pop(0)
            effectifs = [e for e in effectifs if Effectif >= e >= effectif]
            effectifs.insert(0, total)




        line0 = []
        line1 = []
        line2 = []
        line3 = []
        total = self.collTotal(collTypes)
        line0.append(effectifs[0])
        line1.append(total)
        line2.append(str(round(total/effectifs[0]*100))+'%')
        line3.append('')
        i = 1
        typesReduits = []
        for tp in typesDifferenceComplet:
            # val=round(effectifs[tp]/len(collTypes[tp])*100)
            val = len(collTypes[tp])
            if val:
                try:
                    prc = round(val / effectifs[i] * 100)
                except:
                    prc = 0

                if PourcenType >= prc >= pourcenType:
                    line0.append(effectifs[i])
                    line1.append(val)
                    line2.append(str(round(val / total * 100)) + '%')
                    line3.append(str(prc)+'%')
                    typesReduits.append(tp)

            i += 1
        lines.append(line0)
        lines.append(line1)
        lines.append(line2)
        lines.append(line3)
        print(color.bold + nom1 + '/' + nom2 + color.end)

        display(pd.DataFrame(lines,
                             columns=['Total'] + typesReduits,
                             index=['Effectifs', 'différence', '%différences', '%type']))

        # Liste des variables sur lesquelles deux éditions sont égales

    def vars_commun(self,
                    nom1, nom2, vars=[], varSauf=[],
                    varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
        indexNom1 = self.nomToIndex(nom1)
        indexNom2 = self.nomToIndex(nom2)

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

        com = self.communsStrict(indexNom1, indexNom2, indexesVars)
        vars_com = [self.indexToVar(indexesVars[i]) for i in range(len(indexesVars)) if not com[i] == '']

        return vars_com

    # Liste des indexes de variables sur lesquelles deux éditions diffèrent
    def indexes_vars_commun(self,
                            indexNom1, indexNom2, indexesVars):

        com = self.communsStrict(indexNom1, indexNom2, indexesVars)
        indexesVars_com = [indexesVars[i] for i in range(len(indexesVars)) if not com[i] == '']
        return indexesVars_com

    # indexes des variables pour lesquelles deux éditions ont les mêmes valeurs
    def indexesVarsCommunStrict(self,
                                indexNom1, indexNom2, indexesVars):
        com = []
        for k in indexesVars:
            if not self.__data[indexNom1][k] in self.__exclus and \
                    not self.__data[indexNom2][k] in self.__exclus and \
                    self.equalStrict(self.__data[indexNom1][k], self.__data[indexNom2][k]):
                com.append(k)

        return com

    # indexes des variables pour lesquelles deux éditions ont des valeurs différentes
    def indexesVarsDifferenceStrict(self,
                                    indexNom1, indexNom2, indexesVars):
        diff = []
        for k in indexesVars:
            if not self.equalStrict(self.__data[indexNom1][k], self.__data[indexNom2][k]):
                diff.append(k)

        return diff

    def show_commun(self,
                    nom1, nom2, vars=[], varSauf=[],
                    varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
        indexNom1 = self.nomToIndex(nom1)
        indexNom2 = self.nomToIndex(nom2)

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

        com = [self.communsStrict(indexNom1, indexNom2, indexesVars)]

        # ligne avec les critères
        varsL = [self.indexToVar(v) for v in indexesVars]
        nomsL = [nom1 + '/' + nom2]
        display(pd.DataFrame(com, columns=varsL, index=nomsL))

    # valeurs communes d'une édition avec d'autres éditions,
    # en précisant le pourcentage d'éditions ayant cette valeur
    # l'idée est de récupérer ainsi les variables "rares" communes à deux éditions
    def show_noms_commun_pourcent(self,
                                  nom, vars=[], varSauf=[],
                                  noms=[], nomSauf=[],
                                  pourcent=0, Pourcent=100,
                                  varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                  nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                  pasColonne=10, pasLigne=10):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

        indexNom = self.nomToIndex(nom)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        linesNoms = [[] for n in indexesNoms]
        totalNoms = [0 for n in indexesNoms]
        resVars = []

        pourcents = []
        totaux = []
        for v in indexesVars:
            indexesNomsCommun = self.indexes_like(indexNom, indexesNoms, [v], 100)
            indexesNomsCommun.remove(indexNom)
            total = len(indexesNomsCommun)
            prc = round(100 * total / len(indexesNoms))
            if Pourcent >= prc > pourcent:
                resVars.append(self.__vars[v])
                for n in indexesNoms:
                    if n in indexesNomsCommun:
                        linesNoms[n].append(self.__data[n][v])
                        totalNoms[n] += 1
                    else:
                        linesNoms[n].append('')

                totaux.append(total)
                pourcents.append(prc)

        lines = []
        resNoms = []
        for n in indexesNoms:
            if totalNoms[n]:
                total = self.totalNotNull(linesNoms[n])
                lines.append([total] + linesNoms[n])
                resNoms.append(self.indexToNom(n))
        lines.append([''] + totaux)
        lines.append([''] + pourcents)

        columns = ['Total'] + resVars
        index = resNoms + ['total', '%']

        if pasColonne:
            res = self.repeteIndex(pasColonne, lines, columns, index)
            lines = res[0]
            columns = res[1]

        if pasLigne:
            res = self.repeteColumns(pasLigne, lines, columns, index)
            lines = res[0]
            index = res[1]

        display(pd.DataFrame(lines, columns=columns, index=index))

    def show_commun_types(self,
                          nom1, nom2, vars=[], varSauf=[],
                          varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                          varsTypeSortie=[], varsTypeSortieSauf=[],
                          effectifType=0, EffectifType=0,
                          pourcenType=0, PourcenType=100):
        indexNom1 = self.nomToIndex(nom1)
        indexNom2 = self.nomToIndex(nom2)

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesVarsTypeSortie = self.varsTypesToIndexesTypes(varsTypeSortie, varsTypeSortieSauf)

        indexesVarsCommun = self.indexesVarsCommunStrict(indexNom1, indexNom2,
                                                         indexesVars)

        collTypes = self.indexesVarsToDictTypesIndexesVars(
            indexesVarsCommun,
            indexesVarsTypeSortie)

        lines = []

        indexesTypesCommunComplet = sorted([t for t in indexesVarsTypeSortie \
                                            if self.__vars_types_types[t] in collTypes])
        typesCommunComplet = [self.__vars_types_types[i] for i in indexesTypesCommunComplet]
        effectifs = self.effectifsTypes([indexNom1, indexNom2], indexesVars, indexesTypesCommunComplet)

        if effectif or Effectif:
            # restriction de indexesVarsTypes
            if EffectifType == 0: EffectifType = len(self.__vars)
            indexesTypesCommunComplet = [indexesTypesCommunComplet[i] \
                                         for i in range(len(indexesTypesCommunComplet)) \
                                         if EffectifType >= effectifs[i + 1] >= effectifType]
            typesCommunComplet = [self.__vars_types_types[i] for i in indexesTypesCommunComplet]

            total = effectifs[0]
            effectifs.pop(0)
            effectifs = [e for e in effectifs if Effectif >= e >= effectif]
            effectifs.insert(0, total)

        # première ligne avec l'effectif total pour chaque type

        line0 = []
        line1 = []
        line2 = []
        line3 = []
        total = self.collTotal(collTypes)
        line1.append(total)
        line2.append('')
        line3.append('')
        i = 1
        typesReduits = []
        for tp in typesCommunComplet:
            # val=round(effectifs[tp]/len(collTypes[tp])*100)
            val = len(collTypes[tp])
            if val:
                try:
                    prcType = round(val / effectifs[i] * 100)
                except:
                    prcType = 0

                prcCommuns = round(val / total * 100)

                if PourcenType >= prcType >= pourcenType:
                    typesReduits.append(tp)
                    line0.append(effectifs[i])
                    line1.append(val)
                    line2.append(str(prcCommuns) + '%')
                    line3.append(str(prcType) + '%')

            i += 1

        lines.append(line0)
        lines.append(line1)
        lines.append(line2)
        lines.append(line3)
        print(color.bold + nom1 + '/' + nom2 + color.end)

        display(pd.DataFrame(lines,
                             columns=['Total'] + typesReduits,
                             index=['Effectifs', 'communs', '%communs', '%type']))

        # Retourne la somme et la somme pondérée

    # vals contient la liste des valeurs des variables.
    def stats(self,
              vals, indexesVars):
        sum = 0
        total = 0
        sumPond = 0
        for k in range(len(vals)):
            if self.__poids[self.redindexVarToIndex(k, indexesVars)] != 0:
                total += 1
                if vals[k] != '':
                    sum += 1
                    sumPond += self.__poids[self.redindexVarToIndex(k, indexesVars)]
        try:
            return [int(round(100 * sumPond / total)), sum]
        except:
            return [0, sum]

            # Tableau descendant des corrélations

    def tableau_correlations_desc(self,
                                  indexNom, indexesVars, indexesNoms,
                                  pourcent, Pourcent):

        # liste des corrélations descendantes, avec le nom au début et le total à la fin
        corDes = []
        for k in indexesNoms:
            if k < indexNom:
                l = self.communs(indexNom, k, indexesVars)
                # ajouts des stats en début de liste
                total = self.totalPondereVarsDefiniesConjointes(
                    indexNom, k, indexesVars)
                totalCommun = self.totalNotNull(l)
                try:
                    prc = round(100 * totalCommun / total)
                except:
                    prc = 0
                l = [prc, total, totalCommun] + l
                l.insert(0, self.__noms[k])
                if Pourcent >= l[1] >= pourcent:
                    corDes.append(l)

        corDes_sorted = sorted(corDes, key=itemgetter(1), reverse=True)

        return corDes_sorted

    # Tableau ascendant des corrélations
    def tableau_correlations_asc(self,
                                 indexNom, indexesVars, indexesNoms,
                                 pourcent, Pourcent):

        # liste des corrélations ascendantes, avec le nom au début et le total à la fin
        corAsc = []
        for k in indexesNoms:
            if k > indexNom:
                l = self.communs(indexNom, k, indexesVars)
                # ajout des stats en début de liste
                total = self.totalPondereVarsDefiniesConjointes(
                    indexNom, k, indexesVars)
                totalCommun = self.totalNotNull(l)
                try:
                    prc = round(100 * totalCommun / total)
                except:
                    prc = 0
                l = [prc, total, totalCommun] + l
                l.insert(0, self.__noms[k])
                if Pourcent >= l[1] >= pourcent:
                    corAsc.append(l)

        corAsc_sorted = sorted(corAsc, key=itemgetter(1))

        return corAsc_sorted

    def show_discrimine(self,
                                       nom, discrimines, vars=[], varSauf=[],
                                       varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                       pasColonne=10):
        # variables sur lesquelles les deux éditions diffèrent
        # parmi celle où le nom a des valeurs égales à l'une ou l'autre
        # varsDiff1 = self.vars_difference_relative(nom,discrimnes)
        varsDiff = self.vars_difference(discrimines[0], discrimines[1],
                        vars = self.vars_somme_relative(nom,discrimines))
        #varsDiff = list(set(varsDiff1) & set(varsDiff2))
        if vars :
            vars = list (set(vars) & set(varsDiff))
        else :
            vars = varsDiff

        self.show_tableau_correlations_desc(
                                       nom, noms=discrimines,
                                        vars = vars,
                                        varSauf=set(varSauf + self.vars_innove(nom)),
                                       varsTypes = varsTypes, varsTypeSauf =  varsTypeSauf, varsTypesFormule =  varsTypesFormule,
                                       pasColonne = pasColonne)

    def show_tableau_correlations_desc(self,
                                       nom, vars=[], varSauf=[],
                                       noms=[], nomSauf=[],
                                       pourcent=0, Pourcent=100,effectif = 0, Effectif = 0,
                                       varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                       nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                       pasColonne=10, pasLigne=10):

        indexNom = self.nomToIndex(nom)

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesVars = self.indexesVarsDefiniesNom(indexNom, indexesVars)

        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)





        self.set_selectedIndexesVars(indexesVars)
        self.set_selectedIndexesNoms(indexesNoms)

        corDes = self.tableau_correlations_desc(indexNom, indexesVars, indexesNoms, pourcent, Pourcent)
        # première ligne avec les poids
        # poidsL=['poids : ']+self.__selectedPoids

        if Effectif == 0: Effectif = len(self.__vars)

        # deuxième ligne avec les critères
        varsL = ['%', 'effectif', 'communs'] + [self.indexToVar(v) for v in indexesVars]
        nomsL = []
        corDesData = []
        for L in corDes:
            if Effectif >= L[2] >= effectif :
                nomsL.append(L[0])
                del L[0]
                corDesData.append(L)

        if pasColonne:
            res = self.repeteIndex(pasColonne, corDesData, varsL, nomsL)
            corDesData = res[0]
            varsL = res[1]

        if pasLigne:
            res = self.repeteColumns(pasLigne, corDesData, varsL, nomsL)
            corDesData = res[0]
            nomsL = res[1]

        print('Variables : ' + str(len(varsL) - 3))
        display(pd.DataFrame(corDesData, columns=varsL, index=nomsL))

    def show_tableau_correlations_asc(self,
                                      nom, vars=[], varSauf=[],
                                      noms=[], nomSauf=[],
                                      pourcent=0, Pourcent=100, effectif = 0, Effectif = 0,
                                      varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                      nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                      pasColonne=10, pasLigne=10):

        indexNom = self.nomToIndex(nom)

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesVars = self.indexesVarsDefiniesNom(indexNom, indexesVars)

        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        self.set_selectedIndexesVars(indexesVars)
        self.set_selectedIndexesNoms(indexesNoms)

        if Effectif == 0: Effectif = len(self.__vars)

        corAsc = self.tableau_correlations_asc(indexNom, indexesVars, indexesNoms, pourcent, Pourcent)

        # deuxième ligne avec les critères
        varsL = ['%', 'effectif', 'communs'] + [self.indexToVar(v) for v in indexesVars]
        nomsL = []
        corAscData = []
        for L in corAsc:
            if Effectif >= L[2] >= effectif :
                nomsL.append(L[0])
                del L[0]
                corAscData.append(L)

        columns = varsL
        index = nomsL

        if pasColonne:
            res = self.repeteIndex(pasColonne, corAscData, columns, index)
            corAscDat = res[0]
            columns = res[1]

        if pasLigne:
            res = self.repeteColumns(pasLigne, corAscData, columns, index)
            corAscDat = res[0]
            index = res[1]

        print('Variables : ' + str(len(varsL) - 3))
        display(pd.DataFrame(corAscData, columns=columns, index=index))

    def show_tableaux_correlations_asc(self,
                                       vars=[], varSauf=[],
                                       noms=[], nomSauf=[],
                                       pourcent=0, Pourcent=100,
                                       varsTypes=[], varsTypeSauf=[],
                                       varsTypesFormule='',
                                       nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        noms = [self.__noms[n] for n in indexesNoms]
        vars = [self.__vars[v] for v in indexesVars]

        for n in indexesNoms:
            nom = self.__noms[n]
            print(nom)
            self.show_tableau_correlations_asc(nom, vars, varSauf,
                                               noms, nomSauf,
                                               pourcent, Pourcent,
                                               varsTypes, varsTypeSauf, varsTypesFormule,
                                               nomsTypes, nomsTypeSauf)

    def show_tableaux_correlations_desc(self,
                                        vars=[], varSauf=[],
                                        noms=[], nomSauf=[],
                                        pourcent=0, Pourcent=100,
                                        varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                        nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        noms = [self.__noms[n] for n in indexesNoms]
        vars = [self.__vars[v] for v in indexesVars]

        for n in indexesNoms:
            nom = self.__noms[n]
            print(nom)
            self.show_tableau_correlations_desc(nom, vars, varSauf,
                                                noms, nomSauf,
                                                pourcent, Pourcent,
                                                varsTypes, varsTypeSauf, varsTypesFormule,
                                                nomsTypes, nomsTypeSauf)

    # Tableau ascendant et des descendant des corrélations dans fichier csv "nomCor.csv"
    def save_tableau_correlations(self,
                                  nom, noms=[], nomSauf=[],
                                  vars=[], varSauf=[],
                                  pourcent=0, Pourcent=100,
                                  varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                  nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        indexNom = self.nomToIndex(nom)

        # liste des corrélations ascendantes, avec le nom au début et le total à la fin
        corAsc = self.tableau_correlations_asc(indexNom, indexesVars, indexesNoms, pourcent, Pourcent)
        corDes = self.tableau_correlations_desc(indexNom, indexesVars, indexesNoms, pourcent, Pourcent)

        filename = nom + self.__baseName + 'Cor.csv'
        with open(filename, 'w',encoding="UTF-8") as file:
            wr = csv.writer(file, quotiinng=csv.QUOTE_ALL)

            for line in corAsc:
                wr.writerow(line)

            # première ligne avec les poids
            poidsL = ['poids : ', '', ''] + [self.__poids[i] for i in indexesVars]
            wr.writerow(poidsL)

            # deuxième ligne avec les critères
            varsL = ['nom', '%', 'total'] + [self.__vars[v] for v in indexesVars]
            wr.writerow(varsL)

            for line in corDes:
                wr.writerow(line)

    def save_tableaux_correlations(self,
                                   noms=[], nomSauf=[],
                                   vars=[], varSauf=[],
                                   pourcent=0, Pourcent=100,
                                   varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                   nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        noms = [self.__noms[n] for n in indexesNoms]
        vars = [self.__vars[v] for v in indexesVars]

        for n in indexesNoms:
            nom = self.__noms[n]
            print(nom)
            self.save_tableau_correlations(
                nom, noms, nomSauf,
                vars, varSauf,
                pourcent, Pourcent,
                varsTypes, varsTypeSauf, varsTypesFormule,
                nomsTypes, nomsTypeSauf)

    #####################################
    # tableaux corrélation types
    #####################################

    # Tableau descendant des corrélations par types
    # les corrélations sont déterminées à partir des variables
    # les types servent à la présentation des résultats
    def tableau_correlations_types_desc(self,
                                        indexNom, indexesVars, indexesNoms,
                                        indexesVarsTypes, indexesVarsTypeSortie,
                                        pourcent, Pourcent):

        # dict des corrélations descendantes par types de variables,
        # avec le nom  et le total au début
        corDes = []
        for k in indexesNoms:
            if k < indexNom:
                # print('indexesVarsToVars : ',self.indexesVarsToVars(indexesVars))
                vars_com = self.indexes_vars_commun(indexNom, k, indexesVars)
                # print('communs : ',self.__noms[indexNom],'-',self.__noms[k],' : ', vars_com)
                vars_com = list(set(vars_com).intersection(set(indexesVars)))
                collTypes = self.indexesVarsToDictTypesIndexesVars(vars_com,
                                                                   indexesVarsTypes)
                line = []
                for indexTp in indexesVarsTypeSortie:
                    try:
                        tp = self.__vars_types_types[indexTp]
                        val = len(collTypes[tp])
                        if val == 0: val = ''
                        line.append(val)
                    except:
                        line.append('')
                line = [self.__noms[k], self.collTotal(collTypes)] + line
                corDes.append(line)

        corDes_sorted = sorted(corDes, key=itemgetter(1), reverse=True)

        return corDes_sorted


    def tableau_correlations_types_asc(self,
                                       indexNom, indexesVars, indexesNoms,
                                       indexesVarsTypes, indexesVarsTypeSortie,
                                       pourcent, Pourcent):

        # dict des corrélations descendantes par types de variables,
        # avec le nom  et le total au début
        corAsc = []
        for k in indexesNoms:
            if k > indexNom:
                vars_com = self.indexes_vars_commun(indexNom, k, indexesVars)
                vars_com = list(set(vars_com).intersection(set(indexesVars)))
                collTypes = self.indexesVarsToDictTypesIndexesVars(vars_com, indexesVarsTypes)
                line = []
                for indexTp in indexesVarsTypeSortie:
                    try:
                        tp = self.__vars_types_types[indexTp]
                        val = len(collTypes[tp])
                        if val == 0: val = ''
                        line.append(val)
                    except:
                        line.append('')
                line = [self.__noms[k], self.collTotal(collTypes)] + line
                corAsc.append(line)

        corAsc_sorted = sorted(corAsc, key=itemgetter(1))

        return corAsc_sorted

    # Tableau descendant des corrélations par types exprimées en pourcentages (relativement à chaque type)
    # les corrélations sont déterminées à partir des variables
    # les types servent à la présentation des résultats
    def tableau_correlations_types_pourcent_desc(self,
                                                 indexNom, indexesVars, indexesNoms,
                                                 indexesVarsTypeSortie,
                                                 pourcent, Pourcent):

        # dict des corrélations descendantes par types de variables,
        # avec le nom  et le total au début
        corDes = []
        for k in tqdm(indexesNoms):
            if k < indexNom:
                # print('indexesVarsToVars : ',self.indexesVarsToVars(indexesVars))
                vars_com = self.indexes_vars_commun(indexNom, k, indexesVars)
                # print('communs : ',self.__noms[indexNom],'-',self.__noms[k],' : ', vars_com)
                vars_com = list(set(vars_com).intersection(set(indexesVars)))
                collTypes = self.indexesVarsToDictTypesIndexesVars(
                    vars_com, indexesVarsTypeSortie)
                line = []

                for indexTp in indexesVarsTypeSortie:
                    try:
                        tp = self.__vars_types_types[indexTp]
                        val = len(collTypes[tp])
                        total = self.totalVarsDefiniesConjointesType(indexNom, k, tp, indexesVars)
                        prc = round(val / total * 100)
                        if prc:
                            line.append(prc)
                        else:
                            line.append('')
                    except:
                        line.append('')
                try:
                    Total = self.totalVarsDefiniesConjointes(indexNom, k, indexesVars)
                    prc = round(len(vars_com) / Total * 100)
                except:
                    prc = 0

                if Pourcent >= prc >= pourcent:
                    line = [self.__noms[k], prc] + line
                    corDes.append(line)

        corDes_sorted = sorted(corDes, key=itemgetter(1), reverse=True)

        return corDes_sorted

    def tableau_correlations_types_pourcent_asc(self,
                                                indexNom, indexesVars, indexesNoms,
                                                indexesVarsTypeSortie,
                                                pourcent, Pourcent):

        # dict des corrélations descendantes par types de variables,
        # avec le nom  et le total au début
        corAsc = []
        for k in tqdm(indexesNoms):
            if k > indexNom:
                vars_com = self.indexes_vars_commun(indexNom, k, indexesVars)
                vars_com = list(set(vars_com).intersection(set(indexesVars)))
                collTypes = self.indexesVarsToDictTypesIndexesVars(
                    vars_com, indexesVarsTypeSortie)
                line = []


                for indexTp in indexesVarsTypeSortie:
                    try:
                        tp = self.__vars_types_types[indexTp]
                        val = len(collTypes[tp])
                        total = self.totalVarsDefiniesConjointesType(indexNom, k, tp, indexesVars)
                        prc = round(val / total * 100)
                        if prc:
                            line.append(prc)
                        else:
                            line.append('')
                    except:
                        line.append('')
                try:
                    Total = self.totalVarsDefiniesConjointes(indexNom, k, indexesVars)
                    prc = round(len(vars_com) / Total * 100)
                except:
                    prc = 0

                if Pourcent >= prc >= pourcent:
                    line = [self.__noms[k], prc] + line
                    corAsc.append(line)

        corAsc_sorted = sorted(corAsc, key=itemgetter(1), reverse=True)

        return corAsc_sorted

    def show_tableau_correlations_types_desc(self,
                                             nom, vars=[], varSauf=[],
                                             noms=[], nomSauf=[],
                                             pourcent=0, Pourcent=100,
                                             effectif=0, Effectif=0,
                                             varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                             varsTypeSortie=[], varsTypeSortieSauf=[],
                                             nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                             pasColonne=10, pasLigne=10):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
        indexesVarsTypes = self.varsTypesToIndexesTypes(varsTypes, varsTypeSauf)
        indexesVarsTypeSortie = self.varsTypesToIndexesTypes(varsTypeSortie, varsTypeSortieSauf)
        indexNom = self.nomToIndex(nom)

        self.set_selectedIndexesVars(indexesVars)
        self.set_selectedIndexesNoms(indexesNoms)

        effectifs = self.effectifsTypesNom(indexNom, indexesVars, indexesVarsTypeSortie)

        if effectif or Effectif:
            # restriction de indexesVarsTypes
            if Effectif == 0: Effectif = len(self.__vars)
            indexesVarsTypes = [indexesVarsTypes[i] \
                                for i in range(len(indexesVarsTypeSortie)) \
                                if Effectif >= effectifs[i + 1] >= effectif]
            effectifs = [e for e in effectifs if Effectif >= e >= effectif]

        corDes = self.tableau_correlations_types_desc(indexNom, indexesVars, indexesNoms, \
                                                      indexesVarsTypes, indexesVarsTypeSortie,
                                                      pourcent, Pourcent)

        varsTypeSortie = [self.__vars_types_types[tp] for tp in indexesVarsTypeSortie]

        nomsL = []
        corDesData = []

        # première ligne avec l'effectif total et pour chaque type
        corDesData.append(effectifs)
        for L in corDes:
            nomsL.append(L[0])
            del L[0]
            corDesData.append(L)

        columns = ['total'] + varsTypeSortie
        index = ['Effectifs'] + nomsL

        if pasColonne:
            res = self.repeteIndex(pasColonne, corDesData, columns, index)
            corDesData = res[0]
            columns = res[1]

        if pasLigne:
            res = self.repeteColumns(pasLigne, corDesData, columns, index)
            corDesData = res[0]
            index = res[1]

        print('Types : ' + str(len(varsTypeSortie)))

        display(pd.DataFrame(corDesData, columns=columns, index=index))

    #Fonction pour discriminer les corrélations d'une édition à deux autres suivant les types
    def show_discrimine_types(self,
                                       nom, discrimines, vars=[], varSauf=[],
                                       varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                        varsTypeSortie=[], varsTypeSortieSauf=[],
                                       pasColonne=10):
        varsDiff = self.vars_difference(discrimines[0], discrimines[1])
        if vars :
            vars = list (set(vars) & set(varsDiff))
        else :
            vars = varsDiff

        self.show_tableau_correlations_types_desc(
                                       nom, noms=discrimines,
                                        vars = vars,
                                        varSauf=set(varSauf + self.vars_innove(nom)),
                                       varsTypes = varsTypes, varsTypeSauf =  varsTypeSauf, varsTypesFormule =  varsTypesFormule,
                                        varsTypeSortie = varsTypeSortie, varsTypeSortieSauf = varsTypeSortieSauf,
                                       pasColonne = pasColonne)


    def show_tableau_correlations_types_asc(self,
                                            nom, vars=[], varSauf=[],
                                            noms=[], nomSauf=[],
                                            pourcent=0, Pourcent=100,
                                            effectif=0, Effectif=0,
                                            varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                            varsTypeSortie=[], varsTypeSortieSauf=[],
                                            nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
        indexesVarsTypes = self.varsTypesToIndexesTypes(varsTypes, varsTypeSauf)
        indexesVarsTypeSortie = self.varsTypesToIndexesTypes(varsTypeSortie, varsTypeSortieSauf)
        indexNom = self.nomToIndex(nom)

        self.set_selectedIndexesVars(indexesVars)
        self.set_selectedIndexesNoms(indexesNoms)

        effectifs = self.effectifsTypesNom(indexNom, indexesVars, indexesVarsTypeSortie)

        if effectif or Effectif:
            # restriction de indexesVarsTypes
            if Effectif == 0: Effectif = len(self.__vars)
            indexesVarsTypes = [indexesVarsTypes[i] \
                                for i in range(len(indexesVarsTypeSortie)) \
                                if Effectif >= effectifs[i + 1] >= effectif]
            effectifs = [e for e in effectifs if Effectif >= e >= effectif]

        corAsc = self.tableau_correlations_types_asc(indexNom, indexesVars, indexesNoms,
                                                     indexesVarsTypes, indexesVarsTypeSortie,
                                                     pourcent, Pourcent)

        varsTypeSortie = [self.__vars_types_types[tp] for tp in indexesVarsTypeSortie]
        corAscData = []

        # première ligne avec l'effectif total et pour chaque type
        corAscData.append(effectifs)
        for L in corAsc:
            nomsL.append(L[0])
            del L[0]
            corAscData.append(L)

        display(pd.DataFrame(corAscData, columns=['total'] + varsTypeSortie, index=['Effectifs'] + nomsL))

    # liste du nombre de variables pour chaque type d'une édition donnée,
    # avec au début le total sur l'ensemble des types
    def effectifsTypesNom(self,
                          indexNom, indexesVars, indexesVarsTypes):
        effectifs = [self.totalVarsNom(indexNom, indexesVars)] + \
                    [self.totalVarsDefiniesTypeNom(indexNom, indexesVars, self.__vars_types_types[tp]) for tp in
                     indexesVarsTypes]
        return effectifs

    # liste du nombre de variables pour chaque type d'une liste d'éditions donnée,
    # avec au début le total sur l'ensemble des types
    def effectifsTypes(self, indexesNoms, indexesVars, indexesVarsTypes):
        effectifs = [self.totalVarsDefinies(indexesNoms, indexesVars)] + \
                    [self.totalVarsDefiniesType(indexesNoms, indexesVars, self.__vars_types_types[tp]) for tp in
                     indexesVarsTypes]
        return effectifs

    def show_tableau_correlations_types_pourcent_desc(self,
                                                      nom, vars=None, varSauf=None,
                                                      noms=None, nomSauf=None,
                                                      pourcent=0, Pourcent=100,
                                                      pourcenType=0,PourcenType=100,
                                                      effectif=0, Effectif=0,
                                                      varsTypes=None, varsTypeSauf=None, varsTypesFormule='',
                                                      varsTypeSortie=None, varsTypeSortieSauf=None,
                                                      nomsTypes=None, nomsTypeSauf=None, nomsTypesFormule='',
                                                      pasColonne=10, pasLigne=10):

        if nomsTypeSauf is None:
            nomsTypeSauf = []
        if nomsTypes is None:
            nomsTypes = []
        if varsTypeSortieSauf is None:
            varsTypeSortieSauf = []
        if varsTypeSortie is None:
            varsTypeSortie = []
        if varsTypeSauf is None:
            varsTypeSauf = []
        if varsTypes is None:
            varsTypes = []
        if nomSauf is None:
            nomSauf = []
        if noms is None:
            noms = []
        if varSauf is None:
            varSauf = []
        if vars is None:
            vars = []

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
        indexesVarsTypeSortie = self.varsTypesToIndexesTypes(varsTypeSortie, varsTypeSortieSauf)
        indexNom = self.nomToIndex(nom)
        self.set_selectedIndexesVars(indexesVars)
        self.set_selectedIndexesNoms(indexesNoms)

        effectifs = self.effectifsTypesNom(indexNom, indexesVars, indexesVarsTypeSortie)
        if effectif or Effectif:
            # restriction de indexesVarsTypes
            if Effectif == 0: Effectif = len(self.__vars)
            indexesVarsTypeSortie = [indexesVarsTypeSortie[i] \
                                     for i in range(len(indexesVarsTypeSortie)) \
                                     if Effectif >= effectifs[i + 1] >= effectif]
            effectifs = [e for e in effectifs if Effectif >= e >= effectif]

        corDes = self.tableau_correlations_types_pourcent_desc(
            indexNom, indexesVars, indexesNoms,
            indexesVarsTypeSortie,
            pourcent, Pourcent)

        varsTypeSortie = [self.__vars_types_types[tp] for tp in indexesVarsTypeSortie]

        # application condition sur les pourcentages
        if pourcenType > 0 or PourcenType < 100 :
            corDesReduit = []
            effectifsReduit = [effectifs[0]] #total de l'effectif
            varsTypeSortieReduit = []


            #ajout des noms et du pourcentage total
            for n in range(len(corDes)):
                corDesReduit.append([corDes[n][0],corDes[n][1]])

            #ajout des pourcentages sélectionnés
            for indexType in range(len(varsTypeSortie)) :
                typeReduit = False
                corDesReduiTemp = list(map(list, corDesReduit))
                for n in range(len(corDes)) :
                    prc = corDes[n][2+indexType]
                    if prc == '' : prc = 0
                    if PourcenType >= prc >= pourcenType :
                        typeReduit = True
                        corDesReduiTemp[n].append(prc)
                    else :
                        corDesReduiTemp[n].append('-')
                if typeReduit:
                    corDesReduit =  list(map(list,corDesReduiTemp))
                    varsTypeSortieReduit.append(varsTypeSortie[indexType])
                    effectifsReduit.append(effectifs[1+indexType])

            effectifs=effectifsReduit
            varsTypeSortie=varsTypeSortieReduit
            corDes = corDesReduit


        # première ligne avec l'effectif total et pour chaque type
        corDesData = []
        corDesData.append(effectifs)

        nomsL = []
        for L in corDes:
            nomsL.append(L[0])
            del L[0]
            corDesData.append(L)

        columns = ['% total'] + varsTypeSortie
        index = ['Effectifs'] + nomsL
        lines = corDesData

        if pasColonne:
            res = self.repeteIndex(pasColonne, lines, columns, index)
            lines = res[0]
            columns = res[1]

        if pasLigne:
            res = self.repeteColumns(pasLigne, lines, columns, index)
            lines = res[0]
            index = res[1]

        display(pd.DataFrame(lines, columns=columns, index=index))

    # Fonction pour discriminer les corrélations d'une édition à deux autres
    # suivant les types, exprimés en pourcentages
    def show_discrimine_types_pourcent(self,
                                  nom, discrimines, vars=[], varSauf=[],
                                  varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                  varsTypeSortie=[], varsTypeSortieSauf=[],
                                  pasColonne=10):
            varsDiff = self.vars_difference(discrimines[0], discrimines[1])
            if vars:
                vars = list(set(vars) & set(varsDiff))
            else:
                vars = varsDiff

            self.show_tableau_correlations_types_pourcent_desc(
                nom, noms=discrimines,
                vars=vars,
                varSauf=set(varSauf + self.vars_innove(nom)),
                varsTypes = varsTypes, varsTypeSauf = varsTypeSauf, varsTypesFormule = varsTypesFormule,
                varsTypeSortie = varsTypeSortie, varsTypeSortieSauf = varsTypeSortieSauf,
                pasColonne=pasColonne)

    def show_tableau_correlations_types_pourcent_asc(self,
                                                     nom, vars=None, varSauf=None,
                                                     noms=None, nomSauf=None,
                                                     pourcent=0, Pourcent=100,
                                                     pourcenType=0, PourcenType=100,
                                                     effectif=0, Effectif=0,
                                                     varsTypes=None, varsTypeSauf=None, varsTypesFormule='',
                                                     varsTypeSortie=None, varsTypeSortieSauf=None,
                                                     nomsTypes=None, nomsTypeSauf=None, nomsTypesFormule='',
                                                     pasColonne=10, pasLigne=10):

        if nomsTypeSauf is None:
            nomsTypeSauf = []
        if nomsTypes is None:
            nomsTypes = []
        if varsTypeSortie is None:
            varsTypeSortie = []
        if varsTypeSortieSauf is None:
            varsTypeSortieSauf = []
        if varsTypeSauf is None:
            varsTypeSauf = []
        if varsTypes is None:
            varsTypes = []
        if noms is None:
            noms = []
        if nomSauf is None:
            nomSauf = []
        if varSauf is None:
            varSauf = []
        if vars is None:
            vars = []
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
        indexesVarsTypeSortie = self.varsTypesToIndexesTypes(varsTypeSortie, varsTypeSortieSauf)
        indexNom = self.nomToIndex(nom)
        self.set_selectedIndexesVars(indexesVars)
        self.set_selectedIndexesNoms(indexesNoms)

        effectifs = self.effectifsTypesNom(indexNom, indexesVars, indexesVarsTypeSortie)
        if effectif or Effectif:
            # restriction de indexesVarsTypes
            if Effectif == 0: Effectif = len(self.__vars)
            indexesVarsTypeSortie = [indexesVarsTypeSortie[i] \
                                     for i in range(len(indexesVarsTypeSortie)) \
                                     if Effectif >= effectifs[i + 1] >= effectif]
            effectifs = [e for e in effectifs if Effectif >= e >= effectif]

        corAsc = self.tableau_correlations_types_pourcent_asc(
            indexNom, indexesVars, indexesNoms,
            indexesVarsTypeSortie,
            pourcent, Pourcent)

        varsTypeSortie = [self.__vars_types_types[tp] for tp in indexesVarsTypeSortie]
        # condition sur les pourcentages
        if pourcenType > 0 or PourcenType < 100:
            corAscReduit = []
            effectifsReduit = [effectifs[0]]  # total de l'effectif
            varsTypeSortieReduit = []

            # ajout des noms et du pourcentage total
            for n in range(len(corAsc)):
                corAscReduit.append([corAsc[n][0], corAsc[n][1]])

            # ajout des pourcentages sélectionnés
            for indexType in range(len(varsTypeSortie)):
                typeReduit = False
                for n in range(len(corAsc)):
                    prc = corAsc[n][2 + indexType]
                    if PourcenType >= prc >= pourcenType:
                        typeReduit = True
                        corAscReduit[n].append(prc)
                    else:
                        corAscReduit[n].append('-')

                if typeReduit:
                    varsTypeSortieReduit.append(varsTypeSortie[indexType])
                    effectifsReduit.append(effectifs[1 + indexType])
                else:
                    # suppression de tous les '' ajoutés
                    for n in range(len(corAsc)):
                        del (corAscReduit[n][-1])

            effectifs = effectifsReduit
            varsTypeSortie = varsTypeSortieReduit
            corAsc = corAscReduit

        # première ligne avec l'effectif total et pour chaque type
        corAscData = []
        corAscData.append(effectifs)

        nomsL = []
        for L in corAsc:
            nomsL.append(L[0])
            del L[0]
            corAscData.append(L)

        columns = ['% total'] + varsTypeSortie
        index = ['Effectifs'] + nomsL
        lines = corAscData

        if pasColonne:
            res = self.repeteIndex(pasColonne, lines, columns, index)
            lines = res[0]
            columns = res[1]

        if pasLigne:
            res = self.repeteColumns(pasLigne, lines, columns, index)
            lines = res[0]
            index = res[1]

        display(pd.DataFrame(lines, columns=columns, index=index))

    #####################################
    # liens directs
    #####################################

    def lien_direct(self, indexNom1, indexNom2, indexVar, indexesNoms):
        if indexNom2 > indexNom1:
            indexN = indexNom1
            indexNom1 = indexNom2
            indexNom2 = indexN
        boole1 = self.equal(self.__data[indexNom1][indexVar], self.__data[indexNom2][indexVar])
        boole2 = False
        if boole1:
            indexesNomsEntre = [i for i in indexesNoms if indexNom1 >= i >= indexNom2]
            vals = [self.__data[n][indexVar] for n in indexesNomsEntre \
                    if self.equal(self.__data[indexNom1][indexVar], self.__data[n][indexVar])]
            # print(self.__vars[indexVar]+' : ',vals)
            boole2 = (len(vals) == 2)
        return boole1 and boole2

    def indexesVars_liens_directs(self, nom1, nom2, vars=[], varSauf=[],
                                  noms=[], nomSauf=[],
                                  varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                  nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        indexNom1 = self.nomToIndex(nom1)
        indexNom2 = self.nomToIndex(nom2)
        res = [v for v in indexesVars if self.lien_direct(indexNom1, indexNom2, v, indexesNoms)]
        return res

    def vars_liens_directs(self, nom1, nom2, vars=[], varSauf=[],
                           noms=[], nomSauf=[],
                           varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                           nomsTypes=[], nomsTypeSauf=[]):

        resIndexesVars = self.indexesVars_liens_directs(nom1, nom2, vars=vars, varSauf=varSauf,
                                                        noms=noms, nomSauf=nomSauf,
                                                        varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                                        varsTypesFormule=varsTypesFormule,
                                                        nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf)
        resVars = [self.__vars[i] for i in resIndexesVars]
        return resVars

    def liens_directs_desc(self, nom1, nom2, vars=[], varSauf=[],
                           noms=[], nomSauf=[],
                           varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                           nomsTypes=[], nomsTypeSauf=[]):
        resIndexesVars = self.indexesVars_liens_directs(nom1, nom2, vars=vars, varSauf=varSauf,
                                                        noms=noms, noSauf=nomSauf,
                                                        varTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                                        varsTypsFormule=varsTypesFormule,
                                                        nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf)
        resVars = [self.__vars[i] for i in resIndexesVars]
        return resVars

    def show_vars_liens_directs(self, nom1, nom2, vars=[], varSauf=[],
                                noms=[], nomSauf=[],
                                varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                nomsTypes=[], nomsTypeSauf=[]):
        indexNom1 = self.nomToIndex(nom1)
        resIndexesVars = self.indexesVars_liens_directs(nom1, nom2, vars=vars, varSauf=varSauf,
                                                        noms=noms, nomSauf=nomSauf,
                                                        varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                                        varsTypesFormule=varsTypesFormule,
                                                        nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf)
        lines = [[self.__data[indexNom1][v] for v in resIndexesVars]]
        resNom = [nom1 + '/' + nom2]
        resVars = [self.__vars[i] for i in resIndexesVars]

        display(pd.DataFrame(lines, columns=resVars, index=resNom))

    def show_liens_directs_desc(self, nom, vars=[], varSauf=[],
                                noms=[], nomSauf=[],
                                varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        indexNom = self.nomToIndex(nom)
        indexesNomsAvant = [i for i in indexesNoms if indexNom > i]

        resIndexesVars = []
        resIndexesVarsComplet = []
        resVars = []
        for n in indexesNomsAvant:
            res = self.indexesVars_liens_directs(nom, self.__noms[n], vars=vars, varSauf=varSauf,
                                                 noms=noms, nomSauf=nomSauf,
                                                 varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                                 varsTypesFormule=varsTypesFormule,
                                                 nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf)
            resIndexesVars.append(res)
            resIndexesVarsComplet += res

        resIndexesVarsComplet = list(set(resIndexesVarsComplet))
        lines = []
        resNoms = []
        for n in indexesNomsAvant:
            line = []
            total = 0
            sum = 0
            if resIndexesVars[indexesNomsAvant.index(n)]:
                for v in resIndexesVarsComplet:
                    if not v in self.__exclus:
                        total += 1
                        if v in resIndexesVars[indexesNomsAvant.index(n)]:
                            line.append(self.__data[n][v])
                            sum += 1
                        else:
                            line.append('')

                if total:
                    prc = round(sum * 100 / total)
                else:
                    prc = 0
                lines.append([prc] + line)
                resNoms.append(self.__noms[n])

        resVars = ['%'] + [self.__vars[i] for i in resIndexesVarsComplet]

        display(pd.DataFrame(list(reversed(lines)), columns=resVars, index=list(reversed(resNoms))))

    def show_liens_directs_asc(self, nom, vars=[], varSauf=[],
                               noms=[], nomSauf=[],
                               varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                               nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        indexNom = self.nomToIndex(nom)
        indexesNomsApres = [i for i in indexesNoms if i > indexNom]

        resIndexesVars = []
        resIndexesVarsComplet = []
        resVars = []
        for n in indexesNomsApres:
            res = self.indexesVars_liens_directs(nom, self.__noms[n], vars=vars, varSauf=varSauf,
                                                 noms=noms, nomSauf=nomSauf,
                                                 varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                                 varsTypesFormule=varsTypesFormule,
                                                 nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf)
            resIndexesVars.append(res)
            resIndexesVarsComplet += res

        resIndexesVarsComplet = list(set(resIndexesVarsComplet))
        lines = []
        resNoms = []
        for n in indexesNomsApres:
            line = []
            total = 0
            sum = 0
            if resIndexesVars[indexesNomsApres.index(n)]:
                for v in resIndexesVarsComplet:
                    if not v in self.__exclus:
                        total += 1
                        if v in resIndexesVars[indexesNomsApres.index(n)]:
                            line.append(self.__data[n][v])
                            sum += 1
                        else:
                            line.append('')

                if total:
                    prc = round(sum * 100 / total)
                else:
                    prc = 0
                lines.append([prc] + line)
                resNoms.append(self.__noms[n])

        resVars = ['%'] + [self.__vars[i] for i in resIndexesVarsComplet]

        display(pd.DataFrame(lines, columns=resVars, index=resNoms))

    def lien_direct(self, indexNom1, indexNom2, indexVar, indexesNoms):
        if indexNom2 > indexNom1:
            indexN = indexNom1
            indexNom1 = indexNom2
            indexNom2 = indexN
        boole1 = self.equal(self.__data[indexNom1][indexVar], self.__data[indexNom2][indexVar])
        boole2 = False
        if boole1:
            indexesNomsEntre = [i for i in indexesNoms if indexNom1 >= i >= indexNom2]
            vals = [self.__data[n][indexVar] for n in indexesNomsEntre \
                    if self.equal(self.__data[indexNom1][indexVar], self.__data[n][indexVar])]
            # print(self.__vars[indexVar]+' : ',vals)
            boole2 = (len(vals) == 2)
        return boole1 and boole2

    def indexesVars_liens_directs(self, nom1, nom2, vars=[], varSauf=[],
                                  noms=[], nomSauf=[],
                                  varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                  nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        indexNom1 = self.nomToIndex(nom1)
        indexNom2 = self.nomToIndex(nom2)
        res = [v for v in indexesVars if self.lien_direct(indexNom1, indexNom2, v, indexesNoms)]
        return res

    def vars_liens_directs(self, nom1, nom2, vars=[], varSauf=[],
                           noms=[], nomSauf=[],
                           varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                           nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):
        resIndexesVars = self.indexesVars_liens_directs(nom1, nom2, vars=vars, varSauf=varSauf,
                                                        noms=noms, nomSauf=nomSauf,
                                                        varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                                        varsTypesFormule=varsTypesFormule,
                                                        nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                                                        nomsTypesFormule=nomsTypesFormule)
        resVars = [self.__vars[i] for i in resIndexesVars]
        return resVars

    def liens_directs_desc(self, nom1, nom2, vars = None, varSauf = None,
                           noms=None, nomSauf=None,
                           varsTypes=None, varsTypeSauf=None, varsTypesFormule='',
                           nomsTypes=None, nomsTypeSauf=None, nomsTypesFormule=''):
        if nomsTypes is None:
            nomsTypes = []
        if varsTypeSauf is None:
            varsTypeSauf = []
        if varsTypes is None:
            varsTypes = []
        if nomSauf is None:
            nomSauf = []
        if nomsTypeSauf is None:
            nomsTypeSauf = []
        if noms is None:
            noms = []
        if varSauf is None:
            varSauf = []
        if vars is None:
            vars = []
        resIndexesVars = self.indexesVars_liens_directs(nom1, nom2, vars=vars, varSauf=varSauf,
                                                        noms=noms, nomSauf=nomSauf,
                                                        varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                                        varsTypesFormule=varsTypesFormule,
                                                        nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                                                        nomsTypesFormule=nomsTypesFormule)
        resVars = [self.__vars[i] for i in resIndexesVars]
        return resVars

    def show_vars_liens_directs(self, nom1, nom2, vars=[], varSauf=[],
                                noms=[], nomSauf=[],
                                varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                nomsTypes=[], nomsTypeSauf=[]):
        indexNom1 = self.nomToIndex(nom1)
        resIndexesVars = self.indexesVars_liens_directs(nom1, nom2, vars=vars, varSauf=varSauf,
                                                        noms=noms, nomSauf=nomSauf,
                                                        varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                                        varsTypesFormule=varsTypesFormule,
                                                        nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                                                        nomsTypesFormule=nomsTypesFormule)
        lines = [[self.__data[indexNom1][v] for v in resIndexesVars]]
        resNom = [nom1 + '/' + nom2]
        resVars = [self.__vars[i] for i in resIndexesVars]

        display(pd.DataFrame(lines, columns=resVars, index=resNom))

    def show_liens_directs_desc(self, nom, vars=[], varSauf=[],
                                noms=[], nomSauf=[],
                                varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        indexNom = self.nomToIndex(nom)
        indexesNomsAvant = [i for i in indexesNoms if indexNom > i]

        resIndexesVars = []
        resIndexesVarsComplet = []
        for n in indexesNomsAvant:
            res = self.indexesVars_liens_directs(nom, self.__noms[n], vars=vars, varSauf=varSauf,
                                                 noms=noms, nomSauf=nomSauf,
                                                 varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                                 varsTypesFormule=varsTypesFormule,
                                                 nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf)
            resIndexesVars.append(res)
            resIndexesVarsComplet += res

        resIndexesVarsComplet = list(set(resIndexesVarsComplet))
        lines = []
        resNoms = []
        for n in indexesNomsAvant:
            line = []
            total = 0
            sum = 0
            if resIndexesVars[indexesNomsAvant.index(n)]:
                for v in resIndexesVarsComplet:
                    if not v in self.__exclus:
                        total += 1
                        if v in resIndexesVars[indexesNomsAvant.index(n)]:
                            line.append(self.__data[n][v])
                            sum += 1
                        else:
                            line.append('')

                if total:
                    prc = round(sum * 100 / total)
                else:
                    prc = 0
                lines.append([prc] + line)
                resNoms.append(self.__noms[n])

        resVars = ['%'] + [self.__vars[i] for i in resIndexesVarsComplet]

        display(pd.DataFrame(list(reversed(lines)), columns=resVars, index=list(reversed(resNoms))))

    def show_liens_directs_asc(self, nom, vars=[], varSauf=[],
                               noms=[], nomSauf=[],
                               varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                               nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        indexNom = self.nomToIndex(nom)
        indexesNomsApres = [i for i in indexesNoms if i > indexNom]

        resIndexesVars = []
        resIndexesVarsComplet = []
        resVars = []
        for n in indexesNomsApres:
            res = self.indexesVars_liens_directs(nom, self.__noms[n], vars=vars, varSauf=varSauf,
                                                 noms=noms, nomSauf=nomSauf,
                                                 varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                                 varsTypesFormule=varsTypesFormule,
                                                 nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                                                 nomsTypesFormule=nomsTypesFormule)
            resIndexesVars.append(res)
            resIndexesVarsComplet += res

        resIndexesVarsComplet = list(set(resIndexesVarsComplet))
        lines = []
        resNoms = []
        for n in indexesNomsApres:
            line = []
            total = 0
            sum = 0
            if resIndexesVars[indexesNomsApres.index(n)]:
                for v in resIndexesVarsComplet:
                    if not v in self.__exclus:
                        total += 1
                        if v in resIndexesVars[indexesNomsApres.index(n)]:
                            line.append(self.__data[n][v])
                            sum += 1
                        else:
                            line.append('')

                if total:
                    prc = round(sum * 100 / total)
                else:
                    prc = 0
                lines.append([prc] + line)
                resNoms.append(self.__noms[n])

        resVars = ['%'] + [self.__vars[i] for i in resIndexesVarsComplet]

        display(pd.DataFrame(lines, columns=resVars, index=resNoms))

    ##########################################################################################
    ### Graphes de déviation
    ##########################################################################################

    @property
    def distMax(self):
        print(self.__distMax)

    @property
    def proxMax(self):
        print(self.__proxMax)

    @property
    def graph_size(self):
        print(self.__graph_width, 'x', self.__graph_height)

    def set_graph_width(self, num):
        self.__graph_width = num

    def set_graph_height(self, num):
        self.__graph_height = num

    @property
    def font_size(self):
        print("Taille des labels des nœuds : ", self.__font_size)

    def set_font_size(self, num):
        self.__font_size = num

    @property
    def font_color(self):
        print("Couleur des labels des nœuds : ", self.__font_color)

    def set_font_color(self, chain):
        self.__font_color = chain

    @property
    def node_color(self):
        print("Couleur des nœuds : ", self.__node_color)

    def set_node_color(self, chain):
        self.__node_color = chain

    @property
    def node_size(self):
        print("Taille des nœuds : ", self.__node_size)

    def set_node_size(self, num):
        self.__node_size = num

    def set_label_posX(self, num):
        self.__label_posX = num

    def set_label_posY(self, num):
        self.__label_posY = num

    def set_graphe(self, width='', height='', \
                   font_size='', font_color='', \
                   node_color='', \
                   label_posX='', label_posY=''):
        if not width == '':
            self.set_graph_width(width)

        if not height == '':
            self.set_graph_height(height)

        if not font_size == '':
            self.set_font_size(font_size)

        if not font_color == '':
            self.set_font_color('black')

        if not node_color == '':
            self.set_node_color('black')

        if not label_posX == '':
            self.set_label_posX(label_posX)

        if not label_posY == '':
            self.set_label_posY(label_posY)

    @property
    def distance_matrice(self):
        return self.__distance_matrice

    @property
    def proximite_matrice(self):
        return self.__proximite_matrice

    @property
    def correlations(self):
        return self.__correlations

    def colorMap(self, cm):
        self.__colorMap = cm

    def graphe_deviation(self, indexNom, indexesVars, indexesNoms, pourcent, Pourcent):

        nom = self.__noms[indexNom]

        x0 = 0  # abcisse edition
        y0 = 0  # ordonnée edition
        sources = []

        plt.clf()
        fig = plt.figure(figsize=(self.__graph_width, self.__graph_height))
        # print(pd.DataFrame(cor, columns=self.__noms, index=self.__noms))

        # Noeud de la référence sélectionnée
        try:
            date0 = int(self.__data[indexNom][0])
        except:
            date0 = indexNom
        dateMax = dateMin = date0
        Gr = nx.Graph()
        Gr.add_node(nom)
        Gr.nodes[nom]['annee'] = dateMax
        Gr.nodes[nom]['pos'] = (x0, y0)

        # Si nécessaire, recalcule la matrice de corrélation

        redindexNom = self.indexNomToRedindex(indexNom, indexesNoms)

        try:
            self.__correlations[0][0]
        except:
            self.prox_matrices(indexesNoms, indexesVars)

        # Création des noeuds
        for j in range(len(indexesNoms)):
            indexj = indexesNoms[j]
            nomj = self.__noms[indexj]
            # if i>j :
            if Pourcent >= (10 - self.__correlations[redindexNom][j]) * 10 >= pourcent:
                Gr.add_node(nomj)
                try:
                    date = int(self.__data[indexj][0])
                except:
                    date = indexj
                Gr.nodes[nomj]['annee'] = date
                Gr.nodes[nomj]['cor'] = self.__correlations[redindexNom][j]
                sources.append(nomj)
                if date > dateMax:
                    dateMax = date
                if date < dateMin:
                    dateMin = date

        try:
            dy = 10 / (dateMax - dateMin)
        except:
            dy = 1

        # dictionnaire des positions
        # et attribution de leur position aux noeuds et aux labels

        # position du noeud et du label de la réf. sélectionnée
        pos = {}
        labels_pos = {}
        labels = {}
        pos[nom] = (x0, y0)
        labels[nom] = nom
        labels_pos[nom] = (x0 + .1, y0 + .1)

        # la distance verticale au nœud est conservée
        def prox1(node0, node, dx, dy):
            x0 = node0['pos'][0]
            y0 = node0['pos'][1]
            d = node0['annee'] - node['annee']
            c = node['cor']
            t = np.pi / 2 * c / 10
            return (x0 + d * np.tan(t), y0 - dy * d)

        # la distance au nœud est conservée
        def prox2(node0, node, dx, dy):
            x0 = node0['pos'][0]
            y0 = node0['pos'][1]
            d = node['annee'] - node0['annee']
            c = node['cor']
            if d < 0:
                t = np.pi / 2 * c / 10
                coord = (-d * np.sin(t), d * np.cos(t))
            else:
                t = np.pi / 2 * c / 10
                coord = (-d * np.sin(t), d * np.cos(t))
            return coord

        for n in sources:
            pos[n] = prox2(Gr.nodes[nom], Gr.nodes[n], 0, dy)
            Gr.nodes[n]['pos'] = pos[n]
            labels_pos[n] = (pos[n][0] + self.__label_posX, pos[n][1] + self.__label_posY)
            labels[n] = n

        cmap = cm = plt.get_cmap(self.__colorMap)
        cNorm = colors.Normalize(vmin=0, vmax=10)
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cmap)

        for source in sources:
            j = self.__noms.index(source)
            redindexj = indexesNoms.index(j)
            colorVal = scalarMap.to_rgba(self.__correlations[redindexNom][redindexj])
            Gr.add_edge(nom, source, color=colorVal, label=self.__correlations[redindexNom][redindexj])

        edge_colors = [Gr[u][v]['color'] for u, v in Gr.edges]
        nx.draw(Gr, pos, with_labels=False, node_color=self.__node_color, node_size=self.__node_size,
                edge_color=edge_colors, label_pos=.5)
        nx.draw_networkx_labels(Gr, labels_pos, labels, font_size=self.__font_size, font_color=self.__font_color)
        return plt

    def show_graphe_deviation(self, nom, vars=[], varSauf=[], noms=[], nomSauf=[],
                              varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                              nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                              pourcent=0, Pourcent=100, width='', height='',
                              font_size='', font_color='', node_color='',
                              label_posX='', label_posY=''):

        indexNom = self.nomToIndex(nom)
        indexesNoms = self.nomsToIndexesNoms(noms, nomSauf)
        indexesNoms = sorted(list(set(indexesNoms) | set([indexNom])))

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

        self.set_graphe(width, height, font_size, font_color, node_color, label_posX, label_posY)

        self.updateProxMatrices(indexesVars, indexesNoms)

        self.graphe_deviation(indexNom, indexesVars, indexesNoms, pourcent, Pourcent)
        plt.show()

    def save_graphe_deviation(self, nom, vars=[], varSauf=[],
                              noms=[], nomSauf=[],
                              varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                              nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                              pourcent=0, Pourcent=100,
                              width='', height='',
                              font_size='', font_color='',
                              node_color='',
                              label_posX='', label_posY=''):

        indexNom = self.nomToIndex(nom)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        indexesNoms = sorted(list(set(indexesNoms) | set([indexNom])))
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

        self.set_graphe(width, height, font_size, font_color, node_color, label_posX, label_posY)
        self.updateProxMatrices(indexesVars, indexesNoms)

        self.graphe_deviation(indexNom, indexesVars, indexesNoms, pourcent, Pourcent)
        plt.savefig(nom + self.__baseName + 'Prox.png', dpi=200)
        plt.show()

    def show_graphes_deviation(self, vars=[], varSauf=[],
                               noms=[], nomSauf=[],
                               varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                               nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                               pourcent=0, Pourcent=100):
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        if len(varSauf):
            if not len(vars): vars = self.__vars
            vars = [v for v in vars if not v in varSauf]

        if len(nomSauf):
            if not len(noms): noms = self.__noms
            noms = [n for n in noms if not n in nomSauf]

        for n in indexesNoms:
            nom = self.__noms[n]
            self.show_graphe_deviation(nom, vars, varSauf, noms, nomSauf,
                                       varsTypes, varsTypeSauf, varsTypesFormule,
                                       nomsTypes, nomsTypeSauf,
                                       pourcent, Pourcent)

    def save_graphes_deviation(self, vars=[], varSauf=[],
                               noms=[], nomSauf=[],
                               varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                               nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                               pourcent=0, Pourcent=100):
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        if len(varSauf):
            if not len(vars): vars = self.__vars
            vars = [v for v in vars if not v in varSauf]

        if len(nomSauf):
            if not len(noms): noms = self.__noms
            noms = [n for n in noms if not n in nomSauf]

        for n in indexesNoms:
            nom = self.__noms[n]
            self.save_graphe_deviation(nom, vars, varSauf,
                                       noms, nomSauf,
                                       varsTypes, varsTypeSauf, varsTypesFormule,
                                       nomsTypes, nomsTypeSauf,
                                       pourcent, Pourcent)

    ##########################################################################################
    ### Méthodes sur les matrices de distance
    ##########################################################################################
    # fonction de calcul de la distance
    # Les "*","#" et les "?" sont ignorés
    # Les '#' sont retirés de stats

    def dist(self, L1, L2, indexesVars):
        dist = 0
        for i in indexesVars:
            if not L1[i] in self.__exclus and not L2[i] in self.__exclus:
                dist += (not self.equal(L1[i], L2[i])) * self.__poids[i]
        return dist

    # fonction de calcul de la proximité
    def prox(self, L1, L2, indexesVars):
        prox = 0
        for i in indexesVars:
            if not L1[i] in self.__exclus and not L2[i] in self.__exclus:
                prox += (self.equal(L1[i], L2[i])) * self.__poids[i]
        return prox

        # calcule la matrice des distances

    def distMat(self, indexesNoms, indexesVars):
        distMat = np.full((len(indexesNoms), len(indexesNoms)), self.__selectedDistMax)
        for i in range(len(indexesNoms)):
            for j in range(len(indexesNoms)):
                distMat[i][j] = self.dist(self.__data[self.redindexNomToIndex(i, indexesNoms)],
                                          self.__data[self.redindexNomToIndex(j, indexesNoms)], indexesVars)
        return distMat

    # calcule la matrice de proximité une liste d'indexes de noms et de variables
    def proxMat(self, indexesNoms, indexesVars):
        proxMat = np.full((len(indexesNoms), len(indexesNoms)), 0)
        for i in range(len(indexesNoms)):
            for j in range(len(indexesNoms)):
                proxMat[i][j] = self.prox(self.__data[self.redindexNomToIndex(i, indexesNoms)],
                                          self.__data[self.redindexNomToIndex(j, indexesNoms)], indexesVars)
        return proxMat

    def matrices(self):
        self.__distance_matrice = self.distMat()
        self.__proximite_matrice = self.proxMat()
        # la correlation est une valeur entre 0 et 10
        self.__proxCorrelations = 10 - 10 / self.__selectedDistMax * self.__proximite_matrice
        self.__distCorrelations = 10 - 10 / self.__selectedDistMax * self.__distance_matrice
        # choix d'une distance par défaut...
        self.__correlations = self.__proxCorrelations

    def prox_matrices(self, indexesNoms, indexesVars):
        self.set_selectedIndexesVars(indexesVars)
        self.set_selectedIndexesNoms(indexesNoms)
        self.__proximite_matrice = self.proxMat(indexesNoms, indexesVars)
        # la correlation est une valeur entre 0 et 10
        self.__proxCorrelations = 10 - 10 / self.__selectedDistMax * self.__proximite_matrice
        # choix d'une distance par défaut...
        self.__correlations = self.__proxCorrelations

    def dist_matrices(self, indexesNoms, indexesVars):
        self.set_selectedIndexesVars(indexesVars)
        self.set_selectedIndexesNoms(indexesNoms)
        self.__distance_matrice = self.distMat(indexesNoms, indexesVars)
        # la correlation est une valeur entre 0 et 10
        self.__distCorrelations = 10 - 10 / self.__selectedDistMax * self.__distance_matrice
        # choix d'une distance par défaut...
        self.__correlations = self.__distCorrelations

    @property
    def distance_matrice(self):
        return self.__distance_matrice

    def show_distance_matrice(self, nomsI=[], nomsISauf=[], nomsJ=[], nomsJSauf=[], vars=[], varSauf=[]):
        indexesNomsI = self.nomsToIndexesNoms(nomsI, nomsISauf)
        indexesNomsJ = self.nomsToIndexesNoms(nomsJ, nomsJSauf)
        indexesVars = self.varsToIndexesVars(vars, varSauf)
        indexesNoms = list(set(indexesNomsI) | set(indexesNomsJ))

        self.updateDistMatrices(indexesVars, indexesNoms)

        try:
            self.__distance_matrice[0][0]
        except:
            self.dist_matrices(indexesNoms, indexesVars)

        lines = [
            [self.__distance_matrice[self.indexNomToRedindex(i, indexesNoms)][self.indexNomToRedindex(j, indexesNoms)]
             for j in indexesNomsJ] for i in indexesNomsI]
        resNomsI = [self.__noms[i] for i in indexesNomsI]
        resNomsJ = [self.__noms[i] for i in indexesNomsJ]
        return pd.DataFrame(lines, columns=resNomsJ, index=resNomsI)

    def show_distance_matrice_normalisee(self, nomsI=[], nomsISauf=[], nomsJ=[], nomsJSauf=[], vars=[], varSauf=[]):
        indexesNomsI = self.nomsToIndexesNoms(nomsI, nomsISauf)
        indexesNomsJ = self.nomsToIndexesNoms(nomsJ, nomsJSauf)
        indexesVars = self.varsToIndexesVars(vars, varSauf)
        indexesNoms = list(set(indexesNomsI) | set(indexesNomsJ))

        self.updateDistMatrices(indexesVars, indexesNoms)

        try:
            self.__distance_matrice[0][0]
        except:
            self.dist_matrices(indexesNoms, indexesVars)

        lines = [
            [self.__distCorrelations[self.indexNomToRedindex(i, indexesNoms)][self.indexNomToRedindex(j, indexesNoms)]
             for j in indexesNomsJ] for i in indexesNomsI]
        resNomsI = [self.__noms[i] for i in indexesNomsI]
        resNomsJ = [self.__noms[i] for i in indexesNomsJ]
        display(pd.DataFrame(lines, columns=resNomsJ, index=resNomsI))

    def show_distance_matrice_pourcent(self, nomsI=[], nomsISauf=[], nomsJ=[], nomsJSauf=[], vars=[], varSauf=[]):
        indexesNomsI = self.nomsToIndexesNoms(nomsI, nomsISauf)
        indexesNomsJ = self.nomsToIndexesNoms(nomsJ, nomsJSauf)
        indexesVars = self.varsToIndexesVars(vars, varSauf)
        indexesNoms = list(set(indexesNomsI) | set(indexesNomsJ))

        self.updateDistMatrices(indexesVars, indexesNoms)

        try:
            self.__distance_matrice[0][0]
        except:
            self.dist_matrices(indexesNoms, indexesVars)

        lines = [[int(round(100 * self.__distance_matrice[self.indexNomToRedindex(i, indexesNoms)][
            self.indexNomToRedindex(j, indexesNoms)] / self.__selectedDistMax)) for j in indexesNomsJ] for i in
                 indexesNomsI]
        resNomsI = [self.__noms[i] for i in indexesNomsI]
        resNomsJ = [self.__noms[i] for i in indexesNomsJ]
        display(pd.DataFrame(lines, columns=resNomsJ, index=resNomsI))

    def save_distance_matrice(self, nomsI=[], nomsISauf=[], nomsJ=[], nomsJSauf=[], vars=[], varSauf=[]):
        indexesNomsI = self.nomsToIndexesNoms(nomsI, nomsISauf)
        indexesNomsJ = self.nomsToIndexesNoms(nomsJ, nomsJSauf)
        indexesVars = self.varsToIndexesVars(vars, varSauf)
        indexesNoms = list(set(indexesNomsI) | set(indexesNomsJ))

        self.updateDistMatrices(indexesVars, indexesNoms)

        try:
            self.__distance_matrice[0][0]
        except:
            self.dist_matrices(indexesNoms, indexesVars)

        listNoms = [self.__noms[i] for i in indexesNoms]

        fileName = self.__baseName + 'Dist.csv'
        pd.DataFrame(self.__distance_matrice, columns=listNoms, index=listNoms).to_csv(fileName)

        lines = [
            [self.__distance_matrice[self.indexNomToRedindex(i, indexesNoms)][self.indexNomToRedindex(j, indexesNoms)]
             for j in indexesNomsJ] for i in indexesNomsI]
        resNomsI = [self.__noms[i] for i in indexesNomsI]
        resNomsJ = [self.__noms[j] for j in indexesNomsJ]

        fileName = self.__baseName + 'Dist.csv'
        pd.DataFrame(lines, columns=resNomsJ, index=resNomsI).to_csv(fileName)

        print(
            "La matrice des distances pour la mesure d'éloignement a été enregistrée dans le fichier \"" + self.__baseName + "Dist.csv\".")

    def save_distance_matrice_pourcent(self, nomsI=[], nomsISauf=[], nomsJ=[], nomsJSauf=[], vars=[], varSauf=[]):
        indexesNomsI = self.nomsToIndexesNoms(nomsI, nomsISauf)
        indexesNomsJ = self.nomsToIndexesNoms(nomsJ, nomsJSauf)
        indexesVars = self.varsToIndexesVars(vars, varSauf)
        indexesNoms = list(set(indexesNomsI) | set(indexesNomsJ))

        self.updateDistMatrices(indexesVars, indexesNoms)

        try:
            self.__distance_matrice[0][0]
        except:
            self.__dist_matrices(indexesNoms, indexesVars)

        lines = [[int(round(100 * self.__distance_matrice[self.indexNomToRedindex(i, indexesNoms)][
            self.indexNomToRedindex(j, indexesNoms)] / self.__selectedDistMax)) for j in indexesNomsJ] for i in
                 indexesNomsI]
        resNomsI = [self.__noms[i] for i in indexesNomsI]
        resNomsJ = [self.__noms[j] for j in indexesNomsJ]

        fileName = self.__baseName + 'Dist.csv'
        pd.DataFrame(lines, columns=resNomsJ, index=resNomsI).to_csv(fileName)

        print(
            "La matrice des distances en pourcentages pour la mesure d'éloignemnet a été enregistrée dans le fichier \"" + self.__baseName + "PourcentDist.csv\".")

    def distance_matrice_coordonnees(self, indexesNoms, indexesVars):
        mds = manifold.MDS(n_components=2, dissimilarity="precomputed", random_state=6)
        return mds.fit_transform(self.__distance_matrice)

    def show_distance_matrice_coordonnees(self, noms=[], nomSauf=[],
                                          vars=[], varSauf=[],
                                          varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                          nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):

        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

        self.updateDistMatrices(indexesVars, indexesNoms)

        try:
            self.__distance_matrice[0][0]
        except:
            self.dist_matrices(indexesNoms, indexesVars)

        listNoms = [self.__noms[i] for i in indexesNoms]

        display(pd.DataFrame(self.distance_matrice_coordonnees(indexesNoms, indexesVars), columns=['x', 'y'],
                             index=listNoms))

    def show_distance_ordonnee(self, noms=[], nomSauf=[],
                               vars=[], varSauf=[],
                               varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                               nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                               pourcent=0, Pourcent=100):

        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

        self.updateDistMatrices(indexesVars, indexesNoms)

        try:
            self.__distance_matrice[0][0]
        except:
            self.dist_matrices(indexesNoms, indexesVars)

        distEtNoms = [[self.__distance_matrice[i][j],
                       self.redindexNomToNom(j, indexesNoms) + ' - ' + self.redindexNomToNom(i, indexesNoms)] for i, j
                      in np.ndindex(self.__distance_matrice.shape) if i < j and pourcent <= int(
                round(self.__distance_matrice[i][j] * 100 / self.__selectedDistMax)) <= Pourcent]
        distEtNomsOrdonnes = sorted(distEtNoms, key=itemgetter(0), reverse=False)
        distOrdonnes = [[d, int(round(100 * d / self.__selectedDistMax))] for d, n in distEtNomsOrdonnes]
        nomsOrdonnes = [n for d, n in distEtNomsOrdonnes]
        display(pd.DataFrame(distOrdonnes, index=nomsOrdonnes, columns=['distance', '%']))

    def graphe_matrice_distance(self,
                                liens, indexesNoms, indexesVars, pourcent, Pourcent, couleursLiens):
        plt.clf()
        fig = plt.figure(figsize=(self.__gmc_width, self.__gmc_height))

        coordMat = self.distance_matrice_coordonnees(indexesNoms, indexesVars)

        listNoms = [self.__noms[n] for n in indexesNoms]
        # dictionnaire des positions
        pos = {}
        labels = {}
        labels_pos = {}
        for n, c in zip(listNoms, coordMat):
            pos[n] = (c[0], c[1])

        G = nx.Graph()
        G.add_nodes_from(pos.keys())
        colors = []

        for n, p in pos.items():
            G.nodes[n]['pos'] = p
            labels[n] = n
            labels_pos[n] = (pos[n][0] + self.__gmc_label_posX, pos[n][1] + self.__gmc_label_posY)

        if liens:
            # Création des liens significatifs
            # pour l'ensemble des noeuds

            for redindexi in range(len(indexesNoms)):
                indexi = self.redindexNomToIndex(redindexi, indexesNoms)
                nomi = self.__noms[indexi]
                for redindexj in range(len(indexesNoms)):
                    indexj = self.redindexNomToIndex(redindexj, indexesNoms)
                    nomj = self.__noms[indexj]
                    if redindexi > redindexj:
                        for k in couleursLiens:
                            if self.__correlations[redindexi][redindexj] > k:
                                G.add_edge(nomi, nomj, color=couleursLiens[k],
                                           label=self.__correlations[redindexi][redindexj])
                                break

            colors = [G[u][v]['color'] for u, v in G.edges]

        nx.draw(G, pos, with_labels=False, node_size=self.__gmc_node_size, node_color=self.__gmc_node_color,
                edge_color=colors)
        nx.draw_networkx_labels(G, labels_pos, labels, font_size=self.__gmc_font_size, font_color=self.__gmc_font_color)

        # pltComp.savefig(baseName+baseNameSecondaire+'Liens.png')
        plt.show()

    def show_graphe_distance(self, liens=True, noms=[], nomSauf=[], vars=[], varSauf=[],
                             varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                             nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                             pourcent=0, Pourcent=100, couleursLiens={}):
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

        if (len(couleursLiens) == 0): couleursLiens = {9: 'red', 8: 'green', 7: 'yellow', 6: 'pink'}

        self.updateDistMatrices(indexesVars, indexesNoms)

        try:
            self.__distance_matrice[0][0]
        except:
            self.dist_matrices(indexesNoms, indexesVars)

        self.graphe_matrice_distance(liens, indexesNoms, indexesVars, pourcent, Pourcent, couleursLiens)
        plt.show()

    def save_graphe_distance(self, liens=True, noms=[], nomSauf=[],
                             vars=[], varSauf=[],
                             varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                             nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                             pourcent=0, Pourcent=100, couleursLiens={}):

        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

        if (len(couleursLiens) == 0): couleursLiens = {9: 'red', 8: 'green', 7: 'yellow', 6: 'pink'}

        self.updateDistMatrices(indexesVars, indexesNoms)

        try:
            self.__distance_matrice[0][0]
        except:
            self.dist_matrices(indexesNoms, indexesVars)

        self.graphe_matrice_coordonnees(self.distance_matrice_coordonnees(), liens, indexesNoms, indexesVars, pourcent,
                                        Pourcent, couleursLiens)

        plt.savefig(self.__baseName + 'Dist.png')
        plt.show()

    @property
    def proximite_matrice(self):
        return self.__proximite_matrice

    def show_proximite_matrice(self, nomsI=[], nomsISauf=[],
                               nomsJ=[], nomsJSauf=[],
                               vars=[], varSauf=[],
                               varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
        indexesNomsI = self.nomsToIndexesNoms(nomsI, nomsISauf)
        indexesNomsJ = self.nomsToIndexesNoms(nomsJ, nomsJSauf)
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = list(set(indexesNomsI) | set(indexesNomsJ))

        self.updateProxMatrices(indexesVars, indexesNoms)

        try:
            self.__proximite_matrice[0][0]
        except:
            self.prox_matrices(indexesNoms, indexesVars)

        lines = [
            [self.__proximite_matrice[self.indexNomToRedindex(i, indexesNoms)][self.indexNomToRedindex(j, indexesNoms)]
             for j in indexesNomsJ] for i in indexesNomsI]
        resNomsI = [self.__noms[i] for i in indexesNomsI]
        resNomsJ = [self.__noms[i] for i in indexesNomsJ]

        display(pd.DataFrame(lines, columns=resNomsJ, index=resNomsI))
        # return pd.DataFrame(self.__proximite_matrice, columns=self.__selectedNoms, index=self.__selectedNoms)

    def show_proximite_matrice_normalisee(self, nomsI=[], nomsISauf=[],
                                          nomsJ=[], nomsJSauf=[],
                                          vars=[], varSauf=[],
                                          varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
        indexesNomsI = self.nomsToIndexesNoms(nomsI, nomsISauf)
        indexesNomsJ = self.nomsToIndexesNoms(nomsJ, nomsJSauf)
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = list(set(indexesNomsI) | set(indexesNomsJ))

        self.updateProxMatrices(indexesVars, indexesNoms)

        try:
            self.__proximite_matrice[0][0]
        except:
            self.prox_matrices(indexesNoms, indexesVars)

        lines = [
            [self.__proxCorrelations[self.indexNomToRedindex(i, indexesNoms)][self.indexNomToRedindex(j, indexesNoms)]
             for j in indexesNomsJ] for i in indexesNomsI]
        resNomsI = [self.__noms[i] for i in indexesNomsI]
        resNomsJ = [self.__noms[i] for i in indexesNomsJ]
        display(pd.DataFrame(lines, columns=resNomsJ, index=resNomsI))

    def show_proximite_matrice_pourcent(self, nomsI=[], nomsISauf=[],
                                        nomsJ=[], nomsJSauf=[],
                                        vars=[], varSauf=[],
                                        varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
        indexesNomsI = self.nomsToIndexesNoms(nomsI, nomsISauf)
        indexesNomsJ = self.nomsToIndexesNoms(nomsJ, nomsJSauf)
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = list(set(indexesNomsI) | set(indexesNomsJ))

        self.updateProxMatrices(indexesVars, indexesNoms)

        try:
            self.__proximite_matrice[0][0]
        except:
            self.prox_matrices(indexesNoms, indexesVars)

        lines = [[int(round(100 * self.__proximite_matrice[self.indexNomToRedindex(i, indexesNoms)][
            self.indexNomToRedindex(j, indexesNoms)] / self.__selectedDistMax)) for j in indexesNomsJ] for i in
                 indexesNomsI]
        resNomsI = [self.__noms[i] for i in indexesNomsI]
        resNomsJ = [self.__noms[j] for j in indexesNomsJ]

        display(pd.DataFrame(lines, columns=resNomsJ, index=resNomsI))
        # return pd.DataFrame(self.__proximite_matrice, columns=self.__selectedNoms, index=self.__selectedNoms)

    def save_proximite_matrice(self, nomsI=[], nomsISauf=[],
                               nomsJ=[], nomsJSauf=[],
                               vars=[], varSauf=[],
                               varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
        indexesNomsI = self.nomsToIndexesNoms(nomsI, nomsISauf)
        indexesNomsJ = self.nomsToIndexesNoms(nomsJ, nomsJSauf)
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = list(set(indexesNomsI) | set(indexesNomsJ))

        self.updateProxMatrices(indexesVars, indexesNoms)

        try:
            self.__proximite_matrice[0][0]
        except:
            self.prox_matrices(indexesNoms, indexesVars)

        lines = [
            [self.__proximite_matrice[self.indexNomToRedindex(i, indexesNoms)][self.indexNomToRedindex(j, indexesNoms)]
             for j in indexesNomsJ] for i in indexesNomsI]
        resNomsI = [self.__noms[i] for i in indexesNomsI]
        resNomsJ = [self.__noms[j] for j in indexesNomsJ]

        pd.DataFrame(lines, columns=resNomsJ, index=resNomsI).to_csv(self.__baseName + 'Prox.csv')
        print(
            "La matrice des distances pour la mesure de proximité a été enregistrée dans le fichier \"" + self.__baseName + "Prox.csv\".")

    def save_proximite_matrice_pourcent(self, nomsI=[], nomsISauf=[],
                                        nomsJ=[], nomsJSauf=[],
                                        vars=[], varSauf=[],
                                        varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
        indexesNomsI = self.nomsToIndexesNoms(nomsI, nomsISauf)
        indexesNomsJ = self.nomsToIndexesNoms(nomsJ, nomsJSauf)
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = list(set(indexesNomsI) | set(indexesNomsJ))

        self.updateProxMatrices(indexesVars, indexesNoms)

        try:
            self.__proximite_matrice[0][0]
        except:
            self.prox_matrices(indexesNoms, indexesVars)

        lines = [[int(round(100 * self.__proximite_matrice[self.indexNomToRedindex(i, indexesNoms)][
            self.indexNomToRedindex(j, indexesNoms)] / self.__selectedDistMax)) for j in indexesNomsJ] for i in
                 indexesNomsI]
        resNomsI = [self.__noms[i] for i in indexesNomsI]
        resNomsJ = [self.__noms[j] for j in indexesNomsJ]

        pd.DataFrame(lines, columns=resNomsJ, index=resNomsI).to_csv(self.__baseName + 'Prox.csv')
        print(
            "La matrice des distances en pourcentages pour la mesure de proximité a été enregistrée dans le fichier \"" + self.__baseName + "PourcentProx.csv\".")

    def proximite_matrice_coordonnees(self, indexesNoms, indexesVars):

        mds = manifold.MDS(n_components=2, dissimilarity="precomputed", random_state=6)
        return mds.fit_transform(self.__proximite_matrice)

    def show_proximite_matrice_coordonnees(self,
                                           noms=[], nomSauf=[], vars=[], varSauf=[],
                                           varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
        indexesNoms = self.nomsToIndexesNoms(noms, nomSauf)
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

        self.updateProxMatrices(indexesVars, indexesNoms)

        try:
            self.__proximite_matrice[0][0]
        except:
            self.prox_matrices(indexesNoms, indexesVars)

        listNoms = [self.__noms[i] for i in indexesNoms]
        display(pd.DataFrame(self.proximite_matrice_coordonnees(indexesNoms, indexesVars), columns=['x', 'y'],
                             index=listNoms))

    def show_proximite_ordonnee(self, noms=[], nomSauf=[],
                                vars=[], varSauf=[],
                                varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                pourcent=0, Pourcent=100):
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

        self.updateProxMatrices(indexesVars, indexesNoms)

        try:
            self.__proximite_matrice[0][0]
        except:
            self.prox_matrices(indexesNoms, indexesVars)

        proxEtNoms = [[self.__proximite_matrice[i][j],
                       self.redindexNomToNom(j, indexesNoms) + ' - ' + self.redindexNomToNom(i, indexesNoms)] for i, j
                      in np.ndindex(self.__proximite_matrice.shape) if i < j and Pourcent >= int(
                round(self.__proximite_matrice[i][j] * 100 / self.__selectedDistMax)) >= pourcent]
        proxEtNomsOrdonnes = sorted(proxEtNoms, key=itemgetter(0), reverse=True)
        proxOrdonnes = [[d, int(round(100 * d / self.__selectedDistMax))] for d, n in proxEtNomsOrdonnes]
        nomsOrdonnes = [n for d, n in proxEtNomsOrdonnes]
        display(pd.DataFrame(proxOrdonnes, index=nomsOrdonnes, columns=['proximité', '%']))

    def graphe_matrice_proximite(self, coordMat, liens, indexesNoms, indexesVars, pourcent, Pourcent, couleursLiens):
        plt.clf()
        fig = plt.figure(figsize=(self.__gmc_width, self.__gmc_height))

        coordMat = self.proximite_matrice_coordonnees(indexesNoms, indexesVars)

        listNoms = [self.__noms[n] for n in indexesNoms]
        # dictionnaire des positions
        pos = {}
        labels = {}
        labels_pos = {}
        for n, c in zip(listNoms, coordMat):
            pos[n] = (c[0], c[1])

        G = nx.Graph()
        G.add_nodes_from(pos.keys())
        colors = []

        for n, p in pos.items():
            G.node[n]['pos'] = p
            labels[n] = n
            labels_pos[n] = (pos[n][0] + self.__gmc_label_posX, pos[n][1] + self.__gmc_label_posY)

        if liens:
            # Création des liens significatifs
            # pour l'ensemble des noeuds

            for redindexi in range(len(indexesNoms)):
                indexi = self.redindexNomToIndex(redindexi, indexesNoms)
                nomi = self.__noms[indexi]
                for redindexj in range(len(indexesNoms)):
                    indexj = self.redindexNomToIndex(redindexj, indexesNoms)
                    nomj = self.__noms[indexj]
                    if redindexi > redindexj:
                        for k in couleursLiens:
                            if self.__correlations[redindexi][redindexj] < k:
                                G.add_edge(nomi, nomj, color=couleursLiens[k],
                                           label=self.__correlations[redindexi][redindexj])
                                break

            colors = [G[u][v]['color'] for u, v in G.edges]

        nx.draw(G, pos, with_labels=False, node_size=self.__gmc_node_size, node_color=self.__gmc_node_color,
                edge_color=colors)
        nx.draw_networkx_labels(G, labels_pos, labels, font_size=self.__gmc_font_size, font_color=self.__gmc_font_color)

        # pltComp.savefig(baseName+baseNameSecondaire+'Liens.png')
        plt.show()

    def show_graphe_proximite(self, liens=True, noms=[], nomSauf=[], vars=[], varSauf=[],
                              varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                              nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                              pourcent=0, Pourcent=100, couleursLiens={}):

        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

        if (len(couleursLiens) == 0): couleursLiens = {1: 'red', 2: 'green', 3: 'yellow', 4: 'pink'}

        self.updateProxMatrices(indexesVars, indexesNoms)

        try:
            self.__proximite_matrice_coordonnees[0][0]
        except:
            self.prox_matrices(indexesNoms, indexesVars)

        self.graphe_matrice_proximite(self.proximite_matrice_coordonnees(indexesNoms, indexesVars), liens, indexesNoms,
                                      indexesVars, pourcent, Pourcent, couleursLiens)
        plt.show()

    def save_graphe_proximite(self, liens=True, noms=[], nomSauf=[], vars=[], varSauf=[],
                              varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                              nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                              pourcent=0, Pourcent=100, couleursLiens={}):

        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

        self.updateProxMatrices(indexesVars, indexesNoms)

        if (len(couleursLiens) == 0): couleursLiens = {9: 'red', 8: 'green', 7: 'yellow', 6: 'pink'}

        try:
            self.__proximite_matrice[0][0]
        except:
            self.prox_matrices(indexesNoms, indexesVars)

        self.graphe_matrice_coordonnees(
            self.proximite_matrice_coordonnees(indexesNoms, indexesVars), liens, indexesNoms,
            indexesVars, pourcent, Pourcent, couleursLiens)

        plt.savefig(self._baseName + 'Prox.png')
        plt.show()

    # détermine la corrélation la plus faible d'une matrice de distances m et les éditions ayant cette corrélation
    def minCor(self, m):
        min = np.amin(m)
        worse = np.where(m == min)
        rs = list(zip(worse[0], worse[1]))
        rs = np.array([(self.__noms[i], self.__noms[j]) for (i, j) in rs if i > j])
        # res=rs[:len(rs)//2]
        return [str(round(100 * min / sum(self.__poids))) + '%', rs]

    # détermine la corrélation la plus faible d'une matrice de distances m et les éditions ayant cette corrélation
    def maxCor(self, m):
        # on exclut les élements au-dessus de la diagonale, diagonale comprise
        m = np.tril(m, -1)
        max = np.amax(m)
        best = np.where(m == max)
        rs = list(zip(best[0], best[1]))
        rs = np.array([(self.__noms[i], self.__noms[j]) for (i, j) in rs if i > j])
        # res=rs[:len(rs)//2]
        return [str(round(100 * max / sum(self.__poids))) + '%', rs]

    @property
    def maxDistCor(self):
        return self.maxCor(self.__distance_matrice)

    @property
    def minDistCor(self):
        return self.minCor(self.__distance_matrice)

    @property
    def maxProxCor(self):
        return self.maxCor(self.__proximite_matrice)

    @property
    def minProxCor(self):
        return self.minCor(self.__proximite_matrice)

    @property
    def gmc_size(self):
        print(self.__gmc_width, 'x', self.__gmc_height)

    def set_gmc_width(self, num):
        self.__gmc_width = num

    def set_gmc_height(self, num):
        self.__gmc_height = num

    @property
    def gmc_font_size(self):
        print("Taille des labels des nœuds : ", self.__gmc_font_size)

    def set_gmc_font_size(self, num):
        self.__gmc_font_size = num

    @property
    def gmc_font_color(self):
        print("Couleur des labels des nœuds : ", self.__gmc_font_color)

    def set_gmc_font_color(self, chain):
        self.__gmc_font_color = chain

    @property
    def gmc_node_color(self):
        print("Couleur des nœuds : ", self.__gmc_node_color)

    def set_gmc_node_color(self, chain):
        self.__gmc_node_color = chain

    @property
    def gmc_node_size(self):
        print("Taille des nœuds : ", self.__gmc_node_size)

    def set_gmc_node_size(self, num):
        self.__gmc_node_size = num

    def set_gmc_label_posX(self, num):
        self.__gmc_label_posX = num

    def set_gmc_label_posY(self, num):
        self.__gmc_label_posY = num

    ##########################################################################################
    ### Optimisation
    ##########################################################################################

    def optimise_intervalles(self, indexNom1, indexNom2, indexesVars, pourcent, longueur, pas):
        max = len(indexesVars)
        L1 = self.__data[indexNom1]
        L2 = self.__data[indexNom2]
        intervalles = []
        pourcents = []

        # l=longueur des intervalles parcourus

        for l in reversed(range(longueur, max + 1)):
            debut = 0
            fin = l - 1
            # print(l)
            while fin < max:
                # print('     ',debut,'-',fin)
                if not subIntervalles([indexesVars[debut], indexesVars[fin]], intervalles):
                    indexesVarsSub = indexesVars[debut:fin + 1]
                    val = self.listsEqualPourcent(L1, L2, indexesVarsSub)

                    if val >= pourcent:
                        intervalles.append([indexesVars[debut], indexesVars[fin]])
                        pourcents.append(val)

                debut = debut + pas
                fin = fin + pas

        res = [[pourcents[i]] + intervalles[i] for i in range(len(intervalles))]
        return res

    def show_intervalles(self, nom1, nom2, noms=[], nomSauf=[],
                         vars=[], varSauf=[],
                         varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                         nomsTypes=[], nomsTypeSauf=[],
                         pourcent=100, longueur=1, pas=1):

        indexNom1 = self.nomToIndex(nom1)
        indexNom2 = self.nomToIndex(nom2)
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        res = self.optimise_intervalles(indexNom1, indexNom2, indexesVars, pourcent, longueur, pas)
        # print(res)
        if res:
            lignes = []
            for r in res:
                ligne = []
                for i in indexesVars:
                    if r[1] <= i <= r[2]:
                        if self.equal(self.__data[indexNom1][i], self.__data[indexNom2][i]):
                            ligne.append(self.__data[indexNom1][i])
                        else:
                            ligne.append(self.__data[indexNom1][i] + '/' + self.__data[indexNom2][i])
                    else:
                        ligne.append('')

                ligne = [r[0], r[2] - r[1]] + ligne
                lignes.append(ligne)

            columns = ['%', 'long.'] + [self.__vars[v] for v in indexesVars]
            display(pd.DataFrame(lignes, columns=columns))
        else:
            print('Aucun résultat')

    def plot_intervalles(self, nom1, nom2, longueur,
                         vars=[], varSauf=[],
                         varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                         pas=1, elev=0, azim=0):
        indexNom1 = self.nomToIndex(nom1)
        indexNom2 = self.nomToIndex(nom2)
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexMax = len(indexesVars)
        L1 = self.__data[indexNom1]
        L2 = self.__data[indexNom2]

        def fun(xList, yList, L1, L2, indexesVars):
            res = [self.listsEqualPourcent(L1, L2, indexesVars[x:y + 1]) for x, y in zip(xList, yList)]

            return res

        x = np.arange(0, indexMax, pas)
        y = np.arange(longueur, indexMax, pas)
        X, Y = np.meshgrid(x, y)
        zs = np.array(fun(np.ravel(X), np.ravel(Y), L1, L2, indexesVars))
        Z = zs.reshape(X.shape)

        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection='3d')

        # Plot a 3D surface
        ax.plot_surface(X, Y, Z, cmap='viridis')

        ax.view_init(elev=30 + elev, azim=45 + azim)

        plt.show()

    ##########################################################################################
    ### Représentation moyennée
    ##########################################################################################

    def moyenne(self, L1, L2, indexVar, n, indexesVars):
        i = indexesVars.index(indexVar)
        m = max([0, i - n])
        M = min([len(indexesVars) - 1, i + n])
        sum = 0
        for j in range(m, M + 1):
            if self.equal(L1[indexesVars[j]], L2[indexesVars[j]]):
                sum += 1

        return sum / max([M - m + 1, 1])

    def plot_moyenne(self, nom1, noms, rayon=3, vars=[], varSauf=[],
                     varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                     width=20, height=10, legend_size=10):
        indexNom1 = self.nomToIndex(nom1)
        if type(noms) == str:
            noms = [noms]

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

        L1 = self.__data[indexNom1]
        x = indexesVars

        fig = plt.figure(figsize=(width, height))
        ax = plt.subplot(111)

        for nom2 in noms:
            indexNom2 = self.nomToIndex(nom2)
            L2 = self.__data[indexNom2]
            y = [self.moyenne(L1, L2, indexVar, rayon, indexesVars) for indexVar in x]
            ax.plot(x, y, label=nom2)

        box = ax.get_position()
        ax.set_position([box.x0, box.y0,
                         box.width, box.height])

        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
                  fancybox=True, shadow=True, ncol=5, prop={'size': legend_size})
        plt.show()

    def vars_moyenne(self, nom1, nom2, rayon=3, pourcent=0, Pourcent=100,
                     vars=[], varSauf=[],
                     varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
        indexNom1 = self.nomToIndex(nom1)
        indexNom2 = self.nomToIndex(nom2)

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

        L1 = self.__data[indexNom1]
        L2 = self.__data[indexNom2]
        resVars = [self.indexToVar(i) for i in indexesVars if
                   Pourcent >= 100 * self.moyenne(L1, L2, i, rayon, indexesVars) >= pourcent]
        return resVars

    ##########################################################################################
    ### Bases et générateurs
    ##########################################################################################

    def sum_set(self, indexesNoms, indexesVars):
        res = [set([self.__data[n][i] \
                    for n in indexesNoms \
                    if not self.__data[n][i] in self.__exclus]) \
               for i in indexesVars]
        return res

    def difference_liset(self, liset1, liset2, indexesVars):
        res = [liset1[i] - liset2[i] for i in range(len(indexesVars))]
        return res

    def show_sum_set(self, noms=None, nomSauf=None,
                     vars=None, varSauf=None,
                     varsTypes=None, varsTypeSauf=None, varsTypesFormule=''):

        if varsTypeSauf is None:
            varsTypeSauf = []
        if varsTypes is None:
            varsTypes = []
        if varSauf is None:
            varSauf = []
        if vars is None:
            vars = []
        if nomSauf is None:
            nomSauf = []
        if noms is None:
            noms = []
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.nomsToIndexesNoms(noms, nomSauf)

        res = self.sum_set(indexesNoms, indexesVars)
        self.show_liset(res, indexesVars)

    def lisetEmpty(self, liset, indexesVars):
        test = True
        for i in range(len(indexesVars)):
            if not len(liset[i]) == 0:
                test = False
                break
        return test

    def show_liset(self, lst, indexesVars):
        lst = [sorted(list(lst[i])) for i in range(len(indexesVars))]
        lignes = []
        test = True
        j = 0
        while test:
            test = False
            ligne = []
            for i in range(len(indexesVars)):
                try:
                    ligne.append(lst[i][j])
                    test = True
                except:
                    ligne.append('')
            lignes.append(ligne)
            j += 1

        varsL = [self.indexToVar(v) for v in indexesVars]
        display(pd.DataFrame(lignes[:-1], columns=varsL))

    def lisetContainsPourcent(self, liset1, liset2, indexesVars, pourcent, Pourcent):
        prc = self.pourcentLisetContains(liset1, liset2, indexesVars)
        return Pourcent >= prc >= pourcent

    def pourcentLisetContains(self, liset1, liset2, indexesVars):
        sum = 0
        for i in range(len(indexesVars)):
            if len(liset1[i] - liset2[i]) == 0 and not liset2[i] in self.__exclus:
                sum += 1
        prc = 100 * sum / len(indexesVars)

        return prc

    def lisetIncludesPourcent(self, ls, l, indexesVars, pourcent, Pourcent):
        prc = self.pourcentLisetIncludes(ls, l, indexesVars)
        return Pourcent >= prc >= pourcent

    def pourcentLisetIncludes(self, ls, l, indexesVars):
        sum = 0
        total = 0
        i = 0
        for v in indexesVars:
            if not l[v] in self.__exclus:
                total += 1
                if l[v] in ls[i]:
                    sum += 1
            i += 1

        try:
            prc = 100 * sum / total
        except:
            prc = 0
        return prc

    def pourcentLiset(self, ls, indexesVars):
        sum = 0
        for i in range(len(indexesVars)):
            if not len(ls[i]) == 0 and not ls[i] in self.__exclus:
                sum += 1
        prc = 100 * sum / len(indexesVars)

        return prc

    def vars_incompletes(self, liset1, liset2, indexesVars):
        varsIncompletes = []
        for i in range(len(indexesVars)):
            if not len(liset1[i] - liset2[i]) == 0 and not liset2[i] in self.__exclus:
                varsIncompletes.append(self.__vars[indexesVars[i]])

        return varsIncompletes

    def noms_base_complete(self, nomsGenerateurs=[], nomsGenerateurSauf=[], nomsBaseIncomplete=[],
                           vars=[], varSauf=[],
                           noms=[], nomSauf=[],
                           varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                           nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                           pourcent=100, Pourcent=100, max=0):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        indexesNomsGenerateurs = self.nomsToIndexesNoms(nomsGenerateurs, nomsGenerateurSauf)
        if nomsBaseIncomplete:
            indexesNomsBaseIncomplete = self.nomsToIndexesNoms(nomsBaseIncomplete, [])
        else:
            indexesNomsBaseIncomplete = []

        indexesNomsReste = list(set(indexesNoms) - set(indexesNomsBaseIncomplete))

        lisetComplet = self.sum_set(indexesNomsGenerateurs, indexesVars)

        if not max: max = len(indexesNoms)

        decomp = []
        res = []

        for indexes in tqdm(sorted(getCombinations(indexesNomsReste,
                                                   max - len(indexesNomsBaseIncomplete)), key=len)):

            if not includes(indexes, decomp):
                # print('indexes : ',indexesNoms)
                liset = self.sum_set(indexes + indexesNomsBaseIncomplete, indexesVars)
                # print(liset)
                if self.lisetContainsPourcent(lisetComplet, liset, indexesVars, pourcent, Pourcent):
                    dec = sorted(indexesNomsBaseIncomplete + indexes)
                    varsIncompletes = self.vars_incompletes(lisetComplet, liset, indexesVars)
                    decomp.append(dec)
                    res.append([dec, varsIncompletes])

        return res

    def show_noms_base_complete(self, nomsGenerateurs=[], nomsGenerateurSauf=[],
                                nomsBaseIncomplete=[],
                                vars=[], varSauf=[],
                                noms=[], nomSauf=[],
                                varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                pourcent=100, Pourcent=100, max=0):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        indexesNomsGenerateurs = self.nomsToIndexesNoms(
            nomsGenerateurs,
            nomsGenerateurSauf)

        lisetComplet = self.sum_set(indexesNomsGenerateurs, indexesVars)

        if not max: max = len(indexesNoms)
        nomsG = [self.__noms[i] for i in indexesNomsGenerateurs]
        print(color.bold + 'Tableau complet :' + color.end)
        print('  Générateurs :')
        if len(indexesNomsGenerateurs) == len(self.__noms):
            print('  Tous')
        else:
            print('  ' + ', '.join(nomsG))
        print('  Variables : ' + str(len(indexesVars)))
        self.show_liset(lisetComplet, indexesVars)

        resultats = self.noms_base_complete(nomsGenerateurs=nomsGenerateurs, nomsGenerateurSauf=nomsGenerateurSauf, \
                                            nomsBaseIncomplete=nomsBaseIncomplete,
                                            vars=vars, varSauf=varSauf,
                                            noms=noms, nomSauf=nomSauf,
                                            varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                            varsTypesFormule=varsTypesFormule,
                                            nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                                            pourcent=pourcent, Pourcent=Pourcent, max=max)


        if not resultats:
            print(color.bold + 'Aucun résultat' + color.end)
        for res in resultats:
            indexes = res[0]
            noms = [self.__noms[i] for i in indexes]
            lisetDiff = self.difference_liset(lisetComplet, self.sum_set(indexes, indexesVars), indexesVars)
            prc = round(100 - self.pourcentLiset(lisetDiff, indexesVars))
            print(color.bold + str(prc) + '% - ' + str(len(indexes)) + ' : ' + ', '.join(noms) + color.end)
            if prc < 100:
                self.show_liset(lisetDiff, indexesVars)
            print(' ')

    def show_values(self, noms=[], nomSauf=[],
                    vars=[], varSauf=[],
                    varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                    nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        lisetComplet = self.sum_set(indexesNoms, indexesVars)

        nomsG = [self.__noms[i] for i in indexesNoms]
        print(color.bold + 'Tableau complet :' + color.end)
        print('  Générateurs :')
        if len(indexesNoms) == len(self.__noms):
            print('  Tous')
        else:
            print('  ' + ', '.join(nomsG))
        self.show_liset(lisetComplet, indexesVars)

    def noms_inclus(self, indexesNomsGenerateurs, indexesVars, indexesNoms,
                    lisetComplet,
                    pourcent=100, Pourcent=100):
        res = []
        for n in indexesNoms:
            if self.lisetIncludesPourcent(lisetComplet,
                                          self.__data[n],
                                          indexesVars,
                                          pourcent, Pourcent):
                res.append(n)

        return res

    def show_noms_inclus(self, nomsGenerateurs=[], nomsGenerateurSauf=[],
                         vars=[], varSauf=[],
                         noms=[], nomSauf=[],
                         varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                         nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                         pourcent=0, Pourcent=100):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
        indexesNomsGenerateurs = self.nomsToIndexesNoms(nomsGenerateurs, nomsGenerateurSauf)

        lisetComplet = self.sum_set(indexesNomsGenerateurs, indexesVars)
        nomsG = [self.__noms[i] for i in indexesNomsGenerateurs]
        print(color.bold + 'Tableau complet :' + color.end)
        print('  Générateurs :')
        if len(indexesNomsGenerateurs) == len(self.__noms):
            print('  Tous')
        else:
            print('  ' + ', '.join(nomsG))

        self.show_liset(lisetComplet, indexesVars)

        indexesNomsInclude = self.noms_inclus(
            indexesNomsGenerateurs, indexesVars, indexesNoms,
            lisetComplet,
            pourcent=pourcent, Pourcent=Pourcent)

        if indexesNomsInclude:
            for n in indexesNomsInclude:
                l = list(self.__data[n])
                prc = round(self.pourcentLisetIncludes(lisetComplet, l, indexesVars))
                print('')
                print(color.bold + self.__noms[n] + ' : ' + str(prc) + '%' + color.end)
                if not prc == 100:
                    l = [l[v] for v in indexesVars]
                    lisetDiff = self.difference_liset(liset(l), lisetComplet, indexesVars)
                    self.show_liset(lisetDiff, indexesVars)
        else:
            print(color.bold + 'Aucun résultat' + color.end)

    # Comme précédemment, mais les résultats sont donnés par types
    def show_noms_inclus_types(self, nomsGenerateurs=[], nomsGenerateurSauf=[],
                               vars=[], varSauf=[],
                               noms=[], nomSauf=[],
                               varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                               nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                               pourcent=0, Pourcent=100,
                               effectif=0, Effectif=0,
                               varsTypeSortie=[], varsTypeSortieSauf=[]):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
        indexesVarsTypeSortie = self.varsTypesToIndexesTypes(varsTypeSortie, varsTypeSortieSauf)

        indexesNomsGenerateurs = self.nomsToIndexesNoms(nomsGenerateurs, nomsGenerateurSauf)

        if varsTypeSortie or varsTypeSortieSauf:
            indexesVarsTypeSortie = self.varsTypesToIndexesTypes(varsTypeSortie, varsTypeSortieSauf)
        else:
            indexesVarsTypeSortie = self.varsTypesToIndexesTypes(varsTypes, varsTypeSauf)

        varsTypeSortie = [self.__vars_types_types[tp] for tp in indexesVarsTypeSortie]

        lisetComplet = self.sum_set(indexesNomsGenerateurs, indexesVars)
        nomsG = [self.__noms[i] for i in indexesNomsGenerateurs]
        print(color.bold + 'Tableau complet :' + color.end)
        print('  Générateurs :')
        if len(indexesNomsGenerateurs) == len(self.__noms):
            print('  Tous')
        else:
            print('  ' + ', '.join(nomsG))

        self.show_liset(lisetComplet, indexesVars)

        indexesNomsInclude = self.noms_inclus(
            indexesNomsGenerateurs, indexesVars, indexesNoms,
            lisetComplet,
            pourcent=pourcent, Pourcent=Pourcent)

        if indexesNomsInclude:
            print("Les nombres donnés sont les nombres de variables du type dont les valeurs manquent.")
            for n in indexesNomsInclude:
                lines = []
                l = list(self.__data[n])
                prc = round(self.pourcentLisetIncludes(lisetComplet, l, indexesVars))
                print('')
                print(color.bold + self.__noms[n] + ' : ' + str(prc) + '%' + color.end)
                if not prc == 100:
                    # inutile d'afficher la différence si 100% des valeurs sont les mêmes
                    l = [l[v] for v in indexesVars]
                    lisetDiff = self.difference_liset(liset(l), lisetComplet, indexesVars)
                    # indexes des variables où il y a une différence
                    indexesVarsDiff = self.lisetToIndexesVars(lisetDiff, indexesVars)
                    collTypes = self.indexesVarsToDictTypesIndexesVars(
                        indexesVarsDiff,
                        indexesVarsTypeSortie)
                    effectifs = self.effectifsTypes([n], indexesVars, indexesVarsTypeSortie)

                    if effectif or Effectif:
                        # restriction de indexesVarsTypesSortie
                        if Effectif == 0: Effectif = len(self.__vars)
                        indexesVarsTypeSortie = [indexesVarsTypeSortie[i] \
                                                 for i in range(len(indexesVarsTypeSortie)) \
                                                 if Effectif >= effectifs[i + 1] >= effectif]
                        varsTypeSortie = [self.__vars_types_types[i] for i in indexesVarsTypeSortie]
                        total = effectifs[0]
                        effectifs.pop(0)
                        effectifs = [e for e in effectifs if Effectif >= e >= effectif]
                        effectifs.insert(0, total)
                    # première ligne avec l'effectif total et pour chaque type
                    lines.append(effectifs)
                    line = []
                    for indexTp in indexesVarsTypeSortie:
                        try:
                            tp = self.__vars_types_types[indexTp]
                            val = len(collTypes[tp])
                            if val == 0: val = ''
                            line.append(val)
                        except:
                            line.append('')

                    line = [self.collTotal(collTypes)] + line
                    lines.append(line)

                    columns = ['total'] + varsTypeSortie
                    index = ['Effectif', self.__noms[n]]
                    display(pd.DataFrame(lines, columns=columns, index=index))
        else:
            print(color.bold + 'Aucun résultat' + color.end)

    # Comme précédemment, mais les résultats sont donnés par types et en pourcentage
    def show_noms_inclus_types_pourcent(self, nomsGenerateurs=[], nomsGenerateurSauf=[],
                                        vars=[], varSauf=[],
                                        noms=[], nomSauf=[],
                                        varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                        nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                        pourcent=0, Pourcent=100,
                                        effectif=0, Effectif=0,
                                        varsTypeSortie=[], varsTypeSortieSauf=[]):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
        indexesVarsTypeSortie = self.varsTypesToIndexesTypes(varsTypeSortie, varsTypeSortieSauf)

        indexesNomsGenerateurs = self.nomsToIndexesNoms(nomsGenerateurs, nomsGenerateurSauf)

        if varsTypeSortie or varsTypeSortieSauf:
            indexesVarsTypeSortie = self.varsTypesToIndexesTypes(varsTypeSortie, varsTypeSortieSauf)
        else:
            indexesVarsTypeSortie = self.varsTypesToIndexesTypes(varsTypes, varsTypeSauf)

        varsTypeSortie = [self.__vars_types_types[tp] for tp in indexesVarsTypeSortie]

        lisetComplet = self.sum_set(indexesNomsGenerateurs, indexesVars)
        nomsG = [self.__noms[i] for i in indexesNomsGenerateurs]
        print(color.bold + 'Tableau complet :' + color.end)
        print('  Générateurs :')
        if len(indexesNomsGenerateurs) == len(self.__noms):
            print('  Tous')
        else:
            print('  ' + ', '.join(nomsG))

        self.show_liset(lisetComplet, indexesVars)

        indexesNomsInclude = self.noms_inclus(
            indexesNomsGenerateurs, indexesVars, indexesNoms,
            lisetComplet,
            pourcent=pourcent, Pourcent=Pourcent)

        if indexesNomsInclude:
            print("Les nombres donnés sont les pourcentages de variables du type dont les valeurs manquent.")
            for n in indexesNomsInclude:
                lines = []
                l = list(self.__data[n])
                prc = round(self.pourcentLisetIncludes(lisetComplet, l, indexesVars))
                print('')
                print(color.bold + self.__noms[n] + ' : ' + str(prc) + '%' + color.end)
                if not prc == 100:
                    # inutile d'afficher la différence si 100% des valeurs sont les mêmes
                    l = [l[v] for v in indexesVars]
                    lisetDiff = self.difference_liset(liset(l), lisetComplet, indexesVars)
                    # indexes des variables où il y a une différence
                    indexesVarsDiff = self.lisetToIndexesVars(lisetDiff, indexesVars)
                    collTypes = self.indexesVarsToDictTypesIndexesVars(
                        indexesVarsDiff,
                        indexesVarsTypeSortie)

                    effectifs = self.effectifsTypes([n], indexesVars, indexesVarsTypeSortie)

                    if effectif or Effectif:
                        # restriction de indexesVarsTypesSortie
                        if Effectif == 0: Effectif = len(self.__vars)
                        indexesVarsTypeSortie = [indexesVarsTypeSortie[i] \
                                                 for i in range(len(indexesVarsTypeSortie)) \
                                                 if Effectif >= effectifs[i + 1] >= effectif]
                        varsTypeSortie = [self.__vars_types_types[i] for i in indexesVarsTypeSortie]
                        total = effectifs[0]
                        effectifs.pop(0)
                        effectifs = [e for e in effectifs if Effectif >= e >= effectif]
                        effectifs.insert(0, total)

                    # première ligne avec l'effectif total et pour chaque type
                    lines.append(effectifs)
                    line = []
                    for i in range(len(indexesVarsTypeSortie)):
                        indexTp = indexesVarsTypeSortie[i]
                        totalType = effectifs[i + 1]
                        try:
                            tp = self.__vars_types_types[indexTp]
                            val = len(collTypes[tp])
                            prc = round(val / totalType * 100)
                        except:
                            prc = 0
                        if prc:
                            line.append(str(prc) + '%')
                        else:
                            line.append('')

                    line = [self.collTotal(collTypes)] + line
                    lines.append(line)

                    columns = ['total'] + varsTypeSortie
                    index = ['Effectif', self.__noms[n]]
                    display(pd.DataFrame(lines, columns=columns, index=index))
        else:
            print(color.bold + 'Aucun résultat' + color.end)

    # retourne les (indexes des) éditions dans l'image d'une liste
    # de valeurs de variables d'une liste d'éditions
    def noms_image(self, indexesVars, indexesNoms):
        res = []
        for n in indexesNoms:
            nomsImage = self.indexes_like(n, indexesNoms, indexesVars, 100)
            if nomsImage == [n]:
                res.append(n)
        return res

    def vars_base(self, varsBaseIncomplete=[],
                  vars=[], varSauf=[],
                  noms=[], nomSauf=[],
                  varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                  nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                  max=0):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        if not varsBaseIncomplete == []:
            indexesVarsBaseIncomplete = self.varsToIndexesVars(varsBaseIncomplete, [])
        else:
            indexesVarsBaseIncomplete = []

        indexesVarsReste = list(set(indexesVars) - set(indexesVarsBaseIncomplete))
        res = []

        if not max: max = len(indexesVars)

        for indexes in tqdm(sorted(getCombinations(indexesVarsReste,
                                                   max - len(indexesVarsBaseIncomplete)),
                                   key=len)):
            if not includes(indexes, res):
                if self.noms_image(indexes + indexesVarsBaseIncomplete, indexesNoms) == indexesNoms:
                    res.append(sorted(list(set(indexes + indexesVarsBaseIncomplete))))
        return res

    def vars_base_first(self, varsBaseIncomplete=[],
                        vars=[], varSauf=[],
                        noms=[], nomSauf=[],
                        varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                        nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                        max=0):
        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        if not varsBaseIncomplete == []:
            indexesVarsBaseIncomplete = self.varsToIndexesVars(varsBaseIncomplete, [])
        else:
            indexesVarsBaseIncomplete = []

        indexesVarsReste = list(set(indexesVars) - set(indexesVarsBaseIncomplete))

        if not max: max = len(indexesVars)
        res = ''

        for indexes in tqdm(sorted(getCombinations(indexesVarsReste,
                                                   max - len(indexesVarsBaseIncomplete)),
                                   key=len)):
            if self.noms_image(indexes + indexesVarsBaseIncomplete, indexesNoms) == indexesNoms:
                res = sorted(list(set(indexes + indexesVarsBaseIncomplete)))
                break
        return res

    def show_vars_base_first(self, varsBaseIncomplete=[],
                             vars=[], varSauf=[],
                             noms=[], nomSauf=[],
                             varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                             nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                             max=0):

        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        indexes = self.vars_base_first(varsBaseIncomplete=varsBaseIncomplete,
                                       vars=vars, varSauf=varSauf,
                                       noms=noms, nomSauf=nomSauf,
                                       varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                       varsTypesFormule=varsTypesFormule,
                                       nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                                       nomsTypesFormule=nomsTypesFormule,
                                       max=max)

        if indexes:
            varsBase = [self.__vars[i] for i in indexes]
            print(color.bold + ', '.join(varsBase) + color.end)
            for n in indexesNoms:
                nom = self.__noms[n]
                self.show_data(nom, vars=varsBase)
        else:
            print(color.bold + 'Aucun résultat' + color.end)

    def show_vars_base(self, varsBaseIncomplete=[],
                       vars=[], varSauf=[],
                       noms=[], nomSauf=[],
                       varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                       nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                       max=0):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        indexesVarsBase = self.vars_base(varsBaseIncomplete=varsBaseIncomplete,
                                         vars=vars, varSauf=varSauf,
                                         noms=noms, nomSauf=nomSauf,
                                         varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                         varsTypesFormule=varsTypesFormule,
                                         nomsTypes=nomsTypes, nomsTypeSauf=[],
                                         max=max)

        if indexesVarsBase:
            for indexes in indexesVarsBase:
                varsBase = [self.__vars[i] for i in indexes]
                print(color.bold + ', '.join(varsBase) + color.end)
                for n in indexesNoms:
                    nom = self.__noms[n]
                    self.show_data(nom, vars=varsBase)
                print('------------------------------------')
        else:
            print(color.bold + 'Aucun résultat' + color.end)

    ##########################################################################################
    ### Distributions
    ##########################################################################################

    separateurs = [' ', '.', ':', ',', ';', '!', '?', '-', '...']

    def get_langue(self, indexNom):
        indexLangue = self.__vars.index('langue')
        return self.__data[indexNom][indexLangue]

    def find(self, indexNom, indexVar, pattern):
        txt = self.__data[indexNom][indexVar]
        reg = re.compile(pattern)
        res = reg.findall(txt, re.IGNORECASE)
        return len(res)

    def distribution(self, motif, indexNom, indexesVars):
        lang = self.get_langue(indexNom)
        pattern = '|'.join(motif[lang])
        distr = [self.find(indexNom, v, pattern) for v in indexesVars]
        return distr

    # indexes des variables où le motif est présent
    def indexesVars_distribution(self, motif,
                                 noms,
                                 vars=[], varSauf=[],
                                 varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                 pasColonne=10, pasLigne=10):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

        distributions = []

        for nom in noms:
            try:
                indexNom = self.__noms.index(nom)
            except:
                print(color.bold + "Le nom \"" + nom + "\" ne fait pas partie des noms reconnus." + color.end)
                sys.exit(1)
            distributions.append(self.distribution(motif, indexNom, indexesVars))

        indexesVarsDistr = []

        for i in range(len(indexesVars)):
            for n in range(len(noms)):
                if distributions[n][i]:
                    indexesVarsDistr.append(indexesVars[i])
                    break

        return indexesVarsDistr

    # variables où le motif est présent
    def vars_distribution(self, motif,
                          noms,
                          vars=[], varSauf=[],
                          varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                          pasColonne=10, pasLigne=10):

        indexesVars = self.indexesVars_distribution(motif, noms,
                                                    vars=vars, varSauf=varSauf,
                                                    varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                                    varsTypesFormule=varsTypesFormule,
                                                    pasColonne=pasColonne, pasLigne=pasLigne)

        varsDistr = [self.__vars[i] for i in indexesVars]

        return varsDistr

    def show_distribution(self, motif={},
                          vars=[], varSauf=[],
                          noms=[], nomSauf=[],
                          varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                          nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                          pasColonne=10, pasLigne=10):

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
        indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

        distributions = []
        # suppression des blancs avant et après les motifs
        motif = {k: list(map(str.strip, m)) for k, m in motif.items()}

        n = len(indexesNoms)
        for indexNom in indexesNoms:
            distributions.append(self.distribution(motif, indexNom, indexesVars))

        # Représentation en barres
        width = 0.35  # largeur emplacement des barres
        pos = [i * width for i in range(len(indexesVars))]  # placement première barre
        posTicks = [x + width / 2 for x in pos]  # placement ticks
        labels = ['' for i in range(len(indexesVars))]

        fig, ax = plt.subplots()
        for i in range(n):
            posi = [x + i * width / n for x in pos]
            ax.bar(posi, distributions[i], width / n, label=self.__noms[indexesNoms[i]])

        ax.set_ylabel("Nombre d\'occurrences")
        ax.set_title('Occurrences')
        ax.set_xticks(posTicks)
        ax.set_xticklabels(labels)
        ax.legend()

        fig.tight_layout()
        plt.show()

        # Tableau
        vars = [self.__vars[i] for i in indexesVars]

        distributions_blk = []
        # remplace les 0 par des blancs
        for n in range(len(noms)):
            distributions_blk.append([i if not i == 0 else '' for i in distributions[n]])

        lines = distributions_blk
        columns = vars
        index = noms

        if pasColonne:
            res = self.repeteIndex(pasColonne, lines, columns, index)
            lines = res[0]
            columns = res[1]

        if pasLigne:
            res = self.repeteColumns(pasLigne, lines, columns, index)
            lines = res[0]
            index = res[1]

        display(pd.DataFrame(lines, columns=vars, index=noms))

        #return distributions

    # Lexique d'un texte avec fréquences
    def lexiqueFreq(self, indexNom, indexesVars, identifications, mots, motSauf,
                    min, max,
                    ordre, reverse,
                    minfreq, maxfreq):

        words = []
        for v in indexesVars:
            txt = self.__data[indexNom][v]
            words += textToWords(txt)

        words = [w.lower() for w in words]

        # Liste des orbites définies par les identifications
        orbites = wordsToOrbites(words, identifications)

        # Suppression des expressions régulières
        mots = identificationToOrbite(mots, words)
        motSauf = identificationToOrbite(motSauf, words)

        # Réduction de la liste des orbites
        # conditions sur :
        # -- la longueur des mots
        # -- mots exclus
        # -- mots forcés
        orbites = orbitesReduction(orbites,
                                   mots, motSauf, min, max)

        # Lexique avec fréquences
        lexiqueFreq = orbitesToLexiqueFreq(orbites, words)

        # Réduction du lexique aux orbites dont le représentant
        # vérifie les conditions sur les fréquences
        def freqCondition(orbiteFreq, minfreq, maxfreq):
            freqTotal = orbiteFreqTotal(orbiteFreq)
            condition = minfreq <= freqTotal and (maxfreq == 0 or freqTotal <= maxfreq)
            return condition

        lexiqueFreq = [orbite for orbite in lexiqueFreq if freqCondition(orbite, minfreq, maxfreq)]

        # Tri de lexiqueFreq
        lexiqueFreq = sortLexiqueFreq(lexiqueFreq, ordre, reverse)

        return lexiqueFreq

    def show_lexique(self, nom, identifications=[], mots=[], motSauf=[], min=0, max=0,
                     ordre='alpha', reverse=False,
                     minfreq=0, maxfreq=0,
                     vars=[], varSauf=[],
                     varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):

        try:
            indexNom = self.__noms.index(nom)
        except:
            print(color.bold + "Le nom \"" + nom + "\" ne fait pas partie des noms reconnus." + color.end)
            sys.exit(1)

        indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

        if ordre.startswith('fr'):
            ordre = 'freq'
        else:
            ordre = 'alpha'

        # suppression des blancs en début et fin de chaîne
        identifications = [list(map(str.strip, l)) for l in identifications]

        lexiqueFreq = self.lexiqueFreq(indexNom, indexesVars, identifications,
                                       mots, motSauf,
                                       min, max, ordre, reverse,
                                       minfreq, maxfreq)

        lines = []
        index = []
        total = 0
        for orbiteFreq in lexiqueFreq:
            index.append(orbiteFreq[0][0])
            freq = orbiteFreqTotal(orbiteFreq)
            if len(orbiteFreq) > 1:
                line = [orbiteFreqToStr(orbiteFreq), freq]
            else:
                line = ['', freq]
            total += freq
            lines.append(line)
        lines.append(['', total])

        # Affichage du lexique
        display(pd.DataFrame(lines, columns=['orbite', 'fréquence'], index=index + ['Total']))

    #########################################################
    #### Interactivité - fonctions communes
    #########################################################

    # Form Noms
    def form_nom(self, inom):

        form_nom_items = [
            Box([inom],
                layout=titre_layout)
        ]

        form_nom = Box(form_nom_items, layout=Layout(
            display='flex',
            flex_flow='column',
            align_items='stretch'
        ))
        display(form_nom)

    # Form Noms
    def form_noms(self, inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf):

        noms_sub_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-around',
            align_items='stretch'
        )

        nomsTypes_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-around',
            align_items='stretch'
        )

        form_noms_sub_items = [
            Box([Label(value='sélectionnés'), Label(value='exclus')],
                layout=sous_titres_layout),
            Box([inoms, inomSauf], layout=noms_sub_layout)
        ]

        form_noms_sub = Box(form_noms_sub_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 1px',
            justify_content='space-around',
            align_items='stretch',
            width='98%'
        ))

        form_nomsTypes_items = [
            Box([Label(value='Types')],
                layout=titre_layout),
            Box([Label(value='sélectionnés'), Label(value='exclus')],
                layout=sous_titres_layout),
            Box([inomsTypes, inomsTypeSauf],
                layout=nomsTypes_layout),
            Box([Label(value='Formule :'), inomsTypesFormule],
                layout=formule_layout)
        ]

        # nomsTypesExist=len(cor.noms_types_types)!=0
        # visibility=nomsTypesExist,

        form_nomsTypes = Box(form_nomsTypes_items, layout=Layout(
            display='none',
            flex_flow='column',
            border='solid 1px',
            justify_content='space-around',
            align_items='center',
            width='98%'
        ))

        form_noms_items = [
            Box([Label(value='Noms')],
                layout=titre_layout),
            form_noms_sub,
            form_nomsTypes
        ]

        form_noms = Box(form_noms_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 2px',
            justify_content='space-around',
            align_items='center',
            width='100%',
            padding='5px',
            margin='5px'
        ))
        display(form_noms)

    # Form Variables
    def form_vars(self, ivarsTypesFormule,
                  ivarsTypes, ivarsTypeSauf, ivars, ivarSauf):
        vars_sub_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-around'
        )

        varsTypes_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-around'
        )

        form_vars_sub_items = [
            Box([Label(value='sélectionnées'), Label(value='exclues')], layout=sous_titres_layout),
            Box([ivars, ivarSauf], layout=vars_sub_layout)
        ]

        form_vars_sub = Box(form_vars_sub_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 1px',
            justify_content='space-around',
            align_items='stretch',
            padding='5px',
            margin='5px',
            width='98%'

        ))

        form_varsTypes_items = [
            Box([Label(value='Types')],
                layout=titre_layout),
            Box([Label(value='sélectionnés'), Label(value='exclus')],
                layout=sous_titres_layout),
            Box([ivarsTypes, ivarsTypeSauf],
                layout=varsTypes_layout),
            Box([Label(value='Formule :'), ivarsTypesFormule],
                layout=formule_layout)
        ]

        try:
            self.__vars_types_types
            disp = 'flex'
        except:
            disp = 'none'

        form_varsTypes = Box(form_varsTypes_items, layout=Layout(
            display=disp,
            flex_flow='column',
            border='solid 1px',
            justify_content='space-around',
            align_items='stretch',
            width='98%',
            margin='5px',
            padding='5px'
        ))

        form_vars_items = [
            Box([Label(value='Variables')],
                layout=titre_layout),
            form_vars_sub,
            form_varsTypes
        ]

        form_vars = Box(form_vars_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 2px',
            justify_content='space-around',
            align_items='center',
            width='100%',
            padding='5px'
        ))

        display(form_vars)

    # Form pour les types en sortie
    def form_varsTypeSortie(self,
                            ivarsTypeSortie, ivarsTypeSortieSauf):

        varsTypeSortie_sub_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-around',
            justify_items='center'
        )

        form_varsTypeSortie_sub_items = [
            Box([Label(value='sélectionnés'), Label(value='exclus')],
                layout=sous_titres_layout),
            Box([ivarsTypeSortie, ivarsTypeSortieSauf],
                layout=varsTypeSortie_sub_layout)
        ]

        form_varsTypeSortie_sub = Box(form_varsTypeSortie_sub_items, layout=Layout(
            display='flex',
            flex_flow='column',
            align_items='stretch',
            width='98%'
        ))

        form_varsTypeSortie_items = [
            Box([Label(value='Types en sortie')],
                layout=titre_layout),
            form_varsTypeSortie_sub
        ]

        form_varsTypeSortie = Box(form_varsTypeSortie_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 2px',
            justify_content='space-around',
            align_items='stretch',
            width='100%'
        ))
        display(form_varsTypeSortie)

    # Form pour le lexique
    def form_mots(self,
                  imots, imotSauf, iidentifications, iminmax, ifrequences):

        identifications_layout = Layout(
            display='flex',
            height='120px',
            width='600px',
            justify_content="space-around",
            align_content='space-around',
            justify_items='center')

        mots_sub_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-around',
            justify_items='center'
        )

        form_mots_sub_items = [
            Box([Label(value='forcés'), Label(value='exclus')],
                layout=sous_titres_layout),
            Box([imots, imotSauf],
                layout=mots_sub_layout),

            Box([Label(value='identifications')],
                layout=sous_titres_layout),
            Box([Label(value='Chaque ligne contient les mots identifiés séparés par des virgules.')],
                layout=sous_titres_layout),
            Box([iidentifications],
                layout=identifications_layout),

            Box([Label(value='longueurs'), Label(value='fréquences')],
                layout=sous_titres_layout),
            Box([iminmax, ifrequences],
                layout=mots_sub_layout),

        ]

        form_mots_sub = Box(form_mots_sub_items, layout=Layout(
            display='flex',
            flex_flow='column',
            justify_content='space-around',
            align_items='stretch',
            width='98%'
        ))

        form_mots_items = [
            Box([Label(value='Mots')],
                layout=titre_layout),
            form_mots_sub
        ]

        form_mots = Box(form_mots_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 2px',
            justify_content='space-around',
            align_items='center',
            width='100%'
        ))
        display(form_mots)

    # Form deux noms
    def form_2noms(self, inom1, inom2):

        Twonoms_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-around'
        )

        form_2noms_items = [
            Box([inom1, inom2], layout=Twonoms_layout)
        ]

        form_2noms = Box(form_2noms_items, layout=Layout(
            display='flex',
            flex_flow='column',
            align_items='stretch',
            width='100%'
        ))
        display(form_2noms)

    # Form pourcents
    def form_pourcents(self, ipourcents):

        pourcents_sub_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-around'
        )

        form_pourcents_sub_items = [
            Box([ipourcents], layout=pourcents_sub_layout)
        ]

        form_pourcents_sub = Box(form_pourcents_sub_items, layout=Layout(
            display='flex',
            flex_flow='column',
            align_items='center',
            width='98%'
        ))

        form_pourcents_items = [
            Box([Label(value='Pourcents')],
                layout=titre_layout),
            form_pourcents_sub
        ]

        form_pourcents = Box(form_pourcents_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 2px',
            align_items='center',
            width='100%',
            padding='5px'
        ))
        display(form_pourcents)

    # Form effectif
    def form_effectif(self, ieffectif):

        effectif_sub_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-around'
        )

        form_effectif_sub_items = [
            Box([ieffectif], layout=effectif_sub_layout)
        ]

        form_effectif_sub = Box(form_effectif_sub_items, layout=Layout(
            display='flex',
            flex_flow='column',
            align_items='center',
            width='98%'
        ))

        form_effectif_items = [
            Box([Label(value='Effectifs')],
                layout=titre_layout),
            form_effectif_sub
        ]

        form_effectif = Box(form_effectif_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 2px',
            align_items='center',
            width='100%',
            padding='5px'
        ))
        display(form_effectif)

    # Form ordre
    def form_ordre(self, iordre, ireverse):

        ordre_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='center',
            align_items='center',
            width='350px',
            padding='5px')

        form_ordre_items = [
            Box([iordre, ireverse],
                layout=ordre_layout),

        ]

        form_ordre = Box(form_ordre_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 2px',
            align_items='center',
            width='100%',
            padding='5px'
        ))
        display(form_ordre)

        # Form Graphe

    def form_graph(self, iwidth, iheight,
                   ifont_size, ifont_color, inode_color,
                   ilabel_posX, ilabel_posY):

        graph_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-around'
        )

        form_graph_items = [
            Box([Label(value='Apparence du graphe')],
                layout=titre_layout),
            Box([Label(value='largeur'), Label(value='hauteur')],
                layout=sous_titres_layout),
            Box([iwidth, iheight],
                layout=graph_layout),
            Box([Label(value='taille police'), Label(value='couleur police')],
                layout=sous_titres_layout),
            Box([ifont_size, ifont_color],
                layout=graph_layout),
            Box([Label(value='couleur nœud'), Label(value='label x'), Label(value='label y')],
                layout=sous_titres_layout),
            Box([inode_color, ilabel_posX, ilabel_posY],
                layout=graph_layout),
        ]

        form_graph = Box(form_graph_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 2px',
            justify_content='space-around',
            align_items='stretch',
            width='100%',
            padding='5px'
        ))
        display(form_graph)

    # Form pour le motif de distribution
    def form_motif(self, imotifs):

        motif_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-around'

        )

        langues = self.get_langues()
        form_motif_items = [Box([Label(value='Motif')], layout=titre_layout)]
        for lg in langues:
            form_motif_items.append(Box([Label(value=lg + ':'),
                                         imotifs['imotif_' + lg]], layout=motif_layout))

        form_motif = Box(form_motif_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 2px',
            justify_content='space-around',
            align_items='center',
            width='100%',
            padding='5px'
        ))
        display(form_motif)

        #########################################################

    #### Interactivité - variante des fonctions
    #########################################################

    def iiCorrelations(inomClass, istrFiles, istrVarsTypesFiles, istrNomsTypesFiles):
        if istrFiles:
            files = strToList(istrFiles)

            varsTypesFiles = ''
            if istrVarsTypesFiles:
                varsTypesFiles = strListToLists(istrVarsTypesFiles)

            nomsTypesFiles = ''
            if iNomsTypesFiles:
                nomsTypesFiles = strListToLists(istrNomsTypesFiles)

            if inomClass == '':
                nomClass = 'cor'
            else:
                nomClass = inomClass

            exec(nomClass + "=Correlations(files,varsTypes=varsTypesFiles,nomsTypes=nomsTypesFiles)")
            exec(nomClass + ".show_data()")

    def iCorrelations(self):
        istrFiles = widgets.Textarea(
            disabled=False)

        istrVarsTypesFiles = widgets.Textarea(
            disabled=False)
        istrNomsTypesFiles = widgets.Textarea(
            disabled=False)

        inomClass = widgets.Textarea(
            value='cor',
            disabled=False)

        init_sub_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-around'
        )

        nomClass_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='center',
            align_items='center'
        )

        form_init_sub_items = [
            Box([Label('Fichiers des Tableaux de variables')],
                layout=sous_titres_layout),
            Box([istrFiles],
                layout=init_sub_layout),
            Box([Label('Fichiers des Types des Noms'),
                 Label('Fichiers des Types des Variables')],
                layout=sous_titres_layout),
            Box([istrVarsTypesFiles, istrNomsTypesFiles],
                layout=init_sub_layout),
            Box([Label('Nom de la classe : '), inomClass],
                layout=nomClass_layout),

        ]

        form_init_sub = Box(form_init_sub_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 2px',
            align_items='stretch',
            width='98%'
        ))

        form_effectif_items = [
            Box([Label(value='Initialisation')],
                layout=titre_layout),
            form_init_sub
        ]

        form_init = Box(form_init_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 2px',
            align_items='stretch',
            width='100%'
        ))
        display(form_init)

        out = widgets.interactive_output(self.iiCorrelations,
                                         {'inomClass': inomClass, 'istrFiles': istrFiles,
                                          'istrVarsTypesFiles': istrVarsTypesFiles,
                                          'istrNomsTypesFiles': istrNomsTypesFiles})

        display(vbox4, out)

    def iishow_data(self, inoms='', inomSauf='',
                    ivars='', ivarSauf='',
                    ivarsTypes='', ivarsTypeSauf='',
                    ivarsTypesFormule='',
                    inomsTypes='', inomsTypeSauf='', inomsTypesFormule='',
                    ipasColonne=10, ipasLigne=10):

        if inoms:
            noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        vars = self.vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []

        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = ''

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = ''

        self.show_data(
            noms, nomSauf,
            vars, varSauf,
            varsTypes, varsTypeSauf,
            varsTypesFormule,
            nomsTypes=inomsTypes, nomsTypeSauf=inomsTypeSauf,
            nomsTypesFormule=inomsTypesFormule,
            pasColonne=10, pasLigne=10)

    def ishow_data(self):
        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        out = widgets.interactive_output(self.iishow_data,
                                         {'inoms': inoms, 'inomSauf': inomSauf,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf,
                                          'inomsTypesFormule': inomsTypesFormule,
                                          'inomsTypes': inomsTypes,
                                          'inomsTypeSauf': inomsTypeSauf,
                                          })

        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        try:
            display(out)
        except:
            print('Données incomplètes...')

    def iishow_data_pourcent(self, inom = '', inoms = '', inomSauf = '',
                             ipourcents = (0, 0), ivars = '', ivarSauf = '',
                             ivarsTypes = '', ivarsTypeSauf = '', ivarsTypesFormule = '',
                             inomsTypes = '', inomsTypeSauf = '', inomsTypesFormule = '',
                             ipasColonne = 10, ipasLigne = 10) :
        nom = inom
        if inoms:
            if inoms in ['avant', 'Avant']:
                noms = self.nomsAvant(nom)
            elif inoms in ['après', 'Après', 'apres', 'Apres']:
                noms = self.nomsApres(nom)
            else:
                noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        pourcent = ipourcents[0]
        Pourcent = ipourcents[1]
        vars = self.vars[ivars[0]:ivars[1]]

        vars = self.vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = ''

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = ''

        if inomsTypes:
            nomsTypes = strToList(inomsTypes)
        else:
            nomsTypes = ''

        if inomsTypeSauf:
            nomsTypeSauf = strToList(inomsTypeSauf)
        else:
            nomsTypeSauf = ''

        self.show_data_pourcent(nom,
                                noms=noms, nomSauf=nomSauf, pourcent=pourcent, Pourcent=Pourcent,
                                vars=vars, varSauf=varSauf,
                                varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                varsTypesFormule=ivarsTypesFormule,
                                nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                                nomsTypesFormule=inomsTypesFormule,
                                pasColonne=10, pasLigne=10)

    def ishow_data_pourcent(self):
        inom = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False,
        )
        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.vars)],
            min=0,
            max=len(self.vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ipourcents = widgets.IntRangeSlider(
            value=[0, 100],
            min=0,
            max=100,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        out = widgets.interactive_output(self.iishow_data_pourcent,
                                         {'inom': inom, 'inoms': inoms, 'inomSauf': inomSauf,
                                          'ipourcents': ipourcents,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf})

        self.form_nom(inom)
        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_pourcents(ipourcents)
        display(out)

    def iishow_data_only(self, inom='', inoms='', inomSauf='',
                         ivars='', ivarSauf='',
                         ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                         inomsTypes='', inomsTypeSauf='', inomsTypesFormule='',
                         ipasColonne=10, ipasLigne=10):
        nom = inom
        if inoms:
            if inoms in ['avant', 'Avant']:
                noms = self.nomsAvant(nom)
            elif inoms in ['après', 'Après', 'apres', 'Apres']:
                noms = self.nomsApres(nom)
            else:
                noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = ''

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = []

        if inomsTypes:
            nomsTypes = strToList(inomsTypes)
        else:
            nomsTypes = []

        if inomsTypeSauf:
            nomsTypeSauf = strToList(inomsTypeSauf)
        else:
            nomsTypeSauf = []

        self.show_data_only(nom,
                            noms=noms, nomSauf=nomSauf,
                            vars=vars, varSauf=varSauf,
                            varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                            varsTypesFormule=ivarsTypesFormule,
                            nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                            nomsTypesFormule=inomsTypesFormule)

    def ishow_data_only(self):

        inom = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False,
        )
        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        out = widgets.interactive_output(self.iishow_data_only,
                                         {'inom': inom, 'inoms': inoms, 'inomSauf': inomSauf,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf})

        self.form_nom(inom)
        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        display(out)

    def iishow_commun(self, inom1='', inom2='',
                      ivars='', ivarSauf='',
                      ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule=''):
        nom1 = inom1
        nom2 = inom2

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = []

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = []

        self.show_commun(nom1, nom2,
                         vars=vars, varSauf=varSauf,
                         varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                         varsTypesFormule=ivarsTypesFormule)

    def ishow_commun(self):

        inom1 = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False)

        inom2 = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[1],
            disabled=False
        )

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        out = widgets.interactive_output(self.iishow_commun,
                                         {'inom1': inom1, 'inom2': inom2,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf})

        self.form_2noms(inom1, inom2)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        display(out)

    def iishow_commun_types(self, inom1='', inom2='',
                            ivars='', ivarSauf='',
                            ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                            ivarsTypeSortie='', ivarsTypeSortieSauf='',
                            ieffectif=(0, 0)):

        nom1 = inom1
        nom2 = inom2

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = []

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = []

        if ivarsTypeSortie:
            varsTypeSortie = strToList(ivarsTypeSortie)
        else:
            varsTypeSortie = []

        if ivarsTypeSortieSauf:
            varsTypeSortieSauf = strToList(ivarsTypeSortieSauf)
        else:
            varsTypeSortieSauf = []

        effectif = ieffectif[0]
        Effectif = ieffectif[1]

        self.show_commun_types(nom1, nom2,
                               vars=vars, varSauf=varSauf,
                               varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                               varsTypesFormule=ivarsTypesFormule,
                               varsTypeSortie=varsTypeSortie,
                               varsTypeSortieSauf=varsTypeSortieSauf,
                               effectif=effectif, Effectif=Effectif)

    def ishow_commun_types(self):

        inom1 = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False)

        inom2 = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[1],
            disabled=False
        )

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ieffectif = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ivarsTypeSortie = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSortieSauf = widgets.Textarea(layout=textArea_layout)

        # sortie
        out = widgets.interactive_output(self.iishow_commun_types,
                                         {'inom1': inom1, 'inom2': inom2,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf,
                                          'ivarsTypeSortie': ivarsTypeSortie,
                                          'ivarsTypeSortieSauf': ivarsTypeSortieSauf,
                                          'ieffectif': ieffectif})

        self.form_2noms(inom1, inom2)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_effectif(ieffectif)
        self.form_varsTypeSortie(ivarsTypeSortie, ivarsTypeSortieSauf)
        display(out)

    def iishow_difference(self, inom1='', inom2='',
                          ivars='', ivarSauf='',
                          ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule=''):
        nom1 = inom1
        nom2 = inom2

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = []

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = []

        self.show_difference(nom1, nom2,
                             vars=vars, varSauf=varSauf,
                             varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                             varsTypesFormule=ivarsTypesFormule)

    def ishow_difference(self):

        inom1 = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False)

        inom2 = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[1],
            disabled=False
        )

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        out = widgets.interactive_output(self.iishow_difference,
                                         {'inom1': inom1, 'inom2': inom2,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf})

        self.form_2noms(inom1, inom2)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        display(out)

    def iishow_difference_types(self, inom1='', inom2='',
                                ivars='', ivarSauf='',
                                ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                                ivarsTypeSortie='', ivarsTypeSortieSauf='',
                                ieffectif=(0, 0)):

        nom1 = inom1
        nom2 = inom2

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = []

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = []

        if ivarsTypeSortie:
            varsTypeSortie = strToList(ivarsTypeSortie)
        else:
            varsTypeSortie = []

        if ivarsTypeSortieSauf:
            varsTypeSortieSauf = strToList(ivarsTypeSortieSauf)
        else:
            varsTypeSortieSauf = []

        effectif = ieffectif[0]
        Effectif = ieffectif[1]

        self.show_difference_types(nom1, nom2,
                                   vars=vars, varSauf=varSauf,
                                   varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                   varsTypesFormule=ivarsTypesFormule,
                                   varsTypeSortie=varsTypeSortie,
                                   varsTypeSortieSauf=varsTypeSortieSauf,
                                   effectif=effectif, Effectif=Effectif)

    def ishow_difference_types(self):

        inom1 = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False)

        inom2 = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[1],
            disabled=False
        )

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ieffectif = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ivarsTypeSortie = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSortieSauf = widgets.Textarea(layout=textArea_layout)

        # sortie
        out = widgets.interactive_output(self.iishow_difference_types,
                                         {'inom1': inom1, 'inom2': inom2,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf,
                                          'ivarsTypeSortie': ivarsTypeSortie,
                                          'ivarsTypeSortieSauf': ivarsTypeSortieSauf,
                                          'ieffectif': ieffectif})

        self.form_2noms(inom1, inom2)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_effectif(ieffectif)
        self.form_varsTypeSortie(ivarsTypeSortie, ivarsTypeSortieSauf)
        display(out)

    def iishow_tableau_correlations_desc(self, inom='', inoms='', inomSauf='',
                                         ipourcents=(0, 0), ivars='', ivarSauf='',
                                         ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                                         inomsTypes='', inomsTypeSauf='', inomsTypesFormule='',
                                         ipasColonne=10, ipasLigne=10):
        nom = inom
        if inoms:
            if inoms in ['avant', 'Avant']:
                noms = self.nomsAvant(nom)
            elif inoms in ['après', 'Après', 'apres', 'Apres']:
                noms = self.nomsApres(nom)
            else:
                noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        pourcent = ipourcents[0]
        Pourcent = ipourcents[1]
        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = ''

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = ''

        if inomsTypes:
            nomsTypes = strToList(inomsTypes)
        else:
            nomsTypes = ''

        if inomsTypeSauf:
            nomsTypeSauf = strToList(inomsTypeSauf)
        else:
            nomsTypeSauf = ''

        self.show_tableau_correlations_desc(nom,
                                            noms=noms, nomSauf=nomSauf, pourcent=pourcent, Pourcent=Pourcent,
                                            vars=vars, varSauf=varSauf,
                                            varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                            varsTypesFormule=ivarsTypesFormule,
                                            nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                                            nomsTypesFormule=inomsTypesFormule,
                                            pasColonne=10, pasLigne=10)

    def ishow_tableau_correlations_desc(self):
        inom = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False
        )
        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ipourcents = widgets.IntRangeSlider(
            value=[0, 100],
            min=0,
            max=100,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        out = widgets.interactive_output(self.iishow_tableau_correlations_desc,
                                         {'inom': inom, 'inoms': inoms, 'inomSauf': inomSauf,
                                          'ipourcents': ipourcents,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf})

        self.form_nom(inom)
        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_pourcents(ipourcents)
        display(out)

    def iishow_tableau_correlations_asc(self, inom='', inoms='', inomSauf='',
                                        ipourcents=(0, 0), ivars='', ivarSauf='',
                                        ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                                        inomsTypes='', inomsTypeSauf='', inomsTypesFormule='',
                                        ipasColonne=10, ipasLigne=10):
        nom = inom
        if inoms:
            if inoms in ['avant', 'Avant']:
                noms = self.nomsAvant(nom)
            elif inoms in ['après', 'Après', 'apres', 'Apres']:
                noms = self.nomsApres(nom)
            else:
                noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        pourcent = ipourcents[0]
        Pourcent = ipourcents[1]
        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = ''

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = ''

        if inomsTypes:
            nomsTypes = strToList(inomsTypes)
        else:
            nomsTypes = ''

        if inomsTypeSauf:
            nomsTypeSauf = strToList(inomsTypeSauf)
        else:
            nomsTypeSauf = ''

        self.show_tableau_correlations_asc(nom,
                                           noms=noms, nomSauf=nomSauf, pourcent=pourcent, Pourcent=Pourcent,
                                           vars=vars, varSauf=varSauf,
                                           varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                           varsTypesFormule=ivarsTypesFormule,
                                           nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                                           nomsTypesFormule=inomsTypesFormule,
                                           pasColonne=10, pasLigne=10)

    def ishow_tableau_correlations_asc(self):
        inom = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False
        )
        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ipourcents = widgets.IntRangeSlider(
            value=[0, 100],
            min=0,
            max=100,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        out = widgets.interactive_output(self.iishow_tableau_correlations_asc,
                                         {'inom': inom, 'inoms': inoms, 'inomSauf': inomSauf,
                                          'ipourcents': ipourcents,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf})

        self.form_nom(inom)
        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_pourcents(ipourcents)
        display(out)


    def iishow_tableau_correlations_types_desc(self, inom='', inoms='', inomSauf='',
                                               ipourcents=(0, 0), ieffectif=(0, 0), ivars='', ivarSauf='',
                                               ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                                               ivarsTypeSortie='', ivarsTypeSortieSauf='',
                                               inomsTypes='', inomsTypeSauf='', inomsTypesFormule='',
                                               ipasColonne=10, ipasLigne=10):

        nom = inom
        if inoms:
            if inoms in ['avant', 'Avant']:
                noms = self.nomsAvant(nom)
            elif inoms in ['après', 'Après', 'apres', 'Apres']:
                noms = self.nomsApres(nom)
            else:
                noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        pourcent = ipourcents[0]
        Pourcent = ipourcents[1]

        effectif = ieffectif[0]
        Effectif = ieffectif[1]

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = ''

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = ''

        if ivarsTypeSortie:
            varsTypeSortie = strToList(ivarsTypeSortie)
        else:
            varsTypeSortie = ''

        if ivarsTypeSortieSauf:
            varsTypeSortieSauf = strToList(ivarsTypeSortieSauf)
        else:
            varsTypeSortieSauf = ''

        if inomsTypes:
            nomsTypes = strToList(inomsTypes)
        else:
            nomsTypes = ''

        if inomsTypeSauf:
            nomsTypeSauf = strToList(inomsTypeSauf)
        else:
            nomsTypeSauf = ''

        self.show_tableau_correlations_types_desc(nom,
                                                  noms=noms, nomSauf=nomSauf, pourcent=pourcent, Pourcent=Pourcent,
                                                  effectif=effectif, Effectif=Effectif,
                                                  vars=vars, varSauf=varSauf,
                                                  varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                                  varsTypesFormule=ivarsTypesFormule,
                                                  varsTypeSortie=varsTypeSortie, varsTypeSortieSauf=varsTypeSortieSauf,
                                                  nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                                                  nomsTypesFormule=inomsTypesFormule)

    def ishow_tableau_correlations_types_desc(self):
        inom = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False
        )
        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSortie = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSortieSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ieffectif = widgets.IntRangeSlider(
            value=[0, len(self.__noms)],
            min=0,
            max=len(self.__noms),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ipourcents = widgets.IntRangeSlider(
            value=[0, 100],
            min=0,
            max=100,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        out = widgets.interactive_output(self.iishow_tableau_correlations_types_desc,
                                         {'inom': inom, 'inoms': inoms, 'inomSauf': inomSauf,
                                          'ipourcents': ipourcents,
                                          'ieffectif': ieffectif,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf,
                                          'ivarsTypeSortie': ivarsTypeSortie,
                                          'ivarsTypeSortieSauf': ivarsTypeSortieSauf})

        self.form_nom(inom)
        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_pourcents(ipourcents)
        self.form_effectif(ieffectif)
        self.form_varsTypeSortie(ivarsTypeSortie, ivarsTypeSortieSauf)
        display(out)

    def iishow_tableau_correlations_types_asc(self, inom='', inoms='', inomSauf='',
                                              ipourcents=(0, 0), ieffectif=(0, 0), ivars='', ivarSauf='',
                                              ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                                              ivarsTypeSortie='', ivarsTypeSortieSauf='',
                                              inomsTypes='', inomsTypeSauf='', inomsTypesFormule='',
                                              ipasColonne=10, ipasLigne=10):

        nom = inom
        if inoms:
            if inoms in ['avant', 'Avant']:
                noms = self.nomsAvant(nom)
            elif inoms in ['après', 'Après', 'apres', 'Apres']:
                noms = self.nomsApres(nom)
            else:
                noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        pourcent = ipourcents[0]
        Pourcent = ipourcents[1]

        effectif = ieffectif[0]
        Effectif = ieffectif[1]

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = ''

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = ''

        if ivarsTypeSortie:
            varsTypeSortie = strToList(ivarsTypeSortie)
        else:
            varsTypeSortie = ''

        if ivarsTypeSortieSauf:
            varsTypeSortieSauf = strToList(ivarsTypeSortieSauf)
        else:
            varsTypeSortieSauf = ''

        if inomsTypes:
            nomsTypes = strToList(inomsTypes)
        else:
            nomsTypes = ''

        if inomsTypeSauf:
            nomsTypeSauf = strToList(inomsTypeSauf)
        else:
            nomsTypeSauf = ''

        self.show_tableau_correlations_types_asc(nom,
                                                 noms=noms, nomSauf=nomSauf, pourcent=pourcent, Pourcent=Pourcent,
                                                 effectif=effectif, Effectif=Effectif,
                                                 vars=vars, varSauf=varSauf,
                                                 varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                                 varsTypesFormule=ivarsTypesFormule,
                                                 varsTypeSortie=varsTypeSortie, varsTypeSortieSauf=varsTypeSortieSauf,
                                                 nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                                                 nomsTypesFormule=inomsTypesFormule)

    def ishow_tableau_correlations_types_asc(self):
        inom = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False
        )
        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSortie = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSortieSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ieffectif = widgets.IntRangeSlider(
            value=[0, len(self.__noms)],
            min=0,
            max=len(self.__noms),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ipourcents = widgets.IntRangeSlider(
            value=[0, 100],
            min=0,
            max=100,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        out = widgets.interactive_output(self.iishow_tableau_correlations_types_asc,
                                         {'inom': inom, 'inoms': inoms, 'inomSauf': inomSauf,
                                          'ipourcents': ipourcents,
                                          'ieffectif': ieffectif,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf,
                                          'ivarsTypeSortie': ivarsTypeSortie,
                                          'ivarsTypeSortieSauf': ivarsTypeSortieSauf})

        self.form_nom(inom)
        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_pourcents(ipourcents)
        self.form_effectif(ieffectif)
        self.form_varsTypeSortie(ivarsTypeSortie, ivarsTypeSortieSauf)
        display(out)

    def iishow_tableau_correlations_types_pourcent_desc(self, inom = '', inoms = '', inomSauf = '',
                                                        ipourcents = (0, 0), ieffectif = (0, 0), ivars = '', ivarSauf = '',
                                                        ivarsTypes = '', ivarsTypeSauf = '', ivarsTypesFormule = '',
                                                        ivarsTypeSortie = '', ivarsTypeSortieSauf = '',
                                                        inomsTypes = '', inomsTypeSauf = '', inomsTypesFormule = '',
                                                        ipasColonne = 10, ipasLigne = 10):

        nom = inom
        if inoms:
            if inoms in ['avant', 'Avant']:
                noms = self.nomsAvant(nom)
            elif inoms in ['après', 'Après', 'apres', 'Apres']:
                noms = self.nomsApres(nom)
            else:
                noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        pourcent = ipourcents[0]
        Pourcent = ipourcents[1]

        effectif = ieffectif[0]
        Effectif = ieffectif[1]

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []

        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = []

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = []

        if ivarsTypeSortie:
            varsTypeSortie = strToList(ivarsTypeSortie)
        else:
            varsTypeSortie = []

        if ivarsTypeSortieSauf:
            varsTypeSortieSauf = strToList(ivarsTypeSortieSauf)
        else:
            varsTypeSortieSauf = []

        if inomsTypes:
            nomsTypes = strToList(inomsTypes)
        else:
            nomsTypes = []

        if inomsTypeSauf:
            nomsTypeSauf = strToList(inomsTypeSauf)
        else:
            nomsTypeSauf = []

        nomsTypesFormule = inomsTypesFormule


        self.show_tableau_correlations_types_pourcent_desc(nom,
                                                           noms = noms, nomSauf = nomSauf, pourcent = pourcent,
                                                           Pourcent = Pourcent,
                                                           effectif = effectif, Effectif = Effectif,
                                                           vars = vars, varSauf = varSauf,
                                                           varsTypes = varsTypes, varsTypeSauf = varsTypeSauf,
                                                           varsTypesFormule = varsTypesFormule,
                                                           varsTypeSortie = varsTypeSortie,
                                                           varsTypeSortieSauf = varsTypeSortieSauf,
                                                           nomsTypes = nomsTypes, nomsTypeSauf = nomsTypeSauf,
                                                           nomsTypesFormule = nomsTypesFormule)

    def ishow_tableau_correlations_types_pourcent_desc(self):
        inom = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False
        )
        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSortie = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSortieSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ieffectif = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ipourcents = widgets.IntRangeSlider(
            value=[0, 100],
            min=0,
            max=100,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        out = widgets.interactive_output(self.iishow_tableau_correlations_types_pourcent_desc,
                                         {'inom': inom, 'inoms': inoms, 'inomSauf': inomSauf,
                                          'ipourcents': ipourcents,
                                          'ieffectif': ieffectif,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf,
                                          'ivarsTypeSortie': ivarsTypeSortie,
                                          'ivarsTypeSortieSauf': ivarsTypeSortieSauf})

        self.form_nom(inom)
        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_pourcents(ipourcents)
        self.form_effectif(ieffectif)
        self.form_varsTypeSortie(ivarsTypeSortie, ivarsTypeSortieSauf)
        display(out)

    def iishow_tableau_innove(self, inomsDonnes, inoms='', inomSauf='',
                              ivars='', ivarSauf='',
                              ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                              inomsTypes='', inomsTypeSauf='', inomsTypesFormule='',
                              ipasColonne=10, ipasLigne=10):

        nomsDonnes = strToList(inomsDonnes)
        if inoms:
            noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = ''

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = ''

        if inomsTypes:
            nomsTypes = strToList(inomsTypes)
        else:
            nomsTypes = ''

        if inomsTypeSauf:
            nomsTypeSauf = strToList(inomsTypeSauf)
        else:
            nomsTypeSauf = ''

        self.show_tableau_innove(nomsDonnes,
                                 noms=noms, nomSauf=nomSauf,
                                 vars=vars, varSauf=varSauf,
                                 varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                 varsTypesFormule=ivarsTypesFormule,
                                 nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                                 nomsTypesFormule=inomsTypesFormule)

    def ishow_tableau_innove(self):

        inomsDonnes = widgets.Textarea(description='Noms :',
                                       layout=nomsDonnes_layout)
        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ipourcents = widgets.IntRangeSlider(
            value=[0, 100],
            min=0,
            max=100,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        out = widgets.interactive_output(self.iishow_tableau_innove,
                                         {'inomsDonnes': inomsDonnes, 'inoms': inoms, 'inomSauf': inomSauf,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf})

        display(inomsDonnes)
        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        display(out)

    def iishow_tableau_innove_types(self, inomsDonnes='',
                                    ivars='', ivarSauf='',
                                    ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                                    ivarsTypeSortie='', ivarsTypeSortieSauf=''):

        nomsDonnes = strToList(inomsDonnes)

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = []

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = []

        if ivarsTypeSortie:
            varsTypeSortie = strToList(ivarsTypeSortie)
        else:
            varsTypeSortie = []

        if ivarsTypeSortieSauf:
            varsTypeSortieSauf = strToList(ivarsTypeSortieSauf)
        else:
            varsTypeSortieSauf = []

        self.show_tableau_innove_types(nomsDonnes,
                                       vars=vars, varSauf=varSauf,
                                       varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                       varsTypesFormule=ivarsTypesFormule,
                                       varsTypeSortie=varsTypeSortie,
                                       varsTypeSortieSauf=varsTypeSortieSauf)

    def ishow_tableau_innove_types(self):

        inomsDonnes = widgets.Textarea(description='Noms :', value=self.__noms[0],
                                       layout=nomsDonnes_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ieffectif = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ivarsTypeSortie = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSortieSauf = widgets.Textarea(layout=textArea_layout)

        # sortie
        out = widgets.interactive_output(self.iishow_tableau_innove_types,
                                         {'inomsDonnes': inomsDonnes,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf,
                                          'ivarsTypeSortie': ivarsTypeSortie,
                                          'ivarsTypeSortieSauf': ivarsTypeSortieSauf})

        display(inomsDonnes)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_effectif(ieffectif)
        self.form_varsTypeSortie(ivarsTypeSortie, ivarsTypeSortieSauf)
        display(out)

    def iishow_tableau_innove_types_pourcent(self, inomsDonnes='',
                                             inoms='', inomSauf='',
                                             ivars='', ivarSauf='',
                                             ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                                             ivarsTypeSortie='', ivarsTypeSortieSauf='',
                                             inomsTypes='', inomsTypeSauf='', inomsTypesFormule='',
                                             ieffectif=(0, 0),
                                             ipasColonne=10, ipasLigne=10):

        nomsDonnes = strToList(inomsDonnes)
        if inoms:
            noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = []

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = []

        if ivarsTypeSortie:
            varsTypeSortie = strToList(ivarsTypeSortie)
        else:
            varsTypeSortie = []

        if ivarsTypeSortieSauf:
            varsTypeSortieSauf = strToList(ivarsTypeSortieSauf)
        else:
            varsTypeSortieSauf = []

        effectif = ieffectif[0]
        Effectif = ieffectif[1]

        self.show_tableau_innove_types_pourcent(nomsDonnes,
                                                noms=noms, nomSauf=nomSauf,
                                                vars=vars, varSauf=varSauf,
                                                varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                                varsTypesFormule=ivarsTypesFormule,
                                                varsTypeSortie=varsTypeSortie,
                                                varsTypeSortieSauf=varsTypeSortieSauf,
                                                effectif=effectif, Effectif=Effectif)

    def ishow_tableau_innove_types_pourcent(self):

        inomsDonnes = widgets.Textarea(description='Noms :', value=self.__noms[0],
                                       layout=nomsDonnes_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ieffectif = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ivarsTypeSortie = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSortieSauf = widgets.Textarea(layout=textArea_layout)

        # sortie
        out = widgets.interactive_output(self.iishow_tableau_innove_types_pourcent,
                                         {'inomsDonnes': inomsDonnes,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf,
                                          'ivarsTypeSortie': ivarsTypeSortie,
                                          'ivarsTypeSortieSauf': ivarsTypeSortieSauf,
                                          'ieffectif': ieffectif})

        display(inomsDonnes)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_effectif(ieffectif)
        self.form_varsTypeSortie(ivarsTypeSortie, ivarsTypeSortieSauf)
        display(out)

    def iishow_graphe_deviation(self, inom='', inoms='', inomSauf='',
                                ipourcents=(0, 0), ivars='', ivarSauf='',
                                ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                                inomsTypes='', inomsTypeSauf='', inomsTypesFormule='',
                                iwidth='', iheight='',
                                ifont_size='', ifont_color='', inode_color='',
                                ilabel_posX='', ilabel_posY=''):
        nom = inom
        if inoms:
            if inoms in ['avant', 'Avant']:
                noms = self.nomsAvant(nom)
            elif inoms in ['après', 'Après', 'apres', 'Apres']:
                noms = self.nomsApres(nom)
            else:
                noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        pourcent = ipourcents[0]
        Pourcent = ipourcents[1]
        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = ''

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = ''

        if inomsTypes:
            nomsTypes = strToList(inomsTypes)
        else:
            nomsTypes = ''

        if inomsTypeSauf:
            nomsTypeSauf = strToList(inomsTypeSauf)
        else:
            nomsTypeSauf = ''

        if ifont_size:
            font_size = int(ifont_size)
        else:
            font_size = ''

        if ilabel_posX:
            label_posX = int(ilabel_posX)
        else:
            label_posX = ''

        if ilabel_posY:
            label_posY = int(ilabel_posY)
        else:
            label_posY = ''

        self.show_graphe_deviation(nom,
                                   noms=noms, nomSauf=nomSauf, pourcent=pourcent, Pourcent=Pourcent,
                                   vars=vars, varSauf=varSauf,
                                   varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                   varsTypesFormule=ivarsTypesFormule,
                                   nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                                   nomsTypesFormule=inomsTypesFormule,
                                   width=iwidth, height=iheight,
                                   font_size=font_size, font_color=ifont_color,
                                   node_color=inode_color,
                                   label_posX=label_posX, label_posY=label_posY)

    def ishow_graphe_deviation(self):
        inom = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False
        )
        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ipourcents = widgets.IntRangeSlider(
            value=[0, 100],
            min=0,
            max=100,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        iwidth = widgets.Textarea(layout=textArea_layout)
        iheight = widgets.Textarea(layout=textArea_layout)
        ifont_size = widgets.Textarea(layout=textArea_layout)
        ifont_color = widgets.Textarea(layout=textArea_layout)
        inode_color = widgets.Textarea(layout=textArea_layout)
        ilabel_posX = widgets.Textarea(layout=textArea_layout)
        ilabel_posY = widgets.Textarea(layout=textArea_layout)

        # sortie
        out = widgets.interactive_output(self.iishow_graphe_deviation,
                                         {'inom': inom, 'inoms': inoms, 'inomSauf': inomSauf,
                                          'ipourcents': ipourcents,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf,
                                          'iwidth': iwidth, 'iheight': iheight,
                                          'ifont_size': ifont_size, 'ifont_color': ifont_color,
                                          'inode_color': inode_color,
                                          'ilabel_posX': ilabel_posX, 'ilabel_posY': ilabel_posY})

        self.form_nom(inom)
        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_pourcents(ipourcents)
        self.form_graph(iwidth, iheight, ifont_size, ifont_color,
                        inode_color, ilabel_posX, ilabel_posY)
        display(out)

    def iishow_graphe_distance(self, iliens=True, inoms='', inomSauf='',
                               ivars='', ivarSauf='',
                               ivarsTypes='', ivarsTypeSauf='',
                               ivarsTypesFormule='',
                               inomsTypes='', inomsTypeSauf='',
                               inomsTypesFormule='',
                               pourcent=0, Pourcent=100, icouleursLiens=''):

        liens = iliens

        if inoms:
            noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = ''

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = ''

        if inomsTypes:
            nomsTypes = strToList(inomsTypes)
        else:
            nomsTypes = ''

        if inomsTypeSauf:
            nomsTypeSauf = strToList(inomsTypeSauf)
        else:
            nomsTypeSauf = ''

        couleursLiens = icouleursLiens

        self.show_graphe_distance(liens=liens,
                                  noms=noms, nomSauf=nomSauf,
                                  vars=vars, varSauf=varSauf,
                                  varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                  varsTypesFormule=ivarsTypesFormule,
                                  nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                                  nomsTypesFormule=inomsTypesFormule, couleursLiens=couleursLiens)

    def ishow_graphe_distance(self):

        sys.exit('EN COURS')
        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ipourcents = widgets.IntRangeSlider(
            value=[0, 100],
            min=0,
            max=100,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        iwidth = widgets.Textarea(layout=textArea_layout)
        iheight = widgets.Textarea(layout=textArea_layout)
        ifont_size = widgets.Textarea(layout=textArea_layout)
        ifont_color = widgets.Textarea(layout=textArea_layout)
        inode_color = widgets.Textarea(layout=textArea_layout)
        ilabel_posX = widgets.Textarea(layout=textArea_layout)
        ilabel_posY = widgets.Textarea(layout=textArea_layout)

        iliens = widgets.RadioButtons(
            description='liens',
            options=['avec', 'sans'],
            values=[True, False],
            layout={'width': 'max-content'}
        )
        icouleursLiens = widgets.Textarea(layout=textArea_layout)

        # sortie
        out = widgets.interactive_output(self.iishow_graphe_distance,
                                         {'iliens': iliens, 'inoms': inoms, 'inomSauf': inomSauf,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf,
                                          'icouleursLiens': icouleursLiens})

        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_pourcents(ipourcents)
        display(iliens)
        self.form_graph(iwidth, iheight, ifont_size, ifont_color,
                        inode_color, ilabel_posX, ilabel_posY)
        display(out)

    def iishow_like(self, inom='', inoms='', inomSauf='',
                    ipourcent=100, ivars='', ivarSauf='',
                    ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                    inomsTypes='', inomsTypeSauf='', inomsTypesFormule=''):

        nom = inom

        if inoms:
            if inoms in ['avant', 'Avant']:
                noms = self.nomsAvant(nom)
            elif inoms in ['après', 'Après', 'apres', 'Apres']:
                noms = self.nomsApres(nom)
            else:
                noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        pourcent = int(ipourcent)
        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = ''

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = ''

        if inomsTypes:
            nomsTypes = strToList(inomsTypes)
        else:
            nomsTypes = ''

        if inomsTypeSauf:
            nomsTypeSauf = strToList(inomsTypeSauf)
        else:
            nomsTypeSauf = ''

        nomsTypesFormule = inomsTypesFormule

        self.show_like(nom,
                       noms=noms, nomSauf=nomSauf, pourcent=pourcent,
                       vars=vars, varSauf=varSauf,
                       varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                       varsTypesFormule=varsTypesFormule,
                       nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                       nomsTypesFormule=nomsTypesFormule)

    def ishow_like(self):
        inom = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False
        )
        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ipourcent = widgets.FloatSlider(
            value=0,
            min=0,
            max=100,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        out = widgets.interactive_output(self.iishow_like,
                                         {'inom': inom, 'inoms': inoms, 'inomSauf': inomSauf,
                                          'ipourcent': ipourcent,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf,
                                          'inomsTypes': inomsTypes,
                                          'inomsTypeSauf': inomsTypeSauf,
                                          'inomsTypesFormule': inomsTypesFormule})

        self.form_nom(inom)
        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_pourcents(ipourcent)
        display(out)

    def iishow_lexique(self, inom, iidentifications='', imots='', imotSauf='', iminmax=(0, 0),
                       iordre='alpha', ireverse=False,
                       ifrequences=(0, 0),
                       ivars='', ivarSauf='',
                       ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule=''):

        nom = inom
        identifications = strListToLists(iidentifications.replace("\n", ";"))

        mots = list(map(str.strip, strToList(imots)))
        motSauf = list(map(str.strip, strToList(imotSauf)))

        min = iminmax[0]
        max = iminmax[1]

        ordre = iordre
        reverse = (ireverse == 'décroissant')

        minfreq = ifrequences[0]
        maxfreq = ifrequences[1]

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = ''

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = ''

        self.show_lexique(nom,
                          identifications=identifications, mots=mots, motSauf=motSauf,
                          min=min, max=max, ordre=ordre, reverse=reverse,
                          minfreq=minfreq, maxfreq=maxfreq,
                          vars=vars, varSauf=varSauf,
                          varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                          varsTypesFormule=ivarsTypesFormule)

    def ishow_lexique(self):
        inom = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0]
        )
        imots = widgets.Textarea(layout=Layout(width='45%', height='40px'))
        imotSauf = widgets.Textarea(layout=Layout(width='45%', height='40px'))

        iidentifications = widgets.Textarea()

        iminmax = widgets.IntRangeSlider(
            value=[0, 30],
            min=0,
            max=30,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        )

        iordre = widgets.Dropdown(
            options=['alphabétique', 'fréquences'],
            value='alphabétique',
            description='ordre :'
        )

        ireverse = widgets.Dropdown(
            options=['croissant', 'décroissant'],
            value='croissant'
        )

        ifrequences = widgets.IntRangeSlider(
            value=[0, 100],
            min=0,
            max=100,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        )

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        )

        # sortie
        out = widgets.interactive_output(self.iishow_lexique, {'inom': inom, 'iidentifications': iidentifications,
                                                               'imots': imots, 'imotSauf': imotSauf,
                                                               'iminmax': iminmax,
                                                               'iordre': iordre, 'ireverse': ireverse,
                                                               'ifrequences': ifrequences,
                                                               'ivars': ivars, 'ivarSauf': ivarSauf,
                                                               'ivarsTypesFormule': ivarsTypesFormule,
                                                               'ivarsTypes': ivarsTypes,
                                                               'ivarsTypeSauf': ivarsTypeSauf})

        self.form_nom(inom)
        self.form_mots(imots, imotSauf, iidentifications, iminmax, ifrequences)
        self.form_ordre(iordre, ireverse)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        display(out)

    def iishow_distribution(self, **kwargs):

        if kwargs['inoms']:
            noms = strToList(kwargs['inoms'])
        else:
            noms = []
        nomSauf = strToList(kwargs['inomSauf'])

        vars = self.__vars[kwargs['ivars'][0]:kwargs['ivars'][1]]

        if kwargs['ivarSauf'][0] != 0 and kwargs['ivarSauf'][1] != len(self.__vars):
            varSauf = self.__vars[kwargs['ivarSauf'][0]:kwargs['ivarSauf'][1]]
        else:
            varSauf = []
        varsTypesFormule = kwargs['ivarsTypesFormule']

        if kwargs['ivarsTypes']:
            varsTypes = strToList(kwargs['ivarsTypes'])
        else:
            varsTypes = ''

        if kwargs['ivarsTypeSauf']:
            varsTypeSauf = strToList(kwargs['ivarsTypeSauf'])
        else:
            varsTypeSauf = ''

        if kwargs['ivarsTypesFormule']:
            varsTypesFormule = strToList(kwargs['ivarsTypesFormule'])
        else:
            varsTypesFormule = ''

        if kwargs['inomsTypes']:
            nomsTypes = strToList(kwargs['inomsTypes'])
        else:
            nomsTypes = ''

        if kwargs['inomsTypeSauf']:
            nomsTypeSauf = strToList(kwargs['inomsTypeSauf'])
        else:
            nomsTypeSauf = ''

        if kwargs['inomsTypesFormule']:
            nomsTypesFormule = strToList(kwargs['inomsTypesFormule'])
        else:
            nomsTypesFormule = ''

        langues = self.get_langues()
        motif = {}
        for lg in langues:
            motif[lg] = strToList(kwargs['imotif_' + lg])

        self.show_distribution(motif=motif, noms=noms, nomSauf=nomSauf,
                               vars=vars, varSauf=varSauf,
                               varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                               varsTypesFormule=varsTypesFormule, nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                               nomsTypesFormule=nomsTypesFormule)

    def ishow_distribution(self):

        langues = self.get_langues()

        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        params = {'inoms': inoms, 'inomSauf': inomSauf,
                  'ivars': ivars, 'ivarSauf': ivarSauf,
                  'ivarsTypesFormule': ivarsTypesFormule,
                  'ivarsTypes': ivarsTypes,
                  'ivarsTypeSauf': ivarsTypeSauf,
                  'inomsTypesFormule': inomsTypesFormule,
                  'inomsTypes': inomsTypes,
                  'inomsTypeSauf': inomsTypeSauf}
        imotifs = {}
        for lg in langues:
            params['imotif_' + lg] = widgets.Textarea(layout=Layout(display='flex',
                                                                    height='40px',
                                                                    width='300px'))
            imotifs['imotif_' + lg] = params['imotif_' + lg]
        out = widgets.interactive_output(self.iishow_distribution, params)

        self.form_motif(imotifs)
        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        display(out)
        
        
    