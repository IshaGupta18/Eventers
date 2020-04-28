from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import mysql.connector
import pymysql
import datetime, json, random
from decimal import *
app = Flask(__name__,static_folder="templates/static")
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'my_password'
app.config['MYSQL_DB'] = 'EventManagement'
mysql = MySQL(app)
config = {
  'host':"eventersiiitd.mysql.database.azure.com",
  'user':"eventers@eventersiiitd",
  'password':'SIRASsiras123',
  'database':'EventManagement',
  'ssl_ca':'/var/www/html/BaltimoreCyberTrustRoot.crt.pem',
  'ssl_verify_cert':'true'
}
# cur = mysql.connector.connect(**config).cursor()
conn = pymysql.connect(user='eventers@eventersiiitd',
                       password='SIRASsiras123',
                       database='EventManagement',
                       host='eventersiiitd.mysql.database.azure.com',
                       ssl={'ssl': {'ca': '/var/www/html/BaltimoreCyberTrustRoot.crt.pem'}})
# cur=conn.cursor()
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
    mysql.connection.commit()
    print(query)
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

def convertToDate(s):
    s=s.split("/")
    DD=int(s[0])
    MM=int(s[1])
    YYYY=int(s[2].strip("\n"))
    return datetime.date(YYYY,MM,DD).strftime('%Y-%m-%d')

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
    cur.execute("select SubEvent.E_ID, SubEvent.Name from SubEvent where SubEvent.ME_ID = "+str(ME_ID)+" ;")
    queryresults= list(cur.fetchall())
    for i in range(len(queryresults)):
        queryresults[i]=list(queryresults[i])
    return queryresults

def saveEntry(table,ID1,ID2):
    cur = mysql.connection.cursor()
    query = "insert into "+table+" values ("+ID1+","+ID2+");"
    print(query)
    cur.execute("SET FOREIGN_KEY_CHECKS=0;")
    cur.execute(query)
    mysql.connection.commit()
    cur.execute("SET FOREIGN_KEY_CHECKS=1;")
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
        return render_template("sponsor.htm",main_event_list=data)
    elif current_user["table"]=="Participant":
        return render_template("participant.htm",main_event_list=data)
    elif current_user["table"]=="Volunteer":
        return render_template("volunteer.htm",main_event_list=data)
    elif current_user["table"]=="Organizer":
        return render_template("organizer.htm",main_event_list=data)
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

@app.route('/profile',methods=['GET','POST'])
def profile():
    if request.method=='POST':
        return redirect(url_for('index'))
    data=[]
    cur = mysql.connection.cursor()
    query = "select S.ME_ID, S.L_ID, S.TS_ID, S.Number_Participants, S.Name from SubEvent as S where S.E_ID in (select T.E_ID from "+current_user["throughTable"]+" as T where T."+str(current_user["throughTable"][0])+"_ID= "+str(current_user["ID"])+");"
    cur.execute(query)
    rv=list(cur.fetchall())
    mainEvents={}
    for subEvent in rv:
        ME_ID=subEvent[0]
        q="select M.Name, M.StartDate, M.EndDate, M.ContactID from MainEvent as M where M.ME_ID="+str(ME_ID)+";"
        cur.execute(q)
        result=cur.fetchall()[0]
        try:
            mainEvents[result].append(list(subEvent))
        except:
            mainEvents[result]=[list(subEvent)]
    for m in mainEvents:
        subEvents=mainEvents[m]
        for i in range(len(subEvents)):
            subEvent=subEvents[i]
            L_ID=str(subEvent[1])
            TS_ID=str(subEvent[2])
            cur.execute("select L.Name, L.Address from Location as L where L.L_ID="+L_ID+";")
            location=cur.fetchall()[0]
            cur.execute("select TS.StartDate,TS.StartTime,TS.EndDate,TS.EndTime from TimeSlot as TS where TS.TS_ID="+TS_ID+";")
            timeslot=cur.fetchall()[0]
            l=[subEvent[4],location[0]+" , "+location[1],timeslot[0]+" , "+timeslot[1],timeslot[2]+" , "+timeslot[3],subEvent[3]]
            subEvents[i]=l
    print(mainEvents)
    return render_template("guestProfile.htm")


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

@app.route('/requestSubEvent',methods=['GET','POST'])
def requestSubEvent():
    if request.method == 'POST':
        data=request.form
        loadedData={}
        for i in data.keys():
            loadedData=json.loads(i)
        ID=loadedData['data'][0]
        subEventList=getSubEventList(ID)
    return {"dataList":subEventList}

@app.route('/registerGuest',methods=['POST'])
def registerGuest():
    if request.method == 'POST':
        fees=request.form.get("GuestFees")
        post=request.form.get("GuestPost")
        SE_ID=request.form.get("subEventSelect")
        post='"'+post+'"'
        print(fees,post,SE_ID)
        cur = mysql.connection.cursor()
        cur.execute("update Guest set Fees = "+fees+", Post = "+post+" where Guest.G_ID = "+str(current_user["ID"])+";")
        saveEntry("GuestEvent",str(current_user["ID"]),SE_ID)
    return redirect(url_for('index', flag=True))

