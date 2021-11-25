import sqlite3
from sqlite3 import Error
import os
import requests
import json

from apicalls import create_lnurl, create_user_api


SQLITE_DB_PATH = 'db/lntipbot.db'

def create_database():

    if not os.path.exists('db'):
        os.mkdir('db')

    # database setup
    try:
        con = sqlite3.connect(SQLITE_DB_PATH)
        cur = con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS user (id INTEGER NOT NULL, lnurl TEXT NOT NULL);')
        cur.execute('CREATE TABLE IF NOT EXISTS user_api (id INTEGER NOT NULL, wallet_id INTEGER, admin_key TEXT, invoice_key TEXT);')
        con.commit()
        con.close()
    except Error as e:
        print('Failed to setup database.\n' + e)
        exit(1)


# connect to the database, returns connection object
def get_connection():

    try:
        con = sqlite3.connect(SQLITE_DB_PATH)
        return con
    except:
        print('Unable to connect to database. Please try again later.\n')
        exit(1)


def create_user(user_id : int):

    json_data = create_user_api(user_id)

    wallet_id : str = json_data['wallets'][0]['id']
    admin_key : str = json_data['wallets'][0]['adminkey']
    invoice_key : str = json_data['wallets'][0]['inkey']

    lnurl = create_lnurl(admin_key)

    # connect to database
    con = get_connection()
    cur = con.cursor()

    cur.execute('INSERT INTO user (id, lnurl) VALUES (?, ?);', (user_id, lnurl))
    cur.execute('INSERT INTO user_api (id, wallet_id, admin_key, invoice_key) VALUES (?, ?, ?, ?);', (user_id, wallet_id, admin_key, invoice_key))

    con.commit()
    con.close()


# return lnurl string from database query
def get_lnurl(user_id : int):

    con = get_connection()
    cur = con.cursor()

    cur.execute('SELECT lnurl FROM user WHERE id=?;', (user_id,))
    lnurl = str(cur.fetchone()[0])

    con.commit()
    con.close()

    return lnurl


def get_balance(user_id : int):

    invoice_key = get_invoice_key(user_id)
    url = os.getenv('GET_WALLET_DETAILS_API')
    headers = {"X-Api-Key": invoice_key}

    r = requests.get(url, headers=headers)
    json_data = r.json()

    balance = int(json_data['balance'] / 1000)
    return balance
    

def get_admin_key(user_id : int):
    
    con = get_connection()
    cur = con.cursor()

    cur.execute('SELECT admin_key FROM user_api WHERE id=?;', (user_id,))
    admin_key : str = str(cur.fetchone()[0])

    con.commit()
    con.close()

    return admin_key


def get_invoice_key(user_id : int):
    
    con = get_connection()
    cur = con.cursor()

    cur.execute('SELECT invoice_key FROM user_api WHERE id=?;', (user_id,))
    invoice_key : str = str(cur.fetchone()[0])

    con.commit()
    con.close()

    return invoice_key


# do checks below
def does_user_exist(user_id : int):

    con = get_connection()
    cur = con.cursor()

    cur.execute('SELECT id FROM user WHERE id=?;', (user_id,))
    result = cur.fetchone()

    con.commit()
    con.close()

    if result is None:
        return 0
    else:
        return 1