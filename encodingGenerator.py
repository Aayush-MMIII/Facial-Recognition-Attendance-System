import cv2
import face_recognition
import pickle
import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

# connecting to the database
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://smart-attendance-system-4cabf-default-rtdb.firebaseio.com/",
    "storageBucket": "smart-attendance-system-4cabf.appspot.com"
})

# Importing images into a list and separating the ID's
folderPath = "images"
pathList = os.listdir(folderPath)

imgList = []
studentIds = []

for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentIds.append(os.path.splitext(path)[0])

    # sending the images to the database
    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

# Generating encoding of the images
def findEncodings(imgList):
    encodeList = []
    for img in imgList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


print("ENCODING STARTED ...")
# Creating a list of encoded images
encodeListKnown = findEncodings(imgList)
# Saving the encodings with the ids inside a list
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("ENCODING COMPLETE !!!")

# Creating an encoding file and saving the encoding data
file = open("encodeFile.p", "wb")
pickle.dump(encodeListKnownWithIds, file)
print("FILE SAVED !!!")
