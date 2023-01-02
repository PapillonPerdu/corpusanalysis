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



        # Tableau descendant des corrélations

def corr(self,indexNom1, indexNom2, indexesVars,variantes=[]):
    """        :return: {
                effectif : number of variables where both indexNom1 and indeNom2 have positive values
                effectif1 : number of positive values of indexNom1.
                 effectif2: number of positive values of indexNom2.
                 equal : number of equal values (a & b = b & c)
                 percent : percentage of equal values : effectif/commun*100 arrondi à la première décimale
        """
    correlation = 0
    effectif = 0
    for v in indexesVars:
        if not self.data[indexNom1][v] in self.exclus and \
                not self.data[indexNom2][v] in self.exclus:
                effectif += 1
                if equal(self.data[indexNom1][v], self.data[indexNom2][v],variantes):
                    correlation += 1
    effectif1 = len([i for i in indexesVars if self.data[indexNom1][i] not in self.exclus])
    effectif2 = len([i for i in indexesVars if self.data[indexNom2][i] not in self.exclus])
    try:
        percent = round(correlation/effectif*100)
    except:
        percent = 0
    return {'effectif':effectif,'effectif1':effectif1,'effectif2':effectif2,'equal':correlation,'percent':percent}

def tableau_correlations(self,
                         indexNom, indexesNoms, indexesVars,
                         variantes=[],
                         percent=0, Percent=100,
                         effectif=0,Effectif=float('inf')):
    # liste des corrélations avec le nom au début et le total à la fin
    cor = []
    for n in indexesNoms:
        if not n == indexNom:
            l = difference(self, n, indexNom, indexesVars,variantes=variantes)
            # ajouts des stats en début de liste
            corTotal = corr(self,indexNom, n, indexesVars,variantes)
            l = [self.noms[n], corTotal['percent'], corTotal['effectif'], corTotal['equal']] + l
            if percent <= corTotal['percent'] <= Percent\
                    and \
                    effectif <= corTotal['effectif'] <= Effectif :
                cor.append(l)
    cor_sorted = sorted(cor, key=itemgetter(1), reverse=True)
    return cor_sorted

def indexesVars_discrimine(self,
                    indexNom, discrimines, indexesVars,
                    variantes=[]):
    """Variables which values for a name discriminate between two names, i.e. that are the same for one but different for the other."""
    varsDiff = vars_difference(self, discrimines[0], discrimines[1],
                               vars_relative_sum(self, indexNom, discrimines, indexesVars, variantes=variantes),
                               variantes=variantes)
    indexesVars = list(set(indexesVars) & set(varsDiff))
    indexesVarsInnove = vars_innove(self, [indexNom], indexesVars, 'asc')
    indexesVars = sorted(list(set(indexesVars) - set(indexesVarsInnove)))
    return indexesVars

def show_discrimine(self,
                    indexNom, discrimines, indexesVars,
                    variantes=[],
                    pasColonne=10,
                    decoration=True):
    """Displays values of a name that discriminate between two names, i.e. that are the same for one but different for the other."""

    #varsDiff = vars_difference(self, discrimines[0], discrimines[1],
   #                            vars_relative_sum(self, indexNom, discrimines, indexesVars, variantes=variantes), variantes=variantes)
    #indexesVars = list(set(indexesVars) & set(varsDiff))
    #indexesVarsInnove = vars_innove(self, [indexNom], indexesVars, 'asc')
    #indexesVars = sorted(list(set(indexesVars) - set(indexesVarsInnove)))
    indexesVars = indexesVars_discrimine(self,
                    indexNom, discrimines, indexesVars,
                    variantes=[])

    show_correlations(self, indexNom, discrimines, indexesVars,
                      variantes=variantes, pasColonne=pasColonne,decoration=decoration)


