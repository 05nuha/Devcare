from pynput import keyboard
import time
import threading


class TypingAnalyzer:
    def __init__(self):
        """Initialize typing analyzer"""
        self.keystrokes = 0
        self.backspaces = 0
        self.start_time = time.time()
        self.last_key_time = time.time()
        self.running = False
        self.listener = None

        # Tracking for patterns
        self.keys_last_minute = []
        self.backspaces_last_minute = []

        print("📝 Typing Analyzer initialized")

    def on_press(self, key):
        """Called when any key is pressed"""
        try:
            current_time = time.time()

            # Count keystroke
            self.keystrokes += 1
            self.last_key_time = current_time

            # Track for rolling average
            self.keys_last_minute.append(current_time)

            # Clean old entries (keep only last 60 seconds)
            cutoff = current_time - 60
            self.keys_last_minute = [t for t in self.keys_last_minute if t > cutoff]

            # Check if it's a backspace
            if key == keyboard.Key.backspace:
                self.backspaces += 1
                self.backspaces_last_minute.append(current_time)
                # Clean old backspaces
                self.backspaces_last_minute = [t for t in self.backspaces_last_minute if t > cutoff]

        except Exception as e:
            # Some keys might cause errors, just ignore
            pass

    def on_release(self, key):
        """Called when key is released (not used currently)"""
        pass

    def run(self):
        """Start listening to keyboard (runs in background)"""
        self.running = True
        print("⌨️  Keyboard listener starting...")

        # Start keyboard listener
        with keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release
        ) as listener:
            self.listener = listener
            listener.join()

    def get_typing_speed(self):
        """
        Get current typing speed in keys per minute
        Returns: int - keys per minute
        """
        current_time = time.time()

        # Count keys in last 60 seconds
        cutoff = current_time - 60
        recent_keys = [t for t in self.keys_last_minute if t > cutoff]

        # If less than 60 seconds of data, calculate proportionally
        elapsed = min(60, current_time - self.start_time)
        if elapsed < 5:  # Need at least 5 seconds of data
            return 0

        keys_per_minute = int((len(recent_keys) / elapsed) * 60)
        return keys_per_minute

    def get_backspace_ratio(self):
        """
        Get ratio of backspaces to total keystrokes
        Returns: float - ratio between 0 and 1
        """
        if self.keystrokes == 0:
            return 0.0

        return self.backspaces / self.keystrokes

    def get_stress_level(self):
        """
        Detect stress level based on typing patterns
        Returns: str - 'Low', 'Medium', or 'High'
        """
        if self.keystrokes < 10:  # Not enough data yet
            return "Low"

        speed = self.get_typing_speed()
        backspace_ratio = self.get_backspace_ratio()

        # Detect stress patterns
        # High stress: Very fast typing OR lots of backspaces
        if backspace_ratio > 0.3 or speed > 400:
            return "High"

        # Medium stress: Moderately fast with some corrections
        elif backspace_ratio > 0.15 or speed > 250:
            return "Medium"

        # Low stress: Normal typing patterns
        else:
            return "Low"

    def get_time_since_last_key(self):
        """
        Get seconds since last keystroke
        Returns: float - seconds
        """
        return time.time() - self.last_key_time

    def is_actively_typing(self):
        """
        Check if user is currently typing
        Returns: bool - True if typed in last 5 seconds
        """
        return self.get_time_since_last_key() < 5

    def get_stats(self):
        """
        Get all typing statistics
        Returns: dict with all stats
        """
        return {
            'total_keystrokes': self.keystrokes,
            'total_backspaces': self.backspaces,
            'typing_speed': self.get_typing_speed(),
            'backspace_ratio': round(self.get_backspace_ratio(), 3),
            'stress_level': self.get_stress_level(),
            'actively_typing': self.is_actively_typing(),
            'time_since_last_key': round(self.get_time_since_last_key(), 1)
        }

    def reset(self):
        """Reset all counters"""
        self.keystrokes = 0
        self.backspaces = 0
        self.start_time = time.time()
        self.keys_last_minute = []
        self.backspaces_last_minute = []
        print("🔄 Typing stats reset")

    def stop(self):
        """Stop the keyboard listener"""
        self.running = False
        if self.listener:
            self.listener.stop()
        print("⏹️  Typing analyzer stopped")


# ==========================================
# TEST CODE (Run this file directly to test)
# ==========================================

if __name__ == "__main__":
    print("=" * 60)
    print("TYPING ANALYZER - TEST MODE")
    print("=" * 60)
    print("\nType something! The analyzer will track your typing.")
    print("Press Ctrl+C to stop\n")

    analyzer = TypingAnalyzer()

    # Start in background thread
    thread = threading.Thread(target=analyzer.run, daemon=True)
    thread.start()

    try:
        while True:
            # Print stats every 2 seconds
            time.sleep(2)

            stats = analyzer.get_stats()

            print("\n" + "=" * 60)
            print(f"Typing Speed:     {stats['typing_speed']} keys/min")
            print(f"Total Keystrokes: {stats['total_keystrokes']}")
            print(f"Backspaces:       {stats['total_backspaces']} ({stats['backspace_ratio']:.1%})")
            print(f"Stress Level:     {stats['stress_level']}")
            print(f"Active:           {'Yes' if stats['actively_typing'] else 'No'}")

            # Show stress indicator
            if stats['stress_level'] == 'High':
                print("⚠️  HIGH STRESS DETECTED!")
            elif stats['stress_level'] == 'Medium':
                print("⚠️  Moderate stress")
            else:
                print("✅ Low stress")

    except KeyboardInterrupt:
        print("\n\n👋 Stopping typing analyzer...")
        analyzer.stop()
        print("Goodbye!\n")