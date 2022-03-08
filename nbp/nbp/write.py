# fonctions pour modifier la base ou les fichiers de données

import csv
import os
import ipywidgets as widgets

from .basics import *
from .sql import *


def rename_var(self, var):
    var = varsExtUnique(self,html.unescape(var))

    if not var in self.vars:
        print(color.bold + '''The variable "{}" doesn't exist.'''.format(var) + color.end)
        sys.exit()
    newVar = input('''Rename variable "{}" to : '''.format(var))
    if newVar in self.vars:
        print(color.bold + '''The variable "{}" already exists.'''.format(newVar) + color.end)
        sys.exit()

    if self.source == 'csv':
        rename_var_csv(self, var, newVar)
    else:
        rename_var_db(self,var, newVar)
    # mise à jour des tableaux
    indexVar = self.vars.index(var)
    self.vars[indexVar] = newVar
    self.vars_defs_dic[newVar] = self.vars_defs_dic[var]
    del self.vars_defs_dic[var]
    self.vars_augmented[indexVar] = var_augmented(self, newVar)


def delete_nom(self, nom):
    answer = input("Are you sure you want to delete the name \"{}\" ? (y/n) : ".format(nom))
    if answer == 'y':
        delete_nom_db(self, nom)
        load_db(self, self.db)
        print(color.bold + "The name \"{}\" has been deleted.".format(nom) + color.end)


def delete_var(self, var):
    answer = input("Are you sure you want to delete the variable \"{}\" ? (y/n) : ".format(var))
    if answer == 'y':
        delete_var_db(self, var)
        load_db(self, self.db)
        print(color.bold + "The variable \"{}\" has been deleted.".format(var) + color.end)


def delete_noms_type(self,type):
    answer = input("Are you sure you want to delete the name type \"{}\" ? (y/n) : ".format(type))
    if answer == 'y':
        delete_noms_type_db(self, type)
        load_db(self, self.db)
        print(color.bold + "The name type \"{}\" has been deleted.".format(type) + color.end)

def delete_vars_type(self,type):
    answer = input("Are you sure you want to delete the variable type \"{}\" ? (y/n) : ".format(type))
    if answer == 'y':
        delete_vars_type_db(self, type)
        load_db(self, self.db)
        print(color.bold + "The variable type \"{}\" has been deleted.".format(type) + color.end)


def rename_nom(self,nom):
    nom = html.unescape(nom)

    if not nom in self.noms:
        print(color.bold + '''The name "{}" doesn't exist.'''.format(nom) + color.end)
        sys.exit()

    newNom = input('''Rename name "{}" to : '''.format(nom))

    if newNom in self.noms:
        print(color.bold + '''The name "{}" already exists.'''.format(newNom) + color.end)
        sys.exit()

    if self.source == 'csv':
        rename_nom_csv(self, nom, newNom)
    else:
        rename_nom_db(self, nom, newNom)

    # mise à jour des tableaux
    indexNom = self.noms.index(nom)
    self.noms[indexNom] = newNom
    self.noms_defs_dic[newNom] = self.noms_defs_dic[nom]
    del self.noms_defs_dic[nom]
    self.noms_augmented[indexNom] = nom_augmented(self, newNom)


def rename_vars_type(self,type):
    type = html.unescape(type)
    newType = input('''Rename type "{}" to : '''.format(type))

    if newType in self.vars_types_types:
        print(color.bold + '''The variable type "{}" already exists.'''.format(newType) + color.end)
        sys.exit()

    if self.source == 'csv':
        print('Rename a type is not possible for csv file.')
    else:
        rename_vars_type_db(self, type, newType)

    # mise à jour des tableaux
    indexType = self.vars_types_types.index(type)
    self.vars_types_types[indexType] = newType


def rename_noms_type(self,type):
    type = html.unescape(type)
    newType = input('''Rename type "{}" to : '''.format(type))

    if newType in self.noms_types_types:
        print(color.bold + '''The name type "{}" already exists.'''.format(newType) + color.end)
        sys.exit()

    if self.source == 'csv':
        print('Rename a type is not possible for csv file.')
    else:
        rename_noms_type_db(self, type, newType)

    # mise à jour des tableaux
    indexType = self.noms_types_types.index(type)
    self.noms_types_types[indexType] = newType


def add_var(self, newVar, var = '', position = 'after'):
    var = html.unescape(var)
    if newVar in self.vars:
        print(color.bold + '''The variable "{}" already exists.'''.format(newVar) + color.end)
        sys.exit()

    if self.source == 'db':
        add_var_db(self, newVar, var = var, position = position)
    else:
        print('Variable cannot be added to csv file.')
        sys.exit()

    # mise à jour des tableaux
    load_db(self, self.db)

    print('''The variable "{}" has been added.'''.format(newVar))