def show_correlations(self,
                      indexNom, indexesNoms, indexesVars,
                      percent=0, Percent=100,
                      effectif=0, Effectif=float('inf'),
                      variantes = [],
                      pasColonne=10, pasLigne=10,
                      decoration=True):
    #on se restreint aux variables sur lesquelles indexNom a des valeurs non excluses
    indexesVars = indexesVarsDefiniesNom(self, indexNom,indexesVars)
    cor = tableau_correlations(self, indexNom, indexesNoms, indexesVars,
                               variantes = variantes,
                               percent=percent, Percent=Percent,
                               effectif=effectif,Effectif=Effectif)

    # première ligne avec les critères
    varsL = ['%', 'effectif', 'communs'] + [self.vars_augmented[v] if decoration else self.vars[v] for v in indexesVars]
    nom = self.noms_augmented[indexNom] if decoration else self.noms[indexNom]
    nomsL = [nom]
    corData = [['-',str(len(indexesVars)),'-']+[self.data_augmented[indexNom][v] for v in indexesVars]]
    for L in cor:
        nm = L[0]
        nomsL.append(self.noms_augmented[self.noms.index(nm)] if decoration else self.noms[self.noms.index(nm)])
        del L[0]
        L[0] = str(L[0]) + '%'
        corData.append(valuesToValues_augmented(self, L, indexesVars, self.noms.index(nm), start=3))
    
    print(color.bold + 'Correlations of {}'.format(self.noms[indexNom]) + color.end)
    print('Names : ' + str(len(nomsL)))
    print('Variables : ' + str(len(varsL) - 3))
    printLines(corData, columns=varsL, index=nomsL, pasColonne=pasColonne, pasLigne=pasLigne)


#####################################
# tableaux corrélation types
#####################################

def tableau_correlations_types(self,
                               indexNom, indexesNoms, indexesVars, indexesVarsTypeSortie,
                               variantes=[],
                               effectif=0, Effectif=float('inf'),
                               percent=0, Percent=100,
                               effectifType=0, EffectifType=float('inf')):
    # dict des corrélations  par types de variables,
    # avec le nom, le pourcentage total de valeurs communes, l'effectif total, l'effectif commun total, au début
    lines = []
    for n in indexesNoms:
        if not n == indexNom:
            line = []
            #contrôle la corrélation d'ensemble
            corTotal = corr(self, indexNom, n, indexesVars, variantes=variantes)
            if percent <= corTotal['percent'] <= Percent and \
                    effectif <= corTotal['effectif'] <= Effectif:
                for t in indexesVarsTypeSortie:
                    indexesVarsTp = indexVarsTypeToIndexesVars(self,t,indexesVars)
                    cor = corr(self,indexNom,n,indexesVarsTp)
                    if effectifType <= cor['effectif'] <= EffectifType:
                        val = cor['equal']
                        line.append(val)
                    else:
                        line.append('')
                line = [self.noms[n], corTotal['percent'], corTotal['effectif'], corTotal['equal']] + line
                lines.append(line)


    lines_sorted = sorted(lines, key=itemgetter(1), reverse=True)
    return lines_sorted

