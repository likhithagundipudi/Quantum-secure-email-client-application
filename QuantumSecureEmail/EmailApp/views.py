from django.shortcuts import render
import pymysql
from datetime import datetime
from django.template import RequestContext
from django.contrib import messages
import pymysql
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
import QuantumEncryption
from QuantumEncryption import *

global username

def ComposeMailAction(request):
    if request.method == 'POST':
        global username
        receiver = request.POST.get('t1', False)
        subject = request.POST.get('t2', False)
        msg = request.POST.get('t3', False)
        today = str(datetime.now())
        filename = request.FILES['t4'].name
        myfile = request.FILES['t4'].read()
        count = 0
        mysqlConnect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'SecureEmail',charset='utf8')
        with mysqlConnect:
            result = mysqlConnect.cursor()
            result.execute("select max(mail_id) from emails")
            lists = result.fetchall()
            for ls in lists:
                count = ls[0]
        if count is not None:
            count += 1
        else:
            count = 1
        key = computeQuantumKeys(myfile)
        iv, ciphertext = quantumEncryptMessage(msg.encode(), key, "EmailApp/static/files/"+str(count)+".txt")
        iv, ciphertext = quantumEncryptMessage(myfile, key, "EmailApp/static/files/"+filename)
        dbconnection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'SecureEmail',charset='utf8')
        dbcursor = dbconnection.cursor()
        qry = "INSERT INTO emails(mail_id,sender_name,receiver_name,send_date,subject,attached_file) VALUES('"+str(count)+"','"+username+"','"+receiver+"','"+today+"','"+subject+"','"+filename+"')"
        dbcursor.execute(qry)
        dbconnection.commit()
        context= {'data':'Message successfully sent to '+receiver+'Encrypted Message : '+str(ciphertext)}
        return render(request,'UserScreen.html', context)

def getEncrypted(path):
    with open(path, "rb") as file:
        data = file.read()
    file.close()
    return data[0:10]

def DecryptMessage(request):
    if request.method == 'GET':
        filename = request.GET.get('msgid', False)
        plain_text = quantumDecryptMessage("EmailApp/static/files/"+filename+".txt")
        context= {'data':'Decrypted Message : '+str(plain_text.decode())}
        return render(request,'UserScreen.html', context)

def DownloadAction(request):
    if request.method == 'GET':
        filename = request.GET.get('filename', False)
        content = quantumDecryptMessage("EmailApp/static/files/"+filename)
        response = HttpResponse(content,content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename='+filename
        return response

def ViewEmail(request):
    if request.method == 'GET':
        global username
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Mail ID</font></th>'
        output+='<th><font size=3 color=black>Sender Name</font></th>'
        output+='<th><font size=3 color=black>Receiver Name</font></th>'
        output+='<th><font size=3 color=black>Mail Date</font></th>'
        output+='<th><font size=3 color=black>Subject</font></th>'
        output+='<th><font size=3 color=black>Encrypted Message</font></th>'
        output+='<th><font size=3 color=black>Decrypt Message</font></th>'
        output+='<th><font size=3 color=black>Decrypt & Download Attachment</font></th></tr>'
        mysqlConnect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'SecureEmail',charset='utf8')
        with mysqlConnect:
            result = mysqlConnect.cursor()
            result.execute("select * from emails")
            lists = result.fetchall()
            for arr in lists:
                if arr[1] == username or arr[2] == username:
                    output+='<tr><td><font size=3 color=black>'+str(arr[0])+'</font></td>'
                    output+='<td><font size=3 color=black>'+arr[1]+'</font></td>'
                    output+='<td><font size=3 color=black>'+str(arr[2])+'</font></td>'
                    output+='<td><font size=3 color=black>'+str(arr[3])+'</font></td>'
                    output+='<td><font size=3 color=black>'+str(arr[4])+'</font></td>'
                    output+='<td><font size=3 color=black>'+str(getEncrypted('EmailApp/static/files/'+str(arr[0])+".txt"))+'</font></td>'
                    output+='<td><a href=\'DecryptMessage?filename='+str(arr[5])+'&msgid='+str(arr[0])+'\'><font size=3 color=black>Click Here</font></a></td>'
                    output+='<td><a href=\'DownloadAction?filename='+str(arr[5])+'&msgid='+str(arr[0])+'\'><font size=3 color=black>Click Here</font></a></td></tr>'
        output+="</table><br/><br/><br/><br/><br/><br/>"
        context= {'data':output}
        return render(request, 'UserScreen.html', context)             
        

def ComposeMail(request):
    if request.method == 'GET':
        global username
        output = '<tr><td><font size="3" color="black">Subject</td><td><select name="t1">'
        mysqlConnect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'SecureEmail',charset='utf8')
        with mysqlConnect:
            result = mysqlConnect.cursor()
            result.execute("select username from user_signup")
            lists = result.fetchall()
            for ls in lists:
                if ls[0] != username:
                    output+='<option value="'+ls[0]+'">'+ls[0]+'</option>'
        output += "</select></td></tr>"            
        context= {'data1':output}
        return render(request,'ComposeMail.html', context)

def index(request):
    if request.method == 'GET':
        return render(request,'index.html', {})

def UserLogin(request):
    if request.method == 'GET':
       return render(request, 'UserLogin.html', {})        

def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})
    
def isUserExists(username):
    is_user_exists = False
    global details
    mysqlConnect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'SecureEmail',charset='utf8')
    with mysqlConnect:
        result = mysqlConnect.cursor()
        result.execute("select * from user_signup where username='"+username+"'")
        lists = result.fetchall()
        for ls in lists:
            is_user_exists = True
    return is_user_exists    

def RegisterAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        email = request.POST.get('t4', False)
        address = request.POST.get('t5', False)
        record = isUserExists(username)
        page = None
        if record == False:
            dbconnection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'SecureEmail',charset='utf8')
            dbcursor = dbconnection.cursor()
            qry = "INSERT INTO user_signup(username,password,phone_no,email,address) VALUES('"+str(username)+"','"+password+"','"+contact+"','"+email+"','"+address+"')"
            dbcursor.execute(qry)
            dbconnection.commit()
            if dbcursor.rowcount == 1:
                data = "Signup Done! You can login now"
                context= {'data':data}
                return render(request,'Register.html', context)
            else:
                data = "Error in signup process"
                context= {'data':data}
                return render(request,'Register.html', context) 
        else:
            data = "Given "+username+" already exists"
            context= {'data':data}
            return render(request,'Register.html', context)


def checkUser(uname, password, utype):
    global username
    msg = "Invalid Login Details"
    mysqlConnect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'SecureEmail',charset='utf8')
    with mysqlConnect:
        result = mysqlConnect.cursor()
        result.execute("select * from "+utype+" where username='"+uname+"' and password='"+password+"'")
        lists = result.fetchall()
        for ls in lists:
            msg = "success"
            username = uname
            break
    return msg

def UserLoginAction(request):
    if request.method == 'POST':
        global username
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        msg = checkUser(username, password, "user_signup")
        if msg == "success":
            context= {'data':"Welcome "+username}
            return render(request,'UserScreen.html', context)
        else:
            context= {'data':msg}
            return render(request,'UserLogin.html', context)
        
