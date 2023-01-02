from .basics import *
from .utils import *



def optimise_intervalles(self, indexNom1, indexNom2, indexesVars, pourcent, longueur, pas):
    max = len(indexesVars)
    L1 = self.data[indexNom1]
    L2 = self.data[indexNom2]
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
                val = listsEqualPourcent(L1, L2, indexesVarsSub)

                if val >= pourcent:
                    intervalles.append([indexesVars[debut], indexesVars[fin]])
                    pourcents.append(val)

            debut = debut + pas
            fin = fin + pas

    res = [[pourcents[i]] + intervalles[i] for i in range(len(intervalles))]
    return res


def show_intervals(self, indexNom1, indexNom2, indexesNoms, indexesVars,
                   percent=100, length=1, pas=1):

    res = optimise_intervalles(self, indexNom1, indexNom2, indexesVars, percent, length, pas)
    # print(res)
    if res:
        lignes = []
        for r in res:
            ligne = []
            for i in indexesVars:
                if r[1] <= i <= r[2]:
                    if equal(self.data[indexNom1][i], self.data[indexNom2][i]):
                        ligne.append(self.data[indexNom1][i])
                    else:
                        ligne.append(self.data[indexNom1][i] + '/' + self.data[indexNom2][i])
                else:
                    ligne.append('')

            ligne = [r[0], r[2] - r[1]] + ligne
            lignes.append(ligne)

        columns = ['%', 'long.'] + [self.vars_augmented[v] for v in indexesVars]
        df = pd.DataFrame(lignes, columns=columns)
        display(HTML(df.to_html(escape=False)))


    else:
        print('Aucun résultat')