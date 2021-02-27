import sqlite3
from collections import defaultdict
from collections.abc import Sequence
import project_helpers as ph

#TIMEOUT = 120

def get_all_tables(db):
    #conn = sqlite3.connect(db, timeout = TIMEOUT)

    c = db.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    res = c.fetchall()
    #print(res)
    return [el[0] for el in c.fetchall()]


def check_for_new_cols(old_db, old_name, new_db, new_name):

    old_cols = get_column_names(old_db, old_name)
    new_cols = get_column_names(new_db, new_name)
    
    old_set = set()
    for pair in old_cols:
        old_set.add(pair)
    new_set = set()
    for el in new_cols:
        new_set.add(el)

    add_cols = ph.find_added_columns(new_set, old_set)
    return add_cols


def print_column_names(db, table_name):
    c = db.cursor()

    c.execute('SELECT name FROM PRAGMA_TABLE_INFO(?)', (table_name,))

    res = [el[0] for el in c.fetchall()]
    print(res)
    return res

def get_column_names(db, table_name):
    c = db.cursor()

    c.execute('SELECT name FROM PRAGMA_TABLE_INFO(?)', (table_name,))

    #print(c.fetchall())
    return [el[0] for el in c.fetchall()]

def get_column_types(db, table_name):
    c = db.cursor()

    c.execute('SELECT type FROM PRAGMA_TABLE_INFO(?)', (table_name,))

    #print(c.fetchall())
    return [el[0] for el in c.fetchall()]


def get_column_names_old(db, table_name):
    c = db.cursor()

    c.execute('SELECT name FROM PRAGMA_TABLE_INFO(?)', (table_name,))

    #print(c.fetchall())
    return c.fetchall()


def get_column_types_old(db, table_name):
    c = db.cursor()

    c.execute('SELECT type FROM PRAGMA_TABLE_INFO(?)', (table_name,))

    #print(c.fetchall())
    return c.fetchall()

def print_columns(db, table_name):
    c = db.cursor()


    cmd = f"SELECT rowid, * FROM {table_name}"

    c.execute(cmd)
    res = c.fetchall()
    print(res)
    return res

def print_columns_formatted(db, table_name):
    c = db.cursor()


    cmd = f"SELECT rowid, * FROM {table_name}"

    c.execute(cmd)
    res = c.fetchall()
    for row in res:
        print(row)
        print()
        print()
    return res

def get_columns(db, table_name):
    c = db.cursor()


    cmd = f"SELECT rowid, * FROM {table_name}"

    c.execute(cmd)
    #print(c.fetchall())
    return c.fetchall()

def count_rows(db, table_name):
    c = db.cursor()
    c.execute(f"SELECT COUNT(rowid) from {table_name}")
    res = c.fetchone()[0]
    return res

def add_column(db, table_name, pair):
    c = db.cursor()

    cmd = f"ALTER TABLE {table_name} ADD COLUMN {pair} text"
    #print(cmd)
    c.execute(cmd)
    db.commit()


def add_column_new(db, table_name, col_name, col_type):
    c = db.cursor()

    cmd = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"
    c.execute(cmd)
    db.commit()

def insert_row(db, table_name,cols,vals):
    c = db.cursor()
    rows_before = count_rows(db,table_name)


    if (not isinstance(cols,Sequence)) or (isinstance(cols,str)):
        cmd = f"INSERT INTO {table_name}({cols}) VALUES('{vals}')"
    else:
        cmd = f"INSERT INTO {table_name}{*cols,} VALUES{*vals,}"
        #print(cmd)
    c.execute(cmd)
    db.commit()

    rows_after = count_rows(db,table_name)
    if rows_after - rows_before != 1:
        raise sqlite3.OperationalError("Row insertion failed")

def update_row(db, table_name,cols, vals, rowid):
    c = db.cursor()
    #print(cols)
    if (not isinstance(cols,Sequence)) or (isinstance(cols,str)):
        cmd = f"UPDATE {table_name} SET {cols} = '{vals}' WHERE rowid = {rowid}"
    else:
        cmd = f"UPDATE {table_name} SET {*cols,} = {*vals,} WHERE rowid = {rowid}"

    c.execute(cmd)
    db.commit()

    check = get_row(db, table_name, cols, rowid)
    if isinstance(vals,Sequence) and not isinstance(vals,str):
        if tuple(check) != tuple(vals):
            raise sqlite3.OperationalError("Update operation failed")
    else:
        if check[0] != vals:
            raise sqlite3.OperationalError("Update operation failed")


def get_table_row(db, table_name, rowid):
    c = db.cursor()
    cmd = f"SELECT * FROM {table_name} WHERE rowid = {rowid}"
    c.execute(cmd)
    res = c.fetchall()
    if len(res) == 0:
        return []
    return res[0]

