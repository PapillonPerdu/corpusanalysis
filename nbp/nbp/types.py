import pandas as pd
import numpy as np
import sys
from .basics import *

def set_vars_types(self, fileIn, varsTypesRegles=''):
    """
    initialisation des types de variable
    """
    if type(fileIn) == str: fileIn = [fileIn]
    fr = pd.DataFrame([])
    types = []
    for f in fileIn:
        try:
            ar = np.array(pd.read_csv(open(f, encoding="UTF-8"), delimiter=","))
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
        types = types + [str(x) for x in index if x not in types]

    # remplace les nan par des ''
    fr = pd.DataFrame(fr).replace(np.nan, '')

    variables = [str(x) for x in fr.columns.tolist()]

    # variables sans types et variables typées non reconnues
    varsTypesError = sorted(list(set(variables) - set(self.vars)))
    varSansType = sorted(list(set(self.vars) - set(variables)))

    if varsTypesError:
        print('')
        print('')
        print(color.bold + str(len(varsTypesError)) + ' variables typées non reconnues : ' + color.end)
        display(pd.DataFrame(columns=varsTypesError))

    if varSansType:
        print('')
        print('')
        print(color.bold + str(len(varSansType)) + ' variables ayant des valeurs sans type : ' + color.end)
        display(pd.DataFrame(columns=varSansType))

    if varsTypesError or varSansType: sys.exit(1)

    # L'ensemble des variables des tableaux de valeurs et des types coïncident
    # contrôle des doublons

    if len(variables) != len(set(self.vars)):
        print(color.bold + 'Variables ayant le même nom :' + color.end)
        doubles = [item for item, count in collections.Counter(variables).items() if count > 1]
        print('')
        print(','.join(map(str, doubles)))
        sys.exit(1)

    # réordonnement des variables des types
    fr = fr[self.vars]
    # réordonnement des types
    fr = fr.reindex(index=types)

    ar = fr.values
    self.vars_types_data = ar.tolist()
    self.vars_types_vars = fr.columns.tolist()
    self.vars_types_types = [tp for tp in types if not tp == '']
    print('Types de variables : ' + str(len(self.vars_types_types)))

    # application des règles
    if varsTypesRegles:
        reglesListe = []
        if type(varsTypesRegles) == str:
            varsTypesRegles = [varsTypesRegles]

        for file in varsTypesRegles:
            try:
                array_regles = np.array(pd.read_csv(open(file, encoding="UTF-8"),
                                                    delimiter=","))
                ar = pd.DataFrame(array_regles).replace(np.nan, '')
                reglesListe = reglesListe + ar.values.tolist()
            except:
                print("Impossible d\'ouvrir le fichier des règles \"" + file + "\"")
                sys.exit(1)

        # dictionnaire des règles : type : règle
        regles = {r[0]: r[1] for r in reglesListe}
        self.vars_types_data = self.applyRegles(self.vars_types_data,
                                                self.vars_types_types,
                                                regles)


def set_noms_types(self, fileIn, nomsTypesRegles=''):
    """
    Initialisation des types de noms
    """
    if type(fileIn) == str: fileIn = [fileIn]
    fr = pd.DataFrame([])
    types = []
    for f in fileIn:
        try:
            ar = np.array(pd.read_csv(open(f, encoding="UTF-8"), delimiter=","))
        except:
            print("Impossible d\'ouvrir le fichier des types \"" + f + "\"")
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
        index = ar[2:, 0].tolist()
        cols = ar[1, 1:].tolist()
        ar = ar[2:, 1:]
        fr_new = pd.DataFrame(ar, index=index, columns=cols)
        fr = pd.concat([fr_new, fr], axis=1)

        # pour préserver l'ordre des types
        types = types + [str(x) for x in cols if x not in types]

    # remplace les nan par des ''
    fr = pd.DataFrame(fr).replace(np.nan, '')

    noms = [str(x) for x in fr.index.tolist()]

    # noms sans types et noms typées non reconnues
    nomsTypesError = sorted(list(set(noms) - set(self.noms)))
    nomSansType = sorted(list(set(self.noms) - set(noms)))

    if nomsTypesError:
        print('')
        print('')
        print(color.bold + str(len(nomsTypesError)) + ' noms typés non reconnus : ' + color.end)
        display(pd.DataFrame(columns=nomsTypesError))

    if nomSansType:
        print('')
        print('')
        print(color.bold + str(len(nomSansType)) + ' noms ayant des valeurs sans type : ' + color.end)
        display(pd.DataFrame(columns=nomSansType))

    if nomsTypesError or nomSansType: sys.exit(1)

    # L'ensemble des noms des tableaux de valeurs et des types coïncident
    # contrôle des doublons
    if len(noms) != len(set(self.noms)):
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
    self.noms_types_data = ar.tolist()
    self.noms_types_noms = fr.index.tolist()
    self.noms_types_types = [tp for tp in types if not tp == '']
    print('Types de noms : ' + str(len(self.noms_types_types)))

    # application des règles
    if nomsTypesRegles:
        try:
            array_regles = np.array(pd.read_csv(open(nomsTypesRegles, encoding="UTF-8"), delimiter=","))
        except:
            print("Impossible d\'ouvrir le fichier des règles \"" + f + "\"")
            sys.exit(1)
        ar = pd.DataFrame(array_regles).replace(np.nan, '')

        reglesListe = ar.values
        # dictionnaire des règles : type : règle
        regles = {r[0]: r[1] for r in reglesListe}
        self.noms_types_data = self.applyRegles(self.noms_types_data,
                                                self.noms_types_types,
                                                regles)

