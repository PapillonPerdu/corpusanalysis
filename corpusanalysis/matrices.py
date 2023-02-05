##########################################################################################
### Méthodes sur les matrices de distance
##########################################################################################
# fonction de calcul de la distance
# Les "*","#" et les "?" sont ignorés
# Les '#' sont retirés de stats

from scipy.spatial import distance_matrix
import matplotlib.pyplot as plt
#from sklearn import manifold
#TODO je n'arrive pas à le charger dans l'environnement sqlite.
import networkx as nx
from operator import itemgetter


from .utils import *
from .basics import *

def dist(self, L1, L2, indexesVars):
    dist = 0
    for i in indexesVars:
        if not L1[i] in self.exclus and not L2[i] in self.exclus:
            poids = self.poids[i] if self.poidsExist else 1
            dist += (not strEqual(L1[i], L2[i])) * poids
    return dist


# fonction de calcul de la proximité
def prox(self, L1, L2, indexesVars):
    prox = 0
    for i in indexesVars:
        if not L1[i] in self.exclus and not L2[i] in self.exclus:
            poids = self.poids[i] if self.poidsExist else 1
            prox += (strEqual(L1[i], L2[i])) * poids
    return prox

    # calcule la matrice des distances


def distMat(self, indexesNoms, indexesVars):
    distMat = np.full((len(indexesNoms), len(indexesNoms)), self.selectedDistMax)
    for i in range(len(indexesNoms)):
        for j in range(len(indexesNoms)):
            distMat[i][j] = dist(self,self.data[redindexNomToIndex(self,i, indexesNoms)],
                                      self.data[redindexNomToIndex(self,j, indexesNoms)], indexesVars)
    return distMat


# calcule la matrice de proximité une liste d'indexes de noms et de variables
def proxMat(self, indexesNoms, indexesVars):
    proxMat = np.full((len(indexesNoms), len(indexesNoms)), 0)
    for i in range(len(indexesNoms)):
        for j in range(len(indexesNoms)):
            proxMat[i][j] = prox(self,self.data[redindexNomToIndex(self,i, indexesNoms)],
                                      self.data[redindexNomToIndex(self,j, indexesNoms)], indexesVars)
    return proxMat


def matrices(self):
    self.distance_matrice = self.distMat()
    self.proximite_matrice = self.proxMat()
    # la correlation est une valeur entre 0 et 10
    self.proxCorrelations = 10 - 10 / self.selectedDistMax * self.proximite_matrice
    self.distCorrelations = 10 - 10 / self.selectedDistMax * self.distance_matrice
    # choix d'une distance par défaut...
    self.correlations = self.proxCorrelations


def prox_matrices(self, indexesNoms, indexesVars):
    set_selectedIndexesVars(self,indexesVars)
    set_selectedIndexesNoms(self,indexesNoms)
    self.proximite_matrice = proxMat(self,indexesNoms, indexesVars)
    # la correlation est une valeur entre 0 et 10
    self.proxCorrelations = 10 - 10 / self.selectedDistMax * self.proximite_matrice
    # choix d'une distance par défaut...
    self.correlations = self.proxCorrelations


def dist_matrices(self, indexesNoms, indexesVars):
    set_selectedIndexesVars(self,indexesVars)
    set_selectedIndexesNoms(self,indexesNoms)
    self.distance_matrice = distMat(self,indexesNoms, indexesVars)
    # la correlation est une valeur entre 0 et 10
    self.distCorrelations = 10 - 10 / self.selectedDistMax * self.distance_matrice
    # choix d'une distance par défaut...
    self.correlations = self.distCorrelations


@property
def distance_matrice(self):
    return self.distance_matrice

def updateProxMatrices(self,
                       indexesVars, indexesNoms):
    if not indexesVars == self.selectedIndexesVars or not indexesNoms == self.selectedIndexesNoms:
        prox_matrices(self,indexesNoms, indexesVars)

def updateDistMatrices(self,
                       indexesVars, indexesNoms):
    if not indexesVars == self.selectedIndexesVars or not indexesNoms == self.selectedIndexesNoms:
        dist_matrices(self,indexesNoms, indexesVars)

