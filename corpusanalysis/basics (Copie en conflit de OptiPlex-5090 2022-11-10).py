import sys
import pandas as pd
import numpy as np
from sympy import *
from IPython.display import display, HTML
from collections import defaultdict
from operator import itemgetter
import csv
import os

from .utils import *
from .defs import *


def getIndexes(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula,
               vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula,
               corpus, domain):
    indexesNoms = getIndexesNoms(self, names, namesEx, namesTypes, namesTypesEx, namesTypesFormula)
    indexesVars = getIndexesVars(self, vars, varsEx, varsTypes, varsTypesEx, varsTypesFormula)
    if not (corpus == 'all' and domain == 'all'):
        indexes = corpusdomaine(self, corpus, domain, indexesNoms, indexesVars)
    else:
        indexes={'noms':indexesNoms,'vars':indexesVars}
    return indexes


# détermination d'indexesVars à partir de
# vars,varSauf,varsTypes,varsTypeSauf,varsTypesFormule
def getIndexesVarsStrict(self,vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule):

    varsT = []
    if varsTypesFormule:
        varsT = varsTypesFormulaToVars(self, 'self.typeToIndexesVars', varsTypesFormule)

    if varsTypes:
        if varsT:
            varsT = list(set(typesToVars(self, varsTypes)).intersection(set(varsT)))
        else:
            varsT = typesToVars(self, varsTypes)

    if vars:
        if varsT:
            vars = list(set(vars).intersection(set(varsT)))
    else:
        vars = varsT

    varsTSauf = []
    if varsTypeSauf:
        varsTSauf = typesToVars(self, varsTypeSauf)

    if varSauf:
        if varsTSauf:
            varSauf = list(set(varSauf)).union(set(varsTSauf))
    else:
        varSauf = varsTSauf

    indexesVars = varsToIndexesVars(self, vars, varSauf)

    return indexesVars

def getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule):
    if vars: vars = varsExt(self, toList(vars))
    if varSauf: varSauf = varsExt(self, toList(varSauf))
    if varsTypes: varsTypes = varsTypesExt(self, toList(varsTypes))
    if varsTypeSauf: varsTypeSauf = varsTypesExt(self, toList(varsTypeSauf))

    indexesVars = getIndexesVarsStrict(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

    if not indexesVars:
        indexesVars = [i for i in range(len(self.vars))]

    return indexesVars

def getIndexesNomsStrict(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule):
    nomsT = []
    if nomsTypesFormule:
        nomsT = nomsTypesFormulaToNoms(self, 'self.typeToIndexesNoms', nomsTypesFormule)
    if nomsTypes:
        if nomsT:
            nomsT = list(set(typesToNoms(self, nomsTypes)).intersection(set(nomsT)))
        else:
            nomsT = typesToNoms(self, nomsTypes)

    if noms:
        if nomsT:
            noms = list(set(noms).intersection(set(nomsT)))
    else:
        noms = nomsT

    nomsTSauf = []
    if nomsTypeSauf:
        nomsTSauf = typesToNoms(self, nomsTypeSauf)

    if nomSauf:
        if nomsTSauf:
            nomSauf = list(set(nomSauf)).union(set(nomsTSauf))
    else:
        nomSauf = nomsTSauf

    indexesNoms = nomsToIndexesNoms(self, noms, nomSauf)

    return indexesNoms

def getIndexesNoms(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule):
    if noms: noms = nomsExt(self, toList(noms))
    if nomSauf: nomSauf = nomsExt(self, toList(nomSauf))
    if nomsTypes: nomsTypes = nomsTypesExt(self, toList(nomsTypes))
    if nomsTypeSauf: nomsTypeSauf = nomsTypesExt(self, toList(nomsTypeSauf))

    indexesNoms = getIndexesNomsStrict(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

    if not indexesNoms:
        indexesNoms = [n for n in range(len(self.noms))]

    return indexesNoms


##########################################################################################
### Méthodes communes
######################################################################################
from io import StringIO
from html.parser import HTMLParser

class MLStripper(HTMLParser):
    #source : https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def exportToCSV(lines, columns = [],index = []):
    filename = input("File name ?")
    filename, file_extension = os.path.splitext(filename)
    if not file_extension == 'csv':
        filename += '.csv'

    with open(filename, mode='w') as csvfile:
        csvWriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for line in lines:
            line = map(strip_tags, line)
            csvWriter.writerow(line)

def replaceValue(value,replace):
    if replace :
        values = [rp[0] for rp in replace]
        newVal = replace[values.index(value)][1] if value in values else value
        return newVal
    else :
        return value

def replaceLine(line,replace):
    if replace:
        values = [rp[0] for rp in replace]
        newLine=[l if not l in values else replace[values.index(l)][1] for l in line]
        return newLine
    else :
        return line

#Replace the exact values given in lines using the correpondences given in replace
def replaceLines(lines,replace):
    values = [rp[0] for rp in replace]
    newLines=[[l if not l in values else replace[values.index(l)][1] for l in line] for line in lines]
    return newLines

def printLines(lines, columns=[],index=[], pasColonne=0, pasLigne=0, width='50px',
               replaceValues=[], replaceNames=[], replaceVars=[],
               export = False) :
    if pasColonne:
        res = repeteIndex(pasColonne, lines, columns, index)
        lines = res[0]
        columns = res[1]

    if pasLigne:
        res = repeteColumns(pasLigne, lines, columns, index)
        lines = res[0]
        index = res[1]

    if replaceValues :
        lines=replaceLines(lines,replaceValues)

    if replaceNames :
        columns = replaceLine(columns, replaceNames)

    if replaceVars :
        index = replaceLine(index,replaceVars)

    df = pd.DataFrame(lines, columns=columns, index=index)
    display(HTML(df.to_html(escape=False,col_space=width,bold_rows=True,render_links=True)))
    if export :
        filename = input("File name ?")
        filename, file_extension = os.path.splitext(filename)
        if not file_extension == 'csv':
            filename += '.csv'
        index = map(strip_tags, index)
        columns = map(strip_tags, columns)
        df.to_csv(filename,index=index, columns=columns)
        #exportToCSV(lines, columns=columns, index=index)

def show_dashboard(self):
    columns = ['<b>Names</b>', '<b>Variables</b>']
    index = ['Number', '<b>Defined</b>', '<b>Not defined</b>', '<b>Types</b>', '<b>Types defined</b>', '<b>Types not defined</b>']

    lineNumber = [len(self.noms), len(self.vars)]

    if self.varsDefs_exists:
        ldv = len(self.vars) - len(self.vars_sans_def)
        lndv = len(self.vars_sans_def)
    else :
        ldv = 0
        lndv = len(self.vars)

    if self.nomsDefs_exists:
        ldn = len(self.noms) - len(self.names_without_def)
        lndn = len(self.names_without_def)
    else:
        ldn = 0
        lndn = len(self.noms)

    lineDefined = [ldn, ldv]
    lineNotDefined = [lndn, lndv]

    if self.nomsTypes_exists :
        lntt = len(self.noms_types_types)
        ldnt = len(self.names_types_with_def)
        lndnt = len(self.names_types_without_def)
    else:
        lntt=0
        ldnt='-'
        lndnt='-'

    if self.varsTypes_exists :
        lvtt=len(self.vars_types_types)
        ldvt = len(self.vars_types_with_def)
        lndvt = len(self.vars_types_without_def)
    else:
        lvtt=0
        ldvt='-'
        lndvt='-'

    lineTypes = [lntt, lvtt]
    lineTypesDefined = [ldnt,ldvt]
    lineTypesNotDefined = [lndnt,lndvt]

    lines = [lineNumber, lineDefined, lineNotDefined, lineTypes,lineTypesDefined,lineTypesNotDefined]

    df = pd.DataFrame(lines, columns=columns, index=index)
    display(HTML(df.to_html(escape=False)))

    values = novalues = 0
    for n in range(len(self.noms)) :
        for v in range(len(self.vars)):
            if self.data[n][v] in self.nuls :
                novalues += 1
            else:
                values += 1

    columnsData = ['values','no values']
    indexData = ['Data']
    linesData=[[values, novalues]]
    df = pd.DataFrame(linesData, columns=columnsData, index=indexData)
    display(HTML(df.to_html(escape=False)))


def get_langues(self):
    try:
        res = self.data[0:, varToIndex(self,'langue')].tolist()
        return list(set(res))
    except:
        return []

def show_data(self,indexesNoms,indexesVars,
              pasColonne=10, pasLigne=10,
              values = True, citations = False, width = '',
              replaceValues= [],replaceNames=[],replaceVars=[],
              decoration=True,
              export = False):

    if width :
        width=width.replace(' ','')
        if 'px' not in width:
            width+='px'

    if (len(indexesVars) == len(self.vars) or len(indexesNoms) == len(self.noms)) and len(indexesVars) >= 50 and len(indexesNoms) >= 10:
        answer =  input("Show " + str(len(indexesVars)) + " variables ? It can be quite long...")
        if not answer in self.yes :
            sys.exit(1)
    lines = []
    resNoms = []
    if replaceValues :
        valuesReplaced = [cpl[0] for cpl in replaceValues]
        
    for i in indexesNoms :
        if values :
            if decoration :
                lines.append([self.data_augmented[i][k] for k in indexesVars])
            elif replaceValues :
                lines.append(
                    [self.data_augmented[i][k] if self.data[i][k] not in valuesReplaced else replaceValues[valuesReplaced.index(self.data[i][k])][1] for k in
                     indexesVars])
            else :
                lines.append(
                    [self.data_augmented[i][k] for k in indexesVars])

        if citations :
            lines.append([self.citations[i][k] for k in indexesVars])

        resNoms.append(self.noms_augmented[i] if decoration else replaceValue(self.noms[i],replaceNames))

        if values and citations :
            resNoms.append('')
    resVars = [self.vars_augmented[i] if decoration else replaceValue(self.vars[i],replaceVars) for i in indexesVars]

    print('names : ' + str(len(indexesNoms)))
    print('Variables : ' + str(len(indexesVars)))
    printLines(lines, columns=resVars, index=resNoms,
               pasColonne=pasColonne, pasLigne=pasLigne,width=width,
               replaceValues=replaceValues, replaceNames=replaceNames,replaceVars=replaceVars,
               export = export)


def show_names(self, indexesNoms):
    """
        Affiche le tableau des noms choisis.
        :param self:
        :param noms: liste de noms sélectionnés
        :param nomSauf: liste de noms exclus
        :param nomsTypes: liste de types de noms sélectionnés
        :param nomsTypeSauf: liste de types de noms exclus
        :param nomsTypesFormule: formule propositionnelle sur les types de noms
        :return: tableau des valeurs pour les noms et les variables choisis
        """

    listNoms = ['Noms'] + [self.noms_augmented[n] for n in indexesNoms]
    print("Names : " + str(len(indexesNoms)))
    printLines([], columns=listNoms)



def get_vars(self,indexesVars):
    listVars = [self.vars[v] for v in indexesVars]
    return listVars

def show_vars(self, indexesVars):
    """Display the selected variables."""
    listVars = ['Variables'] + [self.vars_augmented[v] for v in indexesVars]
    print('Variables : ' + str(len(indexesVars)))
    printLines([], columns=listVars)


def indexToVar(self, num):
    return self.vars[num]

def indexToVar_augmented(self, num):
    return var_augmented(self,self.vars[num])

def indexToNom(self, num):
    return self.noms[num]

def indexToSelectedNom(self, num):
    return self.selectedNoms[num]

def varToIndex(self, chain):
    try:
        return self.vars.index(chain)
    except:
        print("\"" + str(chain) + "\" n'est pas le nom d'une variable.")
        sys.exit(1)

def nomToIndex(self, nom):
    # index1=np.where(self.noms == nom)

    if type(nom) == str:
        try:
            return self.noms.index(nom)
        except:
            sys.exit(color.bold + "Le nom \"" + nom + "\" n'est pas reconnu." + color.end)

    if type(nom) == int:
        try:
            return self.noms[nom]
        except:
            print(color.bold + "Le nom \"" + nom + "\" n'est pas reconnu." + color.end)
            sys.exit(1)

def indexNomToRedindex(self,
                       num, indexesNoms):
    print(indexesNoms)
    return indexesNoms.index(num)

def redindexNomToIndex(self,
                       num, indexesNoms):
    return self.noms.index(self.selectedNoms[num])

def redindexVarToIndex(self,
                       num, indexesVars):
    return self.vars.index(self.selectedVars[num])

def redindexNomToNom(self,
                     num, indexesNoms):
    return self.noms[indexesNoms[num]]

def nomToRedindex(self,
                  nom, indexesNoms):
    return indexNomToRedindex(self,self.noms.index(nom), indexesNoms)

def nomsToIndexes(self, noms):
    indexes = [nomToIndex(self,nom) for nom in noms]
    return indexes

def varToNum(self, chain):
    vars = [i for i in range(len(self.vars)) if
            str(chain).replace('\n', '').strip() in str(self.vars[i]).replace('\n', '').strip()]
    for v in vars:
        print(v + 1)
        print(self.vars[v].replace('\n', ' '))
        print()

def varsInter(self,
              var1, var2=''):
    if var2 == '': var2 = var1
    try:
        index1 = self.selectedVars.index(var1)
    except:
        print("La variable \"" + var1 + "\" n'est pas sélectionnée.")
        exit(1)

    try:
        index2 = self.selectedVars.index(var2) + 1
    except:
        print("La variable \"" + var2 + "\" n'est pas sélectionnée.")
        exit(1)

    if index1 > index2:
        print("La variable \"" + var1 + "\" doit être avant \"" + var2 + "\"")
        exit(1)
    else:
        return self.selectedVars[index1:index2]

def interNames(self,
               name1, name2=''):
    if name2 == '': name2 = name1
    try:
        index1 = self.noms.index(name1)
    except:
        print("L'édition \"" + name1 + "\" n'existe pas.")
    try:
        index2 = self.noms.index(name2) + 1
    except:
        print("L'édition \"" + name2 + "\" n'existe pas.")

    if index1 > index2:
        print("L'édition \"" + name1 + "\" doit être avant \"" + name2 + "\"")
    else:
        return self.noms[index1:index2]

def namesBelow(self, nom):
    try:
        index = self.noms.index(nom)
        return self.noms[index:len(self.noms)]
    except:
        print("Le nom \"" + nom + "\" n'est pas reconnu")

def namesBelowStrict(self, nom):
    try:
        index = self.noms.index(nom)
        return self.noms[index + 1:len(self.noms)]
    except:
        print("Le nom \"" + nom + "\" n'est pas reconnu")

def namesAbove(self, nom):
    try:
        indexNom = nomToIndex(self,nom)
        return self.noms[0:indexNom + 1]
    except:
        print("Le nom \"" + nom + "\" n'est pas reconnu")

def namesAboveStrict(self, nom):
    """
    Liste des noms venant avant le nom donné (nom exclu).
    """
    try:
        indexNom = self.nomToIndex(nom)
        return self.noms[0:indexNom]
    except:
        print("Le nom \"" + nom + "\" n'est pas reconnu")


def varsBefore(self, var):
    """
    Liste des variables avant la variable donnée (comprise).
    :param self:
    :param var:
    :return:
    """
    try:
        index = self.vars.index(var)
        return self.vars[0:index + 1]
    except:
        print("La variable \"" + var + "\" n'est pas reconnue")

def varsAfter(self, var):
    try:
        index = self.vars.index(var)
        return self.vars[index:len(self.vars)]
    except:
        print("La variable \"" + var + "\" n'est pas reconnue")


def indexes_like(self,
                 indexNom, indexesNoms, indexesVars, pourcent):
    """
    Liste des indexes des éditions ayant les mêmes valeurs qu'une édition donnée, à un pourcentage près, sur un domaine de variables donné
    :param self:
    :param indexNom:
    :param indexesNoms:
    :param indexesVars:
    :param pourcent:
    :return:
    """

    indexesNomsRes = [i for i in indexesNoms if \
                      listsEqual(self.data[indexNom], self.data[i], indexesVars, pourcent)]
    return indexesNomsRes

# Liste des indexes des éditions ayant les mêmes valeurs qu'une édition donnée, à un pourcentage près,
# sur un domaine de variables donné
def like(self,indexNom,indexesNoms,indexesVars,
         pourcent=100):
    # print(color.bold+str(self.__vars[start-1]).replace('\n',' ')+ ", précision "+str(pourcent)+"% : "+color.end)

    indexesNomsRes = indexes_like(self,indexNom, indexesNoms, indexesVars, pourcent)
    nomsRes = [indexToNom(self,n) for n in indexesNomsRes]
    return nomsRes




def set_selectedIndexesVars(self, indexesVars):
    self.selectedIndexesVars = indexesVars
    self.selectedVarsCard = len(self.selectedIndexesVars)
    self.selectedVars = [self.vars[v] for v in self.selectedIndexesVars]
    if self.poidsExist :
        self.selectedPoids = [self.poids[i] for i in self.selectedIndexesVars]
    self.selectedDistMax = sum(self.selectedPoids) if self.poidsExist else self.selectedVarsCard

def set_selectedIndexesNoms(self, indexesNoms):
    self.selectedIndexesNoms = indexesNoms
    self.selectedNomsCard = len(self.selectedIndexesNoms)
    self.selectedNoms = [self.noms[n] for n in self.selectedIndexesNoms]

def set_selectedVars(self, vars):
    self.selectedVars = vars
    self.selectedVarsCard = len(self.selectedVars)
    self.selectedIndexesVars = [self.varToIndex(var) for var in self.selectedVars]
    if self.poidsExist:
        self.selectedPoids = [self.poids[i] for i in self.selectedIndexesVars]
    self.selectedDistMax = sum(self.selectedPoids) if self.poidsExist else self.selectedVarsCard
    self.matrices()
    self.show_selectedVars

def set_selectedNoms(self, noms):
    self.selectedNoms = noms
    self.selectedNomsCard = len(self.selectedNoms)
    self.selectedIndexesNoms = [nomToIndex(self,(nom)) for nom in self.selectedNoms]
    self.matrices()
    self.show_selectedNoms

@property
def card(self):
    print(self.card)

# variables pour lesquelles une édition a une vraie valeur (i.e. n'a pas une valeur exclue)
def indexesVarsDefiniesNom(self,
                           indexNom, indexesVars):
    trueVars = [i for i in indexesVars if not self.data[indexNom][i] in self.exclus]
    return trueVars

# variables pour lesquelles des éditions ont une vraie valeur (i.e. n'a pas une valeur exclue)
def indexesVarsDefinies(self,
                        indexesNoms, indexesVars):
    trueVars = []
    for n in indexesNoms:
        trueVars += indexesVarsDefiniesNom(self,n, indexesVars)

    trueVars = sorted(list(set(trueVars)))
    return trueVars

# nombre de variables pour lesquelles l'édition a une vraie valeur (i.e. n'a pas une valeur exclue)
def totalVarsNom(self,
                 indexNom, indexesVars):
    trueVars = indexesVarsDefiniesNom(self,indexNom, indexesVars)
    return len(trueVars)

# nombre de variables pour lesquelles une liste d'éditions ont une vraie valeur (i.e. n'a pas une valeur exclue)
def totalVarsDefinies(self,
                      indexesNoms, indexesVars):
    trueVars = indexesVarsDefinies(self,indexesNoms, indexesVars)
    return len(trueVars)

# nombre total des variables (différentes) dans un dictionnaire/collection de listes de variables
def collTotal(self, coll):
    vals = []
    for k, l in coll.items():
        vals += l
    vals = set(vals)
    return len(vals)

    # indexes des variables d'un type, parmi une liste d'indexes de variables,

# vals contient la liste des valeurs des variables.
def stats(self,
          vals, indexesVars):
    sum = 0
    total = 0
    sumPond = 0
    for k in range(len(vals)):
        poids = self.poids[redindexVarToIndex(self,k, indexesVars)] if self.poidsExist else 1
        if poids != 0:
            total += 1
            if vals[k] != '':
                sum += 1
                sumPond += poids
    try:
        return [int(round(100 * sumPond / total)), sum]
    except:
        return [0, sum]

# sur lesquelles deux éditions données
# ont des valeurs définies
def indexesVarsDefiniesConjointes(self,
                                  indexNom1, indexNom2, indexesVars):
    indexesVarsDef = []
    for i in indexesVars:
        if self.data[indexNom1][i] not in self.exclus and \
                self.data[indexNom2][i] not in self.exclus:
            indexesVarsDef.append(i)
    return indexesVarsDef

# nombre des variables d'un type, parmi une liste d'indexes de variables,
# sur lesquelles deux éditions données
# ont des valeurs définies
def totalVarsDefiniesConjointes(self,
                                indexNom1, indexNom2, indexesVars):
    indexesVarsDef = indexesVarsDefiniesConjointes(self,indexNom1, indexNom2, indexesVars)
    return len(indexesVarsDef)

# somme pondérée de variables d'un type, parmi une liste d'indexes de variables,
# sur lesquelles deux éditions données
# ont des valeurs définies
def totalPondereVarsDefiniesConjointes(self,
                                       indexNom1, indexNom2, indexesVars):
    indexesVarsDef = indexesVarsDefiniesConjointes(self,indexNom1, indexNom2, indexesVars)
    if self.poidsExist:
        sum = 0
        for v in indexesVarsDef:
            sum += self.poids[v]
    else:
        sum = len(indexesVarsDef)
    return sum

def varsToIndexesVars(self,listVars, listVarSauf=[]):
    indexesVars = []
    if type(listVars) == int:
        try:
            v = indexToVar(self,listVars)
        except:
            print(color.bold + "La variable n°", listVars, " n'est pas reconnue." + color.end)
            sys.exit(1)
        listVars = [v]

    if type(listVars) == str:
        try:
            v = self.vars.index(listVars)
        except:
            print(color.bold + "La variable \"", listVars, "\" n'est pas reconnue." + color.end)
            sys.exit(1)
        listVars = [listVars]

    # if len(listVars) == 0: listVars = self.vars
    if listVars:
        indexesVars = [varToIndex(self,v) for v in listVars if v not in listVarSauf]
        indexesVars = sorted(list(set(indexesVars)))
    return indexesVars


def communs(self,
            indexNom1, indexNom2, indexesVars):
    """ liste des valeurs définies de premier nom, contenues dans celles de deuxième nom, parmi des variables, donnés par leurs indexes. """
    comp = []
    for v in indexesVars:
        if not self.data[indexNom1][v] in self.exclus and \
                not self.data[indexNom2][v] in self.exclus and \
                strEqual(self.data[indexNom1][v], self.data[indexNom2][v]):
            comp.append(self.data[indexNom2][v])
        else:
            comp.append('')

    return comp

def communsStrict(self,
                  indexNom1, indexNom2, indexesVars):
    """liste des valeurs définies de premier nom, contenues dans celles de deuxième nom, parmi des variables, donnés par leurs indexes. """
    comp = []
    for k in indexesVars:
        if not self.data[indexNom1][k] in self.exclus and \
                not self.data[indexNom2][k] in self.exclus and \
                strEqualStrict(self.data[indexNom1][k], self.data[indexNom2][k]):
            comp.append(self.data[indexNom2][k])
        else:
            comp.append('')

    return comp

def difference(self,
               indexNom1, indexNom2, indexesVars):
    """" liste des valeurs définies de premier nom, différentes de celles de deuxième nom, parmi des variables, donnés par leurs indexes """
    diff = []
    for k in indexesVars:
        if not self.data[indexNom1][k] in self.exclus and \
                not self.data[indexNom2][k] in self.exclus and \
                not strEqual(self.data[indexNom1][k], self.data[indexNom2][k]):
            diff.append(self.data_augmented[indexNom1][k])
        else:
            diff.append('')

    return diff

def differenceStrict(self,
                     indexNom1, indexNom2, indexesVars):
    """liste des valeurs de nom1, strictement différentes de celles de nom2, parmi des variables, donnés par leurs indexes."""
    diff = []
    for k in indexesVars:
        if not self.data[indexNom1][k] in self.exclus and \
                not self.data[indexNom2][k] in self.exclus and \
                not strEqualStrict(self.data[indexNom1][k], self.data[indexNom2][k]):
            diff.append(self.data_augmented[indexNom1][k])
        else:
            diff.append('')

    return diff


# List of variables on which two texts are different
def vars_difference(self ,indexNom1 ,indexNom2 ,indexesVars):

    diff = differenceStrict(self ,indexNom1, indexNom2, indexesVars)
    indexVars_diff = sorted([indexesVars[i] for i in range(len(indexesVars)) if not diff[i] in self.nuls])

    return indexVars_diff


def show_difference(self,
                    indexNom1, indexNom2, indexesVars ,
                    pasColonne=10 ,pasLigne=10 ,width='', decoration = True):
    diff = [differenceStrict(self ,indexNom1, indexNom2, indexesVars),
            difference(self ,indexNom2, indexNom1, indexesVars)]

    # ligne avec les critères
    if decoration:
        varsL = [self.vars_augmented[v] for v in indexesVars]
        nomsL = [self.noms_augmented[indexNom1], self.noms_augmented[indexNom2]]
    else:
        varsL = [self.vars[v] for v in indexesVars]
        nomsL = [self.noms[indexNom1], self.noms[indexNom2]]
    print('Variables : ' + str(len(varsL)))
    printLines(diff, columns=varsL, index=nomsL, pasColonne=pasColonne, pasLigne=pasLigne, width=width)


def show_difference_types(self,
                          indexNom1, indexNom2, indexesVars,
                          indexesVarsTypeSortie,
                          effectifType=0, EffectifType=0,
                          pourcenType=0, PourcenType=100):

    indexesVarsDifference = indexesVarsDifferenceStrict(self ,indexNom1, indexNom2,
                                                        indexesVars)

    collTypes = indexesVarsToDictTypesIndexesVars(self ,indexesVarsDifference, indexesVarsTypeSortie)

    lines = []

    indexesTypesDifferenceComplet = sorted([t for t in indexesVarsTypeSortie
                                            if self.vars_types_types[t] in collTypes])
    typesDifferenceComplet = [self.vars_types_types[i] for i in indexesTypesDifferenceComplet]
    effectifs = effectifsTypes(self ,[indexNom1, indexNom2], indexesVars, indexesTypesDifferenceComplet)

    if effectifType or EffectifType:
        # restriction de indexesVarsTypes
        if EffectifType == 0: EffectifType = len(self.vars)
        indexesTypesDifferenceComplet = [indexesTypesDifferenceComplet[i] \
                                         for i in range(len(indexesTypesDifferenceComplet)) \
                                         if int(EffectifType) >= int(effectifs[i + 1]) >= int(effectifType)]
        typesDifferenceComplet = [self.vars_types_types[i] for i in indexesTypesDifferenceComplet]

        total = effectifs[0]
        effectifs.pop(0)
        effectifs = [e for e in effectifs if int(EffectifType) >= e >= int(effectifType)]
        effectifs.insert(0, total)

    line0 = []
    line1 = []
    line2 = []
    line3 = []
    total = collTotal(self ,collTypes)
    line0.append(effectifs[0])
    line1.append(total)
    line2.append(str(round(total / effectifs[0] * 100)) + '%')
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
                line3.append(str(prc) + '%')
                typesReduits.append(tp)

        i += 1
    lines.append(line0)
    lines.append(line1)
    lines.append(line2)
    lines.append(line3)
    print(color.bold + self.noms[indexNom1] + '/' + self.noms[indexNom2] + color.end)

    printLines(lines, columns=['Total'] + typesReduits,
               index=['Effectifs', 'différence', '%différences', '%type'])




def vars_common(self, indexNom1, indexNom2, indexesVars):
    com = communsStrict(self ,indexNom1, indexNom2, indexesVars)
    vars_com = [indexToVar(self ,indexesVars[i]) for i in range(len(indexesVars)) if not com[i] in self.nuls]
    return vars_com


# Liste des indexes de variables sur lesquelles deux éditions diffèrent
def indexes_vars_commun(self,
                        indexNom1, indexNom2, indexesVars):

    com = communsStrict(self ,indexNom1, indexNom2, indexesVars)
    indexesVars_com = [indexesVars[i] for i in range(len(indexesVars)) if not com[i] == '']
    return indexesVars_com

# indexes des variables pour lesquelles deux éditions ont les mêmes valeurs
def indexesVarsCommunStrict(self,
                            indexNom1, indexNom2, indexesVars):
    com = []
    for k in indexesVars:
        if not self.data[indexNom1][k] in self.exclus and \
                not self.data[indexNom2][k] in self.exclus and \
                strEqualStrict(self.data[indexNom1][k], self.data[indexNom2][k]):
            com.append(k)

    return com

# indexes des variables pour lesquelles deux éditions ont des valeurs différentes
def indexesVarsDifferenceStrict(self,
                                indexNom1, indexNom2, indexesVars):
    diff = []
    for k in indexesVars:
        if not strEqualStrict(self.data[indexNom1][k], self.data[indexNom2][k]):
            diff.append(k)

    return diff


def show_common(self, indexNom1, indexNom2, indexesVars):
    com = [communsStrict(self ,indexNom1, indexNom2, indexesVars)]

    # ligne avec les critères
    varsL = [self.vars_augmented[v] for v in indexesVars]
    nomsL = [self.noms_augmented[indexNom1] + '/' + self.noms_augmented[indexNom2]]
    printLines(com, columns=varsL, index=nomsL)

# valeurs communes d'une édition avec d'autres éditions,
# en précisant le pourcentage d'éditions ayant cette valeur
# l'idée est de récupérer ainsi les variables "rares" communes à deux éditions
def show_names_common_percent(self,
                              indexNom, indexesNoms, indexesVars,
                              percent=0, Percent=100,
                              pasColonne=10, pasLigne=10):

    linesNoms = [[] for n in indexesNoms]
    totalNoms = [0 for n in indexesNoms]
    resVars = []

    pourcents = []
    totaux = []
    for v in indexesVars:
        indexesNomsCommun = indexes_like(self ,indexNom, indexesNoms, [v], 100)
        if indexNom in indexesNomsCommun: indexesNomsCommun.remove(indexNom)
        total = len(indexesNomsCommun)
        prc = round(100 * total / len(indexesNoms))
        if Percent >= prc > percent:
            resVars.append(self.vars_augmented[v])
            for n in range(len(indexesNoms)):
                indexN = indexesNoms[n]
                if indexN in indexesNomsCommun:
                    linesNoms[n].append(self.data[indexN][v])
                    totalNoms[n] += 1
                else:
                    linesNoms[n].append('')

            totaux.append(total)
            pourcents.append(prc)

    lines = []
    resNoms = []
    for n in range(len(indexesNoms)):
        indexN = indexesNoms[n]
        if totalNoms[n]:
            total = totalNotNull(self ,linesNoms[n])
            lines.append([total] + linesNoms[n])
            resNoms.append(self.noms_augmented[indexN])
    lines.append([''] + totaux)
    lines.append([''] + pourcents)

    columns = ['Total'] + resVars
    index = resNoms + ['total', '%']

    printLines(lines, columns=columns, index=index ,pasColonne=pasColonne ,pasLigne=pasLigne)

def show_common_types(self,
                      indexNom1, indexNom2, indexesVars,
                      indexesVarsTypeSortie,
                      effectifType=0, EffectifType=0,
                      percenType=0, PercenType=100,order=''):

    indexesVarsCommun = indexesVarsCommunStrict(self ,indexNom1, indexNom2 ,indexesVars)

    collTypes = indexesVarsToDictTypesIndexesVars(self,
                                                  indexesVarsCommun,
                                                  indexesVarsTypeSortie)
    print(collTypes)
    lines = []

    indexesTypesCommunComplet = sorted([t for t in indexesVarsTypeSortie \
                                        if self.vars_types_types[t] in collTypes])
    typesCommunComplet = [self.vars_types_types[i] for i in indexesTypesCommunComplet]
    effectifs = effectifsTypes(self ,[indexNom1, indexNom2], indexesVars, indexesTypesCommunComplet)

    if effectifType or EffectifType:
        # restriction de indexesVarsTypes
        if EffectifType == 0: EffectifType = len(self.vars)
        indexesTypesCommunComplet = [indexesTypesCommunComplet[i] \
                                     for i in range(len(indexesTypesCommunComplet)) \
                                     if EffectifType >= effectifs[i + 1] >= effectifType]
        typesCommunComplet = [self.vars_types_types[i] for i in indexesTypesCommunComplet]

        total = effectifs[0]
        effectifs.pop(0)
        effectifs = [e for e in effectifs if EffectifType >= e >= effectifType]
        effectifs.insert(0, total)

    # première ligne avec l'effectif total pour chaque type

    line0 = [] #effectifs
    line1 = [] #communs
    line2 = [] #pourcentages communs
    line3 = [] #pourcentages communs par type
    total = collTotal(self ,collTypes)

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

            if PercenType >= prcType >= percenType:
                typesReduits.append(tp)
                line0.append(effectifs[i])
                line1.append(val)
                line2.append(str(prcCommuns) + '%')
                line3.append(prcType)

        i += 1

    if order=='asc' or order=='desc':
        reverse = False if order == 'asc' else True
        line3,line0,line1,line2 = zip(*sorted(zip(line3,line0,line1,line2), reverse=reverse))
        line0 = list(line0)
        line1 = list(line1)
        line2 = list(line2)
        line3 = list(line3)


    line0=[total]+line0
    line1=['']+line1
    line2=['']+line2
    line3=['']+[str(p)+'%' for p in line3]
    lines.append(line0)
    lines.append(line1)
    lines.append(line2)
    lines.append(line3)
    print(color.bold + self.noms[indexNom1] + '/' +self.noms[indexNom2] + color.end)
    printLines(lines, columns=['Total'] + typesReduits,
               index=['Effectifs', 'communs', '%communs', '%type'])

    # Retourne la somme et la somme pondérée


# vals contient la liste des valeurs des variables.
def stats(self,
          vals, indexesVars):
    sum = 0
    total = 0
    sumPond = 0
    for k in range(len(vals)):
        pds = self.poids[redindexVarToIndex(self, k, indexesVars)] if self.poidsExist else 1
        if pds != 0:
            total += 1
            if vals[k] != '':
                sum += 1
                pds = self.poids[redindexVarToIndex(self, k, indexesVars)] if self.poidsExist else 1
                sumPond += pds
    try:
        return [int(round(100 * sumPond / total)), sum]
    except:
        return [0, sum]


def corpusdomaine(self,corpus, domaine, indexesNoms, indexesVars):
    '''
    :param self:
    :param domaine: valeur du domaine
    :param corpus: valeur du corpus
    :param indexesVars:
    :param indexesNoms:
    :return: (indexesNoms,indexesVars) satisfying the values of domaine and corpus
    '''
    # domaine = 'all' pas de restriction
    # domaine = 'positif' : les valeurs en sont pas nulles
    # domaine = 'strict' : les valeurs doivent être positivement définies
    # domaine = 'null' : les valeurs sont nulles

    if domaine == "defined":
        testDomaine = self.nuls
        testDBoole = False
    elif domaine == "positif":
        testDomaine = self.exclus
        testDBoole = False
    elif domaine == "strict":
        testDomaine = self.notStrict
        testDBoole = False
    elif domaine == "null":
        testDomaine = self.nuls
        testDBoole = True
    else:
        domaine = "all"
        testDBoole = True

    if corpus == "defined":
        testCorpus = self.nuls
        testCBoole = True
    elif corpus == "positif":
        testCorpus = self.exclus
        testCBoole = True
    elif corpus == 'strict':
        testCorpus = self.notStrict
        testCBoole = True
    elif corpus == 'null':
        testCorpus = self.nuls
        testCBoole = False
    else:
        corpus = "all"
        testCBoole = True

    if not domaine == 'all' or not corpus == 'all':
        indexesNomsRed = []
        for n in indexesNoms:
            booleCorpus = True
            indexesVarsRed = []
            for v in indexesVars:
                if domaine == "all" or (self.data[n][v] in testDomaine) == testDBoole:
                    indexesVarsRed.append(v)
                    if not corpus == "all" and (self.data[n][v] in testCorpus) == testCBoole:
                        booleCorpus = False

            if booleCorpus:
                indexesNomsRed.append(n)
            indexesVars = indexesVarsRed

        return {'noms': indexesNomsRed, 'vars':indexesVarsRed}
    else:
        return {'noms':indexesNoms, 'vars':indexesVars}


def indexesToVars(self, indexesVars):
    return [self.vars[v] for v in indexesVars]

def indexesToNoms(self, indexesNoms):
        return [self.noms[n] for n in indexesNoms]

def nomsToIndexesNoms(self, listNoms, listNomSauf=[]):
    if type(listNoms) == str:
        try:
            n = self.noms.index(listNoms)
        except:
            print(color.bold + "Le nom \"" + listNoms + "\" ne fait pas partie des noms sélectionnés." + color.end)
            sys.exit(1)
        listNoms = [listNoms]

    if len(listNoms) == 0: listNoms = self.noms

    indexesNoms = [nomToIndex(self,n) for n in listNoms if n not in listNomSauf]
    indexesNoms = sorted(list(set(indexesNoms)))
    return indexesNoms



# nombre de variables pour lesquelles l'édition a une vraie valeur (i.e. n'a pas une valeur exclue)
def totalVars(self, indexNom, indexesVars):
    trueVars = [i for i in indexesVars if not self.data[indexNom][i] in self.exclus]
    return len(trueVars)


# liste du nombre de variables pour chaque type d'une édition donnée,
# avec au début le total sur l'ensemble des types
def effectifsTypesNom(self,
                      indexNom, indexesVars, indexesVarsTypes):
    effectifs = [totalVarsNom(self,indexNom, indexesVars)] + \
                [totalVarsDefiniesTypeNom(self,indexNom, indexesVars, self.vars_types_types[tp]) for tp in
                 indexesVarsTypes]
    return effectifs

# liste du nombre de variables pour chaque type d'une liste d'éditions donnée,
# avec au début le total sur l'ensemble des types
def effectifsTypes(self, indexesNoms, indexesVars, indexesVarsTypes):
    effectifs = [totalVarsDefinies(self,indexesNoms, indexesVars)] + \
                [totalVarsDefiniesType(self,indexesNoms, indexesVars, tp) for tp in indexesVarsTypes]
    return effectifs
# NON UTILISE
# fonction de calcul de la proximité
def prox(L1, L2, poids):
    prox = 0
    for i in range(len(L1)):
        if L1[i] != '*' and L2[i] != '*' and L1[i] != '?' and L2[i] != '?':
            prox += (strEqual(L1[i], L2[i])) * poids[i]
    return prox



# Liste des variables sur lesquelles une édition diffère d'une liste d'éditions
def vars_relative_difference(self, indexNom, indexesNoms, indexesVars):

    ListeL = [self.data[i] for i in indexesNoms]
    indexesVarsDiff = []
    for i in indexesVars:
        eq = False
        for l in ListeL:
            if strEqual(l[i], self.data[indexNom][i]):
                eq = True
                break
        if not eq: indexesVarsDiff.append(i)

    indexesVarsDiff = sorted(indexesVarsDiff)
    varsDiff = [indexToVar(self,i) for i in indexesVarsDiff]

    return varsDiff

def show_difference_relative(self,indexNom,indexesNoms,indexesVars):
    varsDiff = self.vars_relative_difference(indexNom, indexesNoms, indexesVars)
    display(pd.DataFrame(columns=varsDiff))


# Liste des indexes de variables sur lesquelles une éditions est égale à une édition d'une liste d'éditions
def vars_relative_sum(self, indexNom, indexesNoms, indexesVars):

    ListeL = [self.data[i] for i in indexesNoms]
    indexesVarsSum = []
    for i in indexesVars:
        eq = False
        for l in ListeL:
            if strEqual(l[i], self.data[indexNom][i]):
                eq = True
                break
        if eq: indexesVarsSum.append(i)

    return indexesVarsSum



# répète la colonne de noms pour un pas donné
def repeteIndex(pas, data, columns, index):
    i = pas
    while i < len(columns):
        columns.insert(i, '')
        for j in range(len(index)):
            data[j].insert(i,index[j])
        i += pas + 1
    return [data, columns]

# répète la ligne de critères pour un pas donné
def repeteColumns(pas, data, columns, index):
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


# complète le tableau de types (data)
# à partir d'un dictionnaire de règles (regles)
# pour les types (types)
def applyRegles(self,data, types, regles) :
    #print(types)
    # parcours des types ayant une regle
    for type, regle in regles.items() :
        if regle :
            typesRegle = list(map(str.strip,regle.split('&')))
            if type in types and typesRegle != [''] :
                indexType = types.index(type)
                for ssType in typesRegle :
                    neg = False
                    if ssType[0]=='~' :
                        neg = True
                        ssType = ssType[1:].strip()

                    testssType = False
                    try :
                        index_ssType = types.index(ssType)
                        testssType =  True
                    except :
                        print('\"'+color.bold+ssType+color.end+'\" dans la règle de \"'+color.bold+types[indexType]+color.end+'\" n\'est pas un type reconnu.')

                    if testssType :
                        for i in range(len(data[0])) :
                            if data[indexType][i] != '':
                                if (data[index_ssType][i] == '' and neg == False) or (
                                        data[index_ssType][i] != '' and neg == True):
                                    data[index_ssType][i] = '*'

    return data



def equalVals(self, indexNom, indexesVars, values):
    '''

    :param indexNom:
    :param indexesVars:
    :param values:
    :return: [percentage of values of indexNom strEqual to values, ['' if strEqual, value if different]]
    '''

    total = 0
    diff = []
    for i in range(len(indexesVars)):
        if self.data[indexNom][indexesVars[i]] == values[i]:
            diff.append('')
            total += 1
        else:
            diff.append(self.data[indexNom][indexesVars[i]])
    prc = round(total / len(indexesVars) * 100)
    res = [prc, diff]
    return res


def totalNotNull(self, l):
    total = len(l) - l.count('')
    return total

def indexesVarsDefiniesTypeNom(self,
                               indexNom, indexesVars, indexType):
    indexesVarsType = indexVarsTypeToIndexesVars(self,indexType, indexesVars)
    trueVars = [i for i in indexesVarsType if not self.data[indexNom][i] in self.exclus]
    return trueVars

# nombre de variables d'un type donné pour lesquelles l'édition
# a une vraie valeur (i.e. n'a pas une valeur exclue)
def totalVarsDefiniesTypeNom(self,
                             indexNom, indexesVars, indexType):
    trueVars = indexesVarsDefiniesTypeNom(self,indexNom, indexesVars, indexType)
    return len(trueVars)

# variables d'un type donné pour lesquelles les éditions d'une liste ont une vraie valeur (i.e. n'a pas une valeur exclue)
def indexesVarsDefiniesType(self,
                            indexesNoms, indexesVars, indexVarsType):
    trueVars = []
    for n in indexesNoms:
        trueVars += indexesVarsDefiniesTypeNom(self,n, indexesVars,indexVarsType)

    trueVars = sorted(list(set(trueVars)))
    return trueVars

# nombre de variables d'un type donné pour lesquelles l'édition a une vraie valeur (i.e. n'a pas une valeur exclue)
def totalVarsDefiniesType(self,
                          indexesNoms, indexesVars, indexVarsType):
    trueVars = indexesVarsDefiniesType(self,indexesNoms, indexesVars, indexVarsType)
    return len(trueVars)


def varToTypes(self, var):
    tps = [tp for tp in self.vars_types_types if var in typeToVars(self,tp)]
    return tps

def varToindexesTypes(self, var):
    indexesTypes = [self.vars_types_types.index(tp) \
                    for tp in self.vars_types_types \
                    if var in typeToVars(self,tp)]
    return indexesTypes

# types d'une variable
def show_var_types(self, var):
    types = varToTypes(self,var)
    typesL = [[tp] for tp in types]

    df=pd.DataFrame(typesL, columns=[var_augmented(self,var)])
    display(HTML(df.to_html(escape=False)))

# variables d'un type donné
def show_vars_type(self, tp):
    varsT = vars_augmented(self,typeToVars(self,tp))
    print('Variables : ' + str(len(varsT)))
    df=pd.DataFrame(columns=[tp + ':'] + varsT)
    display(HTML(df.to_html(escape=False)))

def indexVarToTypes(self, indexVar):
    return varToTypes(self,self.vars[indexVar])

def indexVarToIndexesTypes(self, indexVar):
    indexesTypes = [self.vars_types_types.index(tp) \
                    for tp in self.vars_types_types \
                    if indexVar in typeToIndexesVars(self,tp)]
    return indexesTypes

def indexesVarsToIndexesTypes(self, indexesVars):
    indexesTypes = []
    for v in indexesVars:
        indexesTypes += indexVarToIndexesTypes(self,v)

    indexesTypes = sorted(list(set(indexesTypes)))
    return indexesTypes

def indexesVarsToDictTypesIndexesVars(self,
                                      indexesVars, indexesVarsTypes):
    types = defaultdict(list)
    #On met dans le dictionnaire des types les types dans indexesVarsTypes
    for t in indexesVarsTypes :
        types[self.vars_types_types[t]]=[]

    for v in indexesVars:
        for tp in indexVarToTypes(self,v):
            types[tp].append(v)
    return types

def indexesVarsToDictTypesVars(self, indexesVars):
    types = defaultdict(list)

    for v in indexesVars:
        for tp in indexVarToTypes(self,v):
            types[tp].append(self.vars[v])
    return types

    # indexes des variables pour lesquelles une liset a des valeurs

def lisetToIndexesVars(self, liset, indexesVars):
    indexesVars = [indexesVars[i] for i in range(len(indexesVars)) \
                   if len(liset[i] - set(self.exclus))]
    return indexesVars

def indexTypeToIndexesVars(self, indexType):

    indexesVarsType = [varToIndex(self,self.vars_types_vars[i]) for i in range(len(self.vars_types_vars)) if
                       self.vars_types_data[indexType][i] in self.coches]
    return indexesVarsType

def indexTypeToIndexesNoms(self, indexType):

    indexesNomsType = [nomToIndex(self,self.noms_types_noms[i]) for i in range(len(self.noms_types_noms)) if
                       self.noms_types_data[i][indexType] in self.coches]
    return indexesNomsType

def typeToIndexesVars(self, tp):
    try:
        indexType = self.vars_types_types.index(tp)
    except:
        print("Le type \"" + tp + "\" n'est pas reconnu")
        sys.exit(1)

    indexesVarsType = [varToIndex(self,self.vars_types_vars[i]) for i in range(len(self.vars_types_vars)) if
                       self.vars_types_data[indexType][i] in self.coches]
    return indexesVarsType

def typesToIndexesVars(self, tps):
    indexesVars = []
    for tp in tps:
        indexesVars += typeToIndexesVars(self,tp)
    indexesVars = sorted(list(set(indexesVars)))
    return indexesVars

def typeToVars(self, tp):
    try:
        indexType = self.vars_types_types.index(tp)
    except:
        print("Le type \"" + tp + "\" n'est pas reconnu")
        sys.exit(1)

    varsType = [self.vars_types_vars[i] for i in range(len(self.vars_types_vars)) if
                self.vars_types_data[indexType][i] in self.coches]
    return varsType

def typesToVars(self, tps):
    if not type(tps) == list:
        tps = list(tps)

    indexesVarsTypes = []
    for tp in tps:
        indexesVarsTypes += typeToIndexesVars(self,tp)

    indexesVarsTypes = sorted(list(set(indexesVarsTypes)))
    varsTypes = [self.vars[i] for i in indexesVarsTypes]
    return varsTypes

# retourne la liste des valeurs (avec répétition) d'une édition
# pour une liste d'indexes de variable donnée
def indexesVarsToValsSimple(self, indexNom, indexesVars):
    values = [str(self.data[indexNom][v]) for v in indexesVars]
    return sorted(values)

def indexesVarsToVals(self, indexesNoms, indexesVars):
    values = [str(self.data[n][v]) for v in indexesVars for n in indexesNoms]
    return sorted(values)

def value_augmented(self, value, indexNom, indexVar):
    nom = self.noms[indexNom]
    var = self.vars[indexVar]
    try:
        citation = self.citations[indexNom][indexVar]
    except:
        citation=''
    if str(value).strip() == '':
        value = '-'

    htm = "<a id=\'nbp-" + str(indexNom) + '-' + str(indexVar) + "\' style=\"color:black;cursor:pointer;\" " \
            " title=\"" + html.escape(str(self.vars_defs_dic[self.vars[indexVar]]).replace('\n',' - '))+"\" " \
            " onmouseup=\"click_on_val(event,\'" + html.escape(str(nom).replace("'", "\\'")) + \
          "\',\'" + html.escape(str(var).replace("'", "\\'")) + "\',\'" + \
          html.escape(str(value).replace("'", "\\'")) + "\',\'" + \
          html.escape(str(citation).replace("'", "&#x27;")) + "\',\'" + \
          str(self.instanceName) + "\');\" >" + str(value).replace("'", "&#x27;") + "</a>"

    return htm

def values_augmented(self, indexesVars, indexesNoms):
    """
    :param self:
    :param values: array of values
    :param indexesVars: variables indexes of the values
    :param indexesNoms: names indexes
    :return: array of values with quotations
    """

    valsAugmented = []
    for n in indexesNoms:
        line = []
        for v in indexesVars:
            line.append(self.data_augmented[n][v])
        valsAugmented.append(line)
    return valsAugmented


def valuesToValues_augmented(self, values, indexesVars, indexNom, start=0):
    """
    :param self:
    :param values: list of values
    :param indexesVars:
    :param indexNom:
    :param start: index of first values
    :return: array of values with quotation
    """

    line = []
    line = values[0:start]  # données qui ne sont pas des valeurs de variables
    for v in range(len(indexesVars)):
        if values[v + start]:
            line.append(self.data_augmented[indexNom][indexesVars[v]])
        else:
            line.append('')
    return line


def data_augmented(self):
    data_augmented = []
    for n in range(len(self.noms)):
        line = [value_augmented(self, self.data[n][v], n, v) for v in range(len(self.vars))]
        data_augmented.append(line)
    self.data_augmented = data_augmented
    return data_augmented

# retourne la liste des valeurs (avec répétition) d'une édition
# sur les variables d'un même type
def typeToVals(self, indexNom, tp):
    indexesVarsType = typeToIndexesVars(self,tp)
    values = [str(self.data[indexNom][v]) for v in indexesVarsType]
    return sorted(values)


def indexNomsTypeToIndexesNoms(self, indexType, indexesNoms = []):
    if indexesNoms == [] : indexesNoms = list(range(0, len(self.noms)))
    indexes = [i for i in indexesNoms if
                       self.noms_types_data[indexType][i] in self.coches]
    return indexes


def indexVarsTypeToIndexesVars(self, indexType, indexesVars = []): ##indexType= citation !!!!
    if indexesVars == [] : indexesVars = list(range(0, len(self.vars)))

    indexes = [i for i in indexesVars if
                       self.vars_types_data[indexType][i] in self.coches]
    return indexes


def indexesTypesToIndexesVars(self, indexesVarsTypes):
    types = [self.vars_types_types[i] for i in indexesVarsTypes]
    return typesToIndexesVars(self,types)

##indexes des variables d'un type, parmi une liste d'indexes de variables,
# sur lesquelles deux éditions données
# ont des valeurs définies
def indexesVarsDefiniesConjointesType(self,
                                      indexNom1, indexNom2, tp, indexesVars):
    indexesVarsDef = []
    indexesV = list(set(typeToIndexesVars(self,tp)).intersection(set(indexesVars)))
    for i in indexesV:
        if self.data[indexNom1][i] not in self.exclus and \
                self.data[indexNom2][i] not in self.exclus:
            indexesVarsDef.append(i)

    return indexesVarsDef

##nombre de variables d'un type, parmi une liste d'indexes de variables,
# sur lesquelles deux éditions données
# ont des valeurs définies
def totalVarsDefiniesConjointesType(self,
                                    indexNom1, indexNom2, tp, indexesVars):
    indexesVarsDef = indexesVarsDefiniesConjointesType(self,
        indexNom1, indexNom2, tp, indexesVars)
    return len(indexesVarsDef)


def varsTypesToIndexesTypes(self,
                            varsTypes, varsTypeSauf):
    for tp in varsTypes:
        try:
            v = self.vars_types_types.index(tp)
        except:
            print(color.bold + "The type \"", tp, "\" is not recognized." + color.end)
            sys.exit(1)

    if len(varsTypes) == 0: varsTypes = self.vars_types_types

    indexesVarsTypes = [self.vars_types_types.index(v) for v in varsTypes if v not in varsTypeSauf]
    indexesVarsTypes = sorted(list(set(indexesVarsTypes)))
    return indexesVarsTypes

def varsTypesToIndexesTypesExt(self,
                                varsTypes, varsTypeSauf):
    if varsTypes:
        varsTypes = varsTypesExt(self, varsTypes)
    if varsTypeSauf:
        varsTypeSauf = varsTypesExt(self, varsTypeSauf)
    return varsTypesToIndexesTypes(self, varsTypes, varsTypeSauf)


def nomsTypesToIndexesTypesExt(self,
                                nomsTypes, nomsTypeSauf):
    if nomsTypes:
        nomsTypes = nomsTypesExt(self, nomsTypes)
    if nomsTypeSauf:
        nomsTypeSauf = nomsTypesExt(self, nomsTypeSauf)
    return varsTypesToIndexesTypes(self, nomsTypes, nomsTypeSauf)

def nomsTypesToIndexesTypes(self,
                            nomsTypes, nomsTypeSauf):

    for tp in nomsTypes:
        try:
            v = self.noms_types_types.index(tp)
        except:
            print(color.bold + "The type \"", tp, "\" is not recognized." + color.end)
            sys.exit(1)

    if len(nomsTypes) == 0: nomsTypes = self.noms_types_types

    indexesNomsTypes = [self.noms_types_types.index(v) for v in nomsTypes if v not in nomsTypeSauf]
    indexesNomsTypes = sorted(list(set(indexesNomsTypes)))
    return indexesNomsTypes


# reduit un tableau sur l'ensemble des types au tableau sur
# une liste de types donnés
# il peut y avoir d'autre données au début, start est l'indice du premier type
def reduceLinesByVarsTypes(self, lines, varsTypes, start=0):
    redLines = []
    for line in lines:
        redLine = line[0:start]
        for tp in varsTypes:
            print('line : ', line, ' - indexe du type ',
                  self.vars_types_types.index(tp), ' valeur : ',
                  line[start + self.vars_types_types.index(tp)])
            redLine.append(line[start + self.vars_types_types.index(tp)])
        redLines.append(redLine)
    return redLines



def nomToTypes(self, var):
    tps = [tp for tp in self.noms_types_types if var in typeToNoms(self,tp)]
    return tps

def nomToindexesTypes(self, nom):
    indexesTypes = [self.noms_types_types.index(tp) \
                    for tp in self.noms_types_types \
                    if var in typeToNoms(self,tp)]
    return indexesTypes

# types d'un nom
def show_name_types(self, nom):
    if not nom in self.noms:
        nom=nomsExtUnique(self, nom)
    types = nomToTypes(self,nom)
    typesL = [[tp] for tp in types]

    display(pd.DataFrame(typesL, columns=[var]))

# noms d'un type donné
def show_names_type(self, tp):
    nomsT = typeToNoms(self,tp)
    print('Names : ' + str(len(nomsT)))
    display(pd.DataFrame(columns=[tp + ':'] + nomsT))

def indexNomToTypes(self, indexNom):
    return nomToTypes(self,self.noms[indexNom])

def indexNomToIndexesTypes(self, indexNom):
    indexesTypes = [self.noms_types_types.index(tp) \
                    for tp in self.noms_types_types \
                    if indexNom in typeToIndexesNoms(self,tp)]
    return indexesTypes

def indexesNomsToIndexesTypes(self, indexesNoms):
    indexesTypes = []
    for v in indexesNoms:
        indexesTypes += self.indexNomToIndexesTypes(v)

    indexesTypes = sorted(list(set(indexesTypes)))
    return indexesTypes

def indexesNomsToDictTypesIndexesNoms(self,
                                      indexesNoms, indexesNomsTypes):
    types = defaultdict(list)

    for v in indexesNoms:
        for tp in self.indexNomToTypes(v):
            types[tp].append(v)
    return types

def indexesNomsToDictTypesNoms(self, indexesNoms):
    types = defaultdict(list)

    for v in indexesNoms:
        for tp in self.indexNomToTypes(v):
            types[tp].append(self.noms[v])
    return types

    # indexes des variables pour lesquelles une liset a des valeurs

def lisetToIndexesNoms(self, liset, indexesNoms):
    indexesNoms = [indexesNoms[i] for i in range(len(indexesNoms)) \
                   if len(liset[i] - set(self.exclus))]
    return indexesNoms

def typeToIndexesNoms(self, tp):
    try:
        indexType = self.noms_types_types.index(tp)
    except:
        print("Le type \"" + tp + "\" n'est pas reconnu")
        sys.exit(1)
    for i in range(len(self.noms_types_noms)):
        indexesNomsType = [nomToIndex(self,(self.noms_types_noms[i])) for i in
                           range(len(self.noms_types_noms)) if
                           self.noms_types_data[i][indexType] in self.coches]
    return indexesNomsType

def typesToIndexesNoms(self, tps):
    indexesNoms = []
    for tp in tps:
        indexesNoms += typeToIndexesNoms(self,tp)
    indexesNoms = sorted(list(set(indexesNoms)))
    return indexesNoms

def typeToNoms(self, tp):
    try:
        indexType = self.noms_types_types.index(tp)
    except:
        print("Le type \"" + tp + "\" n'est pas reconnu")
        sys.exit(1)

    nomsType = [self.noms_types_noms[i] for i in range(len(self.noms_types_noms)) if
                self.noms_types_data[i][indexType] in self.coches]
    return nomsType

def typesToNoms(self, tps):
    if not type(tps) == list:
        tps = list(tps)

    indexesNomsTypes = []
    for tp in tps:
        indexesNomsTypes += typeToIndexesNoms(self,tp)

    indexesNomsTypes = sorted(list(set(indexesNomsTypes)))
    nomsTypes = [self.noms[i] for i in indexesNomsTypes]
    return nomsTypes

def indexes_noms_type(self, tp):
    try:
        indexType = self.noms_types_types.index(tp)
    except:
        print("Le type \"" + tp + "\" n'est pas reconnu")
        sys.exit(1)

    indexesNomsType = [nomToIndex(self,(self.noms_types_noms[i])) \
                       for i in range(len(self.noms_types_noms)) \
                       if self.noms_types_data[i][indexType] in self.coches]
    return indexesNomsType

def indexesTypesToIndexesNoms(self, indexesNomsTypes):
    types = [self.noms_types_types[i] for i in indexesNomsTypes]
    return typesToIndexesNoms(self,types)

def nomsTypesToIndexesTypes(self,
                            nomsTypes, nomsTypeSauf):

    for tp in nomsTypes:
        try:
            v = self.noms_types_types.index(tp)
        except:
            print(color.bold + "Le type \"", tp, "\" n'est pas reconnu." + color.end)
            sys.exit(1)

    if len(nomsTypes) == 0: nomsTypes = self.noms_types_types

    indexesNomsTypes = [self.noms_types_types.index(v) for v in nomsTypes if v not in nomsTypeSauf]
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
                  self.noms_types_types.index(tp), ' valeur : ',
                  line[start + self.noms_types_types.index(tp)])
            redLine.append(line[start + self.noms_types_types.index(tp)])
        redLines.append(redLine)
    return redLines

def typeToNom(self, tp):
    try:
        indexType = self.noms_types_types.index(tp)
    except:
        print("Le type \"" + tp + "\" n'est pas reconnu")
        sys.exit(1)

    nomsType = [self.noms_types_vars[i] \
                for i in range(len(self.noms_types_noms)) \
                if self.noms_types_data[indexType][i] in self.coches]
    return nomsType

def typesToNoms(self, tps):
    if not type(tps) == list:
        tps = list(tps)

    indexesNomsTypes = []
    for tp in tps:
        indexesNomsTypes += indexes_noms_type(self, tp)

    indexesNomsTypes = sorted(list(set(indexesNomsTypes)))
    nomsTypes = [self.noms[i] for i in indexesNomsTypes]
    return nomsTypes

def nomsTypesToIndexesNomsTypes(self,
                                nomsTypes, nomsTypeSauf):

    if type(nomsTypes) == str:
        try:
            v = self.noms.index(nomsTypes)
        except:
            print(color.bold + "Le type \"", nomsTypes, "\" n'est pas reconnu." + color.end)
            sys.exit(color.bold + "Le type \"", nomsTypes, "\" n'est pas reconnu." + color.end)
        nomsTypes = [nomsTypes]

    if len(nomsTypes) == 0: nomsTypes = self.noms_types_types

    indexesNomsTypes = [self.noms_types_types.index(n) for n in nomsTypes if n not in nomsTypeSauf]
    return indexesNomsTypes

##########################################################################
# extensions par expressions régulières
#########################################################################
# liste des variables vérifiant une liste de regVar
def varsExt(self, regVars):
    return strsExt(regVars,self.vars)


# First variable from regVar list
def varsExtUnique(self, var):
    vars=strsExt([var], self.vars)
    try:
        return vars[0]
    except IndexError:
        print("There is no variable with the reg. expression \"" +var+"\"")

# liste des noms vérifiant une liste de regVar
def nomsExt(self, regNoms):
    return strsExt(regNoms,self.noms)

def nomsExtUnique(self, nom):
    noms=strsExt([nom],self.noms)
    return noms[0]

# liste des types de variables vérifiants une liste de regTypes
def varsTypesExt(self, regTypes):
    try:
        return strsExt(regTypes, self.vars_types_types)
    except:
        return regTypes

# liste des types de variables vérifiants une liste de regTypes
def nomsTypesExt(self, regTypes):
    try:
        return strsExt(regTypes, self.noms_types_types)
    except:
        return regTypes

 # indexes des variables pour lesquelles les valeurs manquent
def manque(self, indexesVars, indexNom):
    return [i for i in indexesVars if self.data[indexNom][i] in self.nuls]


def show_missing(self, indexNom, indexesVars):
    indexesVarsManque = manque(self,indexesVars, indexNom)
    varsManque=[self.vars_augmented[v] for v in indexesVarsManque]

    print('Missing values for '+ self.noms[indexNom] +' : ' + str(len(varsManque)))
    printLines([[self.data_augmented[indexNom][v] for v in indexesVarsManque]],index=[self.noms[indexNom]], columns=varsManque)



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
    neg = [v for v in range(len(self.vars)) if not v in a]
    return sorted(neg)

# Etant donnée une formule propositionnelle sur les types,
# retourne les variables correspondantes
def varsTypesFormulaToIndexesVars(self, f, expr):
    import re
    # suppression des opérateurs unaires
    pat = "|".join(["\s*\\" + op + '\s*' for op in self.logicalOperatorsUnary])
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
    pat2 = "|".join(["\s*\\" + op + '\s*' for op in self.logicalOperatorsBinary])
    listTypes = re.split(pat2, exprReduite)
    indexesTypes = varsTypesToIndexesTypes(self,listTypes, [])
    # Problème des types qui sont des sous-chaînes d'un type...
    # substitution des types par des symboles : type i -> xi
    numbered_symbols(prefix='x', start=0)
    exprS = expr
    for i in indexesTypes:
        pat = "\s*" + self.vars_types_types[i] + "\s*"
        reg = re.compile(pat)
        exprS = reg.sub('x' + str(i), exprS)
    exprSymb = sympify(exprS)

    if exprSymb.is_Atom:
        return indexTypeToIndexesVars(self,indexesTypes[0])
    else:
        sexpr = srepr(exprSymb)
        sexpr = sexpr.replace('Or(', 'orVarsTypes(self,' + f + ',')
        sexpr = sexpr.replace('And(', 'andVarsTypes(self,' + f + ',')
        sexpr = sexpr.replace('Not(', 'notVarsTypes(self,' + f + ',')

        for i in indexesTypes:
            sexpr = sexpr.replace("Symbol('x" + str(i) + "')", "'" + self.vars_types_types[i] + "'")
        return eval(sexpr)

def varsTypesFormulaToVars(self, f, expr):
    indexesVars = varsTypesFormulaToIndexesVars(self,f, expr)
    vars = [self.vars[i] for i in indexesVars]
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
    neg = [v for v in range(len(self.noms)) if not v in a]
    return sorted(neg)

    # Etant donnée une formule propositionnelle sur les types,
    # retourne les noms correspondants
def nomsTypesFormulaToIndexesNoms(self, f, expr):
    import re
    # suppression des opérateurs unaires
    pat = "|".join(["\s*\\" + op + '\s*' for op in self.logicalOperatorsUnary])
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
    pat2 = "|".join(["\s*\\" + op + '\s*' for op in self.logicalOperatorsBinary])
    listTypes = re.split(pat2, exprReduite)
    indexesTypes = nomsTypesToIndexesTypes(self,listTypes, [])

    # Problème des types qui sont des sous-chaînes d'un type...

    # substitution des types par des symboles : type i -> xi
    numbered_symbols(prefix='x', start=0)
    exprS = expr
    for i in indexesTypes:
        pat = "\s*" + self.noms_types_types[i] + "\s*"
        reg = re.compile(pat)
        exprS = reg.sub('x' + str(i), exprS)
    exprSymb = sympify(exprS)

    if exprSymb.is_Atom:
        return indexTypeToIndexesNoms(self, indexesTypes[0])
    else:
        sexpr = srepr(exprSymb)
        sexpr = sexpr.replace('Or(', 'orVarsTypes(self,' + f + ',')
        sexpr = sexpr.replace('And(', 'andVarsTypes(self,' + f + ',')
        sexpr = sexpr.replace('Not(', 'notNomsTypes(self,' + f + ',')

        for i in indexesTypes:
            sexpr = sexpr.replace("Symbol('x" + str(i) + "')", "'" + self.noms_types_types[i] + "'")

        return eval(sexpr)

def nomsTypesFormulaToNoms(self, f, expr):
    indexesNoms = nomsTypesFormulaToIndexesNoms(self,f, expr)
    noms = [self.noms[i] for i in indexesNoms]
    return noms


# Affiche les variables et leur définition
def show_vars_defs(self,indexesVars):

    print(color.bold + 'Tableau des définitions des variables : ' + color.end)

    headers = [self.vars[i] for i in indexesVars]
    lines=[[self.vars_defs_dic[self.__vars[i]] for i in indexesVars]]
    # display(pd.DataFrame(lines, columns=columns, index=['Définition : ']))
    display(HTML(tabulate.tabulate(lines, headers=headers, stralign='left', colalign='left', tablefmt='html')))




def vars_defs(self, str,indexesVars):
    vars=[self.vars[v] for v in indexesVars  if str in self.vars_defs_dic[self.vars[v]]]
    return vars


def names_defs(self, str, indexesNoms):
    noms=[self.noms[n] for n in indexesNoms if str in self.noms_defs_dic[self.noms[n]]]
    return noms

