import sqlite3
from collections import defaultdict

#TIMEOUT = 120

def get_all_tables(db):
    #conn = sqlite3.connect(db, timeout = TIMEOUT)

    c = db.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(c.fetchall())
    return c.fetchall()


def print_column_names(db, table_name):
    c = db.cursor()

    c.execute('SELECT name FROM PRAGMA_TABLE_INFO(?)', (table_name,))

    print(c.fetchall())
    return c.fetchall()

def get_column_names(db, table_name):
    c = db.cursor()

    c.execute('SELECT name FROM PRAGMA_TABLE_INFO(?)', (table_name,))

    #print(c.fetchall())
    return c.fetchall()

def print_columns(db, table_name):
    c = db.cursor()


    cmd = f"SELECT rowid, * FROM {table_name}"

    c.execute(cmd)
    print(c.fetchall())
    return c.fetchall()

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
    if len(cols) == 1:
        cmd = f"INSERT INTO {table_name}({cols}) VALUES('{vals}')"
    else:
        cmd = f"INSERT INTO {table_name}{*cols,} VALUES{*vals,}"

    c.execute(cmd)
    db.commit()

    rows_after = count_rows(db,table_name)
    if rows_after - rows_before != 1:
        raise sqlite3.OperationalError("Row insertion failed")

def update_row(db, table_name,cols, vals, rowid):
    c = db.cursor()

    if len(cols) == 1:
        cmd = f"UPDATE {table_name} SET {cols} = '{vals}' WHERE rowid = {row_num}"
    else:
        cmd = f"UPDATE {table_name} SET {*cols,} = {*vals,} WHERE rowid = {rowid}"

    c.execute(cmd)
    db.commit()

    check = get_row(db, table_name, rowid)
    if tuple(check) != tuple(vals):
        raise sqlite3.OperationalError("Update operation failed")


def get_row(db, table_name, rowid):
    c = cursor()
    cmd = f"SELECT * FROM {table_name} WHERE rowid = {rowid}"
    c.execute(cmd)

    return c.fetchall()[0]

def post_single_val(db,table_name,col_name, value):
    c = db.cursor()
    value = [value]
    cmd = f'INSERT INTO {table_name}({col_name}) VALUES(?)'
    c.execute(cmd,value)
    db.commit()


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

def create_table(db, name, col_names, col_types):

    col_zip = zip(col_names,col_types)
    col_heads = []
    for i in col_zip:
        col_heads.append(' '.join(i))
    #col_tup_mod = [col + ' text' for col in col_tup]
    #print(col_heads)
    cmd_string = 'CREATE TABLE IF NOT EXISTS ' + '"' + name + '"' + \
                        ' (' + ','.join(col_heads) + ')'
    c = db.cursor()
    #print(cmd_string)
    c.execute(cmd_string)
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
