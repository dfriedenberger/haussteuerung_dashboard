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
                this.renderAlarms(message.data.alarms);
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
        
        const template = Handlebars.compile(document.getElementById('alarm-template').innerHTML);
        
        // Sort alarms: active unacknowledged first, then by priority (high to low), then by timestamp
        const sortedAlarms = alarms.sort((a, b) => {
            // Status priority: active+unacknowledged > active+acknowledged > inactive
            const getStatusPriority = (alarm) => {
                if (alarm.active && !alarm.acknowledged) return 3; // Active, not acknowledged
                if (alarm.active && alarm.acknowledged) return 2;   // Active, acknowledged
                return 1; // Inactive
            };
            
            const statusDiff = getStatusPriority(b) - getStatusPriority(a);
            if (statusDiff !== 0) return statusDiff;
            
            // Then by priority (high to low)
            const priorityDiff = b.priority - a.priority;
            if (priorityDiff !== 0) return priorityDiff;
            
            // Then by timestamp (newest first)
            return new Date(b.timestamp) - new Date(a.timestamp);
        });
        

        $('#alarms-container').html(template({ alarms: sortedAlarms }));
        
        const ws = this
        $(".acknowledge-alarm").on("click", function(ev) {
            ev.preventDefault();
            const alarmId = $(this).data("alarm-id");
            // send message via websocket
            const message = { type: 'acknowledge_alarm', data: { alarm_id: alarmId } };

            if (ws.isConnected) {
                ws.socket.send(JSON.stringify(message));
            }
        });


        // Update alarm count
        this.updateAlarmCount(alarms);
        
        // Apply current filter
        this.applyFilter();
    }
    

    
    updateAlarmCount(alarms) {
        const activeAlarms = alarms.filter(alarm => alarm.active && !alarm.acknowledged).length;
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
            const active = card.dataset.active === 'true';
            const acknowledged = card.dataset.acknowledged === 'true';
            
            let showCard = false;
            
            switch (selectedFilter) {
                case 'all':
                    showCard = true;
                    break;
                case 'active':
                    showCard = active && !acknowledged;
                    break;
                case 'acknowledged':
                    showCard = acknowledged;
                    break;
                case 'inactive':
                    showCard = !active;
                    break;
            }
            
            if (showCard) {
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

Handlebars.registerHelper('and', function(a, b) {
    return a && b;
});

Handlebars.registerHelper('not', function(a) {
    return !a;
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