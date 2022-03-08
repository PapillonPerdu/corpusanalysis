from operator import itemgetter
import matplotlib.pyplot as plt


from .basics import *
from .innove import *
from .types import *

try:
    from tqdm.notebook import tqdm
except:
    print("Le module tqdm.notebook n'a pu être importé.")
    print("Les fonctions sushoivantes ne seront pas utilisables : ")
    print("     decomposition")
    print("     noms_base_complete")
    print("     vars_base")
    print("     vars_base_first")

def communs(self,
            indexNom1, indexNom2, indexesVars):
    """

    :param self:
    :param indexNom1:
    :param indexNom2:
    :param indexesVars:
    :return: liste des valeurs définies de premier nom, contenues dans celles de deuxième nom, parmi des variables, donnés par leurs indexes.
    """
    comp = []
    for v in indexesVars:
        if not self.data[indexNom1][v] in self.exclus and \
                not self.data[indexNom2][v] in self.exclus and \
                equal(self.data[indexNom1][v], self.data[indexNom2][v]):
            comp.append(self.data[indexNom2][v])
        else:
            comp.append('')

    return comp

def communsStrict(self,
                  indexNom1, indexNom2, indexesVars):
    """

        :param self:
        :param indexNom1:
        :param indexNom2:
        :param indexesVars:
        :return: liste des valeurs définies de premier nom, contenues dans celles de deuxième nom, parmi des variables, donnés par leurs indexes.
        """
    comp = []
    for k in indexesVars:
        if not self.data[indexNom1][k] in self.exclus and \
                not self.data[indexNom2][k] in self.exclus and \
                equalStrict(self.data[indexNom1][k], self.data[indexNom2][k]):
            comp.append(self.data[indexNom2][k])
        else:
            comp.append('')

    return comp

def difference(self,
               indexNom1, indexNom2, indexesVars):
    """

        :param self:
        :param indexNom1:
        :param indexNom2:
        :param indexesVars:
        :return: liste des valeurs définies de premier nom,
        différentes de celles de deuxième nom, parmi des variables, donnés par leurs indexes.
        """
    diff = []
    for k in indexesVars:
        if not self.data[indexNom1][k] in self.exclus and \
                not self.data[indexNom2][k] in self.exclus and \
                not equal(self.data[indexNom1][k], self.data[indexNom2][k]):
            diff.append(self.data_augmented[indexNom1][k])
        else:
            diff.append('')

    return diff

def differenceStrict(self,
                     indexNom1, indexNom2, indexesVars):
    """

        :param self:
        :param indexNom1:
        :param indexNom2:
        :param indexesVars:
        :return: liste des valeurs de nom1, strictement différentes de celles de nom2, parmi des variables, donnés par leurs indexes.
        """
    diff = []
    for k in indexesVars:
        if not self.data[indexNom1][k] in self.exclus and \
                not self.data[indexNom2][k] in self.exclus and \
                not equalStrict(self.data[indexNom1][k], self.data[indexNom2][k]):
            diff.append(self.data_augmented[indexNom1][k])
        else:
            diff.append('')

    return diff


# List of variables on which two texts are different
def vars_difference(self,indexNom1,indexNom2,indexesVars):

    diff = differenceStrict(self,indexNom1, indexNom2, indexesVars)
    indexVars_diff = sorted([indexesVars[i] for i in range(len(indexesVars)) if not diff[i] in self.nuls])

    return indexVars_diff

def show_difference(self,
                    nom1, nom2,indexesVars):
    indexNom1 = nomToIndex(self,nom1)
    indexNom2 = nomToIndex(self,nom2)

    diff = [differenceStrict(self,indexNom1, indexNom2, indexesVars),
            difference(self,indexNom2, indexNom1, indexesVars)]

    diff =  valuesToValues_augmented(self, diff, indexesVars,[indexNom1,indexNom2])

    # ligne avec les critères
    varsL = [indexToVar_augmented(self,v) for v in indexesVars]
    nomsL = [nom_augmented(self,nom1), nom_augmented(self,nom2)]
    df=pd.DataFrame(diff, columns=varsL, index=nomsL)
    display(HTML(df.to_html(escape=False)))


