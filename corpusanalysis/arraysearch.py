from operator import itemgetter

from .basics import *
from .correlations import *


def findVarsIndexes(self,
                    cars, indexesVars):
    if type(cars) == list:
        indexes = []
        for c in cars:
            indexes = indexes + findVarsIndexes(self,c, indexesVars)

        indexes = sorted(list(set(indexes)))
        return indexes


    else:
        indexes = [v for v in indexesVars if
                   str(cars).lower() in str(self.vars[v]).lower()]
        return indexes


def findVars(self,
             cars, indexesVars):
    indexes = findVarsIndexes(self,cars, indexesVars)
    listVars = [self.vars[i] for i in indexes]
    return listVars


def findNomsIndexes(self,
                    cars, indexesNoms):
    if type(cars) == list:
        indexes = []
        for c in cars:
            indexes = indexes + findNomsIndexes(self,c, indexesNoms)

        indexes = sorted(list(set(indexes)))
        return indexes


    else:
        indexes = [v for v in indexesNoms if
                   str(cars).lower() in str(self.noms[v]).lower()]
        return indexes


def findNoms(self,
             cars, noms=[], nomSauf=[]):
    indexesNoms = self.nomsToIndexesNoms(noms, nomSauf)

    indexes = findNomsIndexes(self,cars, indexesNoms)
    listNoms = [self.noms[i] for i in indexes]
    return listNoms


# Recherche les variables ayant une valeur donnée d'une édition
def findVarsValue(self,
                  indexNom, cars,indexesVars):

    listVars = [self.vars[i] for i in indexesVars if str(cars).lower() in str(self.data[indexNom][i]).lower()]
    return listVars


# indexes des noms pour lesquels les variables données ont une valeur donnée
# varsValues=[['nomVar1','valVar1'],['nomVar2','valVar2']]
def indexesNomsVarsValues(self, varsValues, indexesNoms, variantes=[]):
    resIndexesNoms = []
    for n in indexesNoms:
        boole = false
        for i in range(len(varsValues)):
            if equal(self.data[n, varToIndex(self,varsValues[i][0])], varsValues[i][1],variantes):
                boole = true
                break
        if boole:
            resIndexesNoms.append(n)
    return resIndexesNoms


def namesVarsValues(self, indexesNoms, varsValues=[],variantes=[]):
    """List of names with a given value on given variables varsValues=[[var1,value1],[var2,value2], etc.]."""
    for vv in varsValues:
        if not len(vv) == 2:
            print(color.bold + "varsValues doit être une liste de ['vars', 'valeur']." + color.end)
            sys.exit(1)
    resNoms = indexesNomsVarsValues(self,varsValues, indexesNoms,variantes=variantes)
    return [self.noms[i] for i in resNoms]


# indexes des noms pour lesquels les variables données contiennent une valeur donnée
def indexesNomsVarsContientValues(self,indexesNoms,
                                  varsValues=[], variantes=[]):

    resIndexesNoms = []
    for n in indexesNoms:
        boole = true
        for i in range(len(varsValues)):
            if not reduceVariante(varsValues[i][1],variantes) in reduceVariante(self.data[n, varToIndex(self,varsValues[i][0])],variantes):
                boole = false
                break
        if boole:
            resIndexesNoms.append(n)
    return resIndexesNoms


# noms pour lesquels les variables données ont une valeur donnée
def namesVarsContainsValues(self, indexesNoms,
                            varsValues, variantes=[]):
    indexesNoms = indexesNomsVarsContientValues(self,indexesNoms,varsValues=varsValues, variantes=variantes)
    return [self.noms[i] for i in indexesNoms]


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
    if type(listVars) == int: listVars = [indexToVar(self,listVars)]

    for var in listVars:
        print(color.bold + var.replace('\n', ' ') + " : " + color.end)
        res = [self.noms[i] for i in self.selectedIndexesNoms if self.data[i][varToIndex(self,var)] == val]
        print(res)
        print()


# Liste des indexes des éditions ayant les mêmes valeurs qu'une édition donnée, à un pourcentage près,
# sur un domaine de variables donné
def indexes_like(self,
                 indexNom, indexesNoms, indexesVars, pourcent):
    # print(color.bold+str(self.__vars[start-1]).replace('\n',' ')+ ", précision "+str(pourcent)+"% : "+color.end)

    indexesNomsRes = [i for i in indexesNoms if \
                      listsEqual(self,self.data[indexNom], self.data[i], indexesVars, pourcent)]

    return indexesNomsRes



def contains(self,chain, indexesNoms,indexesVars):
    resData = []
    resNoms = []
    for i in indexesNoms:
        l = []
        ok = False
        for v in indexesVars:
            if str(chain).lower() in \
                    str(self.data[i][v]).replace('[', '').replace(']', '').lower():
                l.append(self.data[i][v])
                ok = True
            else:
                l.append('')
        if ok:
            resData.append(l)
            resNoms.append(self.noms_augmented[i])

    resVars = [self.vars_augmented[i] for i in indexesVars]
    df=pd.DataFrame(resData, columns=resVars, index=resNoms)

    return display(HTML(df.to_html(escape=False)))
