import sqlite3
db=sqlite3.connect("./data.db")
cur=db.cursor()

def printKeys(value, valid):
    cur.execute(f"SELECT * FROM keys WHERE value={value} AND validity={valid}")
    keys=[]
    for keyDB in cur.fetchall():
        keys.append(keyDB[1])
    
    i=0
    for x in keys:
        i+=1
        return(str(i) + ". " + x)
    
