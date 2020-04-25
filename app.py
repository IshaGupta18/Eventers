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
table_id={"MainEvent":"ME_ID","SubEvent":"E_ID","Team":"T_ID","TimeSlot":"TS_ID","Organizer":"O_ID","Sponsor":"S_ID","Participant":"P_ID","Guest":"G_ID","Prize":"PZ_ID","Location":"L_ID","Resource":"R_ID","Volunteer":"V_ID","OrganizerEvent":"E_ID","GuestEvent":"E_ID","SponsorEvent":"E_ID","ParticipantEvent":"E_ID","VolunteerEvent":"E_ID"}
def matchPassword(tableName,username,password):
    cur = mysql.connection.cursor()
    cur.execute("select ")
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
def fetchInitialDetails():
    cur = mysql.connection.cursor()
    cur.execute("select * from MainEvent where MainEvent.ME_ID in (select SubEvent.ME_ID from SubEvent);")
    queryresults_1 = list(cur.fetchall())
    cur.execute("select * from MainEvent where MainEvent.ME_ID in (select Team.ME_ID from Team);")
    queryresults_2 = list(cur.fetchall())
    queryresults=list(set(queryresults_1) & set(queryresults_2))
    rv = random.sample(queryresults,10)
    for i in range(len(rv)):
        rv[i]=list(rv[i])
    data=[]
    for i in rv:
        i[2]=returnDate(i[2])
        i[3]=returnDate(i[3])
        data.append([i[0],i[1],i[2:]])
    print(data)
    return data
@app.route('/')
def index():
    main_event_list=fetchInitialDetails()
    return render_template("index.htm",main_event_list=data,toggle=False)
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
        throughTable=loadedData['data'][3]
        # print(ID)
        dataList=[]
        if throughTable=="null":
            dataList=fetchData(tableName,ID,tablenameID)
        else:
            dataList=fetchDataThroughTable(tableName,ID,tablenameID,throughTable)
        # print(dataList,"blahhhhhh")

    return {"dataList":dataList}
@app.route('/saveEvent',methods=['GET','POST'])
def saveEvent():
    if request.method=='POST':
        return redirect(url_for('index'))
    return render_template("addEntries.htm")
@app.route('/applet',methods=['GET','POST'])
def applet():
    if request.method=='POST':
        return redirect(url_for('index'))
    return render_template("applet.htm")
@app.route('/renderLogin',methods=['GET','POST'])
def renderLogin():
    if request.method=='POST':
        return redirect(url_for('index'))
    return render_template("login.htm")
@app.route('/renderSignup',methods=['GET','POST'])
def renderSignup():
    if request.method=='POST':
        return redirect(url_for('index'))
    return render_template("signUp.htm")
@app.route('/login',methods=['POST'])
def login():
    username=request.form.get('loginName')
    password=request.form.get('loginPassword')

    data=fetchInitialDetails()
    return render_template("index.htm",main_event_list=data,toggle=True)
    
if __name__ == '__main__':
   app.run()