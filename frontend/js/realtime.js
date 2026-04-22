/**
 * WebSocket Real-time Updates Manager
 * Handles live data push from server with token auth and retry logic
 */

class RealtimeManager {
    constructor() {
        this.ws = null;
        this.connected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 3;
        this.reconnectDelay = 5000; // 5 seconds
        this.reconnectTimeout = null;
        this.heartbeatTimeout = null;
        this.shouldReconnect = true;

        this.warningBanner = null;
        this.connectionStatus = null;
    }

    /**
     * Initialize WebSocket connection
     */
    connect() {
        // Check if already logged in
        const token = sessionStorage.getItem('auth_token');
        if (!token) {
            console.log('No auth token, skipping WebSocket');
            return;
        }

        // Get WebSocket URL
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        const url = `${protocol}//${host}/ws/live?token=${encodeURIComponent(token)}`;

        console.log('Connecting to WebSocket:', url);

        try {
            this.ws = new WebSocket(url);
            this.ws.onopen = () => this._onOpen();
            this.ws.onmessage = (event) => this._onMessage(event);
            this.ws.onerror = (event) => this._onError(event);
            this.ws.onclose = () => this._onClose();
        } catch (err) {
            console.error('WebSocket connection error:', err);
            this._scheduleReconnect();
        }
    }

    /**
     * Handle WebSocket open
     */
    _onOpen() {
        console.log('WebSocket connected');
        this.connected = true;
        this.reconnectAttempts = 0;

        // Hide warning banner if shown
        if (this.warningBanner) {
            this.warningBanner.style.display = 'none';
        }

        // Update status
        this._updateConnectionStatus(true);

        // Clear any pending reconnect timeout
        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
            this.reconnectTimeout = null;
        }

