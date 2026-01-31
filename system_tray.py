"""
System Tray Application for DevCare
Shows icon in system tray with current status

NOTE: This is OPTIONAL and complex. Skip if short on time!
"""

import sys
from PIL import Image, ImageDraw
import io

try:
    import pystray
    from pystray import MenuItem as item

    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False
    print("⚠️ pystray not installed - system tray disabled")
    print("   Install with: pip install pystray")


def create_icon_image(posture_score):
    """
    Create a colored icon based on posture score
    Green = good, Yellow = ok, Red = bad
    """
    # Create a 64x64 image
    size = 64
    image = Image.new('RGB', (size, size), 'white')
    draw = ImageDraw.Draw(image)

    # Choose color based on score
    if posture_score >= 80:
        color = (0, 200, 0)  # Green
    elif posture_score >= 60:
        color = (255, 200, 0)  # Yellow
    else:
        color = (255, 0, 0)  # Red

    # Draw a circle
    margin = 8
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=color,
        outline='black',
        width=2
    )

    return image


class SystemTrayApp:
    def __init__(self, state_dict):
        """
        state_dict: Reference to the global state dictionary
        """
        self.state = state_dict
        self.icon = None

        if not HAS_TRAY:
            print("❌ System tray not available")
            return

        # Create initial icon
        image = create_icon_image(0)

        # Create menu
        menu = (
            item('DevCare', lambda: None),
            item('---', lambda: None),  # Separator
            item(
                lambda text: f'Posture: {self.state.get("posture", 0)}/100',
                lambda: None
            ),
            item(
                lambda text: f'Time: {self.state.get("time", "0 min")}',
                lambda: None
            ),
            item(
                lambda text: f'Stress: {self.state.get("stress", "Low")}',
                lambda: None
            ),
            item('---', lambda: None),
            item('Open Dashboard', self.open_dashboard),
            item('Take Break', self.take_break),
            item('---', lambda: None),
            item('Quit', self.quit_app)
        )

        # Create icon
        self.icon = pystray.Icon(
            'DevCare',
            image,
            'DevCare - Posture Monitor',
            menu
        )

    def update_icon(self):
        """Update icon based on current posture"""
        if self.icon:
            posture = self.state.get('posture', 0)
            image = create_icon_image(posture)
            self.icon.icon = image

    def open_dashboard(self):
        """Open the full dashboard window"""
        print("📊 Opening dashboard...")
        try:
            from ui_dashboard import DashboardWindow
            import threading

            def launch():
                dashboard = DashboardWindow(self.state)
                dashboard.run()

            threading.Thread(target=launch, daemon=True).start()
        except Exception as e:
            print(f"❌ Could not open dashboard: {e}")

    def take_break(self):
        """Record a break"""
        import requests
        try:
            requests.post('http://localhost:5000/break', timeout=1)
            print("✅ Break recorded!")
        except:
            print("❌ Could not record break")

    def quit_app(self):
        """Quit the application"""
        print("👋 Quitting DevCare...")
        if self.icon:
            self.icon.stop()
        sys.exit(0)

    def run(self):
        """Run the system tray (blocking)"""
        if self.icon:
            print("✅ System tray active")
            self.icon.run()
        else:
            print("❌ System tray not available")


# Test
if __name__ == "__main__":
    test_state = {
        'posture': 85,
        'time': '42 min',
        'stress': 'Low'
    }

    if HAS_TRAY:
        app = SystemTrayApp(test_state)
        app.run()
    else:
        print("Install pystray to use system tray: pip install pystray")