def show_compare_types(self, indexNom1, indexNom2, indexesVars, indexesVarsTypesOutput=[],
                       variantes=[],
                       effectif=0, Effectif=float('inf'),
                       effectifType=0, EffectifType=float('inf'),
                       pasColonne=10, order=''):
    #effectifs pour les types sélectionnés
    effectifs = effectifsTypesNom(self, indexNom1, indexesVars, indexesVarsTypesOutput)

    # Restriction aux types selon les effectifs
    if effectifType or EffectifType:
        indexesVarsTypesReduit = [indexesVarsTypesOutput[i] for i in range(len(indexesVarsTypesOutput)) \
                                  if EffectifType >= effectifs[i + 1] >= effectifType]
        effectifs = [e for e in effectifs if EffectifType >= e >= effectifType]
        indexesVarsTypesOutput = indexesVarsTypesReduit

    lines=tableau_correlations_types(self,
                                     indexNom1, [indexNom2], indexesVars, indexesVarsTypesOutput,
                                     variantes=variantes,
                                     effectif=effectif, Effectif=Effectif,
                                     effectifType=effectifType, EffectifType=EffectifType)

    line=lines[0]
    total=effectifs[0]
    if order=='asc' or order=='desc':
        reverse = False if order == 'asc' else True
        communs,effectifs, indexesVarsTypesOutput = zip(*sorted(zip(line[4:],effectifs[1:], indexesVarsTypesOutput), reverse=reverse))
        communs = list(communs)
        effectifs = list(effectifs)
        indexesVarsTypesOutput = list(indexesVarsTypesOutput)

    else:
        communs=line[4:]
        effectifs=effectifs[1:]

    communsprc = [str(round(c/total*100))+'%' for c in communs]
    typesprc = [str(round(communs[i]/effectifs[i]*100))+'%' for i in range(len(communs))]
    columns=['Total']+[self.vars_types_types[t] for t in indexesVarsTypesOutput]
    index=['Effectifs','Communs','%Communs','%Types']
    lines=[[total]+effectifs,[line[3]]+communs,[str(round(line[3]/total*100))+'%']+communsprc,['']+typesprc]
    printLines(lines, columns=columns, index=index, pasColonne=pasColonne)

def show_compare_types_percent(self,
                               indexNom1, indexNom2, indexesVars, indexesVarsTypesOutput,
                               variantes=[],
                               effectif=0, Effectif=float('inf'),
                               percent=0, Percent=100,
                               percenType=0, PercenType=100,
                               effectifType=0, EffectifType=float('inf'),
                               pasColonne=10, order=''):

    #effectifs pour les types sélectionnés
    effectifs = effectifsTypesNom(self, indexNom1, indexesVars, indexesVarsTypesOutput)

    # Restriction aux types selon les effectifs
    if effectifType or EffectifType:
        indexesVarsTypesReduit = [indexesVarsTypesOutput[i] for i in range(len(indexesVarsTypesOutput)) \
                                  if EffectifType >= effectifs[i + 1] >= effectifType]
        effectifs = [e for e in effectifs if EffectifType >= e >= effectifType]
        indexesVarsTypesOutput = indexesVarsTypesReduit

    lines = tableau_correlations_types_percent(self, indexNom1, [indexNom2], indexesVars,
                                               indexesVarsTypesOutput,
                                               variantes=variantes,
                                               effectif=effectif, Effectif=Effectif,
                                               percent=percent, Percent=Percent,
                                               percenType=percenType, PercenType=PercenType,
                                               effectifType=effectifType, EffectifType=EffectifType)

    line = lines[0]
    total = effectifs[0]
    effectifs = effectifs[1:]
    typesprc = line[3:]
    # Restriction aux types selon les pourcentages communes
    # le faire de toute façon, car il peut y avoir des '' à la place de 0
    # if percenType !=0  or PercenType != 100:
    indexesVarsTypesReduit=[]
    effectifsReduits = []
    typesprcReduits = []
    for i in range(len(indexesVarsTypesOutput)):
        if typesprc[i] :
            indexesVarsTypesReduit.append(indexesVarsTypesOutput[i])
            effectifsReduits.append(effectifs[i])
            typesprcReduits.append(typesprc[i])

    indexesVarsTypesOutput = indexesVarsTypesReduit
    effectifs = effectifsReduits
    typesprc = typesprcReduits


    if typesprc and (order=='asc' or order=='desc'):
        reverse = False if order == 'asc' else True
        typesprc, effectifs, indexesVarsTypesOutput = zip(*sorted(zip(typesprc,effectifs, indexesVarsTypesOutput), reverse=reverse))
        typesprc = list(typesprc)
        effectifs = list(effectifs)
        indexesVarsTypesOutput = list(indexesVarsTypesOutput)


    typesprc = [str(t)+'%' for t in typesprc]
    columns = ['Total'] + [self.vars_types_types[t] for t in indexesVarsTypesOutput]
    index = ['Effectifs', '%Types']
    lines = [[total] + effectifs, ['']+typesprc]
    printLines(lines, columns=columns, index=index, pasColonne=pasColonne)