def show_distance_matrix(self, namesI=[], namesIEx=[], namesJ=[], namesJEx=[], vars=[], varSauf=[]):
    indexesNomsI = nomsToIndexesNoms(self, namesI, namesIEx)
    indexesNomsJ = nomsToIndexesNoms(self, namesJ, namesJEx)
    indexesVars = varsToIndexesVars(self,vars, varSauf)
    indexesNoms = list(set(indexesNomsI) | set(indexesNomsJ))

    updateDistMatrices(self,indexesVars, indexesNoms)

    try:
        self.distance_matrice[0][0]
    except:
        dist_matrices(self,indexesNoms, indexesVars)

    lines = [
        [self.distance_matrice[indexNomToRedindex(self,i, indexesNoms)][indexNomToRedindex(self,j, indexesNoms)]
         for j in indexesNomsJ] for i in indexesNomsI]
    resNomsI = [self.noms_augmented[i] for i in indexesNomsI]
    resNomsJ = [self.noms_augmented[i] for i in indexesNomsJ]
    df = pd.DataFrame(lines, columns=resNomsJ, index=resNomsI)
    return HTML(df.to_html(escape=False))


def show_distance_matrix_normalized(self, namesI=[], namesIEx=[], namesJ=[], namesJEx=[], vars=[], varSauf=[]):
    indexesNomsI = nomsToIndexesNoms(self, namesI, namesIEx)
    indexesNomsJ = nomsToIndexesNoms(self, namesJ, namesJEx)
    indexesVars = varsToIndexesVars(self,vars, varSauf)
    indexesNoms = list(set(indexesNomsI) | set(indexesNomsJ))

    updateDistMatrices(self,indexesVars, indexesNoms)

    try:
        self.distance_matrice[0][0]
    except:
        self.dist_matrices(indexesNoms, indexesVars)

    lines = [
        [self.distCorrelations[indexNomToRedindex(self,i, indexesNoms)][indexNomToRedindex(self,j, indexesNoms)]
         for j in indexesNomsJ] for i in indexesNomsI]
    resNomsI = [self.noms_augmented[i] for i in indexesNomsI]
    resNomsJ = [self.noms_augmented[i] for i in indexesNomsJ]
    df = pd.DataFrame(lines, columns=resNomsJ, index=resNomsI)
    display(HTML(df.to_html(escape=False)))


def show_distance_matrix_percent(self, namesI=[], namesIEx=[], namesJ=[], namesJEx=[], vars=[], varSauf=[]):
    indexesNomsI = nomsToIndexesNoms(self, namesI, namesIEx)
    indexesNomsJ = nomsToIndexesNoms(self, namesJ, namesJEx)
    indexesVars = varsToIndexesVars(self,vars, varSauf)
    indexesNoms = list(set(indexesNomsI) | set(indexesNomsJ))

    updateDistMatrices(self,indexesVars, indexesNoms)

    try:
        self.distance_matrice[0][0]
    except:
        dist_matrices(self,indexesNoms, indexesVars)

    lines = [[int(round(100 * self.distance_matrice[indexNomToRedindex(self,i, indexesNoms)][
        indexNomToRedindex(self,j, indexesNoms)] / self.selectedDistMax)) for j in indexesNomsJ] for i in
             indexesNomsI]
    resNomsI = [self.noms_augmented[i] for i in indexesNomsI]
    resNomsJ = [self.noms_augmented[i] for i in indexesNomsJ]
    df = pd.DataFrame(lines, columns=resNomsJ, index=resNomsI)
    display(HTML(df.to_html(escape=False)))


def save_distance_matrice(self, nomsI=[], nomsISauf=[], nomsJ=[], nomsJSauf=[], vars=[], varSauf=[]):
    indexesNomsI = nomsToIndexesNoms(self,nomsI, nomsISauf)
    indexesNomsJ = nomsToIndexesNoms(self,nomsJ, nomsJSauf)
    indexesVars = varsToIndexesVars(self,vars, varSauf)
    indexesNoms = list(set(indexesNomsI) | set(indexesNomsJ))

    updateDistMatrices(self,indexesVars, indexesNoms)

    try:
        self.distance_matrice[0][0]
    except:
        dist_matrices(self,indexesNoms, indexesVars)

    listNoms = [self.noms[i] for i in indexesNoms]

    fileName = self.baseName + 'Dist.csv'
    pd.DataFrame(self.distance_matrice, columns=listNoms, index=listNoms).to_csv(fileName)

    lines = [
        [self.distance_matrice[indexNomToRedindex(i, indexesNoms)][indexNomToRedindex(self,j, indexesNoms)]
         for j in indexesNomsJ] for i in indexesNomsI]
    resNomsI = [self.noms_augmented[i] for i in indexesNomsI]
    resNomsJ = [self.noms_augmented[j] for j in indexesNomsJ]

    fileName = self.baseName + 'Dist.csv'
    df = pd.DataFrame(lines, columns=resNomsJ, index=resNomsI).to_csv(fileName)
    display(HTML(df.to_html(escape=False)))

    print(
        "La matrice des distances pour la mesure d'éloignement a été enregistrée dans le fichier \"" + self.baseName + "Dist.csv\".")


