##########################################################################################
### Distributions
##########################################################################################

separateurs = [' ', '.', ':', ',', ';', '!', '?', '-', '...']


def get_langue(self, indexNom):
    indexLangue = self.__vars.index('langue')
    return self.__data[indexNom][indexLangue]


def find(self, indexNom, indexVar, pattern):
    txt = self.__data[indexNom][indexVar]
    reg = re.compile(pattern)
    res = reg.findall(txt, re.IGNORECASE)
    return len(res)


def distribution(self, motif, indexNom, indexesVars):
    lang = self.get_langue(indexNom)
    pattern = '|'.join(motif[lang])
    distr = [self.find(indexNom, v, pattern) for v in indexesVars]
    return distr


# indexes des variables où le motif est présent
def indexesVars_distribution(self, indexesNoms, indexesVars, motif,
                             pasColonne=10, pasLigne=10):
    distributions = []

    for n in indexesNoms:
        distributions.append(self.distribution(motif, n, indexesVars))

    indexesVarsDistr = []

    for i in range(len(indexesVars)):
        for n in range(len(indexesNoms)):
            if distributions[n][i]:
                indexesVarsDistr.append(indexesVars[i])
                break

    return indexesVarsDistr


# variables où le motif est présent
def vars_distribution(self, motif,
                      noms,
                      vars=[], varSauf=[],
                      varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                      pasColonne=10, pasLigne=10):
    indexesVars = self.indexesVars_distribution(motif, noms,
                                                vars=vars, varSauf=varSauf,
                                                varsTypes=varsTypes, varsTypeSauf=varsTypeSauf,
                                                varsTypesFormule=varsTypesFormule,
                                                pasColonne=pasColonne, pasLigne=pasLigne)

    varsDistr = [self.__vars[i] for i in indexesVars]

    return varsDistr


def show_distribution(self, motif={},
                      vars=[], varSauf=[],
                      noms=[], nomSauf=[],
                      varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
                      nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
                      pasColonne=10, pasLigne=10):
    indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
    indexesNoms = self.getIndexesNoms(noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)

    distributions = []
    # suppression des blancs avant et après les motifs
    motif = {k: list(map(str.strip, m)) for k, m in motif.items()}

    n = len(indexesNoms)
    for indexNom in indexesNoms:
        distributions.append(self.distribution(motif, indexNom, indexesVars))

    # Représentation en barres
    width = 0.35  # largeur emplacement des barres
    pos = [i * width for i in range(len(indexesVars))]  # placement première barre
    posTicks = [x + width / 2 for x in pos]  # placement ticks
    labels = ['' for i in range(len(indexesVars))]

    fig, ax = plt.subplots()
    for i in range(n):
        posi = [x + i * width / n for x in pos]
        ax.bar(posi, distributions[i], width / n, label=self.__noms[indexesNoms[i]])

    ax.set_ylabel("Nombre d\'occurrences")
    ax.set_title('Occurrences')
    ax.set_xticks(posTicks)
    ax.set_xticklabels(labels)
    ax.legend()

    fig.tight_layout()
    plt.show()

    # Tableau
    vars = [self.__vars_augmented[i] for i in indexesVars]

    distributions_blk = []
    # remplace les 0 par des blancs
    for n in range(len(noms)):
        distributions_blk.append([i if not i == 0 else '' for i in distributions[n]])

    lines = distributions_blk
    columns = vars
    index = self.noms_augmented(noms)

    if pasColonne:
        res = self.repeteIndex(pasColonne, lines, columns, index)
        lines = res[0]
        columns = res[1]

    if pasLigne:
        res = self.repeteColumns(pasLigne, lines, columns, index)
        lines = res[0]
        index = res[1]

    display(pd.DataFrame(lines, columns=vars, index=noms))

    # return distributions


# Lexique d'un texte avec fréquences
def lexiqueFreq(self, indexNom, indexesVars, identifications, mots, motSauf,
                min, max,
                ordre, reverse,
                minfreq, maxfreq):
    words = []
    for v in indexesVars:
        txt = self.__data[indexNom][v]
        words += textToWords(txt)

    words = [w.lower() for w in words]

    # Liste des orbites définies par les identifications
    orbites = wordsToOrbites(words, identifications)

    # Suppression des expressions régulières
    mots = identificationToOrbite(mots, words)
    motSauf = identificationToOrbite(motSauf, words)

    # Réduction de la liste des orbites
    # conditions sur :
    # -- la longueur des mots
    # -- mots exclus
    # -- mots forcés
    orbites = orbitesReduction(orbites,
                               mots, motSauf, min, max)

    # Lexique avec fréquences
    lexiqueFreq = orbitesToLexiqueFreq(orbites, words)

    # Réduction du lexique aux orbites dont le représentant
    # vérifie les conditions sur les fréquences
    def freqCondition(orbiteFreq, minfreq, maxfreq):
        freqTotal = orbiteFreqTotal(orbiteFreq)
        condition = minfreq <= freqTotal and (maxfreq == 0 or freqTotal <= maxfreq)
        return condition

    lexiqueFreq = [orbite for orbite in lexiqueFreq if freqCondition(orbite, minfreq, maxfreq)]

    # Tri de lexiqueFreq
    lexiqueFreq = sortLexiqueFreq(lexiqueFreq, ordre, reverse)

    return lexiqueFreq


def show_lexique(self, nom, identifications=[], mots=[], motSauf=[], min=0, max=0,
                 ordre='alpha', reverse=False,
                 minfreq=0, maxfreq=0,
                 vars=[], varSauf=[],
                 varsTypes=[], varsTypeSauf=[], varsTypesFormule=''):
    try:
        indexNom = self.__noms.index(nom)
    except:
        print(color.bold + "Le nom \"" + nom + "\" ne fait pas partie des noms reconnus." + color.end)
        sys.exit(1)

    indexesVars = self.getIndexesVars(vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)

    if ordre.startswith('fr'):
        ordre = 'freq'
    else:
        ordre = 'alpha'

    # suppression des blancs en début et fin de chaîne
    identifications = [list(map(str.strip, l)) for l in identifications]

    lexiqueFreq = self.lexiqueFreq(indexNom, indexesVars, identifications,
                                   mots, motSauf,
                                   min, max, ordre, reverse,
                                   minfreq, maxfreq)

    lines = []
    index = []
    total = 0
    for orbiteFreq in lexiqueFreq:
        index.append(orbiteFreq[0][0])
        freq = orbiteFreqTotal(orbiteFreq)
        if len(orbiteFreq) > 1:
            line = [orbiteFreqToStr(orbiteFreq), freq]
        else:
            line = ['', freq]
        total += freq
        lines.append(line)
    lines.append(['', total])

    # Affichage du lexique
    display(pd.DataFrame(lines, columns=['orbite', 'fréquence'], index=index + ['Total']))