def show_difference(self,
                    indexNom1, indexNom2, indexesVars):
    diff = [self.differenceStrict(indexNom1, indexNom2, indexesVars),
            self.difference(indexNom2, indexNom1, indexesVars)]

    # ligne avec les critères
    varsL = [self.indexToVar_and_def(v) for v in indexesVars]
    nomsL = [self.nomToNom_and_def(self.noms[indexNom1]), self.nomToNom_and_def(self.noms[indexNom2])]

    printLines(diff, columns=varsL, index=nomsL)


def show_difference_types(self,
                          indexNom1, indexNom2, indexesVars,
                          indexesVarsTypeSortie,
                          effectifType=0, EffectifType=0,
                          pourcenType=0, PourcenType=100):

    indexesVarsDifference = indexesVarsDifferenceStrict(self,indexNom1, indexNom2,
                                                             indexesVars)

    collTypes = indexesVarsToDictTypesIndexesVars(self,indexesVarsDifference, indexesVarsTypeSortie)

    lines = []

    indexesTypesDifferenceComplet = sorted([t for t in indexesVarsTypeSortie
                                            if self.vars_types_types[t] in collTypes])
    typesDifferenceComplet = [self.vars_types_types[i] for i in indexesTypesDifferenceComplet]
    effectifs = effectifsTypes(self,[indexNom1, indexNom2], indexesVars, indexesTypesDifferenceComplet)

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
    total = collTotal(self,collTypes)
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


def vars_commun(self,indexNom1,indexNom2,indexesVars):
    com = communsStrict(self,indexNom1, indexNom2, indexesVars)
    vars_com = [indexToVar(self,indexesVars[i]) for i in range(len(indexesVars)) if not com[i] in self.nuls]
    return vars_com


# Liste des indexes de variables sur lesquelles deux éditions diffèrent
def indexes_vars_commun(self,
                        indexNom1, indexNom2, indexesVars):

    com = communsStrict(self,indexNom1, indexNom2, indexesVars)
    indexesVars_com = [indexesVars[i] for i in range(len(indexesVars)) if not com[i] == '']
    return indexesVars_com

# indexes des variables pour lesquelles deux éditions ont les mêmes valeurs
def indexesVarsCommunStrict(self,
                            indexNom1, indexNom2, indexesVars):
    com = []
    for k in indexesVars:
        if not self.data[indexNom1][k] in self.exclus and \
                not self.data[indexNom2][k] in self.exclus and \
                equalStrict(self.data[indexNom1][k], self.data[indexNom2][k]):
            com.append(k)

    return com

# indexes des variables pour lesquelles deux éditions ont des valeurs différentes
def indexesVarsDifferenceStrict(self,
                                indexNom1, indexNom2, indexesVars):
    diff = []
    for k in indexesVars:
        if not equalStrict(self.data[indexNom1][k], self.data[indexNom2][k]):
            diff.append(k)

    return diff


def show_commun(self, indexNom1, indexNom2, indexesVars):
    com = [self.communsStrict(indexNom1, indexNom2, indexesVars)]

    # ligne avec les critères
    varsL = [self.indexToVar_and_def(v) for v in indexesVars]
    nomsL = [self.nomToNom_and_def(self.noms[indexNom1]) + '/' + self.nomToNom_and_def(self.noms[indexeNom2])]
    printLines(com, columns=varsL, index=nomsL)