def save_distance_matrice_pourcent(self, nomsI=[], nomsISauf=[], nomsJ=[], nomsJSauf=[], vars=[], varSauf=[]):
    indexesNomsI = nomsToIndexesNoms(self,nomsI, nomsISauf)
    indexesNomsJ = nomsToIndexesNoms(self,nomsJ, nomsJSauf)
    indexesVars = varsToIndexesVars(self,vars, varSauf)
    indexesNoms = list(set(indexesNomsI) | set(indexesNomsJ))

    updateDistMatrices(self,indexesVars, indexesNoms)

    try:
        self.distance_matrice[0][0]
    except:
        self.dist_matrices(indexesNoms, indexesVars)

    lines = [[int(round(100 * self.distance_matrice[indexNomToRedindex(self,i, indexesNoms)][
        indexNomToRedindex(self,j, indexesNoms)] / self.selectedDistMax)) for j in indexesNomsJ] for i in
             indexesNomsI]
    resNomsI = [self.noms_augmented[i] for i in indexesNomsI]
    resNomsJ = [self.noms_augmented[j] for j in indexesNomsJ]

    fileName = self.baseName + 'Dist.csv'
    df = pd.DataFrame(lines, columns=resNomsJ, index=resNomsI).to_csv(fileName)
    display(HTML(df.to_html(escape=False)))

    print(
        "La matrice des distances en pourcentages pour la mesure d'éloignemnet a été enregistrée dans le fichier \"" + self.baseName + "PourcentDist.csv\".")


def distance_matrice_coordonnees(self, indexesNoms, indexesVars):
    mds = manifold.MDS(n_components=2, dissimilarity="precomputed", random_state=6)
    return mds.fit_transform(self.distance_matrice)


def show_distance_matrix_coordinates(self, indexesNoms, indexesVars):

    updateDistMatrices(self,indexesVars, indexesNoms)

    try:
        self.distance_matrice[0][0]
    except:
        dist_matrices(self,indexesNoms, indexesVars)

    listNoms = [self.noms_augmented[i] for i in indexesNoms]

    df = pd.DataFrame(distance_matrice_coordonnees(self,indexesNoms, indexesVars), columns=['x', 'y'],
                      index=listNoms)
    display(HTML(df.to_html(escape=False)))


def show_distance_ordered(self, indexesNoms, indexesVars,
                          percent=0, Percent=100):
    updateDistMatrices(self,indexesVars, indexesNoms)

    try:
        self.distance_matrice[0][0]
    except:
        dist_matrices(self,indexesNoms, indexesVars)

    distEtNoms = [[self.distance_matrice[i][j],
                   nom_augmented(self,redindexNomToNom(self,j, indexesNoms)) + ' - ' + nom_augmented(self,
                       redindexNomToNom(self,i, indexesNoms))] for i, j
                  in np.ndindex(self.distance_matrice.shape) if i < j and percent <= int(
            round(self.distance_matrice[i][j] * 100 / self.selectedDistMax)) <= Percent]
    distEtNomsOrdonnes = sorted(distEtNoms, key=itemgetter(0), reverse=False)
    distOrdonnes = [[d, int(round(100 * d / self.selectedDistMax))] for d, n in distEtNomsOrdonnes]
    nomsOrdonnes = [n for d, n in distEtNomsOrdonnes]
    df = pd.DataFrame(distOrdonnes, index=nomsOrdonnes, columns=['distance', '%'])
    display(HTML(df.to_html(escape=False)))


