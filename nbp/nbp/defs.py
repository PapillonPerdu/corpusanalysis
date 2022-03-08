import pandas as pd
import numpy as np
import sys
import html

from .basics import *


def var_augmented(self, var):
    if self.varsDefs_exists:
        definition = self.vars_defs_dic[var]
        if str(var).strip() == '':
            value = '-'
        var_aug = "<a style=\"color:black;cursor:pointer;\" " \
               "title=\"" + html.escape(str(definition)) + "\" " \
                "onmouseup=\"click_on_var(event, \'" + html.escape(str(var).replace("'", "\\'")) + "\',\'" + \
               html.escape(str(definition).replace("'", "&#x27;").replace('\n', '\\n')) + "\',\'" + \
               self.instanceName + "\');\">" + str(var) + "</a>"
    else:
        var_aug = "<a style=\"color:black;cursor:pointer; \" " \
               "onmouseup=\"add_variable(\'" + html.escape(str(var).replace("'", "\\'")) + "\',\'after\',\'" + \
               self.instanceName + "\');\">" + str(var) + "</a>"

    var_aug += "<sup><a style=\"color:black;cursor:pointer;\" " \
               "title=\"Add new variable after this one\" " \
 \
               "onmouseup=\"add_variable(\'" + html.escape(str(var).replace("'", "\\'")) + "\',\'after\',\'" + \
               self.instanceName + "\');\">" + "+" + "</a></sup>"
    return var_aug

#transforme une liste de vars en une liste de vars avec leur déf.
def vars_augmented(self,vars):
    return [var_augmented(self,v) for v in vars]


def nom_augmented(self, nom):
    definition = self.noms_defs_dic[nom]

    try:
        table = self.noms_tables_dic[nom]
        id = self.noms_ids_dic[nom]
        prjt = self.noms_prjts_dic[nom]
    except:
        id = 0

    try:
        nomAug = "<a style=\"color:black;cursor:pointer;\" " \
                 "title=\"" + html.escape(str(definition)) + "\" " \
            "onmouseup=\"click_on_nom(event,\'" + html.escape(
            str(nom).replace("'", "\\'")) + "\',\'" + \
                 html.escape(str(definition).replace("'", "&#x27;").replace('\n', '\\n')) + "\',\'" + \
                 self.instanceName + "\');\">" + str(nom) + "</a>"
        if id:
            thm = "<sup ><small><a title='Open in Thamous' href='https://thamous.univ-rennes1.fr/php/form_ref.php?id_ref=" + str(id) + "&table=t" + table + "&projet="+prjt+"' target='_blank' style='color:black; text-decoration: none'>Thm</a>" \
                   "  <a title='Thamous navigation' href='https://thamous.univ-rennes1.fr/php/navigation_liens_invariante.php?id_origine=" + str(id) + "&table_origine=t" + table + "&projet="+prjt+"&type_liens=Tous' target='_blank' style='color:black; text-decoration: none'>&harr;</a></small></sup>"
            nomAug += thm
        nomAug += "<sup><a style=\"color:black;cursor:pointer;\" " \
                  "title=\"Add new name below this one\" " \
                                                              "onmouseup=\"add_nom(\'" + html.escape(str(nom).replace("'", "&#x27;")) + "\',\'after\',\'" + \
                   self.instanceName + "\');\">" + "+" + "</a></sup>"
        return nomAug

    except:
        return nom

# transforme une liste de noms en une liste de noms avec leur déf.
def noms_augmented(self, noms):
    return [nom_augmented(self,n) for n in noms]

def indexesToVars_augmented(self, indexesVars):
    return [var_augmented(self,self.vars[v]) for v in indexesVars]

def indexesToNoms_augmented(self, indexesNoms):
    return [nom_augmented(self,self.noms[n]) for n in indexesNoms]

def indexToVar_augmented(self, num):
    return var_augmented(self, self.vars[num])



