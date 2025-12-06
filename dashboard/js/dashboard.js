// Main Dashboard Application v1.2.4

class TradingDashboard {
    constructor() {
        this.refreshInterval = 10000; // 10 seconds
        this.intervalId = null;
        this.isConnected = false;
        this.charts = {}; // Store Chart.js instances
    }

    /**
     * Initialize dashboard
     */
    async init() {
        console.log('Initializing Trading Dashboard v1.2.4...');

        // Initial load
        await this.loadSignals();

        // Start auto-refresh
        this.startAutoRefresh();

        // Setup controls
        this.setupControls();

        this.updateConnectionStatus(true);
    }

    /**
     * Load all signals from API
     */
    async loadSignals() {
        const container = document.getElementById('signals-grid');
        const statusEl = document.getElementById('status-text');

        try {
            // Show loading
            container.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
            statusEl.textContent = 'Loading...';

            // Fetch signals
            const signals = await api.getAllSignals();

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
            statusEl.textContent = `${signalCount} active signal${signalCount !== 1 ? 's' : ''}`;

            this.updateConnectionStatus(true);

        } catch (error) {
            console.error('Error loading signals:', error);
            container.innerHTML = `
        <div class="loading">
          <p style="color: var(--accent-short);">⚠️ Error loading signals</p>
          <p style="color: var(--text-muted); font-size: 0.875rem;">${error.message}</p>
        </div>
      `;
            statusEl.textContent = 'Error';
            this.updateConnectionStatus(false);
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
     * Start auto-refresh
     */
    startAutoRefresh() {
        if (this.intervalId) return;

        console.log(`Starting auto-refresh (${this.refreshInterval / 1000}s interval)`);

        this.intervalId = setInterval(() => {
            this.loadSignals();
            this.updateCountdown();
        }, this.refreshInterval);

        // Start countdown
        this.updateCountdown();
    }

    /**
     * Stop auto-refresh
     */
    stopAutoRefresh() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
            console.log('Auto-refresh stopped');
        }
    }

    /**
     * Update countdown timer
     */
    updateCountdown() {
        const countdownEl = document.getElementById('countdown');
        if (!countdownEl) return;

        let seconds = this.refreshInterval / 1000;

        const countdownInterval = setInterval(() => {
            seconds--;
            if (seconds <= 0) {
                clearInterval(countdownInterval);
                return;
            }
            countdownEl.textContent = `Next update in ${seconds}s`;
        }, 1000);
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
     * Setup control buttons
     */
    setupControls() {
        // Manual refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadSignals();
            });
        }

        // Pause/Resume button
        const pauseBtn = document.getElementById('pause-btn');
        if (pauseBtn) {
            pauseBtn.addEventListener('click', () => {
                if (this.intervalId) {
                    this.stopAutoRefresh();
                    pauseBtn.textContent = '▶️ Resume';
                } else {
                    this.startAutoRefresh();
                    pauseBtn.textContent = '⏸️ Pause';
                }
            });
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const dashboard = new TradingDashboard();
    dashboard.init();
});
