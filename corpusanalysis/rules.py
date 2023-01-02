from .basics import *
from .sql import *


def show_vars_rules(self,indexesVarsTypeSortie):
    vars_rules=get_vars_regles_db(self)
    print(color.bold + 'Variables types rules : ' + color.end)

    columns = ['rules']
    index = list(vars_rules.keys())
    lines = [[vars_rules[t]] for t in index]

    printLines( lines, columns=columns, index=index)

def show_noms_rules(self,indexesNomsTypeSortie):
    noms_rules=get_noms_regles_db(self)
    print(color.bold + 'Names types rules : ' + color.end)

    columns = ['rules']
    index = list(noms_rules.keys())
    lines = [[noms_rules[t]] for t in index]

    printLines( lines, columns=columns, index=index)