def add_vars(self, newVars, var = '', position = 'after'):
    if self.source != 'db':
        print('Variables cannot be added to csv file.')
        sys.exit()
    if not type(newVars) == list:
        print('List of names expected')
        sys.exit()

    var = html.unescape(var)
    newVars = [html.unescape(newVar) for newVar in newVars]
    varsAdded = []
    for newVar in newVars:
        if newVar in self.vars:
            print(color.bold + '''The variable "{}" already exists.'''.format(newVar) + color.end)
        else:
            add_var_db(self, newVar, var = var, position = position)
            varsAdded.append(newVar)

    # mise à jour des tableaux
    load_db(self, self.db)

    print('''The variables "{}" have been added.'''.format(', '.join(varsAdded)))


def add_nom(self, newNom, nom = '', position = 'after', table='', id='', projet=''):
    nom = html.unescape(nom)
    if newNom in self.noms:
        print(color.bold + '''The name "{}" already exists.'''.format(newNom) + color.end)
        sys.exit()

    if self.source == 'db':
        add_nom_db(self, newNom, nom = nom, position = position)
        if not table == '' and not id == '':
            write_nom_thamous(self, newNom,table,id, projet)
    else:
        print('Name cannot be added to csv file.')
        sys.exit()

    # mise à jour des tableaux
    load_db(self, self.db)

    print('''The name "{}" has been added.'''.format(newNom))



def add_noms(self, newNoms, nom='', position='after'):
    if self.source != 'db':
        print('Names cannot be added to csv file.')
        sys.exit()

    nom = html.unescape(nom)
    newNoms = [html.unescape(newNom) for newNom in newNoms]
    nomsAdded = []
    for newNom in newNoms:
        if newNom in self.noms:
            print(color.bold + '''The name "{}" already exists.'''.format(newVar) + color.end)
        else:
            add_nom_db(self, newNom, nom=nom, position=position)
            nomsAdded.append(newNom)

    # mise à jour des tableaux
    load_db(self, self.db)

    print('''The names "{}" have been added.'''.format(', '.join(varsAdded)))


def add_noms_type(self, newT, nomsType  = '', position = 'after'):
    nomsType = html.unescape(nomsType)
    if newT in self.noms_types_types:
        print(color.bold + '''The type "{}" already exists.'''.format(newT) + color.end)
        sys.exit()

    if self.source == 'db':
        add_noms_type_db(self, newT, nomsType = nomsType, position = position)
    else:
        print('Types cannot be added to csv file.')
        sys.exit()

    # mise à jour des tableaux
    load_db(self, self.db)

    print('''The name type "{}" has been added.'''.format(newT))


def add_noms_types(self, newTypes, nomsType = '', position = 'after'):
    if self.source != 'db':
        print('Types cannot be added to csv file.')
        sys.exit()

    nomsType = html.unescape(nomsType)
    newTypes = [html.unescape(newType) for newType in newTypes]
    typesAdded = []
    for newT in newTypes:
        if newT in self.noms_types_types:
            print(color.bold + '''The name type "{}" already exists.'''.format(newT) + color.end)
        else:
            add_noms_type_db(self, newT, nomsType = nomsType, position = position)
            typesAdded.append(newVar)

    # mise à jour des tableaux
    load_db(self, self.db)

    print('''The name types "{}" have been added.'''.format(', '.join(typesAdded)))

def add_vars_type(self, newT, varsType  = '', position = 'after'):
    varsType = html.unescape(varsType)
    if newT in self.vars_types_types:
        print(color.bold + '''The type "{}" already exists.'''.format(newT) + color.end)
        sys.exit()

    if self.source == 'db':
        add_vars_type_db(self, newT, varsType = varsType, position = position)
    else:
        print('Types cannot be added to csv file.')
        sys.exit()

    # mise à jour des tableaux
    load_db(self, self.db)

    print('''The variable type "{}" has been added.'''.format(newT))


def add_vars_types(self, newTypes, varsType = '', position = 'after'):
    if self.source != 'db':
        print('Types cannot be added to csv file.')
        sys.exit()
    if not type(newTypes) == list:
        print("A list of names should be given")
        sys.exit(1)

    varsType = html.unescape(varsType)
    newTypes = [html.unescape(newType) for newType in newTypes]
    typesAdded = []
    for newT in newTypes:
        if newT in self.vars_types_types:
            print(color.bold + '''The variable type "{}" already exists.'''.format(newT) + color.end)
        else:
            add_vars_type_db(self, newT, varsType = varsType, position = position)
            typesAdded.append(newT)

    # mise à jour des tableaux
    load_db(self, self.db)

    print('''The variable types "{}" have been added.'''.format(', '.join(typesAdded)))


