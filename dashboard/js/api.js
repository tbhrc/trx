// API Client for AI Trading Copilot v1.2.4

const API_BASE_URL = 'http://127.0.0.1:8000';

class TradingAPI {
    /**
     * Fetch all signals for configured instruments
     */
    async getAllSignals() {
        try {
            const response = await fetch(`${API_BASE_URL}/signals/all`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching signals:', error);
            throw error;
        }
    }

    /**
     * Fetch signal for a single instrument
     */
    async getSignal(instrument) {
        try {
            const response = await fetch(`${API_BASE_URL}/signal/latest?instrument=${instrument}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`Error fetching signal for ${instrument}:`, error);
            throw error;
        }
    }

    /**
     * Fetch system configuration
     */
    async getConfig() {
        try {
            const response = await fetch(`${API_BASE_URL}/config`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching config:', error);
            throw error;
        }
    }
}

// Export singleton instance
const api = new TradingAPI();
