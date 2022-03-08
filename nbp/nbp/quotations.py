import sys
import numpy as np
import pandas as pd

from .basics import *



def show_citations(self):
    df = pd.DataFrame(self.citations, columns=self.vars_augmented, index=self.noms_augmented)
    display(HTML(df.to_html(escape=False)))


def indexesVars_avec_citations(self, indexNom, indexesVars):
    indexesVarsCitations = [v for v in indexesVars if self.citations[indexNom][v] != '']
    return indexesVarsCitations


def vars_avec_citations(self,indexNom,indexesVars):
    indexesVars_avec_citations = indexesVars_avec_citations(self,indexNom,indexesVars)
    vars_avec_citations = [self.vars[v] for v in indexesVars_avec_citations]
    return vars_avec_citations


def indexesVars_sans_citations(self, indexNom,indexesVars):
    indexesVarsCitations = [v for v in indexesVars if self.citations[indexNom][v] == '']
    return indexesVarsCitations


def vars_sans_citations(self,indexNom,indexesVars):
    indexesVars_sans_citations = indexesVars_sans_citations(self, indexNom,indexesVars)
    vars_sans_citations = [self.vars[v] for v in indexesVars_sans_citations]
    return vars_sans_citations

def show_avec_citations(self,indexNom,indexesVars):
    lines = [[self.data_augmented[indexNom][v] for v  in indexesVars]]
    columns = [indexToVar_augmented(self, v) for v in indexesVars]
    index = [nom_augmented(self,nom)]
    df = pd.DataFrame(lines, columns = columns, index = index)
    display(HTML(df.to_html(escape=False)))

def show_sans_citations(self,indexNom,indexesVars):
    lines = [[self.data_augmented[indexNom][v] for v  in indexesVars]]
    columns = [indexToVar_augmented(self, v) for v in indexesVars]
    index = [nom_augmented(self,nom)]
    df = pd.DataFrame(lines, columns = columns, index = index)
    display(HTML(df.to_html(escape=False)))

def vars_citations(self, indexNom, str,indexesVars):

    varsSelected = [self.vars[v] for v in indexesVars if str in self.citations[indexNom][v]]

    return varsSelected