def write_val(self, nom, var, value):
    nom = html.unescape(nom)
    var = html.unescape(var)
    value = html.unescape(value)

    if self.source == 'csv':
        write_val_csv(self, nom, var, value)
    else:
        write_val_db(self, nom, var, value)

    # mise à jour des tableaux
    indexNom = nomToIndex(self, nom)
    indexVar = varToIndex(self, var)
    self.data[indexNom][indexVar] = value
    self.data_augmented[indexNom][indexVar] = value_augmented(self, self.data[indexNom][indexVar], indexNom,
                                                              indexVar)


def write_var_definition(self, var, definition):
    var = html.unescape(var)
    definition = html.unescape(definition)
    if self.source == 'csv':
        write_var_definition_csv(self, var, definition)
    else:
        write_var_definition_db(self,var, definition)

    # mise à jour des tableaux
    indexVar = varToIndex(self, var)
    self.vars_defs_dic[var] = definition
    self.vars_augmented[indexVar] = var_augmented(self, var)


def write_var_type_val(self, type, var, value):
    type = html.unescape(type)
    var = html.unescape(var)
    value = html.unescape(value)

    if self.source == 'csv':
        print('Set type value is not possible for csv file.')
        sys.exit()

    write_var_type_value_db(self, type, var, value)

    # mise à jour des tableaux
    indexType = self.vars_types_types.index(type)
    indexVar = varToIndex(self, var)
    self.vars_types_data[indexType][indexVar] = value
    self.vars_types_data_augmented[indexType][indexVar] = var_type_value_augmented(self, type, var, value)
    # Rules on vars
    update_vars_regles(self)
    self.vars_types_data_augmented = [
        [var_type_value_augmented(self, self.vars_types_types[t], self.vars_types_vars[v], self.vars_types_data[t][v])
         for v in range(len(self.vars_types_vars))] for t in range(len(self.vars_types_types))]


def write_nom_type_val(self, type, nom, value):
    type = html.unescape(type)
    nom = html.unescape(nom)
    value = html.unescape(value)

    if self.source == 'csv':
        print('Set type value is not possible for csv file.')
        sys.exit()

    write_nom_type_value_db(self, type, nom, value)

    # mise à jour des tableaux
    indexType = self.noms_types_types.index(type)
    indexNom = nomToIndex(self, nom)
    self.noms_types_data[indexNom][indexType] = value
    self.noms_types_data_augmented[indexNom][indexType] = nom_type_value_augmented(self, type, nom, value)
    # Rules on names
    update_noms_regles(self)
    self.noms_types_data_augmented = [
        [nom_type_value_augmented(self, self.noms_types_types[t], self.noms_types_noms[n], self.noms_types_data[n][t])
         for t in range(len(self.noms_types_types))] for n in range(len(self.noms_types_noms))]


def write_nom_definition(self, nom, definition):
    nom = html.unescape(nom)
    definition = html.unescape(definition)
    if self.source == 'csv':
        write_nom_definition_csv(self, nom, definition)
    else:
        write_nom_definition_db(self, nom, definition)

    #mise à jour des tableaux
    indexNom=nomToIndex(self,nom)
    self.noms_defs_dic[nom]=definition
    self.noms_augmented[indexNom] = nom_augmented(self,nom)



def write_citation(self, nom, var, citation):
    nom = html.unescape(nom)
    var = html.unescape(var)
    citation = html.unescape(citation)
    if self.source == 'csv':
        write_citation_csv(self, nom, var, citation)
    else:
        write_citation_db(self, nom, var, citation)

    # mise à jour des tableaux
    indexNom = nomToIndex(self, nom)
    indexVar = varToIndex(self, var)
    self.citations[indexNom][indexVar] = citation
    self.data_augmented[indexNom][indexVar] = value_augmented(self, self.data[indexNom][indexVar], indexNom,
                                                              indexVar)


def write_nom_thamous(self, nom, table, id, projet):
    if self.source == 'csv':
        print('Operation not possible with csv files.')
        sys.exit()

    write_nom_thamous_db(self, nom, table, id, projet)

    # mise à jour des tableaux
    self.noms_tables_dic[nom] = table
    self.noms_ids_dic[nom] = id
    self.noms_prjts_dic[nom] = projet
    self.noms_augmented[self.noms.index(nom)] = nom_augmented(self, nom)

