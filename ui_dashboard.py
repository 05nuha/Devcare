"""
Full Dashboard Window using CustomTkinter
Beautiful, modern UI for detailed stats
"""

import customtkinter as ctk
from datetime import datetime
import threading
import time


class DashboardWindow:
    def __init__(self, state_dict):
        """
        state_dict: Reference to the global state dictionary
        """
        self.state = state_dict

        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Create window
        self.root = ctk.CTk()
        self.root.title("DevCare Dashboard")
        self.root.geometry("600x700")

        # Build UI
        self.create_ui()

        # Start update loop
        self.update_ui()

    def create_ui(self):
        """Build the UI components"""

        # ===== HEADER =====
        header = ctk.CTkFrame(self.root)
        header.pack(fill="x", padx=20, pady=20)

        title = ctk.CTkLabel(
            header,
            text="🪑 DevCare",
            font=("Arial", 32, "bold")
        )
        title.pack()

        subtitle = ctk.CTkLabel(
            header,
            text="Your Posture & Productivity Monitor",
            font=("Arial", 14),
            text_color="gray"
        )
        subtitle.pack()

        # ===== POSTURE SECTION =====
        posture_frame = ctk.CTkFrame(self.root)
        posture_frame.pack(fill="x", padx=20, pady=10)

        posture_label = ctk.CTkLabel(
            posture_frame,
            text="Current Posture",
            font=("Arial", 18, "bold")
        )
        posture_label.pack(pady=10)

        self.posture_score = ctk.CTkLabel(
            posture_frame,
            text="--/100",
            font=("Arial", 48, "bold"),
            text_color="#4CAF50"
        )
        self.posture_score.pack(pady=10)

        self.posture_bar = ctk.CTkProgressBar(
            posture_frame,
            width=400,
            height=20
        )
        self.posture_bar.pack(pady=10)
        self.posture_bar.set(0)

        # ===== STATS GRID =====
        stats_frame = ctk.CTkFrame(self.root)
        stats_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Time stat
        time_card = self.create_stat_card(
            stats_frame,
            "⏱️ Coding Time",
            "-- min"
        )
        time_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Stress stat
        stress_card = self.create_stat_card(
            stats_frame,
            "😤 Stress Level",
            "Low"
        )
        stress_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Breaks stat
        breaks_card = self.create_stat_card(
            stats_frame,
            "☕ Breaks Taken",
            "0"
        )
        breaks_card.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Typing stat
        typing_card = self.create_stat_card(
            stats_frame,
            "⌨️ Typing Speed",
            "0 keys/min"
        )
        typing_card.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # Configure grid
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)

        # Store card labels for updating
        self.time_value = time_card.winfo_children()[1]
        self.stress_value = stress_card.winfo_children()[1]
        self.breaks_value = breaks_card.winfo_children()[1]
        self.typing_value = typing_card.winfo_children()[1]

        # ===== ACTION BUTTONS =====
        button_frame = ctk.CTkFrame(self.root)
        button_frame.pack(fill="x", padx=20, pady=20)

        take_break_btn = ctk.CTkButton(
            button_frame,
            text="Take Break",
            command=self.take_break,
            height=40,
            font=("Arial", 14)
        )
        take_break_btn.pack(side="left", expand=True, padx=5)

        reset_btn = ctk.CTkButton(
            button_frame,
            text="Reset Stats",
            command=self.reset_stats,
            height=40,
            font=("Arial", 14),
            fg_color="gray"
        )
        reset_btn.pack(side="left", expand=True, padx=5)

    def create_stat_card(self, parent, title, value):
        """Create a stat card"""
        card = ctk.CTkFrame(parent)

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 14)
        )
        title_label.pack(pady=(10, 5))

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 24, "bold")
        )
        value_label.pack(pady=(5, 10))

        return card

    def update_ui(self):
        """Update UI with current state (called every second)"""
        try:
            # Update posture
            posture = self.state.get('posture', 0)
            self.posture_score.configure(text=f"{posture}/100")
            self.posture_bar.set(posture / 100)

            # Change color based on posture
            if posture >= 80:
                color = "#4CAF50"  # Green
            elif posture >= 60:
                color = "#FFA726"  # Orange
            else:
                color = "#EF5350"  # Red
            self.posture_score.configure(text_color=color)

            # Update stats
            self.time_value.configure(text=self.state.get('time', '0 min'))
            self.stress_value.configure(text=self.state.get('stress', 'Low'))
            self.breaks_value.configure(text=str(self.state.get('breaks_taken', 0)))
            self.typing_value.configure(
                text=f"{self.state.get('typing_speed', 0)} keys/min"
            )

        except Exception as e:
            print(f"Error updating UI: {e}")

        # Schedule next update
        self.root.after(1000, self.update_ui)

    def take_break(self):
        """Record a break"""
        import requests
        try:
            requests.post('http://localhost:5000/break', timeout=1)
            print("✅ Break recorded!")
        except:
            print("❌ Could not record break")

    def reset_stats(self):
        """Reset statistics"""
        import requests
        try:
            requests.post('http://localhost:5000/reset', timeout=1)
            print("✅ Stats reset!")
        except:
            print("❌ Could not reset stats")

    def run(self):
        """Run the dashboard (blocking)"""
        self.root.mainloop()


# Test
if __name__ == "__main__":
    # Test state
    test_state = {
        'posture': 85,
        'time': '42 min',
        'stress': 'Low',
        'breaks_taken': 3,
        'typing_speed': 120
    }

    dashboard = DashboardWindow(test_state)
    dashboard.run()