# valeurs communes d'une édition avec d'autres éditions,
# en précisant le pourcentage d'éditions ayant cette valeur
# l'idée est de récupérer ainsi les variables "rares" communes à deux éditions
def show_noms_commun_pourcent(self,
                              indexNom,indexesNoms,indexesVars,
                              pourcent=0, Pourcent=100,
                              pasColonne=10, pasLigne=10):

    linesNoms = [[] for n in indexesNoms]
    totalNoms = [0 for n in indexesNoms]
    resVars = []

    pourcents = []
    totaux = []
    for v in indexesVars:
        indexesNomsCommun = indexes_like(self,indexNom, indexesNoms, [v], 100)
        indexesNomsCommun.remove(indexNom)
        total = len(indexesNomsCommun)
        prc = round(100 * total / len(indexesNoms))
        if Pourcent >= prc > pourcent:
            resVars.append(self.vars_augmented[v])
            for n in indexesNoms:
                if n in indexesNomsCommun:
                    linesNoms[n].append(self.data[n][v])
                    totalNoms[n] += 1
                else:
                    linesNoms[n].append('')

            totaux.append(total)
            pourcents.append(prc)

    lines = []
    resNoms = []
    for n in indexesNoms:
        if totalNoms[n]:
            total = totalNotNull(self,linesNoms[n])
            lines.append([total] + linesNoms[n])
            resNoms.append(self.noms_augmented[n])
    lines.append([''] + totaux)
    lines.append([''] + pourcents)

    columns = ['Total'] + resVars
    index = resNoms + ['total', '%']

    printLines(lines, columns=columns, index=index,pasColonne=pasColonne,pasLigne=pasLigne)

def show_commun_types(self,
                      indexNom1,indexNom2,indexesVars,
                      indexesVarsTypeSortie,
                      effectifType=0, EffectifType=0,
                      pourcenType=0, PourcenType=100):

    indexesVarsCommun = indexesVarsCommunStrict(self,indexNom1, indexNom2,indexesVars)

    collTypes = indexesVarsToDictTypesIndexesVars(self,
        indexesVarsCommun,
        indexesVarsTypeSortie)

    lines = []

    indexesTypesCommunComplet = sorted([t for t in indexesVarsTypeSortie \
                                        if self.vars_types_types[t] in collTypes])
    typesCommunComplet = [self.vars_types_types[i] for i in indexesTypesCommunComplet]
    effectifs = effectifsTypes(self,[indexNom1, indexNom2], indexesVars, indexesTypesCommunComplet)

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

    line0 = []
    line1 = []
    line2 = []
    line3 = []
    total = collTotal(self,collTypes)
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
    print(color.bold + self.noms[indexNom1] + '/' +self.noms[indexNom2] + color.end)
    printLines(lines,columns=['Total'] + typesReduits,
                         index=['Effectifs', 'communs', '%communs', '%type'])

    # Retourne la somme et la somme pondérée

# vals contient la liste des valeurs des variables.
def stats(self,
          vals, indexesVars):
    sum = 0
    total = 0
    sumPond = 0
    for k in range(len(vals)):
        pds = self.poids[redindexVarToIndex(self,k, indexesVars)] if self.poidsExist else 1
        if pds != 0:
            total += 1
            if vals[k] != '':
                sum += 1
                pds = self.poids[redindexVarToIndex(self,k, indexesVars)] if self.poidsExist else 1
                sumPond += pds
    try:
        return [int(round(100 * sumPond / total)), sum]
    except:
        return [0, sum]

        # Tableau descendant des corrélations

def tableau_correlations(self,
                              indexNom, indexesVars, indexesNoms,
                              pourcent, Pourcent):

    # liste des corrélations, avec le nom au début et le total à la fin
    cor = []
    for k in indexesNoms:
        if not k == indexNom:
            l = communs(self, indexNom, k, indexesVars)
            # ajouts des stats en début de liste
            total = totalPondereVarsDefiniesConjointes(self,
                indexNom, k, indexesVars)
            totalCommun = totalNotNull(self,l)
            try:
                prc = round(100 * totalCommun / total)
            except:
                prc = 0
            l = [prc, total, totalCommun] + l
            l.insert(0, self.noms[k])
            if int(Pourcent) >= int(l[1]) >= int(pourcent):
                cor.append(l)

    cor_sorted = sorted(cor, key=itemgetter(1), reverse=True)

    return cor_sorted


