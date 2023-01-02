import sqlite3 as sq
import sys
import os

from .basics import *
from .types import *
from .thamous import *

vars_first_cols = ['id', 'indexx', 'nom', 'def']
noms_first_cols = ['id', 'indexx', 'nom', 'def',  'thmtable','thmid','thmprojet']

def newProject(self,db):

    try:
        co=sq.connect(db)
        print(str(db)+" opened successfully...")
        self.db=db
    except:
        print("Cannot open " + str(db))
        sys.exit()

    co.execute('''CREATE TABLE tdata
             (id INTEGER PRIMARY KEY AUTOINCREMENT);''')

    co.execute('''CREATE TABLE tcitations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT);''')

    co.execute('''CREATE TABLE tvars
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 indexx INT,
                 nom  TEXT  NOT NULL UNIQUE,
                 def TEXT );''')

    co.execute('''CREATE TABLE tvars_types
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     indexx INT,
                     nom  TEXT  NOT NULL UNIQUE,
                     def TEXT,
                     rule TEXT);''')


    co.execute('''CREATE TABLE tnoms
                     (id INTEGER  PRIMARY KEY AUTOINCREMENT,
                     indexx INT,
                     nom  TEXT  NOT NULL UNIQUE,
                     def TEXT,
                     thmtable TEXT,
                     thmid INT,
                     thmprojet TEXT);''')

    co.execute('''CREATE TABLE tnoms_types
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         indexx INT,
                         nom  TEXT  NOT NULL UNIQUE,
                         def TEXT,
                         rule TEXT);''')


def indexVarToId_db(self, indexVar, db=''):
    if db == '' : db = self.db
    co = sq.connect(db)
    rq = "SELECT id FROM tvars WHERE indexx = ?"
    rows = list(co.execute(rq,(indexVar,)))
    id = rows[0][0]
    return id

def indexNomToId_db(self, indexNom, db=''):
    if db == '' : db = self.db
    co = sq.connect(db)
    rq = "SELECT id FROM tnoms WHERE indexx = ?"
    rows = list(co.execute(rq,(indexNom,)))
    id = rows[0][0]
    return id

def indexVarTypeToId_db(self, indexVarType, db=''):
    if db == '' : db = self.db
    co = sq.connect(db)
    rq = "SELECT id FROM tvars_types WHERE indexx = ?"
    rows = list(co.execute(rq,(indexVarType,)))
    id = rows[0][0]
    return id

def indexNomTypeToId_db(self, indexNomType, db=''):
    if db == '' : db = self.db
    co = sq.connect(db)
    rq = "SELECT id FROM tnoms_types WHERE indexx = ?"
    rows = list(co.execute(rq,(indexNomType,)))
    id = rows[0][0]
    return id

def reindexplus(self, table, start, db=''):
    if db == '': db = self.db
    co=sq.connect(db)
    rq = "UPDATE " + table + " SET indexx = indexx+1 WHERE indexx >=  " + str(start)
    co.execute(rq)
    co.commit()



def add_var_db(self,newV, var = '',indexNewVar='', position = 'after', db=''):
    if db == '' : db = self.db
    co=sq.connect(db)

    if not indexNewVar:
        if var:
            indexVar = self.vars.index(var)
            if position == 'before':
                indexNewVar = indexVar
            else:
                indexNewVar = indexVar + 1
        else:
            if position == 'last':
                indexNewVar = len(self.vars)
            else:
                indexNewVar = 0

        reindexplus(self, 'tvars', indexNewVar, db=db)


    rqData = '''ALTER TABLE tdata ADD "''' + newV.replace('"', '""') + '''" TEXT  DEFAULT '' '''
    rqCitations = '''ALTER TABLE tcitations ADD "''' + newV.replace('"', '""') + '''" TEXT  DEFAULT '' '''
    co.execute(rqData)
    co.execute(rqCitations)

    rqVars = '''INSERT INTO tvars (indexx, nom) VALUES (?, ?) '''
    co.execute(rqVars, (indexNewVar, newV.replace('"', '""')))
    co.commit()


def add_vars_db(self,newVars, var = '', position = 'after', db=''):
    for newVar in newVars:
        add_var_db(self, newVar, var = var, position = position, db=db)
        var = newVar
        position = 'after'

def show_noms_db(self,db=''):
    if db == '': db = self.db
    co = sq.connect(db)
    rqNomsTest = '''SELECT * FROM 'tnoms' WHERE 1 '''
    cur = co.cursor()
    cur.execute(rqNomsTest)
    rows = cur.fetchall()
    print(rows)

def show_vars_db(self,db=''):
    if db == '': db = self.db
    co = sq.connect(db)
    rqVarsTest = '''SELECT * FROM 'tvars' WHERE 1 '''
    cur = co.cursor()
    cur.execute(rqVarsTest)
    rows = cur.fetchall()
    print(rows)

