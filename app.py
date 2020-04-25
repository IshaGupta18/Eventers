from flask import Flask, render_template, request, redirect, url_for
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
table_throughTable={"Guest":"GuestEvent","Participant":"ParticipantEvent","Organizer":"OrganizerEvent","Sponsor":"SponsorEvent","Volunteer":"VolunteerEvent"}
current_user={"ID":-1,"table":None,"username":None,"throughTable":None}
def matchPassword(tableName,username,password):
    username='"'+username+'"'
    password='"'+password+'"'
    cur = mysql.connection.cursor()
    query="select "+tableName+".Name, "+tableName+"."+table_id[tableName]+" from "+tableName+" where "+tableName+".Name = "+username+" AND "+tableName+".Password = "+password+";"
    cur.execute(query)
    rv=list(cur.fetchall())
    rv=list(rv[0])
    if rv==[]:
        print("False")
        return False
    else:
        current_user["ID"]=rv[1]
        current_user["Name"]=rv[0]
        current_user["table"]=tableName
        current_user["throughTable"]=table_throughTable[tableName]
        print("True")
        return True
def getID(tableName,ID_NAME):
    cur = mysql.connection.cursor()
    cur.execute("select max("+tableName+"."+ID_NAME+") from "+tableName+";")
    rv=list(cur.fetchall())
    print(int(rv[0][0]))
    return str(int(rv[0][0])+1)
def createUser(tableName,username,password,contactID):
    ID_Name=tableName[0]+"_ID"
    username='"'+username+'"'
    password='"'+password+'"'
    contactID='"'+contactID+'"'
    ID=getID(tableName,ID_Name)
    cur = mysql.connection.cursor()
    query="insert into "+tableName+" (Name,Password,Contact,"+ID_Name+") values ("+username+","+password+","+contactID+","+ID+");"
    cur.execute(query)
    current_user["ID"]=ID
    current_user["Name"]=username
    current_user["table"]=tableName
    current_user["throughTable"]=table_throughTable[tableName]

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

def getMainEventList():
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
        data.append([i[0],i[1]])
    return data
def getSubEventList(ME_ID):
    cur = mysql.connection.cursor()
    cur.execute("select SubEvent.E_ID, SubEvent.Name from SubEvent where SubEvent.ME_ID "+str(ME_ID)+" ;")
    queryresults= list(cur.fetchall())
    for i in range(len(queryresults)):
        queryresults[i]=list(queryresults[i])
    return queryresults
@app.route('/')
def index(toggleR=False):
    data=fetchInitialDetails()
    toggleR=toggleR or request.args.get('flag')
    if toggleR=='False':
        toggleR=None
    return render_template("index.htm",main_event_list=data,toggle=toggleR)
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
    data=getMainEventList()
    if current_user["table"]=="Guest":
        return render_template("guest.htm",main_event_list=data)
    elif current_user["table"]=="Sponsor":
        return render_template("sponsor.htm")
    elif current_user["table"]=="Participant":
        return render_template("participant.htm")
    elif current_user["table"]=="Volunteer":
        return render_template("volunteer.htm")
    elif current_user["table"]=="Organizer":
        return render_template("organizer.htm")
    else:
        return redirect(url_for('index'))
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
    tableName=request.form['userType']
    flag=matchPassword(tableName,username,password)
    if flag==True:
        return redirect(url_for('index', flag=True))
    else:
        return redirect(url_for('renderLogin'))
@app.route('/signup',methods=['POST'])
def signup():
    username=request.form.get('signupName')
    password=request.form.get('signupPassword')
    contact=request.form.get('signupContact')
    tableName=request.form['userType']  
    createUser(tableName,username,password,contact)
    return redirect(url_for('index', flag=True))

@app.route('/logout',methods=['GET'])
def logout():
    current_user={"ID":-1,"table":None,"username":None,"throughTable":None}
    return redirect(url_for('index', flag=False))

@app.route('/requestSubEvent',methods=['GET'])
def requestSubEvent():
    if request.method == 'GET':
        data=request.form
        loadedData={}
        for i in data.keys():
            loadedData=json.loads(i)
        ID=loadedData['data'][0]
        subEventList=getSubEventList(ID)
    return {"dataList":subEventList}

if __name__ == '__main__':
   app.run()