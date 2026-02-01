"""
DevCare Web Application
Flask server that serves HTML frontend and provides API
"""

from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS
import threading
import time
import sys
import os

# Try to import other modules
print("=" * 60)
print("DEVCARE - Starting Up")
print("=" * 60)

# Import Person 2's code
try:
    from posture_detector import PostureDetector
    HAS_POSTURE = True
    print("✅ Posture Detection: LOADED")
except ImportError as e:
    HAS_POSTURE = False
    print(f"❌ Posture Detection: NOT FOUND ({e})")

# Import Person 3's code
try:
    from typing_analyzer import TypingAnalyzer
    HAS_TYPING = True
    print("✅ Typing Analyzer: LOADED")
except ImportError as e:
    HAS_TYPING = False
    print(f"❌ Typing Analyzer: NOT FOUND ({e})")

try:
    from break_manager import BreakManager
    HAS_BREAKS = True
    print("✅ Break Manager: LOADED")
except ImportError as e:
    HAS_BREAKS = False
    print(f"❌ Break Manager: NOT FOUND ({e})")

print("=" * 60)

# Initialize Flask
app = Flask(__name__,
            static_folder='static',
            template_folder='templates')
CORS(app)

# Global state dictionary
state = {
    'posture': 0,
    'time': '0 min',
    'stress': 'Low',
    'breaks_taken': 0,
    'should_break': False,
    'typing_speed': 0,
    'status': 'Starting...'
}

# Initialize components
posture_detector = None
typing_analyzer = None
break_manager = None

def initialize_components():
    """Initialize all monitoring components"""
    global posture_detector, typing_analyzer, break_manager

    if HAS_POSTURE:
        print("Initializing Posture Detector...")
        posture_detector = PostureDetector()
        threading.Thread(target=posture_detector.run, daemon=True).start()
        print("✅ Posture detector running")

    if HAS_TYPING:
        print("Initializing Typing Analyzer...")
        typing_analyzer = TypingAnalyzer()
        threading.Thread(target=typing_analyzer.run, daemon=True).start()
        print("✅ Typing analyzer running")

    if HAS_BREAKS:
        print("Initializing Break Manager...")
        break_manager = BreakManager()
        print("✅ Break manager ready")

def update_state_loop():
    """Background thread that updates state from all components"""
    print("Starting state update loop...")

    while True:
        try:
            # Update posture
            if HAS_POSTURE and posture_detector:
                state['posture'] = posture_detector.get_score()

            # Update typing & stress
            if HAS_TYPING and typing_analyzer:
                state['stress'] = typing_analyzer.get_stress_level()
                state['typing_speed'] = typing_analyzer.get_typing_speed()

            # Update breaks
            if HAS_BREAKS and break_manager:
                break_status = break_manager.get_status()
                state['time'] = f"{break_status['time_working']} min"
                state['breaks_taken'] = break_status['breaks_taken']
                state['should_break'] = break_status['should_break']

            # Update overall status
            if state['posture'] > 0:
                state['status'] = 'Running'
            else:
                state['status'] = 'Waiting for webcam...'

        except Exception as e:
            print(f"Error updating state: {e}")

        time.sleep(1)

# ============================================
# WEB ROUTES (Serve HTML pages)
# ============================================

@app.route('/')
def index():
    """Serve the main web app"""
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS)"""
    return send_from_directory('static', path)

# ============================================
# HTTP API ENDPOINTS
# ============================================

@app.route('/api/status', methods=['GET'])
def get_status():
    """API endpoint for getting current status"""

    posture_score = state.get('posture', 0)
    typing_speed = state.get('typing_speed', 0)
    breaks_taken = state.get('breaks_taken', 0)
    should_break = state.get('should_break', False)
    session_time = state.get('time', '0 min')
    stress_level = state.get('stress', 'Low')
    overall_status = state.get('status', 'Starting...')

    response = {
        "status": overall_status,
        "posture": {
            "score": posture_score,
            "status": "Good posture" if posture_score >= 70 else "Needs improvement",
            "color": "green" if posture_score >= 70 else "orange"
        },
        "typing": {
            "speed": typing_speed
        },
        "breaks": {
            "taken": breaks_taken,
            "should_break": should_break,
            "time": session_time
        },
        "stress": stress_level
    }

    return jsonify(response)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'components': {
            'posture': HAS_POSTURE,
            'typing': HAS_TYPING,
            'breaks': HAS_BREAKS
        }
    })

@app.route('/api/break', methods=['POST'])
def record_break():
    """Record a break taken"""
    if HAS_BREAKS and break_manager:
        break_manager.take_break()
        return jsonify({'success': True, 'message': 'Break recorded'})
    return jsonify({'success': False, 'message': 'Break manager not available'})

@app.route('/api/reset', methods=['POST'])
def reset_stats():
    """Reset all statistics"""
    if HAS_BREAKS and break_manager:
        break_manager.reset()
    return jsonify({'success': True, 'message': 'Stats reset'})

# ============================================
# STARTUP
# ============================================

def print_startup_banner():
    """Print nice startup message"""
    print("\n" + "=" * 60)
    print("  ____             ____                ")
    print(" |  _ \\  _____   _/ ___|__ _ _ __ ___  ")
    print(" | | | |/ _ \\ \\ / / |   / _` | '__/ _ \\ ")
    print(" | |_| |  __/\\ V /| |__| (_| | | |  __/ ")
    print(" |____/ \\___| \\_/  \\____\\__,_|_|  \\___| ")
    print("                                        ")
    print("=" * 60)
    print("\n🚀 Starting DevCare Web Application...")
    print("\n📊 Component Status:")
    print(f"   Posture Detection: {'✅ ACTIVE' if HAS_POSTURE else '❌ MISSING'}")
    print(f"   Typing Analysis:   {'✅ ACTIVE' if HAS_TYPING else '❌ MISSING'}")
    print(f"   Break Management:  {'✅ ACTIVE' if HAS_BREAKS else '❌ MISSING'}")
    print("\n🌐 Web App: http://localhost:5000")
    print("📡 API: http://localhost:5000/api/status")
    print("\n" + "=" * 60)
    print("Open your browser and go to: http://localhost:5000")
    print("Press Ctrl+C to stop\n")

if __name__ == '__main__':
    # Print banner
    print_startup_banner()

    # Create templates and static directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)

    # Initialize all components
    initialize_components()

    # Start background state updater
    threading.Thread(target=update_state_loop, daemon=True).start()

    # Give components 2 seconds to initialize
    time.sleep(2)

    # Start Flask server
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down DevCare...")
        print("Goodbye!\n")
        sys.exit(0)