// DevCare Frontend Application
class DevCareApp {
    constructor() {
        this.updateInterval = 1000; // Update every second
        this.init();
    }

    init() {
        console.log('DevCare App initializing...');

        // Get DOM elements
        this.elements = {
            postureScore: document.getElementById('postureScore'),
            postureBar: document.getElementById('postureBar'),
            postureStatus: document.getElementById('postureStatus'),
            codingTime: document.getElementById('codingTime'),
            stressLevel: document.getElementById('stressLevel'),
            breaksTaken: document.getElementById('breaksTaken'),
            typingSpeed: document.getElementById('typingSpeed'),
            statusIndicator: document.getElementById('statusIndicator'),
            connectionStatus: document.getElementById('connectionStatus'),
            lastUpdate: document.getElementById('lastUpdate'),
            takeBreakBtn: document.getElementById('takeBreakBtn'),
            resetStatsBtn: document.getElementById('resetStatsBtn')
        };

        // Setup event listeners
        this.setupEventListeners();

        // Start polling
        this.startPolling();
    }

    setupEventListeners() {
        this.elements.takeBreakBtn.addEventListener('click', () => this.takeBreak());
        this.elements.resetStatsBtn.addEventListener('click', () => this.resetStats());
    }

    async fetchStatus() {
        try {
            const response = await fetch('/api/status');

            if (!response.ok) {
                throw new Error('Server error');
            }

            const data = await response.json();
            this.updateUI(data);
            this.setConnectionStatus(true);

        } catch (error) {
            console.error('Error fetching status:', error);
            this.setConnectionStatus(false);
        }
    }

    updateUI(data) {
        // Update posture score
        const posture = data.posture || 0;
        this.elements.postureScore.textContent = `${posture}/100`;

        // Update progress bar
        this.elements.postureBar.style.width = `${posture}%`;

        // Set color based on score
        this.elements.postureBar.className = 'posture-bar';
        if (posture >= 80) {
            this.elements.postureBar.classList.add('excellent');
            this.elements.postureStatus.textContent = 'Excellent Posture!';
        } else if (posture >= 60) {
            this.elements.postureBar.classList.add('good');
            this.elements.postureStatus.textContent = 'Good Posture';
        } else if (posture > 0) {
            this.elements.postureBar.classList.add('poor');
            this.elements.postureStatus.textContent = '⚠Poor Posture - Sit up straight!';
        } else {
            this.elements.postureStatus.textContent = 'Calibrating...';
        }

        // Update other stats
        this.elements.codingTime.textContent = data.time || '0 min';
        this.elements.stressLevel.textContent = data.stress || 'Low';
        this.elements.breaksTaken.textContent = data.breaks_taken || 0;
        this.elements.typingSpeed.textContent = `${data.typing_speed || 0} keys/min`;

        // Update last update time
        const now = new Date();
        this.elements.lastUpdate.textContent = now.toLocaleTimeString();
    }

    setConnectionStatus(connected) {
        this.elements.statusIndicator.className = 'status-indicator';

        if (connected) {
            this.elements.statusIndicator.classList.add('connected');
            this.elements.connectionStatus.textContent = 'Connected';
        } else {
            this.elements.statusIndicator.classList.add('disconnected');
            this.elements.connectionStatus.textContent = 'Disconnected';
        }
    }

    async takeBreak() {
        try {
            const response = await fetch('/api/break', {
                method: 'POST'
            });

            const result = await response.json();

            if (result.success) {
                console.log('Break recorded!');
                this.showNotification('Break recorded!');
                this.fetchStatus();
            }
        } catch (error) {
            console.error('Error recording break:', error);
        }
    }

    async resetStats() {
        if (!confirm('Reset all statistics?')) {
            return;
        }

        try {
            const response = await fetch('/api/reset', {
                method: 'POST'
            });

            const result = await response.json();

            if (result.success) {
                console.log('Stats reset!');
                this.showNotification('Stats reset!');
                this.fetchStatus();
            }
        } catch (error) {
            console.error('Error resetting stats:', error);
        }
    }

    showNotification(message) {
        const notification = document.createElement('div');
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            background: #4CAF50;
            color: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    startPolling() {
        // Initial fetch
        this.fetchStatus();

        // Poll every second
        setInterval(() => {
            this.fetchStatus();
        }, this.updateInterval);

        console.log('Polling started');
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.devCareApp = new DevCareApp();
});
```

---

## **NOW REFRESH YOUR BROWSER!**
```
http://localhost:5000
```

**You should see the beautiful web app!**

---

## **VERIFY YOUR FILE STRUCTURE:**
```
python-app/
├── devcare_app.py          ✅ (running)
│
├── templates/
│   └── index.html          ✅ (just created)
│
└── static/
    ├── css/
    │   └── style.css       ✅ (just created)
    └── js/
        └── app.js          ✅ (just created)