        // Setup heartbeat to detect drops
        this._setupHeartbeat();
    }

    /**
     * Handle incoming WebSocket message
     */
    _onMessage(event) {
        try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'live_update') {
                this._processLiveUpdate(data);
            }

            // Reset heartbeat
            if (this.heartbeatTimeout) {
                clearTimeout(this.heartbeatTimeout);
            }
            this._setupHeartbeat();

        } catch (err) {
            console.error('Error processing WebSocket message:', err);
        }
    }

    /**
     * Handle WebSocket error
     */
    _onError(event) {
        console.error('WebSocket error:', event);
        this._updateConnectionStatus(false);
    }

    /**
     * Handle WebSocket close
     */
    _onClose() {
        console.log('WebSocket disconnected');
        this.connected = false;

        // Clear heartbeat
        if (this.heartbeatTimeout) {
            clearTimeout(this.heartbeatTimeout);
        }

        // Show warning banner
        if (this.warningBanner) {
            this.warningBanner.style.display = 'grid';
        }

        // Try to reconnect
        if (this.shouldReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
            this._scheduleReconnect();
        } else if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.warn('Max reconnection attempts reached, falling back to polling');
            this._fallbackToPolling();
        }
    }

    /**
     * Schedule WebSocket reconnection
     */
    _scheduleReconnect() {
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1);
        
        console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
        }

        this.reconnectTimeout = setTimeout(() => {
            this.connect();
        }, delay);
    }

    /**
     * Fallback to polling if WebSocket fails
     */
    _fallbackToPolling() {
        console.log('Falling back to polling interval');
        
        // Switch main polling to faster interval
        if (window.pollInterval) {
            clearInterval(window.pollInterval);
        }

        // Resume 15s polling if it exists
        if (window.startPolling) {
            window.startPolling();
        }
    }

    /**
     * Setup heartbeat to detect connection drops
     */
    _setupHeartbeat() {
        if (this.heartbeatTimeout) {
            clearTimeout(this.heartbeatTimeout);
        }

        // Trigger fallback if no message for 30 seconds
        this.heartbeatTimeout = setTimeout(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                console.warn('WebSocket heartbeat timeout');
                this.ws.close();
            }
        }, 30000);
    }

    /**
     * Process live update data
     */
    _processLiveUpdate(data) {
        try {
            const { timestamp, zones, active_alerts, kpis } = data;

            console.log('Live update received:', timestamp);

            // Update KPI boxes
            this._updateKPIBoxes(kpis, active_alerts);

            // Update zone indicators
            this._updateZoneIndicators(zones);

            // Update timestamp
            const tsElement = document.getElementById('liveUpdateTimestamp');
            if (tsElement) {
                const date = new Date(timestamp);
                tsElement.textContent = date.toLocaleTimeString();
            }

        } catch (err) {
            console.error('Error processing live update:', err);
        }
    }

    /**
     * Update KPI boxes with new data
     */
    _updateKPIBoxes(kpis, activeAlerts) {
        try {
            // Update flights
            const flightsEl = document.querySelector('[data-metric="flights"]');
            if (flightsEl) {
                flightsEl.textContent = kpis.flights || 0;
            }

            // Update anomalies
            const anomaliesEl = document.querySelector('[data-metric="anomalies"]');
            if (anomaliesEl) {
                anomaliesEl.textContent = kpis.anomalies || 0;
            }

            // Update avg stress
            const stressEl = document.querySelector('[data-metric="avg_stress"]');
            if (stressEl) {
                stressEl.textContent = (kpis.avg_stress || 0).toFixed(1);
            }

            // Update avg rubber
            const rubberEl = document.querySelector('[data-metric="avg_rubber"]');
            if (rubberEl) {
                rubberEl.textContent = (kpis.avg_rubber || 0).toFixed(1);
            }

            // Update worst zone
            const worstEl = document.querySelector('[data-metric="worst_zone"]');
            if (worstEl) {
                worstEl.textContent = kpis.worst_zone || 'Zone-01';
            }

            // Update active alerts
            const alertsEl = document.querySelector('[data-metric="active_alerts"]');
            if (alertsEl) {
                alertsEl.textContent = activeAlerts || 0;
            }

        } catch (err) {
            console.error('Error updating KPI boxes:', err);
        }
    }

    /**
     * Update zone status indicators
     */
    _updateZoneIndicators(zones) {
        try {
            for (const [zoneId, zoneData] of Object.entries(zones)) {
                const zoneEl = document.querySelector(`[data-zone-id="${zoneId}"]`);
                if (zoneEl) {
                    // Update status classes
                    zoneEl.classList.remove('normal', 'warning', 'critical', 'anomaly');
                    zoneEl.classList.add(zoneData.status.toLowerCase());

                    // Update status text
                    const statusEl = zoneEl.querySelector('.zone-status');
                    if (statusEl) {
                        statusEl.textContent = zoneData.status;
                    }

                    // Update stress value
                    const stressEl = zoneEl.querySelector('.zone-stress');
                    if (stressEl) {
                        stressEl.textContent = zoneData.avg_stress.toFixed(1);
                    }
                }
            }
        } catch (err) {
            console.error('Error updating zone indicators:', err);
        }
    }

    /**
     * Update connection status display
     */
    _updateConnectionStatus(connected) {
        try {
            if (!this.connectionStatus) {
                this.connectionStatus = document.getElementById('connectionStatus');
            }

            if (this.connectionStatus) {
                const indicator = this.connectionStatus.querySelector('.status-indicator');
                const text = this.connectionStatus.querySelector('.status-text');

                if (connected) {
                    indicator?.classList.add('connected');
                    indicator?.classList.remove('disconnected');
                    text?.textContent = 'LIVE';
                } else {
                    indicator?.classList.remove('connected');
                    indicator?.classList.add('disconnected');
                    text?.textContent = 'OFFLINE';
                }
            }
        } catch (err) {
            console.error('Error updating connection status:', err);
        }
    }

    /**
     * Create and show warning banner
     */
    createWarningBanner() {
        if (this.warningBanner) {
            return;
        }

        this.warningBanner = document.createElement('div');
        this.warningBanner.id = 'signalLostBanner';
        this.warningBanner.style.cssText = `
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 40px;
            background: #ff3333;
            color: #1a1a0e;
            border-bottom: 2px solid #1a1a0e;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 1px;
            z-index: 1000;
            animation: pulse 1s infinite;
        `;
        this.warningBanner.textContent = '⚠️ SIGNAL LOST - ATTEMPTING RECONNECTION ⚠️';

        // Add CSS animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }
        `;
        document.head.appendChild(style);

        document.body.insertBefore(this.warningBanner, document.body.firstChild);
    }

    /**
     * Disconnect and cleanup
     */
    disconnect() {
        this.shouldReconnect = false;

        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
        }

        if (this.heartbeatTimeout) {
            clearTimeout(this.heartbeatTimeout);
        }

        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}

// Create global instance
window.realtimeManager = null;

/**
 * Initialize real-time updates on page load
 */
window.addEventListener('DOMContentLoaded', () => {
    // Check if user is still logged in
    const token = sessionStorage.getItem('auth_token');
    if (!token) {
        // Not logged in, redirect to login
        window.location.href = '/login.html';
        return;
    }

    // Initialize real-time manager
    window.realtimeManager = new RealtimeManager();
    window.realtimeManager.createWarningBanner();
    
    // Adjust body margin if banner might be used
    document.body.style.marginTop = '0';

    // Connect to WebSocket
    window.realtimeManager.connect();
});

/**
 * Cleanup on page unload
 */
window.addEventListener('beforeunload', () => {
    if (window.realtimeManager) {
        window.realtimeManager.disconnect();
    }
});

export { RealtimeManager };
