# --- posture_detector.py (clean, production-ready) ---

import cv2
import mediapipe as mp
import math
import time
import numpy as np
import threading

class PostureDetector:
    def __init__(self):
        print("📷 Initializing Posture Detector...")

        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils

        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=1
        )

        self.current_score = 0
        self.running = False
        self.camera = None
        self.last_detection_time = 0

        self.calibration_data = {
            'shoulder_hip_ratio': [],
            'head_shoulder_ratio': [],
            'frames': 0,
            'complete': False,
            'baseline_shoulder_hip': None,
            'baseline_head_shoulder': None
        }

        self.CALIBRATION_FRAMES = 90
        self.score_history = []
        self.max_history = 5

        print("✅ Posture Detector initialized")

    def calculate_posture_score(self, landmarks):
        try:
            nose = landmarks[self.mp_pose.PoseLandmark.NOSE.value]
            left_ear = landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value]
            right_ear = landmarks[self.mp_pose.PoseLandmark.RIGHT_EAR.value]

            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]
            right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value]

            shoulder_width = math.sqrt(
                (left_shoulder.x - right_shoulder.x)**2 +
                (left_shoulder.y - right_shoulder.y)**2
            )

            if shoulder_width < 0.05:
                return 0

            shoulder_x = (left_shoulder.x + right_shoulder.x) / 2
            shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
            hip_y = (left_hip.y + right_hip.y) / 2
            ear_x = (left_ear.x + right_ear.x) / 2
            ear_y = (left_ear.y + right_ear.y) / 2

            shoulder_hip_vertical = abs(hip_y - shoulder_y)
            shoulder_hip_ratio = shoulder_hip_vertical / shoulder_width

            if not self.calibration_data['complete']:
                self.calibration_data['shoulder_hip_ratio'].append(shoulder_hip_ratio)
                torso_score = 85
            else:
                baseline = self.calibration_data['baseline_shoulder_hip']
                deviation = (baseline - shoulder_hip_ratio) / baseline

                if deviation < 0:
                    torso_score = 100
                elif deviation < 0.15:
                    torso_score = 100 - deviation * 300
                elif deviation < 0.30:
                    torso_score = 55 - (deviation - 0.15) * 200
                else:
                    torso_score = max(0, 25 - (deviation - 0.30) * 100)

            head_shoulder_vertical = abs(shoulder_y - ear_y)
            head_shoulder_ratio = head_shoulder_vertical / shoulder_width

            if not self.calibration_data['complete']:
                self.calibration_data['head_shoulder_ratio'].append(head_shoulder_ratio)
                head_score = 85
            else:
                baseline = self.calibration_data['baseline_head_shoulder']
                deviation = (baseline - head_shoulder_ratio) / baseline

                if deviation < 0:
                    head_score = 100
                elif deviation < 0.15:
                    head_score = 100 - deviation * 400
                elif deviation < 0.30:
                    head_score = 40 - (deviation - 0.15) * 200
                else:
                    head_score = max(0, 10 - (deviation - 0.30) * 50)

            head_forward = abs(ear_x - shoulder_x)
            head_forward_ratio = head_forward / shoulder_width

            if head_forward_ratio < 0.15:
                neck_score = 100
            elif head_forward_ratio < 0.30:
                neck_score = 100 - (head_forward_ratio - 0.15) * 500
            else:
                neck_score = max(20, 25 - (head_forward_ratio - 0.30) * 100)

            shoulder_tilt = abs(left_shoulder.y - right_shoulder.y)
            shoulder_tilt_ratio = shoulder_tilt / shoulder_width

            if shoulder_tilt_ratio < 0.10:
                symmetry_score = 100
            elif shoulder_tilt_ratio < 0.20:
                symmetry_score = 100 - (shoulder_tilt_ratio - 0.10) * 500
            else:
                symmetry_score = max(50, 50 - (shoulder_tilt_ratio - 0.20) * 200)

            avg_visibility = (nose.visibility + left_ear.visibility + right_ear.visibility) / 3

            if avg_visibility > 0.9:
                visibility_score = 100
            elif avg_visibility > 0.7:
                visibility_score = 70 + (avg_visibility - 0.7) * 150
            else:
                visibility_score = max(30, avg_visibility * 100)

            if not self.calibration_data['complete']:
                final_score = 85
            else:
                final_score = (
                    torso_score * 0.35 +
                    head_score * 0.25 +
                    neck_score * 0.20 +
                    visibility_score * 0.12 +
                    symmetry_score * 0.08
                )

            return int(max(0, min(100, final_score)))

        except Exception as e:
            print(f"⚠️ Error calculating posture: {e}")
            return 50

    def smooth_score(self, new_score):
        self.score_history.append(new_score)
        if len(self.score_history) > self.max_history:
            self.score_history.pop(0)
        return int(sum(self.score_history) / len(self.score_history))

    def run(self):
        self.running = True
        print("📹 Starting webcam...")

        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            self.camera = cv2.VideoCapture(1)

        if not self.camera.isOpened():
            print("❌ Could not open webcam")
            self.running = False
            return

        print("✅ Webcam opened")
        print("⚙️ Calibration: Sit with GOOD posture for 3 seconds")

        while self.running:
            success, frame = self.camera.read()
            if not success:
                time.sleep(0.1)
                continue

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = self.pose.process(image)

            if results.pose_landmarks:
                raw_score = self.calculate_posture_score(results.pose_landmarks.landmark)

                if not self.calibration_data['complete']:
                    self.calibration_data['frames'] += 1

                    if self.calibration_data['frames'] >= self.CALIBRATION_FRAMES:
                        self.calibration_data['baseline_shoulder_hip'] = np.median(
                            self.calibration_data['shoulder_hip_ratio']
                        )
                        self.calibration_data['baseline_head_shoulder'] = np.median(
                            self.calibration_data['head_shoulder_ratio']
                        )
                        self.calibration_data['complete'] = True
                        print("✅ Calibration complete!")

                self.current_score = self.smooth_score(raw_score)
                self.last_detection_time = time.time()

            else:
                self.current_score = 0

            time.sleep(0.033)

        if self.camera:
            self.camera.release()

    def get_score(self):
        if time.time() - self.last_detection_time > 5:
            return 0
        if not self.calibration_data['complete']:
            return 0
        return self.current_score

    def get_status(self):
        score = self.get_score()

        if not self.calibration_data['complete']:
            status = "Calibrating..."
            color = "yellow"
        elif score == 0:
            status = "No person detected"
            color = "gray"
        elif score >= 80:
            status = "Excellent posture"
            color = "green"
        elif score >= 60:
            status = "Good posture"
            color = "yellow"
        elif score >= 40:
            status = "Poor posture"
            color = "orange"
        else:
            status = "Bad posture"
            color = "red"

        return {
            'score': score,
            'status': status,
            'color': color,
            'running': self.running,
            'calibrated': self.calibration_data['complete'],
            'person_detected': score > 0 or not self.calibration_data['complete']
        }

    def reset_calibration(self):
        self.calibration_data = {
            'shoulder_hip_ratio': [],
            'head_shoulder_ratio': [],
            'frames': 0,
            'complete': False,
            'baseline_shoulder_hip': None,
            'baseline_head_shoulder': None
        }
        self.score_history = []
        print("🔄 Calibration reset")

    def stop(self):
        print("⏹️ Stopping posture detector...")
        self.running = False
        if self.camera:
            self.camera.release()
        if self.pose:
            self.pose.close()


if __name__ == "__main__":
    detector = PostureDetector()
    thread = threading.Thread(target=detector.run, daemon=True)
    thread.start()

    try:
        while True:
            print(detector.get_status())
            time.sleep(1)
    except KeyboardInterrupt:
        detector.stop()