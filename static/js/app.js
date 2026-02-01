// DevCare Frontend Application
class DevCareApp {
    constructor() {
        this.updateInterval = 1000; // Update every second
        this.backendUrl = "http://127.0.0.1:5000"; // Central backend URL
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

        this.setupEventListeners();
        this.startPolling();
    }

    setupEventListeners() {
        this.elements.takeBreakBtn.addEventListener('click', () => this.takeBreak());
        this.elements.resetStatsBtn.addEventListener('click', () => this.resetStats());
    }

    async fetchStatus() {
        try {
            const response = await fetch(`${this.backendUrl}/api/status`);

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
        // ---- POSTURE ----
        const postureScore = data.posture?.score ?? 0;

        this.elements.postureScore.textContent = `${postureScore}/100`;
        this.elements.postureBar.style.width = `${postureScore}%`;

        this.elements.postureBar.className = 'posture-bar';

        if (postureScore >= 80) {
            this.elements.postureBar.classList.add('excellent');
            this.elements.postureStatus.textContent = data.posture.status || 'Excellent posture';
        } else if (postureScore >= 60) {
            this.elements.postureBar.classList.add('good');
            this.elements.postureStatus.textContent = data.posture.status || 'Good posture';
        } else if (postureScore > 0) {
            this.elements.postureBar.classList.add('poor');
            this.elements.postureStatus.textContent =
                data.posture.status || '⚠ Poor posture — sit up straight!';
        } else {
            this.elements.postureStatus.textContent = 'Calibrating...';
        }

        // ---- OTHER STATS ----
        this.elements.codingTime.textContent = data.breaks?.time || '0 min';
        this.elements.stressLevel.textContent = data.stress || 'Low';
        this.elements.breaksTaken.textContent = data.breaks?.taken ?? 0;
        this.elements.typingSpeed.textContent = `${data.typing?.speed ?? 0} keys/min`;

        // ---- LAST UPDATE ----
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
            const response = await fetch(`${this.backendUrl}/api/break`, {
                method: 'POST'
            });
            const result = await response.json();

            if (result.success) {
                this.showNotification('Break recorded!');
                this.fetchStatus();
            }
        } catch (error) {
            console.error('Error recording break:', error);
        }
    }

    async resetStats() {
        if (!confirm('Reset all statistics?')) return;

        try {
            const response = await fetch(`${this.backendUrl}/api/reset`, {
                method: 'POST'
            });
            const result = await response.json();

            if (result.success) {
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

        setTimeout(() => notification.remove(), 3000);
    }

    startPolling() {
        this.fetchStatus();
        setInterval(() => this.fetchStatus(), this.updateInterval);
        console.log('Polling started');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.devCareApp = new DevCareApp();
});
