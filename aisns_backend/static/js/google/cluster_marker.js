
    //handle cluster marker
    var markerCluster;
    var hiddenMarkers = {};
    var hiddenMarkerNationIds = {};
    var markers;

    function __snsNormalizeNationId(value) {
        try {
            return String(value ?? '').trim();
        } catch (e) {
            return '';
        }
    }

    try {
        if (typeof window !== 'undefined') {
            window.__snsNormalizeNationId = __snsNormalizeNationId;
        }
    } catch (e) {
    }

    function _aiSnsUrl(p) {
        try {
            const baseRaw = (typeof window !== 'undefined' && window.__AI_SNS_SERVER__) ? String(window.__AI_SNS_SERVER__) : '';
            const base = baseRaw.endsWith('/') ? baseRaw.slice(0, -1) : baseRaw;
            if (!base) return '';
            const path = String(p || '');
            if (!path) return base;
            if (path.startsWith('/')) return base + path;
            return base + '/' + path;
        } catch (e) {
            return '';
        }
    }

    function showpoints() {
        // 2. Generate coordinate points

        const markersData = personsdata;


        // 3. Create marker objects and add to the map
        const iconSize = new google.maps.Size(36, 49); // Actual icon size
        markers = markersData.map(data => {
            const nationId = __snsNormalizeNationId(data && (data.nation_id ?? data.nationid));
            const marker = new google.maps.Marker({
                position: {
                    lng: data.location[0],
                    lat: data.location[1]
                },
                map: map,
                title: data.nick_name, // Marker title
                nation_id: data.nation_id,
                icon: {
                    url: _aiSnsUrl('/avatars/' + data.nation_id + '_avatar.png'), // Custom icon URL
                    scaledSize: iconSize // Scaled icon size
                }
            });

            try {
                if (nationId && hiddenMarkerNationIds && hiddenMarkerNationIds[nationId]) {
                    marker.setMap(null);
                    marker.setVisible(false);
                }
            } catch (e) {
            }

            // Add click handler for each marker
            marker.addListener('click', () => {
                alert(`Coordinates: (${data.location[0]}, ${data.location[1]})\nName: ${data.nick_name}`);
                const nid = __snsNormalizeNationId(data && (data.nation_id ?? data.nationid));
                if (nid) {
                    hiddenMarkers[nid] = marker;
                }
                showprofile(data.nation_id);
                // hideMarker(marker); // Hide marker and move to hidden list
            });
            console.log("marker:", marker);

            return marker;
        });

        // 4. Marker clustering (optional)
        try {
            if (markerCluster && typeof markerCluster.clearMarkers === 'function') {
                markerCluster.clearMarkers();
            }
        } catch (e) {
        }

        const clusterMarkers = (Array.isArray(markers) ? markers : []).filter(m => {
            try {
                const nid = __snsNormalizeNationId(m && m.nation_id);
                return !nid || !hiddenMarkerNationIds || !hiddenMarkerNationIds[nid];
            } catch (e) {
                return true;
            }
        });

        markerCluster = new MarkerClusterer(map, clusterMarkers, {
            // imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m'
            imagePath: './assets/m'
            // Combined m1-m5: actual URL e.g. https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m1.png
        });
        console.log("markers", markers);
        persons_loaded_flag = true;
    }

    function getMarkerByNationId(nationId) {
        try {
            const id = __snsNormalizeNationId(nationId);
            if (!id || !Array.isArray(markers)) return null;
            return markers.find(marker => __snsNormalizeNationId(marker && marker.nation_id) === id) || null;
        } catch (e) {
            return null;
        }
    }

    function hideMarker(marker, nationId) {
        const id = __snsNormalizeNationId(nationId || (marker && marker.nation_id));
        if (id) {
            hiddenMarkerNationIds[id] = true;
        }

        if (!marker || typeof marker.setVisible !== 'function') {
            console.warn('[sns][marker] hideMarker skipped: marker not ready', { nationId: id });
            return;
        }

        try {
            if (markerCluster && typeof markerCluster.removeMarker === 'function') {
                markerCluster.removeMarker(marker, true);
                marker.setMap(null);
                marker.setVisible(false);
                return;
            }
        } catch (e) {
            console.warn('[sns][marker] hideMarker removeMarker failed:', e);
        }

        try {
            marker.setVisible(false);
        } catch (e) {
            console.warn('[sns][marker] hideMarker failed:', e);
        }
    }

    function showMarker(marker, nationId) {
        const id = __snsNormalizeNationId(nationId || (marker && marker.nation_id));
        if (id && hiddenMarkerNationIds) {
            delete hiddenMarkerNationIds[id];
        }

        if (!marker || typeof marker.setVisible !== 'function') {
            console.warn('[sns][marker] showMarker skipped: marker not ready', { nationId: id });
            return;
        }

        try {
            if (typeof marker.setMap === 'function') {
                marker.setMap(map);
            }
            marker.setVisible(true);
        } catch (e) {
            console.warn('[sns][marker] showMarker base restore failed:', e);
        }

        try {
            if (markerCluster && typeof markerCluster.addMarker === 'function') {
                markerCluster.addMarker(marker, true);
            }
        } catch (e) {
            console.warn('[sns][marker] showMarker addMarker failed:', e);
        }
    }

    try {
        if (typeof window !== 'undefined') {
            window.hideMarker = hideMarker;
            window.showMarker = showMarker;
            window.getMarkerByNationId = getMarkerByNationId;
        }
    } catch (e) {
    }