def tableau_correlations(self,
                              indexNom, indexesNoms, indexesVars, dir,
                              pourcent, Pourcent):

    # liste des corrélations descendantes, avec le nom au début et le total à la fin
    cor = []
    for k in indexesNoms:
        if (k < indexNom and dir == 'asc') or (k > indexNom and dir == 'desc') or (not k == indexNom and dir =='both'):
            l = communs(self,indexNom, k, indexesVars)
            # ajouts des stats en début de liste
            total = totalPondereVarsDefiniesConjointes(self,
                indexNom, k, indexesVars)
            totalCommun = totalNotNull(self,l)
            try:
                prc = round(100 * totalCommun / total)
            except:
                prc = 0
            l = [prc, total, totalCommun] + l
            l.insert(0, self.noms[k])
            if int(Pourcent) >= int(l[1]) >= int(pourcent):
                cor.append(l)

    cor_sorted = sorted(cor, key=itemgetter(1), reverse=True)

    return cor_sorted


def show_discrimine(self,
                    indexNom, discrimines, indexesVars,
                    pasColonne=10):
    # variables sur lesquelles les deux éditions diffèrent
    # parmi celle où le nom a des valeurs égales à l'une ou l'autre

    varsDiff = vars_difference(self,discrimines[0], discrimines[1],
                               vars_somme_relative(self,indexNom,discrimines,indexesVars))
    #varsDiff = list(set(varsDiff1) & set(varsDiff2))
    indexesVars = list (set(indexesVars) & set(varsDiff))
    indexesVarsInnove=vars_innove(self, [indexNom],indexesVars, 'asc')
    indexesVars = sorted(list(set(indexesVars) - set(indexesVarsInnove)))

    show_correlations(self, indexNom, discrimines, indexesVars,dir='both',pasColonne = pasColonne)



def show_correlations_resa(self,
                                  indexNom,indexesNoms,indexesVars,
                                   pourcent=0, Pourcent=100,effectif = 0, Effectif = 0,
                                   pasColonne=10, pasLigne=10):


    cor = tableau_correlations(self, indexNom, indexesVars, indexesNoms, pourcent, Pourcent)
    # première ligne avec les poids
    # poidsL=['poids : ']+self.__selectedPoids

    if Effectif == 0: Effectif = len(self.vars)

    # deuxième ligne avec les critères
    varsL = ['%', 'effectif', 'communs'] + [indexToVar_augmented(self, v) for v in indexesVars]
    nomsL = []
    corData = []
    for L in cor:
        if Effectif >= L[2] >= effectif :
            nomsL.append(nom_augmented(self, L[0]))
            del L[0]
            corData.append(L)

    print(color.bold + 'Correlations of ' + self.noms[indexNom] + color.end)
    print('Names : ' + str(len(nomsL)))
    print('Variables : ' + str(len(varsL) - 3))
    printLines(corData, columns=varsL, index=nomsL)

def show_correlations(self,
                                  indexNom, indexesNoms,indexesVars, dir='asc',
                                   pourcent=0, Pourcent=100,effectif = 0, Effectif = 0,
                                   pasColonne=10, pasLigne=10):


    cor = tableau_correlations(self,indexNom, indexesNoms, indexesVars, dir, pourcent, Pourcent)
    # première ligne avec les poids
    # poidsL=['poids : ']+self.selectedPoids

    if Effectif == 0: Effectif = len(self.vars)

    # deuxième ligne avec les critères
    varsL = ['%', 'effectif', 'communs'] + [self.vars_augmented[v] for v in indexesVars]
    nomsL = []
    corData = []
    for L in cor:
        if int(Effectif) >= int(L[2]) >= int(effectif) :
            nm=L[0]
            nomsL.append(self.noms_augmented[self.noms.index(nm)])
            del L[0]
            corData.append(valuesToValues_augmented(self,L,indexesVars,self.noms.index(nm),start=3))

    print(color.bold +  'Correlations '+ dir +' of ' + self.noms[indexNom] + color.end)
    print('Names : ' + str(len(nomsL)))
    print('Variables : ' + str(len(varsL) - 3))
    printLines(corData, columns=varsL, index=nomsL)

