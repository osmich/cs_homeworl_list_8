import sys, random, string,argon2
import MySQLdb
from flask import request

import json

def register_user(param):
    conn = None

    try:
        conn = MySQLdb.connect('localhost', 'testuser', 'xxxx', 'cs_bank_2')

        salt = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(20))
        passw = argon2.argon2_hash(password=param['password'], salt=salt, t=16, m=8, p=1, buflen=128, argon_type=argon2.Argon2Type.Argon2_i).decode("ISO-8859-15")

        sql = "insert into users (FirstName, LastName, Email, UserName, City, Address, Password, Salt) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (param['firstname'] , param['lastname'], param['email'], param['username'], param['city'], param['address'], passw, salt )
        print(sql,'\n')            
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)
        conn.commit()

    except MySQLdb.Error as e:
        print('error {}: {}'.format(e.args[0], e.args[1])) 
        return False  

    finally:
        if conn:
            conn.close()
            return True


def login_user(param):
    conn = None

    try:
        sql = "SELECT Salt FROM users WHERE UserName = \'{}\';".format(param['username'])
        # print(sql)         
        conn = MySQLdb.connect('localhost', 'testuser', 'xxxx', 'cs_bank_2')

        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)
        rows = cursor.fetchall()
        if len(rows) != 1:
            return {"result":False, "value":"empty"}
        salt = rows[0]['Salt']
        salt = salt.encode("ISO-8859-15")
        passw = argon2.argon2_hash(password=param['password'], salt=salt, t=16, m=8, p=1, buflen=128, argon_type=argon2.Argon2Type.Argon2_i).decode("ISO-8859-15")

        sql = "SELECT id, Role FROM users WHERE UserName = \'{}\' AND Password = \'{}\'".format(param['username'], passw)
        cursor.execute(sql)
        rows = cursor.fetchall()

        print("rows: ", rows)
        if len(rows) == 1:
            return {"result":True, "value":rows}

        return {"result":False, "value":"empty"}

    except MySQLdb.Error as e:
        print('error {}: {}'.format(e.args[0], e.args[1]))
        return {"result":False, "value":"empty"}

    finally:
        conn.close()


def new_transfer(param, user):
    sql = "insert into transfers (UserID, pln, pln_c, AccountNumber, FirstName, LastName, City, Address, TitleTransfer, Status) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (user , param['PLN'], param['PLN_C'], param['accountnumber'], param['firstname'], param['lastname'], param['city'], param['address'], param['titletransfer'], "False" )
    try:
        conn = MySQLdb.connect('localhost', 'testuser', 'xxxx', 'cs_bank_2')

        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)
        conn.commit()

        return True

    except MySQLdb.Error as e:
        print('error {}: {}'.format(e.args[0], e.args[1]))
        return False

    finally:
        conn.close()      

def get_transfers(user):
    sql = "SELECT * FROM transfers WHERE userID = \'{}\'".format(user)
    try:
        conn = MySQLdb.connect('localhost', 'testuser', 'xxxx', 'cs_bank_2')

        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)
        rows = cursor.fetchall()

        print(json.dumps( [dict(ix) for ix in rows] ) )

        return rows

    except MySQLdb.Error as e:
        print('error {}: {}'.format(e.args[0], e.args[1]))
        return None

    finally:
        conn.close()

def admin_get_transfers():
    sql = "SELECT * FROM transfers"
    try:
        conn = MySQLdb.connect('localhost', 'testuser', 'xxxx', 'cs_bank_2')

        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)
        rows = cursor.fetchall()

        return rows

    except MySQLdb.Error as e:
        print('error {}: {}'.format(e.args[0], e.args[1]))
        return None

    finally:
        conn.close()

def admin_get_pending():
    sql = "SELECT * FROM transfers WHERE Status = False"
    try:
        conn = MySQLdb.connect('localhost', 'testuser', 'xxxx', 'cs_bank_2')

        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)
        rows = cursor.fetchall()

        return rows

    except MySQLdb.Error as e:
        print('error {}: {}'.format(e.args[0], e.args[1]))
        return None

    finally:
        conn.close()

def reset_password(user):
    sql = "SELECT Email FROM users WHERE UserName = \'{}\'".format(user)
    try:
        print('here')
        conn = MySQLdb.connect('localhost', 'testuser', 'xxxx', 'cs_bank_2')

        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)
        rows = cursor.fetchall()

        if len(rows) != 1:
            return {"result":False, "value":"empty"}

        email = rows[0]["Email"]
        newPassword = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))

        salt = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(20))
        passw = argon2.argon2_hash(password=newPassword, salt=salt, t=16, m=8, p=1, buflen=128, argon_type=argon2.Argon2Type.Argon2_i).decode("ISO-8859-15")


        sql = "UPDATE users SET Password = \'{}\' , Salt = \'{}\' WHERE UserName = \'{}\';".format(passw, salt, user)
        # print(sql)
        cursor.execute(sql)
        conn.commit()

        return {"result":True, "email":email, "password":newPassword}

    except MySQLdb.Error as e:
        print('error {}: {}'.format(e.args[0], e.args[1]))
        return {"result":False, "value":"empty"}

    finally:
        conn.close()


def admin_accept(id):
    sql = "UPDATE transfers set Status=True WHERE id =\'{}\'".format(id)
    try:
        conn = MySQLdb.connect('localhost', 'testuser', 'xxxx', 'cs_bank_2')

        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)
        conn.commit()
        sql = "SELECT * FROM transfers WHERE Status = False"

        cursor.execute(sql)
        rows = cursor.fetchall()

        return rows

    except MySQLdb.Error as e:
        print('error {}: {}'.format(e.args[0], e.args[1]))
        return None

    finally:
        conn.close()



def new_transfer_api(param, user):
    sql = "insert into transfers (UserID, pln, pln_c, AccountNumber, FirstName, LastName, City, Address, TitleTransfer, Status) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (user , param['PLN'], param['PLN_C'], param['accountnumber'], param['firstname'], param['lastname'], param['city'], param['address'], param['titletransfer'], "False" )
    try:
        conn = MySQLdb.connect('localhost', 'testuser', 'xxxx', 'cs_bank_2')

        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)
        conn.commit()

        return True

    except MySQLdb.Error as e:
        print('error {}: {}'.format(e.args[0], e.args[1]))
        return False

    finally:
        conn.close() 



def check_admin(id):
    sql = "SELECT Role FROM users WHERE id=\'{}\'".format(id)
    try:
        conn = MySQLdb.connect('localhost', 'testuser', 'xxxx', 'cs_bank_2')

        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)

        rows = cursor.fetchall()

        if len(rows) == 1 and rows[0]["Role"] == "ADMIN":
            return True
        
        return False

    except MySQLdb.Error as e:
        print('error {}: {}'.format(e.args[0], e.args[1]))
        return False

    finally:
        conn.close() 