def write_vars(self, nom, vars=[], varSauf=[],
                    varsTypes=[], varsTypeSauf=[], varsTypesFormule='', domaine = 'all'):


    if not nom in self.noms:
        nom=nomsExtUnique(self, nom)
        if not nom in self.noms:
            print('The name "{}" doesn\'t exist.'.format(nom))
            sys.exit()
    indexNom = self.noms.index(nom)
    indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
    indexesNomsVars = corpusdomaine(self, 'all', domaine, [indexNom], indexesVars)
    indexesVars = indexesNomsVars[1]
    print('Name : "{}".'.format(nom))
    for v in indexesVars:
        value = input(str(self.vars[v]) + ' : {}/'.format(self.data[indexNom][v])) or str(self.data[indexNom][v])
        if value :
            write_val(self, nom, self.vars[v], value)


def write_noms(self, vars=[], varSauf=[],
               varsTypes=[], varsTypeSauf=[], varsTypesFormule='',
               domaine = 'all',
               noms=[], nomSauf=[],
                nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='',
               corpus='all'):
    indexesVars = getIndexesVars(self, toList(vars), varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
    indexesNoms = getIndexesNoms(self, toList(noms), nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
    indexesNomsVars = corpusdomaine(self, corpus, domaine, indexesNoms, indexesVars)
    indexesNoms = indexesNomsVars[0]

    for n in indexesNoms:
        for v in indexesVars:
            value = input(str(self.noms[n]) + ' variable {} : {}/'.format(self.vars[v],self.data[n][v])) or str(
                self.data[n][v])
            if value:
                write_val(self, self.noms[n], self.vars[v], value)

def write_type_vars(self, varsType, vars=[], varSauf=[],
                    varsTypes=[], varsTypeSauf=[], varsTypesFormule='', domaine = 'all'):

    if not varsType in self.vars_types_types:
        print('The variable type "{}" doesn\'t exist.'.format(varsType))
        sys.exit()


    indexType = self.vars_types_types.index(varsType)
    indexesVars = getIndexesVars(self, vars, varSauf, varsTypes, varsTypeSauf, varsTypesFormule)
    indexesNomsVars = corpusdomaine(self, 'all', domaine, [], indexesVars)
    indexesVars = indexesNomsVars[1]
    for v in indexesVars:
        value = input(str(self.vars[v]) + ' : {}/'.format(self.vars_types_data[indexType][v])) or str(self.vars_types_data[indexType][v])
        if value :
            write_var_type_val(self, varsType, self.vars[v], value)

def write_var_types(self, var, varsTypes=[], varsTypeSauf=[]):

    if not var in self.vars:
        print('The variable "{}" doesn\'t exist.'.format(var))
        sys.exit()
    if varsTypes == []:
        varsTypes = self.vars_types_types

    indexVar = self.vars.index(var)
    types = [tp for tp in varsTypes if tp not in varsTypeSauf]
    for type in types:
        indexType = self.vars_types_types.index(type)
        value = input(str(type) + ' : {}/'.format(self.vars_types_data[indexType][indexVar] )) or str(self.vars_types_data[indexType][indexVar])
        if value :
            write_var_type_val(self, type, var, value)

def write_nom_types(self, nom, nomsTypes=[], nomsTypeSauf=[]):
    if not nom in self.noms:
        nom = nomsExtUnique(self, [nom])
        if not nom in self.noms:
            print('The name "{}" doesn\'t exist.'.format(nom))
            sys.exit()
    if nomsTypes == []:
        nomsTypes = self.noms_types_types

    indexNom = self.noms.index(nom)
    types = [tp for tp in nomsTypes if tp not in nomsTypeSauf]
    for type in types:
        indexType = self.vars_types_types.index(type)
        value = input(str(type) + ' : {}/'.format(self.noms_types_data[indexNom][indexType])) or  str(self.noms_types_data[indexNom][indexType])
        if value :
            write_nom_type_val(self, type, nom, value)

def write_type_noms(self, nomsType, noms=[], nomSauf=[],
                    nomsTypes=[], nomsTypeSauf=[], nomsTypesFormule='', corpus = 'all'):

    if not nomsType in self.noms_types_types:
        print('The name type "{}" doesn\'t exist.'.format(varsType))
        sys.exit()

    indexType = self.noms_types_types.index(nomsType)
    indexesNoms = getIndexesNoms(self, noms, nomSauf, nomsTypes, nomsTypeSauf, nomsTypesFormule)
    indexesNomsVars = corpusdomaine(self, corpus, 'all', indexesNoms, [])
    indexesNoms = indexesNomsVars[0]
    for n in indexesNoms:
        value = input(str(self.noms[n]) + ' : {}/'.format(self.noms_types_data[n][indexType])) or str(self.noms_types_data[n][indexType])
        if value :
            write_nom_type_val(self, type, self.noms[n], value)