def add_nom_db(self,newNom, nom = '',indexNewNom='', position = 'after', db=''):
    if db == '' : db = self.db
    co=sq.connect(db)

    if not indexNewNom:
        if nom:
            indexNom = self.noms.index(nom)
            if position == 'before':
               indexNewNom = indexNom
            else:
                indexNewNom = indexNom + 1
        else:
            if position == 'last':
                indexNewNom = len(self.noms)
            else:
                indexNewNom = 0

        reindexplus(self, 'tnoms', indexNewNom, db=db)

    rqNoms = '''INSERT INTO tnoms (indexx, nom) VALUES (?, ?) '''
    rqData = '''INSERT INTO tdata DEFAULT VALUES '''
    rqCitations = '''INSERT INTO tcitations DEFAULT VALUES '''

    co.execute(rqNoms, (indexNewNom, newNom.replace('"', '""')))
    co.execute(rqData)
    co.execute(rqCitations)

    co.commit()



def add_noms_db(self,newNoms, nom = '', position = 'after', db = ''):
    for newNom in newNoms:
        add_nom_db(self, newNom, nom = nom, position = position,db=db)
        nom = newNom
        position = 'after'

def add_thamous_db(self, id_thm, table, projet, newNom, nom, position = 'after', db = ''):
    add_nom_db(newNom, nom, position = position, db = db)
    write_nom_thamous_db(self, newNom, table, id_thm, projet)
    definition = thamous_ref(id_thm, table)
    write_nom_definition_db(self, nom, definition)


def rename_var_db(self,var, newVar):
    co=sq.connect(self.db)
    rqData = '''ALTER TABLE tdata RENAME COLUMN "{}" TO "{}"'''.format(var,newVar)
    rqCitations = '''ALTER TABLE tcitations RENAME COLUMN "{}" TO "{}" '''.format(var,newVar)
    co.execute(rqData)
    co.execute(rqCitations)

    rqVars = '''UPDATE  tvars SET  nom = ? WHERE nom = ?'''
    co.execute(rqVars, (newVar, var))
    co.commit()



def rename_nom_db(self,nom,newNom):
    co=sq.connect(self.db)

    rqNoms = '''UPDATE  tnoms SET  nom = ? WHERE nom = ?'''
    co.execute(rqNoms, (newNom, nom))
    co.commit()

def rename_vars_type_db(self,varType,newVarType):
    co=sq.connect(self.db)

    rq = '''UPDATE  tvars_types SET  nom = ? WHERE nom = ?'''
    co.execute(rq, (newVarType, varType))

    rqVars = '''ALTER TABLE tvars  RENAME COLUMN `{}` TO `{}` '''.format(varType,newVarType)
    co.execute(rqVars)
    co.commit()


def rename_noms_type_db(self, nomType, newNomType):
    co = sq.connect(self.db)

    rq = '''UPDATE  tnoms_types SET  nom = ? WHERE nom = ?'''
    co.execute(rq, (newNomType, nomType))

    rqNoms = '''ALTER TABLE tnoms  RENAME COLUMN `{}` TO `{}` '''.format(nomType, newNomType)
    co.execute(rqNoms)
    co.commit()

def add_noms_type_db(self, newT, nomsType='', position='after', db=''):
    if db == '' : db = self.db
    co = sq.connect(db)

    if nomsType:
        try :
            indexType = self.noms_types_types.index(nomsType)
        except valueError:
            print('The type \"" + type + "\" is not recognized')
            sys.exit(1)

        if position == 'before':
            if indexType == 0:
                indexNewType = 0
            else:
                indexNewType = indexType - 1
        else:
            indexNewType = indexType + 1

    else:
        if position == 'last' :
            indexNewType = len(self.noms_types_types)
        else:
            indexNewType = 0

    rqNoms = '''ALTER TABLE tnoms ADD "{}" TEXT  DEFAULT '' '''.format(newT.replace('"','""'))
    co.execute(rqNoms)

    reindexplus(self, 'tnoms_types', indexNewType, db=db)
    rqTypes = '''INSERT INTO tnoms_types (indexx, nom) VALUES (?, ?) '''
    co.execute(rqTypes, (indexNewType, newT))
    co.commit()

def add_vars_type_db(self, newT, varsType='', position='after', db=''):
    if db == '' : db = self.db
    co = sq.connect(db)

    if varsType:
        try:
            indexType = self.vars_types_types.index(varsType)
        except valueError:
            print("The type \"" + varsType + "\" is not recognized")
            sys.exit(1)

        if position == 'before':
            if indexType == 0:
                indexNewType = 0
            else:
                indexNewType = indexType - 1
        else:
            indexNewType = indexType + 1

    else:
        if position == 'last':
            indexNewType = len(self.vars_types_types)
        else:
            indexNewType = 0

    rqVars = '''ALTER TABLE tvars ADD "{}" TEXT  DEFAULT '' '''.format(newT.replace('"','""'))
    co.execute(rqVars)

    reindexplus(self, 'tvars_types', indexNewType, db=db)
    rqTypes = '''INSERT INTO tvars_types (indexx, nom) VALUES (?, ?) '''
    co.execute(rqTypes, (indexNewType, newT))
    co.commit()



