import numpy as np
import pandas as pd
import collections
import csv

from .basics import *
from .quotations import *




def load_csv(self, fileIn, varsTypes = [], varsDefs=[],
                 nomsTypes = [],
                 varsTypesRegles = '', nomsTypesRegles = '',nomsDefs=[],
                 citations = []):

    if type(fileIn) == str: fileIn = [fileIn]
    frames = []
    noms = []
    variables = []
    files=[] #liste des adresses des fichiers des variables
    varsToIndexesFiles={} # dictionnaire : var:index fichier
    # de variables
    for f in fileIn:
        try:
            ar = np.array(pd.read_csv(open(f,encoding="UTF-8"), delimiter=","))
        except FileNotFoundError:
            print("File \"" + f + "\" doesn't exist.")
            sys.exit(1)

        # Suppression des colonnes (resp. lignes) dont le nom est vide
        # enregistrement pour chaque variable du numéro de son fichier csv.
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


        newVars=ar[1, 1:].tolist()
        indexFile=len(files)
        varsToIndexesFiles.update({v: indexFile for v in newVars})
        files.append(f)
        variables += newVars
        frames.append(pd.DataFrame(ar[2:, 1:]).replace(np.nan, ''))

    self.array = pd.concat(frames, axis=1, join='inner')
    data = np.array(self.array)
    self.data = data
    self.selectedData = data

    variables = [str(x) for x in variables]
    self.vars = variables
    self.selectedVars = self.vars
    self.selectedIndexesVars = [i for i in range(len(self.vars))]

    self.varsToIndexesFiles=varsToIndexesFiles
    self.files=files

    # initialisation des types de variables
    if varsTypes:
        set_vars_types_csv(self, varsTypes, varsTypesRegles=varsTypesRegles)
        self.vars_types_with_def = []
        self.vars_types_without_def = self.vars_types_types
        self.varsTypes_exists = True
    else:
        self.varsTypes_exists = False
        self.vars_types_types=[]
        self.vars_types_data=[[] for v in self.vars]
        self.varsRegles = {}

    # initialisation des définitions des variables
    if varsDefs:
        self.varsDefs_exists = True
        set_vars_defs_csv(self, varsDefs)
    else:
        self.varsDefs_exists = False
        self.vars_defs_dic = {v: '' for v in self.vars}

    self.vars_augmented = vars_augmented(self, self.vars)


    try:
        poids = list(map(int, poids))
    except:
        poids = [1] * (len(variables))
    self.poids = poids
    self.selectedPoids = poids

    noms = [str(x) for x in noms]
    self.noms = noms
    self.selectedNoms = noms
    self.selectedIndexesNoms = [i for i in range(len(self.selectedNoms))]

    # initialisation des citations associées aux variables
    if citations:
        set_citations_csv(self, citations)
        self.citations_exists = True
    else:
        self.citations_exists = False


    # initialisation des définitions des noms
    if nomsDefs:
        set_noms_defs_csv(self, nomsDefs)
        self.nomsDefs_exists = True
    else:
        self.nomsDefs_exists = False
        self.noms_defs_dic = {n: '' for n in self.noms}

    self.noms_augmented = noms_augmented(self, self.noms)

    # initialisation des types de noms
    if nomsTypes:
        set_noms_types_csv(self, nomsTypes, nomsTypesRegles=nomsTypesRegles)
        self.names_types_with_def = []
        self.names_types_without_def = self.noms_types_types
        self.nomsTypes_exists = True
    else:
        self.nomsTypes_exists = False
        self.noms_types_types=[]
        self.noms_types_data=[[] for n in self.noms]
        self.nomsRegles = {}
    self.data_augmented = data_augmented(self)