@app.route('/registerVolunteer',methods=['POST'])
def registerVolunteer():
    if request.method == 'POST':
        SE_ID=request.form.get("subEventSelect")
        print(str(current_user["ID"]),SE_ID)
        saveEntry("VolunteerEvent",str(current_user["ID"]),SE_ID)
    return redirect(url_for('index', flag=True))

@app.route('/registerSponsor',methods=['POST'])
def registerSponsor():
    if request.method == 'POST':
        sponsorprize=request.form.get("SponsorPrize")
        product=request.form.get("SponsorProduct")
        SE_ID=request.form.get("subEventSelect")
        product='"'+product+'"'
        cur = mysql.connection.cursor()
        cur.execute("update Sponsor set Amount = "+sponsorprize+", Product = "+product+" where Sponsor.S_ID = "+str(current_user["ID"])+";")
        saveEntry("SponsorEvent",str(current_user["ID"]),SE_ID)
    return redirect(url_for('index', flag=True))

@app.route('/registerParticipant',methods=['POST'])
def registerParticipant():
    if request.method == 'POST':
        age=request.form.get("ParticipantAge")
        SE_ID=request.form.get("subEventSelect")
        cur = mysql.connection.cursor()
        cur.execute("update Partcipant set Age = "+age+" where Partcipant.P_ID = "+str(current_user["ID"])+";")
        saveEntry("ParticipantEvent",str(current_user["ID"]),SE_ID)
    return redirect(url_for('index', flag=True))

@app.route('/registerMainEvent',methods=['POST'])
def registerMainEvent():
    if request.method == 'POST':
        data=request.form
        loadedData={}
        for i in data.keys():
            loadedData=json.loads(i)
        name='"'+loadedData['data'][0]+'"'
        contact='"'+loadedData['data'][1]+'"'
        sdate='"'+convertToDate(loadedData['data'][2])+'"'
        edate='"'+convertToDate(loadedData['data'][3])+'"'
        ID=getID("MainEvent","ME_ID")
        print(name,contact,sdate,edate)
        cur = mysql.connection.cursor()
        query="insert into MainEvent (Name,ContactID,StartDate,EndDate,ME_ID) values ("+name+","+contact+","+str(sdate)+","+str(edate)+","+str(ID)+");"
        cur.execute(query)
        mysql.connection.commit()
        cur.execute("select M.ME_ID, M.Name from MainEvent as M order by M.ME_ID desc limit 5;")
        rv=list(cur.fetchall())
        for i in range(len(rv)):
            rv[i]=list(rv[i]) 
    return {"data":rv}
@app.route('/registerLocation',methods=['POST'])
def registerLocation():
    if request.method == 'POST':
        data=request.form
        loadedData={}
        for i in data.keys():
            loadedData=json.loads(i)
        name='"'+loadedData['data'][0]+'"'
        capacity=loadedData['data'][1]
        address='"'+loadedData['data'][2]+'"'
        rent=loadedData['data'][3]
        contact='"'+loadedData['data'][4]+'"'
        ID=getID("Location","L_ID")
        cur = mysql.connection.cursor()
        query="insert into Location (Name,Address,Capacity,Rent,CONTACT_ID,L_ID,Availability) values ("+name+","+address+","+capacity+","+rent+","+contact+","+str(ID)+","+"1"+");"
        cur.execute(query)
        mysql.connection.commit()
        cur.execute("select L.L_ID,L.Name from Location as L where L.Availability=1 order by L.L_ID desc limit 5;")
        rv=list(cur.fetchall())
        for i in range(len(rv)):
            rv[i]=list(rv[i]) 
    return {"data":rv}
@app.route('/registerSubEvent',methods=['POST'])
def registerSubEvent():
    if request.method == 'POST':
        name='"'+request.form.get("SubEventName")+'"'
        fees=request.form.get("SubEventFees")
        ME_ID=request.form.get("SubEventMainEvent")
        L_ID=request.form.get("SubEventLocation")
        startTime='"'+request.form.get("timeSlotStart")+'"'
        endTime='"'+request.form.get("timeSlotEnd")+'"'
        startDate='"'+request.form.get("SubEventStartDate")+'"'
        endDate='"'+request.form.get("SubEventEndDate")+'"'
        E_ID=getID("SubEvent","E_ID")
        TS_ID=getID("TimeSlot","TS_ID")
        cur = mysql.connection.cursor()
        cur.execute("insert into TimeSlot (TS_ID,StartDate,EndDate,StartTime,EndTime) values ("+TS_ID+","+startDate+","+endDate+","+startTime+","+endTime+");")
        mysql.connection.commit()
        cur.execute("SET FOREIGN_KEY_CHECKS=0;")
        cur.execute("insert into SubEvent (E_ID,ME_ID,TS_ID,L_ID,Fees,Name) values ("+E_ID+","+ME_ID+","+TS_ID+","+L_ID+","+fees+","+name+");")
        mysql.connection.commit()
        cur.execute("SET FOREIGN_KEY_CHECKS=1;")
    return redirect(url_for('index', flag=True))
if __name__ == '__main__':
   app.run()