def getIndexesNomsTypes(self,
                        nomsTypes, nomsTypeSauf):

    for tp in nomsTypes:
        try:
            v = self.noms_types_types.index(tp)
        except:
            print(color.bold + "Type  \"", tp, "\" unrecognized" + color.end)
            sys.exit(1)

    if len(nomsTypes) == 0: nomsTypes = self.noms_types_types

    indexesNomsTypes = [self.noms_types_types.index(v) for v in nomsTypes if v not in nomsTypeSauf]
    indexesNomsTypes = sorted(list(set(indexesNomsTypes)))
    return indexesNomsTypes

def getIndexesVarsTypes(self,
                                varsTypes, varsTypeSauf):

        for tp in varsTypes:
            try:
                v = self.vars_types_types.index(tp)
            except:
                print(color.bold + "Type  \"", tp, "\" unrecognized" + color.end)
                sys.exit(1)

        if len(varsTypes) == 0: varsTypes = self.vars_types_types

        indexesVarsTypes = [self.vars_types_types.index(v) for v in varsTypes if v not in varsTypeSauf]
        indexesVarsTypes = sorted(list(set(indexesVarsTypes)))
        return indexesVarsTypes

def show_vars_types(self, indexesVars,indexesVarsTypeSortie,
                    pasColonne= 10,pasLigne=10):
    print(color.bold + 'Variables types : ' + color.end)

    index = [self.vars_types_types[t] for t in indexesVarsTypeSortie]
    columns = [var_augmented(self, self.vars[v]) for v in indexesVars if self.vars[v] in self.vars_types_vars]
    lines = [[self.vars_types_data_augmented[t][v] for v in indexesVars] for t in indexesVarsTypeSortie]

    printLines(lines, columns=columns, index=index,pasColonne=pasColonne,pasLigne=pasLigne)


def show_noms_types(self,indexesNoms, indexesNomsTypeSortie,pasColonne=10,pasLigne=10):

    index = [nom_augmented(self, self.noms[n]) for n in indexesNoms if self.noms[n] in self.noms_types_noms]
    columns = [self.noms_types_types[t] for t in indexesNomsTypeSortie]
    lines = [[self.noms_types_data_augmented[n][t] for t in indexesNomsTypeSortie] for n in indexesNoms]

    if indexesNoms:
        print ('names : '+ str(len(indexesNoms)))
    print('types : '+str(len(indexesNomsTypeSortie)))
    print(color.bold + 'Names types : ' + color.end)

    printLines(lines, columns=columns, index=index,pasColonne=pasColonne,pasLigne=pasLigne)

def var_type_value_augmented(self, type, var, value):
    if str(value).strip() == '':
        value = '-'
        style = "style=\"color:black;cursor:pointer;\""
    else:
        style = "style=\"color:black;font-weight: bold;font-size: 14px;cursor:pointer;\""

    return "<a " + style +  \
            "onmouseup=\"click_on_var_type_value(event, \'" + html.escape(str(type).replace("'", "&#x27;")) + "\',\'" + \
           html.escape(str(var).replace("'", "&#x27;")) + "\',\'" + \
           self.instanceName + "\');\">" + str(value) + "</a>"


def nom_type_value_augmented(self, type, nom, value):
    if str(value).strip() == '':
        value = '-'
        style = "style=\"color:black;cursor:pointer;\""
    else:
        style = "style=\"color:black;font-weight: bold;font-size: 14px;cursor:pointer;\""

    return "<a " + style + \
           "onmouseup=\"click_on_nom_type_value(event, \'" + html.escape(str(type).replace("'", "&#x27;")) + "\',\'" + \
           html.escape(str(nom).replace("'", "&#x27;")) + "\',\'" +\
           self.instanceName + "\');\">" + str(value) + "</a>"
