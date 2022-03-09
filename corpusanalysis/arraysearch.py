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
             cars, vars=[], varSauf=[]):
    if vars == []: vars = self.vars
    indexesVars = varsToIndexesVars(self,vars, varSauf)
    indexes = findVarsIndexes(self,cars, indexesVars)
    print(indexes)
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
def indexesNomsVarsValues(self, varsValues, indexesNoms):
    resIndexesNoms = []
    for n in indexesNoms:
        boole = false
        for i in range(len(varsValues)):
            if self.data[n, varToIndex(self,varsValues[i][0])] == varsValues[i][1]:
                boole = true
                break
        if boole:
            resIndexesNoms.append(n)
    return resIndexesNoms


# noms pour lesquels les variables données ont une valeur donnée
def nomsVarsValues(self,indexesNoms, varsValues=[]):
    for vv in varsValues:
        if not len(vv) == 2:
            print(color.bold + "varsValues doit être une liste de ['vars', 'valeur']." + color.end)
            sys.exit(1)
    resNoms = indexesNomsVarsValues(self,varsValues, indexesNoms)
    return [self.noms[i] for i in resNoms]


# indexes des noms pour lesquels les variables données contiennent une valeur donnée
def indexesNomsVarsContientValues(self,indexesNoms,
                                  varsValues=[]):

    resIndexesNoms = []
    for n in indexesNoms:
        boole = true
        for i in range(len(varsValues)):
            if not varsValues[i][1] in self.data[n, varToIndex(self,varsValues[i][0])]:
                boole = false
                break
        if boole:
            resIndexesNoms.append(n)
    return resIndexesNoms


# noms pour lesquels les variables données ont une valeur donnée
def nomsVarsContientValues(self,indexesNoms,
                           varsValues):
    indexesNoms = indexesNomsVarsContientValues(self,indexesNoms,varsValues=varsValues)
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


# Recherche les éditions ayant les mêmes valeurs qu'une édition donnée, à un pourcentage près,
# sur un domaine de variables donné par leur nom
def show_like(self,
              nom, noms=[], nomSauf=[],
              vars=[], varSauf=[],
              varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
              nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
              pourcent=0):

    try:
        indexNom = self.noms.index(nom)
    except:
        print(color.bold + "Le nom \"" + nom + "\" ne fait pas partie des noms reconnus." + color.end)
        sys.exit(1)

    indexesVars = getIndexesVars(self,vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
    indexesVars = indexesVarsDefiniesNom(self,indexNom, indexesVars)

    indexesNoms = getIndexesNoms(self,noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

    indexesNomsRes = indexes_like(self,indexNom, indexesNoms, indexesVars, pourcent)

    resNomsLignes = [
        [self.noms[i]] + stats(self,communs(self,indexNom, i, indexesVars), indexesVars) + [self.data[i][k] for
                                                                                              k in indexesVars] for
        i in indexesNomsRes]
    resNomsLignes = sorted(resNomsLignes, key=itemgetter(1), reverse=True)
    resNoms = []
    resLignes = []
    for L in resNomsLignes:
        resNoms.append(nom_augmented(self,L[0]))
        del L[0]
        resLignes.append(L)

    resVars = ['%', 'total\ncommuns'] + [self.vars_augmented[i] for i in indexesVars]

    df=pd.DataFrame(resLignes, columns=resVars, index=resNoms)
    display(HTML(df.to_html(escape=False)))


def contains(self,
             chain, vars=[], varSauf=[],
             noms=[], nomSauf=[],
             varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
             nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule=''):

    indexesVars = getIndexesVars(self,vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
    indexesNoms = getIndexesNoms(self,noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

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