def show_correlations_desc(self,
                                  indexNom, indexesNoms,indexesVars,
                                   pourcent=0, Pourcent=100,effectif = 0, Effectif = 0,
                                   pasColonne=10, pasLigne=10):


    corDes = tableau_correlations_desc(self,indexNom, indexesNoms, indexesVars, pourcent, Pourcent)
    # première ligne avec les poids
    # poidsL=['poids : ']+self.selectedPoids

    if Effectif == 0: Effectif = len(self.vars)

    # deuxième ligne avec les critères
    varsL = ['%', 'effectif', 'communs'] + [self.vars_augmented[v] for v in indexesVars]
    nomsL = []
    corDesData = []
    for L in corDes:
        if Effectif >= L[2] >= effectif :
            nm=L[0]
            nomsL.append(self.noms_augmented[self.noms.index(nm)])
            del L[0]
            corDesData.append(valuesToValues_augmented(self,L,indexesVars,self.noms.index(nm),start=3))

    print(color.bold +  'Desc. correlations of ' + self.noms[indexNom] + color.end)
    print('Names : ' + str(len(nomsL)))
    print('Variables : ' + str(len(varsL) - 3))
    printLines(corDesData, columns=varsL, index=nomsL)

def show_correlations_asc(self,
                                  indexNom,indexesNoms, indexesVars,
                                  pourcent=0, Pourcent=100, effectif = 0, Effectif = 0,
                                  pasColonne=10, pasLigne=10):
    if Effectif == 0: Effectif = len(self.vars)

    corAsc = tableau_correlations_asc(self,indexNom, indexesNoms,indexesVars, pourcent, Pourcent)

    # deuxième ligne avec les critères
    varsL = ['%', 'effectif', 'communs'] + [self.vars_augmented[v] for v in indexesVars]
    nomsL = []
    corAscData = []
    for L in corAsc:
        if Effectif >= L[2] >= effectif :
            nm=L[0]
            nomsL.append(self.noms_augmented[self.noms.index(nm)])
            del L[0]
            corAscData.append(valuesToValues_augmented(self,L,indexesVars,self.noms.index(nm),start=3))

    columns = varsL
    index = nomsL


    print(color.bold +  'Asc. correlations of ' + self.noms[indexNom] + color.end)
    print('Names : ' + str(len(nomsL)))
    print('Variables : ' + str(len(varsL) - 3))
    printLines(corAscData, columns=columns, index=index)



# Tableau ascendant et des descendant des corrélations dans fichier csv "nomCor.csv"
def save_correlations(self,indexNom,indexesNoms,indexesVars,
                              pourcent=0, Pourcent=100):

    # liste des corrélations ascendantes, avec le nom au début et le total à la fin
    corAsc = tableau_correlations_asc(self,indexNom, indexesVars, indexesNoms, pourcent, Pourcent)
    corDes = tableau_correlations_desc(self,indexNom, indexesVars, indexesNoms, pourcent, Pourcent)

    filename = nom + self.baseName + 'Cor.csv'
    with open(filename, 'w',encoding="UTF-8") as file:
        wr = csv.writer(file, quotiinng=csv.QUOTE_ALL)

        for line in corAsc:
            wr.writerow(line)

        # première ligne avec les poids
        poidsL = ['poids : ', '', ''] + [self.poids[i] for i in indexesVars]
        wr.writerow(poidsL)

        # deuxième ligne avec les critères
        varsL = ['nom', '%', 'total'] + [self.vars[v] for v in indexesVars]
        wr.writerow(varsL)

        for line in corDes:
            wr.writerow(line)

