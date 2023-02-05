

##########################################################################################
### Fonctions lexique
######################################################################################


# Une identification est une liste commençant par un mot, suivie
# d'expressions régulières décrivant les identifications à ce mot
# Une orbite est une liste de mots (identifiés)
# Une orbiteFreq est une liste de couples [mot, fréquence]
# Un lexiqueFreq est une liste d'orbiteFreq


# entrée : texte sous forme d'une chaîne
# sortie : liste des mots du texte
def textToWords(text):
   return re.sub("[^\w]", " ", text).split()


# teste si un mot est dans l'orbite donnée par une identification,
# pouvant comprendre des expressions régulières
def inOrbite(word, identification):
   boole = False
   idsx = ["^" + id + "$" for id in identification]
   ids_reg = '|'.join(idsx)
   if re.match(ids_reg, word):
       boole = True
   return boole


# entrée : liste de termes identifiés (avec reg exp.)
# sortie : orbite (relative à une liste de mots).
def identificationToOrbite(identification, words):
   orbite = [word for word in words if inOrbite(word, identification)]
   orbite = list(set(orbite))
   return orbite


# retourne la fréquence totale d'une orbiteFreq (somme des fréquences)
def orbiteFreqTotal(orbiteFreq):
   freq = sum([f for w, f in orbiteFreq])
   return freq


# Transforme une liste d'orbites en lexiqueFreq
def orbitesToLexiqueFreq(orbites, words):
   dictFreq = {word: words.count(word) for word in words}
   lexiqueFreq = []
   for orbite in orbites:
       orbiteFreq = [[word, dictFreq[word]] for word in orbite]
       lexiqueFreq.append(orbiteFreq)
   return lexiqueFreq


# Représentation sous forme de chaîne d'une orbiteFreq
def orbiteFreqToStr(orbiteFreq):
   res = ', '.join([str(w) + ' (' + str(f) + ')' for w, f in orbiteFreq])
   return res


# Trie un lexiqueFreq
def sortLexiqueFreq(lexiqueFreq, ordre, reverse):
   if ordre == 'freq':
       frequences = [orbiteFreqTotal(orbiteFreq) for orbiteFreq in lexiqueFreq]
       lexiqueFreq = [orbiteFreq for freq, orbiteFreq in sorted(zip(frequences, lexiqueFreq), reverse=reverse)]

   if ordre == 'alpha':
       lexiqueFreq = sorted(lexiqueFreq, reverse=reverse)

   return lexiqueFreq


def wordsToOrbites(words, identifications):
   '''Transforme une liste de mots en une liste d'orbite'''
   from itertools import groupby
   words = [w.lower() for w in words]
   words_uniques = list(set(words))
   # dictionnaire des orbites définies par identification
   dictOrbites = {str(identification[0]): identificationToOrbite(identification, words_uniques) for identification in
                   identifications}
   # liste des mots dans une orbites
   motsInOrbites = list(set(merge(list(dictOrbites.values()))))
   representants = list(dictOrbites.keys())
   # Substitution du représentant aux mots identifiés
   orbites = []
   for word in words_uniques:
        if word in representants:
            # word est le représentant d'une identification. On enregistre son orbite
            orbites.append(dictOrbites[word])
        else:
            # word n'est pas le représentant d'une identification
            if not word in motsInOrbites:
                # si word est dans une orbite, on ne l'enregistre pas dans le lexique
                # sinon, on enregistre son orbite réduite à lui-même
                orbites.append([word])
        return orbites


''' Réduction de la liste des orbites
conditions sur :
 -- la longueur des mots
 -- mots exclus
 -- mots forcés'''