def set_vars_types_csv(self, fileIn, varsTypesRegles = '',pasColonne=10, pasLigne=10):
    if type(fileIn) == str: fileIn = [fileIn]
    fr = pd.DataFrame([])
    types = []
    for f in fileIn:
        try:
            ar = np.array(pd.read_csv(open(f,encoding="UTF-8"), delimiter=","))
        except:
            print("The file of types \"" + f + "\" cannot be opened")
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
    varsTypesError = sorted(list(set(variables) - set(self.vars)))
    varSansType = sorted(list(set(self.vars) - set(variables)))

    if varsTypesError:
        print('')
        print('')
        print(color.bold + str(len(varsTypesError))+' unrecognized variables with types : ' + color.end)
        display(pd.DataFrame(columns=varsTypesError))

    if varSansType:
        print('')
        print('')
        print(color.bold  + str(len(varSansType))+ ' variables without type : ' + color.end)
        display(pd.DataFrame(columns=varSansType))

    if varsTypesError or varSansType : sys.exit(1)

    # L'ensemble des variables des tableaux de valeurs et des types coïncident
    #contrôle des doublons

    if len(variables) != len(set(self.vars)):
        print(color.bold + 'Variables with the same name :' + color.end)
        doubles = [item for item, count in collections.Counter(variables).items() if count > 1]
        print('')
        print(','.join(map(str, doubles)))
        sys.exit(1)

    #réordonnement des variables des types
    fr = fr[self.vars]
    #réordonnement des types
    fr = fr.reindex(index=types)


    ar = fr.values
    self.vars_types_data = ar.tolist()
    self.vars_types_vars = fr.columns.tolist()
    self.vars_types_types = [tp for tp in types if not tp == '']


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
            except FileNotFoundError:
                print("The file \"" + file + "\" doesn't exist.")
                sys.exit(1)

        # dictionnaire des règles : type : règle
        self.varsRegles = {r[0] : r[1] for r in reglesListe if not r[0] == '' }
        self.vars_types_data = applyRegles(self,self.vars_types_data,
                                                  self.vars_types_types,
                                                  self.varsRegles)
    else:
        self.varsRegles = {}




def set_noms_types_csv(self, fileIn, nomsTypesRegles='',
                   pasColonne=10, pasLigne=10):
    if type(fileIn) == str: fileIn = [fileIn]
    fr = pd.DataFrame([])
    types = []
    for f in fileIn:
        try:
            ar = np.array(pd.read_csv(open(f, encoding="UTF-8"), delimiter=","))
        except:
            print("The file of types \"" + f + "\" cannot be opened")
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
    nomsTypesError = sorted(list(set(noms) - set(self.noms)))
    nomSansType = sorted(list(set(self.noms) - set(noms)))

    if nomsTypesError:
        print('')
        print('')
        print(color.bold + str(len(nomsTypesError)) + ' unrecognized names with types : ' + color.end)
        display(pd.DataFrame(columns=nomsTypesError))

    if nomSansType:
        print('')
        print('')
        print(color.bold + str(len(nomSansType)) + ' mames without type : ' + color.end)
        display(pd.DataFrame(columns=nomSansType))

    if nomsTypesError or nomSansType: sys.exit(1)

    # L'ensemble des noms des tableaux de valeurs et des types coïncident
    # contrôle des doublons
    if len(noms) != len(set(self.noms)):
        print(color.bold + 'Repeated names :' + color.end)
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

    # application des règles
    if nomsTypesRegles:
        try:
            array_regles = np.array(pd.read_csv(open(nomsTypesRegles, encoding="UTF-8"), delimiter=","))
        except:
            print("The file of rules \"" + f + "\" cannot be open")
            sys.exit(1)
        ar = pd.DataFrame(array_regles).replace(np.nan, '')

        reglesListe = ar.values
        # dictionnaire des règles : type : règle
        self.nomsRegles = {r[0]: r[1] for r in reglesListe if not r[0] == ''}
        self.noms_types_data = applyRegles(self,self.noms_types_data,
                                                  self.noms_types_types,
                                                  self.nomsRegles)
    else:
        self.nomsRegles = {}

##########################################################################################
### types noms
##########################################################################################

