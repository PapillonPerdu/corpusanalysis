from .basics import *

try:
    from tqdm.notebook import tqdm
except:
    print("Le module tqdm.notebook n'a pu être importé.")
    print("Les fonctions suivantes ne seront pas utilisables : ")
    print("     decomposition")
    print("     noms_base_complete")
    print("     vars_base")
    print("     vars_base_first")



def indexesVars_data_pourcent(self,indexNom,indexesNoms,indexesVars,
                       pourcent=0, Pourcent=100):


    indexesVars = indexesVarsDefiniesNom(self,indexNom, indexesVars)

    if indexNom in indexesNoms: indexesNoms.remove(indexNom)

    resVars = []

    for v in indexesVars:
        exclus = self.exclus
        if not self.data[indexNom][v] in exclus:
            total = len(indexes_like(self,indexNom, indexesNoms, [v], 100))
            try:
                prc = round(100 * total / len(indexesNoms))
            except:
                break
            if Pourcent >= prc >= pourcent:
                resVars.append(v)

    return resVars

def vars_data_pourcent(self,indexNom,indexesNoms,indexesVars,
                       pourcent=0, Pourcent=100):

    return indexesToVars(indexesVars_data_pourcent(self,indexNom,indexesNoms,indexesVars,
                       pourcent=pourcent, Pourcent=Pourcent))

def show_data_pourcent(self,indexNom,indexesNoms,indexesVars,
                       pourcent=0, Pourcent=100,
                       pasColonne=10, pasLigne=10):

    indexesVars = indexesVarsDefiniesNom(self,indexNom, indexesVars)

    if indexNom in indexesNoms: indexesNoms.remove(indexNom)

    resVals = []
    resVars = []

    pourcents = []
    totaux = []
    for v in indexesVars:
        total = len(indexes_like(self,indexNom, indexesNoms, [v], 100))
        prc = round(100 * total / len(indexesNoms))
        if Pourcent >= prc >= pourcent:
            resVars.append(self.vars_augmented[v])
            resVals.append(self.data[indexNom][v])
            totaux.append(total)
            pourcents.append(prc)

    lines = [resVals, totaux, pourcents]
    columns = resVars
    index = [nom_augmented(self,nom), 'total', '%']

    printLines(lines, columns=columns, index=index,pasColonne=pasColonne,pasLigne=pasLigne)


def indexeNoms_data_pourcent(self,indexNom,indexesNoms,indexesVars,
                       pourcent=0, Pourcent=100):

    indexesVars = indexesVarsDefiniesNom(self,indexNom, indexesVars)

    if indexNom in indexesNoms: indexesNoms.remove(indexNom)

    resVals = []
    resNoms = []

    for v in indexesVars:
        total = len(indexes_like(self,indexNom, indexesNoms, [v], 100))
        prc = round(100 * total / len(indexesNoms))
        if Pourcent >= prc >= pourcent:
            for n in indexesNoms:
                if equal(self.data[n][v], self.data[indexNom][v]):
                    resNoms.append(n)

    return list(set(resNoms))

def noms_data_pourcent(self,indexNom,indexesNoms,indexesVars,
                       pourcent=0, Pourcent=100):

    return indexesToNoms(indexesNoms_data_pourcent(self,indexNom,indexesNoms,indexesVars,
                       pourcent=pourcent, Pourcent=Pourcent))

def show_noms_data_pourcent(self,indexNom,indexesNoms,indexesVars,
                            pourcent=0, Pourcent=100,
                            pasColonne='10', pasLigne='10',
                            ):
    indexesNomSel = indexesNoms_data_pourcent(self,indexNom,indexesNoms,indexesVars,
                                              pourcent=pourcent,Pourcent=Pourcent)
    indexesVarSel = indexesVars_data_pourcent(self,indexNom,indexesNoms,indexesVars,
                                              pourcent=pourcent, Pourcent=Pourcent)
    show_data(self,[indexNom]+indexesNomSel,indexesVarSel,pasColonne=pasColonne,pasLigne=pasLigne)


def vars_only(self,indexNom,indexesNoms,indexesVars):
    return indexesVars_data_pourcent(self,indexNom,indexesNoms,indexesVars,
        Pourcent=0)


def show_data_only(self,indexNom,indexesNoms,indexesVars):

    varsO = vars_only(self,indexNom,indexesNoms,indexesVars)
    if varsO:
        show_data(self,[indexNom], indexesVarsO)
    else:
        print('Aucun résultat')

