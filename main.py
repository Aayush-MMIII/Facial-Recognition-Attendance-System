import cv2
import os
import pickle
import cvzone
import face_recognition
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import numpy as np
from firebase_admin import storage
from datetime import datetime

# connecting to the database
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://smart-attendance-system-4cabf-default-rtdb.firebaseio.com/",
    "storageBucket": "smart-attendance-system-4cabf.appspot.com"
})

bucket = storage.bucket()
# Getting the webcam access
# Specifying 0 for the default camera
cap = cv2.VideoCapture(0)

# Importing the background
background = cv2.imread("resources/background.png")

# Checking the camera
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# Setting the width and height of the frame
cap.set(3, 500)  # width
cap.set(4, 500)  # height

# Importing modes into a list
modeFolderPath = "resources/modes"
modeList = os.listdir(modeFolderPath)
imgModeList = []

for path in modeList:
    imgModeList.append(cv2.imread(os.path.join(modeFolderPath, path)))

# Loading the encodeFile
print("LOADING FILE ...")
file = open("encodeFile.p", "rb")
encodeListKnownWithIds = pickle.load(file)
file.close()

encodeListKnown, studentIds = encodeListKnownWithIds
print("SUCCESSFULLY LOADED FILE !!!")

modeType = 0
counter = 0
id = -1
imgStudent=[]

while True:
    # Reading a frame from the camera
    success, img = cap.read()

    # Checking the frame
    if not success:
        print("Error: Could not read frame.")
        break

    # Reducing the size of the image 1/4
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurrentFrame = face_recognition.face_locations(imgS)
    encodeCurrentFrame = face_recognition.face_encodings(imgS, faceCurrentFrame)

    # Displaying the webcam over the background
    background[171:171 + 480, 81:81 + 640] = img

    # Displaying the modes over the background
    background[61:61 + 600, 781:781 + 420] = imgModeList[modeType]

    if faceCurrentFrame:
        # comparing the generated encodings with actual encodings
        for encodeFace, faceLoc in zip(encodeCurrentFrame, faceCurrentFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDistance = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDistance)

            if matches[matchIndex]:
                print("Known Face Detected !!!")
                print(studentIds[matchIndex])
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                bbox = 81 + x1, 171 + y1, x2 - x1, y2 - y1
                background = cvzone.cornerRect(background, bbox, rt=0)
                id = studentIds[matchIndex]
                if counter==0:
                    # Defining the text, position, and font settings
                    text = "Loading..."
                    position = (350, 410)
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 1
                    font_color = (255, 255, 255)  # White color in BGR
                    thickness = 2

                    # Puting text on the background image
                    cv2.putText(background, text, position, font, font_scale, font_color, thickness)
                    cv2.imshow("Face Attendance", background)
                    cv2.waitKey(1)
                    counter=1
                    modeType=1

        if counter!=0:
            if counter==1:
                #getting the data from the database
                studentInfo = db.reference(f'Students/{id}').get()

                #getting the images from the storage
                blob = bucket.get_blob(f'images/{id}.jpg')
                array = np.frombuffer(blob.download_as_string(),np.uint8)
                imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)

                #updating data of attendance
                ref = db.reference(f'Students/{id}')
                datetimeObject = datetime.strptime(studentInfo['Last Attendance'], "%Y-%m-%d %H:%M:%S")
                secElapsed = (datetime.now()-datetimeObject).total_seconds()
                studentInfo['Total Attendance'] += 1

                if secElapsed>30:
                    ref.child('Total Attendance').set(studentInfo['Total Attendance'])
                    ref.child('Last Attendance').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    background[61:61 + 600, 781:781 + 420] = imgModeList[modeType]

            if modeType!=3:

                if 10<counter<20:
                    modeType = 2
                    background[61:61 + 600, 781:781 + 420] = imgModeList[modeType]

                if counter<=10:
                    cv2.putText(background,str(id),(900,445),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
                    cv2.putText(background, str(studentInfo['Course']), (960, 510), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(background, str(studentInfo['Year']), (930, 570), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(background, str(studentInfo['Total Attendance']), (780, 90), cv2.FONT_HERSHEY_COMPLEX, 1,(255, 255, 255), 2)
                    background[80:80+300,835:835+300] = imgStudent
                counter+=1

                if counter>=20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    background[61:61 + 600, 781:781 + 420] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0

    # Displaying the frame in a window
    # cv2.imshow("Webcam", img)
    # Displaying the background with webcam
    cv2.imshow("Face Attendance", background)

    # Breaking the loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Releasing the video capture object and destroying the OpenCV window
cap.release()
cv2.destroyAllWindows()
