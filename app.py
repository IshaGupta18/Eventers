from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import datetime, json, random
from decimal import *
app = Flask(__name__,static_folder="templates/static")
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'my_password'
app.config['MYSQL_DB'] = 'EventManagement'
mysql = MySQL(app)
def datatypeConverter(var):
    if type(var) is datetime:
        return returnDate(var)
    elif type(var) is Decimal:
        return str(int(var))
    return var

def returnDate(date):
    return date.strftime('%m/%d/%Y')
def fetchData(tableName,ID,tablenameID):
    cur = mysql.connection.cursor()
    cur.execute("select * from "+str(tableName)+" where "+str(tableName)+"."+tablenameID+"="+str(ID)+";")
    rv = list(cur.fetchall())
    for i in range(len(rv)):
        rv[i]=list(rv[i])
        n=len(rv[i])
        for j in range(n):
            rv[i][j]=datatypeConverter(rv[i][j])

    data=[]
    cur.execute("select COLUMN_NAME from INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME="+"'"+tableName+"';")
    headers=list(cur.fetchall())
    print(headers)
    for i in rv:
        d={}
        n=len(i)
        for j in range(n):
            d[str(headers[j][0])]=i[j]
        data.append([i[0],i[1],d])
    return data
def fetchDataThroughTable(tableName,ID,tablenameID,throughTableName):
    cur = mysql.connection.cursor()
    cur.execute("select * from "+str(tableName)+" where "+str(tableName)+"."+tablenameID+" in (select "+throughTableName+"."+tablenameID+" from "+throughTableName+" where "+throughTableName+"."+table_id[throughTableName]+"="+ID+");")
    rv = list(cur.fetchall())
    for i in range(len(rv)):
        rv[i]=list(rv[i])
        n=len(rv[i])
        for j in range(n):
            rv[i][j]=datatypeConverter(rv[i][j])

    data=[]
    cur.execute("select COLUMN_NAME from INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME="+"'"+tableName+"';")
    headers=list(cur.fetchall())
    print(headers)
    for i in rv:
        d={}
        n=len(i)
        for j in range(n):
            d[str(headers[j][0])]=i[j]
        data.append([i[0],i[1],d])
    return data
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("select * from MainEvent where MainEvent.ME_ID in (select SubEvent.ME_ID from SubEvent);")
    queryresults = list(cur.fetchall())
    rv = random.sample(queryresults,10)
    for i in range(len(rv)):
        rv[i]=list(rv[i])
    data=[]
    for i in rv:
        i[2]=returnDate(i[2])
        i[3]=returnDate(i[3])
        data.append([i[0],i[1],i[2:]])

    # for i in rv:
    #     print(i)
    # print(list(rv))
    # return "Hello World "+str(rv)
    print(data)
    return render_template("index.htm",main_event_list=data)
@app.route('/requestdata/',methods=['GET','POST'])
def requestdata():
    if request.method=='POST':
        data=request.form
        loadedData={}
        for i in data.keys():
            loadedData=json.loads(i)
        ID=loadedData['data'][0]
        tableName=loadedData['data'][1]
        tablenameID=loadedData['data'][2]
        # print(ID)
        dataList=fetchData(tableName,ID,tablenameID)
        # print(dataList,"blahhhhhh")

    return {"dataList":dataList}
    
if __name__ == '__main__':
   app.run()