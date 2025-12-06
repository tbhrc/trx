// Dashboard Components and Utilities v1.2.4

/**
 * Calculate signal strength (0-100)
 */
function calculateSignalStrength(signal) {
    if (!signal) return 0;

    let strength = 0;

    // R:R ratio contribution (30%)
    const rr = signal.reward_risk_ratio || 0;
    strength += Math.min(rr / 2.0, 1.0) * 30;

    // Sentiment alignment (20%)
    const sentiment = signal.sentiment_score || 0;
    if (signal.direction === 'long' && sentiment > 0) strength += 20;
    if (signal.direction === 'short' && sentiment < 0) strength += 20;

    // Not blocked by news (30%)
    if (!signal.news_blocked) strength += 30;

    // Base quality (20%)
    strength += 20;

    return Math.round(Math.min(strength, 100));
}

/**
 * Get strength class (weak/medium/strong)
 */
function getStrengthClass(strength) {
    if (strength >= 70) return 'strong';
    if (strength >= 40) return 'medium';
    return 'weak';
}

/**
 * Format timestamp to relative time
 */
function formatRelativeTime(timestamp) {
    if (!timestamp) return 'Unknown';

    const now = new Date();
    const signalTime = new Date(timestamp);
    const diffMs = now - signalTime;
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;

    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
}

/**
 * Format price with appropriate decimal places
 */
function formatPrice(price, instrument) {
    if (!price) return 'N/A';

    // Forex pairs: 5 decimals for JPY, 5 for others
    if (instrument.includes('JPY')) return price.toFixed(3);
    if (instrument.includes('USD') || instrument.includes('EUR') || instrument.includes('GBP')) {
        return price.toFixed(5);
    }

    // Gold, indices: 2 decimals
    return price.toFixed(2);
}

/**
 * Create sentiment gauge chart
 */
function createSentimentGauge(canvasId, score) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    // Normalize score to 0-100 range (from -1 to +1)
    const normalizedScore = ((score + 1) / 2) * 100;

    // Color based on sentiment
    let color;
    if (score < -0.5) color = '#ef4444';
    else if (score > 0.5) color = '#10b981';
    else color = '#f59e0b';

    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [normalizedScore, 100 - normalizedScore],
                backgroundColor: [color, '#1f2937'],
                borderWidth: 0
            }]
        },
        options: {
            rotation: -90,
            circumference: 180,
            cutout: '75%',
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            },
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

/**
 * Create signal card HTML
 */
function createSignalCard(instrument, signal) {
    const strength = calculateSignalStrength(signal);
    const strengthClass = getStrengthClass(strength);

    if (!signal) {
        return `
      <div class="signal-card no-signal">
        <div class="card-header">
          <div>
            <div class="instrument-name">${instrument}</div>
            <div class="timeframe">D | H4</div>
          </div>
        </div>
        <div style="text-align: center; padding: 2rem 0; color: var(--text-muted);">
          <p>No signal available</p>
        </div>
      </div>
    `;
    }

    const canvasId = `gauge-${instrument}`;

    return `
    <div class="signal-card">
      <div class="card-header">
        <div>
          <div class="instrument-name">${instrument}</div>
          <div class="timeframe">D | H4</div>
        </div>
        <span class="direction-badge ${signal.direction}">${signal.direction.toUpperCase()} ${signal.direction === 'long' ? '🟢' : '🔴'}</span>
      </div>
      
      <div class="price-levels">
        <div class="price-item">
          <div class="price-label">Entry</div>
          <div class="price-value">${formatPrice(signal.entry, instrument)}</div>
        </div>
        <div class="price-item">
          <div class="price-label">Stop Loss</div>
          <div class="price-value">${formatPrice(signal.stop_loss, instrument)}</div>
        </div>
        <div class="price-item">
          <div class="price-label">TP1</div>
          <div class="price-value">${formatPrice(signal.tp1, instrument)}</div>
        </div>
        <div class="price-item">
          <div class="price-label">TP2</div>
          <div class="price-value">${formatPrice(signal.tp2, instrument)}</div>
        </div>
      </div>
      
      <div class="risk-metrics">
        <div class="metric">
          <div class="metric-label">R:R</div>
          <div class="metric-value">${signal.reward_risk_ratio ? signal.reward_risk_ratio.toFixed(2) : 'N/A'}</div>
        </div>
        <div class="metric">
          <div class="metric-label">Risk</div>
          <div class="metric-value">${signal.risk_percent ? signal.risk_percent.toFixed(1) + '%' : 'N/A'}</div>
        </div>
      </div>
      
      <div class="news-status ${signal.news_blocked ? 'blocked' : ''}">
        <span class="news-icon">${signal.news_blocked ? '🔴' : '🟢'}</span>
        <div class="news-text">
          <strong>${signal.news_blocked ? 'BLOCKED' : 'Clear'}</strong>
          ${signal.news_blocked ? ' - High-impact event' : ' - No blocking events'}
        </div>
      </div>
      
      <div class="signal-strength">
        <div class="strength-header">
          <span class="strength-label">Signal Strength</span>
          <span class="strength-value">${strength}%</span>
        </div>
        <div class="strength-bar">
          <div class="strength-fill ${strengthClass}" style="width: ${strength}%"></div>
        </div>
      </div>
      
      <div class="sentiment-gauge">
        <div class="strength-header">
          <span class="strength-label">Sentiment</span>
          <span class="strength-value">${signal.sentiment_score !== null ? signal.sentiment_score.toFixed(2) : '0.00'}</span>
        </div>
        <div class="gauge-container">
          <canvas id="${canvasId}" height="100"></canvas>
        </div>
      </div>
      
      <div class="card-footer">
        <span class="timestamp">${formatRelativeTime(signal.timestamp)}</span>
      </div>
    </div>
  `;
}
