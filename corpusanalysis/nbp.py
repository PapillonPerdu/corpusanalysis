'''Introduction

 Le programme ci-dessous offre quelques fonctions pour l'analyse et la représentation des corrélations entre les textes d'un corpus présentées dans un tableau.
 pour activer les widgets, exécuter avant le lancement de jupyter :
jupyter nbextension enable --py widgetsnbextension --sys-prefix'''
# # Le programme

from __future__ import print_function
import numpy as np
import pandas as pd
from sympy import *
import csv
import html
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
import tabulate
import os

from .csvfiles import load_csv
from .basics import *
from .innove import *
from .quotations import *
from .defs import *
from .types import *
from .modalbox import *
from .corpus import *
from .bases import *
from .write import *
from .correlations import *
from .repartition import *
from .coherence import *
from .graphes import *
from .sql import *
from .rules import *

# from .lexique import *
from .optimisation import *
from .matrices import *
# from .interactif import *
# from .distribution import *
from .arraysearch import *

try:
    from tqdm.notebook import tqdm
except:
    print("Le module tqdm.notebook n'a pu être importé.")
    print("Les fonctions suivantes ne seront pas utilisables : ")
    print("     decomposition")
    print("     noms_base_complete")
    print("     vars_base")
    print("     vars_base_first")

if __name__ == "__main__":
    lock = thread.allocate_lock()
    thread.start_new_thread(myfunction, ("Thread #: 1", 2, lock))
    thread.start_new_thread(myfunction, ("Thread #: 2", 2, lock))


