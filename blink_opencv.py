import cv2
import time
import numpy as np
import socket
import json
import statistics
from collections import deque, Counter
from deepface import DeepFace
import os

# Enforce keras backend
os.environ["DEEPFACE_BACKEND"] = "keras"

# =============================
# UDP SOCKET CONFIGURATION
# =============================
UDP_IP = "127.0.0.1"
RECEIVE_PORT = 5005   # Listens to the game
SEND_PORT = 5006      # Sends data to the game

sock_receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_receive.bind((UDP_IP, RECEIVE_PORT))
sock_receive.setblocking(False)

sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# =============================
# DATA LOGGING VARIABLES
# =============================
recording = False
current_phase = ""
recorded_arousals = []
recorded_emotions = []

# =============================
# CASCADES
# =============================
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# =============================
# BLINK VARIABLES
# =============================
blink_count = 0
eyes_closed = False
blink_start_time = None
blink_durations = []
real_blink_timestamps = []

# =============================
# EMOTION STABILITY
# =============================
emotion_buffer = deque(maxlen=6)
frame_count = 0
smoothed_emotion = "neutral"

# =============================
# AROUSAL & VALENCE FUNCTIONS
# =============================
def compute_arousal(blink_rate, avg_blink_duration):
    br_norm = (blink_rate - 0.1) / (0.6 - 0.1)
    br_norm = max(0.0, min(br_norm, 1.0))

    bd_norm = 1 - ((avg_blink_duration - 0.1) / (0.4 - 0.1))
    bd_norm = max(0.0, min(bd_norm, 1.0))

    arousal = 0.7 * br_norm + 0.3 * bd_norm
    arousal = arousal - 0.15 # baseline correction
    return max(0.0, min(arousal, 1.0))

def map_valence(emotion):
    weights = {
        "happy": 0.8, "surprise": 0.5, "neutral": 0.0,
        "sad": -0.3, "angry": -0.9, "fear": -0.9, "disgust": -0.7
    }
    return weights.get(emotion, 0.0)

def fused_state(arousal, valence):
    if arousal < 0.35: 
        return "Calm"
    if -0.4 <= valence <= 0.4 and arousal < 0.5: 
        return "Neutral"
    if valence > 0.4: 
        return "Excitement" if arousal >= 0.5 else "Happy/Content"
    if valence < -0.4: 
        return "Stress/Fear" if arousal >= 0.5 else "Sad/Tired"
    return "Neutral"

# =============================
# CAMERA & MAIN LOOP
# =============================
cap = cv2.VideoCapture(0)
print("Facial Detection Bridge Started. Listening for game commands...")

while True:
    # 1. CHECK FOR GAME COMMANDS
    try:
        data, addr = sock_receive.recvfrom(1024)
        message = json.loads(data.decode('utf-8'))
        command = message.get("command")
        phase = message.get("phase")

        if command == "START":
            print(f"--- START RECORDING: {phase} ---")
            recording = True
            current_phase = phase
            recorded_arousals = []
            recorded_emotions = []
            
        elif command == "STOP":
            print(f"--- STOP RECORDING: {phase} ---")
            recording = False
            
            # Calculate Summary
            mean_arousal = 0.0
            dominant_emotion = "neutral"
            calculated_state = "neutral"
            
            if len(recorded_arousals) > 0:
                mean_arousal = round(np.mean(recorded_arousals), 2)
            if len(recorded_emotions) > 0:
                try:
                    dominant_emotion = statistics.mode(recorded_emotions)
                except statistics.StatisticsError:
                    dominant_emotion = Counter(recorded_emotions).most_common(1)[0][0]
            
            # Use your custom logic to determine final state for the CSV
            valence = map_valence(dominant_emotion)
            calculated_state = fused_state(mean_arousal, valence)

            results = {
                "type": "summary_data",
                "phase": phase,
                "mean_arousal": mean_arousal,
                "dominant_emotion": dominant_emotion,
                "state": calculated_state
            }
            
            sock_send.sendto(json.dumps(results).encode('utf-8'), (UDP_IP, SEND_PORT))
            print(f"Sent data to game: {results}")

    except BlockingIOError:
        pass 

    # 2. PROCESS VIDEO FRAME
    ret, frame = cap.read()
    if not ret: break
    frame_count += 1

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    eye_detected = False

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        if len(eyes) > 0: eye_detected = True
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

    # 3. BLINK LOGIC
    current_time = time.time()
    if not eye_detected:
        if not eyes_closed:
            blink_start_time = current_time
            eyes_closed = True
    else:
        if eyes_closed:
            blink_count += 1
            blink_durations.append(current_time - blink_start_time)
            real_blink_timestamps.append(current_time)
            eyes_closed = False

    window = 10
    real_blink_timestamps = [t for t in real_blink_timestamps if current_time - t <= window]
    
    blink_rate = len(real_blink_timestamps) / window
    avg_blink_duration = np.mean(blink_durations) if blink_durations else 0.2
    current_arousal = compute_arousal(blink_rate, avg_blink_duration)

    # 4. DEEPFACE (Run every 5 frames so the video and sockets don't lag)
    if frame_count % 5 == 0:
        try:
            # silent=True hides the constant terminal spam
            result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False, silent=True)
            emotion = result[0]['dominant_emotion']
        except:
            emotion = "neutral"

        emotion_buffer.append(emotion)
        smoothed_emotion = Counter(emotion_buffer).most_common(1)[0][0]

    # Calculate real-time state
    valence = map_valence(smoothed_emotion)
    current_state = fused_state(current_arousal, valence)

    # 5. LOG DATA IF RECORDING IS ACTIVE
    if recording:
        recorded_arousals.append(current_arousal)
        recorded_emotions.append(smoothed_emotion)
        # Visual indicator that it's currently logging
        cv2.circle(frame, (30, 30), 10, (0, 0, 255), -1) 
        cv2.putText(frame, f"REC: {current_phase}", (50, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

    # 6. UI
    cv2.putText(frame, f"Arousal: {current_arousal:.2f}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,165,255), 2)
    cv2.putText(frame, f"Emotion: {smoothed_emotion}", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
    cv2.putText(frame, f"State: {current_state}", (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

    cv2.imshow("Stable Emotion System Bridge", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


