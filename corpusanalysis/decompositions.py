from .basics import *


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
            prc = self.sumEqualPercent(ListeL, self.data[indexNom], indexesVars)
            if pourcent <= prc <= Pourcent:
                prcs.append(prc)
                decomp.append(indexes)

    return [prcs, decomp]


def show_decomposition(self,
                   nom,
                   nomsBaseIncomplete=[], nomsBaseIncompleteSauf=[],
                   vars=[], varSauf=[],
                   noms=[], nomSauf=[],
                   max=0, pourcent=100, Pourcent=100,
                   varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                   nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
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

    indexNom = nomToIndex(self,nom)
    indexesVars = getIndexesVars(self,vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
    indexesVars = indexesVarsDefiniesNom(self,indexNom, indexesVars)
    indexesNoms = getIndexesNoms(self,noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

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
                prc = listsEqualPercent(self, self.data[indexNom], self.data[i], indexesVars)
                ligne = [prc]
                for j in indexesVars:
                    if self.strEqual(self.data[i][j], self.data[indexNom][j]):
                        ligne.append('')
                    else:
                        ligne.append(self.data[i][j])
                resData.append(ligne)

            resNoms = [self.noms[i] for i in indexesComplet]
            lines = resData
            columns = resVars
            index = [nom_augmented(self,nom)] + noms_augmented(self,resNoms)

            if pasColonne:
                res = repeteIndex(self, pasColonne, lines, index, resNoms)
                lines = res[0]
                index = res[1]

            if pasLigne:
                res = repeteColumns(self, pasLigne, lines, index, resNoms)
                lines = res[0]
                columns = res[1]
            print('')
            print(color.bold + str(prcTotal) + "% : " + ', '.join(resNoms) + color.end)
            df = pd.DataFrame(lines, columns=columns, index=index)
            display(HTML(df.to_html(escape=False)))
    else:
        print('Aucune décomposition.')
