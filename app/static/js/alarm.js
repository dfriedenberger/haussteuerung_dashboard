// Alarm WebSocket Management
class AlarmWebSocket {
    constructor() {
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 1000;
        this.isConnected = false;
        
        this.connect();
        
        // Auto-refresh every 30 seconds as fallback
        setInterval(() => {
            if (!this.isConnected) {
                this.connect();
            }
        }, 30000);
    }
    
    connect() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/alarm/ws`;
            
            this.socket = new WebSocket(wsUrl);
            
            this.socket.onopen = () => {
                console.log('Alarm WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.updateConnectionStatus(true);
            };
            
            this.socket.onmessage = (event) => {
                const message = JSON.parse(event.data);
                this.handleMessage(message);
            };
            
            this.socket.onclose = () => {
                console.log('Alarm WebSocket disconnected');
                this.isConnected = false;
                this.updateConnectionStatus(false);
                this.attemptReconnect();
            };
            
            this.socket.onerror = (error) => {
                console.error('Alarm WebSocket error:', error);
                this.isConnected = false;
                this.updateConnectionStatus(false);
            };
            
        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
            this.attemptReconnect();
        }
    }
    
    handleMessage(message) {
        console.log('Received alarm message:', message);
        
        switch (message.type) {
            case 'initial_data':
                this.renderAlarms(message.data.alarms);
                break;
            case 'alarm_update':
                this.updateAlarm(message.data);
                break;
            default:
                console.log('Unknown message type:', message.type);
        }
        
        this.updateLastRefresh();
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay * this.reconnectAttempts);
        }
    }
    
    updateConnectionStatus(connected) {
        const indicator = document.getElementById('connection-indicator');
        if (connected) {
            indicator.innerHTML = '<i class="bi bi-wifi"></i> Verbunden';
            indicator.className = 'badge bg-success status-connected';
        } else {
            indicator.innerHTML = '<i class="bi bi-wifi-off"></i> Getrennt';
            indicator.className = 'badge bg-danger status-disconnected';
        }
    }
    
    renderAlarms(alarms) {
        const container = document.getElementById('alarms-container');
        const template = Handlebars.compile(document.getElementById('alarm-template').innerHTML);
        
        // Sort alarms: active first, then by priority (high to low), then by timestamp
        const sortedAlarms = alarms.sort((a, b) => {
            // Status priority: an > quittiert > aus
            const statusPriority = { an: 3, quittiert: 2, aus: 1 };
            const statusDiff = statusPriority[b.status] - statusPriority[a.status];
            if (statusDiff !== 0) return statusDiff;
            
            // Then by priority (high to low)
            const priorityDiff = b.priority - a.priority;
            if (priorityDiff !== 0) return priorityDiff;
            
            // Then by timestamp (newest first)
            return new Date(b.timestamp) - new Date(a.timestamp);
        });
        
        container.innerHTML = template({ alarms: sortedAlarms });
        
        // Update alarm count
        this.updateAlarmCount(alarms);
        
        // Apply current filter
        this.applyFilter();
    }
    
    updateAlarm(alarmData) {
        // For now, refresh all alarms - in a real implementation, 
        // we would update just the specific alarm
        console.log('Alarm updated:', alarmData);
        // This would typically trigger a refresh or update the specific alarm element
    }
    
    updateAlarmCount(alarms) {
        const activeAlarms = alarms.filter(alarm => alarm.status === 'an').length;
        const totalAlarms = alarms.length;
        
        const countElement = document.getElementById('alarm-count');
        if (activeAlarms > 0) {
            countElement.textContent = `${activeAlarms} aktive von ${totalAlarms} Alarmen`;
            countElement.className = 'badge bg-danger';
        } else {
            countElement.textContent = `${totalAlarms} Alarme`;
            countElement.className = 'badge bg-success';
        }
    }
    
    updateLastRefresh() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('de-DE');
        document.getElementById('last-refresh').textContent = `Aktualisiert: ${timeString}`;
    }
    
    applyFilter() {
        const selectedFilter = document.querySelector('input[name="alarm-filter"]:checked').value;
        const alarmCards = document.querySelectorAll('.alarm-card');
        
        let visibleCount = 0;
        
        alarmCards.forEach(card => {
            const status = card.dataset.status;
            
            if (selectedFilter === 'all' || status === selectedFilter) {
                card.style.display = 'block';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });
        
        // Update filter button text with count
        const filterButtons = document.querySelectorAll('label[for^="filter-"]');
        filterButtons.forEach(button => {
            const input = document.querySelector(`#${button.getAttribute('for')}`);
            const filterValue = input.value;
            
            if (filterValue === 'all') {
                const totalCount = alarmCards.length;
                button.innerHTML = button.innerHTML.replace(/\d+/, '').replace('Alle', `Alle (${totalCount})`);
            }
        });
    }
}

// Handlebars helpers
Handlebars.registerHelper('eq', function(a, b) {
    return a === b;
});

Handlebars.registerHelper('formatDateTime', function(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('de-DE', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
});

// Global function for acknowledging alarms
function acknowledgeAlarm(alarmId) {
    // This would send a request to acknowledge the alarm
    console.log('Acknowledging alarm:', alarmId);
    
    // Show confirmation
    if (confirm('Möchten Sie diesen Alarm wirklich quittieren?')) {
        // Here you would send an API request to acknowledge the alarm
        // For now, we'll just show a notification
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-success alert-dismissible fade show position-fixed';
        alertDiv.style.top = '70px';
        alertDiv.style.right = '20px';
        alertDiv.style.zIndex = '1050';
        alertDiv.innerHTML = `
            Alarm #${alarmId} wurde quittiert.
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alertDiv);
        
        // Remove alert after 3 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 3000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize WebSocket
    const alarmWS = new AlarmWebSocket();
    
    // Filter change handlers
    document.querySelectorAll('input[name="alarm-filter"]').forEach(radio => {
        radio.addEventListener('change', () => {
            alarmWS.applyFilter();
        });
    });
    
    // Refresh button
    document.getElementById('refresh-btn').addEventListener('click', function() {
        const button = this;
        const icon = button.querySelector('i');
        
        // Add loading state
        button.disabled = true;
        icon.className = 'bi bi-arrow-clockwise';
        icon.style.animation = 'spin 1s linear infinite';
        
        // Reconnect WebSocket to fetch fresh data
        alarmWS.connect();
        
        // Reset button after 2 seconds
        setTimeout(() => {
            button.disabled = false;
            icon.style.animation = '';
        }, 2000);
    });
});

// CSS for spin animation
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);