from .basics import *
from .defs import *

# indexes des variables ayant des valeurs sur tous les indexes de vars et de noms considérés
def indexesDomaine(self, indexesVars, indexesNoms):
    indexesNotDomaine = [v for v in indexesVars for n in indexesNoms if self.data[n][v] in self.nuls]
    indexesDomaine=sorted(list(set(indexesVars)-set(indexesNotDomaine)))
    return indexesDomaine

# variables ayant des valeurs sur les vars et noms considérés
def domaine(self, vars=[], noms=[]):
    indexesVars = varsToIndexesVars(self,vars)
    indexesNoms = nomsToIndexesNoms(self,noms)
    domaine = [self.vars[v] for v in indexesDomaine(self,indexesVars,indexesNoms)]
    return domaine


# indexes des noms ayant des valeurs pour sur tous les indexes de vars et de noms considérés@@
def indexesCorpus(self, indexesVars, indexesNoms):
    indexesNotCorpus = [n for n in indexesNoms for i in indexesVars if self.data[n][i] in self.nuls]
    indexesCorpus=sorted(list(set(indexesNoms)-set(indexesNotCorpus)))
    return indexesCorpus



def indexesVars_manquantes(self, indexNom,indexesVars):
    """
    indexes des variables sans valeur d'une édition donnée parmi des indexes donnés
    """
    manquantes = [i for i in indexesVars if self.data[indexNom][i] in self.nuls]
    return manquantes


def varsManquantes(self, indexesVars, indexNom):
    """
    :param indexesVars:
    :param indexNom:
    :return: indexes des variables pour lesquelles les valeurs manquent
    """
    return [i for i in indexesVars if self.data[indexNom][i] in ['','?']]


def show_vars_manquantes(self,indexNom,indexesVars):
    """
    Tableau des variables sans valeur pour le nom donné.

    """

    indexesVarsManque = varsManquantes(self,indexesVars, indexNom)
    varsManque = [indexToVar_augmented(self,v) for v in indexesVarsManque]
    line = [self.data_augmented[indexNom][v] for v in indexesVarsManque]
    if varsManque:
        print('Valeurs manquantes pour ' + nom + ' : ' + str(len(varsManque)))
        printLines([line], index=[nom_augmented(self,nom)], columns=varsManque)
    else:
        print(color.bold + 'Aucune variable sans valeur pour le nom \"' + nom + '\".')


def show_types_vars_manquants(self):
    """
    :return: types de variables non assignés
    """
    resTypes = [t for t in self.vars_types_types if not self.typeToVars(t)]
    if resTypes:
        df = pd.DataFrame(index=resTypes)
        print(color.bold + "Types de variables non assignés :" + color.end)
        return display(HTML(df.to_html(escape=False)))
    else:
        print(color.bold + "Tous les types sont assignés à des variables." + color.end)

def indexesVarsTypes_manquants(self, indexesVars):
    """
    :param indexNom:
    :param indexesVars:
    :return: indexes des variables sans types
    """
    manquantes = [v for v in indexesVars if not indexVarToTypes(self,v)]
    return manquantes

def show_vars_types_manquants(self,indexesVars):
    """
    Tableau des variables sans types.

    """

    resVars = [self.vars_augmented[i] for i in indexesVarsTypes_manquants(self,indexesVars)]
    if resVars:
        print(color.bold + "Variables sans types : " + color.end)
        printLines(columns=resVars)
    else:
        print(color.bold + "Toutes les variables ont un type." + color.end)


def indexesNomsTypes_manquants(self, indexesNoms):
    """
    :param indexesNoms:
    :return: indexes des noms sans types
    """
    manquants = [n for n in indexesNoms if not indexNomToTypes(self,n)]
    return manquants

def show_noms_types_manquants(self,indexesNoms):
    """
    :param noms:
    :param nomSauf:
    :param nomsTypes:
    :param nomsTypeSauf:
    :param nomsTypesFormule:
    :return: affiche les noms sans types
    """
    # TODO : contrôler l'existence de types de noms.
    resNoms = [self.noms_augmented[i] for i in indexesNomsTypes_manquants(self,indexesNoms)]
    if resNoms:
        print(color.bold + "Noms sans types : " + color.end)
        printLines(index=resNoms)
    else:
        print(color.bold + "Tous les noms ont un type." + color.end)