def set_noms_defs_csv(self, fileIn):
    if type(fileIn) == str: fileIn = [fileIn]
    fr = pd.DataFrame([])
    files = []
    nomsToIndexesNomsDefsFiles = {}  # dictionnaire : var:index fichier des définitions des noms

    for f in fileIn:
        try:
            ar = np.array(pd.read_csv(open(f, encoding="UTF-8"), delimiter=","))
            # print(ar)
        except:
            print("The names definitions file \"" + f + "\" cannot be open")
            sys.exit(1)

        # Suppression des lignes dont le nom est vides
        i = 2
        while i < np.size(ar, 0):
            if str(ar[i, 0]) == 'nan':
                ar = np.delete(ar, i, 0)
            else:
                i += 1

        # noms ayant une définition
        self.noms_defs_noms = [str(ar[i, 0]) for i in
                                 range(len(ar[0:, 0])) if str(ar[i, 1]) != 'nan']
        newNoms = ar[2:, 0].tolist()
        indexNomsDefsFile = len(files)
        nomsToIndexesNomsDefsFiles.update({v: indexNomsDefsFile for v in newNoms})
        files.append(f)

        index = newNoms
        cols = ['Définition']
        num_rows, num_cols = ar.shape
        if num_cols >=4 and ar[1, 2] == 'Thamous table' and ar[1, 3] == 'Thamous id' and ar[1,4] == 'Thamous projet':
            thamous = True
            cols += ['Thamous table', 'Thamous id', 'Thamous projet']
            ar = ar[2:, 1:5]
        else:
            thamous = False
            ar = ar[2:, 1]
        fr_new = pd.DataFrame(ar, index=index, columns=cols)
        fr = pd.concat([fr_new, fr], axis=1)

    # remplace les nan par des ''
    fr = pd.DataFrame(fr).replace(np.nan, '')

    noms = [str(x) for x in fr.index.tolist()]
    if thamous:
        defs = [str(x) if str(x) != 'nan' else '' for x in ar[0:, 0].tolist()]
        tables = [str(x) if str(x) != 'nan' else '' for x in ar[0:, 1].tolist()]
        ids = [str(x) if str(x) != 'nan' else '' for x in ar[0:, 2].tolist()]
        prjts = [str(x) if str(x) != 'nan' else '' for x in ar[0:, 3].tolist()]
    else:
        defs = [str(x) if str(x) != 'nan' else '' for x in ar[0:].tolist()]
    # noms sans déf (=absentes du tableau des defs) et noms définis non reconnues
    nomsDefsError = sorted(list(set(noms) - set(self.noms)))
    nomSansDef = sorted(list(set(self.noms) - set(noms)))

    if nomsDefsError:
        print('')
        print('')
        print(color.bold + str(len(nomsDefsError)) + ' unrecognized names with definition : ' + color.end)
        display(pd.DataFrame(columns=nomsDefsError))

    if nomSansDef:
        print('')
        print('')
        print(color.bold + str(len(nomSansDef)) + ' unedefined names : ' + color.end)
        display(pd.DataFrame(columns=nomSansDef))

    # if varsDefsError or varSansDef : sys.exit(1)

    # L'ensemble des noms des tableaux de valeurs et des défs coïncident
    # contrôle des doublons

    if len(noms) != len(set(self.noms)):
        print(color.bold + 'Repeated names :' + color.end)
        doubles = [item for item, count in collections.Counter(noms).items() if count > 1]
        print('')
        print(','.join(map(str, doubles)))
        # sys.exit(1)

    # réordonnement des variables des défs
    # fr = fr[self.__vars]
    # réordonnement des défs
    # fr = fr.reindex(index=defs)

    # dictionnaire : nom:def pour les noms ayant une définition
    nomsDefsDicPart = {noms[i]: defs[i] for i in range(len(noms))}
    if thamous:
        nomsTablesDicPart = {noms[i]: tables[i] for i in range(len(noms))}
        nomsIdsDicPart = {noms[i]: ids[i] for i in range(len(noms))}
        nomsPrjtsDicPart = {noms[i]: prjts[i] for i in range(len(noms))}
    # dictionnaire : var:def pour toutes les variables définies
    self.noms_defs_dic = {v: (nomsDefsDicPart[v] if v in nomsDefsDicPart else '') for v in self.noms}
    if thamous:
        self.noms_tables_dic = {v: (nomsTablesDicPart[v] if v in nomsTablesDicPart else '') for v in self.noms}
        self.noms_ids_dic = {v: (nomsIdsDicPart[v] if v in nomsIdsDicPart else '') for v in self.noms}
        self.noms_prjts_dic = {v: (nomsPrjtsDicPart[v] if v in nomsPrjtsDicPart else '') for v in self.noms}

    self.noms_augmented = noms_augmented(self,self.noms)
    self.names_without_def = [n for n in self.noms if self.noms_defs_dic[n] == '']
    self.nomsToIndexesNomsDefsFiles = nomsToIndexesNomsDefsFiles
    self.nomsDefsFiles = files