def write_val_db(self,nom, var, value):
    idNomSql = indexNomToId_db(self, self.noms.index(nom))
    co = sq.connect(self.db)
    rq='''UPDATE tdata SET "{}"  = ? WHERE id = ?'''.format(var.replace('"','""'))
    co.execute(rq, (value, idNomSql))
    co.commit()

def write_citation_db(self, nom, var, citation):
    idNomSql = indexNomToId_db(self, self.noms.index(nom))
    co = sq.connect(self.db)
    rq='''UPDATE tcitations SET "{}" = ? WHERE id = ?'''.format(var.replace('"','""'))
    co.execute(rq, (citation, idNomSql))
    co.commit()

def write_var_type_value_db(self, type, var, value = '*'):
    co = sq.connect(self.db)
    rq='''UPDATE tvars SET "{}"  = ? WHERE nom = ?'''.format(type.replace('"','""'))
    co.execute(rq, (value, var))
    co.commit()

def write_nom_type_value_db(self, type, nom, value = '*'):
    co = sq.connect(self.db)
    rq='''UPDATE tnoms SET "{}"  = ? WHERE nom = ?'''.format(type.replace('"','""'))
    co.execute(rq, (value, nom))
    co.commit()

def write_var_definition_db(self, var, definition):
    co = sq.connect(self.db)
    rq='''UPDATE tvars SET 'def'  = ? WHERE nom = ?'''
    co.execute(rq, (definition, var))
    co.commit()

def write_nom_definition_db(self,nom, definition):
    co = sq.connect(self.db)
    rq='''UPDATE tnoms SET 'def' = ? WHERE nom = ?'''
    co.execute(rq, (definition, nom))
    co.commit()

def write_nom_thamous_db(self, nom, table, id, projet ):
    co = sq.connect(self.db)
    rq = '''UPDATE tnoms SET 'thmtable' = ?, 'thmid' = ?, 'thmprojet' = ? WHERE nom = ?'''
    co.execute(rq, (table, id, projet, nom))
    co.commit()


def get_data_db(self):
    co = sq.connect(self.db)
    cur = co.cursor()
    cur.execute("SELECT tdata.* FROM tdata LEFT JOIN  tnoms ON tnoms.id =  tdata.id ORDER BY tnoms.indexx ASC")
    rows = cur.fetchall()

    cur.execute("SELECT indexx FROM tvars")
    varscols = cur.fetchall()
    varsIndexToId = {varscols[i][0]:i for i in range(len(varscols))}
    data = []
    for row in rows:
        # +1 because of the column id of data
        row = list(row)[1:]
        line = [row[varsIndexToId[i]] for i in range(len(self.vars))]
        data.append(line)
    return np.array(data)


def get_citations_db(self):
    co = sq.connect(self.db)
    cur = co.cursor()
    cur.execute("SELECT tcitations.* FROM tcitations LEFT JOIN  tnoms ON tnoms.id =  tcitations.id ORDER BY tnoms.indexx ASC")
    rows = cur.fetchall()

    cur.execute("SELECT indexx FROM tvars ")
    varscols = cur.fetchall()
    varsIndexToId = {varscols[i][0]:i for i in range(len(varscols))}

    citations = []
    for row in rows:
        # +1 because of the column id of data
        row = list(row)[1:]
        line = [row[varsIndexToId[i]] for i in range(len(self.vars))]
        citations.append(line)

    return citations

def get_vars_db(self):
    co = sq.connect(self.db)
    rows = co.execute("SELECT nom FROM tvars ORDER BY indexx ASC")
    vars = [row[0] for row in rows]
    return vars

def get_noms_db(self):
    co = sq.connect(self.db)
    rows = co.execute("SELECT nom FROM tnoms ORDER BY indexx ASC")
    noms = [row[0] for row in rows]
    return noms

def get_noms_thm_tables_dic_db(self):
    co = sq.connect(self.db)
    rows = co.execute("SELECT nom, thmtable FROM tnoms ORDER BY indexx ASC")
    thmtables = {row[0]:row[1] for row in rows}
    return thmtables

def get_noms_thm_ids_dic_db(self):
    co = sq.connect(self.db)
    rows = co.execute("SELECT nom, thmid FROM tnoms ORDER BY indexx ASC")
    thmids = {row[0]:row[1] for row in rows}
    return thmids

def get_noms_thm_projets_dic_db(self):
    co = sq.connect(self.db)
    rows = co.execute("SELECT nom, thmprojet FROM tnoms ORDER BY indexx ASC")
    thmprojets = {row[0]:row[1] for row in rows}
    return thmprojets

