
from .basics import *

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

##################################################################################
# méthodes sur les listes d'ensembles (liset)
##################################################################################"

def liset(L):
   liset = [{i} for i in L]
   return liset
def sum_set(self, indexesNoms, indexesVars):
    res = [set([self.data[n][i] \
                for n in indexesNoms \
                if not self.data[n][i] in self.exclus]) \
           for i in indexesVars]
    return res


def difference_liset(liset1, liset2, indexesVars):
    res = [liset1[i] - liset2[i] for i in range(len(indexesVars))]
    return res


def show_sum_set(self, indexesNoms,indexesVars):

    res = sum_set(self,indexesNoms, indexesVars)
    show_liset(self,res, indexesVars)

def lisetEmpty(liset, indexesVars):
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

    varsL = [indexToVar_augmented(self, v) for v in indexesVars]
    df = pd.DataFrame(lignes[:-1], columns=varsL)
    display(HTML(df.to_html(escape=False)))


def lisetContainsPourcent(self, liset1, liset2, indexesVars, pourcent, Pourcent):
    prc = pourcentLisetContains(self, liset1, liset2, indexesVars)
    return Pourcent >= prc >= pourcent


def pourcentLisetContains(self, liset1, liset2, indexesVars):
    sum = 0
    for i in range(len(indexesVars)):
        if len(liset1[i] - liset2[i]) == 0 and not liset2[i] in self.exclus:
            sum += 1
    prc = 100 * sum / len(indexesVars)

    return prc


def lisetIncludesPourcent(self, ls, l, indexesVars, pourcent, Pourcent):
    prc = pourcentLisetIncludes(self, ls, l, indexesVars)
    return Pourcent >= prc >= pourcent





def pourcentLisetIncludes(self, ls, l, indexesVars):
    sum = 0
    total = 0
    i = 0
    for v in indexesVars:
        if not l[v] in self.exclus:
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
        if not len(ls[i]) == 0 and not ls[i] in self.exclus:
            sum += 1
    prc = 100 * sum / len(indexesVars)

    return prc


def vars_incompletes(self, liset1, liset2, indexesVars):
    varsIncompletes = []
    for i in range(len(indexesVars)):
        if not len(liset1[i] - liset2[i]) == 0 and not liset2[i] in self.exclus:
            varsIncompletes.append(self.vars[indexesVars[i]])

    return varsIncompletes


######################################################################################################
# décomposition
#######################################################################################################

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
            ListeL = [self.data[i] for i in indexes + indexesNomsBaseIncomplete]
            prc = sumEqualPourcent(ListeL, self.data[indexNom], indexesVars)
            if pourcent <= prc <= Pourcent:
                prcs.append(prc)
                decomp.append(indexes)

    return [prcs, decomp]