def vars_innove(self,indexesNoms,indexesVars,dir):
    varsInnove = []
    for n in indexesNoms:
        if dir == 'asc':
            indexesNoms = list(range(0, n))
        else:
            indexesNoms = list(range(n, len(self.noms)))
        varsInnove += vars_only(self,n, indexesNoms, indexesVars)

    indexesVarsInnove = sorted(list(set(varsInnove)))
    return indexesVarsInnove


def show_vars_innove(self,indexesNoms,indexesVars, dir):
    show_vars(self,vars_innove(self,indexesNoms, indexesVars, dir))

def show_innove(self,indexesNoms,indexesVars, dir,
                    pasColonne=10, pasLigne=10):
    indexesVarsInnove = []
    indexesVarsInnoveComplet = []
    for indexNom in indexesNoms:
        indexesVarsIn = vars_innove(self,[indexNom],indexesVars,dir)
        indexesVarsInnove.append(indexesVarsIn)
        indexesVarsInnoveComplet += indexesVarsIn

    indexesVarsInnoveComplet = sorted(list(set(indexesVarsInnoveComplet)))
    lines = []
    for n in range(len(indexesNoms)):
        try:
            prc = round(len(indexesVarsInnove[n]) / totalVarsNom(self,indexesNoms[n], indexesVars) * 100)
        except:
            prc = '0'
        indexNom=indexesNoms[n]
        line = [prc]
        for v in indexesVarsInnoveComplet:
            if v in indexesVarsInnove[n]:
                line.append(self.data_augmented[indexNom][v])
            else:
                line.append('')
        lines.append(line)

    varsInnoveComplet = [indexToVar_augmented(self,v) for v in indexesVarsInnoveComplet]

    columns = ['%'] + varsInnoveComplet
    index = [self.noms_augmented[n] for n in indexesNoms]
    print("Variables : " + str(len(indexesVars)))
    printLines(lines, columns=columns, index=index,  pasColonne=pasColonne, pasLigne=pasLigne)




def show_noms_commun_pourcent(self, indexNom, indexesNoms,indexesVars,
                              pourcent=0, Pourcent=100,
                              pasColonne=10, pasLigne=10):
    """
     Tableau des valeurs communes d'un nom avec d'autres noms, en précisant le pourcentage de noms ayant cette valeur.
     L'idée est de récupérer ainsi les variables "rares" communes à deux noms.
    """



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

    printLines(lines, columns=columns, index=index,pasColonne=pasColonne, pasLigne=pasLigne)



def show_innove_types(self,indexesNoms,indexesVars,indexesVarsTypeSortie,dir,
                          effectifType=0, EffectifType=0,
                          pasColonne=10, pasLigne=10):

    # typesRetenus = [tp for tp in varsTypes if not tp in varsTypeSauf]

    # indexesNomsDonnes = sorted(self.nomsToIndexesNoms(nomsDonnes, []))
    dictNomsIndexesVarsInnove = defaultdict(list)
    indexesVarsInnoveComplet = []
    for indexNom in tqdm(indexesNoms):
        indexesVarsIn = vars_innove(self,[indexNom], indexesVars,dir)
        dictNomsIndexesVarsInnove[indexNom] = indexesVarsIn
        indexesVarsInnoveComplet += indexesVarsIn

    indexesVarsInnoveComplet = sorted(list(set(indexesVarsInnoveComplet)))

    collTypes = indexesVarsToDictTypesIndexesVars(self,
        indexesVarsInnoveComplet,
        indexesVarsTypeSortie)

    lines = []
    indexesTypesInnoveComplet = sorted([t for t in indexesVarsTypeSortie \
                                        if self.vars_types_types[t] in collTypes])

    typesInnoveComplet = [self.vars_types_types[i] for i in indexesTypesInnoveComplet]

    effectifsListe = effectifsTypes(self,indexesNoms, indexesVars, indexesTypesInnoveComplet)

    if effectifType or EffectifType:
        # restriction de indexesVarsTypes
        if EffectifType == 0: EffectifType = len(self.vars)
        indexesTypesInnoveComplet = [indexesTypesInnoveComplet[i] \
                                     for i in range(len(indexesTypesInnoveComplet)) \
                                     if EffectifType >= effectifs[i + 1] >= effectifType]
        typesInnoveComplet = [self.vars_types_types[i] for i in indexesTypesInnoveComplet]
        effectifsListe = [e for e in effectifsListe if EffectifType >= e >= effectifType]
    if not effectifsListe:
        print('Aucun résultat.')
    else:
        # première ligne avec l'effectif total et pour chaque type
        lines.append(effectifsListe)
        totalVars = len(indexesVars)
        for indexNom in indexesNoms:
            line = []
            totalNom = len(set(dictNomsIndexesVarsInnove[indexNom]). \
                           intersection(set(indexesVarsInnoveComplet)). \
                           intersection(set(indexesVars)))
            # total = len(set(dictNomsIndexesVarsInnove[nom]).intersection(set(indexesVars)))
            line.append(totalNom)
            for tp in typesInnoveComplet:
                communs = list(set(dictNomsIndexesVarsInnove[indexNom]). \
                               intersection(set(collTypes[tp])). \
                               intersection(set(indexesVars)))
                val = len(communs)
                if val:
                    line.append(val)
                else:
                    line.append('')
            lines.append(line)

        columns = ['Total'] + typesInnoveComplet
        index = ['Effectifs'] + noms_augmented(self,noms)
        printLines(lines, columns=columns, index=index, pasColonne=pasColonne, pasLigne=pasLigne)