def orbitesReduction(orbites, mots, motSauf, min, max):
    def minmax(x):
        return (min <= len(x) <= max or x in mots)

    def exclus(x):
        return x in motSauf

    def forces(x):
        return x in mots

    orbitesRed = [orbite for orbite in orbites if testOne(orbite, forces) or
                  (testAll(orbite, minmax) and not testAll(orbite, exclus))]

    return orbitesRed

 ##########################################################################################
    ### Optimisation
    ##########################################################################################

    def optimise_intervalles(self, indexNom1, indexNom2, indexesVars, pourcent, longueur, pas):
        max = len(indexesVars)
        L1 = self.__data[indexNom1]
        L2 = self.__data[indexNom2]
        intervalles = []
        pourcents = []

        # l=longueur des intervalles parcourus

        for l in reversed(range(longueur, max + 1)):
            debut = 0
            fin = l - 1
            # print(l)
            while fin < max:
                # print('     ',debut,'-',fin)
                if not subIntervalles([indexesVars[debut], indexesVars[fin]], intervalles):
                    indexesVarsSub = indexesVars[debut:fin + 1]
                    val = self.listsEqualPourcent(L1, L2, indexesVarsSub)

                    if val >= pourcent:
                        intervalles.append([indexesVars[debut], indexesVars[fin]])
                        pourcents.append(val)

                debut = debut + pas
                fin = fin + pas

        res = [[pourcents[i]] + intervalles[i] for i in range(len(intervalles))]
        return res

    def show_intervalles(self, indexNom1, indexNom2,indexesVars,
                         pourcent=100, longueur=1, pas=1):

        res = self.optimise_intervalles(indexNom1, indexNom2, indexesVars, pourcent, longueur, pas)
        # print(res)
        if res:
            lignes = []
            for r in res:
                ligne = []
                for i in indexesVars:
                    if r[1] <= i <= r[2]:
                        if self.strEqual(self.__data[indexNom1][i], self.__data[indexNom2][i]):
                            ligne.append(self.__data[indexNom1][i])
                        else:
                            ligne.append(self.__data[indexNom1][i] + '/' + self.__data[indexNom2][i])
                    else:
                        ligne.append('')

                ligne = [r[0], r[2] - r[1]] + ligne
                lignes.append(ligne)

            columns = ['%', 'long.'] + [self.__vars_augmented[v] for v in indexesVars]
            df=pd.DataFrame(lignes, columns=columns)
            display(HTML(df.to_html(escape=False)))


        else:
            print('Aucun résultat')

    def plot_intervalles(self, indexNom1, indexNom2, indexesVars,longueur,
                         pas=1, elev=0, azim=0):
        indexMax = len(indexesVars)
        L1 = self.__data[indexNom1]
        L2 = self.__data[indexNom2]

        def fun(xList, yList, L1, L2, indexesVars):
            res = [self.listsEqualPourcent(L1, L2, indexesVars[x:y + 1]) for x, y in zip(xList, yList)]

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

    ##########################################################################################
    ### Représentation moyennée
    ##########################################################################################

    def moyenne(self, L1, L2, indexVar, n, indexesVars):
        i = indexesVars.index(indexVar)
        m = max([0, i - n])
        M = min([len(indexesVars) - 1, i + n])
        sum = 0
        for j in range(m, M + 1):
            if self.strEqual(L1[indexesVars[j]], L2[indexesVars[j]]):
                sum += 1

        return sum / max([M - m + 1, 1])

    def plot_moyenne(self, indexNom1, indexNoms,indexesVars,
                     width=20, height=10, legend_size=10):
        L1 = self.data[indexNom1]
        x = indexesVars

        fig = plt.figure(figsize=(width, height))
        ax = plt.subplot(111)

        for n in indexNoms:
            L2 = self.data[n]
            y = [self.moyenne(L1, L2, indexVar, rayon, indexesVars) for indexVar in x]
            ax.plot(x, y, label=self.noms[n])

        box = ax.get_position()
        ax.set_position([box.x0, box.y0,
                         box.width, box.height])

        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
                  fancybox=True, shadow=True, ncol=5, prop={'size': legend_size})
        plt.show()

    def vars_moyenne(self, indexNom1, indexNom2, indexesVars, rayon=3, pourcent=0, Pourcent=100):
        L1 = self.data[indexNom1]
        L2 = self.data[indexNom2]
        resVars = [self.indexToVar(i) for i in indexesVars if
                   Pourcent >= 100 * self.moyenne(L1, L2, i, rayon, indexesVars) >= pourcent]
        return resVars
