import cv2
import os
import pickle
import face_recognition
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://faceattendancerealtime-c05ea-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancerealtime-c05ea.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

imgBackground = cv2.imread('Resources/background.png')

#importing the mode images into a list
folderModePath = 'Resources/Modes'  
modePathList = os.listdir(folderModePath)
imgModeList = []

for path in modePathList:  
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# print(len(imgModeList))

#load the encoding file
print("Loading The Encoding....")
file = open('EncodeFile.p','rb')
encodeListKnowWithIds = pickle.load(file)
file.close()
encodeListKnown,studentIds = encodeListKnowWithIds
print("Encode File loaded...")
# print(studentIds)

modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()

    imgS = cv2.resize(img , (0,0) , None , 0.25,0.25)
    imgS = cv2.cvtColor(imgS , cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS,faceCurFrame)

    imgBackground[162:162+480, 55:55+640] = img
    imgBackground[44:44 + 633 , 808:808 + 414] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace , faceLoc in zip(encodeCurFrame,faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
            # print("matches",matches)
            # print("faceDis",faceDis)

            matchIndex = np.argmin(faceDis)
            # print("matchIndex",matchIndex)

            if matches[matchIndex]:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                color = (0, 255, 0)  # Green color in BGR format
                thickness = 2  # Thickness of the rectangle edges
                imgBackground = cv2.rectangle(imgBackground, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), color, thickness)
                id = studentIds[matchIndex]

                if counter == 0:
                    counter = 1
                    modeType = 1
                
        if counter!=0:
            if counter==1:
                #get the data
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)
                #get the image from storage
                blob = bucket.get_blob(f'Images/{id}.jpeg')
                array = np.frombuffer(blob.download_as_string(),np.int8)
                imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)
                imgStudent = cv2.resize(imgStudent, (216, 216))
                # update data of attendance
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],"%Y-%m-%d %H:%M:%S")
                secondElapsed = (datetime.now()-datetimeObject).total_seconds()
                print(secondElapsed)

                if secondElapsed>30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType=3
                    counter=0
                    imgBackground[44:44 + 633 , 808:808 + 414] = imgModeList[modeType]


            if modeType!=3:


                if 10<counter<20:
                    modeType = 2
                
                imgBackground[44:44 + 633 , 808:808 + 414] = imgModeList[modeType]


                
                if counter<=10:
                    cv2.putText(imgBackground,str(studentInfo['total_attendance']),(861,125),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                    cv2.putText(imgBackground,str(studentInfo['major']),(1006,550),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                    cv2.putText(imgBackground,str(id),(1006,493),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                    cv2.putText(imgBackground,str(studentInfo['standing']),(910,625),cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
                    cv2.putText(imgBackground,str(studentInfo['year']),(1025,625),cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
                    cv2.putText(imgBackground,str(studentInfo['starting_year']),(1125,625),cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
                    
                    (w,h), _ = cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
                    offset = (414 - w) // 2
                    cv2.putText(imgBackground,str(studentInfo['name']),(808+offset,445),cv2.FONT_HERSHEY_COMPLEX,1,(50,50,50),1)
                    
                    imgBackground[175:175+216 , 909:909+216 ] = imgStudent 


                counter+=1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44 + 633 , 808:808 + 414] = imgModeList[modeType]

    else:
        modeType=0
        counter=0

    cv2.imshow("Face Attendance", imgBackground)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
