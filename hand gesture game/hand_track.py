import cv2
import mediapipe as mp
import numpy as np
import os
import logging
import absl.logging
import pyautogui

# Suppress all warnings and logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
absl.logging.set_verbosity(absl.logging.ERROR)
logging.getLogger().setLevel(logging.ERROR)

from mediapipe.tasks.python.vision.core.image import Image, ImageFormat
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions, HandLandmarksConnections, drawing_utils
from mediapipe.tasks.python.core.base_options import BaseOptions

# Gesture thresholds
GESTURE_THRESHOLD = 0.1  # Normalized distance threshold
key_pressed = {'left': False, 'right': False, 'up': False, 'down': False}

def detect_gesture(hand_landmarks):
    """Detect gesture based on thumb tip position relative to wrist."""
    wrist = hand_landmarks[0]  # Wrist landmark
    thumb_tip = hand_landmarks[4]  # Thumb tip landmark
    
    dx = thumb_tip.x - wrist.x
    dy = thumb_tip.y - wrist.y
    
    if abs(dx) > GESTURE_THRESHOLD or abs(dy) > GESTURE_THRESHOLD:
        if abs(dx) > abs(dy):
            if dx < -GESTURE_THRESHOLD:
                return 'left'
            elif dx > GESTURE_THRESHOLD:
                return 'right'
        else:
            if dy < -GESTURE_THRESHOLD:
                return 'up'
            elif dy > GESTURE_THRESHOLD:
                return 'down'
    return None

def press_key(direction):
    """Press the corresponding key for the direction."""
    key_map = {'left': 'left', 'right': 'right', 'up': 'up', 'down': 'down'}
    if direction in key_map and not key_pressed[direction]:
        pyautogui.keyDown(key_map[direction])
        key_pressed[direction] = True

def release_key(direction):
    """Release the key if it was pressed."""
    key_map = {'left': 'left', 'right': 'right', 'up': 'up', 'down': 'down'}
    if direction in key_map and key_pressed[direction]:
        pyautogui.keyUp(key_map[direction])
        key_pressed[direction] = False

def release_all_keys():
    """Release all keys."""
    for direction in key_pressed:
        release_key(direction)

# Initialize MediaPipe
# Using Tasks API since legacy mp.solutions is not available in this version
model_path = 'hand_landmarker.task'  # Download from https://developers.google.com/mediapipe/solutions/vision/hand_landmarker

try:
    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        num_hands=1,
        min_hand_detection_confidence=0.7,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.7
    )

    hands = HandLandmarker.create_from_options(options)
except Exception as e:
    print(f"Error loading hand landmarker model: {e}")
    print("Make sure 'hand_landmarker.task' is in the current directory.")
    exit(1)

# Start webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit(1)

try:
    while True:
        success, img = cap.read()
        if not success:
            continue

        # Flip for mirror effect
        img = cv2.flip(img, 1)

        # Convert to RGB
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Create MediaPipe Image
        mp_image = Image(ImageFormat.SRGB, np.asarray(rgb))

        # Process image
        result = hands.detect(mp_image)

        # Detect gesture and control keys
        current_gesture = None
        if result.hand_landmarks:
            for hand_landmarks in result.hand_landmarks:
                current_gesture = detect_gesture(hand_landmarks)
                drawing_utils.draw_landmarks(
                    img,
                    hand_landmarks,
                    HandLandmarksConnections.HAND_CONNECTIONS
                )

        # Handle key presses
        if current_gesture:
            press_key(current_gesture)
        else:
            release_all_keys()

        # Show gesture status
        status = f"Gesture: {current_gesture}" if current_gesture else "Gesture: None"
        cv2.putText(img, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Show output
        cv2.imshow("Hand Tracking", img)

        # Exit on ESC
        if cv2.waitKey(1) & 0xFF == 27:
            break
finally:
    release_all_keys()
    hands.close()
    cap.release()
    cv2.destroyAllWindows()


    