def get_vars_types_db(self):
    co = sq.connect(self.db)
    rows = co.execute("SELECT nom FROM tvars_types ORDER BY indexx ASC")
    types = [row[0] for row in rows]
    return types

def get_vars_regles_db(self,db):
    co = sq.connect(db)
    rows = co.execute("SELECT nom, rule  FROM tvars_types ORDER BY tvars_types.indexx ASC")
    regles = {row[0]:row[1] for row in rows}
    return regles

def get_noms_types_db(self):
    co = sq.connect(self.db)
    rows = co.execute("SELECT nom FROM tnoms_types ORDER BY indexx ASC")
    types = [row[0] for row in rows]
    return types

def get_noms_regles_db(self,db):
    co = sq.connect(db)
    rows = co.execute(
        "SELECT nom, rule  FROM tnoms_types ORDER BY tnoms_types.indexx ASC")
    regles = {row[0]: row[1] for row in rows}
    return regles

def get_vars_types_data_db(self):
    co = sq.connect(self.db)
    cur = co.cursor()
    cur.execute("SELECT * FROM tvars ORDER BY tvars.indexx ASC")
    rows = cur.fetchall()

    cur.execute("SELECT indexx FROM tvars_types")
    typescols = cur.fetchall()
    typesIndexToId = {typescols[i][0]: i for i in range(len(typescols))}

    data = []
    for row in rows:
        row = list(row)[len(vars_first_cols):]
        line = [row[typesIndexToId[i]] for i in range(len(self.vars_types_types))]
        data.append(line)

    return np.transpose(np.array(data))


def get_noms_types_data_db(self):
    co = sq.connect(self.db)
    cur = co.cursor()
    cur.execute("SELECT * FROM tnoms ORDER BY tnoms.indexx ASC")
    rows = cur.fetchall()

    cur = co.execute("SELECT indexx FROM tnoms_types")
    typescols = cur.fetchall()
    typesIndexToId = {typescols[i][0]: i for i in range(len(typescols))}

    data = []
    for row in rows:
        row = list(row)[len(noms_first_cols):]
        line = [row[typesIndexToId[i]] for i in range(len(self.noms_types_types))]
        data.append(line)

    return np.array(data)


def get_vars_defs_dic_db(self):
    co = sq.connect(self.db)
    rows = co.execute("SELECT nom, def FROM tvars")
    varsDefsDic = {row[0]: row[1] for row in rows}
    return varsDefsDic

def get_noms_defs_dic_db(self):
    co = sq.connect(self.db)
    rows = co.execute("SELECT nom, def FROM tnoms")
    nomsDefsDic = {row[0]: row[1] for row in rows}
    return nomsDefsDic

def get_vars_types_defs_dic_db(self):
    co = sq.connect(self.db)
    rows = co.execute("SELECT nom, def FROM tvars_types")
    varsTypesDefsDic = {row[0]: row[1] for row in rows}
    return varsTypesDefsDic

def get_noms_types_defs_dic_db(self):
    co = sq.connect(self.db)
    rows = co.execute("SELECT nom, def FROM tnoms_types")
    nomsTypesDefsDic = {row[0]: row[1] for row in rows}
    return nomsTypesDefsDic

