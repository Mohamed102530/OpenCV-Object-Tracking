# 🎯 OpenCV Object Tracking System

An advanced real-time Object Tracking System built using **Python and OpenCV**. The project allows users to upload a video, select a specific object, and track its movement throughout the video.

The system uses the **CSRT (Channel and Spatial Reliability Tracker)** algorithm to track objects without requiring YOLO, Deep Learning, or pretrained models.

## 🚀 Features

- 📤 Upload videos directly from Jupyter Notebook.
- 🎯 Select any object manually using ROI selection.
- 🔍 Track the selected object using the CSRT algorithm.
- 📦 Draw bounding boxes around the tracked object.
- ⚡ Display real-time FPS.
- 📊 Display frame count and tracking status.
- ⚠️ Detect when object tracking is lost.
- 🎥 Save the processed video as an MP4 file.
- 📥 Download the final tracked video.

## 🛠️ Technologies Used

- Python
- OpenCV
- OpenCV Contrib
- NumPy
- IPyWidgets
- Tempfile
- Pathlib

## 📚 Requirements

Install the required libraries:

```bash
pip install opencv-contrib-python
pip install numpy
pip install ipywidgets
```

**Note:** The project requires `opencv-contrib-python` because the CSRT tracker is included in the contrib modules.

## 📂 Project Structure

```text
OpenCV-Object-Tracking/
│
├── Data/
│   └── input_video.mp4
│
├── Object_Tracking.ipynb
│
├── README.md
│
└── requirements.txt
```

## ⚙️ How It Works

The project follows these steps:

1. **Video Upload:** Upload a video file (`.mp4`, `.avi`, or `.mov`).
2. **Video Reading:** OpenCV reads the uploaded video using `cv2.VideoCapture()`.
3. **Object Selection:** Select the object you want to track using `cv2.selectROI()`.
4. **Tracker Initialization:** Initialize the CSRT tracker with the selected object's coordinates.
5. **Object Tracking:** Track the object frame by frame using `tracker.update()`.
6. **Visualization:** Display a bounding box around the tracked object.
7. **Performance Monitoring:** Show FPS, frame count, and tracking status.
8. **Video Export:** Save the final processed video using `cv2.VideoWriter()`.

## ▶️ How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/OpenCV-Object-Tracking.git
```

### 2. Navigate to the Project Directory

```bash
cd OpenCV-Object-Tracking
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Open Jupyter Notebook

```bash
jupyter notebook
```

### 5. Run the Project

- Open `Object_Tracking.ipynb`.
- Execute the notebook cells.
- Upload your video.
- Select the object you want to track.
- Watch the tracking process.
- Download the final output video.

## 📦 Output

The system generates a processed MP4 video containing:

- The tracked object.
- Bounding box visualization.
- Tracking status.
- FPS information.
- Frame counter.

The output video is saved automatically in the system's temporary directory.

## 🧠 Tracking Algorithm

**CSRT (Channel and Spatial Reliability Tracker)**

CSRT is an object tracking algorithm available in OpenCV Contrib.

It uses spatial and channel reliability information to improve tracking accuracy, especially when the object's appearance or surroundings change.

## ⚠️ Limitations

- Tracking accuracy depends on the selected object and video quality.
- The tracker may lose the object when it moves outside the frame.
- Fast movements and significant appearance changes may affect tracking performance.
- The project tracks one selected object at a time.

## 🎓 Project Purpose

This project was developed for learning and practicing:

- Computer Vision.
- Video Processing.
- Object Tracking.
- OpenCV.
- Real-Time Video Analysis.

## 👨‍💻 Author

**Mohamed**

GitHub: [Mohamed102530](https://github.com/Mohamed102530)

---

⭐ If you find this project useful, don't forget to give it a star!