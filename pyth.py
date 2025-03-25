import threading
import asyncio
from flask import Flask, render_template, Response, request, redirect, url_for, flash, session
from PIL import Image
import firebase_admin
from firebase_admin import credentials, db, storage
import os
import cv2
import numpy as np
import pickle
import face_recognition
from datetime import datetime
import cvzone

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Firebase initialization
cred = credentials.Certificate("serviceAccountKeys.son")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://your-project-id.firebaseio.com/",
    'storageBucket': "your-project-id.appspot.com"
})

bucket = storage.bucket()

# Load the known face encodings
print("Loading Encode File ...")
with open('EncodeFile.p', 'rb') as file:
    encodeListKnownWithIds = pickle.load(file)
encodeListKnown, studentIds = encodeListKnownWithIds
print("Encode File Loaded")


def update_attendance(student_id):
    """Update attendance in the database for a recognized student."""
    ref = db.reference(f'Students/{student_id}')
    student_info = ref.get()

    if student_info:
        student_info['total_attendance'] += 1
        ref.child('total_attendance').set(student_info['total_attendance'])
        ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


async def async_update_attendance(student_id):
    """Run the update attendance function in a separate thread."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, update_attendance, student_id)


def generate_frames():
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    imgBackground = cv2.imread('Resources/background.png')
    imgModeList = [cv2.imread(os.path.join('Resources/Modes', path)) for path in os.listdir('Resources/Modes')]

    modeType = 0
    counter = 0
    id = -1
    imgStudent = []

    while True:
        success, img = cap.read()
        if not success:
            break

        imgS = cv2.resize(img, None, fx=0.25, fy=0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        faceCurFrame = face_recognition.face_locations(imgS)
        encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

        imgBackground[162:162 + 480, 55:55 + 640] = img

        if faceCurFrame:
            for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace, tolerance=0.4)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

                matchIndex = np.argmin(faceDis)

                if matches[matchIndex] and faceDis[matchIndex] < 0.5:
                    id = studentIds[matchIndex]
                    y1, x2, y2, x1 = (i * 4 for i in faceLoc)
                    bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                    imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

                    if counter == 0:
                        cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                        counter = 1
                        modeType = 1
                else:
                    cv2.putText(imgBackground, "Face not recognized", (275, 400), cv2.FONT_HERSHEY_COMPLEX, 1,
                                (0, 0, 255), 2)
                    modeType = 0
                    counter = 0

            if counter != 0 and id != -1:
                studentInfo = db.reference(f'Students/{id}').get()
                if studentInfo:
                    last_attendance_time = studentInfo['last_attendance_time']
                    datetimeObject = datetime.strptime(last_attendance_time,
                                                       "%Y-%m-%d %H:%M:%S") if last_attendance_time else None
                    secondsElapsed = (datetime.now() - datetimeObject).total_seconds() if datetimeObject else float(
                        'inf')

                    if secondsElapsed > 30:
                        # Run the attendance update asynchronously
                        asyncio.run(async_update_attendance(id))

                    blob = bucket.get_blob(f'Images/{id}.png')
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    imgStudent = cv2.imdecode(array, cv2.IMREAD_COLOR)
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if modeType != 3:
                    if 10 < counter < 20:
                        modeType = 2
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                    if counter <= 10:
                        cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550), cv2.FONT_HERSHEY_COMPLEX,
                                    0.5, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(id), (1006, 493), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255),
                                    1)
                        cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625), cv2.FONT_HERSHEY_COMPLEX,
                                    0.6, (100, 100, 100), 1)
                        cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                                    (100, 100, 100), 1)
                        cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                        (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                        offset = (414 - w) // 2
                        cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                        imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

                    counter += 1

                if counter >= 20:
                        counter = 0
                        modeType = 0
                        imgStudent = []
                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
        else:
            modeType = 0
            counter = 0

        _, buffer = cv2.imencode('.jpg', imgBackground)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin123':
            session['admin'] = username
            return redirect(url_for('students'))
        else:
            flash('Invalid credentials, please try again!')

    return render_template('admin_login.html')


@app.route('/students', methods=['GET', 'POST'])
def students():
    if 'admin' in session:
        students_ref = db.reference('Students')
        students_data = students_ref.get()

        if request.method == 'POST':
            student_id = request.form['id']
            student_name = request.form['name']
            students_ref.child(student_id).set({
                'name': student_name,
                'total_attendance': 0,
                'last_attendance_time': None
            })

            flash('Student added successfully!')
            return redirect(url_for('students'))

        return render_template('students.html', students=students_data)

    return redirect(url_for('admin_login'))


@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        student_id = request.form['student_id']
        name = request.form['name']
        age = request.form['age']
        major = request.form['major']
        standing = request.form['standing']
        starting_year = request.form['starting_year']
        year = request.form['year']
        image = request.files['image']

        # Create a dictionary for the student data
        student_data = {
            'last_attendance_time': None,
            'name': name,
            'age': age,
            'major': major,
            'standing': standing,
            'starting_year': starting_year,
            'total_attendance': 0,
            'year': year
        }

        students_ref = db.reference('Students')
        students_ref.child(student_id).set(student_data)

        # Resize and upload the image
        img = Image.open(image)
        img = img.resize((216, 216))
        file_name = f"{student_id}.png"
        img_path = os.path.join('/tmp', file_name)

        img.save(img_path)
        blob = bucket.blob(f'Images/{file_name}')
        blob.upload_from_filename(img_path)
        os.remove(img_path)

        flash('Student added successfully!')
        return redirect(url_for('students'))

    return render_template('add_student.html')


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' in session:
        return render_template('admin_dashboard.html')
    return redirect(url_for('admin_login'))


@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))


if __name__ == '__main__':
    app.run(debug=True)