def delete_db(self, var='', nom='', varsType='', nomsType=''):
    co=sq.connect(self.db)
    db, ext = os.path.splitext(self.db)
    db_temp = db+'_temp.db'

    create_empty_db(db_temp)

    vars =  self.vars
    if var :
        indexDelVar=vars.index(var)
        vars.remove(var)
    else:
        indexDelVar = -1

    for newV in vars:
        add_var_db(self, newV)

    noms = self.noms
    if nom:
        indexDelNom=noms.index(nom)
        noms.remove(nom)
    else:
        indexDelNom = -1
    for nom in noms:
        add_nom_db(self, nom)

    varsTypes = self.vars_types_types
    if varsType:
        indexDelVarsType=varsTypes.index(varsType)
        varsTypes.remove(varsType)
    else :
        indexDelVarsType = -1

    type = ''
    for newtype in varsTypes:
        add_vars_type_db(self, newtype, type)
        type = newtype

    nomsTypes = self.noms_types_types
    if nomsType:
        indexDelNomsType=nomsTypes.index(nomsType)
        nomsTypes.remove(nomsType)
    else:
        indexDelNomsType= -1

    type = ''
    for newtype in nomsTypes:
        add_noms_type_db(self, newtype, type)
        type = newtype

    colsVarsList = vars_first_cols[1:] + varsTypes
    colsVars = ', '.join(['''"{}" = ?'''.format(col.replace('"', '""')) for col in colsVarsList])

    colsDataList = vars
    colsData = ', '.join([ '''"{}" = ?'''.format(col.replace('"', '""')) for col in colsDataList])

    colsNomsList = noms_first_cols[1:] + nomsTypes
    colsNoms = ', '.join(['''"{}" = ?'''.format(col.replace('"', '""')) for col in colsNomsList])


    for i in range(len(noms)):
        if i >= indexDelNom >=0: ii = i+1
        else: ii = i
        id = indexNomToId_db(self, i)

        values = tuple(self.data[ii])
        rqData = '''UPDATE tdata SET ''' + colsData + ''' WHERE id = ''' + str(id)
        co.execute(rqData, values)

        values = tuple(self.citations[ii])
        rqCitations = '''UPDATE tcitations SET ''' + colsData + ''' WHERE  id = ''' + str(id)
        co.execute(rqCitations, values)
        nom = self.noms[ii]
        try:
            thmtable = self.noms_tables_dic[nom]
            thmid = self.noms_ids_dic[nom]
            thmprojet = self.noms_prjts_dic[nom]
        except:
            thmtable = ''
            thmid = 0
            thmprojet = ''

        values = tuple([i, self.noms[ii], self.noms_defs_dic[self.noms[ii]], thmtable, thmid, thmprojet] + self.noms_types_data[ii])
        rqNoms = '''UPDATE tnoms SET ''' + str(colsNoms) + ''' WHERE id = ''' + str(id)
        co.execute(rqNoms, values)

    for type, regle in self.nomsRegles.items():
        values = (type, regle)
        rqNomsRules = '''INSERT INTO tnomsrules (type, rule) VALUES (?, ?) '''
        co.execute(rqNomsRules, values)

    for i in range(len(self.vars)):
        if i >= indexDelVar >=0: ii = i+1
        else: ii = i
        values = tuple([i, self.vars[ii], self.vars_defs_dic[self.vars[ii]]] + [varsTypesData[j][i] for j in range(len(self.vars_types_types))])
        rqVars = '''UPDATE tvars SET ''' + str(colsVars) + ''' WHERE indexx =  ''' + str(i)
        co.execute(rqVars, values)

    for type, regle in self.varsRegles.items():
        values = (type, regle)
        rqVarsRules = '''INSERT INTO tvarsrules (type, rule) VALUES (?, ?) '''
        co.execute(rqVarsRules, values)

    co.commit()



def load_db(self, db):
    co = sq.connect(db)
    #existence de la base
    cursor = co.execute('''SELECT name FROM sqlite_master
                            WHERE
                            type = 'table'
                            AND
                            name = 'tdata';''')

    table = ''
    for row in cursor:
        table = row[0]
    if not table:
        print("The database \""+db+"\" doesn't exist.")
        answer = input("Do you want to create it ? (yes/no) ")
        if answer == 'yes' or answer =='y':
            newProject(self, db)
        else:
            os._exit(1)
    else:
        self.db = db


    variables = get_vars_db(self)
    self.vars = variables
    self.selectedVars = variables
    self.selectedIndexesVars = [i for i in range(len(self.selectedVars))]

    noms = get_noms_db(self)
    self.noms = noms
    self.selectedNoms = noms
    self.selectedIndexesNoms = [i for i in range(len(self.selectedNoms))]

    self.varsTypes_exists = True
    self.vars_types_types = get_vars_types_db(self)
    self.vars_types_data = get_vars_types_data_db(self)
    self.vars_types_vars = self.vars
    self.vars_types_defs_dic = get_vars_types_defs_dic_db(self)
    self.vars_types_with_def = [t for t in self.vars_types_types if self.vars_types_defs_dic[t]]
    self.vars_types_without_def = [t for t in self.vars_types_types if not self.vars_types_defs_dic[t]]

    # Application  des règles sur les types de variables
    update_vars_regles(self)
    self.vars_types_data_augmented = [[var_type_value_augmented(self, self.vars_types_types[t], self.vars_types_vars[v], self.vars_types_data[t][v]) for v in range(len(self.vars_types_vars))] for t in range(len(self.vars_types_types))]


    self.nomsTypes_exists = True
    self.noms_types_types = get_noms_types_db(self)
    self.noms_types_data = get_noms_types_data_db(self)
    self.noms_types_noms = self.noms
    self.noms_types_defs_dic = get_noms_types_defs_dic_db(self)
    self.names_types_with_def = [t for t in self.noms_types_types if self.noms_types_defs_dic[t]]
    self.names_types_without_def = [t for t in self.noms_types_types if not self.noms_types_defs_dic[t]]

    # Application des règles sur les types de noms
    update_noms_regles(self)
    self.noms_types_data_augmented = [[nom_type_value_augmented(self, self.noms_types_types[t], self.noms_types_noms[n], self.noms_types_data[n][t]) for t in range(len(self.noms_types_types))] for n in range(len(self.noms_types_noms))]

    self.noms_tables_dic = get_noms_thm_tables_dic_db(self)
    self.noms_ids_dic = get_noms_thm_ids_dic_db(self)
    self.noms_prjts_dic = get_noms_thm_projets_dic_db(self)



    self.vars_defs_dic = get_vars_defs_dic_db(self)
    self.varsDefs_exists = True


    self.noms_defs_dic = get_noms_defs_dic_db(self)
    self.nomsDefs_exists = True

    data = get_data_db(self)
    self.data = data
    self.selectedData = data

    self.vars_augmented = vars_augmented(self, self.vars)
    self.vars_sans_def = [v for v in self.vars if self.vars_defs_dic[v] == '']

    self.noms_augmented = noms_augmented(self, self.noms)
    self.names_without_def = [n for n in self.noms if self.noms_defs_dic[n] == '']

    self.citations_exists = True
    self.citations = get_citations_db(self)

    self.data_augmented = data_augmented(self)

    self.poidsExist = False


