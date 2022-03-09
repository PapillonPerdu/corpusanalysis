from ipywidgets import *


#########################################################
#### Interactivité - fonctions communes
#########################################################
# entrée : "a,b"
# sortie : [a,b]
# les blancs au début des éléments sont supprimés
def strToList(strList):
    L = strList.split(',')
    L = list(map(str.strip, L))
    return L


# entrée : "a,b;c,d;e,f"
# sortie : [[a,b],[c,d],[e,f]]
# les blancs sont supprimés de l'entrée
def strListToLists(strList):
    strList.replace(' ', '')
    L = strList.split(';')
    res = []
    for l in L:
        res.append(l.split(','))
    return res


titre_layout = Layout(
    display='flex',
    flex_flow='row',
    justify_content='space-around'
)

sous_titres_layout = Layout(
    display='flex',
    flex_flow='row',
    justify_content='space-around'
)

formule_layout = Layout(
    display='flex',
    flex_flow='row',
    justify_content='center'
)

textArea_layout = Layout(
    flex='0 1 auto', height='30px', width='auto'
)

textAreaFormule_layout = Layout(
    flex='0 1 auto', height='30px', width='400px'
)

nomsDonnes_layout = Layout(flex='0 1 auto', height='40px', width='400px')


class Correlations:
    '''Classe pour l'analyse d'un tableau de variables

    :fileIn : nom du fichier csv contenant les données
    :baseName : chaîne qui sera ajoutée aux noms des données dans les sorties

    Propriétés :
    data : affiche le tableau des données
    poids : affiche les poids
    noms : affiche les noms
    vars : affiche les variables
    card : affiche le nombre d'entrées
    distMax : affiche la distance maximale possible
    distance_matrice : affiche la matrice des distances. Cette matrice mesure l'éloignement des données.
    proximite_matrice : affiche la matrice des proximités. Cette matrice mesure la proximité des données.
    distance_matrice_csv : enregistre la matrice des distances dans un fichier csv
    proximite_matrice_csv : enregistre la matrice des proximités dans un fichier csv
    distance_matrice_coordonnees : affiche les coordons le plan des données à partir de leurs distances
    proximite_matrice_coordonnees : affiche les coordonnées dans le plan des données à partir de leurs proximité
    graphe_distance_show : affiche le graphe à partir de la matrice des distances
    graphe_distance_save : enregistre le graphe à partir de la matrice des distances
    graphe_proximite_show: affiche le graphe à partir de la matrice de proximité
    graphe_proximite_save : enregistre le graphe à partir de la matrice de proximité
    find : liste des noms ayant pour le critère j la valeur donnée
    contains : liste des noms ayant contenant pour le critère j la chaîne donnée
    like : listes des noms ayant pour le critère j la même valeur que celle du nom donné
     '''

    def __init__(self,
                 fileIn, baseName='',
                 varsTypes=[], varsDefs=[],
                 nomsTypes=[], varsNoms=[],
                 varsTypesRegles='', nomsTypesRegles='', nomsDefs=[]):
        self.__baseName = baseName
        # Pour que les lignes des tableaux ne soient pas tronquées
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_colwidth', -1)
        np.set_printoptions(threshold=sys.maxsize)

        if type(fileIn) == str: fileIn = [fileIn]

        frames = []
        noms = []
        variables = []
        poids = []
        for f in fileIn:
            try:
                ar = np.array(pd.read_csv(open(f, encoding="UTF-8"), delimiter=","))
            except:
                print("Impossible d\'ouvrir le fichier \"" + f + "\"")
                sys.exit(1)

            # Suppression des colonnes (resp. lignes) dont le nom est vide
            j = 1
            while j < np.size(ar, 1):
                if str(ar[1, j]) == 'nan':
                    ar = np.delete(ar, j, 1)
                else:
                    j += 1
            i = 2
            while i < np.size(ar, 0):
                if str(ar[i, 0]) == 'nan':
                    ar = np.delete(ar, i, 0)
                else:
                    i += 1

            if not len(frames):
                noms = ar[2:, 0].tolist()

            variables += ar[1, 1:].tolist()
            poids += ar[0, 1:].tolist()
            frames.append(pd.DataFrame(ar[2:, 1:]).replace(np.nan, ''))

        self.__array = pd.concat(frames, axis=1, join='inner')
        data = np.array(self.__array)

        variables = [str(x) for x in variables]
        self.__vars = variables
        self.__selectedVars = variables
        self.__selectedIndexesVars = [i for i in range(len(self.__selectedVars))]

        # initialisation des types de variables
        if varsTypes: self.set_vars_types(varsTypes, varsTypesRegles=varsTypesRegles)

        # initialisation des définitions des variables
        if varsDefs:
            self.set_vars_defs(varsDefs)
        else:
            self.__vars_augmented = self.__vars

        try:
            poids = list(map(int, poids))
        except:
            poids = [1] * (len(variables))
        self.__poids = poids
        self.__selectedPoids = poids

        noms = [str(x) for x in noms]
        self.__noms = noms
        self.__selectedNoms = noms
        self.__selectedIndexesNoms = [i for i in range(len(self.__selectedNoms))]

        # initialisation des définitions des noms
        if nomsDefs:
            self.set_noms_defs(nomsDefs)
        else:
            self.__noms_augmented = self.__noms

        # initialisation des types de noms
        if nomsTypes: self.set_noms_types(nomsTypes, nomsTypesRegles=nomsTypesRegles)

        self.__data = data
        self.__selectedData = data

        self.__card = len(self.__data)
        self.__selectedCard = len(self.__selectedData)
        self.__selectedVarsCard = len(self.__selectedVars)
        self.__distMax = sum(self.__poids)
        self.__selectedDistMax = sum(self.__selectedPoids)

        self.__exclus = ['', '*', '?', '#']
        self.__coches = ['*', '#', '-']
        self.__logicalOperatorsBinary = ['|', '&']
        self.__logicalOperatorsUnary = ['~']
        self.__logicalOperators = self.__logicalOperatorsBinary + self.__logicalOperatorsUnary

        # self.prox_matrices(indexesVars=self.__selectedIndexesVars,indexesNoms=self.__selectedIndexesNoms)

        mds = manifold.MDS(n_components=2, dissimilarity="precomputed", random_state=6)

        # paramètres graphes de déviation
        self.__colorMap = 'gist_heat'
        self.__font_size = 14
        self.__font_color = 'black'
        self.__font_weight = 'normal'
        self.__node_color = 'black'
        self.__node_size = 20
        self.__graph_width = 20
        self.__graph_height = 20
        self.__label_posX = .1
        self.__label_posY = .1

        # paramètres graphes matrice de coordonnées
        self.__gmc_font_size = 10
        self.__gmc_font_color = 'black'
        self.__gmc_node_size = 5
        self.__gmc_node_color = 'black'
        self.__gmc_label_pos = .5
        self.__gmc_width = 20
        self.__gmc_height = 20
        self.__gmc_label_posX = .1
        self.__gmc_label_posY = .1

    #########################################################
    #### Interactivité - fonctions communes
    #########################################################

    # Form Noms
    def form_nom(self, inom):

        form_nom_items = [
            Box([inom],
                layout=titre_layout)
        ]

        form_nom = Box(form_nom_items, layout=Layout(
            display='flex',
            flex_flow='column',
            align_items='stretch'
        ))
        display(form_nom)

    # Form Noms
    def form_noms(self, inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf):

        noms_sub_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-around',
            align_items='stretch'
        )

        nomsTypes_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-around',
            align_items='stretch'
        )

        form_noms_sub_items = [
            Box([Label(value='sélectionnés'), Label(value='exclus')],
                layout=sous_titres_layout),
            Box([inoms, inomSauf], layout=noms_sub_layout)
        ]

        form_noms_sub = Box(form_noms_sub_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 1px',
            justify_content='space-around',
            align_items='stretch',
            width='98%'
        ))

        form_nomsTypes_items = [
            Box([Label(value='Types')],
                layout=titre_layout),
            Box([Label(value='sélectionnés'), Label(value='exclus')],
                layout=sous_titres_layout),
            Box([inomsTypes, inomsTypeSauf],
                layout=nomsTypes_layout),
            Box([Label(value='Formule :'), inomsTypesFormule],
                layout=formule_layout)
        ]

        # nomsTypesExist=len(cor.noms_types_types)!=0
        # visibility=nomsTypesExist,

        form_nomsTypes = Box(form_nomsTypes_items, layout=Layout(
            display='none',
            flex_flow='column',
            border='solid 1px',
            justify_content='space-around',
            align_items='center',
            width='98%'
        ))

        form_noms_items = [
            Box([Label(value='Noms')],
                layout=titre_layout),
            form_noms_sub,
            form_nomsTypes
        ]

        form_noms = Box(form_noms_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 2px',
            justify_content='space-around',
            align_items='center',
            width='100%',
            padding='5px',
            margin='5px'
        ))
        display(form_noms)

    # Form Variables
    def form_vars(self, ivarsTypesFormule,
                  ivarsTypes, ivarsTypeSauf, ivars, ivarSauf):
        vars_sub_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-around'
        )

        varsTypes_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-around'
        )

        form_vars_sub_items = [
            Box([Label(value='sélectionnées'), Label(value='exclues')], layout=sous_titres_layout),
            Box([ivars, ivarSauf], layout=vars_sub_layout)
        ]

        form_vars_sub = Box(form_vars_sub_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 1px',
            justify_content='space-around',
            align_items='stretch',
            padding='5px',
            margin='5px',
            width='98%'

        ))

        form_varsTypes_items = [
            Box([Label(value='Types')],
                layout=titre_layout),
            Box([Label(value='sélectionnés'), Label(value='exclus')],
                layout=sous_titres_layout),
            Box([ivarsTypes, ivarsTypeSauf],
                layout=varsTypes_layout),
            Box([Label(value='Formule :'), ivarsTypesFormule],
                layout=formule_layout)
        ]

        try:
            self.__vars_types_types
            disp = 'flex'
        except:
            disp = 'none'

        form_varsTypes = Box(form_varsTypes_items, layout=Layout(
            display=disp,
            flex_flow='column',
            border='solid 1px',
            justify_content='space-around',
            align_items='stretch',
            width='98%',
            margin='5px',
            padding='5px'
        ))

        form_vars_items = [
            Box([Label(value='Variables')],
                layout=titre_layout),
            form_vars_sub,
            form_varsTypes
        ]

        form_vars = Box(form_vars_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 2px',
            justify_content='space-around',
            align_items='center',
            width='100%',
            padding='5px'
        ))

        display(form_vars)

    # Form pour les types en sortie
    def form_varsTypeSortie(self,
                            ivarsTypeSortie, ivarsTypeSortieSauf):

        varsTypeSortie_sub_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-around',
            justify_items='center'
        )

        form_varsTypeSortie_sub_items = [
            Box([Label(value='sélectionnés'), Label(value='exclus')],
                layout=sous_titres_layout),
            Box([ivarsTypeSortie, ivarsTypeSortieSauf],
                layout=varsTypeSortie_sub_layout)
        ]

        form_varsTypeSortie_sub = Box(form_varsTypeSortie_sub_items, layout=Layout(
            display='flex',
            flex_flow='column',
            align_items='stretch',
            width='98%'
        ))

        form_varsTypeSortie_items = [
            Box([Label(value='Types en sortie')],
                layout=titre_layout),
            form_varsTypeSortie_sub
        ]

        form_varsTypeSortie = Box(form_varsTypeSortie_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 2px',
            justify_content='space-around',
            align_items='stretch',
            width='100%'
        ))
        display(form_varsTypeSortie)

    # Form pour le lexique
    def form_mots(self,
                  imots, imotSauf, iidentifications, iminmax, ifrequences):

        identifications_layout = Layout(
            display='flex',
            height='120px',
            width='600px',
            justify_content="space-around",
            align_content='space-around',
            justify_items='center')

        mots_sub_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-around',
            justify_items='center'
        )

        form_mots_sub_items = [
            Box([Label(value='forcés'), Label(value='exclus')],
                layout=sous_titres_layout),
            Box([imots, imotSauf],
                layout=mots_sub_layout),

            Box([Label(value='identifications')],
                layout=sous_titres_layout),
            Box([Label(value='Chaque ligne contient les mots identifiés séparés par des virgules.')],
                layout=sous_titres_layout),
            Box([iidentifications],
                layout=identifications_layout),

            Box([Label(value='longueurs'), Label(value='fréquences')],
                layout=sous_titres_layout),
            Box([iminmax, ifrequences],
                layout=mots_sub_layout),

        ]

        form_mots_sub = Box(form_mots_sub_items, layout=Layout(
            display='flex',
            flex_flow='column',
            justify_content='space-around',
            align_items='stretch',
            width='98%'
        ))

        form_mots_items = [
            Box([Label(value='Mots')],
                layout=titre_layout),
            form_mots_sub
        ]

        form_mots = Box(form_mots_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 2px',
            justify_content='space-around',
            align_items='center',
            width='100%'
        ))
        display(form_mots)

    # Form deux noms
    def form_2noms(self, inom1, inom2):

        Twonoms_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-around'
        )

        form_2noms_items = [
            Box([inom1, inom2], layout=Twonoms_layout)
        ]

        form_2noms = Box(form_2noms_items, layout=Layout(
            display='flex',
            flex_flow='column',
            align_items='stretch',
            width='100%'
        ))
        display(form_2noms)

    # Form pourcents
    def form_pourcents(self, ipourcents):

        pourcents_sub_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-around'
        )

        form_pourcents_sub_items = [
            Box([ipourcents], layout=pourcents_sub_layout)
        ]

        form_pourcents_sub = Box(form_pourcents_sub_items, layout=Layout(
            display='flex',
            flex_flow='column',
            align_items='center',
            width='98%'
        ))

        form_pourcents_items = [
            Box([Label(value='Pourcents')],
                layout=titre_layout),
            form_pourcents_sub
        ]

        form_pourcents = Box(form_pourcents_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 2px',
            align_items='center',
            width='100%',
            padding='5px'
        ))
        display(form_pourcents)

    # Form effectif
    def form_effectif(self, ieffectif):

        effectif_sub_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-around'
        )

        form_effectif_sub_items = [
            Box([ieffectif], layout=effectif_sub_layout)
        ]

        form_effectif_sub = Box(form_effectif_sub_items, layout=Layout(
            display='flex',
            flex_flow='column',
            align_items='center',
            width='98%'
        ))

        form_effectif_items = [
            Box([Label(value='Effectifs')],
                layout=titre_layout),
            form_effectif_sub
        ]

        form_effectif = Box(form_effectif_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 2px',
            align_items='center',
            width='100%',
            padding='5px'
        ))
        display(form_effectif)

    # Form ordre
    def form_ordre(self, iordre, ireverse):

        ordre_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='center',
            align_items='center',
            width='350px',
            padding='5px')

        form_ordre_items = [
            Box([iordre, ireverse],
                layout=ordre_layout),

        ]

        form_ordre = Box(form_ordre_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 2px',
            align_items='center',
            width='100%',
            padding='5px'
        ))
        display(form_ordre)

        # Form Graphe

    def form_graph(self, iwidth, iheight,
                   ifont_size, ifont_color, inode_color,
                   ilabel_posX, ilabel_posY):

        graph_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-around'
        )

        form_graph_items = [
            Box([Label(value='Apparence du graphe')],
                layout=titre_layout),
            Box([Label(value='largeur'), Label(value='hauteur')],
                layout=sous_titres_layout),
            Box([iwidth, iheight],
                layout=graph_layout),
            Box([Label(value='taille police'), Label(value='couleur police')],
                layout=sous_titres_layout),
            Box([ifont_size, ifont_color],
                layout=graph_layout),
            Box([Label(value='couleur nœud'), Label(value='label x'), Label(value='label y')],
                layout=sous_titres_layout),
            Box([inode_color, ilabel_posX, ilabel_posY],
                layout=graph_layout),
        ]

        form_graph = Box(form_graph_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 2px',
            justify_content='space-around',
            align_items='stretch',
            width='100%',
            padding='5px'
        ))
        display(form_graph)

    # Form pour le motif de distribution
    def form_motif(self, imotifs):

        motif_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-around'

        )

        langues = self.get_langues()
        form_motif_items = [Box([Label(value='Motif')], layout=titre_layout)]
        for lg in langues:
            form_motif_items.append(Box([Label(value=lg + ':'),
                                         imotifs['imotif_' + lg]], layout=motif_layout))

        form_motif = Box(form_motif_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 2px',
            justify_content='space-around',
            align_items='center',
            width='100%',
            padding='5px'
        ))
        display(form_motif)

        #########################################################

    #### Interactivité - variante des fonctions
    #########################################################

    def iiCorrelations(inomClass, istrFiles, istrVarsTypesFiles, istrNomsTypesFiles):
        if istrFiles:
            files = strToList(istrFiles)

            varsTypesFiles = ''
            if istrVarsTypesFiles:
                varsTypesFiles = strListToLists(istrVarsTypesFiles)

            nomsTypesFiles = ''
            if iNomsTypesFiles:
                nomsTypesFiles = strListToLists(istrNomsTypesFiles)

            if inomClass == '':
                nomClass = 'cor'
            else:
                nomClass = inomClass

            exec(nomClass + "=Correlations(files,varsTypes=varsTypesFiles,nomsTypes=nomsTypesFiles)")
            exec(nomClass + ".show_data()")

    def iCorrelations(self):
        istrFiles = widgets.Textarea(
            disabled=False)

        istrVarsTypesFiles = widgets.Textarea(
            disabled=False)
        istrNomsTypesFiles = widgets.Textarea(
            disabled=False)

        inomClass = widgets.Textarea(
            value='cor',
            disabled=False)

        init_sub_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-around'
        )

        nomClass_layout = Layout(
            display='flex',
            flex_flow='row',
            justify_content='center',
            align_items='center'
        )

        form_init_sub_items = [
            Box([Label('Fichiers des Tableaux de variables')],
                layout=sous_titres_layout),
            Box([istrFiles],
                layout=init_sub_layout),
            Box([Label('Fichiers des Types des Noms'),
                 Label('Fichiers des Types des Variables')],
                layout=sous_titres_layout),
            Box([istrVarsTypesFiles, istrNomsTypesFiles],
                layout=init_sub_layout),
            Box([Label('Nom de la classe : '), inomClass],
                layout=nomClass_layout),

        ]

        form_init_sub = Box(form_init_sub_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 2px',
            align_items='stretch',
            width='98%'
        ))

        form_effectif_items = [
            Box([Label(value='Initialisation')],
                layout=titre_layout),
            form_init_sub
        ]

        form_init = Box(form_init_items, layout=Layout(
            display='flex',
            flex_flow='column',
            border='solid 2px',
            align_items='stretch',
            width='100%'
        ))
        display(form_init)

        out = widgets.interactive_output(self.iiCorrelations,
                                         {'inomClass': inomClass, 'istrFiles': istrFiles,
                                          'istrVarsTypesFiles': istrVarsTypesFiles,
                                          'istrNomsTypesFiles': istrNomsTypesFiles})

        display(vbox4, out)

    def iishow_data(self, inoms='', inomSauf='',
                    ivars='', ivarSauf='',
                    ivarsTypes='', ivarsTypeSauf='',
                    ivarsTypesFormule='',
                    inomsTypes='', inomsTypeSauf='', inomsTypesFormule='',
                    ipasColonne=10, ipasLigne=10):

        if inoms:
            noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        vars = self.vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []

        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = ''

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = ''

        self.show_data(
            noms, nomSauf,
            vars, varSauf,
            varsTypes, varsTypeSauf,
            varsTypesFormule,
            nomsTypes=inomsTypes, nomsTypeSauf=inomsTypeSauf,
            nomsTypesFormule=inomsTypesFormule,
            pasColonne=10, pasLigne=10)

    def ishow_data(self):
        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        out = widgets.interactive_output(self.iishow_data,
                                         {'inoms': inoms, 'inomSauf': inomSauf,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf,
                                          'inomsTypesFormule': inomsTypesFormule,
                                          'inomsTypes': inomsTypes,
                                          'inomsTypeSauf': inomsTypeSauf,
                                          })

        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        try:
            display(out)
        except:
            print('Données incomplètes...')

    def iishow_data_pourcent(self, inom='', inoms='', inomSauf='',
                             ipourcents=(0, 0), ivars='', ivarSauf='',
                             ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                             inomsTypes='', inomsTypeSauf='', inomsTypesFormule='',
                             ipasColonne=10, ipasLigne=10):
        nom = inom
        if inoms:
            if inoms in ['avant', 'Avant']:
                noms = self.nomsAvant(nom)
            elif inoms in ['après', 'Après', 'apres', 'Apres']:
                noms = self.nomsApres(nom)
            else:
                noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        pourcent = ipourcents[0]
        Pourcent = ipourcents[1]
        vars = self.vars[ivars[0]:ivars[1]]

        vars = self.vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = ''

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = ''

        if inomsTypes:
            nomsTypes = strToList(inomsTypes)
        else:
            nomsTypes = ''

        if inomsTypeSauf:
            nomsTypeSauf = strToList(inomsTypeSauf)
        else:
            nomsTypeSauf = ''

        self.show_data_pourcent(nom,
                                noms=noms, nomSauf=nomSauf, pourcent=pourcent, Pourcent=Pourcent,
                                vars=vars, varSauf=varSauf,
                                varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                varsTypesFormule=ivarsTypesFormule,
                                nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                                nomsTypesFormule=inomsTypesFormule,
                                pasColonne=10, pasLigne=10)

    def ishow_data_pourcent(self):
        inom = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False,
        )
        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.vars)],
            min=0,
            max=len(self.vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ipourcents = widgets.IntRangeSlider(
            value=[0, 100],
            min=0,
            max=100,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        out = widgets.interactive_output(self.iishow_data_pourcent,
                                         {'inom': inom, 'inoms': inoms, 'inomSauf': inomSauf,
                                          'ipourcents': ipourcents,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf})

        self.form_nom(inom)
        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_pourcents(ipourcents)
        display(out)

    def iishow_data_only(self, inom='', inoms='', inomSauf='',
                         ivars='', ivarSauf='',
                         ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                         inomsTypes='', inomsTypeSauf='', inomsTypesFormule='',
                         ipasColonne=10, ipasLigne=10):
        nom = inom
        if inoms:
            if inoms in ['avant', 'Avant']:
                noms = self.nomsAvant(nom)
            elif inoms in ['après', 'Après', 'apres', 'Apres']:
                noms = self.nomsApres(nom)
            else:
                noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = ''

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = []

        if inomsTypes:
            nomsTypes = strToList(inomsTypes)
        else:
            nomsTypes = []

        if inomsTypeSauf:
            nomsTypeSauf = strToList(inomsTypeSauf)
        else:
            nomsTypeSauf = []

        self.show_data_only(nom,
                            noms=noms, nomSauf=nomSauf,
                            vars=vars, varSauf=varSauf,
                            varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                            varsTypesFormule=ivarsTypesFormule,
                            nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                            nomsTypesFormule=inomsTypesFormule)

    def ishow_data_only(self):

        inom = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False,
        )
        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        out = widgets.interactive_output(self.iishow_data_only,
                                         {'inom': inom, 'inoms': inoms, 'inomSauf': inomSauf,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf})

        self.form_nom(inom)
        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        display(out)

    def iishow_commun(self, inom1='', inom2='',
                      ivars='', ivarSauf='',
                      ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule=''):
        nom1 = inom1
        nom2 = inom2

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = []

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = []

        self.show_commun(nom1, nom2,
                         vars=vars, varSauf=varSauf,
                         varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                         varsTypesFormule=ivarsTypesFormule)

    def ishow_commun(self):

        inom1 = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False)

        inom2 = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[1],
            disabled=False
        )

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        out = widgets.interactive_output(self.iishow_commun,
                                         {'inom1': inom1, 'inom2': inom2,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf})

        self.form_2noms(inom1, inom2)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        display(out)

    def iishow_commun_types(self, inom1='', inom2='',
                            ivars='', ivarSauf='',
                            ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                            ivarsTypeSortie='', ivarsTypeSortieSauf='',
                            ieffectif=(0, 0)):

        nom1 = inom1
        nom2 = inom2

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = []

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = []

        if ivarsTypeSortie:
            varsTypeSortie = strToList(ivarsTypeSortie)
        else:
            varsTypeSortie = []

        if ivarsTypeSortieSauf:
            varsTypeSortieSauf = strToList(ivarsTypeSortieSauf)
        else:
            varsTypeSortieSauf = []

        effectif = ieffectif[0]
        Effectif = ieffectif[1]

        self.show_commun_types(nom1, nom2,
                               vars=vars, varSauf=varSauf,
                               varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                               varsTypesFormule=ivarsTypesFormule,
                               varsTypeSortie=varsTypeSortie,
                               varsTypeSortieSauf=varsTypeSortieSauf,
                               effectif=effectif, Effectif=Effectif)

    def ishow_commun_types(self):

        inom1 = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False)

        inom2 = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[1],
            disabled=False
        )

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ieffectif = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ivarsTypeSortie = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSortieSauf = widgets.Textarea(layout=textArea_layout)

        # sortie
        out = widgets.interactive_output(self.iishow_commun_types,
                                         {'inom1': inom1, 'inom2': inom2,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf,
                                          'ivarsTypeSortie': ivarsTypeSortie,
                                          'ivarsTypeSortieSauf': ivarsTypeSortieSauf,
                                          'ieffectif': ieffectif})

        self.form_2noms(inom1, inom2)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_effectif(ieffectif)
        self.form_varsTypeSortie(ivarsTypeSortie, ivarsTypeSortieSauf)
        display(out)

    def iishow_difference(self, inom1='', inom2='',
                          ivars='', ivarSauf='',
                          ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule=''):
        nom1 = inom1
        nom2 = inom2

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = []

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = []

        self.show_difference(nom1, nom2,
                             vars=vars, varSauf=varSauf,
                             varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                             varsTypesFormule=ivarsTypesFormule)

    def ishow_difference(self):

        inom1 = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False)

        inom2 = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[1],
            disabled=False
        )

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        out = widgets.interactive_output(self.iishow_difference,
                                         {'inom1': inom1, 'inom2': inom2,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf})

        self.form_2noms(inom1, inom2)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        display(out)

    def iishow_difference_types(self, inom1='', inom2='',
                                ivars='', ivarSauf='',
                                ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                                ivarsTypeSortie='', ivarsTypeSortieSauf='',
                                ieffectif=(0, 0)):

        nom1 = inom1
        nom2 = inom2

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = []

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = []

        if ivarsTypeSortie:
            varsTypeSortie = strToList(ivarsTypeSortie)
        else:
            varsTypeSortie = []

        if ivarsTypeSortieSauf:
            varsTypeSortieSauf = strToList(ivarsTypeSortieSauf)
        else:
            varsTypeSortieSauf = []

        effectif = ieffectif[0]
        Effectif = ieffectif[1]

        self.show_difference_types(nom1, nom2,
                                   vars=vars, varSauf=varSauf,
                                   varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                   varsTypesFormule=ivarsTypesFormule,
                                   varsTypeSortie=varsTypeSortie,
                                   varsTypeSortieSauf=varsTypeSortieSauf,
                                   effectif=effectif, Effectif=Effectif)

    def ishow_difference_types(self):

        inom1 = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False)

        inom2 = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[1],
            disabled=False
        )

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ieffectif = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ivarsTypeSortie = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSortieSauf = widgets.Textarea(layout=textArea_layout)

        # sortie
        out = widgets.interactive_output(self.iishow_difference_types,
                                         {'inom1': inom1, 'inom2': inom2,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf,
                                          'ivarsTypeSortie': ivarsTypeSortie,
                                          'ivarsTypeSortieSauf': ivarsTypeSortieSauf,
                                          'ieffectif': ieffectif})

        self.form_2noms(inom1, inom2)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_effectif(ieffectif)
        self.form_varsTypeSortie(ivarsTypeSortie, ivarsTypeSortieSauf)
        display(out)

    def iishow_tableau_correlations_desc(self, inom='', inoms='', inomSauf='',
                                         ipourcents=(0, 0), ivars='', ivarSauf='',
                                         ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                                         inomsTypes='', inomsTypeSauf='', inomsTypesFormule='',
                                         ipasColonne=10, ipasLigne=10):
        nom = inom
        if inoms:
            if inoms in ['avant', 'Avant']:
                noms = self.nomsAvant(nom)
            elif inoms in ['après', 'Après', 'apres', 'Apres']:
                noms = self.nomsApres(nom)
            else:
                noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        pourcent = ipourcents[0]
        Pourcent = ipourcents[1]
        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = ''

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = ''

        if inomsTypes:
            nomsTypes = strToList(inomsTypes)
        else:
            nomsTypes = ''

        if inomsTypeSauf:
            nomsTypeSauf = strToList(inomsTypeSauf)
        else:
            nomsTypeSauf = ''

        self.show_tableau_correlations_desc(nom,
                                            noms=noms, nomSauf=nomSauf, pourcent=pourcent, Pourcent=Pourcent,
                                            vars=vars, varSauf=varSauf,
                                            varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                            varsTypesFormule=ivarsTypesFormule,
                                            nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                                            nomsTypesFormule=inomsTypesFormule,
                                            pasColonne=10, pasLigne=10)

    def ishow_tableau_correlations_desc(self):
        inom = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False
        )
        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ipourcents = widgets.IntRangeSlider(
            value=[0, 100],
            min=0,
            max=100,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        out = widgets.interactive_output(self.iishow_tableau_correlations_desc,
                                         {'inom': inom, 'inoms': inoms, 'inomSauf': inomSauf,
                                          'ipourcents': ipourcents,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf})

        self.form_nom(inom)
        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_pourcents(ipourcents)
        display(out)

    def iishow_tableau_correlations_asc(self, inom='', inoms='', inomSauf='',
                                        ipourcents=(0, 0), ivars='', ivarSauf='',
                                        ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                                        inomsTypes='', inomsTypeSauf='', inomsTypesFormule='',
                                        ipasColonne=10, ipasLigne=10):
        nom = inom
        if inoms:
            if inoms in ['avant', 'Avant']:
                noms = self.nomsAvant(nom)
            elif inoms in ['après', 'Après', 'apres', 'Apres']:
                noms = self.nomsApres(nom)
            else:
                noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        pourcent = ipourcents[0]
        Pourcent = ipourcents[1]
        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = ''

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = ''

        if inomsTypes:
            nomsTypes = strToList(inomsTypes)
        else:
            nomsTypes = ''

        if inomsTypeSauf:
            nomsTypeSauf = strToList(inomsTypeSauf)
        else:
            nomsTypeSauf = ''

        self.show_tableau_correlations_asc(nom,
                                           noms=noms, nomSauf=nomSauf, pourcent=pourcent, Pourcent=Pourcent,
                                           vars=vars, varSauf=varSauf,
                                           varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                           varsTypesFormule=ivarsTypesFormule,
                                           nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                                           nomsTypesFormule=inomsTypesFormule,
                                           pasColonne=10, pasLigne=10)

    def ishow_tableau_correlations_asc(self):
        inom = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False
        )
        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ipourcents = widgets.IntRangeSlider(
            value=[0, 100],
            min=0,
            max=100,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        out = widgets.interactive_output(self.iishow_tableau_correlations_asc,
                                         {'inom': inom, 'inoms': inoms, 'inomSauf': inomSauf,
                                          'ipourcents': ipourcents,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf})

        self.form_nom(inom)
        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_pourcents(ipourcents)
        display(out)

    def iishow_tableau_correlations_types_desc(self, inom='', inoms='', inomSauf='',
                                               ipourcents=(0, 0), ieffectif=(0, 0), ivars='', ivarSauf='',
                                               ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                                               ivarsTypeSortie='', ivarsTypeSortieSauf='',
                                               inomsTypes='', inomsTypeSauf='', inomsTypesFormule='',
                                               ipasColonne=10, ipasLigne=10):

        nom = inom
        if inoms:
            if inoms in ['avant', 'Avant']:
                noms = self.nomsAvant(nom)
            elif inoms in ['après', 'Après', 'apres', 'Apres']:
                noms = self.nomsApres(nom)
            else:
                noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        pourcent = ipourcents[0]
        Pourcent = ipourcents[1]

        effectif = ieffectif[0]
        Effectif = ieffectif[1]

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = ''

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = ''

        if ivarsTypeSortie:
            varsTypeSortie = strToList(ivarsTypeSortie)
        else:
            varsTypeSortie = ''

        if ivarsTypeSortieSauf:
            varsTypeSortieSauf = strToList(ivarsTypeSortieSauf)
        else:
            varsTypeSortieSauf = ''

        if inomsTypes:
            nomsTypes = strToList(inomsTypes)
        else:
            nomsTypes = ''

        if inomsTypeSauf:
            nomsTypeSauf = strToList(inomsTypeSauf)
        else:
            nomsTypeSauf = ''

        self.show_tableau_correlations_types_desc(nom,
                                                  noms=noms, nomSauf=nomSauf, pourcent=pourcent, Pourcent=Pourcent,
                                                  effectif=effectif, Effectif=Effectif,
                                                  vars=vars, varSauf=varSauf,
                                                  varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                                  varsTypesFormule=ivarsTypesFormule,
                                                  varsTypeSortie=varsTypeSortie, varsTypeSortieSauf=varsTypeSortieSauf,
                                                  nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                                                  nomsTypesFormule=inomsTypesFormule)

    def ishow_tableau_correlations_types_desc(self):
        inom = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False
        )
        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSortie = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSortieSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ieffectif = widgets.IntRangeSlider(
            value=[0, len(self.__noms)],
            min=0,
            max=len(self.__noms),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ipourcents = widgets.IntRangeSlider(
            value=[0, 100],
            min=0,
            max=100,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        out = widgets.interactive_output(self.iishow_tableau_correlations_types_desc,
                                         {'inom': inom, 'inoms': inoms, 'inomSauf': inomSauf,
                                          'ipourcents': ipourcents,
                                          'ieffectif': ieffectif,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf,
                                          'ivarsTypeSortie': ivarsTypeSortie,
                                          'ivarsTypeSortieSauf': ivarsTypeSortieSauf})

        self.form_nom(inom)
        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_pourcents(ipourcents)
        self.form_effectif(ieffectif)
        self.form_varsTypeSortie(ivarsTypeSortie, ivarsTypeSortieSauf)
        display(out)

    def iishow_tableau_correlations_types_asc(self, inom='', inoms='', inomSauf='',
                                              ipourcents=(0, 0), ieffectif=(0, 0), ivars='', ivarSauf='',
                                              ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                                              ivarsTypeSortie='', ivarsTypeSortieSauf='',
                                              inomsTypes='', inomsTypeSauf='', inomsTypesFormule='',
                                              ipasColonne=10, ipasLigne=10):

        nom = inom
        if inoms:
            if inoms in ['avant', 'Avant']:
                noms = self.nomsAvant(nom)
            elif inoms in ['après', 'Après', 'apres', 'Apres']:
                noms = self.nomsApres(nom)
            else:
                noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        pourcent = ipourcents[0]
        Pourcent = ipourcents[1]

        effectif = ieffectif[0]
        Effectif = ieffectif[1]

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = ''

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = ''

        if ivarsTypeSortie:
            varsTypeSortie = strToList(ivarsTypeSortie)
        else:
            varsTypeSortie = ''

        if ivarsTypeSortieSauf:
            varsTypeSortieSauf = strToList(ivarsTypeSortieSauf)
        else:
            varsTypeSortieSauf = ''

        if inomsTypes:
            nomsTypes = strToList(inomsTypes)
        else:
            nomsTypes = ''

        if inomsTypeSauf:
            nomsTypeSauf = strToList(inomsTypeSauf)
        else:
            nomsTypeSauf = ''

        self.show_tableau_correlations_types_asc(nom,
                                                 noms=noms, nomSauf=nomSauf, pourcent=pourcent, Pourcent=Pourcent,
                                                 effectif=effectif, Effectif=Effectif,
                                                 vars=vars, varSauf=varSauf,
                                                 varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                                 varsTypesFormule=ivarsTypesFormule,
                                                 varsTypeSortie=varsTypeSortie, varsTypeSortieSauf=varsTypeSortieSauf,
                                                 nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                                                 nomsTypesFormule=inomsTypesFormule)

    def ishow_tableau_correlations_types_asc(self):
        inom = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False
        )
        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSortie = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSortieSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ieffectif = widgets.IntRangeSlider(
            value=[0, len(self.__noms)],
            min=0,
            max=len(self.__noms),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ipourcents = widgets.IntRangeSlider(
            value=[0, 100],
            min=0,
            max=100,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        out = widgets.interactive_output(self.iishow_tableau_correlations_types_asc,
                                         {'inom': inom, 'inoms': inoms, 'inomSauf': inomSauf,
                                          'ipourcents': ipourcents,
                                          'ieffectif': ieffectif,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf,
                                          'ivarsTypeSortie': ivarsTypeSortie,
                                          'ivarsTypeSortieSauf': ivarsTypeSortieSauf})

        self.form_nom(inom)
        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_pourcents(ipourcents)
        self.form_effectif(ieffectif)
        self.form_varsTypeSortie(ivarsTypeSortie, ivarsTypeSortieSauf)
        display(out)

    def iishow_tableau_correlations_types_pourcent_desc(self, inom='', inoms='', inomSauf='',
                                                        ipourcents=(0, 0), ieffectif=(0, 0), ivars='', ivarSauf='',
                                                        ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                                                        ivarsTypeSortie='', ivarsTypeSortieSauf='',
                                                        inomsTypes='', inomsTypeSauf='', inomsTypesFormule='',
                                                        ipasColonne=10, ipasLigne=10):

        nom = inom
        if inoms:
            if inoms in ['avant', 'Avant']:
                noms = self.nomsAvant(nom)
            elif inoms in ['après', 'Après', 'apres', 'Apres']:
                noms = self.nomsApres(nom)
            else:
                noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        pourcent = ipourcents[0]
        Pourcent = ipourcents[1]

        effectif = ieffectif[0]
        Effectif = ieffectif[1]

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []

        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = []

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = []

        if ivarsTypeSortie:
            varsTypeSortie = strToList(ivarsTypeSortie)
        else:
            varsTypeSortie = []

        if ivarsTypeSortieSauf:
            varsTypeSortieSauf = strToList(ivarsTypeSortieSauf)
        else:
            varsTypeSortieSauf = []

        if inomsTypes:
            nomsTypes = strToList(inomsTypes)
        else:
            nomsTypes = []

        if inomsTypeSauf:
            nomsTypeSauf = strToList(inomsTypeSauf)
        else:
            nomsTypeSauf = []

        nomsTypesFormule = inomsTypesFormule

        self.show_tableau_correlations_types_pourcent_desc(nom,
                                                           noms=noms, nomSauf=nomSauf, pourcent=pourcent,
                                                           Pourcent=Pourcent,
                                                           effectif=effectif, Effectif=Effectif,
                                                           vars=vars, varSauf=varSauf,
                                                           varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                                           varsTypesFormule=varsTypesFormule,
                                                           varsTypeSortie=varsTypeSortie,
                                                           varsTypeSortieSauf=varsTypeSortieSauf,
                                                           nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                                                           nomsTypesFormule=nomsTypesFormule)

    def ishow_tableau_correlations_types_pourcent_desc(self):
        inom = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False
        )
        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSortie = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSortieSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ieffectif = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ipourcents = widgets.IntRangeSlider(
            value=[0, 100],
            min=0,
            max=100,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        out = widgets.interactive_output(self.iishow_tableau_correlations_types_pourcent_desc,
                                         {'inom': inom, 'inoms': inoms, 'inomSauf': inomSauf,
                                          'ipourcents': ipourcents,
                                          'ieffectif': ieffectif,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf,
                                          'ivarsTypeSortie': ivarsTypeSortie,
                                          'ivarsTypeSortieSauf': ivarsTypeSortieSauf})

        self.form_nom(inom)
        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_pourcents(ipourcents)
        self.form_effectif(ieffectif)
        self.form_varsTypeSortie(ivarsTypeSortie, ivarsTypeSortieSauf)
        display(out)

    def iishow_tableau_innove(self, inomsDonnes, inoms='', inomSauf='',
                              ivars='', ivarSauf='',
                              ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                              inomsTypes='', inomsTypeSauf='', inomsTypesFormule='',
                              ipasColonne=10, ipasLigne=10):

        nomsDonnes = strToList(inomsDonnes)
        if inoms:
            noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = ''

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = ''

        if inomsTypes:
            nomsTypes = strToList(inomsTypes)
        else:
            nomsTypes = ''

        if inomsTypeSauf:
            nomsTypeSauf = strToList(inomsTypeSauf)
        else:
            nomsTypeSauf = ''

        self.show_tableau_innove(nomsDonnes,
                                 noms=noms, nomSauf=nomSauf,
                                 vars=vars, varSauf=varSauf,
                                 varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                 varsTypesFormule=ivarsTypesFormule,
                                 nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                                 nomsTypesFormule=inomsTypesFormule)

    def ishow_tableau_innove(self):

        inomsDonnes = widgets.Textarea(description='Noms :',
                                       layout=nomsDonnes_layout)
        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ipourcents = widgets.IntRangeSlider(
            value=[0, 100],
            min=0,
            max=100,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        out = widgets.interactive_output(self.iishow_tableau_innove,
                                         {'inomsDonnes': inomsDonnes, 'inoms': inoms, 'inomSauf': inomSauf,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf})

        display(inomsDonnes)
        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        display(out)

    def iishow_tableau_innove_types(self, inomsDonnes='',
                                    ivars='', ivarSauf='',
                                    ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                                    ivarsTypeSortie='', ivarsTypeSortieSauf=''):

        nomsDonnes = strToList(inomsDonnes)

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = []

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = []

        if ivarsTypeSortie:
            varsTypeSortie = strToList(ivarsTypeSortie)
        else:
            varsTypeSortie = []

        if ivarsTypeSortieSauf:
            varsTypeSortieSauf = strToList(ivarsTypeSortieSauf)
        else:
            varsTypeSortieSauf = []

        self.show_tableau_innove_types(nomsDonnes,
                                       vars=vars, varSauf=varSauf,
                                       varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                       varsTypesFormule=ivarsTypesFormule,
                                       varsTypeSortie=varsTypeSortie,
                                       varsTypeSortieSauf=varsTypeSortieSauf)

    def ishow_tableau_innove_types(self):

        inomsDonnes = widgets.Textarea(description='Noms :', value=self.__noms[0],
                                       layout=nomsDonnes_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ieffectif = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ivarsTypeSortie = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSortieSauf = widgets.Textarea(layout=textArea_layout)

        # sortie
        out = widgets.interactive_output(self.iishow_tableau_innove_types,
                                         {'inomsDonnes': inomsDonnes,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf,
                                          'ivarsTypeSortie': ivarsTypeSortie,
                                          'ivarsTypeSortieSauf': ivarsTypeSortieSauf})

        display(inomsDonnes)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_effectif(ieffectif)
        self.form_varsTypeSortie(ivarsTypeSortie, ivarsTypeSortieSauf)
        display(out)

    def iishow_tableau_innove_types_pourcent(self, inomsDonnes='',
                                             inoms='', inomSauf='',
                                             ivars='', ivarSauf='',
                                             ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                                             ivarsTypeSortie='', ivarsTypeSortieSauf='',
                                             inomsTypes='', inomsTypeSauf='', inomsTypesFormule='',
                                             ieffectif=(0, 0),
                                             ipasColonne=10, ipasLigne=10):

        nomsDonnes = strToList(inomsDonnes)
        if inoms:
            noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = []

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = []

        if ivarsTypeSortie:
            varsTypeSortie = strToList(ivarsTypeSortie)
        else:
            varsTypeSortie = []

        if ivarsTypeSortieSauf:
            varsTypeSortieSauf = strToList(ivarsTypeSortieSauf)
        else:
            varsTypeSortieSauf = []

        effectif = ieffectif[0]
        Effectif = ieffectif[1]

        self.show_tableau_innove_types_pourcent(nomsDonnes,
                                                noms=noms, nomSauf=nomSauf,
                                                vars=vars, varSauf=varSauf,
                                                varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                                varsTypesFormule=ivarsTypesFormule,
                                                varsTypeSortie=varsTypeSortie,
                                                varsTypeSortieSauf=varsTypeSortieSauf,
                                                effectif=effectif, Effectif=Effectif)

    def ishow_tableau_innove_types_pourcent(self):

        inomsDonnes = widgets.Textarea(description='Noms :', value=self.__noms[0],
                                       layout=nomsDonnes_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ieffectif = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ivarsTypeSortie = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSortieSauf = widgets.Textarea(layout=textArea_layout)

        # sortie
        out = widgets.interactive_output(self.iishow_tableau_innove_types_pourcent,
                                         {'inomsDonnes': inomsDonnes,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf,
                                          'ivarsTypeSortie': ivarsTypeSortie,
                                          'ivarsTypeSortieSauf': ivarsTypeSortieSauf,
                                          'ieffectif': ieffectif})

        display(inomsDonnes)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_effectif(ieffectif)
        self.form_varsTypeSortie(ivarsTypeSortie, ivarsTypeSortieSauf)
        display(out)

    def iishow_graphe_deviation(self, inom='', inoms='', inomSauf='',
                                ipourcents=(0, 0), ivars='', ivarSauf='',
                                ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                                inomsTypes='', inomsTypeSauf='', inomsTypesFormule='',
                                iwidth='', iheight='',
                                ifont_size='', ifont_color='', inode_color='',
                                ilabel_posX='', ilabel_posY=''):
        nom = inom
        if inoms:
            if inoms in ['avant', 'Avant']:
                noms = self.nomsAvant(nom)
            elif inoms in ['après', 'Après', 'apres', 'Apres']:
                noms = self.nomsApres(nom)
            else:
                noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        pourcent = ipourcents[0]
        Pourcent = ipourcents[1]
        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = ''

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = ''

        if inomsTypes:
            nomsTypes = strToList(inomsTypes)
        else:
            nomsTypes = ''

        if inomsTypeSauf:
            nomsTypeSauf = strToList(inomsTypeSauf)
        else:
            nomsTypeSauf = ''

        if ifont_size:
            font_size = int(ifont_size)
        else:
            font_size = ''

        if ilabel_posX:
            label_posX = int(ilabel_posX)
        else:
            label_posX = ''

        if ilabel_posY:
            label_posY = int(ilabel_posY)
        else:
            label_posY = ''

        self.show_graphe_deviation(nom,
                                   noms=noms, nomSauf=nomSauf, pourcent=pourcent, Pourcent=Pourcent,
                                   vars=vars, varSauf=varSauf,
                                   varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                   varsTypesFormule=ivarsTypesFormule,
                                   nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                                   nomsTypesFormule=inomsTypesFormule,
                                   width=iwidth, height=iheight,
                                   font_size=font_size, font_color=ifont_color,
                                   node_color=inode_color,
                                   label_posX=label_posX, label_posY=label_posY)

    def ishow_graphe_deviation(self):
        inom = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False
        )
        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ipourcents = widgets.IntRangeSlider(
            value=[0, 100],
            min=0,
            max=100,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        iwidth = widgets.Textarea(layout=textArea_layout)
        iheight = widgets.Textarea(layout=textArea_layout)
        ifont_size = widgets.Textarea(layout=textArea_layout)
        ifont_color = widgets.Textarea(layout=textArea_layout)
        inode_color = widgets.Textarea(layout=textArea_layout)
        ilabel_posX = widgets.Textarea(layout=textArea_layout)
        ilabel_posY = widgets.Textarea(layout=textArea_layout)

        # sortie
        out = widgets.interactive_output(self.iishow_graphe_deviation,
                                         {'inom': inom, 'inoms': inoms, 'inomSauf': inomSauf,
                                          'ipourcents': ipourcents,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf,
                                          'iwidth': iwidth, 'iheight': iheight,
                                          'ifont_size': ifont_size, 'ifont_color': ifont_color,
                                          'inode_color': inode_color,
                                          'ilabel_posX': ilabel_posX, 'ilabel_posY': ilabel_posY})

        self.form_nom(inom)
        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_pourcents(ipourcents)
        self.form_graph(iwidth, iheight, ifont_size, ifont_color,
                        inode_color, ilabel_posX, ilabel_posY)
        display(out)

    def iishow_graphe_distance(self, iliens=True, inoms='', inomSauf='',
                               ivars='', ivarSauf='',
                               ivarsTypes='', ivarsTypeSauf='',
                               ivarsTypesFormule='',
                               inomsTypes='', inomsTypeSauf='',
                               inomsTypesFormule='',
                               pourcent=0, Pourcent=100, icouleursLiens=''):

        liens = iliens

        if inoms:
            noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = ''

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = ''

        if inomsTypes:
            nomsTypes = strToList(inomsTypes)
        else:
            nomsTypes = ''

        if inomsTypeSauf:
            nomsTypeSauf = strToList(inomsTypeSauf)
        else:
            nomsTypeSauf = ''

        couleursLiens = icouleursLiens

        self.show_graphe_distance(liens=liens,
                                  noms=noms, nomSauf=nomSauf,
                                  vars=vars, varSauf=varSauf,
                                  varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                  varsTypesFormule=ivarsTypesFormule,
                                  nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                                  nomsTypesFormule=inomsTypesFormule, couleursLiens=couleursLiens)

    def ishow_graphe_distance(self):

        sys.exit('EN COURS')
        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ipourcents = widgets.IntRangeSlider(
            value=[0, 100],
            min=0,
            max=100,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        iwidth = widgets.Textarea(layout=textArea_layout)
        iheight = widgets.Textarea(layout=textArea_layout)
        ifont_size = widgets.Textarea(layout=textArea_layout)
        ifont_color = widgets.Textarea(layout=textArea_layout)
        inode_color = widgets.Textarea(layout=textArea_layout)
        ilabel_posX = widgets.Textarea(layout=textArea_layout)
        ilabel_posY = widgets.Textarea(layout=textArea_layout)

        iliens = widgets.RadioButtons(
            description='liens',
            options=['avec', 'sans'],
            values=[True, False],
            layout={'width': 'max-content'}
        )
        icouleursLiens = widgets.Textarea(layout=textArea_layout)

        # sortie
        out = widgets.interactive_output(self.iishow_graphe_distance,
                                         {'iliens': iliens, 'inoms': inoms, 'inomSauf': inomSauf,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf,
                                          'icouleursLiens': icouleursLiens})

        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_pourcents(ipourcents)
        display(iliens)
        self.form_graph(iwidth, iheight, ifont_size, ifont_color,
                        inode_color, ilabel_posX, ilabel_posY)
        display(out)

    def iishow_like(self, inom='', inoms='', inomSauf='',
                    ipourcent=100, ivars='', ivarSauf='',
                    ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule='',
                    inomsTypes='', inomsTypeSauf='', inomsTypesFormule=''):

        nom = inom

        if inoms:
            if inoms in ['avant', 'Avant']:
                noms = self.nomsAvant(nom)
            elif inoms in ['après', 'Après', 'apres', 'Apres']:
                noms = self.nomsApres(nom)
            else:
                noms = strToList(inoms)
        else:
            noms = []
        nomSauf = strToList(inomSauf)

        pourcent = int(ipourcent)
        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = ''

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = ''

        if inomsTypes:
            nomsTypes = strToList(inomsTypes)
        else:
            nomsTypes = ''

        if inomsTypeSauf:
            nomsTypeSauf = strToList(inomsTypeSauf)
        else:
            nomsTypeSauf = ''

        nomsTypesFormule = inomsTypesFormule

        self.show_like(nom,
                       noms=noms, nomSauf=nomSauf, pourcent=pourcent,
                       vars=vars, varSauf=varSauf,
                       varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                       varsTypesFormule=varsTypesFormule,
                       nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                       nomsTypesFormule=nomsTypesFormule)

    def ishow_like(self):
        inom = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0],
            disabled=False
        )
        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        ipourcent = widgets.FloatSlider(
            value=0,
            min=0,
            max=100,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        out = widgets.interactive_output(self.iishow_like,
                                         {'inom': inom, 'inoms': inoms, 'inomSauf': inomSauf,
                                          'ipourcent': ipourcent,
                                          'ivars': ivars, 'ivarSauf': ivarSauf,
                                          'ivarsTypesFormule': ivarsTypesFormule,
                                          'ivarsTypes': ivarsTypes,
                                          'ivarsTypeSauf': ivarsTypeSauf,
                                          'inomsTypes': inomsTypes,
                                          'inomsTypeSauf': inomsTypeSauf,
                                          'inomsTypesFormule': inomsTypesFormule})

        self.form_nom(inom)
        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        self.form_pourcents(ipourcent)
        display(out)

    def iishow_lexique(self, inom, iidentifications='', imots='', imotSauf='', iminmax=(0, 0),
                       iordre='alpha', ireverse=False,
                       ifrequences=(0, 0),
                       ivars='', ivarSauf='',
                       ivarsTypes='', ivarsTypeSauf='', ivarsTypesFormule=''):

        nom = inom
        identifications = strListToLists(iidentifications.replace("\n", ";"))

        mots = list(map(str.strip, strToList(imots)))
        motSauf = list(map(str.strip, strToList(imotSauf)))

        min = iminmax[0]
        max = iminmax[1]

        ordre = iordre
        reverse = (ireverse == 'décroissant')

        minfreq = ifrequences[0]
        maxfreq = ifrequences[1]

        vars = self.__vars[ivars[0]:ivars[1]]

        if ivarSauf[0] != 0 and ivarSauf[1] != len(self.__vars):
            varSauf = self.__vars[ivarSauf[0]:ivarSauf[1]]
        else:
            varSauf = []
        varsTypesFormule = ivarsTypesFormule

        if ivarsTypes:
            varsTypes = strToList(ivarsTypes)
        else:
            varsTypes = ''

        if ivarsTypeSauf:
            varsTypeSauf = strToList(ivarsTypeSauf)
        else:
            varsTypeSauf = ''

        self.show_lexique(nom,
                          identifications=identifications, mots=mots, motSauf=motSauf,
                          min=min, max=max, ordre=ordre, reverse=reverse,
                          minfreq=minfreq, maxfreq=maxfreq,
                          vars=vars, varSauf=varSauf,
                          varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                          varsTypesFormule=ivarsTypesFormule)

    def ishow_lexique(self):
        inom = widgets.Dropdown(
            options=self.__noms,
            value=self.__noms[0]
        )
        imots = widgets.Textarea(layout=Layout(width='45%', height='40px'))
        imotSauf = widgets.Textarea(layout=Layout(width='45%', height='40px'))

        iidentifications = widgets.Textarea()

        iminmax = widgets.IntRangeSlider(
            value=[0, 30],
            min=0,
            max=30,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        )

        iordre = widgets.Dropdown(
            options=['alphabétique', 'fréquences'],
            value='alphabétique',
            description='ordre :'
        )

        ireverse = widgets.Dropdown(
            options=['croissant', 'décroissant'],
            value='croissant'
        )

        ifrequences = widgets.IntRangeSlider(
            value=[0, 100],
            min=0,
            max=100,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        )

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        )

        # sortie
        out = widgets.interactive_output(self.iishow_lexique, {'inom': inom, 'iidentifications': iidentifications,
                                                               'imots': imots, 'imotSauf': imotSauf,
                                                               'iminmax': iminmax,
                                                               'iordre': iordre, 'ireverse': ireverse,
                                                               'ifrequences': ifrequences,
                                                               'ivars': ivars, 'ivarSauf': ivarSauf,
                                                               'ivarsTypesFormule': ivarsTypesFormule,
                                                               'ivarsTypes': ivarsTypes,
                                                               'ivarsTypeSauf': ivarsTypeSauf})

        self.form_nom(inom)
        self.form_mots(imots, imotSauf, iidentifications, iminmax, ifrequences)
        self.form_ordre(iordre, ireverse)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        display(out)

    def iishow_distribution(self, **kwargs):

        if kwargs['inoms']:
            noms = strToList(kwargs['inoms'])
        else:
            noms = []
        nomSauf = strToList(kwargs['inomSauf'])

        vars = self.__vars[kwargs['ivars'][0]:kwargs['ivars'][1]]

        if kwargs['ivarSauf'][0] != 0 and kwargs['ivarSauf'][1] != len(self.__vars):
            varSauf = self.__vars[kwargs['ivarSauf'][0]:kwargs['ivarSauf'][1]]
        else:
            varSauf = []
        varsTypesFormule = kwargs['ivarsTypesFormule']

        if kwargs['ivarsTypes']:
            varsTypes = strToList(kwargs['ivarsTypes'])
        else:
            varsTypes = ''

        if kwargs['ivarsTypeSauf']:
            varsTypeSauf = strToList(kwargs['ivarsTypeSauf'])
        else:
            varsTypeSauf = ''

        if kwargs['ivarsTypesFormule']:
            varsTypesFormule = strToList(kwargs['ivarsTypesFormule'])
        else:
            varsTypesFormule = ''

        if kwargs['inomsTypes']:
            nomsTypes = strToList(kwargs['inomsTypes'])
        else:
            nomsTypes = ''

        if kwargs['inomsTypeSauf']:
            nomsTypeSauf = strToList(kwargs['inomsTypeSauf'])
        else:
            nomsTypeSauf = ''

        if kwargs['inomsTypesFormule']:
            nomsTypesFormule = strToList(kwargs['inomsTypesFormule'])
        else:
            nomsTypesFormule = ''

        langues = self.get_langues()
        motif = {}
        for lg in langues:
            motif[lg] = strToList(kwargs['imotif_' + lg])

        self.show_distribution(motif=motif, noms=noms, nomSauf=nomSauf,
                               vars=vars, varSauf=varSauf,
                               varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                               varsTypesFormule=varsTypesFormule, nomsTypes=nomsTypes, nomsTypeSauf=nomsTypeSauf,
                               nomsTypesFormule=nomsTypesFormule)

    def ishow_distribution(self):

        langues = self.get_langues()

        inoms = widgets.Textarea(layout=textArea_layout)
        inomSauf = widgets.Textarea(layout=textArea_layout)
        inomsTypesFormule = widgets.Textarea(layout=textArea_layout)
        inomsTypes = widgets.Textarea(layout=textArea_layout)
        inomsTypeSauf = widgets.Textarea(layout=textArea_layout)

        ivarsTypesFormule = widgets.Textarea(layout=textAreaFormule_layout)
        ivarsTypes = widgets.Textarea(layout=textArea_layout)
        ivarsTypeSauf = widgets.Textarea(layout=textArea_layout)
        ivars = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )
        ivarSauf = widgets.IntRangeSlider(
            value=[0, len(self.__vars)],
            min=0,
            max=len(self.__vars),
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        )

        # sortie
        params = {'inoms': inoms, 'inomSauf': inomSauf,
                  'ivars': ivars, 'ivarSauf': ivarSauf,
                  'ivarsTypesFormule': ivarsTypesFormule,
                  'ivarsTypes': ivarsTypes,
                  'ivarsTypeSauf': ivarsTypeSauf,
                  'inomsTypesFormule': inomsTypesFormule,
                  'inomsTypes': inomsTypes,
                  'inomsTypeSauf': inomsTypeSauf}
        imotifs = {}
        for lg in langues:
            params['imotif_' + lg] = widgets.Textarea(layout=Layout(display='flex',
                                                                    height='40px',
                                                                    width='300px'))
            imotifs['imotif_' + lg] = params['imotif_' + lg]
        out = widgets.interactive_output(self.iishow_distribution, params)

        self.form_motif(imotifs)
        self.form_noms(inoms, inomSauf, inomsTypesFormule, inomsTypes, inomsTypeSauf)
        self.form_vars(ivarsTypesFormule, ivarsTypes, ivarsTypeSauf, ivars, ivarSauf)
        display(out)




