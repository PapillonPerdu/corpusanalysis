from .basics import *


def repartitionList(self,
                    indexesVars, indexesNoms, variantes=[]):
    """
    :param self:
    :param indexesVars:
    :param indexesNoms:
    :return: Tableau regroupant les noms ayant les mêmes valeurs sur un ensemble de variable donné

    """

    indexesEditions = [] + indexesNoms
    resultats = []
    # Valeurs des critères ayant des éditions ayant ces valeurs
    while indexesEditions:
        indexEdition = indexesEditions[0]
        resIndexesNoms = indexes_like(self,indexEdition, indexesNoms, indexesVars, 100, variantes=variantes)
        resVals = [reduceVariante(self.data[indexEdition][j],variantes) for j in indexesVars]
        indexesEditions = [i for i in indexesEditions if i not in resIndexesNoms]
        resultats.append([[indexToNom(self,i) for i in resIndexesNoms], resVals])

    return resultats

def show_repartition(self,indexesNoms,indexesVars,
                     variantes=[],
                     replaceValues = [], replaceNames = [], replaceVars = [],
                     decoration=True):
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
    
    listVars = [self.vars_augmented[v] if decoration else replaceValue(self.vars[v],replaceVars) for v in indexesVars]
    partitions = repartitionList(self,indexesVars, indexesNoms,variantes=variantes)
    total = len(indexesNoms)
    res = [[str(round(len(couple[0]) / total * 100))+'%',len(couple[0])]+replaceLine(couple[1],replaceValues) + [", ".join(noms_augmented(self,replaceLine(couple[0], replaceNames)) if decoration else replaceLine(couple[0], replaceNames))] for couple in partitions]
    res = sorted(res, key=itemgetter(1), reverse=True)
    df=pd.DataFrame(res, columns=['%', '#']+listVars + ['noms'])
    print('Names : {}'.format(total))
    print('Variables : {}'.format(len(listVars)))
    display(HTML(df.to_html(escape=False)))

def values_distribution(self, indexesNoms, indexesVars, variantes=[]):
    '''

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
                    :return: list of the values and their effectifs of the selected variables on the selected names.
                    Descendent order by effectif
                    [[[var1 val1, effectif1],[var1 val2,effectif2],...],[[var2 val1, effectif1],[var2 val2,effectif2],...], ...]
                    '''

    valsEffsList=[]

    for v in indexesVars:
            values = []
            effectifs = []
            for n in indexesNoms:
                value = reduceVariante(self.data[n][v], variantes)
                try :
                    index = values.index(value)
                    effectifs[index] += 1
                except ValueError:
                    values.append(value)
                    effectifs.append(1)

            effectifs, values = zip(*sorted(zip(effectifs, values),reverse =  True))
            valsEffs = [[values[i],effectifs[i]] for i in range(len(values))]
            valsEffsList.append(valsEffs)

    return valsEffsList


def values_distribution_pourcent(self, indexesNoms, indexesVars, variantes=[]):
    '''

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
            :return: list of the values and their porcentage of the selected variables on the selected names.
            Descendent order by percent
            [[[var1 val1, %],[var1 val2,%],...],[[var2 val1, %],[var2 val2,%],...], ...]
            '''

    valsEffsList = values_distribution(self, indexesNoms, indexesVars, variantes=variantes)


    for i in range(len(valsEffsList)):
            #valsEffsList[i] = [[vari val1, effectif1],[vari val2,effectif1],...]
            total = 0
            for j in range(len(valsEffsList[i])):
                #valsEffsList[i][j] = [vari valj, effectifj]
                total += valsEffsList[i][j][1]
            for j in range(len(valsEffsList[i])):
                prc = round(100 *   valsEffsList[i][j][1] /total)
                valsEffsList[i][j][1] = prc

    return valsEffsList

def show_popularity(self,indexesNoms,indexesVars, variantes=[]):
    '''

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
    :return: list of the most popular values of the selected variables on the selected names
    '''

    valsPrcList = values_distribution_pourcent(self, indexesNoms, indexesVars, variantes=variantes)

    # valeurs avec le plus fort pourcentage
    valsMax = [valsPrcList[i][0][0] for i in range(len(valsPrcList))]
    prcMax = [valsPrcList[i][0][1] for i in range(len(valsPrcList))]


    prctDiffList = []
    for indexNom in indexesNoms:
        prctDiff=equalVals(self, indexNom, indexesVars, valsMax)
        prctDiff.insert(1,indexNom) #insert indexNom to recover it after sorting the list
        prctDiffList.append(prctDiff)
        prctDiffList.sort(reverse =  True)

    resNoms=['','']
    lines = []
    lines.append(['']+valsMax)
    prcMax=[str(prc)+'%' for prc in prcMax]
    lines.append(['']+prcMax)
    for l in prctDiffList:
        resNoms.append(nom_augmented(self, self.noms[l[1]]))
        prc = str(l[0])
        values = [value_augmented(self, l[2][i], l[1],indexesVars[i]) if l[2][i] !='' else '' for i in range(len(l[2]))  ]
        line = [str(l[0])+'%']+values
        lines.append(line)

    resVars = [var_augmented(self, self.vars[v]) for v in indexesVars]
    printLines(lines, columns=['%']+resVars, index=resNoms)