def save_tableaux_correlations(self,indexNom,indexesNoms,indexesVar):
    for n in indexesNoms:
        nom = self.noms[n]
        print(nom)
        save_tableau_correlations(self,indexNom,indexesVars,indexesVars)

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
            vars_com = indexes_vars_commun(self,indexNom, k, indexesVars)
            # print('communs : ',self.noms[indexNom],'-',self.noms[k],' : ', vars_com)
            vars_com = list(set(vars_com).intersection(set(indexesVars)))
            collTypes = indexesVarsToDictTypesIndexesVars(self,vars_com,
                                                               indexesVarsTypes)
            line = []
            for indexTp in indexesVarsTypeSortie:
                try:
                    tp = self.vars_types_types[indexTp]
                    val = len(collTypes[tp])
                    if val == 0: val = ''
                    line.append(val)
                except:
                    line.append('')
            line = [self.noms[k], collTotal(self,collTypes)] + line
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
            vars_com = indexes_vars_commun(self,indexNom, k, indexesVars)
            vars_com = list(set(vars_com).intersection(set(indexesVars)))
            collTypes = indexesVarsToDictTypesIndexesVars(self,vars_com, indexesVarsTypes)
            line = []
            for indexTp in indexesVarsTypeSortie:
                try:
                    tp = self.vars_types_types[indexTp]
                    val = len(collTypes[tp])
                    if val == 0: val = ''
                    line.append(val)
                except:
                    line.append('')
            line = [self.noms[k], collTotal(self,collTypes)] + line
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
            vars_com = indexes_vars_commun(self,indexNom, k, indexesVars)
            # print('communs : ',self.noms[indexNom],'-',self.noms[k],' : ', vars_com)
            vars_com = list(set(vars_com).intersection(set(indexesVars)))
            collTypes = indexesVarsToDictTypesIndexesVars(self,
                vars_com, indexesVarsTypeSortie)
            line = []

            for indexTp in indexesVarsTypeSortie:
                try:
                    tp = self.vars_types_types[indexTp]
                    val = len(collTypes[tp])
                    total = totalVarsDefiniesConjointesType(self,indexNom, k, tp, indexesVars)
                    prc = round(val / total * 100)
                    if prc:
                        line.append(prc)
                    else:
                        line.append('')
                except:
                    line.append('')
            try:
                Total = totalVarsDefiniesConjointes(self,indexNom, k, indexesVars)
                prc = round(len(vars_com) / Total * 100)
            except:
                prc = 0

            if Pourcent >= prc >= pourcent:
                line = [self.noms[k], prc] + line
                corDes.append(line)

    corDes_sorted = sorted(corDes, key=itemgetter(1), reverse=True)

    return corDes_sorted

def tableau_correlations_types_pourcent_asc(self,
                                            indexNom, indexesNoms, indexesVars,
                                            indexesVarsTypeSortie,
                                            pourcent, Pourcent):

    # dict des corrélations descendantes par types de variables,
    # avec le nom  et le total au début
    corAsc = []
    for k in tqdm(indexesNoms):
        if k > indexNom:
            vars_com = indexes_vars_commun(self,indexNom, k, indexesVars)
            vars_com = list(set(vars_com).intersection(set(indexesVars)))
            collTypes = indexesVarsToDictTypesIndexesVars(self,
                vars_com, indexesVarsTypeSortie)
            line = []


            for indexTp in indexesVarsTypeSortie:
                try:
                    tp = self.vars_types_types[indexTp]
                    val = len(collTypes[tp])
                    total = totalVarsDefiniesConjointesType(self,indexNom, k, tp, indexesVars)
                    prc = round(val / total * 100)
                    if prc:
                        line.append(prc)
                    else:
                        line.append('')
                except:
                    line.append('')
            try:
                Total = totalVarsDefiniesConjointes(self,indexNom, k, indexesVars)
                prc = round(len(vars_com) / Total * 100)
            except:
                prc = 0

            if Pourcent >= prc >= pourcent:
                line = [self.noms[k], prc] + line
                corAsc.append(line)

    corAsc_sorted = sorted(corAsc, key=itemgetter(1), reverse=True)

    return corAsc_sorted