# Tableau descendant des corrélations par types exprimées en pourcentages (relativement à chaque type)
# les corrélations sont déterminées à partir des variables
# les types servent à la présentation des résultats
def tableau_correlations_types_percent(self,
                                       indexNom, indexesNoms, indexesVars, indexesVarsTypeSortie,
                                       variantes=[],
                                       effectif=0, Effectif=float('inf'),
                                       effectifType=0, EffectifType=float('inf'),
                                       percent=0, Percent=100,
                                       percenType=0, PercenType=100):
    # dict des corrélations descendantes par types de variables,
    # avec le nom  et le total au début
    lines = []
    for n in indexesNoms:
        if not n == indexNom:
            line = []
            corTotal = corr(self, indexNom, n, indexesVars, variantes=variantes)
            corTotal['percent']
            if percent <= corTotal['percent'] <= Percent and \
                    effectif <+ corTotal['effectif'] <= Effectif:
                for t in indexesVarsTypeSortie:
                    indexesVarsTp = indexVarsTypeToIndexesVars(self, t, indexesVars)
                    cor = corr(self, indexNom, n, indexesVarsTp, variantes=variantes)
                    if effectifType <= cor['effectif'] <= EffectifType and \
                            percenType <= cor['percent'] <=PercenType:
                        val = cor['percent']
                        line.append(val)
                    else:
                        line.append('')
                line = [self.noms[n], corTotal['percent'], corTotal['effectif']] + line
                lines.append(line)

    lines_sorted = sorted(lines, key=itemgetter(1),reverse=True)

    return lines_sorted


def show_correlations_types(self,
                            indexNom, indexesNoms, indexesVars,
                            indexesVarsTypeSortie,
                            variantes=[],
                            effectif=0, Effectif=float('inf'),
                            percent=0, Percent=100,
                            effectifType=0, EffectifType=float('inf'),
                            pasColonne=10, pasLigne=10,
                            decoration=True):
    effectifs = effectifsTypesNom(self, indexNom, indexesVars, indexesVarsTypeSortie)

    #Restriction aux types selon les effectifs
    if effectifType or EffectifType:
        effectifs = effectifsTypesNom(self, indexNom, indexesVars, indexesVarsTypeSortie)
        indexesVarsTypesReduit = [indexesVarsTypeSortie[i] for i in range(len(indexesVarsTypeSortie)) \
                                  if EffectifType >= effectifs[i + 1] >= effectifType]
        effectifs = [e for e in effectifs if EffectifType >= e >= effectifType]
        indexesVarsTypeSortie = indexesVarsTypesReduit

    cor = tableau_correlations_types(self, indexNom, indexesNoms, indexesVars,
                                     indexesVarsTypeSortie,
                                     variantes=variantes,
                                     effectif=effectif, Effectif=Effectif,
                                     percent=percent, Percent=Percent,
                                     effectifType=effectifType, EffectifType=EffectifType)
    corData = []
    total = effectifs[0]

    # première ligne avec l'effectif total et pour chaque type
    corData.append(['',total]+effectifs)
    nomsL = []
    for L in cor:
        if decoration:
            nomsL.append(nom_augmented(self, L[0]))
        else:
            nomsL.append(L[0])
        del L[0]
        L=[str(L[0])+'%']+L[1:]
        corData.append(L)

    columns = ['% total','total','communs'] + [self.vars_types_types[t] for t in indexesVarsTypeSortie]
    index = ['Effectifs'] + nomsL
    print(color.bold + 'Correlations by types of ' + self.noms[indexNom]+ color.end)
    print('Types : ' + str(len(indexesVarsTypeSortie)))
    printLines(corData, columns=columns, index=index, pasColonne=pasColonne, pasLigne=pasLigne)


# liste du nombre de variables pour chaque type d'une édition donnée,
# avec au début le total sur l'ensemble des types
def effectifsTypesNom(self,
                      indexNom, indexesVars, indexesVarsTypes):
    effectifs = [totalVarsNom(self, indexNom, indexesVars)] + \
                [totalVarsDefiniesTypeNom(self, indexNom, indexesVars, t) for t in
                 indexesVarsTypes]
    return effectifs


