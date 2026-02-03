# DevCare - Developer Health Monitoring System

**Winner of 1st Place - JetBrains "Help the Developer" Bounty Challenge**  
*Inter-University Hackathon, University of Birmingham Dubai | February 2026*

> Real-time health monitoring for developers, integrated directly into IntelliJ IDEA.

---

DevCare is an IntelliJ IDEA plugin that provides seamless health monitoring without disrupting your workflow:

- **🪑 Real-Time Posture Monitoring** - Computer vision-based tracking using MediaPipe
- **⌨️ Stress Detection** - Analyzes typing patterns to identify stress levels
- **☕ Smart Break Reminders** - Intelligent suggestions based on your work patterns
- **🎮 Gamification** - XP, levels, and achievements to build healthy habits
- **📊 Daily Analytics** - Track your health progress over time

All integrated directly inside your IDE - no context switching required.

---

## 🚀 Features

### Core Features
- Distance-invariant posture detection (works at any camera distance)
- Personal calibration for individual body types
- Real-time posture scoring (0-100)
- Typing velocity and stress level analysis
- Customizable break intervals
- Health statistics dashboard

### Gamification System
- XP and leveling system
- Achievement badges
- Posture streak tracking
- Daily/weekly summaries

### IDE Integration
- Seamless IntelliJ IDEA plugin
- Non-intrusive status bar widget
- Real-time notifications
- Works alongside your development workflow

---

## 🛠️ Tech Stack

**Backend:**
- Python 3.12
- Flask
- MediaPipe (Computer Vision)
- OpenCV
- NumPy

**Frontend:**
- HTML5
- CSS3 (Modern glassmorphism design)
- Vanilla JavaScript
- Real-time API polling

**Plugin:**
- Kotlin
- IntelliJ Platform SDK 2024.1
- JBCefBrowser for web content embedding

---

## 📦 Installation

### Prerequisites
```bash
- Python 3.12+
- IntelliJ IDEA 2024.1+
- Webcam (for posture detection)
```

### Backend Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/devcare.git
cd devcare

# Install Python dependencies
pip install -r requirements.txt

# Run the Flask backend
python devcareapp.py
```

The backend will start on `http://localhost:5000`

### Plugin Installation
```bash
# Build the plugin
./gradlew build

# Or install from IntelliJ:
# 1. File → Settings → Plugins
# 2. Click gear icon → Install Plugin from Disk
# 3. Select the built .jar file from build/distributions/
```

---

## 🎮 Usage

1. **Start the Flask backend:**
```bash
   python devcareapp.py
```

2. **Open IntelliJ IDEA**

3. **Access DevCare:**
   - View → Tool Windows → DevCare
   - Or click the DevCare icon in the status bar

4. **Start coding!**
   - Your posture is monitored in real-time
   - Receive break reminders
   - Track your health stats
   - Earn achievements

---

## 📸 Screenshots

### Main Dashboard
*Real-time health monitoring with modern UI*

### IntelliJ Integration
*Seamless plugin integration in the IDE*

### Posture Detection
*Live posture scoring with visual feedback*

---

## 🏗️ Project Structure
```
devcare/
├── backend/
│   ├── devcareapp.py           # Flask server
│   ├── posture_detector.py     # Posture detection module
│   ├── typing_analyzer.py      # Typing analysis module
│   ├── break_manager.py        # Break management
│   └── requirements.txt        # Python dependencies
│
├── frontend/
│   ├── templates/
│   │   └── index.html         # Main UI
│   └── static/
│       ├── css/style.css      # Styling
│       └── js/app.js          # Frontend logic
│
├── plugin/
│   └── src/main/kotlin/...   # IntelliJ plugin code
│
└── README.md
```

---

## 🎯 API Endpoints
```
GET  /api/status        # Get current health status
POST /api/break         # Record a break
POST /api/reset         # Reset statistics
GET  /api/history       # Get posture history
```

---

## 🤝 Contributing

We welcome contributions! Whether it's:
- 🐛 Bug fixes
- ✨ New features
- 📝 Documentation improvements
- 🎨 UI enhancements

Please feel free to open an issue or submit a pull request.

---

## 👥 Team

Built with ❤️ by:
- **Nuha Aburamadan** - Plugin Development & Integration
- **Samira Alsaqqa** - Backend Development & Computer Vision
- **Laila Elsayed** - Frontend Development & UI/UX


---



---

<p align="center">Made with 💻 and ☕ at the JetBrains Hackathon 2026</p>
