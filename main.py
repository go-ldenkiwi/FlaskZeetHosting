from flask import Flask, render_template, request, redirect
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase import firebase
import random
import datetime as dt

cred = credentials.Certificate("./serviceAccountKey.json")
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()
firebase = firebase.FirebaseApplication('https://musicrc-2d5aa.firebaseio.com', None)

def updatedb(dictdata):
    check = False
    temp = db.collection('user_dataset').where('userId', '==', dictdata['userId']).where('songIndex', '==', dictdata['songIndex']).stream()    

    for doc in temp:
        same_ref = doc.to_dict()  
        sum = dictdata['playCount']+same_ref['playCount']
        db.collection('user_dataset').document(doc.id).update({'playCount' : sum})
        check = True
    
    if check == False:
        doc = db.collection('user_dataset').document(str(dictdata['date']))
        doc.set(dictdata)

def read_collection():
    docs = db.collection('user_dataset').stream()
    dict = {}
    i = 1
    for doc in docs:
        stock = doc.to_dict()
        dict[i] = stock
        i = i+1
    return dict

app = Flask(__name__)

@app.route("/")
@app.route("/home/")
def home():
    return render_template("index.html", data = read_collection())

@app.route("/add/", methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
 
        userId = request.form['userId']
        userId = 'user'+str(userId)
        songIndex = int(request.form['songIndex'])
        playCount = int(request.form['playCount'])
        date = dt.datetime.now()
        dictdata = {'userId' : userId, 'songIndex' : songIndex, 'playCount' : playCount, 'date' : date}
        
        updatedb(dictdata)
        
    return redirect('/')

@app.route("/randadd/", methods=['GET', 'POST'])
def randadd():
    if request.method == 'POST':
        idNum = int(request.form['idNum'])
        indexNum = int(request.form['indexNum'])
        countNum = int(request.form['countNum'])
        num = int(request.form['num'])
        for i in range(num):
            userId = 'user'+str(random.randrange(1,idNum+1))
            songIndex = int(random.randrange(1,indexNum+1))
            playCount = int(random.randrange(1,countNum+1))
            date = dt.datetime.now()
            dictdata = {'userId' : userId, 'songIndex' : songIndex, 'playCount' : playCount, 'date' : date}
            
            updatedb(dictdata)
            
    return redirect('/')

@app.route("/delete/<int:key>", methods=['GET','POST'])
def delete(key):
    if request.method == 'POST':
        data = read_collection()
        
        userId = data[key]['userId']
        songIndex = data[key]['songIndex']
        playCount = data[key]['playCount']
        
        tempdoc = db.collection('user_dataset').where('userId', '==', userId).where('songIndex', '==', songIndex).where('playCount', '==', playCount).stream()
        for doc in tempdoc:
            doc.reference.delete()
            
    return redirect('/')
        



        

if __name__ == '__main__':
    app.run(debug=False, host = '0.0.0.0')