# **Real-Time Attendance System Using Face Recognition**

This is a real-time **Face Recognition Attendance System** built with **Flask, OpenCV, Firebase, and Face Recognition API**. It captures live video, detects faces, and updates attendance records in a Firebase database.

## **🚀 Features**
- **Live Video Streaming** 📷 using OpenCV
- **Face Recognition** 🤖 with `face_recognition` library
- **Firebase Integration** 🔥 for real-time attendance storage
- **Admin Dashboard** 🛠️ to manage students
- **Automatic Attendance Marking** ⏳ with timestamp tracking

---

## **🛠️ Installation & Setup**

### **🔹 1. Clone the Repository**
```sh
git clone https://github.com/YOUR_USERNAME/flask-attendance-system.git
cd flask-attendance-system
```

### **🔹 2. Install Dependencies**
```sh
pip install -r requirements.txt
```

### **🔹 3. Set Up Firebase**
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project & enable **Realtime Database**
3. Download the `serviceAccountKey.json` file
4. Place it inside your project folder

### **🔹 4. Run the Application**
```sh
python app.py
```
The server will start on **http://127.0.0.1:5000/**

---

## **📡 Deployment on Render**

### **1️⃣ Push Your Code to GitHub**
```sh
git add .
git commit -m "Deploying to Render"
git push origin main
```

### **2️⃣ Deploy on Render**
1. Go to [Render](https://render.com/)
2. Click **New Web Service**
3. Connect your GitHub repository
4. Use this **start command**:
   ```sh
   gunicorn app:app
   ```
5. Click **Deploy** 🎉

---

## **📜 License**
This project is **open-source** and free to use under the MIT License.

🚀 Happy Coding!

