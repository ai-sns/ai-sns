/**
 * SNS Module - State Management
 * SNS state management
 */

const snsState = {
    // Map state
    map: {
        initialized: false,
        center: { lng: 116.404, lat: 39.915 },
        zoom: 12,
        markers: []
    },

    // User state
    user: {
        money: 10996.61,
        life: 125,
        energy: 150,
        profession: 'Doctor',
        level: 3,
        credit: 100,
        exp: 30,
        location: {
            lng: 116.36383031947238,
            lat: 39.76458567198844
        }
    },

    // Online state
    online: {
        status: 'online',
        nodes: 0,
        activeUsers: 0,
        messageCount: 0
    },

    // Move mode
    moveMode: 'free', // 'route', 'free', 'follow'

    // Panel state
    panels: {
        toolbar: {
            collapsed: false
        },
        settings: {
            collapsed: false
        },
        status: {
            collapsed: false,
            activeTab: 'process' // 'process', 'resource', 'think'
        }
    },

    // WebSocket connection state
    websocket: {
        connected: false,
        reconnecting: false
    }
};

export default {
    /**
     * Get state
     */
    getState() {
        return snsState;
    },

    /**
     * Update map state
     */
    updateMap(mapData) {
        Object.assign(snsState.map, mapData);
    },

    /**
     * Update user state
     */
    updateUser(userData) {
        Object.assign(snsState.user, userData);
    },

    /**
     * Update online state
     */
    updateOnline(onlineData) {
        Object.assign(snsState.online, onlineData);
    },

    /**
     * Set move mode
     */
    setMoveMode(mode) {
        snsState.moveMode = mode;
    },

    /**
     * Update panel state
     */
    updatePanel(panelName, panelData) {
        if (snsState.panels[panelName]) {
            Object.assign(snsState.panels[panelName], panelData);
        }
    },

    /**
     * Add marker
     */
    addMarker(marker) {
        snsState.map.markers.push(marker);
    },

    /**
     * Remove marker
     */
    removeMarker(markerId) {
        snsState.map.markers = snsState.map.markers.filter(m => m.id !== markerId);
    },

    /**
     * Clear all markers
     */
    clearMarkers() {
        snsState.map.markers = [];
    },

    /**
     * Update WebSocket state
     */
    updateWebSocket(wsData) {
        Object.assign(snsState.websocket, wsData);
    }
};