def update_noms_regles(self):
    regles = get_noms_regles_db(self,self.db)
    self.noms_types_data = applyRegles(self, self.noms_types_data,
                                       self.noms_types_types,
                                       regles)
    self.noms_types_data_augmented = [[nom_type_value_augmented(self, self.noms_types_types[t], self.noms_types_noms[n], self.noms_types_data[n][t]) for t in range(len(self.noms_types_types))] for n in range(len(self.noms_types_noms))]

def update_vars_regles(self):
    regles = get_vars_regles_db(self,self.db)
    self.vars_types_data = applyRegles(self, self.vars_types_data,
                                       self.vars_types_types,
                                       regles)
    self.vars_types_data_augmented = [[var_type_value_augmented(self, self.vars_types_types[t], self.vars_types_vars[v], self.vars_types_data[t][v]) for v in range(len(self.vars_types_vars))] for t in range(len(self.vars_types_types))]


def delete_nom_db(self, nom):
    # table des noms :
    #   - supprimer la ligne
    #   - réindexer les lignes : si indexx > indexNom : indexx-=1
    #table des data :
    #   - supprimer la ligne
    #table des citations
    #   - supprimer la ligne

    if nom in self.noms:
        indexNom = self.noms.index(nom)
        index = indexNomToId_db(self, indexNom)
    else:
        print(color.bold + 'The name "{}" doesn\'t exist.'.format(nom)+color.end)
        sys.exit()

    try:
        # table des noms :
        #   - supprimer la ligne

        co=sq.connect(self.db)
        cur = co.cursor()
        rq = "DELETE FROM tnoms WHERE indexx =  "+str(indexNom)
        cur.execute(rq)



        # table des noms :
        #   - réindexer les lignes : si indexx > indexNom : indexx-=1

        rq = "UPDATE tnoms SET indexx = indexx - 1 WHERE  indexx > " + str(indexNom)
        cur.execute(rq)


        # table des data :
        #   - supprimer la ligne
        rq = "DELETE FROM tdata WHERE id =  " + str(index)
        cur.execute(rq)


        # table des citations
        #   - supprimer la ligne
        rq = "DELETE FROM tcitations WHERE id =  " + str(index)
        cur.execute(rq)
        co.commit()

    except sq.Error as error:
        print("Error when deleting the name \"{}\"".format(nom), error)


def delete_var_db(self, var):
    # tvars :
    #   - delete row
    #   - redinxing
    # tdata :
    #   - delete column

    # tcitations
    #   - delete column

    if var in self.vars:
        indexVar = self.vars.index(var)
    else:
        print(color.bold + 'The variable "{}" doesn\'t exist.'.format(var) + color.end)
        sys.exit()

    try:
        co = sq.connect(self.db)
        cur = co.cursor()

        # table des vars :
        #   - supprimer la ligne
        rq = "DELETE FROM tvars WHERE indexx =  " + str(indexVar)
        cur.execute(rq)

        # table des noms :
        #   - réindexer les lignes : si indexx > indexVar : indexx-=1

        rq = "UPDATE tvars SET indexx = indexx - 1 WHERE  indexx > " + str(indexVar)
        cur.execute(rq)
        co.commit()

        # table des data :
        #   - supprimer la colonne

        drop_col_db(self, 'tdata', var)

        # table des citations
        #   - supprimer la ligne
        drop_col_db(self, 'tcitations', var)

    except sq.Error as error:
        print("Error when deleting the variable \"{}\"".format(var), error)

