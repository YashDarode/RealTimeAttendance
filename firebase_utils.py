import firebase_admin
from firebase_admin import credentials, db, storage
import cv2
import numpy as np


# Fetch all students from Firebase
def fetch_students():
    ref = db.reference('Students')
    students = ref.get()
    return students


# Add a new student to Firebase
def add_student_to_firebase(name, student_id, image_file):
    ref = db.reference(f'Students/{student_id}')

    # Upload image to Firebase Storage
    bucket = storage.bucket()
    blob = bucket.blob(f'Images/{student_id}.png')
    blob.upload_from_file(image_file, content_type='image/png')

    # Store student data in Firebase Realtime Database
    ref.set({
        'name': name,
        'total_attendance': 0,
        'last_attendance_time': "2000-01-01 00:00:00"
    })