class Data:
    '''

    fileIn : list of  csv files containing the  data
    varsTypes : list of csv files containing the types of the variables
    varsDefs : list of csv files containing the types of the names
    baseName : chaîne qui sera ajoutée aux noms des données dans les sorties

     '''

    def __init__(self,
                 db: str = '',
                 csv='',
                 varsTypes=[], varsDefs=[],
                 nomsTypes=[],
                 varsTypesRegles='', nomsTypesRegles='', nomsDefs=[],
                 citations=[],
                 baseName: str = '',
                 instance: str = ''):

        if not instance:
            instance = input('Name of this instance : ')
        self.instanceName = instance

        if csv:
            fl = csv[0] if isinstance(csv, list) else csv
            filename, file_extension = os.path.splitext(fl)
            if file_extension == '.csv':
                self.source = 'csv'
                load_csv(self, csv, varsTypes=varsTypes, varsDefs=varsDefs,
                         nomsTypes=nomsTypes,
                         varsTypesRegles=varsTypesRegles, nomsTypesRegles=nomsTypesRegles,
                         nomsDefs=nomsDefs,
                         citations=citations)
            else:
                print("Extension files must be 'csv'.")
                sys.exit(1)
        elif db:
            self.source = 'db'
            load_db(self, db)
        else:
            answer = input("Do you want to create a new database ? (yes/no) ")
            if answer == 'yes' or answer == 'y':
                dbname = input("Give it a name: ")
                name, extension = os.path.splitext(dbname)
                db = name + '.db'
                self.source = 'db'
                self.data = []
                self.data_augmented = []

                self.noms = []
                self.selectedNoms = []
                self.selectedIndexesNoms = []
                self.nomsTypes_exists = False
                self.noms_types_types = []
                self.noms_types_noms = []
                self.noms_types_data = []
                self.noms_types_defs_dic = []
                self.noms_types_avec_def = []
                self.noms_types_sans_def = []
                self.noms_types_data_augmented = []
                self.noms_tables_dic = []
                self.noms_ids_dic = []
                self.noms_prjts_dic = []
                self.noms_defs_dic = []
                self.nomsDefs_exists = False
                self.noms_augmented = []
                self.noms_sans_def = []

                self.vars = []
                self.selectedVars = []
                self.selectedIndexesVars = []
                self.varsTypes_exists = False
                self.vars_types_types = []
                self.vars_types_vars = []
                self.vars_types_data = []
                self.vars_types_defs_dic = []
                self.vars_types_avec_def = []
                self.noms_types_sans_def = []
                self.vars_types_data_augmented = []
                self.vars_defs_dic = []
                self.varsDefs_exists = False
                self.vars_augmented = []
                self.vars_sans_def = []

                self.citations_exists = False
                self.citations = []

                self.poidsExist = False
                newProject(self, db)
            else:
                sys.exit(1)

        self.poidsExist = False

        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_colwidth', -1)
        np.set_printoptions(threshold=sys.maxsize)

        self.baseName = baseName
        self.instanceName = instance

        # tableau des valeurs avec les fonctionnalités associées
        data_augmented = []
        for n in range(len(self.noms)):
            line = [value_augmented(self, self.data[n][v], n, v) for v in range(len(self.vars))]
            data_augmented.append(line)
        self.data_augmented = data_augmented

        self.card = len(self.data)
        self.selectedCard = len(self.data)
        self.selectedVarsCard = len(self.vars)
        self.distMax = len(self.vars)
        self.selectedDistMax = len(self.vars)

        self.yes = ['yes', 'y', 'Yes', 'Y', 'Oui', 'O', 'oui', 'o']
        self.nuls = ['', ' ', '  ', '-', '?']  # valeurs manquantes
        self.exclus = ['', '  ', '   ', '-', '*', '?', '#']
        self.notStrict = ['', '  ', '   ', '-', '*', '?', '#', '0']
        self.coches = ['*', '#']
        self.logicalOperatorsBinary = ['|', '&']
        self.logicalOperatorsUnary = ['~']
        self.logicalOperators = self.logicalOperatorsBinary + self.logicalOperatorsUnary

        # paramètres graphes de déviation
        self.colorMap = 'gist_heat'
        self.font_size = 14
        self.font_color = 'black'
        self.font_weight = 'normal'
        self.node_color = 'black'
        self.node_size = 20
        self.graph_width = 20
        self.graph_height = 20
        self.label_posX = .1
        self.label_posY = .1

        # paramètres graphes matrice de coordonnées
        self.gmc_font_size = 10
        self.gmc_font_color = 'black'
        self.gmc_node_size = 5
        self.gmc_node_color = 'black'
        self.gmc_label_pos = .5
        self.gmc_width = 20
        self.gmc_height = 20
        self.gmc_label_posX = .1
        self.gmc_label_posY = .1

        show_dashboard(self)

    #########################################################################################
    # Methods from  basics
    ######################################################################################
    try:
        def show_data(self,
                      noms=None, nomSauf=None, vars=None, varSauf=None,
                      varsTypes=None, varsTypeSauf=None, varsTypesFormule='',
                      nomsTypes=None, nomsTypeSauf=None, nomsTypesFormule='',
                      pasColonne=10, pasLigne=10,
                      domaine: str = 'all', corpus: str = 'all',
                      values: bool = True, citations: bool = False, width: str = ''):
            """Display the array of walues for the selected names and variables."""

            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)

            show_data(self, indexes['noms'], indexes['vars'],
                      pasColonne=pasColonne, pasLigne=pasLigne,
                      values=values, citations=citations, width=width)

        def view_data(self,
                      noms=None, nomSauf=None, vars=None, varSauf=None,
                      varsTypes=None, varsTypeSauf=None, varsTypesFormule='',
                      nomsTypes=None, nomsTypeSauf=None, nomsTypesFormule='',
                      pasColonne=10, pasLigne=10,
                      domaine='all', corpus='all',
                      values=True, citations=False, width=''):

            view_data(self, indexesNoms, indexesVars, pasColonne=pasColonne, pasLigne=pasLigne,
                      values=values, citations=citations, width=width)

        def show_vars(self,
                      vars=[], varSauf=[],
                      varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
            """Display the selected variables."""
            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
            show_vars(self, indexesVars)

        def show_noms(self,
                      noms=[], nomSauf=[],
                      nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):

            indexesNoms = getIndexesNoms(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
            show_noms(self, indexesNoms)

        def show_like(self,
                      nom, noms=[], nomSauf=[],
                      vars=[], varSauf=[],
                      varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                      nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                      pourcent=0):

            try:
                indexNom = self.noms.index(nom)
            except:
                print(color.bold + "The name \"" + nom + "\" doesn't exist." + color.end)
                sys.exit(1)

            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
            indexesVars = indexesVarsDefiniesNom(self, indexNom, indexesVars)

            indexesNoms = getIndexesNoms(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
            show_like(self,
                      nom, indexesNoms, indexesVars,
                      pourcent=pourcent)

        def nomsDesc(self, nom):
            return nomsDesc(self, nom)

        def nomsDecsStrict(self, nom):
            return nomsDescStrict(self, nom)

        def nomsAsc(self, nom):
            return nomsAsc(self, nom)

        def nomsAscStrict(self, nom):
            return nomsAscStrict(self, nom)

        def varsAvant(self, var):
            return varsAvant(self, var)

        def varsApres(self, var):
            return varsApres(self, var)

        def typeToIndexesVars(self, tps):
            return typeToIndexesVars(self, tps)

        def typeToIndexesNoms(self, tps):
            return typeToIndexesNoms(self, tps)

        def show_var_types(self, var):
            show_var_types(self, var)

        def show_nom_types(self, nom):
            show_nom_types(self, nom)

        def show_noms_type(self, tp):
            show_noms_type(self, tp)

        def interVars(self,
                      var1, var2=''):
            return interVars(self, var1=var1, var2=var2)

        def interNoms(self,
                      nom1, nom2=''):
            return interNoms(self, nom1=nom1, nom2=nom2)

        def get_vars(self,
                     vars=[], varSauf=[],
                     varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):

            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
            return get_vars(self, indexesVars)

        # Liste des variables sur lesquelles une éditions diffère d'une liste d'éditions
        def vars_difference(self, nom1, nom2,
                            vars=None, varSauf=None,
                            varsTypes=None, varsTypeSauf=None, varsTypesFormule='',
                            domaine='all'):
            indexNom1 = nomToIndex(self, (nom1))
            indexNom2 = nomToIndex(self, (nom2))
            indexes = getIndexes(self, [nom1, nom2], [], [], [], '',
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 'all', domaine)

            return [self.vars[v] for v in vars_difference(self, indexNom1, indexNom2, indexes['vars'])]

        # Liste des variables sur lesquelles une éditions diffère d'une liste d'éditions
        def vars_difference_relative(self,
                                     nom, noms=None, nomSauf=None,
                                     vars=None, varSauf=None,
                                     varsTypes=None, varsTypeSauf=None, varsTypesFormule='',
                                     nomsTypes=None, nomsTypeSauf=None, nomsTypesFormule='',
                                     domaine='all', corpus='all'):

            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)

            return vars_difference_relative(self, indexNom, indexes['Noms'], indexes['Vars'])

        def show_difference_relative(self,
                                     nom, noms=[], nomSauf=[],
                                     vars=[], varSauf=[],
                                     varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                     nomsTypes=[], nomsTypeSauf=[],
                                     corpus='all', domaine='all'):

            indexNom = nomToIndex(self, (nom))
            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            varsDiff = self.vars_difference_relative(nom, indexNom, indexes['Noms'], indexes['Vars'])
            display(pd.DataFrame(columns=varsDiff))

        # Liste des variables sur lesquelles une éditions est égale à une édition d'une liste d'éditions
        def vars_somme_relative(self,
                                nom, noms=[], nomSauf=[],
                                vars=[], varSauf=[],
                                varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                corpus='all', domaine='all'):

            indexNom = nomToIndex(self, (nom))
            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)

            return vars_somme_relative(self, indexNom, indexes['noms'], indexes['vars'])

        def vars_defs(self, str, vars=[], varSauf=[],
                      varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):

            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
            return vars_defs(self, str, indexesVars)

        def show_vars_avec_def(self, vars=[], varSauf=[],
                               varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
            vars_defs = list(self.vars_defs_dic.keys())
            show_vars(self, [v for v in indexesVars if self.vars[v] in vars_defs])

        def show_vars_defs(self, vars=[], varSauf=[],
                           varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
            columns = [self.vars_augmented[v] for v in indexesVars]
            defs = [[self.vars_defs_dic[self.vars[v]] if self.vars_defs_dic[self.vars[v]] else '' for v in indexesVars]]
            df = pd.DataFrame(defs, columns=columns)
            display(HTML(df.to_html(escape=False)))

        def show_vars_sans_def(self, vars=[], varSauf=[],
                               varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
            show_vars(self, [v for v in indexesVars if not self.vars_defs_dic[self.vars[v]]])

        def show_vars_types_types(self, varsTypes=[], varsTypeSauf=[]):
            indexesVarsTypes = varsTypesToIndexesTypes(self, varsTypes, varsTypeSauf)
            show_vars_types(self, [], indexesVarsTypes)

        def vars_types_avec_def(self, varsTypes=[], varsTypeSauf=[]):
            indexesVarsTypes = varsTypesToIndexesTypes(self, varsTypes, varsTypeSauf)
            return vars_types_avec_def(self, indexesVarsTypes)

        def show_vars_types_avec_def(self, varsTypes=[], varsTypeSauf=[]):
            indexesVarsTypes = varsTypesToIndexesTypes(self, varsTypes, varsTypeSauf)
            show_vars_types(self, vars_types_avec_def(self, indexesVarsTypes))

        def vars_types_sans_def(self, varsTypes=[], varsTypeSauf=[]):
            indexesVarsTypes = varsTypesToIndexesTypes(self, varsTypes, varsTypeSauf)
            return vars_types_sans_def(self, indexesVarsTypes)

        def show_vars_types_sans_def(self, varsTypes=[], varsTypeSauf=[]):
            indexesVarsTypes = varsTypesToIndexesTypes(self, varsTypes, varsTypeSauf)
            show_vars_types(self, vars_types_sans_def(self, indexesVarsTypes))

        def noms_defs(self, str, noms=[], nomSauf=[],
                      nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):
            indexesNoms = getIndexesNoms(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
            return noms_defs(self, str, indexesNoms)

        def noms_sans_def(self, noms=[], nomSauf=[],
                          nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):
            indexesNoms = getIndexesNoms(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
            return noms_sans_def(self, indexesNoms)

        def show_noms_sans_def(self, noms=[], nomSauf=[],
                               nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):
            indexesNoms = getIndexesNoms(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
            show_noms(self, [n for n in indexesNoms if not self.noms_defs_dic[self.noms[n]]])

        def noms_avec_def(self, noms=[], nomSauf=[],
                          nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):
            indexesNoms = getIndexesNoms(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
            return noms_avec_def(self, indexesNoms)

        def show_noms_avec_def(self, noms=[], nomSauf=[],
                               nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):
            indexesNoms = getIndexesNoms(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
            show_noms(self, noms_avec_def(self, indexesNoms))

        def show_noms_types_types(self, nomsTypes=[], nomsTypeSauf=[],
                                  pasColonne=10, pasLigne=10):
            indexesNomsTypes = nomsTypesToIndexesTypes(self, nomsTypes, nomsTypeSauf)
            show_noms_types(self, [], indexesNomsTypes,
                            pasColonne=10, pasLigne=10)

        def noms_types_sans_def(self, nomsTypes=[], nomsTypeSauf=[]):
            indexesNomsTypes = nomsTypesToIndexesTypes(self, nomsTypes, nomsTypeSauf)
            return noms_types_sans_def(self, indexesNomsTypes)

        def show_noms_types_sans_def(self, nomsTypes=[], nomsTypeSauf=[],
                                     pasColonne=10, pasLigne=10):
            indexesNomsTypes = nomsTypesToIndexesTypes(self, nomsTypes, nomsTypeSauf)
            show_noms_types(self, noms_types_sans_def(self, indexesNomsTypes),
                            pasColonne=10, pasLigne=10)

        def noms_types_avec_def(self, nomsTypes=[], nomsTypeSauf=[],
                                pasColonne=10, pasLigne=10):
            indexesNomsTypes = nomsTypesToIndexesTypes(self, nomsTypes, nomsTypeSauf)
            return noms_types_avec_def(self, indexesNomsTypes,
                                       pasColonne=10, pasLigne=10)

        def show_noms_types_avec_def(self, nomsTypes=[], nomsTypeSauf=[],
                                     pasColonne=10, pasLigne=10):
            indexesNomsTypes = nomsTypesToIndexesTypes(self, nomsTypes, nomsTypeSauf)
            show_noms_types(self, noms_types_avec_def(self, indexesNomsTypes),
                            pasColonne=10, pasLigne=10)

        # liste des variables vérifiant une liste de regVar
        def varsExt(self, regVars):
            return varsExt(self, regVars)

        # First variable from regVar list
        def varsExtUnique(self, var):
            return varsExtUnique(self, var)

        def show_manque(self, nom,
                        vars=[], varSauf=[],
                        varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):

            indexNom = nomToIndex(self, (nom))
            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

            show_manque(self, indexNom, indexesVars)

        #########################################################################################
        # Methods from types
        #########################################################################################

        def show_noms_types(self,
                            noms=[], nomSauf=[], nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                            nomsTypeSortie=[], nomsTypeSortieSauf=[],
                            pasColonne=10, pasLigne=10):

            indexesNoms = getIndexesNoms(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
            indexesNomsTypeSortie = nomsTypesToIndexesTypes(self, nomsTypeSortie, nomsTypeSortieSauf)
            show_noms_types(self, indexesNoms, indexesNomsTypeSortie,
                            pasColonne=pasColonne, pasLigne=pasLigne)

        def show_vars_types(self, vars=[], varSauf=[],
                            varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                            varsTypeSortie=[], varsTypeSortieSauf=[],
                            pasColonne=10, pasLigne=10):

            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
            indexesVarsTypeSortie = getIndexesVarsTypes(self, varsTypeSortie, varsTypeSortieSauf)

            show_vars_types(self, indexesVars, indexesVarsTypeSortie,
                            pasColonne=pasColonne, pasLigne=pasLigne)

        #########################################################################################
        # Methods from rules
        #########################################################################################
        def show_vars_rules(self, varsTypeSortie=[], varsTypeSortieSauf=[]):

            indexesVarsTypeSortie = getIndexesVarsTypes(self, varsTypeSortie, varsTypeSortieSauf)

            show_vars_rules(self, indexesVarsTypeSortie)

        #########################################################################################
        # Methods from correlations
        #########################################################################################
        def show_difference(self,
                            nom1, nom2, vars=[], varSauf=[],
                            varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):

            indexNom1 = nomToIndex(self, nom1)
            indexNom2 = nomToIndex(self, nom2)
            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
            show_difference(self,
                            indexNom1, indexNom2, indexesVars)

        def show_difference_types(self,
                                  nom1, nom2, vars=[], varSauf=[],
                                  varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                  varsTypeSortie=[], varsTypeSortieSauf=[],
                                  effectifType=0, EffectifType=0,
                                  pourcenType=0, PourcenType=100):

            indexNom1 = nomToIndex(self, nom1)
            indexNom2 = nomToIndex(self, nom2)
            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
            indexesVarsTypeSortie = getIndexesVarsTypes(self, varsTypeSortie, varsTypeSortieSauf)

            show_difference_types(self,
                                  indexNom1, indexNom2, indexesVars, indexesVarsTypeSortie,
                                  effectifType=effectifType, EffectifType=EffectifType,
                                  pourcenType=pourcenType, PourcenType=PourcenType)

        def vars_commun(self,
                        nom1, nom2, vars=[], varSauf=[],
                        varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):

            indexNom1 = nomToIndex(self, nom1)
            indexNom2 = nomToIndex(self, nom2)
            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

            return vars_commun(self, indexNom1, indexNom2, indexesVars)

        def show_commun(self,
                        nom1, nom2, vars=[], varSauf=[],
                        varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):

            indexNom1 = nomToIndex(self, nom1)
            indexNom2 = nomToIndex(self, nom2)
            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
            show_commun(self, indexNom1, indexNom2, indexesVars)

        def show_noms_commun_pourcent(self,
                                      nom, vars=[], varSauf=[],
                                      noms=[], nomSauf=[],
                                      pourcent=0, Pourcent=100,
                                      varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                      nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                      corpus='all', domaine='all',
                                      pasColonne=10, pasLigne=10):
            """
                Tableau des valeurs communes d'un nom avec d'autres noms, en précisant le pourcentage de noms ayant cette valeur.
                L'idée est de récupérer ainsi les variables "rares" communes à deux noms.
               :param self:
               :param nom:
               :param vars:
               :param varSauf:
               :param noms:
               :param nomSauf:
               :param pourcent:
               :param Pourcent:
               :param varsTypes:
               :param varsTypeSauf:
               :param varsTypesFormule:
               :param nomsTypes:
               :param nomsTypeSauf:
               :param nomsTypesFormule:
               :param pasColonne:
               :param pasLigne:
               :return:
               """

            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            show_noms_commun_pourcent(self, indexNom, indexes['noms'], indexes['vars'],
                                      pourcent=pourcent, Pourcent=Pourcent,
                                      pasColonne=pasColonne, pasLigne=pasLigne)

        def show_commun_types(self,
                              nom1, nom2, vars=[], varSauf=[],
                              varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                              varsTypeSortie=[], varsTypeSortieSauf=[],
                              effectifType=0, EffectifType=0,
                              pourcenType=0, PourcenType=100):

            indexNom1 = nomToIndex(self, nom1)
            indexNom2 = nomToIndex(self, nom2)
            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
            indexesVarsTypeSortie = getIndexesVarsTypes(self, varsTypeSortie, varsTypeSortieSauf)

            show_commun_types(self, indexNom1, indexNom2, indexesVars, indexesVarsTypeSortie,
                              effectifType=effectifType, EffectifType=EffectifType,
                              pourcenType=pourcenType, PourcenType=PourcenType)

        def show_discrimine(self,
                            nom, discrimines, vars=[], varSauf=[],
                            varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                            pasColonne=10):

            indexNom = nomToIndex(self, nom)
            indexNom1 = nomToIndex(self, discrimines[0])
            indexNom2 = nomToIndex(self, discrimines[1])
            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

            show_discrimine(self,
                            indexNom, [indexNom1, indexNom2], indexesVars,
                            pasColonne=pasColonne)

        def show_discrimine_types(self,
                                  nom, discrimines, vars=[], varSauf=[],
                                  varsTypes=[], varsTypeSauf=[], varsTypesFormule=[],
                                  varsTypeSortie=[], varsTypeSortieSauf=[],
                                  pasColonne=10):

            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
            indexesVarsTypeSortie = getIndexesVarsTypes(self, varsTypeSortie, varsTypeSortieSauf)

            show_discrimine_types(self,
                                  nom, discrimines, indexesVars, indexesVarsTypeSortie,
                                  pasColonne=pasColonne)

        def show_correlations(self,
                              nom, vars=[], varSauf=[],
                              noms=[], nomSauf=[], dir='both',
                              pourcent=0, Pourcent=100, effectif=0, Effectif=0,
                              varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                              nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                              pasColonne=10, pasLigne=10, corpus='all', domaine='all'):
            """

            :param nom:
            :param vars:
            :param varSauf:
            :param noms:
            :param nomSauf:
            :param pourcent:
            :param Pourcent:
            :param effectif:
            :param Effectif:
            :param varsTypes:
            :param varsTypeSauf:
            :param varsTypesFormule:
            :param nomsTypes:
            :param nomsTypeSauf:
            :param nomsTypesFormule:
            :param pasColonne:
            :param pasLigne:
            :return: Tableau descendant des corrélations
            """

            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            show_correlations(self, indexNom, indexes['noms'], indexes['vars'], dir=dir,
                              pourcent=pourcent, Pourcent=Pourcent, effectif=effectif, Effectif=Effectif,
                              pasColonne=pasColonne, pasLigne=pasLigne)

        def show_correlations_desc(self,
                                   nom, vars=[], varSauf=[],
                                   noms=[], nomSauf=[],
                                   pourcent=0, Pourcent=100, effectif=0, Effectif=0,
                                   varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                   nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                   pasColonne=10, pasLigne=10, corpus='all', domaine='all'):
            """
            :param nom:
            :param vars:
            :param varSauf:
            :param noms:
            :param nomSauf:
            :param pourcent:
            :param Pourcent:
            :param effectif:
            :param Effectif:
            :param varsTypes:
            :param varsTypeSauf:
            :param varsTypesFormule:
            :param nomsTypes:
            :param nomsTypeSauf:
            :param nomsTypesFormule:
            :param pasColonne:
            :param pasLigne:
            :return: Tableau descendant des corrélations
            """

            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)

            show_correlations(self, indexNom, indexes['noms'], indexes['vars'], dir='desc',
                              pourcent=pourcent, Pourcent=Pourcent, effectif=effectif, Effectif=Effectif,
                              pasColonne=pasColonne, pasLigne=pasLigne)

        def show_correlations_asc(self,
                                  nom, vars=[], varSauf=[],
                                  noms=[], nomSauf=[],
                                  pourcent=0, Pourcent=100, effectif=0, Effectif=0,
                                  varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                  nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                  pasColonne=10, pasLigne=10, corpus='all', domaine='all'):
            """
            :param nom:
            :param vars:
            :param varSauf:
            :param noms:
            :param nomSauf:
            :param pourcent:
            :param Pourcent:
            :param effectif:
            :param Effectif:
            :param varsTypes:
            :param varsTypeSauf:
            :param varsTypesFormule:
            :param nomsTypes:
            :param nomsTypeSauf:
            :param nomsTypesFormule:
            :param pasColonne:
            :param pasLigne:
            :return: Tableau ascendant des corrélations
            """
            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            show_correlations(self,
                              indexNom, indexes['noms'], indexes['vars'], dir='asc',
                              pourcent=pourcent, Pourcent=Pourcent, effectif=effectif, Effectif=Effectif,
                              pasColonne=pasColonne, pasLigne=pasLigne)

        def show_correlations_types_desc(self,
                                         nom, vars=[], varSauf=[],
                                         noms=[], nomSauf=[],
                                         pourcent=0, Pourcent=100,
                                         effectifType=0, EffectifType=0,
                                         varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                         varsTypeSortie=[], varsTypeSortieSauf=[],
                                         nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                         corpus='all', domaine='all',
                                         pasColonne=10, pasLigne=10):
            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            indexesVarsTypeSortie = varsTypesToIndexesTypes(self, varsTypeSortie, varsTypeSortieSauf)

            show_correlations_types_desc(self,
                                         indexNom, indexes['noms'], indexes['vars'], indexesVarsTypeSortie,
                                         pourcent=pourcent, Pourcent=Pourcent,
                                         effectifType=effectifType, EffectifType=EffectifType,
                                         pasColonne=pasColonne, pasLigne=pasLigne)

        def show_correlations_types_asc(self,
                                        nom, vars=[], varSauf=[],
                                        noms=[], nomSauf=[],
                                        pourcent=0, Pourcent=100,
                                        effectifType=0, EffectifType=0,
                                        varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                        varsTypeSortie=[], varsTypeSortieSauf=[],
                                        nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                        corpus='all', domaine='all',
                                        pasColonne=10, pasLigne=10):

            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            indexesVarsTypes = varsTypesToIndexesTypes(self, varsTypes, varsTypeSauf)
            indexesVarsTypeSortie = varsTypesToIndexesTypes(self, varsTypeSortie, varsTypeSortieSauf)

            show_correlations_types_asc(self,
                                        indexNom, indexes['noms'], indexes['vars'], indexesVarsTypes,
                                        indexesVarsTypeSortie,
                                        pourcent=pourcent, Pourcent=Pourcent,
                                        effectifType=effectifType, EffectifType=EffectifType,
                                        pasColonne=pasColonne, pasLigne=pasLigne)

        def show_correlations_types_pourcent_desc(self,
                                                  nom, vars=None, varSauf=None,
                                                  noms=None, nomSauf=None,
                                                  pourcent=0, Pourcent=100,
                                                  pourcenType=0, PourcenType=100,
                                                  effectif=0, Effectif=0,
                                                  varsTypes=None, varsTypeSauf=None, varsTypesFormule='',
                                                  varsTypeSortie=None, varsTypeSortieSauf=None,
                                                  nomsTypes=None, nomsTypeSauf=None, nomsTypesFormule='',
                                                  corpus='all', domaine='all',
                                                  pasColonne=10, pasLigne=10):

            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            indexesVarsTypeSortie = varsTypesToIndexesTypes(self, varsTypeSortie, varsTypeSortieSauf)

            show_correlations_types_pourcent_desc(self,
                                                  indexNom, indexes['noms'], indexes['vars'], indexesVarsTypeSortie,
                                                  pourcent=pourcent, Pourcent=Pourcent,
                                                  pourcenType=pourcenType, PourcenType=PourcenType,
                                                  effectif=effectif, Effectif=Effectif,
                                                  pasColonne=pasColonne, pasLigne=pasLigne)

        def show_correlations_types_pourcent_asc(self,
                                                 nom, vars=None, varSauf=None,
                                                 noms=None, nomSauf=None,
                                                 pourcent=0, Pourcent=100,
                                                 pourcenType=0, PourcenType=100,
                                                 effectif=0, Effectif=0,
                                                 varsTypes=None, varsTypeSauf=None, varsTypesFormule='',
                                                 varsTypeSortie=None, varsTypeSortieSauf=None,
                                                 nomsTypes=None, nomsTypeSauf=None, nomsTypesFormule='',
                                                 corpus='all', domaine='all',
                                                 pasColonne=10, pasLigne=10):

            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            indexesVarsTypeSortie = varsTypesToIndexesTypes(self, varsTypeSortie, varsTypeSortieSauf)

            show_correlations_types_pourcent_asc(self,
                                                 indexNom, indexes['noms'], indexes['vars'], indexesVarsTypeSortie,
                                                 pourcent=pourcent, Pourcent=Pourcent,
                                                 pourcenType=pourcenType, PourcenType=PourcenType,
                                                 effectif=effectif, Effectif=Effectif,
                                                 pasColonne=pasColonne, pasLigne=pasLigne)

        def show_discrimine_types_pourcent(self,
                                           nom, discrimines, vars=[], varSauf=[],
                                           varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                           varsTypeSortie=[], varsTypeSortieSauf=[],
                                           pasColonne=10):

            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
            indexesVarsTypeSortie = varsTypesToIndexesTypes(self, varsTypeSortie, varsTypeSortieSauf)

            show_discrimine_types_pourcent(self,
                                           nom, discrimines, indexesVars, indexesVarsTypeSortie,
                                           pasColonne=pasColonne)

        def plot_intervalles(self, nom1, nom2, longueur,
                             vars=[], varSauf=[],
                             varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                             pas=1, elev=0, azim=0):
            indexNom1 = nomToIndex(self, nom1)
            indexNom2 = nomToIndex(self, nom2)
            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

            plot_intervalles(self, indexNom1, indexNom2, indexesVars, longueur,
                             pas=pas, elev=elev, azim=azim)

        #########################################################################################
        # Methods from corpus
        #########################################################################################

        def domaine(self, vars=[], noms=[]):
            """
            :param vars:
            :param noms:
            :return: liste des variables ayant des valeurs sur les variables et les noms considérés
            """
            return domaine(self, vars=vars, noms=noms)

        def show_domaine(self, vars=[], varSauf=[],
                         varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                         noms=[], nomSauf=[],
                         nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):
            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
            indexesNoms = getIndexesNoms(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
            vars = indexesToVars_augmented(self, indexesDomaine(self, indexesVars, indexesNoms))
            printLines(columns=vars)

        def corpus(self, vars=[], varSauf=[],
                   varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                   noms=[], nomSauf=[],
                   nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):
            """
            :param vars:
            :param varSauf:
            :param varsTypes:
            :param varsTypeSauf:
            :param varsTypesFormule:
            :param noms:
            :param nomSauf:
            :param nomsTypes:
            :param nomsTypeSauf:
            :param nomsTypesFormule:
            :return: liste des noms ayant des valeurs sur toutes les variables et les noms considérés
            """

            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
            indexesNoms = getIndexesNoms(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
            indCorpus = indexesCorpus(self, indexesVars, indexesNoms)
            cp = [self.noms[n] for n in indCorpus]
            return cp

        def show_corpus(self, vars=[], varSauf=[],
                        varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                        noms=[], nomSauf=[],
                        nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):
            """

            :param self:
            :param vars:
            :param varSauf:
            :param varsTypes:
            :param varsTypeSauf:
            :param varsTypesFormule:
            :param noms:
            :param nomSauf:
            :param nomsTypes:
            :param nomsTypeSauf:
            :param nomsTypesFormule:
            :return: Affiche les noms ayant des valeurs sur toutes les variables considérées
            """
            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
            indexesNoms = getIndexesNoms(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
            noms = indexesToNoms_augmented(self, indexesCorpus(self, indexesVars, indexesNoms))
            printLines(columns=noms)

        def show_vars_manquantes(self, nom,
                                 vars=[], varSauf=[],
                                 varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
            """
            :param nom:
            :param vars:
            :param varSauf:
            :param varsTypes:
            :param varsTypeSauf:
            :param varsTypesFormule:
            :return: Tableau des variables sans valeur pour le nom donné
            """

            indexNom = nomToIndex(self, nom)
            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
            show_vars_manquantes(self, indexNom, indexesVars)

        def noms_thamous_manquant(self, noms=[], nomSauf=[], nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                  corpus='all'):

            indexesNoms = getIndexesNoms(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
            indexes = corpusdomaine(self, corpus, 'all', indexesNoms, [])
            noms_thamous_manquant(self, indexes['noms'])

        def show_types_vars_manquants(self):
            """
            :return: Tableau des types de variables non attribués.
            """
            show_types_vars_manquants(self)

        def show_types_noms_manquants(self):
            """
            :return:  Tableau des types de noms non attribués.
            """
            show_types_noms_manquants(self)

        def show_vars_types_manquants(self,
                                      vars=[], varSauf=[],
                                      varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
            """
            Tableau des variables sans types
            :param nom:
            :param vars:
            :param varSauf:
            :param varsTypes:
            :param varsTypeSauf:
            :param varsTypesFormule:
            :return: affiche les variables sans types
            """
            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
            show_vars_types_manquants(self, indexesVars)

        def show_noms_types_manquants(self,
                                      noms=[], nomSauf=[],
                                      nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):
            """
            :param noms:
            :param nomSauf:
            :param nomsTypes:
            :param nomsTypeSauf:
            :param nomsTypesFormule:
            :return: affiche les noms sans types
            """
            indexesNoms = getIndexesNoms(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
            show_noms_types_manquants(self, indexesNoms)

        def show_noms_manquants(self,
                                vars=[], varSauf=[],
                                varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                noms=[], nomSauf=[],
                                nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=[]):
            """
            Tableau des noms et des variables pour lesquelles les noms n'ont pas de valeur
            :param vars:
            :param varSauf:
            :param varsTypes:
            :param varsTypeSauf:
            :param varsTypesFormule:
            :param noms:
            :param nomSauf:
            :param nomsTypes:
            :param nomsTypeSauf:
            :param nomsTypesFormule:
            :return: tableau des noms et des variables pour lesquelles les noms n'ont pas de valeur
            """

            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
            indexesNoms = getIndexesNoms(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
            show_noms_manquants(self, indexesNoms, indexesVars)

        # vars définies d'une édition
        def vars_definies(self, nom,
                          vars=[], varSauf=[],
                          varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
            """

            :param nom:
            :param vars:
            :param varSauf:
            :param varsTypes:
            :param varsTypeSauf:
            :param varsTypesFormule:
            :return: liste des variables définies d'un nom
            """
            indexNom = self.nomToIndex(nom)
            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

            return vars_definies(self, indexNom, indexesVars)

        def show_vars_defs_manquantes(self, vars=[], varSauf=[],
                                      varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
            """

            :param vars:
            :param varSauf:
            :param varsTypes:
            :param varsTypeSauf:
            :param varsTypesFormule:
            :return: variables sans définition
            """
            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
            show_vars_defs_manquantes(self, indexesVars)

        def show_noms_defs_manquantes(self, noms=[], nomSauf=[],
                                      nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):
            """
            Tableau des noms sans définition.
            :param vars:
            :param varSauf:
            :param varsTypes:
            :param varsTypeSauf:
            :param varsTypesFormule:
            :return: noms sans définition
            """

            indexesNoms = getIndexesNoms(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
            show_noms_defs_manquantes(self, indexesNoms)

        def show_citations_manquantes(self,
                                      vars=[], varSauf=[],
                                      varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                      noms=[], nomSauf=[],
                                      nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=[]):
            """
            Tableau des valeurs sans citations pour les variables et les noms donnés
            :param vars:
            :param varSauf:
            :param varsTypes:
            :param varsTypeSauf:
            :param varsTypesFormule:
            :param noms:
            :param nomSauf:
            :param nomsTypes:
            :param nomsTypeSauf:
            :param nomsTypesFormule:
            :return: Tableau des valeurs sans citations pour les variables et les noms donnés
            """
            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
            indexesNoms = getIndexesNoms(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

            show_citations_manquantes(self, indexesNoms, indexesVars)

        #########################################################################################
        # Methods from  innove
        #########################################################################################

        def show_data_pourcent(self,
                               nom, noms=[], nomSauf=[],
                               vars=[], varSauf=[],
                               pourcent=0, Pourcent=100,
                               varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                               nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                               corpus='all', domaine='all',
                               pasColonne=10, pasLigne=10):

            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            show_data_pourcent(self, indexNom, indexes['noms'], indexes['vars'],
                               pourcent=pourcent, Pourcent=Pourcent,
                               pasColonne=pasColonne, pasLigne=pasLigne)

        def show_noms_data_pourcent(self,
                                    nom, noms=[], nomSauf=[],
                                    vars=[], varSauf=[],
                                    pourcent=0, Pourcent=100,
                                    varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                    nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                    corpus='all', domaine='all'):

            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            show_noms_data_pourcent(self, indexNom, indexes['noms'], indexes['vars'],
                                    pourcent=pourcent, Pourcent=Pourcent,
                                    pasColonne=pasColonne, pasLigne=pasLigne)

        def show_data_only(self,
                           nom, noms=[], nomSauf=[],
                           vars=[], varSauf=[],
                           varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                           nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                           corpus='all', domaine='all'):
            """
            Tableau des valeurs propres à un nom parmi celles d'une liste de noms et de variables donnés.
            :param nom:
            :param noms:
            :param nomSauf:
            :param vars:
            :param varSauf:
            :param varsTypes:
            :param varsTypeSauf:
            :param varsTypesFormule:
            :param nomsTypes:
            :param nomsTypeSauf:
            :param nomsTypesFormule:
            :return:
            """
            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)

            show_data_only(self, indexNom, indexes['noms'], indexes['vars'])

        def vars_data_pourcent(self,
                               nom, noms=[], nomSauf=[],
                               vars=[], varSauf=[],
                               pourcent=0, Pourcent=100,
                               varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                               nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                               corpus='all', domaine='all'):

            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            return vars_data_pourcent(self, indexNom, indexes['noms'], indexes['vars'],
                                      pourcent=pourcent, Pourcent=Pourcent)

        def show_data_pourcent(self,
                               nom, noms=[], nomSauf=[],
                               vars=[], varSauf=[],
                               pourcent=0, Pourcent=100,
                               varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                               nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                               corpus='all', domaine='all',
                               pasColonne=10, pasLigne=10):
            """
            Affichage des valeurs d'un nom avec le nombre et le pourcentage de noms ayant la même valeur:
            :param nom:
            :param noms:
            :param nomSauf:
            :param vars:
            :param varSauf:
            :param pourcent:
            :param Pourcent:
            :param varsTypes:
            :param varsTypeSauf:
            :param varsTypesFormule:
            :param nomsTypes:
            :param nomsTypeSauf:
            :param nomsTypesFormule:
            :param pasColonne:
            :param pasLigne:
            :return:
            """

            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)

            show_data_pourcent(self,
                               indexNom, indexes['noms'], indexes['vars'],
                               pourcent=pourcent, Pourcent=Pourcent,
                               pasColonne=pasColonne, pasLigne=pasLigne)

        def noms_data_pourcent(self,
                               nom, noms=[], nomSauf=[],
                               vars=[], varSauf=[],
                               pourcent=0, Pourcent=100,
                               varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                               nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):

            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)

            return noms_data_pourcent(self, indexNom, indexes['noms'], indexes['vars'],
                                      pourcent=pourcent, Pourcent=Pourcent)

        def vars_only(self,
                      nom, noms=[], nomSauf=[],
                      vars=[], varSauf=[],
                      varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                      nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                      corpus='all', domaine='all'):

            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            return vars_only(self, indexNom, indexes['noms'], indexes['vars'])

        def vars_innove(self,
                        noms=[], nomSauf=[],
                        vars=[], varSauf=[],
                        varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                        nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                        dir='asc',
                        corpus='all', domaine='all'):

            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            return vars_innove(self, indexes['noms'], indexes['vars'], dir)

        def show_vars_innove(self,
                             noms=None, nomSauf=None,
                             vars=None, varSauf=None,
                             varsTypes=None, varsTypeSauf=None, varsTypesFormule='',
                             nomsTypes=None, nomsTypeSauf=None, nomsTypesFormule='',
                             dir='asc',
                             corpus='all', domaine='all'):

            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)

            show_vars_innove(self, indexes['noms'], indexes['vars'], dir)

        def show_innove(self,
                        noms=[], nomSauf=[],
                        vars=[], varSauf=[],
                        varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                        nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                        dir='asc',
                        corpus='all', domaine='all',
                        pasColonne=10, pasLigne=10):

            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)

            show_innove(self, indexes['noms'], indexes['vars'], dir,
                        pasColonne=pasColonne, pasLigne=pasLigne)

        def show_innove_types(self,
                              noms=[], nomSauf=[],
                              vars=[], varSauf=[],
                              varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                              varsTypeSortie=[], varsTypeSortieSauf=[],
                              nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                              dir='asc',
                              corpus='all', domaine='all',
                              effectifType=0, EffectifType=0,
                              pasColonne=10, pasLigne=10):

            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            indexesVarsTypeSortie = varsTypesToIndexesTypes(self, varsTypeSortie, varsTypeSortieSauf)

            show_innove_types(self, indexes['noms'], indexes['vars'], indexesVarsTypeSortie, dir=dir,
                              effectifType=effectifType, EffectifType=EffectifType,
                              pasColonne=pasColonne, pasLigne=pasLigne)

        def show_innove_types_pourcent(self,
                                       noms=[], nomSauf=[],
                                       vars=[], varSauf=[],
                                       varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                       varsTypeSortie=[], varsTypeSortieSauf=[],
                                       nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                       dir='asc',
                                       corpus='all', domaine='all',
                                       pourcenType=0, PourcenType=100,
                                       effectif=0, Effectif=0,
                                       pasColonne=10, pasLigne=10):

            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            indexesVarsTypeSortie = varsTypesToIndexesTypes(self, varsTypeSortie, varsTypeSortieSauf)

            show_innove_types_pourcent(self, indexes['noms'], indexes['vars'], indexesVarsTypeSortie, dir=dir,
                                       pourcenType=pourcenType, PourcenType=PourcenType,
                                       effectif=effectif, Effectif=Effectif,
                                       pasColonne=pasColonne, pasLigne=pasLigne)

        def show_noms_commun_pourcent(self,
                                      nom, vars=[], varSauf=[],
                                      noms=[], nomSauf=[],
                                      pourcent=0, Pourcent=100,
                                      varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                      nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                      corpus='all', domaine='all',
                                      pasColonne=10, pasLigne=10):
            """
                 Tableau des valeurs communes d'un nom avec d'autres noms, en précisant le pourcentage de noms ayant cette valeur.
                 L'idée est de récupérer ainsi les variables "rares" communes à deux noms.
                :param self:
                :param nom:
                :param vars:
                :param varSauf:
                :param noms:
                :param nomSauf:
                :param pourcent:
                :param Pourcent:
                :param varsTypes:
                :param varsTypeSauf:
                :param varsTypesFormule:
                :param nomsTypes:
                :param nomsTypeSauf:
                :param nomsTypesFormule:
                :param pasColonne:
                :param pasLigne:
                :return:
                """

            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)

            show_noms_commun_pourcent(self, indexNom, indexes['noms'], indexes['vars'],
                                      pourcent=pourcent, Pourcent=Pourcent,
                                      pasColonne=pasColonne, pasLigne=pasLigne)

        def test_traduction(self, nom, vars=[], varSauf=[],
                            varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                            dir='asc'):

            indexNom = nomToIndex(self, nom)
            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

            return test_traduction(self,
                                   indexNom, indexesVars, dir=dir)

        #########################################################################################
        # Methods from  coherence
        #########################################################################################
        def show_coherence(self, noms=None, nomSauf=None, vars=None, varSauf=None,
                           varsTypes=None, varsTypeSauf=None, varsTypesFormule='',
                           nomsTypes=None, nomsTypeSauf=None, nomsTypesFormule='',
                           corpus='all', domaine='all',
                           pasColonne=10, pasLigne=10):

            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)

            show_coherence(self, indexes['noms'], indexes['vars'], pasColonne=pasColonne, pasLigne=pasLigne)

        def show_coherence_pourcent(self, noms=None, nomSauf=None, vars=None, varSauf=None,
                                    varsTypes=None, varsTypeSauf=None, varsTypesFormule='',
                                    nomsTypes=None, nomsTypeSauf=None, nomsTypesFormule='',
                                    corpus='all', domaine='all',
                                    pasColonne=10, pasLigne=10):

            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)

            show_coherence_pourcent(self, indexes['noms'], indexes['vars'], pasColonne=pasColonne, pasLigne=pasLigne)

        def show_coherence_type(self, nom, tp):
            show_coherence_type(self, nom, tp)

        def show_coherence_types(self, nom, varsTypes):
            show_coherence_types(self, nom, varsTypes)

        #########################################################################################
        # Methods from bases
        #########################################################################################
        def show_decomposition(self,
                               nom,
                               nomsBaseIncomplete=[], nomsBaseIncompleteSauf=[],
                               vars=[], varSauf=[],
                               noms=[], nomSauf=[],
                               max=0, pourcent=100, Pourcent=100,
                               varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                               nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                               corpus='all', domaine='positif',
                               pasColonne=10, pasLigne=10):
            """

            :param self:
            :param nom:
            :param nomsBaseIncomplete:
            :param nomsBaseIncompleteSauf:
            :param vars:
            :param varSauf:
            :param noms:
            :param nomSauf:
            :param max:
            :param pourcent: pourcentage inférieur
            :param Pourcent: pourcentage supérieur
            :param varsTypes:
            :param varsTypeSauf:
            :param varsTypesFormule:
            :param nomsTypes:
            :param nomsTypeSauf:
            :param nomsTypesFormule:
            :param pasColonne:
            :param pasLigne:
            :return: Décomposition des valeurs d'un nom en fonction de celles d'autres noms suivant les pourcentages indiqués
            """

            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)

            show_decomposition(self,
                               nom, indexes['noms'], indexes['vars'],
                               nomsBaseIncomplete=nomsBaseIncomplete, nomsBaseIncompleteSauf=nomsBaseIncompleteSauf,
                               max=max, pourcent=pourcent, Pourcent=Pourcent,
                               pasColonne=pasColonne, pasLigne=pasLigne)

        def show_values(self, noms=[], nomSauf=[],
                        vars=[], varSauf=[],
                        varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                        nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                        corpus='all', domaine='all'):

            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)

            show_values(self, indexes['noms'], indexes['vars'])

        def show_noms_inclus(self, nomsGenerateurs=[], nomsGenerateurSauf=[],
                             vars=[], varSauf=[],
                             noms=[], nomSauf=[],
                             varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                             nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                             corpus='all', domaine='all',
                             pourcent=0, Pourcent=100):

            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)

            show_noms_inclus(self, indexes['noms'], indexes['vars'], nomsGenerateurs=nomsGenerateurs,
                             nomsGenerateurSauf=nomsGenerateurSauf,
                             pourcent=pourcent, Pourcent=Pourcent)

        def show_noms_inclus_types(self, nomsGenerateurs=[], nomsGenerateurSauf=[],
                                   vars=[], varSauf=[],
                                   noms=[], nomSauf=[],
                                   varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                   nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                   corpus='all', domaine='all',
                                   pourcent=0, Pourcent=100,
                                   effectif=0, Effectif=0,
                                   varsTypeSortie=[], varsTypeSortieSauf=[]):

            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            indexesVarsTypeSortie = varsTypesToIndexesTypes(self, varsTypeSortie, varsTypeSortieSauf)

            show_noms_inclus_types(self, indexes['noms'], indexes['vars'], indexesVarsTypeSortie,
                                   nomsGenerateurs=nomsGenerateurs, nomsGenerateurSauf=nomsGenerateurSauf,
                                   pourcent=pourcent, Pourcent=Pourcent,
                                   effectif=effectif, Effectif=Effectif)

        def show_noms_inclus_types_pourcent(self, nomsGenerateurs=[], nomsGenerateurSauf=[],
                                            vars=[], varSauf=[],
                                            noms=[], nomSauf=[],
                                            varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                            nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                            pourcent=0, Pourcent=100,
                                            effectif=0, Effectif=0,
                                            varsTypeSortie=[], varsTypeSortieSauf=[]):

            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)

            indexesVarsTypeSortie = varsTypesToIndexesTypes(self, varsTypeSortie, varsTypeSortieSauf)

            show_noms_inclus_types_pourcent(self, indexes['noms'], indexes['vars'], indexesVarsTypeSortie,
                                            nomsGenerateurs=nomsGenerateurs, nomsGenerateurSauf=nomsGenerateurSauf,
                                            pourcent=pourcent, Pourcent=Pourcent,
                                            effectif=effectif, Effectif=Effectif)

        def show_noms_base_complete(self, nomsGenerateurs=[], nomsGenerateurSauf=[],
                                    nomsBaseIncomplete=[],
                                    vars=[], varSauf=[],
                                    noms=[], nomSauf=[],
                                    varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                    nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                    pourcent=100, Pourcent=100, max=0):

            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)

            show_noms_base_complete(self, indexes['noms'], indexes['vars'],
                                    nomsGenerateurs=nomsGenerateurs, nomsGenerateurSauf=nomsGenerateurSauf,
                                    nomsBaseIncomplete=nomsBaseIncomplete,
                                    pourcent=pourcent, Pourcent=Pourcent)

        def show_vars_base_first(self, varsBaseIncomplete=[],
                                 vars=[], varSauf=[],
                                 noms=[], nomSauf=[],
                                 varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                 nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                 max=0):
            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            show_vars_base_first(self, indexes['noms'], indexes['vars'], varsBaseIncomplete=varsBaseIncomplete,
                                 max=max)

        def show_vars_base(self, varsBaseIncomplete=[],
                           vars=[], varSauf=[],
                           noms=[], nomSauf=[],
                           varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                           nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                           corpus='all', domaine='all',
                           max=0):

            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            show_vars_base(self, indexes['noms'], indexes['vars'], varsBaseIncomplete=varsBaseIncomplete,
                           max=max)

        #############################################################################
        # Methods from  repartition
        #############################################################################
        def show_repartition(self,
                             vars=[], varSauf=[],
                             noms=[], nomSauf=[],
                             varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                             nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                             corpus='all', domaine='all'):
            """
            :param self:
            :param vars:
            :param varSauf:
            :param noms:
            :param nomSauf:
            :param varsTypes:
            :param varsTypeSauf:
            :param varsTypesFormule:
            :param nomsTypes:
            :param nomsTypeSauf:
            :param nomsTypesFormule:
            :return: Tableau regroupant les noms ayant les mêmes valeurs sur un ensemble de variable donné
            """

            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            show_repartition(self, indexes['noms'], indexes['vars'])

        def show_popularity(self, vars=[], varSauf=[],
                            noms=[], nomSauf=[],
                            varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                            nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                            domaine='all', corpus='all'):

            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            show_popularity(self, indexes['noms'], indexes['vars'])

        #############################################################################
        # Methods from  graphes
        #############################################################################
        def graph_size(self):
            print(self.graph_width, 'x', self.graph_height)

        def set_graph_width(self, num):
            self.graph_width = num

        def set_graph_height(self, num):
            self.graph_height = num

        def set_graph_width(self, num):
            self.graph_width = num

        def set_graph_height(self, num):
            self.graph_height = num

        def set_font_size(self, num):
            self.font_size = num

        def set_font_color(self, chain):
            self.font_color = chain

        def set_node_color(self, chain):
            self.node_color = chain

        def set_label_posX(self, num):
            self.label_posX = num

        def set_label_posY(self, num):
            self.label_posY = num

        def set_colorMap(self, cm):
            self.colorMap = cm

        def set_graphe(self, width='', height='',
                       font_size='', font_color='',
                       node_color='',
                       label_posX='', label_posY=''):
            set_graphe(self, width, height, font_size, font_color, node_color, label_posX, label_posY)

        def show_graphe_deviation(self, nom, vars=[], varSauf=[],
                                  noms=[], nomSauf=[],
                                  varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                  nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                  pourcent=0, Pourcent=100,
                                  corpus='all', domaine='all',
                                  width='', height='', font_size='', font_color='', node_color='',
                                  label_posX='', label_posY=''):

            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)

            show_graphe_deviation(self, indexNom, indexes['noms'], indexes['vars'],
                                  pourcent=pourcent, Pourcent=Pourcent,
                                  width=width, height=height,
                                  font_size=font_size, font_color=font_color, node_color=node_color,
                                  label_posX=label_posX, label_posY=label_posY)

        def show_graphes_deviation(self, vars=[], varSauf=[],
                                   noms=[], nomSauf=[],
                                   varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                   nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                   pourcent=0, Pourcent=100):

            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            show_graphes_deviation(self, indexes['noms'], indexes['vars'],
                                   pourcent=pourcent, Pourcent=Pourcent)

        #############################################################################
        # Méthodes importée de matrices
        #############################################################################

        def show_graphe_distance(self, liens=True, noms=[], nomSauf=[],
                                 vars=[], varSauf=[],
                                 varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                 nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                 pourcent=0, Pourcent=100, couleursLiens={}):

            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)

            show_graphe_distance(self, indexes['noms'], indexes['vars'], liens=liens,
                                 pourcent=pourcent, Pourcent=Pourcent, couleursLiens=couleursLiens)

        def show_distance_ordonnee(self, noms=[], nomSauf=[],
                                   vars=[], varSauf=[],
                                   varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                   nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                   pourcent=0, Pourcent=100):
            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            show_distance_ordonnee(self, indexes['noms'], indexes['vars'],
                                   pourcent=pourcent, Pourcent=Pourcent)

        def show_distance_matrice(self, nomsI=[], nomsISauf=[],
                                  nomsJ=[], nomsJSauf=[],
                                  vars=[], varSauf=[]):

            show_distance_matrice(self, nomsI=nomsI, nomsISauf=nomsISauf,
                                  nomsJ=nomsJ, nomsJSauf=nomsJSauf,
                                  vars=vars, varSauf=varSauf)

        def show_distance_matrice_pourcent(self,
                                           nomsI=[], nomsISauf=[],
                                           nomsJ=[], nomsJSauf=[],
                                           vars=[], varSauf=[]):
            show_distance_matrice_pourcent(self, nomsI=nomsI, nomsISauf=nomsJSauf,
                                           nomsJ=nomsJ, nomsJSauf=nomsJSauf,
                                           vars=vars, varSauf=varSauf)

        def show_distance_matrice_normalisee(self,
                                             nomsI=[], nomsISauf=[],
                                             nomsJ=[], nomsJSauf=[],
                                             vars=[], varSauf=[]):
            show_distance_matrice_normalisee(self, nomsI=nomsI, nomsISauf=nomsJSauf,
                                             nomsJ=nomsJ, nomsJSauf=nomsJSauf,
                                             vars=vars, varSauf=varSauf)

        def show_distance_matrice_coordonnees(self, noms=[], nomSauf=[],
                                              vars=[], varSauf=[],
                                              varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                              nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):

            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            show_distance_matrice_coordonnees(self, indexes['noms'], indexes['vars'])

        def show_graphe_proximite(self, liens=True, noms=[], nomSauf=[], vars=[], varSauf=[],
                                  varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                  nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                  corpus='all', domaine='all',
                                  pourcent=0, Pourcent=100, couleursLiens={}):

            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            show_graphe_proximite(self, indexes['noms'], indexes['vars'], liens=lien,
                                  pourcent=pourcent, Pourcent=Pourcent, couleursLiens=couleursLiens)

        def show_proximite_ordonnee(self, noms=[], nomSauf=[],
                                    vars=[], varSauf=[],
                                    varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                    nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                    corpus='all', domaine='all',
                                    pourcent=0, Pourcent=100):

            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            show_proximite_ordonnee(self, indexes['noms'], indexes['vars'],
                                    pourcent=pourcent, Pourcent=Pourcent)

        def show_proximite_matrice(self, nomsI=[], nomsISauf=[],
                                   nomsJ=[], nomsJSauf=[],
                                   vars=[], varSauf=[]):

            show_proximite_matrice(self, nomsI=nomsI, nomsISauf=nomsISauf,
                                   nomsJ=nomsJ, nomsJSauf=nomsJSauf,
                                   vars=vars, varSauf=varSauf)

        def show_proximite_matrice_pourcent(self,
                                            nomsI=[], nomsISauf=[],
                                            nomsJ=[], nomsJSauf=[],
                                            vars=[], varSauf=[]):
            show_proximite_matrice_pourcent(self, nomsI=nomsI, nomsISauf=nomsJSauf,
                                            nomsJ=nomsJ, nomsJSauf=nomsJSauf,
                                            vars=vars, varSauf=varSauf)

        def show_proximite_matrice_normalisee(self,
                                              nomsI=[], nomsISauf=[],
                                              nomsJ=[], nomsJSauf=[],
                                              vars=[], varSauf=[]):
            show_proximite_matrice_normalisee(self, nomsI=nomsI, nomsISauf=nomsJSauf,
                                              nomsJ=nomsJ, nomsJSauf=nomsJSauf,
                                              vars=vars, varSauf=varSauf)

        def show_proximite_matrice_coordonnees(self, noms=[], nomSauf=[],
                                               vars=[], varSauf=[],
                                               varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                                               nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                                               corpus='all', domaine='all'):
            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            show_proximite_matrice_coordonnees(self, indexesNoms, indexesVars)

        def set_gmc_width(self, num):
            self.gmc_width = num

        def set_gmc_height(self, num):
            self.gmc_height = num

        def set_gmc_font_size(self, num):
            self.gmc_font_size = num

        def set_gmc_font_color(self, chain):
            self.gmc_font_color = chain

        def set_gmc_node_color(self, chain):
            self.gmc_node_color = chain

        def set_gmc_node_size(self, num):
            self.gmc_node_size = num

        def set_gmc_label_posX(self, num):
            self.gmc_label_posX = num

        def set_gmc_label_posY(self, num):
            self.gmc_label_posY = num

        #########################################################################################
        # Fonctions importées de optimisation
        #########################################################################################
        def show_intervalles(self, nom1, nom2, noms=[], nomSauf=[],
                             vars=[], varSauf=[],
                             varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                             nomsTypes=[], nomsTypeSauf=[],
                             pourcent=100, longueur=1, pas=1):
            indexNom1 = nomToIndex(self, nom1)
            indexNom2 = nomToIndex(self, nom2)
            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            show_intervalles(self, indexNom1, indexNom2, indexes['noms'], indexes['vars'],
                             pourcent=pourcent, longueur=longueur, pas=pas)

        #############################################################################
        # Méthodes importée de arraysearch
        #############################################################################
        def findVars(self,
                     cars, vars=[], varSauf=[]):
            return findVars(self, cars, vars=vars, varSauf=varSauf)

        def show_like(self,
                      nom, noms=[], nomSauf=[],
                      vars=[], varSauf=[],
                      varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                      nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                      corpus='all', domaine='all',
                      pourcent=0):
            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)

            show_like(self, indexNom, indexes['noms'], indexes['vars'],
                      pourcent=pourcent)

        def contains(self,
                     chain, vars=[], varSauf=[],
                     noms=[], nomSauf=[],
                     varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                     nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                     corpus='all', domaine='all'):
            indexes = getIndexes(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule,
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)
            return contains(self,
                            chain, indexes['noms'], indexes['vars'])

        # Recherche les variables ayant une valeur donnée d'une édition
        def findVarsValue(self,
                          nom, cars,
                          vars=[], varSauf=[],
                          varsTypes=[], varsTypeSauf=[],
                          varsTypesFormule=''):
            indexNom = nomToIndex(self, nom)
            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

            return findVarsValue(self,
                                 indexNom, cars, indexesVars)

        def nomsVarsValues(self, varsValues=[], noms=[],
                           nomSauf=[], nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=[]):

            indexesNoms = getIndexesNoms(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

            return nomsVarsValues(self, indexesNoms, varsValues=varsValue)

        def nomsVarsContientValues(self,
                                   varsValues,
                                   noms=[], nomSauf=[],
                                   nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=[]):
            indexesNoms = getIndexesNoms(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

            return nomsVarsContientValues(self, indexesNoms, varsValues=varsValues)

        #############################################################################
        # Méthodes importée de quotations
        #############################################################################
        def vars_citations(self, str, nom, vars=[], varSauf=[],
                           varsTypes=[], varsTypeSauf=[], varsTypesFormule='', corpus='all', domaine='all'):

            indexNom = self.noms.index(nom)
            indexes = getIndexes(self, [nom], [], [], [], '',
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 corpus, domaine)

            return vars_citations(self, str, indexNom, indexes['vars'])

        def indexesVars_avec_citations(self, nom, vars=[], varSauf=[],
                                       varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
            indexNom = nomToIndex(self, nom)
            indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

            return indexesVars_avec_citations(self, indexNom, indexesVars)

        def vars_avec_citations(self, nom, vars=[], varSauf=[],
                                varsTypes=[], varsTypeSauf=[], varsTypesFormule='', domaine='all'):
            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, [nom], [], [], [], '',
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 'all', domaine)
            return vars_avec_citations(self, indexNom, indexes['vars'])

        def show_avec_citations(self, nom, vars=[], varSauf=[],
                                varsTypes=[], varsTypeSauf=[], varsTypesFormule='', domaine='all'):
            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, [nom], [], [], [], '',
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 'all', domaine)
            show_avec_citations(self, indexNom, indexes['vars'])

        def show_sans_citations(self, nom, vars=[], varSauf=[],
                                varsTypes=[], varsTypeSauf=[], varsTypesFormule='', domaine='all'):
            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, [nom], [], [], [], '',
                                 vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule,
                                 'all', domaine)
            show_sans_citations(self, indexNom, indexes['vars'])

        #############################################################################
        # Methods from  write
        #############################################################################

        def write_val_db(self, nom, var, value):
            write_val_db(self, nom, var, value)

        def indexVarToId_db(self, indexVar):
            return indexVarToId_db(self, indexVar)

        def indexNomToId_db(self, indexNom):
            return indexNomToId_db(self, indexNom)

        def rename_var(self, var):
            rename_var(self, var)

        def rename_vars_type(self, type):
            rename_vars_type(self, type)

        def rename_noms_type(self, type):
            rename_noms_type(self, type)

        def delete_nom(self, nom):
            delete_nom(self, nom)

        def delete_var(self, var):
            delete_var(self, var)

        def delete_noms_type(self, type):
            delete_noms_type(self, type)

        def delete_vars_type(self, type):
            delete_vars_type(self, type)

        def rename_nom(self, nom):
            rename_nom(self, nom)

        def add_var(self, newVar, var='', position='after'):
            add_var(self, newVar, var=var, position=position)

        def add_vars(self, newVars, var='', position='after'):
            add_vars(self, newVars, var=var, position=position)

        def add_nom(self, newNom, nom='', position='after', table='', id='', projet=''):
            """Add a new name."""
            add_nom(self, newNom, nom=nom, position=position, table=table, id=id, projet=projet)

        def add_noms(self, newNoms, nom='', position='after'):
            add_noms(self, newNoms, nom=nom, position=position)

        def add_vars_type(self, newType, varsType='', position='after'):
            add_vars_type(self, newType, varsType=varsType, position=position)

        def add_vars_types(self, newTypes, varsType='', position='after'):
            add_vars_types(self, newTypes, varsType=varsType, position=position)

        def add_noms_type(self, newType, nomsType='', position='after'):
            add_noms_type(self, newType, nomsType=nomsType, position=position)

        def add_noms_types(self, newType, nomsType='', position='after'):
            add_noms_type(self, newType, nomsType=nomsType, position=position)

        def write_val(self, nom, var, value):
            write_val(self, nom, var, value)

        def write_citation(self, nom, var, citation):
            write_citation(self, nom, var, citation)

        def write_var_definition(self, var, definition):
            write_var_definition(self, var, definition)

        def write_nom_definition(self, nom, definition):
            write_nom_definition(self, nom, definition)

        def write_var_type_val(self, type, var, value):
            write_var_type_val(self, type=type, var=var, value=value)

        def write_nom_type_val(self, type, nom, value):
            write_nom_type_val(self, type=type, nom=nom, value=value)

        def write_vars(self, nom, vars=[], varSauf=[],
                       varsTypes=[], varsTypeSauf=[], varsTypesFormule='', domaine='all'):
            write_vars(self, nom, vars=vars, varSauf=varSauf,
                       varsTypes=varsTypes, varsTypeSauf=varsTypeSauf, varsTypesFormule=varsTypesFormule,
                       domaine=domaine)

        def write_noms(self, vars=[], varSauf=[], varsTypes=[], varsTypeSauf=[], varsTypesFormule='', domaine='all',
                       noms=[], nomSauf=[], nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='', corpus='all'):
            write_noms(self, vars=vars, varSauf=varSauf,
                       varsTypes=varsTypes, varsTypeSauf=varsTypeSauf, varsTypesFormule=varsTypesFormule,
                       domaine=domaine,
                       noms=noms, nomSauf=nomSauf,
                       nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf, nomsTypesFormule=nomsTypesFormule,
                       corpus=corpus)

        def write_type_vars(self, varsType, vars=[], varSauf=[],
                            varsTypes=[], varsTypeSauf=[], varsTypesFormule='', domaine='all'):
            write_type_vars(self, varsType, vars=vars, varSauf=varSauf,
                            varsTypes=varsTypes, varsTypeSauf=varsTypeSauf, varsTypesFormule=varsTypesFormule,
                            domaine=domaine)

        def write_var_types(self, var, varsTypes=[], varsTypeSauf=[]):
            write_var_types(self, var, varsTypes=varsTypes, varsTypeSauf=varsTypeSauf)

        def write_nom_types(self, nom, nomsTypes=[], nomsTypeSauf=[]):
            write_noms_types(self, nom, nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf)

        def write_type_noms(self, nomsType, noms=[], nomSauf=[],
                            nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='', corpus='all'):
            write_type_noms(self, nomsType, noms=noms, nomSauf=nomSauf,
                            nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf, nomsTypesFormule=nomsTypesFormule,
                            corpus=corpus)

        def write_nom_thamous(self, nom, table, id, projet):
            write_nom_thamous(self, nom, table, id, projet)

        def drop_col_db(self, table, col):
            drop_col_db(self, table, col)

        #############################################################################
        # Methods from sql
        #############################################################################
        def newVar(self, newVar, var, position='after'):
            newVar(self, newVar, var, position)

        def newNom(self, newNom):
            newNom(self, newNom)

        def saveToDb(self):
            saveToDb(self)

    except NameError as e:
        print(e)
    except:
        print(e)