def delete_noms_type_db(self, type):
    # tnoms :
    #   - delete the column of the type
    # tnoms_types  :
    #   - delete the row
    #   - reindixing

    # tnomsrules
    #   - delete the row (if exists)
    #   - delete the type in the rules where it occurs

    if type in self.noms_types_types:
        indexType = self.noms_types_types.index(type)
    else:
        print(color.bold + 'The name type  "{}" doesn\'t exist.'.format(type) + color.end)
        sys.exit()

    try:

        co = sq.connect(self.db)
        cur = co.cursor()

        # tnoms :
        #   - delete the column of the type
        drop_col_db(self, 'tnoms', type)

        # tnoms_types :
        #   - delete the row
        rq = "DELETE FROM tnoms_types WHERE indexx =  " + str(indexType)
        cur.execute(rq)

        # tvars_types :
        #   - reindexing

        rq = "UPDATE tnoms_types SET indexx = indexx - 1 WHERE  indexx > " + str(indexType)
        cur.execute(rq)
        co.commit()

        # tvarsrules
        #   - delete the row (if exists)
        rq = "DELETE FROM tnomsrules WHERE type =  \"{}\"".format(type)
        cur.execute(rq)


        # tnomsrules
        #   - delete the type in the rules where it occurs
        #TODO
        print("The name type \"{}\" must be delete from the rules where it occurs.".format(type))


    except sq.Error as error:
        print("Error when deleting the name type \"{}\"".format(type), error)



def delete_vars_type_db(self, type):
    # tvars :
    #   - delete the column of the type
    # tvars_types  :
    #   - delete the row
    #   - reindixing

    # tvarsrules
    #   - delete the row (if exists)
    #   - delete the type in the rules where it occurs

    if type in self.vars_types_types:
        indexType = self.vars_types_types.index(type)
    else:
        print(color.bold + 'The variable type  "{}" doesn\'t exist.'.format(type) + color.end)
        sys.exit()

    try:

        co = sq.connect(self.db)
        cur = co.cursor()

        # tvars :
        #   - delete the column of the type
        drop_col_db(self, 'tvars', type)

        # tvars_types :
        #   - delete the row
        rq = "DELETE FROM tvars_types WHERE indexx =  " + str(indexType)
        cur.execute(rq)

        # tvars_types :
        #   - reindexing

        rq = "UPDATE tvars_types SET indexx = indexx - 1 WHERE  indexx > " + str(indexType)
        cur.execute(rq)
        co.commit()

        # tvarsrules
        #   - delete the row (if exists)
        rq = "DELETE FROM tvarsrules WHERE type =  \"{}\"".format(type)
        cur.execute(rq)


        # tvarsrules
        #   - delete the type in the rules where it occurs
        #TODO
        print("The variable type \"{}\" must be delete from the rules where it occurs.".format(type))


    except sq.Error as error:
        print("Error when deleting the variable type \"{}\"".format(type), error)


def create_empty_db(db):
    if os.path.isfile(db):
        print(color.bold+"The database \""+db+"\" already exists"+color.end)
        sys.exit()
    try:
        co = sq.connect(db)
        print( str(db) + " opened successfully...")
    except:
        print("Cannot open " + str(db))
        sys.exit()

    co.execute('''CREATE TABLE tdata
             (id INTEGER PRIMARY KEY AUTOINCREMENT);''')

    co.execute('''CREATE TABLE tcitations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT);''')

    co.execute('''CREATE TABLE tvars
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 indexx INT,
                 nom  TEXT  NOT NULL,
                 def TEXT );''')

    co.execute('''CREATE TABLE tvars_types
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     indexx INT,
                     nom  TEXT  NOT NULL,
                     def TEXT,
                     rule TEXT);''')

    co.execute('''CREATE TABLE tnoms
                     (id INTEGER  PRIMARY KEY AUTOINCREMENT,
                     indexx INT,
                     nom  TEXT  NOT NULL,
                     thmtable TEXT,
                     thmid INT,
                     thmprojet TEXT,
                     def TEXT);''')

    co.execute('''CREATE TABLE tnoms_types
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        indexx INT,
                        nom  TEXT  NOT NULL,
                        def TEXT,
                        rule TEXT);''')



