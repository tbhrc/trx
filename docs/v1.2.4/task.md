# Task: v1.2.4 - Enhanced Signal Dashboard

## Overview
Build professional trading dashboard with modern UI, real-time updates, sentiment visualizations, and signal strength indicators.

## Backend: API Endpoints
- [ ] Add `GET /signals/all` endpoint
  - [ ] Fetch signals for all instruments
  - [ ] Return as single JSON object
  - [ ] Test manually with browser/curl

## Frontend: Structure & Setup
- [ ] Create `dashboard/css/dashboard.css`
  - [ ] Define design system variables
  - [ ] Create base styles
  - [ ] Add responsive breakpoints
- [ ] Create `dashboard/js/api.js`
  - [ ] Implement `/signals/all` fetcher
  - [ ] Add error handling
- [ ] Create `dashboard/js/components.js`
  - [ ] Signal card component
  - [ ] Sentiment gauge component
  - [ ] Signal strength bar
- [ ] Create `dashboard/js/dashboard.js`
  - [ ] App initialization
  - [ ] Auto-refresh logic
- [ ] Update [dashboard/index.html](file:///c:/Users/TalentBridgeDubai/Documents/app-web-dev/trx/dashboard/index.html)
  - [ ] Include Chart.js CDN
  - [ ] Link new CSS/JS files
  - [ ] Update HTML structure

## Signal Card Components
- [ ] Card layout structure
  - [ ] Header (instrument + timeframe)
  - [ ] Direction badge (LONG/SHORT)
  - [ ] Price levels (entry, stop, TP1, TP2)
  - [ ] Risk metrics (R:R, risk %)
- [ ] News status indicator
  - [ ] 🟢 Clear / 🔴 Blocked
  - [ ] Countdown timer for blocking window
- [ ] Sentiment gauge (Chart.js arc)
  - [ ] -1.0 to +1.0 range
  - [ ] Color coding (red/yellow/green)
- [ ] Signal strength bar
  - [ ] Calculate strength (0-100%)
  - [ ] Progress bar visual
  - [ ] Color based on strength
- [ ] Timestamp display
  - [ ] Relative time ("5 mins ago")
- [ ] Responsive styling
  - [ ] Mobile (1 column)
  - [ ] Tablet (3 columns)
  - [ ] Desktop (5 columns)

## Auto-Refresh System
- [ ] Implement 10s auto-refresh
  - [ ] setInterval timer
  - [ ] Fetch all signals
  - [ ] Update UI
- [ ] Add countdown timer
  - [ ] "Next update in Xs"
- [ ] Add manual refresh button
- [ ] Add pause/resume toggle
- [ ] Connection status indicator
  - [ ] 🟢 Connected / 🔴 Disconnected
- [ ] Loading states
- [ ] Error handling with retry

## Testing & Validation
- [ ] Test all card components render
- [ ] Test sentiment gauge with various values
- [ ] Test signal strength calculation
- [ ] Test auto-refresh functionality
- [ ] Test manual controls (refresh, pause)
- [ ] Test responsive breakpoints
  - [ ] Mobile (< 768px)
  - [ ] Tablet (768-1200px)
  - [ ] Desktop (> 1200px)
- [ ] Browser compatibility
  - [ ] Chrome
  - [ ] Firefox
  - [ ] Edge
- [ ] Error scenarios
  - [ ] API down
  - [ ] Invalid data
  - [ ] Network timeout

## Documentation
- [ ] Update walkthrough
- [ ] Add usage screenshots
- [ ] Document configuration options

## Status: READY TO IMPLEMENT 🚀
