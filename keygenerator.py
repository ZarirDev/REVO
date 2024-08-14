import string
import sqlite3
import random

db=sqlite3.connect("data.db")
cur=db.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS keys(
            id INTEGER PRIMARY KEY,
            key TEXT,
            value INTEGER,
            validity INTEGER
)""")
db.commit()

chars= (string.ascii_uppercase) + (string.digits)

def createKey(length):
    key=""
    for i in range(length):
            if i%4==0 and i!=0:
                key+="-"
            key+=chars[random.randint(0,len(chars)-1)]
    return key

def uploadKey(key, value):
    cur.execute(f"SELECT * FROM keys WHERE key='{key}'")
    if cur.fetchone() == key:
        uploadKey(createKey(20))
    else:
        cur.execute(f"INSERT INTO keys(key, value, validity) VALUES('{key}', {value}, 1)")
        db.commit()
        return key

def generateKeys(amount, value):
        keyList=[]
        for x in range(amount):
            key=uploadKey(createKey(20), value)
            print("Generated: " + key)
            keyList.append(key)
        return "* "+"\n* ".join(keyList)