import cv2
import mediapipe as mp
import math
import time
import numpy as np

print("=" * 60)
print("PRODUCTION POSTURE DETECTOR - V4")
print("=" * 60)
print("\nInitializing...")

# Initialize MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh

pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    model_complexity=1
)

# Open webcam
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    camera = cv2.VideoCapture(1)

if not camera.isOpened():
    print("❌ Cannot open webcam!")
    exit(1)

print("✅ Webcam opened!")
print("\n" + "=" * 60)
print("PRODUCTION POSTURE TEST - DISTANCE AWARE")
print("=" * 60)
print("Instructions:")
print("1. Sit with GOOD posture for calibration (3 seconds)")
print("2. Try SLOUCHING - head down, shoulders forward")
print("3. Try LEANING CLOSE to camera - should NOT drop score")
print("4. Try sitting FAR - should still work")
print("\nPress 'q' to quit, 'r' to recalibrate")
print("=" * 60 + "\n")

time.sleep(3)

# Calibration storage
calibration_data = {
    'shoulder_hip_ratio': [],
    'head_shoulder_ratio': [],
    'shoulder_width_ratio': [],
    'frames': 0,
    'complete': False
}


def calculate_distance_aware_posture(landmarks):
    """
    Distance-aware posture detection using PROPORTIONAL measurements
    Key insight: Use ratios, not absolute distances!
    """
    try:
        # Get all landmarks
        nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
        left_eye = landmarks[mp_pose.PoseLandmark.LEFT_EYE.value]
        right_eye = landmarks[mp_pose.PoseLandmark.RIGHT_EYE.value]
        left_ear = landmarks[mp_pose.PoseLandmark.LEFT_EAR.value]
        right_ear = landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value]

        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]

        left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]

        # =====================================================
        # KEY: Use PROPORTIONAL measurements (distance-invariant)
        # =====================================================

        # Calculate shoulder width (for scale reference)
        shoulder_width = math.sqrt(
            (left_shoulder.x - right_shoulder.x) ** 2 +
            (left_shoulder.y - right_shoulder.y) ** 2
        )

        if shoulder_width < 0.05:  # Too small, bad detection
            return None

        # Midpoints
        shoulder_x = (left_shoulder.x + right_shoulder.x) / 2
        shoulder_y = (left_shoulder.y + right_shoulder.y) / 2

        hip_x = (left_hip.x + right_hip.x) / 2
        hip_y = (left_hip.y + right_hip.y) / 2

        ear_x = (left_ear.x + right_ear.x) / 2
        ear_y = (left_ear.y + right_ear.y) / 2

        # =====================================================
        # METRIC 1: Shoulder-Hip Vertical Distance (NORMALIZED)
        # =====================================================
        # Vertical distance between shoulders and hips
        shoulder_hip_vertical = abs(hip_y - shoulder_y)

        # NORMALIZE by shoulder width (distance-invariant!)
        shoulder_hip_ratio = shoulder_hip_vertical / shoulder_width

        # Good posture: ratio ~1.8-2.5
        # Slouched: ratio ~1.0-1.5 (torso compressed)

        if not calibration_data['complete']:
            # Store calibration data
            calibration_data['shoulder_hip_ratio'].append(shoulder_hip_ratio)
        else:
            # Compare to baseline
            baseline_ratio = np.median(calibration_data['shoulder_hip_ratio'])
            ratio_deviation = (baseline_ratio - shoulder_hip_ratio) / baseline_ratio

            # Calculate score
            if ratio_deviation < 0:  # Taller than baseline (even better!)
                torso_score = 100
            elif ratio_deviation < 0.15:  # Within 15%
                torso_score = 100 - (ratio_deviation * 300)
            elif ratio_deviation < 0.30:  # 15-30% shorter
                torso_score = 55 - ((ratio_deviation - 0.15) * 200)
            else:  # Very slouched
                torso_score = max(0, 25 - ((ratio_deviation - 0.30) * 100))

        # =====================================================
        # METRIC 2: Head-Shoulder Vertical Distance (NORMALIZED)
        # =====================================================
        head_shoulder_vertical = abs(shoulder_y - ear_y)

        # NORMALIZE by shoulder width
        head_shoulder_ratio = head_shoulder_vertical / shoulder_width

        # Good posture: ratio ~0.8-1.2
        # Head down: ratio ~0.3-0.6

        if not calibration_data['complete']:
            calibration_data['head_shoulder_ratio'].append(head_shoulder_ratio)
        else:
            baseline_head_ratio = np.median(calibration_data['head_shoulder_ratio'])
            head_deviation = (baseline_head_ratio - head_shoulder_ratio) / baseline_head_ratio

            if head_deviation < 0:  # Head higher than baseline
                head_score = 100
            elif head_deviation < 0.15:
                head_score = 100 - (head_deviation * 400)
            elif head_deviation < 0.30:
                head_score = 40 - ((head_deviation - 0.15) * 200)
            else:
                head_score = max(0, 10 - ((head_deviation - 0.30) * 50))

        # =====================================================
        # METRIC 3: Head Tilt (Forward Head Posture)
        # =====================================================
        # Horizontal distance between ears and shoulders
        head_forward = abs(ear_x - shoulder_x)

        # NORMALIZE by shoulder width
        head_forward_ratio = head_forward / shoulder_width

        # Good: < 0.15 (head above shoulders)
        # Bad: > 0.30 (head forward)

        if head_forward_ratio < 0.15:
            neck_score = 100
        elif head_forward_ratio < 0.30:
            neck_score = 100 - ((head_forward_ratio - 0.15) * 500)
        else:
            neck_score = max(20, 25 - ((head_forward_ratio - 0.30) * 100))

        # =====================================================
        # METRIC 4: Shoulder Levelness
        # =====================================================
        shoulder_tilt = abs(left_shoulder.y - right_shoulder.y)
        shoulder_tilt_ratio = shoulder_tilt / shoulder_width

        if shoulder_tilt_ratio < 0.10:
            symmetry_score = 100
        elif shoulder_tilt_ratio < 0.20:
            symmetry_score = 100 - ((shoulder_tilt_ratio - 0.10) * 500)
        else:
            symmetry_score = max(50, 50 - ((shoulder_tilt_ratio - 0.20) * 200))

        # =====================================================
        # METRIC 5: Visibility/Confidence (detects head down)
        # =====================================================
        # When head tilts down, nose/ear visibility drops
        avg_visibility = (nose.visibility + left_ear.visibility + right_ear.visibility) / 3

        if avg_visibility > 0.9:
            visibility_score = 100
        elif avg_visibility > 0.7:
            visibility_score = 70 + ((avg_visibility - 0.7) * 150)
        else:
            visibility_score = max(30, avg_visibility * 100)

        # =====================================================
        # CALCULATE FINAL SCORE
        # =====================================================
        if not calibration_data['complete']:
            # During calibration, show neutral score
            final_score = 85
        else:
            # Weighted combination
            final_score = (
                    torso_score * 0.35 +  # Torso compression (most important)
                    head_score * 0.25 +  # Head height
                    neck_score * 0.20 +  # Forward head posture
                    visibility_score * 0.12 +  # Head tilt detection
                    symmetry_score * 0.08  # Balance
            )

        final_score = max(0, min(100, final_score))

        # Return metrics
        return {
            'score': int(final_score),
            'shoulder_hip_ratio': shoulder_hip_ratio,
            'head_shoulder_ratio': head_shoulder_ratio,
            'head_forward_ratio': head_forward_ratio,
            'visibility': avg_visibility,
            'torso_score': int(torso_score) if calibration_data['complete'] else 85,
            'head_score': int(head_score) if calibration_data['complete'] else 85,
            'neck_score': int(neck_score),
            'vis_score': int(visibility_score),
            'sym_score': int(symmetry_score)
        }

    except Exception as e:
        print(f"Error: {e}")
        return None