def set_vars_defs_csv(self, fileIn):
    if type(fileIn) == str: fileIn = [fileIn]
    fr = pd.DataFrame([])
    defs = []
    files = []  # liste des adresses des fichiers des définitions variables
    varsToIndexesVarsDefsFiles = {}  # dictionnaire : var:index fichier des définitions des variables
    for f in fileIn:
        try:
            ar = np.array(pd.read_csv(open(f, encoding="UTF-8"), delimiter=","))
            # print(ar)
        except:
            print("The file of definitions \"" + f + "\" cannot be opened")
            # sys.exit(1)

        # Suppression des colonnes (resp. lignes) dont le nom est vide
        j = 1
        while j < np.size(ar, 1):
            if str(ar[1, j]) == 'nan':
                ar = np.delete(ar, j, 1)
            else:
                j += 1

        # variables ayant une définition
        self.vars_defs_vars = [str(ar[1, i]) for i in
                               range(len(ar[1, 0:])) if str(ar[2, i]) != 'nan']
        newVars = ar[1, 1:].tolist()
        indexVarsDefsFile = len(defs)
        varsToIndexesVarsDefsFiles.update({v: indexVarsDefsFile for v in newVars})
        files.append(f)
        cols = newVars
        index = ['Définition']
        ar = ar[2:, 1:]
        fr_new = pd.DataFrame(ar, index=index, columns=cols)
        fr = pd.concat([fr_new, fr], axis=1)

    # remplace les nan par des ''
    fr = pd.DataFrame(fr).replace(np.nan, '')

    variables = [str(x) for x in fr.columns.tolist()]

    defs = [str(x) if str(x) != 'nan' else '' for x in ar[0, 0:].tolist()]

    # variables sans déf (=absentes du tableau des defs) et variables définies non reconnues
    varsDefsError = sorted(list(set(variables) - set(self.vars)))
    varSansDef = sorted(list(set(self.vars) - set(variables)))

    if varsDefsError:
        print('')
        print('')
        print(color.bold + str(len(varsDefsError)) + ' unrecognized variables with definition : ' + color.end)
        display(pd.DataFrame(columns=varsDefsError))

    if varSansDef:
        print('')
        print('')
        print(color.bold + str(len(varSansDef)) + ' variables non définies : ' + color.end)
        display(pd.DataFrame(columns=varSansDef))

    # if varsDefsError or varSansDef : sys.exit(1)

    # L'ensemble des variables des tableaux de valeurs et des défs coïncident
    # contrôle des doublons

    if len(variables) != len(set(self.vars)):
        print(color.bold + 'Repeated variables :' + color.end)
        doubles = [item for item, count in collections.Counter(variables).items() if count > 1]
        print('')
        print(','.join(map(str, doubles)))
        # sys.exit(1)

    # réordonnement des variables des défs
    # fr = fr[self.vars]
    # réordonnement des défs
    # fr = fr.reindex(index=defs)

    # dictionnaire : var:def pour les variables ayant une définition
    varsDefsDicPart = {variables[i]: defs[i] for i in range(len(variables))}
    # dictionnaire : var:def pour toutes les variables définies
    self.vars_defs_dic = {v: (varsDefsDicPart[v] if v in varsDefsDicPart else '') for v in self.vars}
    self.vars_augmented = vars_augmented(self,self.vars)
    self.vars_sans_def = [v for v in self.vars if self.vars_defs_dic[v] == '']
    self.varsToIndexesVarsDefsFiles = varsToIndexesVarsDefsFiles
    self.varsDefsFiles = files


def set_citations_csv(self, fileIn):
    """
    Initialisastion des citations associées aux valeurs.
    """
    if type(fileIn) == str: fileIn = [fileIn]
    frames = []
    vars_citations = []
    noms_citations = []
    filesCitations = []  # liste des adresses des fichiers des citations
    varsToIndexesFilesCitations = {}  # dictionnaire : var:index fichier
    for f in fileIn:
        try:
            ar = np.array(pd.read_csv(open(f, encoding="UTF-8"), delimiter=","))
        except:
            print("The file of quotations \"" + f + "\" cannot be opened")
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

        newVarsCitations = ar[1, 1:].tolist()
        indexFile = len(filesCitations)
        vars_citations += newVarsCitations
        varsToIndexesFilesCitations.update({v: indexFile for v in newVarsCitations})
        filesCitations.append(f)
        if not len(frames):
            noms_citations = ar[2:, 0].tolist()

        frames.append(pd.DataFrame(ar[2:, 1:]).replace(np.nan, ''))

    self.array = pd.concat(frames, axis=1, join='inner')
    data_cit = np.array(self.array)

    vars_citations = [str(x) for x in vars_citations]

    self.varsToIndexesFilesCitations = varsToIndexesFilesCitations
    self.filesCitations = filesCitations

    # variables avec citation non reconnues
    varsCitationsError = sorted(list(set(vars_citations) - set(self.vars)))

    if varsCitationsError:
        print('')
        print('')
        print(color.bold + str(len(varsCitationsError)) + ' unrecognized variables with quotations : ' + color.end)
        display(pd.DataFrame(columns=varsCitationsError))
        sys.exit(1)

    # Les variables avec citations existent bien
    # contrôle des doublons

    if len(vars_citations) != len(set(vars_citations)):
        print(color.bold + 'Repeated variables with quotations :' + color.end)
        doubles = [item for item, count in collections.Counter(vars_citations).items() if count > 1]
        print('')
        print(','.join(map(str, doubles)))
        sys.exit(1)

    line = [''] * len(self.vars)
    cit = [line] * len(self.noms)
    # copie de self.__data dans data_citations
    # tableau vide pour les citations
    citations = []
    for n in range(len(self.noms)):
        line = []
        empty = []
        for v in range(len(self.vars)):
            line.append(self.data[n][v])
            empty.append('')
        citations.append(empty)

    for nn in range(len(noms_citations)):
        for vv in range(len(vars_citations)):
            n = self.noms.index(noms_citations[nn])
            v = self.vars.index(vars_citations[vv])
            val = self.data[n][v]
            citations[n][v] = data_cit[nn][vv]
    self.citations = citations



