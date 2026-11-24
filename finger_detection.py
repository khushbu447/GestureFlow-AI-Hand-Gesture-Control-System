
import cv2
import mediapipe as mp

# MediaPipe Tasks API
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Model file
model_path = "hand_landmarker.task"

# Hand Landmarker configuration
options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=1
)

# Function to count fingers
def count_fingers(landmarks, handedness):
    count = 0

    # Thumb detection
    if handedness == "Right":
        if landmarks[4].x < landmarks[3].x:
            count += 1
    else:
        if landmarks[4].x > landmarks[3].x:
            count += 1

    # Other four fingers
    finger_tips = [8, 12, 16, 20]
    finger_pips = [6, 10, 14, 18]

    for tip, pip in zip(finger_tips, finger_pips):
        if landmarks[tip].y < landmarks[pip].y:
            count += 1

    return count


# Start hand detection
with HandLandmarker.create_from_options(options) as landmarker:

    cap = cv2.VideoCapture(0)

    while True:
        success, frame = cap.read()

        if not success:
            print("Camera not found!")
            break

        frame = cv2.flip(frame, 1)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        result = landmarker.detect(mp_image)

        finger_count = 0

        if result.hand_landmarks:

            landmarks = result.hand_landmarks[0]

            # Get handedness
            handedness = "Right"

            if result.handedness:
                handedness = result.handedness[0][0].category_name

            finger_count = count_fingers(
                landmarks,
                handedness
            )

            # Draw landmarks
            h, w, _ = frame.shape

            for landmark in landmarks:
                x = int(landmark.x * w)
                y = int(landmark.y * h)

                cv2.circle(
                    frame,
                    (x, y),
                    5,
                    (0, 255, 0),
                    -1
                )

        # Display finger count
        cv2.putText(
            frame,
            f"Fingers: {finger_count}",
            (30, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.imshow("GestureFlow - Finger Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()