def show_innove_types_pourcent(self,indexesNoms,indexesVars,indexesVarsTypeSortie,dir,
                                   pourcenType=0, PourcenType=100,
                                   effectif=0, Effectif=0,
                                   pasColonne=10, pasLigne=10):

    dictNomsIndexesVarsInnove = defaultdict(list)
    indexesVarsInnoveComplet = []
    for indexNom in tqdm(indexesNoms):
        indexesVarsIn = vars_innove(self,[indexNom], indexesVars,dir)
        dictNomsIndexesVarsInnove[indexNom] = indexesVarsIn
        indexesVarsInnoveComplet += indexesVarsIn

    indexesVarsInnoveComplet = sorted(list(set(indexesVarsInnoveComplet)))
    collTypes = indexesVarsToDictTypesIndexesVars(self,
        indexesVarsInnoveComplet,
        indexesVarsTypeSortie)

    lines = []

    indexesTypesInnoveComplet = sorted([t for t in indexesVarsTypeSortie \
                                        if self.vars_types_types[t] in collTypes])

    # On met d'office les varsTypeSortie demandés :
    typesInnoveComplet = [self.vars_types_types[i] for i in indexesTypesInnoveComplet]

    effectifs = effectifsTypes(self,indexesNoms, indexesVars, indexesTypesInnoveComplet)

    if effectif or Effectif:
        # restriction de indexesVarsTypes
        if Effectif == 0: Effectif = len(self.vars)
        indexesTypesInnoveComplet = [indexesTypesInnoveComplet[i] \
                                     for i in range(len(indexesTypesInnoveComplet)) \
                                     if int(Effectif) >= int(effectifs[i + 1]) >= int(effectif)]
        typesInnoveComplet = [self.vars_types_types[i] for i in indexesTypesInnoveComplet]
        effectifs = [e for e in effectifs if int(Effectif) >= int(e) >= int(effectif)]

    totalVars = len(indexesVars)
    # pourcentage d'innovation total pour chaque nom
    lines.append([effectifs[0]])  # effectif total
    for indexNom in indexesNoms:
        totalNom = len(set(dictNomsIndexesVarsInnove[indexNom]). \
                       intersection(set(indexesVarsInnoveComplet)). \
                       intersection(set(indexesVars)))
        prcNom = str(round(totalNom / totalVars * 100)) + '%'

        lines.append([prcNom])  # pourcentage total

    # application condition sur les pourcentages
    typesReduit = []
    i = 1
    for tp in typesInnoveComplet:
        linesTemp = list(map(list, lines))
        typeReduit = False
        linesTemp[0].append(effectifs[i])
        for n in range(len(indexesNoms)):
            indexNom = indexesNoms[n]
            val = len(
                set(dictNomsIndexesVarsInnove[indexNom]).intersection(set(collTypes[tp])).intersection(set(indexesVars)))
            totalType = totalVarsDefiniesTypeNom(self,indexNom, indexesVars, tp)
            try:
                prc = round(val / totalType * 100)
            except:
                prc = 0
            if val and  int(PourcenType) >= int(prc) >= int(pourcenType):
                typeReduit = True
                linesTemp[1 + n].append(str(prc) + '%')
            else:
                linesTemp[1 + n].append('-')
        if typeReduit:
            lines = list(map(list, linesTemp))
            typesReduit.append(tp)
        i += 1

    columns = ['Total'] + typesReduit
    index = ['Effectifs'] + [self.noms_augmented[n] for n in indexesNoms]

    print("Variables : " + str(len(indexesVars)))
    printLines(lines, columns=columns, index=index, pasColonne=pasColonne,pasLigne=pasLigne)



def test_traduction(self, indexNom, indexesVars,dir='asc'):

    return show_innove_types_pourcent(self, [indexNom], indexesVars, dir,
        varsTypeSortie=['traduction', 'citation'])