def graphe_matrice_distance(self,
                            liens, indexesNoms, indexesVars, pourcent, Pourcent, couleursLiens):
    plt.clf()
    fig = plt.figure(figsize=(self.gmc_width, self.gmc_height))

    coordMat = distance_matrice_coordonnees(self,indexesNoms, indexesVars)

    listNoms = [self.noms[n] for n in indexesNoms]
    # dictionnaire des positions
    pos = {}
    labels = {}
    labels_pos = {}
    for n, c in zip(listNoms, coordMat):
        pos[n] = (c[0], c[1])

    G = nx.Graph()
    G.add_nodes_from(pos.keys())
    colors = []

    for n, p in pos.items():
        G.nodes[n]['pos'] = p
        labels[n] = n
        labels_pos[n] = (pos[n][0] + self.gmc_label_posX, pos[n][1] + self.gmc_label_posY)

    if liens:
        # Création des liens significatifs
        # pour l'ensemble des noeuds

        for redindexi in range(len(indexesNoms)):
            indexi = redindexNomToIndex(self,redindexi, indexesNoms)
            nomi = self.noms[indexi]
            for redindexj in range(len(indexesNoms)):
                indexj = redindexNomToIndex(self,redindexj, indexesNoms)
                nomj = self.noms[indexj]
                if redindexi > redindexj:
                    for k in couleursLiens:
                        if self.correlations[redindexi][redindexj] > k:
                            G.add_edge(nomi, nomj, color=couleursLiens[k],
                                       label=self.correlations[redindexi][redindexj])
                            break

        colors = [G[u][v]['color'] for u, v in G.edges]

    nx.draw(G, pos, with_labels=False, node_size=self.gmc_node_size, node_color=self.gmc_node_color,
            edge_color=colors)
    nx.draw_networkx_labels(G, labels_pos, labels, font_size=self.gmc_font_size, font_color=self.gmc_font_color)

    # pltComp.savefig(baseName+baseNameSecondaire+'Liens.png')
    plt.show()


def show_graphe_distance(self, indexesNoms, indexesVars, links=True,
                         variantes=[],
                         percent=0, Percent=100, linksColors={}):

    if (len(linksColors) == 0): linksColors = {9: 'red', 8: 'green', 7: 'yellow', 6: 'pink'}

    updateDistMatrices(self,indexesVars, indexesNoms)

    try:
        self.distance_matrice[0][0]
    except:
        dist_matrices(self,indexesNoms, indexesVars)

    graphe_matrice_distance(self, links, indexesNoms, indexesVars, percent, Percent, linksColors)
    plt.show()


def save_graphe_distance(self, indexesNoms,indexesVars,liens=True,
                         pourcent=0, Pourcent=100, couleursLiens={}):

    if (len(couleursLiens) == 0): couleursLiens = {9: 'red', 8: 'green', 7: 'yellow', 6: 'pink'}

    updateDistMatrices(self,indexesVars, indexesNoms)

    try:
        self.distance_matrice[0][0]
    except:
        dist_matrices(self,indexesNoms, indexesVars)

    graphe_matrice_coordonnees(self,distance_matrice_coordonnees(self), liens, indexesNoms, indexesVars, pourcent,
                                    Pourcent, couleursLiens)

    plt.savefig(self.baseName + 'Dist.png')
    plt.show()


@property
def proximite_matrice(self):
    return self.proximite_matrice


