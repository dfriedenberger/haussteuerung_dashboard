$(document).ready(function() {

    
    let ws = null;
    let reconnectInterval = null;
    
    // Kompiliere Handlebars Template
    const source = $('#device-tile-template').html();
    const template = Handlebars.compile(source);
    
    // Handlebars Helpers
    Handlebars.registerHelper('formatTime', function(timestamp) {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        return date.toLocaleTimeString('de-DE');
    });
    
    // WebSocket-Verbindung erstellen
    function connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/dashboard/ws`;
        
        ws = new WebSocket(wsUrl);
        
        ws.onopen = function(event) {
            console.log('Dashboard WebSocket connected');
            updateConnectionStatus(true);
            
            // Clear reconnect interval if it exists
            if (reconnectInterval) {
                clearInterval(reconnectInterval);
                reconnectInterval = null;
            }
        };
        
        ws.onmessage = function(event) {
            const message = JSON.parse(event.data);
            
            if (message.type === 'initial_data' || message.type === 'values_update') {
                updateDeviceDisplay(message.data);
                
                // Update last refresh indicator
                $('#last-refresh').text('Zuletzt: ' + new Date().toLocaleTimeString('de-DE'));
                
                // If this is a real-time update, show a brief flash
                if (message.type === 'values_update') {
                    showUpdateIndicator();
                }
            }
        };
        
        ws.onclose = function(event) {
            console.log('Dashboard WebSocket disconnected');
            updateConnectionStatus(false);
            
            // Attempt to reconnect every 5 seconds
            if (!reconnectInterval) {
                reconnectInterval = setInterval(() => {
                    console.log('Attempting to reconnect...');
                    connectWebSocket();
                }, 5000);
            }
        };
        
        ws.onerror = function(error) {
            console.error('Dashboard WebSocket error:', error);
            updateConnectionStatus(false);
        };
    }
    
    // Update the device display with new data
    function updateDeviceDisplay(data) {
        
        console.log(data)
        const html = template({ data: data });
        $('#devices-container').html(html);
        console.log(html)

    }
    
    // Connection status indicator
    function updateConnectionStatus(connected) {
        const statusIndicator = $('#connection-status');
        if (statusIndicator.length === 0) {
            $('#last-refresh').after(
                '<span id="connection-status" class="badge ms-2"></span>'
            );
        }
        
        if (connected) {
            $('#connection-status')
                .removeClass('bg-danger')
                .addClass('bg-success')
                .text('Live');
        } else {
            $('#connection-status')
                .removeClass('bg-success')
                .addClass('bg-danger')
                .text('Offline');
        }
    }
    
    // Show a brief update indicator
    function showUpdateIndicator() {
        const indicator = $('#update-indicator');
        if (indicator.length === 0) {
            $('h1').after('<span id="update-indicator" class="badge bg-info ms-2" style="display: none;">Aktualisiert</span>');
        }
        
        $('#update-indicator').fadeIn(200).delay(1500).fadeOut(500);
    }
    
    // Event Handlers
    $('#refresh-btn').click(function() {
        const icon = $(this).find('.refresh-icon');
        icon.addClass('rotating');
        
        // Reconnect WebSocket to get fresh data
        if (ws) {
            ws.close();
        }
        connectWebSocket();
        
        setTimeout(() => icon.removeClass('rotating'), 1000);
    });
    
    // Start WebSocket connection
    connectWebSocket();
    
    // Cleanup on page unload
    $(window).on('beforeunload', function() {
        if (ws) {
            ws.close();
        }
        if (reconnectInterval) {
            clearInterval(reconnectInterval);
        }
    });
});