def show_decomposition(self,
                   nom,indexesNoms,indexesVars,
                   nomsBaseIncomplete=[], nomsBaseIncompleteSauf=[],
                   max=0, pourcent=100, Pourcent=100,
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
    :return: Décomposition des valeurs d'un nom en fonction de celles d'autres noms
    """

    indexNom = nomToIndex(self, nom)

    if nomsBaseIncomplete or nomsBaseIncompleteSauf:
        indexesNomsBaseIncomplete = nomsToIndexesNoms(self,nomsBaseIncomplete, nomsBaseIncompleteSauf)
    else:
        indexesNomsBaseIncomplete = []

    if indexNom in indexesNoms: indexesNoms.remove(indexNom)

    if max == 0:
        max = 4
        print("Le nombre de termes d'une décomposition a été limité à 4.")

    resDecomp = decomposition(self,indexNom,
                                   indexesNomsBaseIncomplete,
                                   indexesVars,
                                   indexesNoms,
                                   max,
                                   pourcent,
                                   Pourcent)
    prcs = resDecomp[0]
    decomp = resDecomp[1]

    resVars = ['%'] + [self.vars_augmented[i] for i in indexesVars]
    print('Variables : ' + str(len(resVars)))

    if not len(decomp) == 0:
        for i in range(len(decomp)):
            indexes = decomp[i]
            prcTotal = prcs[i]
            ligne = [100] + [self.data[indexNom][j] for j in indexesVars]
            resData = [ligne]
            # Ajout des indexes des noms de la base incomplète
            indexesComplet = sorted(indexesNomsBaseIncomplete + indexes)
            for i in indexesComplet:
                prc = listsEqualPourcent(self.data[indexNom], self.data[i], indexesVars)
                ligne = [prc]
                for j in indexesVars:
                    if equal(self.data[i][j], self.data[indexNom][j]):
                        ligne.append('')
                    else:
                        ligne.append(self.data[i][j])
                resData.append(ligne)

            resNoms = [self.noms[i] for i in indexesComplet]
            lines = resData
            columns = resVars
            index = [nom_augmented(self,nom)] + noms_augmented(self,resNoms)
            print('')
            print(color.bold + str(prcTotal) + "% : " + ', '.join(resNoms) + color.end)
            printLines(lines, columns=columns, index=index, pasColonne=pasColonne,pasLigne=pasLigne)
    else:
        print('Aucune décomposition.')


#########################################################################################################"


def noms_base_complete(self,indexesNoms,indexesVars,  nomsGenerateurs=[], nomsGenerateurSauf=[], nomsBaseIncomplete=[],
                       pourcent=100, Pourcent=100, max=0):

    indexesNomsGenerateurs = nomsToIndexesNoms(self,nomsGenerateurs, nomsGenerateurSauf)
    if nomsBaseIncomplete:
        indexesNomsBaseIncomplete = nomsToIndexesNoms(self,nomsBaseIncomplete, [])
    else:
        indexesNomsBaseIncomplete = []

    indexesNomsReste = list(set(indexesNoms) - set(indexesNomsBaseIncomplete))

    lisetComplet = sum_set(self, indexesNomsGenerateurs, indexesVars)

    if not max: max = len(indexesNoms)

    decomp = []
    res = []

    for indexes in tqdm(sorted(getCombinations(indexesNomsReste,
                                               max - len(indexesNomsBaseIncomplete)), key=len)):

        if not includes(indexes, decomp):
            # print('indexes : ',indexesNoms)
            liset = sum_set(self, indexes + indexesNomsBaseIncomplete, indexesVars)
            # print(liset)
            if lisetContainsPourcent(self,lisetComplet, liset, indexesVars, pourcent, Pourcent):
                dec = sorted(indexesNomsBaseIncomplete + indexes)
                varsIncompletes = vars_incompletes(self,lisetComplet, liset, indexesVars)
                decomp.append(dec)
                res.append([dec, varsIncompletes])

    return res


def show_noms_base_complete(self,indexesNoms,indexesVars, nomsGenerateurs=[], nomsGenerateurSauf=[],
                            nomsBaseIncomplete=[],
                            pourcent=100, Pourcent=100, max=0):

    indexesNomsGenerateurs = nomsToIndexesNoms(self,
        nomsGenerateurs,
        nomsGenerateurSauf)

    lisetComplet = sum_set(self, indexesNomsGenerateurs, indexesVars)

    if not max: max = len(indexesNoms)
    nomsG = [self.noms[i] for i in indexesNomsGenerateurs]
    print(color.bold + 'Tableau complet :' + color.end)
    print('  Générateurs :')
    if len(indexesNomsGenerateurs) == len(self.noms):
        print('  Tous')
    else:
        print('  ' + ', '.join(nomsG))
    print('  Variables : ' + str(len(indexesVars)))
    show_liset(self, lisetComplet, indexesVars)

    resultats = noms_base_complete(self,indexesNoms,indexesVars,nomsGenerateurs=nomsGenerateurs, nomsGenerateurSauf=nomsGenerateurSauf, \
                                        nomsBaseIncomplete=nomsBaseIncomplete,
                                        pourcent=pourcent, Pourcent=Pourcent, max=max)

    if not resultats:
        print(color.bold + 'Aucun résultat' + color.end)
    for res in resultats:
        indexes = res[0]
        noms = [self.noms[i] for i in indexes]
        lisetDiff = difference_liset(lisetComplet, self.sum_set(indexes, indexesVars), indexesVars)
        prc = round(100 - pourcentLiset(lisetDiff, indexesVars))
        print(color.bold + str(prc) + '% - ' + str(len(indexes)) + ' : ' + ', '.join(noms) + color.end)
        if prc < 100:
            self.show_liset(lisetDiff, indexesVars)
        print(' ')


def show_values(self, indexesNoms,indexesVars):

    lisetComplet = sum_set(self,indexesNoms, indexesVars)

    nomsG = [self.noms[i] for i in indexesNoms]
    print(color.bold + 'Tableau complet :' + color.end)
    print('  Générateurs :')
    if len(indexesNoms) == len(self.noms):
        print('  Tous')
    else:
        print('  ' + ', '.join(nomsG))
    show_liset(self, lisetComplet, indexesVars)


def noms_inclus(self, indexesNomsGenerateurs, indexesVars,
                lisetComplet,
                pourcent=100, Pourcent=100):
    res = []
    for n in indexesNoms:
        if lisetIncludesPourcent(self, lisetComplet,
                                      self.data[n],
                                      indexesVars,
                                      pourcent, Pourcent):
            res.append(n)

    return res



def show_noms_inclus(self, indexesNoms, indexesVars, nomsGenerateurs=[], nomsGenerateurSauf=[],
                     pourcent=0, Pourcent=100):

    indexesNomsGenerateurs = nomsToIndexesNoms(self,nomsGenerateurs, nomsGenerateurSauf)

    lisetComplet = sum_set(self, indexesNomsGenerateurs, indexesVars)
    nomsG = [self.noms[i] for i in indexesNomsGenerateurs]
    print(color.bold + 'Tableau complet :' + color.end)
    print('  Générateurs :')
    if len(indexesNomsGenerateurs) == len(self.noms):
        print('  Tous')
    else:
        print('  ' + ', '.join(nomsG))

    show_liset(self, lisetComplet, indexesVars)

    indexesNomsInclude = noms_inclus(self,
                                    indexesNomsGenerateurs, indexesVars, indexesNoms,
                                    lisetComplet,
                                    pourcent=pourcent, Pourcent=Pourcent)

    if indexesNomsInclude:
        for n in indexesNomsInclude:
            l = list(self.data[n])
            prc = round(pourcentLisetIncludes(self,lisetComplet, l, indexesVars))
            print('')
            print(color.bold + self.noms[n] + ' : ' + str(prc) + '%' + color.end)
            if not prc == 100:
                l = [l[v] for v in indexesVars]
                lisetDiff = difference_liset(liset(l), lisetComplet, indexesVars)
                show_liset(self, lisetDiff, indexesVars)
    else:
        print(color.bold + 'Aucun résultat' + color.end)


# Comme précédemment, mais les résultats sont donnés par types
def show_noms_inclus_types(self, indexesNoms, indexesVars,indexesVarsTypeSortie, nomsGenerateurs=[], nomsGenerateurSauf=[],
                           pourcent=0, Pourcent=100,
                           effectif=0, Effectif=0,
                           varsTypeSortie=[], varsTypeSortieSauf=[]):

    indexesNomsGenerateurs = nomsToIndexesNoms(self,nomsGenerateurs, nomsGenerateurSauf)

    if varsTypeSortie or varsTypeSortieSauf:
        indexesVarsTypeSortie = varsTypesToIndexesTypes(self,varsTypeSortie, varsTypeSortieSauf)
    else:
        indexesVarsTypeSortie = indexesVars

    varsTypeSortie = [self.vars_types_types[tp] for tp in indexesVarsTypeSortie]

    lisetComplet = sum_set(self, indexesNomsGenerateurs, indexesVars)
    nomsG = [self.noms[i] for i in indexesNomsGenerateurs]
    print(color.bold + 'Tableau complet :' + color.end)
    print('  Générateurs :')
    if len(indexesNomsGenerateurs) == len(self.noms):
        print('  Tous')
    else:
        print('  ' + ', '.join(nomsG))

    show_liset(self, lisetComplet, indexesVars)

    indexesNomsInclude = noms_inclus(self,
        indexesNomsGenerateurs, indexesVars, indexesNoms,
        lisetComplet,
        pourcent=pourcent, Pourcent=Pourcent)

    if indexesNomsInclude:
        print("Les nombres donnés sont les nombres de variables du type dont les valeurs manquent.")
        for n in indexesNomsInclude:
            lines = []
            l = list(self.data[n])
            prc = round(pourcentLisetIncludes(self,lisetComplet, l, indexesVars))
            print('')
            print(color.bold + self.noms[n] + ' : ' + str(prc) + '%' + color.end)
            if not prc == 100:
                # inutile d'afficher la différence si 100% des valeurs sont les mêmes
                l = [l[v] for v in indexesVars]
                lisetDiff = difference_liset(liset(l), lisetComplet, indexesVars)
                # indexes des variables où il y a une différence
                indexesVarsDiff = lisetToIndexesVars(self,lisetDiff, indexesVars)
                collTypes = indexesVarsToDictTypesIndexesVars(self,
                    indexesVarsDiff,
                    indexesVarsTypeSortie)
                effectifs = effectifsTypes(self,[n], indexesVars, indexesVarsTypeSortie)

                if effectif or Effectif:
                    # restriction de indexesVarsTypesSortie
                    if Effectif == 0: Effectif = len(self.vars)
                    indexesVarsTypeSortie = [indexesVarsTypeSortie[i] \
                                             for i in range(len(indexesVarsTypeSortie)) \
                                             if Effectif >= effectifs[i + 1] >= effectif]
                    varsTypeSortie = [self.vars_types_types[i] for i in indexesVarsTypeSortie]
                    total = effectifs[0]
                    effectifs.pop(0)
                    effectifs = [e for e in effectifs if Effectif >= e >= effectif]
                    effectifs.insert(0, total)
                # première ligne avec l'effectif total et pour chaque type
                lines.append(effectifs)
                line = []
                for indexTp in indexesVarsTypeSortie:
                    try:
                        tp = self.vars_types_types[indexTp]
                        val = len(collTypes[tp])
                        if val == 0: val = ''
                        line.append(val)
                    except:
                        line.append('')

                line = [collTotal(self,collTypes)] + line
                lines.append(line)

                columns = ['total'] + varsTypeSortie
                index = ['Effectif', self.noms_augmented[n]]
                printLines(lines, columns=columns, index=index)

    else:
        print(color.bold + 'Aucun résultat' + color.end)


# Comme précédemment, mais les résultats sont donnés par types et en pourcentage
def show_noms_inclus_types_pourcent(self,indexesNoms, indexesVars, indexesVarsTypeSortie,
                                    nomsGenerateurs=[], nomsGenerateurSauf=[],
                                    pourcent=0, Pourcent=100,
                                    effectif=0, Effectif=0):

    indexesNomsGenerateurs = nomsToIndexesNoms(self,nomsGenerateurs, nomsGenerateurSauf)

    lisetComplet = sum_set(self,indexesNomsGenerateurs, indexesVars)
    nomsG = [self.noms[i] for i in indexesNomsGenerateurs]
    print(color.bold + 'Tableau complet :' + color.end)
    print('  Générateurs :')
    if len(indexesNomsGenerateurs) == len(self.noms):
        print('  Tous')
    else:
        print('  ' + ', '.join(nomsG))

    show_liset(self,lisetComplet, indexesVars)

    indexesNomsInclude = noms_inclus(self,
        indexesNomsGenerateurs, indexesVars, indexesNoms,
        lisetComplet,
        pourcent=pourcent, Pourcent=Pourcent)

    if indexesNomsInclude:
        print("Les nombres donnés sont les pourcentages de variables du type dont les valeurs manquent.")
        for n in indexesNomsInclude:
            lines = []
            l = list(self.data[n])
            prc = round(pourcentLisetIncludes(self,lisetComplet, l, indexesVars))
            print('')
            print(color.bold + self.noms[n] + ' : ' + str(prc) + '%' + color.end)
            if not prc == 100:
                # inutile d'afficher la différence si 100% des valeurs sont les mêmes
                l = [l[v] for v in indexesVars]
                lisetDiff = difference_liset(liset(l), lisetComplet, indexesVars)
                # indexes des variables où il y a une différence
                indexesVarsDiff = lisetToIndexesVars(self,lisetDiff, indexesVars)
                collTypes = indexesVarsToDictTypesIndexesVars(self,
                    indexesVarsDiff,
                    indexesVarsTypeSortie)

                effectifs = effectifsTypes(self,[n], indexesVars, indexesVarsTypeSortie)

                if effectif or Effectif:
                    # restriction de indexesVarsTypesSortie
                    if Effectif == 0: Effectif = len(self.vars)
                    indexesVarsTypeSortie = [indexesVarsTypeSortie[i] \
                                             for i in range(len(indexesVarsTypeSortie)) \
                                             if Effectif >= effectifs[i + 1] >= effectif]
                    varsTypeSortie = [self.vars_types_types[i] for i in indexesVarsTypeSortie]
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
                        tp = self.vars_types_types[indexTp]
                        val = len(collTypes[tp])
                        prc = round(val / totalType * 100)
                    except:
                        prc = 0
                    if prc:
                        line.append(str(prc) + '%')
                    else:
                        line.append('')

                line = [collTotal(self,collTypes)] + line
                lines.append(line)

                columns = ['total'] + varsTypeSortie
                index = ['Effectif', self.noms_augmented[n]]
                printLines(lines, columns=columns, index=index)
    else:
        print(color.bold + 'Aucun résultat' + color.end)


# retourne les (indexes des) éditions dans l'image d'une liste
# de valeurs de variables d'une liste d'éditions
def noms_image(self, indexesVars, indexesNoms):
    res = []
    for n in indexesNoms:
        nomsImage = indexes_like(self,n, indexesNoms, indexesVars, 100)
        if nomsImage == [n]:
            res.append(n)
    return res


def vars_base(self,indexesNoms,indexesVars, varsBaseIncomplete=[],
              max=0):
    if not varsBaseIncomplete == []:
        indexesVarsBaseIncomplete = varsToIndexesVars(self,varsBaseIncomplete, [])
    else:
        indexesVarsBaseIncomplete = []

    indexesVarsReste = list(set(indexesVars) - set(indexesVarsBaseIncomplete))
    res = []

    if not max: max = len(indexesVars)

    for indexes in tqdm(sorted(getCombinations(indexesVarsReste,
                                               max - len(indexesVarsBaseIncomplete)),
                               key=len)):
        if not includes(indexes, res):
            if noms_image(self, indexes + indexesVarsBaseIncomplete, indexesNoms) == indexesNoms:
                res.append(sorted(list(set(indexes + indexesVarsBaseIncomplete))))
    return res


def vars_base_first(self, indexesNoms, indexesVars,varsBaseIncomplete=[],
                    max=0):

    if not varsBaseIncomplete == []:
        indexesVarsBaseIncomplete = varsToIndexesVars(self,varsBaseIncomplete, [])
    else:
        indexesVarsBaseIncomplete = []

    indexesVarsReste = list(set(indexesVars) - set(indexesVarsBaseIncomplete))

    if not max: max = len(indexesVars)
    res = ''

    for indexes in tqdm(sorted(getCombinations(indexesVarsReste,
                                               max - len(indexesVarsBaseIncomplete)),
                               key=len)):
        if noms_image(self, indexes + indexesVarsBaseIncomplete, indexesNoms) == indexesNoms:
            res = sorted(list(set(indexes + indexesVarsBaseIncomplete)))
            break
    return res


def show_vars_base_first(self,indexesNoms,indexesVars, varsBaseIncomplete=[],
                         max=0):

    indexes = vars_base_first(self,indexesNoms,indexesVars, varsBaseIncomplete=varsBaseIncomplete,
                                   max=max)

    if indexes:
        varsBase = [self.vars[i] for i in indexes]
        print(color.bold + ', '.join(varsBase) + color.end)
        for n in indexesNoms:
            nom = self.noms[n]
            show_data(self, nom, vars=varsBase)
    else:
        print(color.bold + 'Aucun résultat' + color.end)


def show_vars_base(self,indexesNoms,indexesVars, varsBaseIncomplete=[],
                   max=0):
    indexesVarsBase = vars_base(self,indexesNoms,indexesVars,varsBaseIncomplete=varsBaseIncomplete,
                                     max=max)

    if indexesVarsBase:
        for indexes in indexesVarsBase:
            varsBase = [self.vars[i] for i in indexes]
            print(color.bold + ', '.join(varsBase) + color.end)
            for n in indexesNoms:
                nom = self.noms[n]
                self.show_data(nom, vars=varsBase)
            print('------------------------------------')
    else:
        print(color.bold + 'Aucun résultat' + color.end)
