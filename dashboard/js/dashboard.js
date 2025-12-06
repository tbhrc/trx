// Main Dashboard Application v1.2.5 (WebSocket)

class TradingDashboard {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000; // 3 seconds
        this.isConnected = false;
        this.charts = {}; // Store Chart.js instances
    }

    /**
     * Initialize dashboard
     */
    async init() {
        console.log('Initializing Trading Dashboard v1.2.5 (WebSocket)...');

        // Setup controls
        this.setupControls();

        // Connect to WebSocket
        this.connectWebSocket();
    }

    /**
     * Connect to WebSocket server
     */
    connectWebSocket() {
        try {
            // Create WebSocket connection
            this.ws = new WebSocket('ws://127.0.0.1:8000/ws');

            // Connection opened
            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.reconnectAttempts = 0;
                this.updateConnectionStatus(true);
                this.updateStatusText('Connected - awaiting signals...');
            };

            // Listen for messages (signals)
            this.ws.onmessage = (event) => {
                try {
                    const signals = JSON.parse(event.data);
                    this.handleSignalUpdate(signals);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            // Connection closed
            this.ws.onclose = (event) => {
                console.log('WebSocket closed:', event.code, event.reason);
                this.updateConnectionStatus(false);
                this.updateStatusText('Disconnected');

                // Attempt reconnection
                this.attemptReconnect();
            };

            // Connection error
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus(false);
                this.updateStatusText('Connection error');
            };

        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            this.updateConnectionStatus(false);
            this.attemptReconnect();
        }
    }

    /**
     * Attempt to reconnect to WebSocket
     */
    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.log('Max reconnection attempts reached');
            this.updateStatusText('Connection failed - please refresh');
            return;
        }

        this.reconnectAttempts++;
        console.log(`Reconnecting... Attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
        this.updateStatusText(`Reconnecting (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

        setTimeout(() => {
            this.connectWebSocket();
        }, this.reconnectDelay);
    }

    /**
     * Handle signal update from WebSocket
     */
    handleSignalUpdate(signals) {
        const container = document.getElementById('signals-grid');

        try {
            // Clear container
            container.innerHTML = '';

            // Create cards
            for (const [instrument, signal] of Object.entries(signals)) {
                const cardHTML = createSignalCard(instrument, signal);
                container.innerHTML += cardHTML;
            }

            // Initialize sentiment gauges
            this.initializeGauges(signals);

            // Update status
            const signalCount = Object.values(signals).filter(s => s !== null).length;
            this.updateStatusText(`${signalCount} active signal${signalCount !== 1 ? 's' : ''}`);

            this.updateConnectionStatus(true);

            // Update last update time
            this.updateLastUpdateTime();

        } catch (error) {
            console.error('Error updating UI:', error);
        }
    }

    /**
     * Initialize sentiment gauge charts
     */
    initializeGauges(signals) {
        // Destroy existing charts
        Object.values(this.charts).forEach(chart => chart.destroy());
        this.charts = {};

        // Create new charts
        for (const [instrument, signal] of Object.entries(signals)) {
            if (signal && signal.sentiment_score !== null) {
                const canvasId = `gauge-${instrument}`;
                const chart = createSentimentGauge(canvasId, signal.sentiment_score);
                if (chart) {
                    this.charts[canvasId] = chart;
                }
            }
        }
    }

    /**
     * Update connection status indicator
     */
    updateConnectionStatus(connected) {
        this.isConnected = connected;

        const dotEl = document.getElementById('status-dot');
        const textEl = document.getElementById('status-connection');

        if (dotEl) {
            dotEl.className = connected ? 'status-dot' : 'status-dot disconnected';
        }
        if (textEl) {
            textEl.textContent = connected ? 'Connected' : 'Disconnected';
        }
    }

    /**
     * Update status text
     */
    updateStatusText(text) {
        const statusEl = document.getElementById('status-text');
        if (statusEl) {
            statusEl.textContent = text;
        }
    }

    /**
     * Update last update time
     */
    updateLastUpdateTime() {
        const countdownEl = document.getElementById('countdown');
        if (countdownEl) {
            const now = new Date();
            const timeStr = now.toLocaleTimeString();
            countdownEl.textContent = `Last update: ${timeStr} (Real-time via WebSocket)`;
        }
    }

    /**
     * Manual refresh (reconnect WebSocket)
     */
    manualRefresh() {
        console.log('Manual refresh requested - reconnecting WebSocket');

        // Close existing connection
        if (this.ws) {
            this.ws.close();
        }

        // Reset reconnection counter
        this.reconnectAttempts = 0;

        // Reconnect
        this.connectWebSocket();
    }

    /**
     * Setup control buttons
     */
    setupControls() {
        // Manual refresh button (now reconnects WebSocket)
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.manualRefresh();
            });
        }

        // Note: Pause button removed since WebSocket is always-on
        // Could add disconnect/connect toggle if needed
        const pauseBtn = document.getElementById('pause-btn');
        if (pauseBtn) {
            pauseBtn.style.display = 'none'; // Hide pause button for WebSocket
        }
    }

    /**
     * Disconnect WebSocket (for cleanup)
     */
    disconnect() {
        if (this.ws) {
            console.log('Disconnecting WebSocket');
            this.ws.close();
            this.ws = null;
        }
    }
}

// Initialize when DOM is ready
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new TradingDashboard();
    dashboard.init();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (dashboard) {
        dashboard.disconnect();
    }
});
