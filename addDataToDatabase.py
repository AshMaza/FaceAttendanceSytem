import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://faceattendancerealtime-c05ea-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')
data = {
    "123" : {
        "name" : "Virat Kohli",
        "major" : "Cricket",
        "starting_year" : 2008 , 
        "total_attendance" : 6 ,
        "standing": "A+",
        "year" : 4 ,
        "last_attendance_time": "2023-07-23  00:54:34"
    },
    "345" : {
        "name" : "Elon Musk",
        "major" : "Entrepreneur",
        "starting_year" : 2014 , 
        "total_attendance" : 17 ,
        "standing": "A",
        "year" : 3 ,
        "last_attendance_time": "2023-07-23  00:34:34"
    },
    "567" : {
        "name" : "Mazahir Zaidi",
        "major" : "CSE",
        "starting_year" : 2020 , 
        "total_attendance" : 20 ,
        "standing": "A++",
        "year" : 4 ,
        "last_attendance_time": "2023-07-23  00:24:34"
    }
}

for key , value in data.items():
    ref.child(key).set(value)