def saveToDb(self):
    db = input ("Database name : ")
    if not '.db' in db :
        db = db + '.db'

    print('Wait...')

    create_empty_db(db)
    co = sq.connect(db)

    for newV in self.vars:
        add_var_db(self, newV,indexNewVar=self.vars.index(newV),db=db)

    for newN in self.noms:
        add_nom_db(self, newN,indexNewNom=self.noms.index(newN), db=db)

    type = ''
    for newtype in self.vars_types_types:
        add_vars_type_db(self, newtype, type,db=db)
        type = newtype

    type = ''
    for newtype in self.noms_types_types:
        add_noms_type_db(self, newtype, type,db=db)
        type = newtype

    colsVarsList = vars_first_cols[1:] + self.vars_types_types
    colsVars = ', '.join(['''"{}" = ?'''.format(col.replace('"', '""')) for col in colsVarsList])

    colsDataList = self.vars
    colsData = ', '.join([ '''"{}" = ?'''.format(col.replace('"', '""')) for col in colsDataList])

    colsNomsList = noms_first_cols[1:] + self.noms_types_types
    colsNoms = ', '.join(['''"{}" = ?'''.format(col.replace('"', '""')) for col in colsNomsList])


    for indexNom in range(len(self.noms)):
        nom = self.noms[indexNom]
        try:
            thmtable = self.noms_tables_dic[nom]
            thmid = self.noms_ids_dic[nom]
            thmprojet = self.noms_prjts_dic[nom]
        except:
            thmtable = ''
            thmid = 0
            thmprojet = ''

        nomsValues = tuple(
            [indexNom, nom, self.noms_defs_dic[nom], thmtable, thmid, thmprojet] + self.noms_types_data[indexNom])
        rqNoms = '''UPDATE tnoms SET ''' + str(colsNoms) + ''' WHERE indexx = ''' + str(indexNom)
        co.execute(rqNoms, nomsValues)

        dataValues = tuple(self.data[indexNom])
        rqData = '''UPDATE tdata SET ''' + colsData + ''' WHERE id = ''' + str(indexNom+1)
        co.execute(rqData, dataValues)

        if self.citations_exists:
            CitationsValues = tuple(self.citations[indexNom])
            rqCitations = '''UPDATE tcitations SET ''' + colsData + ''' WHERE  id = ''' + str(indexNom+1)
            co.execute(rqCitations, CitationsValues)

    for type, regle in self.nomsRegles.items():
        nomsReglesValues = (regle,type)
        rqNomsRules = '''UPDATE  tnoms_types SET "rule"= ? WHERE nom = ? '''
        co.execute(rqNomsRules,nomsReglesValues)



    for indexVar in range(len(self.vars)):
        var=self.vars[indexVar]
        values = tuple([indexVar, var, self.vars_defs_dic[var]] + [self.vars_types_data[j][indexVar] for j in range(len(self.vars_types_types))])
        rqVars = '''UPDATE tvars SET ''' + str(colsVars) + ''' WHERE id =  ''' + str(indexVar+1)
        co.execute(rqVars, values)

    for type, regle in self.varsRegles.items():
        varsReglesValues = (regle, type)
        rqVarsRules = '''UPDATE  tvars_types SET "rule"= ? WHERE nom = ? '''
        co.execute(rqVarsRules, varsReglesValues)


    #defs of types are ignored

    co.commit()
    print('Database saved.')


def drop_col_db(self, table, col):
    co = sq.connect(self.db)
    cur = co.cursor()
    #columns of the table
    cur.execute("SELECT * FROM {}".format(table))
    cols = [description[0] for description in cur.description]

    tabletp=table+'_temp'

    if not col in cols:
        print(color.bold + "\"{}\" is not a column of the table \"{}\".".format(col, table) + color.end)
        sys.exit()
    #remove the column
    cols.remove(col)

    if table == 'tdata':
            co.execute('''CREATE TABLE tdata_temp
                         (id INTEGER PRIMARY KEY AUTOINCREMENT);''')
            colsInit=['id']

    elif table ==  'tcitations':
            co.execute('''CREATE TABLE tcitations_temp
                             (id INTEGER PRIMARY KEY AUTOINCREMENT);''')
            colsInit = ['id']

    elif table ==  'tvars':
            co.execute('''CREATE TABLE tvars_temp
                             (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             indexx INT,
                             nom  TEXT  NOT NULL,
                             def TEXT );''')
            colsInit = ['id','indexx','nom','def']

    elif table ==  'tvars_types':
            co.execute('''CREATE TABLE tvars_types_temp
                                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                 indexx INT,
                                 nom  TEXT  NOT NULL,
                                 def TEXT,
                                 rule TEXT);''')
            colsInit = ['id','indexx','nom','def','rule']


    elif table == 'tnoms':
            co.execute('''CREATE TABLE tnoms_temp
                                 (id INTEGER  PRIMARY KEY AUTOINCREMENT,
                                 indexx INT,
                                 nom  TEXT  NOT NULL,
                                 thmtable TEXT,
                                 thmid INT,
                                 thmprojet TEXT,
                                 def TEXT);''')
            colsInit = ['id','indexx','nom','thmtable','thmid', 'thmprojet','def']

    elif table == 'tnoms_types':
            co.execute('''CREATE TABLE tnoms_types_temp
                                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    indexx INT,
                                    nom  TEXT  NOT NULL,
                                    def TEXT,
                                    rule TEXT);''')
            colsInit = ['id','indexx','nom','def','rule']



    #add cols (without col)
    for c in cols:
        if not c in colsInit:
            rq = '''ALTER TABLE {} ADD `{}` TEXT  DEFAULT '' '''.format(tabletp,c)
            cur.execute(rq)

    #copy values
    colsStr = ', '.join(['''"{}"'''.format(col.replace('"', '""')) for col in cols])
    rq = "INSERT INTO {}  ({}) SELECT {} FROM  {}".format(tabletp, colsStr,colsStr, table)
    cur.execute(rq)

    #delete previous table
    rq = "DROP TABLE `{}`".format(table)
    cur.execute(rq)

    #rename tabletp
    rq = "ALTER TABLE `{}` RENAME TO `{}`".format(tabletp,table)
    cur.execute(rq)


    co.commit()







