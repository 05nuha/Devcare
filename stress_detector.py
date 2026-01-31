import time
from collections import deque


class StressDetector:
    def __init__(self):
        """Initialize stress detector"""
        self.stress_events = deque(maxlen=100)  # Keep last 100 events
        self.current_stress_level = 'Low'

        print("😤 Stress Detector initialized")

    def analyze_patterns(self, typing_stats, posture_score=None):
        """
        Analyze stress patterns from multiple sources

        Args:
            typing_stats: dict - from TypingAnalyzer.get_stats()
            posture_score: int - optional posture score (0-100)

        Returns:
            str - stress level: 'Low', 'Medium', 'High'
        """
        stress_indicators = []

        # Check typing patterns
        if typing_stats['typing_speed'] > 400:
            stress_indicators.append('very_fast_typing')

        if typing_stats['backspace_ratio'] > 0.3:
            stress_indicators.append('excessive_corrections')

        if typing_stats['stress_level'] == 'High':
            stress_indicators.append('high_typing_stress')

        # Check posture if available
        if posture_score is not None:
            if posture_score < 50:
                stress_indicators.append('poor_posture')

        # Determine overall stress level
        if len(stress_indicators) >= 3:
            level = 'High'
        elif len(stress_indicators) >= 1:
            level = 'Medium'
        else:
            level = 'Low'

        # Record event
        self.stress_events.append({
            'timestamp': time.time(),
            'level': level,
            'indicators': stress_indicators
        })

        self.current_stress_level = level
        return level

    def get_stress_trend(self):
        """
        Get stress trend over recent history
        Returns: str - 'increasing', 'decreasing', 'stable'
        """
        if len(self.stress_events) < 5:
            return 'stable'

        # Look at last 5 events
        recent = list(self.stress_events)[-5:]

        stress_values = {
            'Low': 1,
            'Medium': 2,
            'High': 3
        }

        values = [stress_values[e['level']] for e in recent]

        # Simple trend detection
        first_half = sum(values[:3]) / 3
        second_half = sum(values[2:]) / 3

        if second_half > first_half + 0.5:
            return 'increasing'
        elif second_half < first_half - 0.5:
            return 'decreasing'
        else:
            return 'stable'

    def get_recommendation(self):
        """
        Get personalized recommendation based on stress
        Returns: str - recommendation message
        """
        level = self.current_stress_level
        trend = self.get_stress_trend()

        if level == 'High':
            if trend == 'increasing':
                return "High stress detected and increasing. Take a break NOW!"
            else:
                return "High stress detected. Step away for 5 minutes."

        elif level == 'Medium':
            if trend == 'increasing':
                return "Stress is building up. Take deep breaths."
            else:
                return "Moderate stress. Consider a short break soon."

        else:  # Low
            return "Stress levels are healthy. Keep up the good work!"

    def reset(self):
        """Reset stress tracking"""
        self.stress_events.clear()
        self.current_stress_level = 'Low'
        print("🔄 Stress tracking reset")


# ==========================================
# TEST CODE
# ==========================================

if __name__ == "__main__":
    print("=" * 60)
    print("STRESS DETECTOR - TEST MODE")
    print("=" * 60)

    detector = StressDetector()

    # Simulate different stress patterns
    print("\n--- Test 1: Low Stress ---")
    test_stats = {
        'typing_speed': 80,
        'backspace_ratio': 0.1,
        'stress_level': 'Low'
    }
    level = detector.analyze_patterns(test_stats, posture_score=85)
    print(f"Stress Level: {level}")
    print(f"Recommendation: {detector.get_recommendation()}")

    print("\n--- Test 2: Medium Stress ---")
    test_stats = {
        'typing_speed': 300,
        'backspace_ratio': 0.2,
        'stress_level': 'Medium'
    }
    level = detector.analyze_patterns(test_stats, posture_score=60)
    print(f"Stress Level: {level}")
    print(f"Recommendation: {detector.get_recommendation()}")

    print("\n--- Test 3: High Stress ---")
    test_stats = {
        'typing_speed': 450,
        'backspace_ratio': 0.35,
        'stress_level': 'High'
    }
    level = detector.analyze_patterns(test_stats, posture_score=40)
    print(f"Stress Level: {level}")
    print(f"Trend: {detector.get_stress_trend()}")
    print(f"Recommendation: {detector.get_recommendation()}")

    print("\n✅ Stress Detector test complete!\n")