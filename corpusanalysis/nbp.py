# jupyter nbextension enable --py widgetsnbextension --sys-prefix

from __future__ import print_function
import numpy as np
import pandas as pd
from sympy import *
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
from typing import *

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
                 varsTypes: List[str] = [], varsDefs=[],
                 namesTypes: List[str] = [],
                 varsTypesRegles='', namesTypesRegles='', nomsDefs=[],
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
                         namesTypes=namesTypes,
                         varsTypesRegles=varsTypesRegles, namesTypesRegles=namesTypesRegles,
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
                self.namesTypes_exists = False
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

        self.maxData = 100*100 # Au-delà, un avertissement est envoyé

        self.yes = ['yes', 'y', 'Yes', 'Y', 'Oui', 'O', 'oui', 'o']
        self.nuls = ['', ' ', '  ', '-', '?']  # valeurs manquantes
        self.exclus = ['', '  ', '   ', '-', '*', '?', '#']
        self.notStrict = ['', '  ', '   ', '-', '*', '?', '#']
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
                      names: List[str] = [], namesEx: List[str] = [], vars: List[str] = [], varsEx: List[str] = [],
                      varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                      namesTypes: List[str] = [], namesTypesEx:List[str] = [], namesTypesFormula:str = '',
                      pasColonne:int = 5, pasLigne:int = 5,
                      domain: str = 'all', corpus: str = 'all',
                      values: bool = True, citations: bool = False, width: str = '',
                      variantes: List[str] = [],
                      decoration:bool = True,
                      replaceValues: List[str] = [], replaceNames: List[str] = [], replaceVars: List[str] = [],
                      export = False):
            """Display the values for the selected names and variables."""

            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            show_data(self, indexes['noms'], indexes['vars'], variantes=variantes,
                      pasColonne=pasColonne, pasLigne=pasLigne,
                      values=values, citations=citations, width=width, decoration=decoration,
                      replaceValues=replaceValues,replaceNames=replaceNames,replaceVars=replaceVars,
                      export = export )


        def show_vars(self,
                      vars: List[str] = [], varsEx: List[str] = [],
                      varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = ''):
            """Display the selected variables."""
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            show_vars(self, indexesVars)

        def show_names(self,
                       names: List[str] = [], namesEx: List[str] = [],
                       namesTypes: List[str] = [], namesTypeEx: List[str] = [], namesTypesFormula:str = ''):
            """Display the selected names."""
            indexesNoms = getIndexesNoms(self, names, namesEx, namesTypes, namesTypeEx, namesTypesFormula)
            show_names(self, indexesNoms)

        def namesBelow(self, name):
            """List of the names below the given name (included)."""
            return namesBelow(self, name)

        def namesBelowStrict(self, name):
            """List of the names below the given name (excluded)."""
            return namesBelowStrict(self, name)

        def namesAbove(self, name):
            """List of the names above the given name (included)."""
            return namesAbove(self, name)

        def namesAboveStrict(self, name):
            """List of the names above the given name (excluded)."""
            return namesAboveStrict(self, name)

        def varsBefore(self, var):
            """List of the variable before the given variable (included)."""
            return varsBefore(self, var)

        def varsAfter(self, var):
            """List of the variable after the given variable (included)."""
            return varsAfter(self, var)

        def show_vars_type(self, tp):
            """Display the variables with the given type."""
            show_vars_type(self, tp)

        def show_names_type(self, tp):
            """Display the names with the given type."""
            show_names_type(self, tp)

        def varsInter(self,
                      var1, var2=''):
            """List of variables between two variables."""
            return varsInter(self, var1=var1, var2=var2)

        def namesInter(self,
                       name1, name2=''):
            """List of names between two names."""
            return interNames(self, name1=name1, name2=name2)


        def vars_difference(self, name1, name2,
                            vars: List[str] = [], varsEx: List[str] = [],variantes: List[str]=[],
                            varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                            domain:str = 'all'):
            """List of variables on which two names are different."""
            indexNom1 = nomToIndex(self, (name1))
            indexNom2 = nomToIndex(self, (name2))
            indexes = getIndexes(self, [name1, name2], [], [], [], '',
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 'all', domain)

            return [self.vars[v] for v in vars_difference(self, indexNom1, indexNom2, indexes['vars'],variantes=variantes)]

        def vars_relative_difference(self,
                                     name, names: List[str] = [], namesEx: List[str] = [],
                                     vars: List[str] = [], varsEx: List[str] = [],variantes: List[str] = [],
                                     varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                     namesTypes: List[str] = [], namesTypesEx:List[str] = [], namesTypesFormula:str = '',
                                     domain:str = 'all', corpus:str = 'all'):
            """List of variables on which a name differs from a list of names"""
            indexNom = nomToIndex(self, name)
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)

            return vars_relative_difference(self, indexNom, indexes['noms'], indexes['vars'],variantes=variantes)

        def show_relative_difference(self,
                                     name, names: List[str] = [], namesEx: List[str] = [],
                                     vars: List[str] = [], varsEx: List[str] = [], variantes: List[str] = [],
                                     varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                     namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str ='',
                                     pasColonne=10,
                                     corpus:str = 'all', domain:str = 'all'):
            """Display the values of a name on the variables on which it differs from a list of names"""
            indexNom = nomToIndex(self, name)
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            varsDiff = vars_relative_difference(self,indexNom, indexes['noms'], indexes['vars'], variantes=variantes)
            self.show_data(names=[name],vars=varsDiff, pasColonne=pasColonne)


        def vars_relative_sum(self,
                              nom, names: List[str] = [], namesEx: List[str] = [],
                              vars: List[str] = [], varsEx: List[str] = [],
                              varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                              namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                              variantes: List[str] = [],
                              corpus:str = 'all', domain:str = 'all'):
            """List of variables on which a name is equal to one of the names in a list of names."""
            indexNom = nomToIndex(self, (nom))
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)

            return vars_relative_sum(self, indexNom, indexes['noms'], indexes['vars'], variantes=variantes)

        def vars_defs(self, str, vars: List[str] = [], varsEx: List[str] = [],
                      varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = ''):
            """List of variables with a definition."""
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            return vars_defs(self, str, indexesVars)

        def show_vars_with_def(self, vars: List[str] = [], varsEx: List[str] = [],
                               varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = ''):
            """Display the variables with a definition."""
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            vars_defs = list(self.vars_defs_dic.keys())
            show_vars(self, [v for v in indexesVars if self.vars[v] in vars_defs])

        def show_vars_defs(self, vars: List[str] = [], varsEx: List[str] = [],
                           varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = ''):
            """Display variables with their definition."""
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            columns = [self.vars_augmented[v] for v in indexesVars]
            defs = [[self.vars_defs_dic[self.vars[v]] if self.vars_defs_dic[self.vars[v]] else '' for v in indexesVars]]
            df = pd.DataFrame(defs, columns=columns)
            display(HTML(df.to_html(escape=False)))


        def show_vars_without_def(self, vars: List[str] = [], varsEx: List[str] = [],
                                  varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = ''):
            """Display variables without definition."""
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            show_vars(self, [v for v in indexesVars if not self.vars_defs_dic[self.vars[v]]])

        def show_vars_types_types(self, varsTypes: List[str] = [], varsTypesEx: List[str] = []):
            """Display the variables types."""
            indexesVarsTypes = varsTypesToIndexesTypesExt(self, varsTypes, varsTypesEx)
            show_vars_types(self, [], indexesVarsTypes)

        def vars_types_with_def(self, varsTypes: List[str] = [], varsTypesEx: List[str] = []):
            """List of variable types whith definition."""
            indexesVarsTypes = varsTypesToIndexesTypesExt(self, varsTypes, varsTypesEx)
            return vars_types_with_def(self, indexesVarsTypes)

        def show_vars_types_with_def(self, varsTypes: List[str] = [], varsTypesEx: List[str] = []):
            """Display the variable types with definition."""
            indexesVarsTypes = varsTypesToIndexesTypesExt(self, varsTypes, varsTypesEx)
            show_vars_types(self, vars_types_avec_def(self, indexesVarsTypes))

        def vars_types_without_def(self, varsTypes: List[str] = [], varsTypesEx: List[str] = []):
            """List of variable types whithout definition."""
            indexesVarsTypes = varsTypesToIndexesTypesExt(self, varsTypes, varsTypesEx)
            return vars_types_without_def(self, indexesVarsTypes)

        def show_vars_types_without_def(self, varsTypes: List[str] = [], varsTypesEx: List[str] = []):
            """Display the variable types without definition."""
            indexesVarsTypes = varsTypesToIndexesTypesExt(self, varsTypes, varsTypesEx)
            show_vars_types(self, vars_types_sans_def(self, indexesVarsTypes))

        def names_defs(self, str, names: List[str] = [], namesEx: List[str] = [],
                       namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = ''):
            """List of names with a definition."""
            indexesNoms = getIndexesNoms(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula)
            return names_defs(self, str, indexesNoms)

        def names_without_def(self, names: List[str] = [], namesEx: List[str] = [],
                              namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = ''):
            """List of names without a definition."""
            indexesNoms = getIndexesNoms(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula)
            return names_without_def(self, indexesNoms)

        def show_names_without_def(self, names: List[str] = [], namesEx: List[str] = [],
                                   namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = ''):
            """Display the names without a definition."""
            indexesNoms = getIndexesNoms(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula)
            show_names(self, [n for n in indexesNoms if not self.noms_defs_dic[self.noms[n]]])

        def names_with_def(self, names: List[str] = [], namesEx: List[str] = [],
                           namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = ''):
            """List of names with a definition."""
            indexesNoms = getIndexesNoms(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula)
            return names_with_def(self, indexesNoms)

        def show_names_with_def(self, names: List[str] = [], namesEx: List[str] = [],
                                namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = ''):
            """Display the names with a definition."""
            indexesNoms = getIndexesNoms(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula)
            show_names(self, noms_avec_def(self, indexesNoms))

        def show_names_types_types(self, namesTypes: List[str] = [], namesTypesEx: List[str] = []):
            """Display the names types."""
            indexesNomsTypes = nomsTypesToIndexesTypes(self, namesTypes, namesTypesEx)
            show_names_types(self, [], indexesNomsTypes,
                             pasColonne = 10, pasLigne= 10)

        def names_types_without_def(self, namesTypes: List[str] = [], namesTypesEx: List[str] = []):
            """List of name types without a definition."""
            indexesNomsTypes = nomsTypesToIndexesTypes(self, namesTypes, namesTypesEx)
            return names_types_without_def(self, indexesNomsTypes)

        def show_names_types_without_def(self, namesTypes: List[str] = [], namesTypesEx: List[str] = []):
            """Display the name types without a definition."""
            indexesNomsTypes = nomsTypesToIndexesTypes(self, namesTypes, namesTypesEx)
            show_names_types(self, noms_types_sans_def(self, indexesNomsTypes),
                             pasColonne = 10, pasLigne = 10)

        def names_types_with_def(self, namesTypes: List[str] = [], namesTypesEx: List[str] = []):
            """List of name types with a definition."""
            indexesNomsTypes = nomsTypesToIndexesTypes(self, namesTypes, namesTypesEx)
            return names_types_with_def(self, indexesNomsTypes,
                                       pasColonne = 10, pasLigne = 10)

        def show_names_types_with_def(self, namesTypes: List[str] = [], namesTypesEx: List[str] = []):
            """Display name types with a definition."""
            indexesNomsTypes = nomsTypesToIndexesTypes(self, namesTypes, namesTypesEx)
            show_names_types(self, names_types_with_def(self, indexesNomsTypes),
                             pasColonne = 10, pasLigne = 10)


        def varsExt(self, regVars):
            """List of variables checking a list of regVars"""
            return varsExt(self, regVars)

        def namesExt(self, regNames):
            """List of names checking a list of regNames"""
            return nomsExt(self, regNames)

        def nomsTypesExt(self, regNames):
            """List of names Types checking a list of regNames"""
            # todo : à faire
            return nomsTypesExt(self, regNames)

        def varsTypesExt(self, regNames):
            """List of vars Types  checking a list of regNames"""
            # todo : à faire
            return varsTypesExt(self, regNames)



        def show_missing(self, name,
                         vars: List[str] = [], varsEx: List[str] = [],
                         varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = ''):
            """Display variables for which a name has no assigned values."""
            indexNom = nomToIndex(self, (name))
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            show_missing(self, indexNom, indexesVars)

        def typeToIndexesNoms(self, tp):
            # Needed for nomsTypesFormula
            return typeToIndexesNoms(self, tp)



        def typeToIndexesVars(self, tp):
            #Needed for varsTypesFormula
            return typeToIndexesVars(self,tp)



        #########################################################################################
        # Methods from types
        #########################################################################################

        def show_names_types(self,
                             names: List[str] = [], namesEx: List[str] = [], namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                             namesTypesOutput=[], namesTypesOutputEx=[],
                             pasColonne:int = 5, pasLigne:int = 5):
            """Display the types of names"""
            indexesNoms = getIndexesNoms(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula)
            indexesNomsTypeSortie = nomsTypesToIndexesTypes(self, namesTypesOutput, namesTypesOutputEx)
            show_names_types(self, indexesNoms, indexesNomsTypeSortie,
                             pasColonne=pasColonne, pasLigne=pasLigne)
        def show_name_types(self, name,
                            namesTypesOutput:List[str] = [], namesTypesOutputEx:List[str] = [],
                            pasColonne:int = 5):
            """Display the selected types of the variable"""
            indexName = nomToIndex(self, name)
            indexesNamesTypeSortie = varsTypesToIndexesTypesExt(self, namesTypesOutput, namesTypesOutputEx)

            print(color.bold + 'Names types : ' + color.end)

            show_name_types(self, indexName, indexesNamesTypeSortie,
                            pasColonne=pasColonne)


        def show_var_types(self, var,
                            varsTypesOutput:List[str] = [], varsTypesOutputEx:List[str] = [],
                            pasLigne:int = 5):
            """Display the selected types of the variable"""
            indexVar = varToIndex(self, var)
            indexesVarsTypeSortie = varsTypesToIndexesTypesExt(self, varsTypesOutput, varsTypesOutputEx)

            print(color.bold + 'Variables types : ' + color.end)

            show_var_types(self, indexVar, indexesVarsTypeSortie,
                            pasLigne=pasLigne)

        def show_vars_types(self, vars: List[str] = [], varsEx: List[str] = [],
                            varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                            varsTypesOutput:List[str] = [], varsTypesOutputEx:List[str] = [],
                            selected=False,
                            pasColonne:int = 5, pasLigne:int = 5):
            """Display the types of variables"""
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            indexesVarsTypeSortie = varsTypesToIndexesTypesExt(self, varsTypesOutput, varsTypesOutputEx)

            if (len(indexesVars)*len(indexesVarsTypeSortie)) > self.maxData:
                answer = input('This could be quite long. Do you still want to continue ? (y/n) : ')
                if not answer in self.yes : sys.exit()
            print('variables : '+str(len(indexesVars)))
            print('types : '+str(len(indexesVarsTypeSortie)))
            print(color.bold + 'Variables types : ' + color.end)
            if selected :
                show_vars_types_selected(self, indexesVars, indexesVarsTypeSortie,
                                         pasColonne=pasColonne, pasLigne=pasLigne)
            else:
                show_vars_types(self, indexesVars, indexesVarsTypeSortie,
                            pasColonne=pasColonne, pasLigne=pasLigne)

        def show_vars_types_selected(self, vars: List[str] = [], varsEx: List[str] = [],
                            varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                            varsTypesOutput:List[str] = [], varsTypesOutputEx:List[str] = [],
                            pasColonne:int = 5, pasLigne:int = 5):
            """Display the types of the variables for the types selected by at least one of the variables."""
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            indexesVarsTypeSortie = varsTypesToIndexesTypesExt(self, varsTypesOutput, varsTypesOutputEx)

            if (len(indexesVars)*len(indexesVarsTypeSortie)) > self.maxData:
                answer = input('This could be quite long. Do you still want to continue ? (y/n) : ')
                if not answer in self.yes : sys.exit()

            show_vars_types_selected(self, indexesVars, indexesVarsTypeSortie,
                            pasColonne=pasColonne, pasLigne=pasLigne)

        #########################################################################################
        # Methods from rules
        #########################################################################################
        def show_vars_rules(self, varsTypesOutput:List[str] = [], varsTypesOutputEx:List[str] = []):
            """Display the rules for the variable types"""
            indexesVarsTypeSortie = getIndexesVarsTypes(self, varsTypesOutput, varsTypesOutputEx)

            show_vars_rules(self, indexesVarsTypeSortie)

        #########################################################################################
        # Methods from correlations
        #########################################################################################
        def show_difference(self,
                            name1, name2, vars: List[str] = [], varsEx: List[str] = [],
                            varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                            variantes: List[str] = [],
                            pasColonne = 10, pasLigne:int = 5, width = '', decoration = True):
            """Display the values of variables where two names differ."""
            indexNom1 = nomToIndex(self, name1)
            indexNom2 = nomToIndex(self, name2)
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            show_difference(self,
                            indexNom1, indexNom2, indexesVars,variantes=variantes, pasColonne=pasColonne,
                            pasLigne=pasLigne ,width=width, decoration = decoration )

        def show_difference_types(self,
                                  nom1, nom2, vars: List[str] = [], varsEx: List[str] = [],
                                  varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                  varsTypesOutput:List[str] = [], varsTypesOutputEx:List[str] = [],
                                  variantes: List[str] = [],
                                  effectifType=0, EffectifType=0,
                                  percenType=0, PercenType=100):
            """Display the differences by type between two names"""
            indexNom1 = nomToIndex(self, nom1)
            indexNom2 = nomToIndex(self, nom2)
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            indexesVarsTypeSortie = getIndexesVarsTypes(self, varsTypesOutput, varsTypesOutputEx)

            show_difference_types(self,
                                  indexNom1, indexNom2, indexesVars, indexesVarsTypeSortie,variantes=variantes,
                                  effectifType=effectifType, EffectifType=EffectifType,
                                  pourcenType=percenType, PourcenType=PercenType)

        def show_compare_types(self,name1, name2, vars: List[str] = [], varsEx: List[str] = [],
                            varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                               varsTypesOutput: List[str] = [], varsTypesOutputEx: List[str] = [],
                               variantes: List[str] = [],
                               effectif=0,Effectif=float('inf'),
                               effectifType=0, EffectifType=float('inf'),
                               pasColonne = 10,  order=''):
            """Display the number of common values for the selected types. Order is  by  the numbers of common values."""
            indexNom1 = nomToIndex(self, name1)
            indexNom2 = nomToIndex(self, name2)
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            indexesVarsTypesOutput = getIndexesVarsTypes(self, varsTypesOutput, varsTypesOutputEx)

            print(color.bold + 'Comparison by types of \"{}\" and  \"{}\" : '.format(name1,name2) + color.end)
            show_compare_types(self,indexNom1,indexNom2,indexesVars,indexesVarsTypesOutput=indexesVarsTypesOutput,
                               variantes=variantes,
                               effectif=effectif,Effectif=Effectif,
                               effectifType=effectifType, EffectifType=EffectifType,
                               pasColonne=pasColonne,order=order)

        def show_compare_types_percent(self,name1, name2, vars: List[str] = [], varsEx: List[str] = [],
                            varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                               varsTypesOutput: List[str] = [], varsTypesOutputEx: List[str] = [],
                                variantes: List[str] = [],
                               effectifType=0, EffectifType=float('inf'),
                               percenType=0, PercenType=100,
                               pasColonne = 10, order=''):
            """Display the percentage of common values for the selected types. Order is  by percentage of common values."""
            indexNom1 = nomToIndex(self, name1)
            indexNom2 = nomToIndex(self, name2)
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            indexesVarsTypeSortie = getIndexesVarsTypes(self, varsTypesOutput, varsTypesOutputEx)

            print(color.bold + 'Comparison by types of \"{}\" and  \"{}\" : '.format(name1,name2) + color.end)
            show_compare_types_percent(self, indexNom1, indexNom2, indexesVars, indexesVarsTypeSortie,
                                       variantes=variantes,
                                       effectifType=effectifType, EffectifType=EffectifType,
                                       percenType=percenType, PercenType=PercenType,
                                       pasColonne=pasColonne, order=order)


        def vars_common(self,
                        nom1, nom2, vars: List[str] = [], varsEx: List[str] = [],
                        varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                        variantes: List[str] = []):
            """List of variables where both names have the same value."""
            indexNom1 = nomToIndex(self, nom1)
            indexNom2 = nomToIndex(self, nom2)
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)

            return vars_common(self, indexNom1, indexNom2, indexesVars, variantes=variantes)

        def show_common(self,
                        name1, name2, vars: List[str] = [], varsEx: List[str] = [],
                        varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                        variantes: List[str] = []):
            """Display the table of values where the two names are equal. """
            indexNom1 = nomToIndex(self, name1)
            indexNom2 = nomToIndex(self, name2)
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            show_common(self, indexNom1, indexNom2, indexesVars, variantes=variantes)

        def show_names_common_percent(self,
                                      name, vars: List[str] = [], varsEx: List[str] = [],
                                      names: List[str] = [], namesEx: List[str] = [],
                                      percent:int = 0, Percent:int = 100,
                                      varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                      namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                                      variantes: List[str] = [],
                                      corpus:str = 'all', domain:str = 'all',
                                      pasColonne:int = 5, pasLigne:int = 5):
            """Display the common values of a name with other names, specifying the percentage of these names having this value.
            The idea is to recover the "rare" variables of a name relative to others."""
            indexNom = nomToIndex(self, name)
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            show_names_common_percent(self, indexNom, indexes['noms'], indexes['vars'],
                                      variantes=variantes,
                                      percent=percent, Percent=Percent,
                                      pasColonne=pasColonne, pasLigne=pasLigne)

        def vars_discrimine(self,  nom,discrimines,
                              vars: List[str] = [], varsEx: List[str] = [],
                              varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                variantes=[]):
            indexNom = nomToIndex(self, nom)
            indexNom1 = nomToIndex(self, discrimines[0])
            indexNom2 = nomToIndex(self, discrimines[1])
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            return [self.vars[v] for v in indexesVars_discrimine(self,
                                       indexNom, [indexNom1, indexNom2], indexesVars,
                                       variantes=variantes)]
        def show_discrimine(self,
                            nom, discrimines, vars: List[str] = [], varsEx: List[str] = [],
                            varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                            variantes: List[str] = [],
                            pasColonne:int = 5,
                            decoration=True):
            """Display values of a name that discriminate between two names, i.e. that are equal to one but not to the other."""
            indexNom = nomToIndex(self, nom)
            indexNom1 = nomToIndex(self, discrimines[0])
            indexNom2 = nomToIndex(self, discrimines[1])
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)

            show_discrimine(self,
                            indexNom, [indexNom1, indexNom2], indexesVars,
                            variantes=variantes,
                            pasColonne=pasColonne,
                            decoration=decoration)

        def show_discrimine_types(self,
                                  nom, discrimines, vars: List[str] = [], varsEx: List[str] = [],
                                  varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula=[],
                                  varsTypesOutput:List[str] = [], varsTypesOutputEx:List[str] = [],
                                  effectif: int = 0, Effectif: int = float('inf'),
                                  percent: int = 0, Percent: int = 100,
                                  effectifType: int = 0, EffectifType: int = float('inf'),
                                  variantes: List[str] = [],
                                  pasColonne: int = 5, pasLigne: int = 5,
                                  decoration=True):
            """Display the number by type of values of a name that discriminate between two names, i.e. that are equal to one but not to the other. """
            indexNom = nomToIndex(self, nom)
            indexNom1 = nomToIndex(self, discrimines[0])
            indexNom2 = nomToIndex(self, discrimines[1])
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            indexesVars = indexesVars_discrimine(self, indexNom, [indexNom1, indexNom2], indexesVars)
            indexesVarsTypeSortie = varsTypesToIndexesTypesExt(self, varsTypesOutput, varsTypesOutputEx)

            show_correlations_types(self,
                                    indexNom, [indexNom1, indexNom2],
                                    indexesVars, indexesVarsTypeSortie,
                                    variantes=variantes,
                                    effectif=effectif, Effectif=Effectif,
                                    percent=percent, Percent=Percent,
                                    effectifType=effectifType, EffectifType=EffectifType,
                                    pasColonne=pasColonne, pasLigne=pasLigne,
                                    decoration=decoration)

        def show_correlations(self,
                              name, vars: List[str] = [], varsEx: List[str] = [],
                              names: List[str] = [], namesEx: List[str] = [], dir='both',
                              percent:int = 0, Percent:int = 100, effectif:int = 0, Effectif:int = float('inf'),
                              varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                              namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                              variantes:List[str] = [],
                              pasColonne:int = 5, pasLigne:int = 5, corpus:str = 'all', domain:str = 'all',
                              decoration=True):
            """Display the common values with the names above, below, or both (resp. 'asc', 'desc','both'), in descending order of the percentage of equal values."""

            indexNom = nomToIndex(self, name)
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            if dir == 'asc':
                indexesNoms =[n for n in indexes['noms'] if n < indexNom]
            elif dir == 'desc':
                indexesNoms = [n for n in indexes['noms'] if n > indexNom]
            else:
                indexesNoms = indexes['noms']
            show_correlations(self, indexNom, indexesNoms, indexes['vars'],
                              percent=percent, Percent=Percent,
                              effectif=effectif, Effectif=Effectif,
                              variantes=variantes,
                              pasColonne=pasColonne, pasLigne=pasLigne,
                              decoration=decoration)


        def show_correlations_types(self,
                                    name, vars: List[str] = [], varsEx: List[str] = [], varsTypesFormula:str = '',
                                    names: List[str] = [], namesEx: List[str] = [], dir='both',
                                    effectif=0,Effectif=float('inf'),
                                    effectifType=0, EffectifType=float('inf'),
                                    varsTypes: List[str] = [], varsTypesEx: List[str] = [],
                                    varsTypesOutput:List[str] = [], varsTypesOutputEx:List[str] = [],
                                    namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                                    variantes: List[str] = [],
                                    corpus:str = 'all', domain:str = 'all',
                                    pasColonne:int = 5, pasLigne:int = 5,
                                    decoration=True):
            """Display the common values by type with the names below, in descending order of the percentage of equal values."""
            indexNom = nomToIndex(self, name)
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            if dir == 'asc':
                indexesNoms = [n for n in indexes['noms'] if n < indexNom]
            elif dir == 'desc':
                indexesNoms = [n for n in indexes['noms'] if n > indexNom]
            else:
                indexesNoms = indexes['noms']
            indexesVarsTypesOutput = varsTypesToIndexesTypesExt(self, varsTypesOutput, varsTypesOutputEx)

            show_correlations_types(self,
                                    indexNom, indexesNoms, indexes['vars'],indexesVarsTypesOutput,
                                    variantes=variantes,
                                    effectif=effectif,Effectif=Effectif,
                                    effectifType=effectifType, EffectifType=EffectifType,
                                    pasColonne=pasColonne, pasLigne=pasLigne,
                                    decoration=decoration)


        def show_correlations_types_percent(self,
                                            name, vars: List[str] = [], varsEx: List[str] = [],
                                            names: List[str] = [], namesEx: List[str] = [], dir:str = 'both',
                                            effectif:int = 0, Effectif:int = float('inf'),
                                            percent:int = 0, Percent:int = 100,
                                            percenType=0, PercenType=100,
                                            effectifType:int = 0, EffectifType:int = float('inf'),
                                            varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                            varsTypesOutput:List[str] = [], varsTypesOutputEx:List[str] = [],
                                            namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                                            variantes: List[str] = [],
                                            corpus:str = 'all', domain:str = 'all',
                                            pasColonne:int = 5, pasLigne:int = 5,
                                            decoration=True):
            """Display the percentage of common values by type with the names below, in descending order of the percentage of equal values."""
            indexNom = nomToIndex(self, name)
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            if dir == 'asc':
                indexesNoms = [n for n in indexes['noms'] if n < indexNom]
            elif dir == 'desc':
                indexesNoms = [n for n in indexes['noms'] if n > indexNom]
            else:
                indexesNoms = indexes['noms']

            indexesVarsTypeSortie = varsTypesToIndexesTypesExt(self, varsTypesOutput, varsTypesOutputEx)

            show_correlations_types_percent(self,
                                            indexNom, indexesNoms, indexes['vars'], indexesVarsTypeSortie,
                                            variantes=variantes,
                                            effectif=effectif, Effectif=Effectif,
                                            percent=percent, Percent=Percent,
                                            percenType=percenType, PercenType=PercenType,
                                            effectifType=effectifType, EffectifType=EffectifType,
                                            pasColonne=pasColonne, pasLigne=pasLigne,
                                            decoration=decoration)


        def show_discrimine_types_percent(self,
                                          name, discrimines, vars: List[str] = [], varsEx: List[str] = [],
                                          varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                          varsTypesOutput:List[str] = [], varsTypesOutputEx:List[str] = [],
                                          effectif: int = 0, Effectif: int = float('inf'),
                                          percent: int = 0, Percent: int = 100,
                                          percenType: int = 0, PercenType: int = 100,
                                          effectifType: int = 0, EffectifType: int = float('inf'),
                                          variantes: List[str] = [],
                                          pasColonne: int = 5, pasLigne: int = 5,
                                          decoration=True):
            """Display the percentage by type of values of a name that discriminate between two names, i.e. that are equal to one but not to the other. """
            indexNom = nomToIndex(self, name)
            indexNom1 = nomToIndex(self, discrimines[0])
            indexNom2 = nomToIndex(self, discrimines[1])
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            indexesVars = indexesVars_discrimine(self, indexNom, [indexNom1,indexNom2],indexesVars)
            indexesVarsTypeSortie = varsTypesToIndexesTypesExt(self, varsTypesOutput, varsTypesOutputEx)

            show_correlations_types_percent(self,
                                            indexNom, [indexNom1,indexNom2],
                                            indexesVars, indexesVarsTypeSortie,
                                            variantes=variantes,
                                            effectif=effectif,Effectif=Effectif,
                                            percent=percent, Percent=Percent,
                                            percenType=percenType, PercenType=PercenType,
                                            effectifType=effectifType, EffectifType=EffectifType,
                                            pasColonne=pasColonne, pasLigne=pasLigne,
                                            decoration=decoration)

        def show_residual_types_percent(self,
                                          name, names: List[str] = [], namesEx: List[str] = [],
                                          namesTypes: List[str] = [], namesTypesEx: List[str] = [],
                                          namesTypesFormula: str = '',
                                          vars: List[str] = [], varsEx: List[str] = [],
                                          varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                          varsTypesOutput:List[str] = [], varsTypesOutputEx:List[str] = [],
                                          variantes: List[str] = [],
                                          pasColonne:int = 5):
            """Display the residual percentage of the correlations by type of the names relative to the name,
            i.e. that are not equal to name. """
            indexNom = nomToIndex(self, name)
            indexesNoms = getIndexesNoms(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula)
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            indexesVarsTypeSortie = varsTypesToIndexesTypesExt(self, varsTypesOutput, varsTypesOutputEx)

            show_residual_types_percent(self,
                                           indexNom, indexesNoms,
                                           indexesVars, indexesVarsTypeSortie,
                                           variantes=variantes,
                                           pasColonne=pasColonne)

        def plot_intervals(self, name1, name2, length,
                           vars: List[str] = [], varsEx: List[str] = [],
                           varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                           variantes: List[str] = [],
                           pas=1, elev=0, azim=0):
            # todo : docstring
            indexNom1 = nomToIndex(self, name1)
            indexNom2 = nomToIndex(self, name2)
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)

            plot_intervals(self, indexNom1, indexNom2, indexesVars, length,
                           variantes=variantes,
                           pas=pas, elev=elev, azim=azim)

        #########################################################################################
        # Methods from corpus
        #########################################################################################

        def domain(self, vars: List[str] = [], names: List[str] = []):
            """List of variables with values for all selected names."""
            return domain(self, vars=vars, names=names)

        def show_domain(self, vars: List[str] = [], varsEx: List[str] = [],
                        varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                        names: List[str] = [], namesEx: List[str] = [],
                        namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = ''):
            """Display variables with values for all selected names"""
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            indexesNoms = getIndexesNoms(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula)
            vars = indexesToVars_augmented(self, indexesDomaine(self, indexesVars, indexesNoms))
            printLines(columns=vars)

        def corpus(self, vars: List[str] = [], varsEx: List[str] = [],
                   varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                   names: List[str] = [], namesEx: List[str] = [],
                   namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = ''):
            """List of names with values on all selected variables."""

            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            indexesNoms = getIndexesNoms(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula)
            indCorpus = indexesCorpus(self, indexesVars, indexesNoms)
            cp = [self.noms[n] for n in indCorpus]
            return cp

        def show_corpus(self, vars: List[str] = [], varsEx: List[str] = [],
                        varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                        names: List[str] = [], namesEx: List[str] = [],
                        namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = ''):
            """Display variables with values for all selected names"""
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            indexesNoms = getIndexesNoms(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula)
            names = indexesToNoms_augmented(self, indexesCorpus(self, indexesVars, indexesNoms))
            printLines(columns=names)

        def show_vars_missing(self, nom,
                              vars: List[str] = [], varsEx: List[str] = [],
                              varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = ''):
            """Display variables without value for the selected name"""
            indexNom = nomToIndex(self, nom)
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            show_vars_missing(self, indexNom, indexesVars)

        def names_thamous_missing(self, names: List[str] = [], namesEx: List[str] = [], namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                                  corpus:str = 'all'):
            """List of names without Thamous identifier."""
            indexesNoms = getIndexesNoms(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula)
            indexes = corpusdomaine(self, corpus, 'all', indexesNoms, [])
            names_thamous_missing(self, indexes['noms'])

        def show_vars_types_unassigned(self):
            """Display the variable types assigned to no variables."""
            show_vars_types_unassigned(self)

        def show_name_types_unassigned(self):
            """Display the name types assigned to no names."""
            show_name_types_unassigned(self)

        def show_vars_without_types(self,
                                    vars: List[str] = [], varsEx: List[str] = [],
                                    varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = ''):
            """Display variables without types"""
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            show_vars_without_types(self, indexesVars)

        def show_names_without_types(self,
                                     names: List[str] = [], namesEx: List[str] = [],
                                     namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = ''):
            """Display names without types"""
            indexesNoms = getIndexesNoms(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula)
            show_names_without_types(self, indexesNoms)

        def show_names_without_value(self,
                                     vars: List[str] = [], varsEx: List[str] = [],
                                     varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                     names: List[str] = [], namesEx: List[str] = [],
                                     namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = ''):
            """Display the names without values on the selected variables."""
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            indexesNoms = getIndexesNoms(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula)
            show_names_without_value(self, indexesNoms, indexesVars)


        def vars_with_value(self, nom,
                         vars: List[str] = [], varsEx: List[str] = [],
                         varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = ''):
            """List of the variables of a name with a value."""
            indexNom = nomToIndex(self, nom)
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)

            return vars_with_value(self, indexNom, indexesVars)


        def vars_without_value(self, nom,
                         vars: List[str] = [], varsEx: List[str] = [],
                         varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = ''):
            """List of the variables of a name without a value."""
            indexNom = nomToIndex(self, nom)
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)

            return vars_without_value(self, indexNom, indexesVars)

        def vars_without_values(self,
                                names: List[str] = [], namesEx: List[str] = [],
                                namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula: str = '',
                               vars: List[str] = [], varsEx: List[str] = [],
                               varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula: str = ''):
            """List of the variables without a value on any the given names."""
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            indexesNoms = getIndexesNoms(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula)

            return vars_without_values(self, indexesNoms, indexesVars)


        def show_values_without_quotations(self,
                                           vars: List[str] = [], varsEx: List[str] = [],
                                           varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                           names: List[str] = [], namesEx: List[str] = [],
                                           namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = ''):
            """Display values without quotation."""
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            indexesNoms = getIndexesNoms(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula)

            show_values_without_quotations(self, indexesNoms, indexesVars)


        #########################################################################################
        # Methods from  innove
        ########################################################################################

        def show_names_data_percent(self,
                                    nom, names: List[str] = [], namesEx: List[str] = [],
                                    vars: List[str] = [], varsEx: List[str] = [],
                                    percent:int = 0, Percent:int = 100,
                                    varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                    namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                                    variantes: List[str] = [],
                                    corpus:str = 'all', domain:str = 'all',
                                    pasColonne = 10, pasLigne = 10):
            """Displays names with at least one value equal to those of a certain percentage of the selected names. """
            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            show_names_data_percent(self, indexNom, indexes['noms'], indexes['vars'],
                                    variantes=variantes,
                                    percent=percent, Percent=Percent,
                                    pasColonne=pasColonne, pasLigne=pasLigne)

        def show_data_only(self,
                           nom, names: List[str] = [], namesEx: List[str] = [], dir = 'both',
                           vars: List[str] = [], varsEx: List[str] = [],
                           varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                           namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                           variantes: List[str] = [],
                           corpus:str = 'all', domain:str = 'all'):
            """Display the eigenvalues for a name."""
            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            if dir == 'asc':
                indexesNoms = [n for n in indexes['noms'] if n < indexNom]
            elif dir == 'desc':
                indexesNoms = [n for n in indexes['noms'] if n > indexNom]
            else:
                indexesNoms = indexes['noms']

            show_data_only(self, indexNom, indexesNoms, indexes['vars'], variantes=variantes)

        def vars_data_percent(self,
                              nom, names: List[str] = [], namesEx: List[str] = [],
                              vars: List[str] = [], varsEx: List[str] = [],
                              percent:int = 0, Percent:int = 100,
                              varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                              namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                              variantes: List[str] = [],
                              corpus:str = 'all', domain:str = 'all'):
            """List of variables whose percentage of values equal to those of the selected names are between two given percentages."""
            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            if dir == 'asc':
                indexesNoms = [n for n in indexes['noms'] if n < indexNom]
            elif dir == 'desc':
                indexesNoms = [n for n in indexes['noms'] if n > indexNom]
            else:
                indexesNoms = indexes['noms']
            return vars_data_percent(self, indexNom, indexesNoms, indexes['vars'],
                                     variantes=variantes,
                                     percent=percent, Percent=Percent)

        def show_data_percent(self,
                              nom, names: List[str] = [], namesEx: List[str] = [],dir='both',
                              vars: List[str] = [], varsEx: List[str] = [],
                              percent:int = 0, Percent:int = 100,
                              varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                              namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                              variantes: List[str] = [],
                              corpus:str = 'all', domain:str = 'all',
                              pasColonne:int = 5, pasLigne:int = 5):
            """Display the values for variables whose percentage of values equal to those of the selected names are between two given percentages."""
            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)

            show_data_percent(self,
                              indexNom, indexes['noms'], indexes['vars'],
                              variantes=variantes,
                              percent=percent, Percent=Percent,
                              pasColonne=pasColonne, pasLigne=pasLigne)


        def vars_only(self,
                      nom, names: List[str] = [], namesEx: List[str] = [], dir = 'both',
                      vars: List[str] = [], varsEx: List[str] = [],
                      varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                      namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                      variantes: List[str] = [],
                      corpus:str = 'all', domain:str = 'all'):
            """List of variables with their own values."""
            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            if dir == 'asc':
                indexesNoms = [n for n in indexes['noms'] if n < indexNom]
            elif dir == 'desc':
                indexesNoms = [n for n in indexes['noms'] if n > indexNom]
            else:
                indexesNoms = indexes['noms']
            return [self.vars[v] for v in vars_only(self, indexNom, indexesNoms, indexes['vars'], variantes=variantes)]

        def vars_innove(self,
                        names: List[str] = [], namesEx: List[str] = [],
                        vars: List[str] = [], varsEx: List[str] = [],
                        varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                        namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                        variantes: List[str] = [],
                        corpus:str = 'all', domain:str = 'all', dir:str = 'asc'):
            """List of innovative variables relative to the selected names: a variable is innovative when one of the names innovates on this variable relative to the others. """

            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)

            return [self.vars[v] for v in vars_innove(self, indexes['noms'], indexes['vars'], dir = dir, variantes=variantes)]

        def show_innove(self,
                             names: List[str] = [], namesEx: List[str] = [],
                             vars: List[str] = [], varsEx: List[str] = [],
                             varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                             namesTypes: List[str] = [], namesTypesEx:List[str] = [], namesTypesFormula:str = '',
                                variantes: List[str] = [],
                             corpus:str = 'all', domain:str = 'all', dir = 'asc'):
            """Display the innovative variables relative to the selected names: a variable is innovative when one of the names innovates on this variable relative to the others. """
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)

            show_innove(self, indexes['noms'], indexes['vars'], dir = dir,variantes=variantes)


        def show_innove_types(self,
                              names: List[str] = [], namesEx: List[str] = [],
                              vars: List[str] = [], varsEx: List[str] = [],
                              varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                              varsTypesOutput:List[str] = [], varsTypesOutputEx:List[str] = [],
                              namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                              variantes: List[str] = [],
                              corpus:str = 'all', domain:str = 'all',
                              effectifType=0, EffectifType=0,
                              pasColonne:int = 5, pasLigne:int = 5, dir='asc', decoration = True):
            """Display the innovative variables by types relative to the selected names: a variable is innovative when one of the names innovates on this variable relative to the others. """
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            indexesVarsTypeSortie = varsTypesToIndexesTypesExt(self, varsTypesOutput, varsTypesOutputEx)

            show_innove_types(self, indexes['noms'], indexes['vars'], indexesVarsTypeSortie, dir=dir,
                              variantes=variantes,
                              effectifType=effectifType, EffectifType=EffectifType,
                              pasColonne=pasColonne, pasLigne=pasLigne, decoration = decoration)

        def show_innove_types_percent(self,
                                      names: List[str] = [], namesEx: List[str] = [],
                                      vars: List[str] = [], varsEx: List[str] = [],
                                      varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                      varsTypesOutput:List[str] = [], varsTypesOutputEx:List[str] = [],
                                      namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                                      dir='asc',
                                      variantes: List[str] = [],
                                      corpus:str = 'all', domain:str = 'all',
                                      percenType=0, PercenType=100,
                                      effectif:int = 0, Effectif:int = 0,
                                      pasColonne:int = 5, pasLigne:int = 5, decoration = True):
            """Display the percentage of innovative variables by types relative to the selected names: a variable is innovative when one of the names innovates on this variable relative to the others. """
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            indexesVarsTypeSortie = varsTypesToIndexesTypesExt(self, varsTypesOutput, varsTypesOutputEx)

            show_innove_types_percent(self, indexes['noms'], indexes['vars'], indexesVarsTypeSortie, dir=dir,
                                      variantes=variantes,
                                      percenType=percenType, PercenType=PercenType,
                                      effectif=effectif, Effectif=Effectif,
                                      pasColonne=pasColonne, pasLigne=pasLigne, decoration=decoration)


        def translation_test(self, names: List[str], namesEx: List[str] = [],
                             namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula: str = '',
                             vars: List[str] = [], varsEx: List[str] = [],
                             varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                             corpus: str = 'all', domain: str = 'all',
                             dir='asc',decoration=True):
            """Apply the translation test in the direction indicated."""
            if isinstance(names, str):names=[names]
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            indexVarsTypesTraduction = self.vars_types_types.index('traduction')
            indexVarsTypesCitation = self.vars_types_types.index('citation')

            return show_innove_types_percent(self, indexes['noms'], indexes['vars'],
                                             indexesVarsTypesOutput=[indexVarsTypesTraduction,
                                                                     indexVarsTypesCitation],
                                             dir=dir,decoration=decoration)

        #########################################################################################
        # Methods from  coherence
        #########################################################################################
        def show_coherence(self, names: List[str] = [], namesEx: List[str] = [], vars: List[str] = [], varsEx: List[str] = [],
                           varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                           namesTypes: List[str] = [], namesTypesEx:List[str] = [], namesTypesFormula:str = '',
                           variantes: List[str] = [],
                           corpus:str = 'all', domain:str = 'all',
                           pasColonne:int = 5, pasLigne:int = 5, decoration:bool = True):
            """Display for the selected names the number of times a value is taken independently of the variable whose value it is."""
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)

            show_coherence(self, indexes['noms'], indexes['vars'],variantes=variantes,
                           pasColonne=pasColonne, pasLigne=pasLigne, decoration=decoration)

        def show_coherence_percent(self, names: List[str] = [], namesEx: List[str] = [], vars: List[str] = [], varsEx: List[str] = [],
                                   varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                   namesTypes: List[str] = [], namesTypesEx:List[str] = [], namesTypesFormula:str = '',
                                   variantes: List[str] =[],
                                   corpus:str = 'all', domain:str = 'all',
                                   pasColonne:int = 5, pasLigne:int = 5, decoration:bool = True):
            """Display for the selected names the percentage of times a value is taken independently of the variable whose value it is."""
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)

            show_coherence_percent(self, indexes['noms'], indexes['vars'],
                                   variantes=variantes,
                                   pasColonne=pasColonne, pasLigne=pasLigne, decoration=decoration)

        def show_coherence_type(self, nom, tp, variantes: List[str] = []):
            #todo : pourquoi un seul nom quand show_coherence a une liste ?
            show_coherence_type(self, nom, tp, variantes=variantes)

        def show_coherence_types(self, nom, varsTypes
                                 , variantes: List[str] = []):
            #todo : pourquoi un seul nom quand show_coherence a une liste ?
            show_coherence_types(self, nom, varsTypes, variantes=variantes)

        #########################################################################################
        # Methods from bases
        #########################################################################################
        def show_decomposition(self,
                               nom,
                               namesIncompleteBasis=[], namesIncompleteBasisEx=[],
                               vars: List[str] = [], varsEx: List[str] = [],
                               names: List[str] = [], namesEx: List[str] = [],
                               max:int =0, percent:int = 0, Percent :int = 100,
                               varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                               namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                               variantes: List[str] = [],
                               corpus:str = 'all', domain='positif',
                               pasColonne:int = 5, pasLigne:int = 5,decoration = True):
            """Display the decomposition of the values of a name in relation to those of other names according to the percentages indicated."""
            indexNom = nomToIndex(self, nom)
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)

            if namesIncompleteBasis or namesIncompleteBasisEx:
                indexesNomsBaseIncomplete = nomsToIndexesNoms(self, namesIncompleteBasis, namesIncompleteBasisEx)
            else:
                indexesNomsBaseIncomplete = []

            show_decomposition(self,
                               indexNom, indexes['noms'], indexes['vars'],
                               indexesNomsBaseIncomplete,
                               variantes=variantes,
                               max=max, percent=percent, Percent=Percent,
                               pasColonne=pasColonne, pasLigne=pasLigne,decoration=decoration)

        def show_values(self, names: List[str] = [], namesEx: List[str] = [],
                        vars: List[str] = [], varsEx: List[str] = [],
                        varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                        namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                        corpus:str = 'all', domain:str = 'all'):
            """Display the attested values of the variables for a list of names."""
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)

            show_values(self, indexes['noms'], indexes['vars'])

        def show_names_included(self, namesGenerators:List[str]=[], namesGeneratorsEx:List[str]=[],
                                vars: List[str] = [], varsEx: List[str] = [],
                                names: List[str] = [], namesEx: List[str] = [],
                                varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                                corpus:str = 'all', domain:str = 'all',
                                percent:int = 0, Percent:int = 100):
            #todo:à revoir...

            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)

            show_names_included(self, indexes['noms'], indexes['vars'], namesGenerating=namesGenerators,
                                namesGeneringEx=namesGeneratorsEx,
                                percent=percent, Percent=Percent)

        def show_names_included_types(self, namesGenerating:List[str]=[], namesGeneratingEx:List[str]=[],
                                      vars: List[str] = [], varsEx: List[str] = [],
                                      names: List[str] = [], namesEx: List[str] = [],
                                      varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                      namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                                      corpus:str = 'all', domain:str = 'all',
                                      percent:int = 0, Percent:int = 100,
                                      effectif:int = 0, Effectif:int = 0,
                                      varsTypesOutput:List[str] = [], varsTypesOutputEx:List[str] = []):
            #todo:docstring

            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            indexesVarsTypeSortie = varsTypesToIndexesTypesExt(self, varsTypesOutput, varsTypesOutputEx)

            show_names_included_types(self, indexes['noms'], indexes['vars'], indexesVarsTypeSortie,
                                      namesGenerating=namesGenerating, namesGeneratingEx=namesGeneratingEx,
                                      percent=percent, Percent=Percent,
                                      effectif=effectif, Effectif=Effectif)

        def show_names_included_types_percent(self, namesGenerating:List[str]=[], namesGeneratingEx:List[str]=[],
                                              vars: List[str] = [], varsEx: List[str] = [],
                                              names: List[str] = [], namesEx: List[str] = [],
                                              varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                              namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                                              percent:int = 0, Percent:int = 100,
                                              effectif:int = 0, Effectif:int = 0,
                                              corpus='all',domain='all',
                                              varsTypesOutput:List[str] = [], varsTypesOutputEx:List[str] = []):
            #todo:docstring

            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)

            indexesVarsTypeSortie = varsTypesToIndexesTypesExt(self, varsTypesOutput, varsTypesOutputEx)

            show_names_included_types_percent(self, indexes['noms'], indexes['vars'], indexesVarsTypeSortie,
                                              namesGenerating=namesGenerating, namesGeneratingEx=namesGeneratingEx,
                                              percent=percent, Percent=Percent,
                                              effectif=effectif, Effectif=Effectif)

        def show_names_basis_complete(self, namesGenerators:List[str]=[], namesGeneratorsEx:List[str]=[],
                                      nomsBaseIncomplete=[],
                                      vars: List[str] = [], varsEx: List[str] = [],
                                      names: List[str] = [], namesEx: List[str] = [],
                                      varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                      namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                                      corpus='all',domain='all',
                                      percent:int = 0, Percent:int = 100, max:int = 0):
            #todo:docstring

            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)

            show_names_basis_complete(self, indexes['noms'], indexes['vars'],
                                      namesGenerating=namesGenerators, namesGeneratingEx=namesGeneratorsEx,
                                      nomsBaseIncomplete=nomsBaseIncomplete,
                                      percent=percent, Percent=Percent)

        def show_vars_basis_first(self, varsIncompleteBasis=[],
                                 vars: List[str] = [], varsEx: List[str] = [],
                                 names: List[str] = [], namesEx: List[str] = [],
                                 varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                 namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                                 corpus='all',domain='all',
                                 max:int = 0):
            #todo:docstring

            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            show_vars_base_first(self, indexes['noms'], indexes['vars'], varsIncompleteBasis=varsIncompleteBasis,
                                 max=max)

        def show_vars_basis(self, varsIncompleteBasis=[],
                            vars: List[str] = [], varsEx: List[str] = [],
                            names: List[str] = [], namesEx: List[str] = [],
                            varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                            namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                            corpus:str = 'all', domain:str = 'all',
                            max:int = 0):
            #todo:docstring
            '''Display the sets of least number of variables sufficient to discriminate the selected names '''

            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            show_vars_basis(self, indexes['noms'], indexes['vars'], varsIncompleteBasis=varsIncompleteBasis,
                            max=max)

        #############################################################################
        # Methods from  repartition
        #############################################################################
        def show_repartition(self,
                             vars: List[str] = [], varsEx: List[str] = [],
                             names: List[str] = [], namesEx: List[str] = [],
                             varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                             namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                             variantes: List[str] = [],
                             corpus:str = 'all', domain:str = 'all',
                             replaceValues: List[str] = [], replaceNames: List[str] = [], replaceVars: List[str] = [],
                             decoration=True):
            """Display the array of names with the same values on a given set of variables."""

            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            show_repartition(self, indexes['noms'], indexes['vars'],
                             variantes=variantes,
                             replaceValues = replaceValues, replaceNames = replaceNames, replaceVars = replaceVars,
                             decoration=decoration)

        def show_popularity(self, vars: List[str] = [], varsEx: List[str] = [],
                            names: List[str] = [], namesEx: List[str] = [],
                            varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                            namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                            variantes: List[str] = [],
                            domain:str = 'all', corpus:str = 'all'):
            """Display the most common values, and for each name the percentage of its values equal to the most common values."""
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            show_popularity(self, indexes['noms'], indexes['vars'], variantes=variantes)

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

        def set_graph(self, width='', height='',
                      font_size='', font_color='',
                      node_color='',
                      label_posX='', label_posY=''):
            set_graph(self, width, height, font_size, font_color, node_color, label_posX, label_posY)

        def show_graph_deviation(self, name: str, vars: List[str] = [], varsEx: List[str] = [],
                                 names: List[str] = [], namesEx: List[str] = [],
                                 varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                 namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                                 percent:int = 0, Percent:int = 100,
                                 variantes: List[str] = [],
                                 corpus:str = 'all', domain:str = 'all',
                                 width='', height='', font_size='', font_color='', node_color='',
                                 label_posX='', label_posY=''):
            """Display de deviation graph"""
            indexNom = nomToIndex(self, name)
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)

            show_graph_deviation(self, indexNom, indexes['noms'], indexes['vars'],
                                 variantes=variantes,
                                 percent=percent, Percent=Percent,
                                 width=width, height=height,
                                 font_size=font_size, font_color=font_color, node_color=node_color,
                                 label_posX=label_posX, label_posY=label_posY)

        def show_graphs_deviation(self, vars: List[str] = [], varsEx: List[str] = [],
                                  names: List[str] = [], namesEx: List[str] = [],
                                  varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                  namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                                  variantes: List[str] = [],
                                  corpus='all',domain='all',
                                  percent:int = 0, Percent:int = 100):
            """Display the deviation graphs for the names."""

            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            show_graphs_deviation(self, indexes['noms'], indexes['vars'],
                                  variantes=variantes,
                                  percent=percent, Percent=Percent)

        #############################################################################
        # Méthodes importée de matrices
        #############################################################################

        def show_graph_distance(self, links=True, names: List[str] = [], namesEx: List[str] = [],
                                vars: List[str] = [], varsEx: List[str] = [],
                                varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                                variantes: List[str] = [],
                                corpus='all',domain='all',
                                percent:int = 0, Percent:int = 100, linksColors={}):
            #todo: docstring matrix
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)

            show_graphe_distance(self, indexes['noms'], indexes['vars'], links=links,
                                 variantes=variantes,
                                 percent=percent, Percent=Percent, linksColors=linksColors)

        def show_distance_ordered(self, names: List[str] = [], namesEx: List[str] = [],
                                  vars: List[str] = [], varsEx: List[str] = [],
                                  varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                  namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                                  corpus='all',domain='all',
                                  percent:int = 0, Percent:int = 100):
            #todo:docstring matrix
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            show_distance_ordered(self, indexes['noms'], indexes['vars'],
                                  percent=percent, Percent=Percent)

        def show_distance_matrix(self, namesI=[], namesIEx=[],
                                 namesJ=[], namesJEx=[],
                                 vars: List[str] = [], varsEx: List[str] = []):
            #todo:docstring matrix

            show_distance_matrix(self, namesI=namesI, namesIEx=namesIEx,
                                 namesJ=namesJ, namesJEx=namesJEx,
                                 vars=vars, varsEx=varsEx)

        def show_distance_matrix_percent(self,
                                         namesI=[], namesIEx=[],
                                         namesJ=[], namesJEx=[],
                                         vars: List[str] = [], varsEx: List[str] = []):
            #todo:docstring matrix

            show_distance_matrix_percent(self, namesI=namesI, namesIEx=namesIEx,
                                         namesJ=namesJ, namesJEx=namesJEx,
                                         vars=vars, varsEx=varsEx)

        def show_distance_matrix_normalized(self,
                                            namesI=[], namesIEx=[],
                                            namesJ=[], namesJEx=[],
                                            vars: List[str] = [], varsEx: List[str] = []):
            #todo:docstring matrix

            show_distance_matrix_normalized(self, namesI=namesI, namesIEx=namesIEx,
                                            namesJ=namesJ, namesJEx=namesJ,
                                            vars=vars, varsEx=varsEx)

        def show_distance_matrix_coordinates(self, names: List[str] = [], namesEx: List[str] = [],
                                             vars: List[str] = [], varsEx: List[str] = [],
                                             varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                             namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                                             corpus='all',domain='all'):
            #todo:docstring matrix

            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            show_distance_matrix_coordinates(self, indexes['noms'], indexes['vars'])

        def show_graph_proximity(self, links=True, names: List[str] = [], namesEx: List[str] = [], vars: List[str] = [], varsEx: List[str] = [],
                                 varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                 namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                                 corpus:str = 'all', domain:str = 'all',
                                 percent:int = 0, Percent:int = 100, linksColors={}):
            #todo:docstring matrix


            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            show_graph_proximity(self, indexes['noms'], indexes['vars'], liens=links,
                                 percent=percent, Percent=Percent, linksColors=linksColors)

        def show_proximity_ordered(self, names: List[str] = [], namesEx: List[str] = [],
                                   vars: List[str] = [], varsEx: List[str] = [],
                                   varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                   namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                                   corpus:str = 'all', domain:str = 'all',
                                   percent:int = 0, Percent:int = 100):
            #todo:docstring matrix

            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            show_proximity_ordered(self, indexes['noms'], indexes['vars'],
                                   percent=percent, Percent=Percent)

        def show_proximity_matrix(self, namesI=[], namesIEx=[],
                                  namesJ=[], namesJEx=[],
                                  vars: List[str] = [], varsEx: List[str] = []):
            #todo:docstring matrix

            show_proximity_matrix(self, namesI=namesI, namesIEx=namesIEx,
                                  namesJ=namesJ, namesJEx=namesJEx,
                                  vars=vars, varsEx=varsEx)

        def show_proximity_matrix_percent(self,
                                          namesI=[], namesIEx=[],
                                          namesJ=[], namesJEx=[],
                                          vars: List[str] = [], varsEx: List[str] = []):
            #todo:docstring matrix

            show_proximity_matrix_percent(self, namesI=namesI, namesIEx=namesIEx,
                                          namesJ=namesJ, namesJEx=namesJEx,
                                          vars=vars, varsEx=varsEx)

        def show_proximity_matrix_normalized(self,
                                             namesI=[], namesIEx=[],
                                             namesJ=[], namesJEx=[],
                                             vars: List[str] = [], varsEx: List[str] = []):
            #todo:docstring matrix

            show_proximity_matrix_normalized(self, namesI=namesI, namesIEx=namesIEx,
                                             namesJ=namesJ, namesJEx=namesJEx,
                                             vars=vars, varsEx=varsEx)

        def show_proximity_matrix_coordinates(self, names: List[str] = [], namesEx: List[str] = [],
                                              vars: List[str] = [], varsEx: List[str] = [],
                                              varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                                              namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                                              corpus:str = 'all', domain:str = 'all'):
            #todo:docstring matrix

            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            show_proximity_matrix_coordinates(self, indexes['noms'], indexes['vars'])

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
        def show_intervals(self, name1, name2, names: List[str] = [], namesEx: List[str] = [],
                           vars: List[str] = [], varsEx: List[str] = [],
                           varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                           namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                           corpus = 'all', domain = 'all',
                           percent:int = 0, length=1, pas=1):
            #todo:docstring show_intervals

            indexNom1 = nomToIndex(self, name1)
            indexNom2 = nomToIndex(self, name2)
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            show_intervals(self, indexNom1, indexNom2, indexes['noms'], indexes['vars'],
                           percent=percent, length=length, pas=pas)

        #############################################################################
        # Méthodes importée de arraysearch
        #############################################################################
        def findVars(self,
                     cars, vars: List[str] = [], varsEx: List[str] = [],
                     varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = ''):
            """List of variables containing a string."""
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
            return findVars(self, cars, indexesVars)


        def contains(self,
                     chain, vars: List[str] = [], varsEx: List[str] = [],
                     names: List[str] = [], namesEx: List[str] = [],
                     varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                     namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '',
                     corpus:str = 'all', domain:str = 'all'):
            """Display names and variables whose value contains the given string."""
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            return contains(self,
                            chain, indexes['noms'], indexes['vars'])

        def findVarsValue(self,
                          nom, cars,
                          vars: List[str] = [], varsEx: List[str] = [],
                          varsTypes: List[str] = [], varsTypesEx: List[str] = [],
                          varsTypesFormula:str = ''):
            """List of variables for which the given name has the given value."""

            indexNom = nomToIndex(self, nom)
            indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)

            return findVarsValue(self,
                                 indexNom, cars, indexesVars)

        def namesVarsValues(self, varsValues=[],variantes:List[str] = [], names: List[str] = [],
                            namesEx: List[str] = [], namesTypes: List[str] = [], namesTypesEx: List[str] = [],
                            namesTypesFormula:str = '',
                            corpus='all'):
            """List of names with a given value on given variables varsValues=[[var1,value1],[var2,value2], etc.]."""
            vars = [vv[0] for vv in varsValues]
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars=vars, varsEx=[], varsTypes=[], varsTypesEx=[], varsTypesFormula='',
                                 corpus=corpus, domain='all')
            return namesVarsValues(self, indexes['noms'], varsValues, variantes=variantes)

        def namesVarsContainsValues(self,
                                    varsValues, variantes: List[str] = [],
                                    names: List[str] = [], namesEx: List[str] = [],
                                    namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = ''):
            """List of names containing a given value on given variables varsValues=[[var1,value1],[var2,value2], etc.]."""
            indexesNoms = getIndexesNoms(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula)

            return namesVarsContainsValues(self, indexesNoms, varsValues, variantes=variantes)

        #############################################################################
        # Méthodes importée de quotations
        #############################################################################
        def vars_quotations(self, str, name, vars: List[str] = [], varsEx: List[str] = [],
                            varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '', corpus:str = 'all', domain:str = 'all'):
            """List of the variables of name with quotation."""
            indexNom = self.noms.index(name)
            indexes = getIndexes(self, [name], [], [], [], '',
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)

            return vars_quotations(self, str, indexNom, indexes['vars'])


        def vars_with_quotations(self, name, vars: List[str] = [], varsEx: List[str] = [],
                                 varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '', domain:str = 'all'):
            #todo : difference with previous one ?
            indexNom = nomToIndex(self, name)
            indexes = getIndexes(self, [name], [], [], [], '',
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 'all', domain)
            return vars_with_quotations(self, indexNom, indexes['vars'])

        def show_with_quotations(self, name, vars: List[str] = [], varsEx: List[str] = [],
                                 varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '', domain:str = 'all'):
            """Display the variables of name with quotations."""
            indexNom = nomToIndex(self, name)
            indexes = getIndexes(self, [name], [], [], [], '',
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 'all', domain)
            show_with_quotations(self, indexNom, indexes['vars'])

        def show_without_quotations(self, name, vars: List[str] = [], varsEx: List[str] = [],
                                    varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '', domain:str = 'all'):
            """Display the variables of name without quotations."""
            indexNom = nomToIndex(self, name)
            indexes = getIndexes(self, [name], [], [], [], '',
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 'all', domain)
            show_sans_citations(self, indexNom, indexes['vars'])

        #############################################################################
        # Methods from  write
        #############################################################################

        def write_val_db(self, nom, var, value):
            """Assign a value to a variable of name."""
            write_val_db(self, nom, var, value)

        def rename_var(self, var):
            """Rename a variable."""
            rename_var(self, var)

        def rename_vars_type(self, type):
            """Rename a variable type."""
            rename_vars_type(self, type)

        def rename_names_type(self, type):
            """Rename a name type."""
            rename_names_type(self, type)

        def delete_name(self, name):
            """Delete a name."""
            delete_nom(self, name)

        def delete_var(self, var):
            """Delete a variable."""
            delete_var(self, var)

        def delete_names_type(self, type):
            """Delete a name type."""
            delete_names_type(self, type)

        def delete_vars_type(self, type):
            """Delete a variable type."""
            delete_vars_type(self, type)

        def rename_name(self, name):
            """Rename a name."""
            rename_nom(self, name)

        def add_var(self, newVar, var='', position='after'):
            """Add a new variable before, after a variable or in the beginning or at the end of the variables (position = 'before','after','first','last'."""
            add_var(self, newVar, var=var, position=position)

        def add_vars(self, newVars, var='', position='after'):
            """Add a list of new variables before, after a variable or in the beginning or at the end of the variables (position = 'before','after','first','last'."""
            add_vars(self, newVars, var=var, position=position)

        def add_name(self, newNom, name='', position='after', table='', id='', project=''):
            """Add a new name above, below a name or in the beginning or at the end of the names (position = 'above','below','first','last'.
            id, table and projet from Thamous can be given. """
            add_name(self, newNom, name=name, position=position, id=id, table=table, project=project)

        def add_names(self, newNoms, name='', position='after'):
            """Add a liste of new names above, below a name or in the beginning or at the end of the names (position = 'above','below','first','last'."""
            add_noms(self, newNoms, name=name, position=position)

        def add_vars_type(self, newType, varsType='', position='after'):
            add_vars_type(self, newType, varsType=varsType, position=position)

        def add_vars_types(self, newTypes, varsType='', position='after'):
            add_vars_types(self, newTypes, varsType=varsType, position=position)

        def add_names_type(self, newType, namesType='', position='after'):
            add_names_type(self, newType, namesType=namesType, position=position)

        def add_names_types(self, newType, namesType='', position='after'):
            add_names_type(self, newType, namesType=namesType, position=position)

        def write_val(self, nom, var, value):
            write_val(self, nom, var, value)

        def copy_vars(self, name1:str, name2:str, vars: List[str] = [], varsEx: List[str] = [],
                       varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                       domain:str = 'all'):
            """Copy the values of the selected vars of name1 to those of name2."""
            indexNom1 = self.noms.index(name1)
            indexNom2 = self.noms.index(name2)
            indexes = getIndexes(self, names=[], namesEx=[], namesTypes=[], namesTypesEx=[], namesTypesFormula='',
                                 vars=vars, varsEx=varsEx, varsTypes=varsTypes, varsTypesEx=varsTypesEx,
                                 varsTypesFormula=varsTypesFormula,
                                 corpus='all', domain=domain)

            show_data(self,[indexNom1,indexNom2],indexes['vars'])
            answer = input("Copy the values of \"{}\" into \"{}\" ? (y/n) : ".format(name1,name2))
            if answer in self.yes:
                copy_vars(self, indexNom1, indexNom2, indexes['vars'])
                print()
                print(color.bold+'Copy done.'+color.end)
                print()
                show_data(self, [indexNom1,indexNom2], indexes['vars'])


        def complete_vars(self, name1:str, name2:str, vars: List[str] = [], varsEx: List[str] = [],
                       varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                       domain:str = 'all'):
            """Complete the values of the selected vars without value of name1 with those of name2."""
            indexNom1 = self.noms.index(name1)
            indexNom2 = self.noms.index(name2)
            indexes = getIndexes(self, names=[], namesEx=[], namesTypes=[], namesTypesEx=[], namesTypesFormula='',
                                 vars=self.vars_without_values(name1, vars=vars, varsEx=varsEx, varsTypes=varsTypes, varsTypesEx=varsTypesEx,
                                 varsTypesFormula=varsTypesFormula),varsEx=[], varsTypes=[], varsTypesEx=[],
                                 varsTypesFormula='',
                                 corpus='all', domain=domain)

            show_data(self,[indexNom2,indexNom1],indexes['vars'])
            answer = input("Copy the values of \"{}\" into \"{}\" ? (y/n) : ".format(name2,name1))
            if answer in self.yes:
                copy_vars(self, indexNom2, indexNom1, indexes['vars'])
                print()
                print(color.bold+'Copy done.'+color.end)
                print()
                show_data(self, [indexNom2,indexNom1], indexes['vars'])

        def replace_value(self,value:str ='', newValue:str='',
                           names: List[str] = [], namesEx: List[str] = [], vars: List[str] = [], varsEx: List[str] = [],
                      varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                      namesTypes: List[str] = [], namesTypesEx:List[str] = [], namesTypesFormula:str = '',
                      pasColonne:int = 5, pasLigne:int = 5,
                      domain: str = 'all', corpus: str = 'all',
                      values: bool = True, citations: bool = False, width: str = '',
                      decoration:bool = True):
            """Replace value by newValue in the selected vars of the selected names ."""
            if not value:
                print(color.bold + 'A value must be given.' + color.end)
                sys.exit(1)

            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)

            show_data(self, indexes['noms'], indexes['vars'],
                      pasColonne=pasColonne, pasLigne=pasLigne,
                      values=values, citations=citations, width=width, decoration=False,
                      replaceValues=[[value,value+'->'+newValue]])


            answer = input("Replace all the  \"{}\" by \"{}\" ? (y/N) : ".format(value,newValue))

            if answer in self.yes :
                replace_value(self, value, newValue, indexes['noms'], indexes['vars'])
                show_data(self, indexes['noms'], indexes['vars'],
                          pasColonne=pasColonne, pasLigne=pasLigne,
                          values=values, citations=citations, width=width, decoration=decoration)
            else:
                print(color.bold + 'Aborted.' + color.end)



        def write_quotation(self, name, var, quotation):
            write_citation(self, name, var, quotation)

        def write_var_definition(self, var, definition):
            write_var_definition(self, var, definition)

        def write_name_definition(self, name, definition):
            write_name_definition(self, name, definition)

        def write_var_type_val(self, type, var, value):
            write_var_type_val(self, type=type, var=var, value=value)

        def write_name_type_val(self, type, nom, value):
            write_name_type_val(self, type=type, nom=nom, value=value)

        def write_vars(self, name:str, value: str = '', vars: List[str] = [], varsEx: List[str] = [],
                       varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '',
                       domain:str = 'all'):
            """Register the values of name on the selected variables."""
            if not name in self.noms:
                name = nomsExtUnique(self, name)
                if not name in self.noms:
                    print('The name "{}" doesn\'t exist.'.format(name))
                    sys.exit()

            indexNom = self.noms.index(name)
            indexes = getIndexes(self, names=[name], namesEx=[], namesTypes=[], namesTypesEx=[], namesTypesFormula='',
                                 vars=vars, varsEx=varsEx, varsTypes=varsTypes, varsTypesEx=varsTypesEx, varsTypesFormula=varsTypesFormula,
                                 corpus='all', domain=domain)
            indexesVars = indexes['vars']
            show_data(self,[indexNom],indexesVars)
            if indexesVars:
                if value:
                    answer = input("Set the value of this variables to \"{}\" ? (y/n) : ".format(value))
                if answer in self.yes or value == '' :
                    write_vars(self, indexNom, indexesVars, value)
                    show_data(self, [indexNom], indexesVars)
            else:
                print(color.bold+'No variable to be set.'+color.end)

        def write_names(self, vars: List[str] = [], varsEx: List[str] = [], varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '', domain:str = 'all',
                        names: List[str] = [], namesEx: List[str] = [], namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '', corpus:str = 'all'):
            """Register the values of the selected names on the selected variables."""
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
                                 corpus, domain)
            write_names(self,indexes['noms'],indexes['vars'])

        def write_names_value(self,value:str, var: str,
                        names: List[str] = [], namesEx: List[str] = [], namesTypes: List[str] = [], namesTypesEx: List[str] = [],
                        namesTypesFormula:str = '', corpus='all'):
            """Assign the given value to the selected variable of all selected names."""
            indexVar = varToIndex(self, var)
            indexes = getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
                                 vars=[var], varsEx=[], varsTypes=[], varsTypesEx=[], varsTypesFormula=[],
                                 corpus=corpus, domain='all')
            indexesNoms =  indexes['noms']
            show_data(self, indexesNoms, [indexVar])
            if indexVar and indexesNoms and value:
                answer = input("Set the value of the variable \"" + str(var) + "\" to \"" + str(value) + "\" for all this names ? (y/n) : ")
                if answer in self.yes:
                    write_names_value(self, value, indexVar, indexesNoms)
                    show_data(self, indexesNoms, [indexVar])
            else:
                print(color.bold + 'No change.' + color.end)



        def write_type_vars(self, varsType, vars: List[str] = [], varsEx: List[str] = [],
                            varsTypes: List[str] = [], varsTypesEx: List[str] = [], varsTypesFormula:str = '', domain:str = 'all'):
            write_type_vars(self, varsType, vars=vars, varSauf=varsEx,
                            varsTypes=varsTypes, varsTypeSauf=varsTypesEx, varsTypesFormule=varsTypesFormula,
                            domaine=domain)

        def write_var_types(self, var, varsTypes: List[str] = [], varsTypesEx: List[str] = []):
            """Record the types of a variable."""
            write_var_types(self, var, varsTypes=varsTypes, varsTypesEx=varsTypesEx)

        def write_name_types(self, name, namesTypes: List[str] = [], namesTypesEx: List[str] = []):
            """Record the types of a name."""
            write_nom_types(self, name, namesTypes=namesTypes, namesTypesEx=namesTypesEx)

        def write_type_names(self, nomsType, names: List[str] = [], namesEx: List[str] = [],
                             namesTypes: List[str] = [], namesTypesEx: List[str] = [], namesTypesFormula:str = '', corpus:str = 'all'):
            write_type_names(self, nomsType, names=names, namesEx=namesEx,
                             namesTypes=namesTypes, namesTypesEx=namesTypesEx, namesTypesFormula=namesTypesFormula,
                             corpus=corpus)

        def write_name_thamous(self, name, id, table, project=''):
            #remove the 't' at the beginning of table.
            if table[0] == 't': table = table[1:]
            write_name_thamous(self, name, id, table, project)


        def drop_col_db(self, table, col):
            drop_col_db(self, table, col)

        #############################################################################
        # Methods from sql
        #############################################################################
        def newVar(self, newVar, var, position='after'):
            newVar(self, newVar, var, position)

        def newNom(self, newName):
            newName(self, newName)

        def saveToDb(self):
            saveToDb(self)

    except NameError as e:
        print(e)
    except:
        print(e)