def write_val_csv(self, nom, var, value):
    file = self.files[self.varsToIndexesFiles[var]]
    filename, file_extension = os.path.splitext(file)
    newfile = filename+'_temp' + file_extension
    with open(file, encoding="UTF-8") as inf, open(newfile, 'w', encoding="UTF-8", newline='') as outf:
        reader = csv.reader(inf, delimiter=",")
        writer = csv.writer(outf, delimiter=",")
        i = 0
        for row in reader:
            if i == 2:  # ligne des variables
                indexVar = row.index(var)
            elif i > 2 and row[0] == nom:
                row[indexVar] = html.unescape(value)
            writer.writerow(row)
            i = i+1

    try:
        os.remove(file)
        os.rename(newfile, file)
    except PermissionError:
        print(color.red + "The file \"" + file + "\" cannot be opened" + color.end)


def write_var_definition_csv(self, var, definition):
    file = self.varsDefsFiles[self.varsToIndexesVarsDefsFiles[var]]
    filename, file_extension = os.path.splitext(file)
    newfile = filename + '_temp' + file_extension

    with open(file, encoding="UTF-8") as inf, open(newfile, 'w', encoding="UTF-8", newline='') as outf:
        reader = csv.reader(inf, delimiter=",")
        writer = csv.writer(outf, delimiter=",")
        i = 0
        for row in reader:
            if i == 2:  # ligne des variables
                indexVar = row.index(var)
            if i == 3:
                row[indexVar] = html.unescape(definition)
            writer.writerow(row)
            i = i + 1

    try:
        os.remove(file)
        os.rename(newfile, file)
    except PermissionError:
        print(color.red + "The file \"" + file + "\" cannot be opened" + color.end)


def write_nom_definition_csv(self, indexNom, definition):
    nom = self.noms[indexNom]
    file = self.nomsDefsFiles[self.nomsToIndexesNomsDefsFiles[nom]]
    filename, file_extension = os.path.splitext(file)
    newfile = filename + '_temp' + file_extension

    with open(file, encoding="UTF-8") as inf, open(newfile, 'w', encoding="UTF-8", newline='') as outf:
        reader = csv.reader(inf, delimiter=",")
        writer = csv.writer(outf, delimiter=",")
        for row in reader:
            if row[0] == nom:
                row[1] = html.unescape(definition)
            writer.writerow(row)

    try :
        os.remove(file)
        os.rename(newfile, file)
    except PermissionError:
        print(color.red + "The file of names definitions \""+ file +"\" cannot be opened" + color.end)


def write_citation_csv(self, nom, var, citation):
    file = self.filesCitations[self.varsToIndexesFilesCitations[var]]
    filename, file_extension = os.path.splitext(file)
    newfile = filename+'_temp' + file_extension
    with open(file, encoding="UTF-8") as inf, open(newfile, 'w', encoding="UTF-8", newline='') as outf:
        reader = csv.reader(inf, delimiter=",")
        writer = csv.writer(outf, delimiter=",")
        i = 0
        for row in reader:
            if i == 2:  # ligne des variables
                indexVar = row.index(var)
            elif i > 2 and row[0] == nom:
                row[indexVar] = html.unescape(citation)
            writer.writerow(row)
            i = i+1

    try:
        os.remove(file)
        os.rename(newfile, file)
    except PermissionError:
        print(color.red + "The file of quotations \"" + file + "\" cannot be opened" + color.end)

def rename_var_csv(self, var, newVar):
    #TODO
    print('Todo')