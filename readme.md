# Real-Time Attendance System using Face Recognition

## Overview
This project is a **real-time attendance system** that uses **face recognition** technology to mark attendance automatically. It is built using **Flask, OpenCV, Firebase, and Face Recognition libraries**.

## Features
- **Live face recognition** for attendance marking
- **Flask-based web interface** for administrators
- **Firebase Realtime Database** for storing attendance records
- **Firebase Storage** for storing student images
- **Admin authentication** for managing student records

## Tech Stack
- **Backend:** Flask, Firebase Admin SDK
- **Frontend:** HTML, CSS, JavaScript (Jinja2 for templating)
- **Machine Learning:** OpenCV, Face Recognition, NumPy
- **Database:** Firebase Realtime Database
- **Storage:** Firebase Cloud Storage

## Installation
### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- Pip
- Virtual Environment (optional but recommended)

### Steps
1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/realtime-attendance.git
   cd realtime-attendance
   ```

2. **Create and activate a virtual environment (optional but recommended):**
   ```sh
   python -m venv venv
   source venv/bin/activate  # For Linux/macOS
   venv\Scripts\activate  # For Windows
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Setup Firebase:**
   - Get your `serviceAccountKey.json` from Firebase and place it in the project root.
   - Update `databaseURL` and `storageBucket` in `app.py` with your Firebase project details.

5. **Run the application:**
   ```sh
   python app.py
   ```

6. **Access the web app:**
   Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Deployment (Using Render)
1. **Create a GitHub repository and push your code.**
2. **Go to [Render](https://render.com/) and create a new Web Service.**
3. **Select your GitHub repository.**
4. **Set environment variables in Render:**
   - `FIREBASE_CREDENTIALS`: Convert your `serviceAccountKey.json` into a single-line string and store it in Render’s environment variables.
   - `DATABASE_URL`: Your Firebase database URL.
5. **Set the build and start command:**
   - **Build Command:**
     ```sh
     pip install -r requirements.txt
     ```
   - **Start Command:**
     ```sh
     gunicorn app:app
     ```
6. **Deploy and access your app via the Render-provided URL.**

## Known Issues and Fixes
### **1. WebCam Access on Render**
- Render does not support hardware access like `cv2.VideoCapture(0)`.
- **Fix:** Modify the code to use pre-uploaded images instead.

### **2. Asyncio Errors**
- Render might not handle `asyncio.run()` properly.
- **Fix:** Replace `asyncio.run()` with threading:
  ```python
  import threading
  def async_update_attendance(student_id):
      threading.Thread(target=update_attendance, args=(student_id,)).start()
  ```

### **3. Firebase File Upload Issues**
- Ensure Firebase Storage is properly configured.
- **Fix:** Use bucket blobs correctly:
  ```python
  blob = bucket.blob(f'Images/{file_name}')
  blob.upload_from_filename(img_path)
  ```

## Future Improvements
- Implement **face anti-spoofing** to prevent misuse with printed/static photos.
- Add **email notifications** for low attendance.
- Improve **UI/UX** for better user experience.

## License
This project is **open-source** under the **MIT License**.

## Author
Developed by **Yash Darode** and team.

---
Enjoy using the Real-Time Attendance System! 🚀