# liste du nombre de variables pour chaque type d'une liste d'éditions donnée,
# avec au début le total sur l'ensemble des types
def effectifsTypes(self, indexesNoms, indexesVars, indexesVarsTypes):
    effectifs = [totalVarsDefinies(self, indexesNoms, indexesVars)] + \
                [totalVarsDefiniesType(self, indexesNoms, indexesVars, self.vars_types_types[tp]) for tp in
                 indexesVarsTypes]
    return effectifs


def show_correlations_types_percent(self,
                                    indexNom, indexesNoms, indexesVars, indexesVarsTypeSortie,
                                    variantes=[],
                                    effectif=0, Effectif=float('inf'),
                                    percent=0, Percent=100,
                                    percenType=0, PercenType=100,
                                    effectifType=0, EffectifType=float('inf'),
                                    pasColonne=10, pasLigne=10,
                                    decoration=True):
    effectifs = effectifsTypesNom(self, indexNom, indexesVars, indexesVarsTypeSortie)

    # Restriction aux types selon les effectifs
    if effectifType or EffectifType:
        indexesVarsTypesReduit = [indexesVarsTypeSortie[i] for i in range(len(indexesVarsTypeSortie)) \
                                  if EffectifType >= effectifs[i + 1] >= effectifType]
        effectifs = [e for e in effectifs if EffectifType >= e >= effectifType]
        indexesVarsTypeSortie = indexesVarsTypesReduit

    cor = tableau_correlations_types_percent(self, indexNom, indexesNoms, indexesVars,
                                             indexesVarsTypeSortie,
                                             variantes=variantes,
                                             effectif=effectif, Effectif=Effectif,
                                             percent=percent, Percent=Percent,
                                             percenType=percenType, PercenType=PercenType,
                                             effectifType=effectifType, EffectifType=EffectifType)


    varsTypeSortie = [self.vars_types_types[t] for t in indexesVarsTypeSortie]
    corData = []

    # première ligne avec l'effectif total et pour chaque type
    corData.append(['']+effectifs)

    nomsL = []
    for L in cor:
        nomsL.append(nom_augmented(self, L[0],decoration))
        del L[0]
        L=[str(L[0])+'%', L[1]]+[str(L[i+2])+'%' if L[i+2] else '-' for i in range(len(L)-2)]
        corData.append(L)

    columns = ['% total', 'Effectifs'] + varsTypeSortie
    index = ['Effectifs'] + nomsL
    lines = corData
    print(color.bold + "Correlations by types percentages of  {}".format(self.noms[indexNom])+color.end)
    printLines(lines, columns=columns, index=index, pasColonne=pasColonne, pasLigne=pasLigne)





# Fonction pour discriminer les corrélations d'une édition à deux autres
# suivant les types, exprimés en pourcentages
def show_discrimine_types_percent(self,
                                   indexNom, discrimines, indexesVars, indexesVarsTypeSortie,
                                   variantes=[],
                                   pasColonne=10):
    varsDiff = vars_difference(self, discrimines[0], discrimines[1], indexesVars)
    indexesVars = list(set(indexesVars) & set(varsDiff))

    show_correlations_types_percent(self,
                                    indexNom, [discrimines[0], discrimines[1]], indexesVars, indexesVarsTypeSortie,
                                    variantes=variantes,
                                    pasColonne=pasColonne)


def plot_intervals(self, indexNom1, indexNom2, indexesVars, longueur,variantes=[],
                   pas=1, elev=0, azim=0):
    indexMax = len(indexesVars)
    L1 = self.data[indexNom1]
    L2 = self.data[indexNom2]

    def fun(xList, yList, L1, L2, indexesVars):
        res = [listsEqualPourcent(L1, L2, indexesVars[x:y + 1],variantes) for x, y in zip(xList, yList)]

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

