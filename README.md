# GestureFlow – AI Hand Gesture Control System

GestureFlow is an AI-powered hand gesture control system that enables users to interact with their computer using simple hand movements and gestures. It uses computer vision and hand tracking technology to detect hand landmarks and recognize gestures in real time.

The system aims to provide a touch-free, interactive, and user-friendly way to control computer operations.

## Features

- Real-time hand detection and tracking.
- Hand landmark detection using MediaPipe.
- Finger detection and gesture recognition.
- Gesture-based computer control.
- Interactive dashboard.
- Firebase Authentication for user login and authentication.
- User-friendly interface.

## Technologies Used

- **Programming Language:** Python
- **Computer Vision:** OpenCV
- **Hand Tracking:** MediaPipe
- **Authentication:** Firebase Authentication
- **Database:** SQLite (where applicable)
- **Development Environment:** Visual Studio Code

## Project Structure

```text
GestureFlow/
│
├── main.py
├── home_dashboard.py
├── hand_detection.py
├── finger_detection.py
├── gesture_logic.py
├── auth_app.py
├── auth_service.py
├── hand_landmarker.task
├── requirements.txt
└── .gitignore
```

## Installation and Setup

1. Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/GestureFlow-AI-Hand-Gesture-Control-System.git
```

2. Navigate to the project directory:

```bash
cd GestureFlow-AI-Hand-Gesture-Control-System
```

3. Create a virtual environment:

```bash
python -m venv venv
```

4. Activate the virtual environment:

**Windows:**
```bash
venv\Scripts\activate
```

5. Install the required dependencies:

```bash
pip install -r requirements.txt
```

6. Configure Firebase credentials locally using the environment variables required by the application. Do not upload private credentials to GitHub.

7. Run the application:

```bash
python main.py
```

## Requirements

- Python installed on your system.
- Webcam.
- Stable internet connection for Firebase Authentication.
- Required Python libraries listed in `requirements.txt`.

## Future Enhancements

- Support for additional hand gestures.
- Improved gesture recognition accuracy.
- More customizable computer control features.
- Enhanced user interface and functionality.

## Author

**Khushbu Bhadauria**

MCA Student

---

*GestureFlow – Making computer interaction smarter through hand gestures.*