def show_proximity_matrix(self, namesI=[], namesIEx=[],
                          namesJ=[], namesJEx=[],
                          vars=[], varSauf=[],
                          varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
    indexesNomsI = nomsToIndexesNoms(self, namesI, namesIEx)
    indexesNomsJ = nomsToIndexesNoms(self, namesJ, namesJEx)
    indexesVars = getIndexesVars(self,vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
    indexesNoms = list(set(indexesNomsI) | set(indexesNomsJ))

    updateProxMatrices(self,indexesVars, indexesNoms)

    try:
        self.proximite_matrice[0][0]
    except:
        prox_matrices(self,indexesNoms, indexesVars)

    lines = [
        [self.proximite_matrice[indexNomToRedindex(self,i, indexesNoms)][indexNomToRedindex(self,j, indexesNoms)]
         for j in indexesNomsJ] for i in indexesNomsI]
    resNomsI = [self.noms_augmented[i] for i in indexesNomsI]
    resNomsJ = [self.noms_augmented[i] for i in indexesNomsJ]

    df = pd.DataFrame(lines, columns=resNomsJ, index=resNomsI)
    display(HTML(df.to_html(escape=False)))

    # return pd.DataFrame(self.proximite_matrice, columns=self.selectedNoms, index=self.selectedNoms)


def show_proximity_matrix_normalized(self, namesI=[], namesIEx=[],
                                     namesJ=[], namesJEx=[],
                                     vars=[], varSauf=[],
                                     varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
    indexesNomsI = nomsToIndexesNoms(self, namesI, namesIEx)
    indexesNomsJ = nomsToIndexesNoms(self, namesJ, namesJEx)
    indexesVars = getIndexesVars(self,vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
    indexesNoms = list(set(indexesNomsI) | set(indexesNomsJ))

    updateProxMatrices(self,indexesVars, indexesNoms)

    try:
        self.proximite_matrice[0][0]
    except:
        prox_matrices(indexesNoms, indexesVars)

    lines = [
        [self.proxCorrelations[indexNomToRedindex(self,i, indexesNoms)][indexNomToRedindex(self,j, indexesNoms)]
         for j in indexesNomsJ] for i in indexesNomsI]
    resNomsI = [self.noms_augmented[i] for i in indexesNomsI]
    resNomsJ = [self.noms_augmented[i] for i in indexesNomsJ]
    df = pd.DataFrame(lines, columns=resNomsJ, index=resNomsI)
    display(HTML(df.to_html(escape=False)))


def show_proximity_matrix_percent(self, namesI=[], namesIEx=[],
                                  namesJ=[], namesJEx=[],
                                  vars=[], varSauf=[],
                                  varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
    indexesNomsI = nomsToIndexesNoms(self, namesI, namesIEx)
    indexesNomsJ = nomsToIndexesNoms(self, namesJ, namesJEx)
    indexesVars = getIndexesVars(self,vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
    indexesNoms = list(set(indexesNomsI) | set(indexesNomsJ))

    updateProxMatrices(self,indexesVars, indexesNoms)

    try:
        self.proximite_matrice[0][0]
    except:
        prox_matrices(self,indexesNoms, indexesVars)

    lines = [[int(round(100 * self.proximite_matrice[indexNomToRedindex(self,i, indexesNoms)][
        indexNomToRedindex(self,j, indexesNoms)] / self.selectedDistMax)) for j in indexesNomsJ] for i in
             indexesNomsI]
    resNomsI = [self.noms_augmented[i] for i in indexesNomsI]
    resNomsJ = [self.noms_augmented[j] for j in indexesNomsJ]

    df = pd.DataFrame(lines, columns=resNomsJ, index=resNomsI)
    display(HTML(df.to_html(escape=False)))

    # return pd.DataFrame(self.proximite_matrice, columns=self.selectedNoms, index=self.selectedNoms)


def save_proximite_matrice(self, nomsI=[], nomsISauf=[],
                           nomsJ=[], nomsJSauf=[],
                           vars=[], varSauf=[],
                           varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
    indexesNomsI = nomsToIndexesNoms(self,nomsI, nomsISauf)
    indexesNomsJ = nomsToIndexesNoms(self,nomsJ, nomsJSauf)
    indexesVars = getIndexesVars(self,vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
    indexesNoms = list(set(indexesNomsI) | set(indexesNomsJ))

    updateProxMatrices(indexesVars, indexesNoms)

    try:
        self.proximite_matrice[0][0]
    except:
        prox_matrices(self,indexesNoms, indexesVars)

    lines = [
        [self.proximite_matrice[indexNomToRedindex(self,i, indexesNoms)][indexNomToRedindex(self,j, indexesNoms)]
         for j in indexesNomsJ] for i in indexesNomsI]
    resNomsI = [self.noms[i] for i in indexesNomsI]
    resNomsJ = [self.noms[j] for j in indexesNomsJ]

    pd.DataFrame(lines, columns=resNomsJ, index=resNomsI).to_csv(self.baseName + 'Prox.csv')
    print(
        "La matrice des distances pour la mesure de proximité a été enregistrée dans le fichier \"" + self.baseName + "Prox.csv\".")


def save_proximite_matrice_pourcent(self, nomsI=[], nomsISauf=[],
                                    nomsJ=[], nomsJSauf=[],
                                    vars=[], varSauf=[],
                                    varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
    indexesNomsI = nomsToIndexesNoms(self,nomsI, nomsISauf)
    indexesNomsJ = nomsToIndexesNoms(self,nomsJ, nomsJSauf)
    indexesVars = getIndexesVars(self,vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
    indexesNoms = list(set(indexesNomsI) | set(indexesNomsJ))

    updateProxMatrices(self,indexesVars, indexesNoms)

    try:
        self.proximite_matrice[0][0]
    except:
        prox_matrices(self,indexesNoms, indexesVars)

    lines = [[int(round(100 * self.proximite_matrice[indexNomToRedindex(self,i, indexesNoms)][
        indexNomToRedindex(self,j, indexesNoms)] / self.selectedDistMax)) for j in indexesNomsJ] for i in
             indexesNomsI]
    resNomsI = [self.noms[i] for i in indexesNomsI]
    resNomsJ = [self.noms[j] for j in indexesNomsJ]

    pd.DataFrame(lines, columns=resNomsJ, index=resNomsI).to_csv(self.baseName + 'Prox.csv')
    print(
        "La matrice des distances en pourcentages pour la mesure de proximité a été enregistrée dans le fichier \"" + self.baseName + "PourcentProx.csv\".")


def proximite_matrice_coordonnees(self, indexesNoms, indexesVars):
    mds = manifold.MDS(n_components=2, dissimilarity="precomputed", random_state=6)
    return mds.fit_transform(self.proximite_matrice)


def show_proximity_matrix_coordinates(self, indexesNoms, indexesVars):
    updateProxMatrices(self,indexesVars, indexesNoms)

    try:
        self.proximite_matrice[0][0]
    except:
        prox_matrices(self,indexesNoms, indexesVars)

    listNoms = [self.noms_augmented[i] for i in indexesNoms]
    df = pd.DataFrame(proximite_matrice_coordonnees(self,indexesNoms, indexesVars), columns=['x', 'y'],
                      index=listNoms)
    display(HTML(df.to_html(escape=False)))


def show_proximity_ordered(self, noms=[], nomSauf=[],
                           vars=[], varSauf=[],
                           varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                           nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                           percent=0, Percent=100):
    indexesNoms = getIndexesNoms(self,noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
    indexesVars = getIndexesVars(self,vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

    updateProxMatrices(self,indexesVars, indexesNoms)

    try:
        self.proximite_matrice[0][0]
    except:
        prox_matrices(self,indexesNoms, indexesVars)

    proxEtNoms = [[self.proximite_matrice[i][j],
                   nom_augmented(self,redindexNomToNom(self,j, indexesNoms)) + ' - ' + nom_augmented(self,
                       redindexNomToNom(self,i, indexesNoms))] for i, j
                  in np.ndindex(self.proximite_matrice.shape) if i < j and Percent >= int(
            round(self.proximite_matrice[i][j] * 100 / self.selectedDistMax)) >= percent]
    proxEtNomsOrdonnes = sorted(proxEtNoms, key=itemgetter(0), reverse=True)
    proxOrdonnes = [[d, int(round(100 * d / self.selectedDistMax))] for d, n in proxEtNomsOrdonnes]
    nomsOrdonnes = [n for d, n in proxEtNomsOrdonnes]
    df = pd.DataFrame(proxOrdonnes, index=nomsOrdonnes, columns=['proximité', '%'])
    display(HTML(df.to_html(escape=False)))


def graphe_matrice_proximite(self, coordMat, liens, indexesNoms, indexesVars, pourcent, Pourcent, couleursLiens):
    plt.clf()
    fig = plt.figure(figsize=(self.gmc_width, self.gmc_height))

    coordMat = proximite_matrice_coordonnees(self,indexesNoms, indexesVars)

    listNoms = [self.noms[n] for n in indexesNoms]
    # dictionnaire des positions
    pos = {}
    labels = {}
    labels_pos = {}
    for n, c in zip(listNoms, coordMat):
        pos[n] = (c[0], c[1])

    G = nx.Graph()
    G.add_nodes_from(pos.keys())
    colors = []

    for n, p in pos.items():
        G.node[n]['pos'] = p
        labels[n] = n
        labels_pos[n] = (pos[n][0] + self.gmc_label_posX, pos[n][1] + self.gmc_label_posY)

    if liens:
        # Création des liens significatifs
        # pour l'ensemble des noeuds

        for redindexi in range(len(indexesNoms)):
            indexi = redindexNomToIndex(self,redindexi, indexesNoms)
            nomi = self.noms[indexi]
            for redindexj in range(len(indexesNoms)):
                indexj = redindexNomToIndex(self,redindexj, indexesNoms)
                nomj = self.noms[indexj]
                if redindexi > redindexj:
                    for k in couleursLiens:
                        if self.correlations[redindexi][redindexj] < k:
                            G.add_edge(nomi, nomj, color=couleursLiens[k],
                                       label=self.correlations[redindexi][redindexj])
                            break

        colors = [G[u][v]['color'] for u, v in G.edges]

    nx.draw(G, pos, with_labels=False, node_size=self.gmc_node_size, node_color=self.gmc_node_color,
            edge_color=colors)
    nx.draw_networkx_labels(G, labels_pos, labels, font_size=self.gmc_font_size, font_color=self.gmc_font_color)

    # pltComp.savefig(baseName+baseNameSecondaire+'Liens.png')
    plt.show()


def show_graph_proximity(self, indexesNoms, indexesVars, liens=True,
                         percent=0, Percent=100, linksColors={}):

    if (len(linksColors) == 0): linksColors = {1: 'red', 2: 'green', 3: 'yellow', 4: 'pink'}

    updateProxMatrices(self,indexesVars, indexesNoms)

    try:
        self.proximite_matrice_coordonnees[0][0]
    except:
        prox_matrices(self,indexesNoms, indexesVars)

    graphe_matrice_proximite(self, proximite_matrice_coordonnees(self,indexesNoms, indexesVars), liens, indexesNoms,
                             indexesVars, percent, Percent, linksColors)
    plt.show()


def save_graphe_proximite(self, liens=True, noms=[], nomSauf=[], vars=[], varSauf=[],
                          varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                          nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                          pourcent=0, Pourcent=100, couleursLiens={}):
    indexesNoms = getIndexesNoms(self,noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
    indexesVars = getIndexesVars(self,vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

    updateProxMatrices(self,indexesVars, indexesNoms)

    if (len(couleursLiens) == 0): couleursLiens = {9: 'red', 8: 'green', 7: 'yellow', 6: 'pink'}

    try:
        self.proximite_matrice[0][0]
    except:
        prox_matrices(self,indexesNoms, indexesVars)

    graphe_matrice_coordonnees(self,
        proximite_matrice_coordonnees(self,indexesNoms, indexesVars), liens, indexesNoms,
        indexesVars, pourcent, Pourcent, couleursLiens)

    plt.savefig(self.baseName + 'Prox.png')
    plt.show()


# détermine la corrélation la plus faible d'une matrice de distances m et les éditions ayant cette corrélation
def minCor(self, m):
    min = np.amin(m)
    worse = np.where(m == min)
    rs = list(zip(worse[0], worse[1]))
    rs = np.array([(self.noms[i], self.noms[j]) for (i, j) in rs if i > j])
    # res=rs[:len(rs)//2]
    sum = sum(self.poids) if self.poidsExist else len(self.vars)
    return [str(round(100 * min / sum)) + '%', rs]


# détermine la corrélation la plus faible d'une matrice de distances m et les éditions ayant cette corrélation
def maxCor(self, m):
    # on exclut les élements au-dessus de la diagonale, diagonale comprise
    m = np.tril(m, -1)
    max = np.amax(m)
    best = np.where(m == max)
    rs = list(zip(best[0], best[1]))
    rs = np.array([(self.noms[i], self.noms[j]) for (i, j) in rs if i > j])
    # res=rs[:len(rs)//2]
    sum = sum(self.poids) if self.poidsExist else len(self.vars)
    return [str(round(100 * max / sum)) + '%', rs]


@property
def maxDistCor(self):
    return maxCor(self,self.distance_matrice)


@property
def minDistCor(self):
    return minCor(self,self.distance_matrice)


@property
def maxProxCor(self):
    pass


@property
def minProxCor(self):
    return minCor(self,self.proximite_matrice)


@property
def gmc_size(self):
    print(self.gmc_width, 'x', self.gmc_height)



@property
def gmc_font_size(self):
    print("Taille des labels des nœuds : ", self.gmc_font_size)




@property
def gmc_font_color(self):
    print("Couleur des labels des nœuds : ", self.gmc_font_color)


@property
def gmc_node_color(self):
    print("Couleur des nœuds : ", self.gmc_node_color)


@property
def gmc_node_size(self):
    print("Taille des nœuds : ", self.gmc_node_size)