def get_row_all(db, table_name, rowid):
    c = db.cursor()
    cmd = f"SELECT * FROM {table_name} WHERE rowid = {rowid}"
    c.execute(cmd)
    res = c.fetchall()
    if len(res) == 0:
        return []
    return res


def get_last_rowid(db, table_name):
    c = db.cursor()
    cmd = f"SELECT MAX(rowid) FROM {table_name}"
    c.execute(cmd)
    res = c.fetchall()[0][0]
    return res


def get_row(db, table_name, cols, rowid):
    c = db.cursor()
    if isinstance(cols,str) or  not isinstance(cols,Sequence):
        cmd = f"SELECT {cols} FROM {table_name} WHERE rowid = {rowid}"
    else:
        cols_string = ",".join(cols)
        cmd = "SELECT " + cols_string + f" FROM {table_name} WHERE rowid = {rowid}"

    c.execute(cmd)

    return c.fetchall()[0]

def post_single_val(db,table_name,col_name, value):
    c = db.cursor()
    value = [value]
    cmd = f'INSERT INTO {table_name}({col_name}) VALUES(?)'
    c.execute(cmd,value)
    db.commit()

def delete_row(db, table_name, rowid):
    c = db.cursor()

    cmd = f'DELETE FROM {table_name} WHERE rowid = {rowid}'

    c.execute(cmd)
    db.commit()

    cmd2 = f'SELECT * FROM {table_name} WHERE rowid = {rowid}'
    c.execute(cmd2)

    res = c.fetchall()

    if len(res) != 0:
        raise sqlite3.OperationalError("Delete row operation failed")


def delete_table(db, table_name):

    c = db.cursor()

    cmd = f"DROP TABLE IF EXISTS {table_name}"
    c.execute(cmd)
    db.commit()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    res = [item for item in tables if table_name in item]

    #print(res)
    if res:
        raise Exception('delete operation failed')

    #print(c.fetchall())
    #return True if not c.fetchall() else False

def row_exists(db,table_name, row):
    c = db.cursor()

    cmd = f"SELECT EXISTS(SELECT 1 from {table_name} WHERE rowid = {row})"
    c.execute(cmd)
    res = c.fetchall()
    return bool(res[0][0])

def first_n_rows(db,table_name, n=3):
    c = db.cursor()

    cmd = f'SELECT * FROM {table_name} LIMIT {n}'
    c.execute(cmd)
    return c.fetchall()

def last_n_rows(db,table_name, n=3):
    c = db.cursor()
    cmd = f"SELECT * FROM ( \
            SELECT rowid, * FROM {table_name} ORDER BY rowid DESC LIMIT {n}) \
            ORDER BY rowid ASC;"
    #cmd = f'SELECT * FROM {table_name} LIMIT {n}'
    c.execute(cmd)
    return c.fetchall()


def split_columns(db, table_name):
    #res = defaultdict(list)
    rows = get_columns(db, table_name)
    res = list(zip(*rows))
    return res

def create_db_connection(name, tout):
    try:
        db = sqlite3.connect(name, timeout=tout)
        #print('connection success')
    except Exception as e:
        print('An error has occured connecting to the database: ', e)
    return db

def create_table(db, name, cols, types):
    c = db.cursor()

    if (not isinstance(cols,Sequence)) or (isinstance(cols,str)):
        #cmd = f"UPDATE {table_name} SET {cols} = '{vals}' WHERE rowid = {rowid}"
        cmd = f"CREATE TABLE IF NOT EXISTS {name} ({cols} {types})"
    else:
        #cmd = f"UPDATE {table_name} SET {*cols,} = {*vals,} WHERE rowid = {rowid}"
        col_zip = zip(cols,types)
        res = ['"' + item[0] + '"' + ' ' + item[1] for item in col_zip]
        #res = ",".join(res)
        col_cat = ",".join(res)
        cmd = f"CREATE TABLE IF NOT EXISTS {name} ({col_cat})"


    #col_tup_mod = [col + ' text' for col in col_tup]
    #print(col_heads)
    #cmd_string = 'CREATE TABLE IF NOT EXISTS ' + '"' + name + '"' + \
    #                    ' (' + ','.join(col_heads) + ')'

    #print(cmd_string)
    #print(cmd)
    c.execute(cmd)
    db.commit()

    res = check_table_exists(db,name)
    if not res:
        raise Exception("table creation failed")

def check_table_exists(db, table_name):
    c = db.cursor()
    cmd = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
    #print(cmd)
    #res = True
    c.execute(cmd)
    res = c.fetchall()
    return True if res else False


def create_table_from(db, src_table, dest_table):
    c = db.cursor()
    c.execute(f"CREATE TABLE {dest_table} AS SELECT * FROM {src_table} WHERE rowid = -1")
    db.commit()

    res = check_table_exists(db,dest_table)
    return res
