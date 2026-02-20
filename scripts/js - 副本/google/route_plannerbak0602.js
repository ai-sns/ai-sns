
    //route plan
    var directionDisplay;
    var stepDisplay;
    var markerArray = [];
    var position;
    var polyline = null;
    var poly2 = null;
    var speed = 0.000005, wait = 1;

    var myPano;
    var panoClient;
    var nextPanoId;
    var timerHandle = null;

    function createMarker(latlng, label, html) {

        var contentString = '<b>' + label + '</b><br>' + html;
        var marker = new google.maps.Marker({
            position: latlng,
            map: map,
            title: label,
            icon: {
                url: '/scripts/mapavartar.png', // 图标图像的路径
                scaledSize: new google.maps.Size(36, 49), // 图标的缩放大小，单位为像素
                origin: new google.maps.Point(0, 0), // 图标的原点，通常为(0, 0)
                anchor: new google.maps.Point(18, 49) // 图标的锚点，通常为图标底部中心
            },
            zIndex: Math.round(latlng.lat() * -100000) << 5
        });
        marker.myname = label;


        google.maps.event.addListener(marker, 'click', function () {
            infowindow.setContent(contentString);
            infowindow.open(map, marker);
        });
        return marker;
    }


    function initialize_route() {

        // Create a renderer for directions and bind it to the map.

        var rendererOptions = {
            draggable: true,
            map: map
        }
        directionsDisplay = new google.maps.DirectionsRenderer(rendererOptions);

        directionsDisplay.addListener("directions_changed", () => {
            const directions = directionsDisplay.getDirections();

            if (directions) {
                console.log(directions);
                handleRoute(directions);
            }
        });


        // Instantiate an info window to hold step text.
        stepDisplay = new google.maps.InfoWindow();

        polyline = new google.maps.Polyline({
            path: [],
            strokeColor: '#FF0000',
            strokeWeight: 3
        });
        poly2 = new google.maps.Polyline({
            path: [],
            strokeColor: '#FF0000',
            strokeWeight: 3
        });
    }


    var steps = []

    function planRoute() {
        calcRoute();
    }


    function calcRoute() {

        if (timerHandle) {
            clearTimeout(timerHandle);
        }
        if (marker) {
            marker.setMap(null);
        }
        polyline.setMap(null);
        poly2.setMap(null);
        directionsDisplay.setMap(null);
        polyline = new google.maps.Polyline({
            path: [],
            strokeColor: '#FF0000',
            strokeWeight: 3
        });
        poly2 = new google.maps.Polyline({
            path: [],
            strokeColor: '#FF0000',
            strokeWeight: 3
        });
        // Create a renderer for directions and bind it to the map.
        rendererOptions = {
            draggable: true,
            map: map
        }
        directionsDisplay = new google.maps.DirectionsRenderer(rendererOptions);

        directionsDisplay.addListener("directions_changed", () => {
            const directions = directionsDisplay.getDirections();

            if (directions) {
                console.log(directions);
                handleRoute(directions);
            }
        });

        var start = document.getElementById("start").value;
        var end = document.getElementById("end").value;
        var travelMode = google.maps.DirectionsTravelMode.DRIVING

        var request = {
            origin: start,
            destination: end,
            travelMode: travelMode
        };

        // Route the directions and pass the response to a
        // function to create markers for each step.
        directionsService.route(request, function (response, status) {
            if (status == google.maps.DirectionsStatus.OK) {
                let directions = response;
                directionsDisplay.setDirections(directions);
            }
        });
    }


    function handleRoute(directions) {

        if (timerHandle) {
            clearTimeout(timerHandle);
        }
        if (marker) {
            marker.setMap(null);
        }
        polyline.setMap(null);
        poly2.setMap(null);
        // directionsDisplay.setMap(null);

        polyline = new google.maps.Polyline({
            path: [],
            strokeColor: '#FF0000',
            strokeWeight: 3
        });
        poly2 = new google.maps.Polyline({
            path: [],
            strokeColor: '#FF0000',
            strokeWeight: 3
        });

        var bounds = new google.maps.LatLngBounds();
        var route = directions.routes[0];
        startLocation = {};
        endLocation = {};

        // For each route, display summary information.
        var path = directions.routes[0].overview_path;
        var legs = directions.routes[0].legs;
        for (i = 0; i < legs.length; i++) {
            if (i == 0) {
                startLocation.latlng = legs[i].start_location;
                startLocation.address = legs[i].start_address;
                // marker = google.maps.Marker({map:map,position: startLocation.latlng});
                marker = createMarker(legs[i].start_location, "start", legs[i].start_address, "green");
            }
            endLocation.latlng = legs[i].end_location;
            console.log("endLocation.latlng:", endLocation.latlng);
            endLocation.address = legs[i].end_address;
            var steps = legs[i].steps;
            for (j = 0; j < steps.length; j++) {
                var nextSegment = steps[j].path;
                for (k = 0; k < nextSegment.length; k++) {
                    polyline.getPath().push(nextSegment[k]);
                    bounds.extend(nextSegment[k]);


                }
            }
        }

        polyline.setMap(map);
        map.fitBounds(bounds);
    }


    var step = 50; // 5; // metres
    var tick = 100; // milliseconds
    var eol;
    var k = 0;
    var stepnum = 0;
    var speed = "";
    var lastVertex = 1;
    var currentDistance = 50;


    //=============== animation functions ======================
    function updatePoly(d) {
        // Spawn a new polyline every 20 vertices, because updating a 100-vertex poly is too slow
        if (poly2.getPath().getLength() > 20) {
            poly2 = new google.maps.Polyline([polyline.getPath().getAt(lastVertex - 1)]);
        }

        if (polyline.GetIndexAtDistance(d) < lastVertex + 2) {
            if (poly2.getPath().getLength() > 1) {
                poly2.getPath().removeAt(poly2.getPath().getLength() - 1)
            }
            poly2.getPath().insertAt(poly2.getPath().getLength(), polyline.GetPointAtDistance(d));
        } else {
            poly2.getPath().insertAt(poly2.getPath().getLength(), endLocation.latlng);
        }
    }


    function animatePoly(d) {
        if (d > eol) {
            console.log("endLocation.latlng", endLocation.latlng.lat());
            map.panTo(endLocation.latlng);
            marker.setPosition(endLocation.latlng);
            return;
        }
        var p = polyline.GetPointAtDistance(d);
        console.log("middle point", p.lat());
        // map.panTo(p);
        marker.setPosition(p);
        updatePoly(d);
        timerHandle = setTimeout("animatePoly(" + (d + step) + ")", tick);
        currentDistance = d + step;
    }


    function startAnimation() {
        eol = polyline.Distance();
        map.setCenter(polyline.getPath().getAt(0));

        poly2 = new google.maps.Polyline({path: [polyline.getPath().getAt(0)], strokeColor: "#FF0000", strokeWeight: 10});

        setTimeout("animatePoly(50)", 2000);  // Allow time for the initial map display

    }


    // 轨迹模拟
    function startTrack() {

        startAnimation();
    }

    // 暂停动画，并显示当前地理位置点
    function pauseTrack() {

        if (timerHandle) {
            clearTimeout(timerHandle);
        }


    }

    // 继续动画
    function continueTrack() {
        d = currentDistance;
        timerHandle = setTimeout("animatePoly(" + d + ")", tick);
    }

    // 清除路线
    function stopTrack() {
        if (timerHandle) {
            clearTimeout(timerHandle);
        }
        if (marker) {
            marker.setMap(null);
        }
        polyline.setMap(null);
        poly2.setMap(null);
        directionsDisplay.setMap(null);
    }

    function computeTotalDistance(result) {
        let total = 0;
        const myroute = result.routes[0];

        if (!myroute) {
            return;
        }

        for (let i = 0; i < myroute.legs.length; i++) {
            total += myroute.legs[i].distance.value;
        }

        total = total / 1000;

    }