def show_correlations_types_desc(self,
                                 indexNom, indexesNoms, indexesVars,
                                 pourcent=0, Pourcent=100,
                                 effectifType=0, EffectifType=0,
                                 varsTypeSortie=[], varsTypeSortieSauf=[],
                                 pasColonne=10, pasLigne=10):


    indexesVarsTypes = varsTypesToIndexesTypes(self,varsTypes, varsTypeSauf)

    set_selectedIndexesVars(self,indexesVars)
    set_selectedIndexesNoms(self,indexesNoms)

    effectifs = effectifsTypesNom(self,indexNom, indexesVars, indexesVarsTypeSortie)

    if effectifType or EffectifType:
        # restriction de indexesVarsTypes
        if EffectifType == 0: EffectifType = len(self.vars)
        indexesVarsTypes = [indexesVarsTypes[i] \
                            for i in range(len(indexesVarsTypeSortie)) \
                            if EffectifType >= effectifs[i + 1] >= effectifType]
        effectifs = [e for e in effectifs if EffectifType >= e >= effectifType]

    corDes = tableau_correlations_types_desc(self,indexNom, indexesVars, indexesNoms, \
                                                  indexesVarsTypes, indexesVarsTypeSortie,
                                                  pourcent, Pourcent)

    varsTypeSortie = [self.vars_types_types[tp] for tp in indexesVarsTypeSortie]

    nomsL = []
    corDesData = []

    # première ligne avec l'effectif total et pour chaque type
    corDesData.append(effectifs)
    for L in corDes:
        nomsL.append(nom_augmented(self,L[0]))
        del L[0]
        corDesData.append(L)

    columns = ['total'] + varsTypeSortie
    index = ['Effectifs'] + nomsL

    print('Types : ' + str(len(varsTypeSortie)))

    printLines(corDesData, columns=columns, index=index)

#Fonction pour discriminer les corrélations d'une édition à deux autres suivant les types
def show_discrimine_types(self,
                          nom, discrimines,indexesVars,indexesVarsTypeSortie,
                          pasColonne=10):
    varsDiff = vars_difference(self,discrimines[0], discrimines[1])
    indexesVars = list (set(indexesVars) & set(varsDiff))
    indexesVars = list(set(indexesVars) - vars_innove(self,nom))

    show_correlations_types_desc(self,
        nom, discrimines,indexesVars,
        indexesVarsTypeSortie,
        pasColonne = pasColonne)


def show_correlations_types_asc(self,
                                       indexNom,indexesNoms,indexesVars,indexesVarsTypes,indexesVarsTypeSortie,
                                        pourcent=0, Pourcent=100,
                                        effectifType=0, EffectifType=0,
                                         pasColonne=10, pasLigne=10):

    set_selectedIndexesNoms(self,indexesNoms)

    effectifs = effectifsTypesNom(self,indexNom, indexesVars, indexesVarsTypeSortie)

    if effectifType or EffectifType:
        # restriction de indexesVarsTypes
        if EffectifType == 0: EffectifType = len(self.vars)
        indexesVarsTypes = [indexesVarsTypes[i] \
                            for i in range(len(indexesVarsTypeSortie)) \
                            if EffectifType >= effectifs[i + 1] >= effectifType]
        effectifs = [e for e in effectifs if EffectifType >= e >= effectifType]

    corAsc = tableau_correlations_types_asc(self,indexNom, indexesVars, indexesNoms,
                                                 indexesVarsTypes, indexesVarsTypeSortie,
                                                 pourcent, Pourcent)

    varsTypeSortie = [self.vars_types_types[tp] for tp in indexesVarsTypeSortie]
    corAscData = []

    # première ligne avec l'effectif total et pour chaque type
    corAscData.append(effectifs)
    nomsL=[]
    for L in corAsc:
        nomsL.append(nom_augmented(self,L[0]))
        del L[0]
        corAscData.append(L)

    columns = ['total'] + varsTypeSortie
    index = ['Effectifs'] + nomsL

    print('Types : ' + str(len(varsTypeSortie)))

    printLines(corAscData, columns=columns, index=index,pasColonne=pasColonne, pasLigne=pasLigne)

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
                [totalVarsDefiniesType(self,indexesNoms, indexesVars, self.vars_types_types[tp]) for tp in
                 indexesVarsTypes]
    return effectifs

