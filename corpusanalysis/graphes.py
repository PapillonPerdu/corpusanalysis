##########################################################################################
### Graphes de déviation
##########################################################################################
import matplotlib.colors as colors
import matplotlib.cm as cmx


import matplotlib.pyplot as plt
import networkx as nx

from .basics import *
from .matrices import *


def set_graphe(self, width='', height='',
               font_size='', font_color='',
               node_color='',
               label_posX='', label_posY=''):
    if not width == '':
        self.set_graph_width(width)

    if not height == '':
        self.set_graph_height(height)

    if not font_size == '':
        self.set_font_size(font_size)

    if not font_color == '':
        self.set_font_color('black')

    if not node_color == '':
        self.set_node_color('black')

    if not label_posX == '':
        self.set_label_posX(label_posX)

    if not label_posY == '':
        self.set_label_posY(label_posY)


@property
def distance_matrice(self):
    return self.distance_matrice


@property
def proximite_matrice(self):
    return self.proximite_matrice


@property
def correlations(self):
    return self.correlations


def colorMap(self, cm):
    self.colorMap = cm


def graphe_deviation(self, indexNom, indexesVars, indexesNoms, pourcent, Pourcent):
    nom = self.noms[indexNom]

    x0 = 0  # abcisse edition
    y0 = 0  # ordonnée edition
    sources = []

    plt.clf()
    fig = plt.figure(figsize=(self.graph_width, self.graph_height))
    # print(pd.DataFrame(cor, columns=self.noms, index=self.noms))

    # Noeud de la référence sélectionnée
    try:
        date0 = int(self.data[indexNom][0])
    except:
        date0 = indexNom
    dateMax = dateMin = date0
    Gr = nx.Graph()
    Gr.add_node(nom)
    Gr.nodes[nom]['annee'] = dateMax
    Gr.nodes[nom]['pos'] = (x0, y0)

    # Si nécessaire, recalcule la matrice de corrélation

    redindexNom = indexNomToRedindex(self,indexNom, indexesNoms)

    try:
        self.correlations[0][0]
    except:
        prox_matrices(self,indexesNoms, indexesVars)

    # Création des noeuds
    for j in range(len(indexesNoms)):
        indexj = indexesNoms[j]
        nomj = self.noms[indexj]
        # if i>j :
        if Pourcent >= (10 - self.correlations[redindexNom][j]) * 10 >= pourcent:
            Gr.add_node(nomj)
            try:
                date = int(self.data[indexj][0])
            except:
                date = indexj
            Gr.nodes[nomj]['annee'] = date
            Gr.nodes[nomj]['cor'] = self.correlations[redindexNom][j]
            sources.append(nomj)
            if date > dateMax:
                dateMax = date
            if date < dateMin:
                dateMin = date

    try:
        dy = 10 / (dateMax - dateMin)
    except:
        dy = 1

    # dictionnaire des positions
    # et attribution de leur position aux noeuds et aux labels

    # position du noeud et du label de la réf. sélectionnée
    pos = {}
    labels_pos = {}
    labels = {}
    pos[nom] = (x0, y0)
    labels[nom] = nom
    labels_pos[nom] = (x0 + .1, y0 + .1)

    # la distance verticale au nœud est conservée
    def prox1(node0, node, dx, dy):
        x0 = node0['pos'][0]
        y0 = node0['pos'][1]
        d = node0['annee'] - node['annee']
        c = node['cor']
        t = np.pi / 2 * c / 10
        return (x0 + d * np.tan(t), y0 - dy * d)

    # la distance au nœud est conservée
    def prox2(node0, node, dx, dy):
        x0 = node0['pos'][0]
        y0 = node0['pos'][1]
        d = node['annee'] - node0['annee']
        c = node['cor']
        if d < 0:
            t = np.pi / 2 * c / 10
            coord = (-d * np.sin(t), d * np.cos(t))
        else:
            t = np.pi / 2 * c / 10
            coord = (-d * np.sin(t), d * np.cos(t))
        return coord

    for n in sources:
        pos[n] = prox2(Gr.nodes[nom], Gr.nodes[n], 0, dy)
        Gr.nodes[n]['pos'] = pos[n]
        labels_pos[n] = (pos[n][0] + self.label_posX, pos[n][1] + self.label_posY)
        labels[n] = n

    cmap = cm = plt.get_cmap(self.colorMap)
    cNorm = colors.Normalize(vmin=0, vmax=10)
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cmap)

    for source in sources:
        j = self.noms.index(source)
        redindexj = indexesNoms.index(j)
        colorVal = scalarMap.to_rgba(self.correlations[redindexNom][redindexj])
        Gr.add_edge(nom, source, color=colorVal, label=self.correlations[redindexNom][redindexj])

    edge_colors = [Gr[u][v]['color'] for u, v in Gr.edges]
    nx.draw(Gr, pos, with_labels=False, node_color=self.node_color, node_size=self.node_size,
            edge_color=edge_colors, label_pos=.5)
    nx.draw_networkx_labels(Gr, labels_pos, labels, font_size=self.font_size, font_color=self.font_color)
    return plt


def show_graphe_deviation(self, indexNom,indexesNoms,indexesVars,
                          pourcent=0, Pourcent=100,
                          width='', height='',
                          font_size='', font_color='', node_color='',
                          label_posX='', label_posY=''):

    set_graphe(self,width, height, font_size, font_color, node_color, label_posX, label_posY)

    updateProxMatrices(self,indexesVars, indexesNoms)

    graphe_deviation(self,indexNom, indexesVars, indexesNoms, pourcent, Pourcent)
    plt.show()


def save_graphe_deviation(self, nom, vars=[], varSauf=[],
                          noms=[], nomSauf=[],
                          varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                          nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                          pourcent=0, Pourcent=100,
                          width='', height='',
                          font_size='', font_color='',
                          node_color='',
                          label_posX='', label_posY=''):
    indexNom = self.nomToIndex(nom)
    indexesNoms = getIndexesNoms(self,noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

    indexesNoms = sorted(list(set(indexesNoms) | set([indexNom])))
    indexesVars = getIndexesVars(self,vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

    set_graphe(self,width, height, font_size, font_color, node_color, label_posX, label_posY)
    updateProxMatrices(self,indexesVars, indexesNoms)

    graphe_deviation(self,indexNom, indexesVars, indexesNoms, pourcent, Pourcent)
    plt.savefig(nom + self.baseName + 'Prox.png', dpi=200)
    plt.show()


def show_graphes_deviation(self,indexesNoms,indexesVars,
                           pourcent=0, Pourcent=100):


    for n in indexesNoms:
        show_graphe_deviation(self,n, indexesNoms,indexesVars,
                                   pourcent, Pourcent)


def save_graphes_deviation(self,indexesNoms,indexesVars,
                           pourcent=0, Pourcent=100):

    for n in indexesNoms:
        save_graphe_deviation(self,indexNom,indexesNoms,indexesVars,
                                   pourcent, Pourcent)
        prc = 0


    return prc