def show_noms_manquants(self, indexesNoms,indexesVars):
    """
    Tableau des noms et des variables pour lesquelles les noms n'ont pas de valeur

    """


    indexesCorp=indexesCorpus(self,indexesVars,indexesNoms)
    indexesNomsManquants=list(set(indexesNoms) - set(indexesCorp))

    indexesDom = indexesDomaine(self,indexesVars, indexesNoms)
    indexesVarsManquantes=sorted(list(set(indexesVars) - set(indexesDom)))
    if indexesVarsManquantes :
        print(color.bold + "Noms pour lesquels des variables n'ont pas de valeur : " +str(len(indexesNomsManquants))+ color.end)
        data_manquent=[]
        for n in range(len(indexesNomsManquants)) :
            line=[]
            for v in range(len(indexesVarsManquantes)):
                if self.data[indexesNomsManquants[n]][indexesVarsManquantes[v]] in self.nuls :
                    line.append('x')
                else:
                    line.append('')
            data_manquent.append(line)

        printLines(data_manquent,
                          columns=indexesToVars(self,indexesVarsManquantes),
                          index=indexesToNoms(self,indexesNomsManquants))
    else:
        print(color.bold + "Aucun des noms n'a de variable sans valeur : " +  color.end)


def noms_thamous_manquant(self, indexesNoms):

    l = [self.noms[n] for n in indexesNoms if
         self.noms_tables_dic[self.noms[n]] == '' or
        self.noms_ids_dic[self.noms[n]] == '' or
        self.noms_prjts_dic[self.noms[n]] == '']
    return l

def show_types_vars_manquants(self):
    """
    :return: types attribués à aucune variable
    """
    resTypes=[t for t in self.vars_types_types if typeToVars(self,t)]
    if resTypes:
        print(color.bold +'Types de variables non attribués : ' +color.end)
        printLines(index=resTypes)
    else:
        print(color.bold + 'Tous les types sont attribués à une variable.')

def show_types_noms_manquants(self):
    """
    :return: types attribués à aucun nom
    """
    resTypes=[t for t in self.noms_types_types if typeToNoms(self,t)]
    if resTypes:
        print(color.bold +'Types de noms non attribués : ' +color.end)
        display(pd.DataFrame(index=resTypes))
    else:
        print(color.bold + 'Tous les types sont attribués à un nom.')

def show_citations_manquantes(self, indexesNoms,indexesVars):
    """
   Valeurs sans citations pour les variables et les noms donnés
    """
    try: self.citations
    except :
        print(color.bold +'Aucun fichier de citations.' +color.end)
        raise

    indexesVarsDefinies=indexesDomaine(self,indexesVars, indexesNoms)
    lines=[]
    noms=[]
    for n in indexesNoms:
        line=[]
        manque = False
        for v in indexesVarsDefinies:
            if self.citations[n][v] in self.nuls and not self.data[n][v] in self.exclus:
                line.append(self.data_and_citations[n][v])
                manque = True
            else:
                line.append('')
        if manque:
            lines.append(line)
            noms.append(self.noms[n])

    if lines:
        print(color.bold +'Valeurs sans citation associée : ' +color.end)
        printLines(lines, index=noms, columns=indexesToVars(self,indexesVarsDefinies))
    else:
        print(color.bold + 'Toutes les valeurs ont une citation associée.')


def show_vars_defs_manquantes(self,indexesVars):
    """
variables sans définition
    """

    resVars=[self.vars_augmented[v] for v in indexesVars if self.vars[v] in self.vars_sans_def ]
    if resVars:
        print('Variables sans définition : ' + str(len(resVars)))
        printLines([], columns=resVars)
    else:
        print(color.bold + 'Toutes les variables ont une définition.')

def show_noms_defs_manquantes(self,indexesNoms):
    """
noms sans définition
    """

    resNoms=[n for n in indexesNoms if n in self.noms_sans_def ]
    if resNoms:
        print('Noms sans définition : ' + str(len(resNoms)))
        printLines(columns=resVars)
    else:
        print(color.bold + 'Tous les noms ont une définition.')


def indexesVarsDefiniesNom(self,
                           indexNom, indexesVars):
    """
    :param indexNom:
    :param indexesVars:
    :return: indexes des variables pour lesquelles un nom, donné par son index, a une vraie valeur (i.e. n'a pas une valeur exclue)
    """

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





#vars définies d'une édition
def vars_definies(self,indexNom,indexesVars):
    resVars=[self.vars[v] for v in indexesVars if not self.data[indexNom][v] in self.exclus ]
    return resVars

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