def show_correlations_types_pourcent_desc(self,
                                                indexNom,indexesNoms,indexesVars,indexesVarsTypeSortie,
                                                  pourcent=0, Pourcent=100,
                                                  pourcenType=0,PourcenType=100,
                                                  effectif=0, Effectif=0,
                                                  pasColonne=10, pasLigne=10):

    set_selectedIndexesVars(self,indexesVars)
    set_selectedIndexesNoms(self,indexesNoms)

    effectifs = effectifsTypesNom(self,indexNom, indexesVars, indexesVarsTypeSortie)
    if effectif or Effectif:
        # restriction de indexesVarsTypes
        if Effectif == 0: Effectif = len(self.vars)
        indexesVarsTypeSortie = [indexesVarsTypeSortie[i] \
                                 for i in range(len(indexesVarsTypeSortie)) \
                                 if Effectif >= effectifs[i + 1] >= effectif]
        effectifs = [e for e in effectifs if Effectif >= e >= effectif]

    corDes = tableau_correlations_types_pourcent_desc(self,
        indexNom, indexesVars, indexesNoms,
        indexesVarsTypeSortie,
        pourcent, Pourcent)

    varsTypeSortie = [self.vars_types_types[tp] for tp in indexesVarsTypeSortie]

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
        nomsL.append(nom_augmented(self,L[0]))
        del L[0]
        corDesData.append(L)

    columns = ['% total'] + varsTypeSortie
    index = ['Effectifs'] + nomsL
    lines = corDesData

    printLines(lines, columns=columns, index=index)


# Fonction pour discriminer les corrélations d'une édition à deux autres
# suivant les types, exprimés en pourcentages
def show_discrimine_types_pourcent(self,
                                   indexNom, discrimines,indexesVars,indexesVarsTypeSortie,
                                   pasColonne=10):
    varsDiff = vars_difference(self,discrimines[0], discrimines[1])
    indexesVars = list(set(indexesVars) & set(varsDiff))

    show_correlations_types_pourcent_desc(self,
        indexNom, discrimines,indexesVars,indexesVarsTypeSortie,
        pasColonne=pasColonne)

def show_correlations_types_pourcent_asc(self,
                                                 indexNom,indexesNoms,indexesVars,indexesVarsTypeSortie,
                                                 pourcent=0, Pourcent=100,
                                                 pourcenType=0, PourcenType=100,
                                                 effectif=0, Effectif=0,
                                                 pasColonne=10, pasLigne=10):

    set_selectedIndexesVars(self,indexesVars)
    set_selectedIndexesNoms(self,indexesNoms)

    effectifs = effectifsTypesNom(self,indexNom, indexesVars, indexesVarsTypeSortie)
    if effectif or Effectif:
        # restriction de indexesVarsTypes
        if Effectif == 0: Effectif = len(self.vars)
        indexesVarsTypeSortie = [indexesVarsTypeSortie[i] \
                                 for i in range(len(indexesVarsTypeSortie)) \
                                 if Effectif >= effectifs[i + 1] >= effectif]
        effectifs = [e for e in effectifs if Effectif >= e >= effectif]

    corAsc = tableau_correlations_types_pourcent_asc(self,
        indexNom, indexesVars, indexesNoms,
        indexesVarsTypeSortie,
        pourcent, Pourcent)

    varsTypeSortie = [self.vars_types_types[tp] for tp in indexesVarsTypeSortie]
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
        nomsL.append(nom_augmented(self,L[0]))
        del L[0]
        corAscData.append(L)

    columns = ['% total'] + varsTypeSortie
    index = ['Effectifs'] + nomsL
    lines = corAscData

    printLines(lines, columns=columns, index=index, pasColonne=pasColonne,pasLigne=pasLigne)

def plot_intervalles(self,indexNom1,indexNom2,indexesVars, longueur,
                     pas=1, elev=0, azim=0):

    indexMax = len(indexesVars)
    L1 = self.data[indexNom1]
    L2 = self.data[indexNom2]

    def fun(xList, yList, L1, L2, indexesVars):
        res = [listsEqualPourcent(L1, L2, indexesVars[x:y + 1]) for x, y in zip(xList, yList)]

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



