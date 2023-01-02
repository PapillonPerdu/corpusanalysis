from .basics import *

def show_coherence(self, indexesNoms, indexesVars,variantes=[],
                   pasColonne=10, pasLigne=10, decoration=False):
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


    resNoms = [self.noms_augmented[i] if decoration else self.noms[i] for i in indexesNoms]
    valuesCompletes = indexesVarsToVals(self,indexesNoms, indexesVars, variantes=variantes)

    total = len(indexesVars)
    valsCompletes = sorted(list(set(valuesCompletes)))
    lines = []
    for n in indexesNoms:
        cardValues = []
        values = indexesVarsToVals(self,[n], indexesVars, variantes)
        for val in valsCompletes:
            card = values.count(val)
            cardValues.append(card)
        lines.append(cardValues)

    listVars = ['Variables'] + [self.vars_augmented[v] if decoration else self.vars[v] for v in indexesVars]
    print('Variables : ' + str(len(indexesVars)))
    printLines([],columns=listVars)
    printLines(lines, columns=valsCompletes, index=resNoms, pasColonne=pasColonne, pasLigne=pasLigne)



def show_coherence_percent(self, indexesNoms, indexesVars,
                           variantes=[], pasColonne=10, pasLigne=10,decoration=True):

    resNoms = [self.noms_augmented[i] if decoration else self.noms[i] for i in indexesNoms]
    valuesCompletes = indexesVarsToVals(self,indexesNoms, indexesVars, variantes=variantes)

    total = len(indexesVars)
    valsCompletes = sorted(list(set(valuesCompletes)))
    lines = []
    for n in indexesNoms:
        pourcent = []
        values = indexesVarsToVals(self,[n], indexesVars)
        for val in valsCompletes:
            card = values.count(val)
            prc=round(card / total * 100)
            if prc:
                pourcent.append(str(prc) + '%')
            else :
                pourcent.append('-')
        lines.append(pourcent)

    listVars = ['Variables'] + [self.vars_augmented[v] if decoration else self.vars[v] for v in indexesVars]
    print('Variables : ' + str(len(indexesVars)))
    printLines([],columns=listVars)
    printLines(lines, columns=valsCompletes, index=resNoms, pasColonne=pasColonne, pasLigne=pasLigne)

def show_coherence_type(self, nom, tp, variantes):
    """
    :param self:
    :param nom:
    :param tp:
    :return: Tableau avec le nombre et le pourcentages de valeurs égales d'un nom sur les variables d'un même type
    """
    indexNom = nomToIndex(self,nom)
    values = typeToVals(self,indexNom, tp, variantes=variantes)
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
