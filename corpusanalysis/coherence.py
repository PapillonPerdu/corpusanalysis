from .basics import *

def show_coherence(self, indexesNoms, indexesVars, pasColonne=10, pasLigne=10):
    """

    :param noms:
    :param nomSauf:
    :param vars:
    :param varSauf:
    :param varsTypes:
    :param varsTypeSauf:
    :param varsTypesFormule:
    :param nomsTypes:
    :param nomsTypeSauf:
    :param nomsTypesFormule:
    :param pasColonne:
    :param pasLigne:
    :return: Tableau donnant  le nombres de valeurs égales d'une liste de noms sur les variables indiquées
    """


    resNoms = [self.noms_augmented[i] for i in indexesNoms]
    valuesCompletes = indexesVarsToVals(self,indexesNoms, indexesVars)

    total = len(indexesVars)
    valsCompletes = sorted(list(set(valuesCompletes)))
    lines = []
    for n in indexesNoms:
        cardValues = []
        values = indexesVarsToVals(self,[n], indexesVars)
        for val in valsCompletes:
            card = values.count(val)
            cardValues.append(card)
        lines.append(cardValues)

    listVars = ['Variables'] + [self.vars_augmented[v] for v in indexesVars]
    print('Variables : ' + str(len(indexesVars)))
    printLines([],columns=listVars)
    printLines(lines, columns=valsCompletes, index=resNoms, pasColonne=pasColonne, pasLigne=pasLigne)



def show_coherence_pourcent(self,indexesNoms, indexesVars, pasColonne=10, pasLigne=10):

    resNoms = [self.noms_augmented[i] for i in indexesNoms]
    valuesCompletes = indexesVarsToVals(self,indexesNoms, indexesVars)

    total = len(indexesVars)
    valsCompletes = sorted(list(set(valuesCompletes)))
    lines = []
    for n in indexesNoms:
        pourcent = []
        values = indexesVarsToVals(self,[n], indexesVars)
        for val in valsCompletes:
            card = values.count(val)
            pourcent.append(round(card / total * 100))
        lines.append(pourcent)

    listVars = ['Variables'] + [self.vars_augmented[v] for v in indexesVars]
    print('Variables : ' + str(len(indexesVars)))
    printLines(columns=listVars)
    printLines(lines, columns=valsCompletes, index=resNoms, pasColonne=pasColonne, pasLigne=pasLigne)

def show_coherence_type(self, nom, tp):
    """
    :param self:
    :param nom:
    :param tp:
    :return: Tableau avec le nombre et le pourcentages de valeurs égales d'un nom sur les variables d'un même type
    """
    indexNom = nomToIndex(self,nom)
    values = typeToVals(self,indexNom, tp)
    indexesVars = typeToIndexesVars(self,tp)
    total = len(indexesVars)
    vals = sorted(list(set(values)))
    effectifs = [total]
    pourcent = ['']
    for val in vals:
        effectifs.append(values.count(val))
        pourcent.append(round(values.count(val) / total * 100))

    print(color.bold + nom + ': ' + tp + color.end)
    display(pd.DataFrame([effectifs, pourcent], columns=['total'] + vals, index=['effectifs', '%']))


def show_coherence_types(self, nom, varsTypes):
    """
    :param self:
    :param nom:
    :param varsTypes:
    :return: Tableau avec le nombre et le pourcentage de valeurs égales d'un nom sur les variables d'une liste de types
    """
    for tp in varsTypes:
        self.show_coherence_type(nom, tp)
