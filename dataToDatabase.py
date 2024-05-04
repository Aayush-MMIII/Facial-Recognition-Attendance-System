import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://smart-attendance-system-4cabf-default-rtdb.firebaseio.com/"
})

ref = db.reference("Students")
data = {
    "052": {
        "Name": "Aayush Singh",
        "Course": "BCA",
        "Year": 2021,
        "Total Attendance": 12,
        "Last Attendance": "2024-02-25 08:54:34"
    },
    "043": {
        "Name": "Tim Cook",
        "Course": "B Tech",
        "Year": 2022,
        "Total Attendance": 45,
        "Last Attendance": "2024-03-05 06:30:55"
    },
    "065": {
        "Name": "Jeff Besos",
        "Course": "MBA",
        "Year": 2023,
        "Total Attendance": 78,
        "Last Attendance": "2024-01-07 00:54:34"
    },
    "071": {
        "Name": "Sunder Pichai",
        "Course": "B Tech",
        "Year": 2022,
        "Total Attendance": 91,
        "Last Attendance": "2024-04-04 10:30:30"
    },
    "078": {
        "Name": "Elon Musk",
        "Course": "B Com",
        "Year": 2020,
        "Total Attendance": 51,
        "Last Attendance": "2024-01-08 11:55:44"
    },
    "012": {
        "Name": "Aditya Rawat",
        "Course": "BCA",
        "Year": 2021,
        "Total Attendance": 12,
        "Last Attendance": "2024-01-08 11:55:44"
    },
    "049": {
        "Name": "Japneet Kaur",
        "Course": "BCA",
        "Year": 2021,
        "Total Attendance": 9,
        "Last Attendance": "2024-01-08 11:55:44"
    },
    "021": {
        "Name": "Sareena Wilson",
        "Course": "BCA",
        "Year": 2021,
        "Total Attendance": 8,
        "Last Attendance": "2024-01-08 11:55:44"
    },
    "035": {
        "Name": "Vanshika Kataria",
        "Course": "BCA",
        "Year": 2021,
        "Total Attendance": 25,
        "Last Attendance": "2024-01-08 11:55:44"
    }
}

for key,value in data.items():
    ref.child(key).set(value)