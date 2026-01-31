import time
from datetime import datetime, timedelta


class BreakManager:
    def __init__(self):
        """Initialize break manager"""
        self.work_start = time.time()
        self.last_break = time.time()
        self.breaks_taken = 0
        self.break_interval = 45  # Suggest break every 45 minutes

        # History tracking
        self.break_history = []

        print("☕ Break Manager initialized")

    def get_time_working(self):
        """
        Get total minutes worked since start
        Returns: int - minutes
        """
        elapsed = time.time() - self.work_start
        return int(elapsed / 60)

    def get_time_since_break(self):
        """
        Get minutes since last break
        Returns: int - minutes
        """
        elapsed = time.time() - self.last_break
        return int(elapsed / 60)

    def should_suggest_break(self):
        """
        Check if it's time to suggest a break
        Returns: bool - True if break should be suggested
        """
        minutes_since_break = self.get_time_since_break()
        return minutes_since_break >= self.break_interval

    def take_break(self):
        """
        Record that a break was taken
        """
        current_time = time.time()

        # Calculate how long since last break
        duration_before_break = current_time - self.last_break

        # Record break
        self.break_history.append({
            'timestamp': current_time,
            'duration_before': duration_before_break / 60,  # in minutes
            'work_minutes': self.get_time_working()
        })

        # Update counters
        self.last_break = current_time
        self.breaks_taken += 1

        print(f"☕ Break #{self.breaks_taken} recorded")

    def get_break_suggestion(self):
        """
        Get a personalized break suggestion
        Returns: str - suggestion message
        """
        minutes = self.get_time_since_break()

        if minutes < 30:
            return "Keep coding! Break coming soon."
        elif minutes < 45:
            return "Consider a short break soon."
        elif minutes < 60:
            return "Time for a 5-minute break!"
        elif minutes < 90:
            return "You've been working a while. Take a 10-minute break."
        else:
            return "Long session! Take a 15-minute break and stretch."

    def get_status(self):
        """
        Get current break status
        Returns: dict with all break info
        """
        return {
            'time_working': self.get_time_working(),
            'time_since_break': self.get_time_since_break(),
            'breaks_taken': self.breaks_taken,
            'should_break': self.should_suggest_break(),
            'suggestion': self.get_break_suggestion()
        }

    def get_statistics(self):
        """
        Get statistics about break patterns
        Returns: dict with statistics
        """
        if len(self.break_history) == 0:
            return {
                'total_breaks': 0,
                'average_interval': 0,
                'longest_session': 0,
                'shortest_session': 0
            }

        # Calculate statistics
        intervals = [b['duration_before'] for b in self.break_history]

        return {
            'total_breaks': len(self.break_history),
            'average_interval': round(sum(intervals) / len(intervals), 1),
            'longest_session': round(max(intervals), 1),
            'shortest_session': round(min(intervals), 1)
        }

    def set_break_interval(self, minutes):
        """
        Set custom break interval
        Args:
            minutes: int - minutes between breaks
        """
        self.break_interval = minutes
        print(f"⏰ Break interval set to {minutes} minutes")

    def reset(self):
        """Reset all counters and history"""
        self.work_start = time.time()
        self.last_break = time.time()
        self.breaks_taken = 0
        self.break_history = []
        print("🔄 Break stats reset")

    def get_formatted_time(self):
        """
        Get formatted time string for display
        Returns: str - formatted time
        """
        minutes = self.get_time_working()

        if minutes < 60:
            return f"{minutes} min"
        else:
            hours = minutes // 60
            mins = minutes % 60
            return f"{hours}h {mins}m"


# ==========================================
# TEST CODE (Run this file directly to test)
# ==========================================

if __name__ == "__main__":
    print("=" * 60)
    print("BREAK MANAGER - TEST MODE")
    print("=" * 60)
    print("\nThis will simulate a coding session with breaks.")
    print("In real use, time passes naturally.\n")

    manager = BreakManager()

    # For testing, set short interval
    print("⏰ Setting test interval to 2 minutes (normally 45)")
    manager.set_break_interval(2)

    # Simulate time passing by manually setting timestamps
    print("\n--- Simulating 44 minutes of work ---")
    manager.last_break = time.time() - (44 * 60)  # 44 minutes ago

    # Check status
    status = manager.get_status()

    print("\n📊 Current Status:")
    print(f"   Time working: {status['time_working']} min")
    print(f"   Since last break: {status['time_since_break']} min")
    print(f"   Breaks taken: {status['breaks_taken']}")
    print(f"   Should break: {status['should_break']}")
    print(f"   Suggestion: {status['suggestion']}")

    if status['should_break']:
        print("\n⚠️  BREAK RECOMMENDED!")

    print("\n--- Recording a break ---")
    manager.take_break()

    # Check status again
    status = manager.get_status()
    print("\n📊 After Break:")
    print(f"   Since last break: {status['time_since_break']} min")
    print(f"   Breaks taken: {status['breaks_taken']}")
    print(f"   Should break: {status['should_break']}")

    print("\n--- Simulating another 50 minutes ---")
    manager.last_break = time.time() - (50 * 60)
    manager.take_break()

    # Show statistics
    stats = manager.get_statistics()
    print("\n📈 Session Statistics:")
    print(f"   Total breaks: {stats['total_breaks']}")
    print(f"   Average interval: {stats['average_interval']} min")
    print(f"   Longest session: {stats['longest_session']} min")
    print(f"   Shortest session: {stats['shortest_session']} min")

    print("\n✅ Break Manager test complete!\n")