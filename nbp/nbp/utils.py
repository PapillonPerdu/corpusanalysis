#Méthodes indépendantes des données

import re
import numpy as np
import itertools
from IPython.display import HTML

#source : https://stackoverflow.com/questions/40554839/pop-out-expand-jupyter-cell-to-new-browser-window
def view(df):
    css = """<style>
    table { border-collapse: collapse; border: 3px solid #eee; }
    table tr th:first-child { background-color: #eeeeee; color: #333; font-weight: bold }
    table thead th { background-color: #eee; color: #000; }
    tr, th, td { border: 1px solid #ccc; border-width: 1px 0 0 1px; border-collapse: collapse;
    padding: 3px; font-family: monospace; font-size: 10px }</style>
    """
    s  = '<script type="text/Javascript">'
    s += 'var win = window.open("", "Title", "toolbar=no, location=no, directories=no, status=no, menubar=no, scrollbars=yes, resizable=yes, width=780, height=200, top="+(screen.height-400)+", left="+(screen.width-840));'
    s += 'win.document.body.innerHTML = \'' + (df.to_html() + css).replace("\n",'\\') + '\';'
    s += '</script>'

    return HTML(s+css)


# source : https://stackoverflow.com/questions/31581425
def getCombinations(lst, max):
    for L in range(1, max + 1):
        for subset in itertools.combinations(lst, L):
            yield list(subset)


def includes(l, M):
    ''' teste si la liste l contient une liste de la liste M'''
    for m in M :
        if len(set(l) - set(m)) == len(l) - len(m):
            # print(l,' contient un ',M)
            return True
    # print(l,' ne contient pas un ',M)
    return False


def inList(l, M):
    ''' teste si la liste l est contenue dans une liste de la liste M'''
    for m in M:
        if len(set(m) - set(l)) == len(m) - len(l):
            # print(l,' contient un ',M)
            return True
    # print(l,' ne contient pas un ',M)
    return False

# Ex. :
# a & b = b & d est vrai
def equal(str1, str2):
    str1 = str(str1)
    str2 = str(str2)
    str1 = str1.replace(" ", "")
    str2 = str2.replace(" ", "")
    ar1 = str1.split('&')
    ar2 = str2.split('&')
    inter = np.intersect1d(ar1, ar2)
    return len(inter) > 0


def equalStrict(str1, str2):
    str1 = str(str1)
    str2 = str(str2)
    str1 = str1.replace(" ", "")
    str2 = str2.replace(" ", "")
    return str1 == str2


# test d'égalité entre deux listes à un pourcentage entier donné pour une liste d'indexes
def listsEqual(L1, L2, indexesVars, precision=100):
    if (type(precision) != int): precision = 100
    sum = 0
    if indexesVars:
        for i in indexesVars:
            if (equal(L1[i], L2[i])): sum += 1
        return sum / len(indexesVars) * 100 >= precision
    else:
        return False



# Pourcentage d'égalité de deux listes sur une liste de variables
def listsEqualPourcent(L1, L2, indexesVars):
    sum = 0
    for i in indexesVars:
        if (equal(L1[i], L2[i])): sum += 1
    try:
        return round(sum / len(indexesVars) * 100)
    except:
        return 0


# fait la somme d'une liste de listes et et retourne le pourcentage d'égalité
# avec une liste donnée
def sumEqualPourcent(ListeL, L, indexesVars):
    sum = 0
    for i in indexesVars:
        ok = False
        for l in ListeL:
            if equal(l[i], L[i]):
                ok = True
                break
        if ok: sum += 1

    return round(sum / len(indexesVars) * 100)


# fait la somme d'une liste de listes et teste s'il y une égalité, à un pourcentage près
# avec une liste donnée
def sumEqualPourcentTest(ListeL, L, indexesVars, pourcent):
    sum = 0
    for i in indexesVars:
        ok = False
        for l in ListeL:
            if equal(l[i], L[i]):
                ok = True
                break
        if ok: sum += 1

    return sum / len(indexesVars) * 100 >= pourcent

def subIntervalles(l, M):
   for m in M:
       if l[0] >= m[0] and l[1] <= m[1]:
           # print(l,' contient un ',M)
           return True
   # print(l,' ne contient pas un ',M)
   return False


class color:
   purple = '\033[95m'
   cyan = '\033[96m'
   darkcyan = '\033[36m'
   blue = '\033[94m'
   green = '\033[92m'
   yellow = '\033[93m'
   red = '\033[91m'
   bold = '\033[1m'
   underline = '\033[4m'
   end = '\033[0m'


# liste de chaînes dans une liste (extension) vérifiant l'expression régulière regStr
def strExt(regStr,extension):
    regStr = '^' + str(regStr).replace('+','\+') + '$'
    return [s for s in extension if re.search(regStr, s, re.IGNORECASE)]


# liste de chaînes dans une liste (extension) vérifiant
# une liste d'expressions régulières regStrs
def strsExt(regStrs,extension):
    res = []
    for regStr in regStrs:
        res = res + strExt(regStr,extension)
    return res


def toList(object):
    if isinstance(object, list):
        return object
    else:
        return [object]