frame_count = 0
scores_history = []
CALIBRATION_FRAMES = 90  # 3 seconds at 30fps

while True:
    success, frame = camera.read()

    if not success:
        break

    frame_count += 1

    # Process frame
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = pose.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Check for recalibration (press 'r')
    key = cv2.waitKey(5) & 0xFF
    if key == ord('r'):
        calibration_data = {
            'shoulder_hip_ratio': [],
            'head_shoulder_ratio': [],
            'shoulder_width_ratio': [],
            'frames': 0,
            'complete': False
        }
        scores_history = []
        print("🔄 RECALIBRATING! Sit with good posture!")
    elif key == ord('q'):
        break

    if results.pose_landmarks:
        # Draw skeleton
        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing.DrawingSpec(
                color=(0, 255, 0),
                thickness=2,
                circle_radius=2
            ),
            connection_drawing_spec=mp_drawing.DrawingSpec(
                color=(255, 255, 255),
                thickness=2
            )
        )

        # Calculate posture
        metrics = calculate_distance_aware_posture(results.pose_landmarks.landmark)

        if metrics:
            # Handle calibration
            if not calibration_data['complete']:
                calibration_data['frames'] += 1

                if calibration_data['frames'] >= CALIBRATION_FRAMES:
                    calibration_data['complete'] = True
                    print("✅ Calibration complete!")
                    print(f"   Baseline shoulder-hip ratio: {np.median(calibration_data['shoulder_hip_ratio']):.2f}")
                    print(f"   Baseline head-shoulder ratio: {np.median(calibration_data['head_shoulder_ratio']):.2f}")

            score = metrics['score']

            # Smooth score
            scores_history.append(score)
            if len(scores_history) > 5:
                scores_history.pop(0)
            smoothed_score = int(sum(scores_history) / len(scores_history))

            # Determine color and status
            if smoothed_score >= 80:
                color = (0, 255, 0)  # Green
                status = "EXCELLENT"
            elif smoothed_score >= 60:
                color = (0, 255, 255)  # Yellow
                status = "GOOD"
            elif smoothed_score >= 40:
                color = (0, 165, 255)  # Orange
                status = "POOR"
            else:
                color = (0, 0, 255)  # Red
                status = "SLOUCHING"

            # Display
            if not calibration_data['complete']:
                # Calibration display
                remaining = CALIBRATION_FRAMES - calibration_data['frames']
                cv2.putText(
                    image,
                    f"CALIBRATING... {remaining} frames",
                    (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 0),
                    2
                )
                cv2.putText(
                    image,
                    "Sit with BEST posture!",
                    (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 0),
                    2
                )

                # Progress bar
                progress = int((calibration_data['frames'] / CALIBRATION_FRAMES) * 400)
                cv2.rectangle(image, (10, 100), (410, 120), (100, 100, 100), 2)
                cv2.rectangle(image, (10, 100), (10 + progress, 120), (0, 255, 255), -1)

            else:
                # Normal display
                cv2.putText(
                    image,
                    f"POSTURE: {smoothed_score}/100",
                    (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.3,
                    color,
                    3
                )

                cv2.putText(
                    image,
                    f"{status}",
                    (10, 95),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    color,
                    2
                )

                # Component scores
                y_pos = 140
                cv2.putText(image, f"Torso: {metrics['torso_score']}",
                            (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                y_pos += 25
                cv2.putText(image, f"Head: {metrics['head_score']}",
                            (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                y_pos += 25
                cv2.putText(image, f"Neck: {metrics['neck_score']}",
                            (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                # Instruction
                if smoothed_score >= 80:
                    instruction = "Perfect! Keep this posture!"
                elif smoothed_score >= 60:
                    instruction = "Good - minor improvements needed"
                else:
                    instruction = "SLOUCHING! Sit up, shoulders back!"

                cv2.putText(
                    image,
                    instruction,
                    (10, image.shape[0] - 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2
                )

                # Hints
                cv2.putText(
                    image,
                    "Press 'R' to recalibrate",
                    (10, image.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (150, 150, 150),
                    1
                )

    else:
        # No person
        cv2.putText(
            image,
            "NO PERSON DETECTED",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (0, 0, 255),
            3
        )

        # Reset calibration if person leaves
        if calibration_data['complete']:
            calibration_data = {
                'shoulder_hip_ratio': [],
                'head_shoulder_ratio': [],
                'shoulder_width_ratio': [],
                'frames': 0,
                'complete': False
            }

    # Frame counter
    cv2.putText(
        image,
        f"Frame: {frame_count}",
        (image.shape[1] - 150, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (200, 200, 200),
        1
    )

    # Display
    cv2.imshow('PRODUCTION POSTURE V4 - Q=quit, R=recalibrate', image)

camera.release()
cv2.destroyAllWindows()

print("\n" + "=" * 60)
print("SESSION COMPLETE")
print("=" * 60)
print("\nThis version:")
print("✅ Uses proportional measurements (distance-invariant)")
print("✅ Calibrates to YOUR body")
print("✅ Detects actual slouching")
print("✅ NOT affected by camera distance")
print("=" * 60 + "\n")