google.maps.event.addDomListener(window, 'load', init);
var map;
var currAddress;
function init() {
    var mapOptions = allMapOptions;
    var mapElement = document.getElementById('stats-home-map');
    var map = new google.maps.Map(mapElement, mapOptions);

    getMarkers(function(coords) {
        for (i = 0; i < coords.length; i++) {
            session = coords[i];
            infoWindowContent = '<div id="content">'+
            '<div id="siteNotice">'+
            '</div>'+
            '<h1 id="firstHeading" class="firstHeading">' + session.fullName + '</h1>'+
            '<div id="bodyContent">' +
            '<p><b>' + session.country + '</b></p>' +
            '<p>' + session.description + '</p>' +
            '</div>'+
            '</div>';
            addMarker(session.position, map, infoWindowContent);
        }
    });
}

function getMarkers(callback) {
    var coords = [];
    var errors = 0;
    for (i = 0; i < localNames.length; i++) {
        (function(localAddress, countryName, fullName, description){
            geocoder = new google.maps.Geocoder();
            if (geocoder) {
                geocoder.geocode({'address': localAddress}, function (results, status) {
                    if (status == google.maps.GeocoderStatus.OK) {
                        coords.push({
                            position: results[0],
                            fullName: fullName,
                            country: countryName,
                            description: description
                        });
                    }
                    else if (status == google.maps.GeocoderStatus.ZERO_RESULTS) {
                       checkMarkerFurther(countryName, fullName, description, coords, callback, errors);
                    } else {
                        errors++;
                        console.log("An error occured: " + localAddress);
                    }

                    if(coords.length == (localNames.length - errors)) {
                        if( typeof callback == 'function' ) {
                            callback(coords);
                        }
                    }
                });
            }
        })(localNames[i], countryNames[i], fullNames[i], sessionDescriptions[i]);
    }
}

function checkMarkerFurther(countryName, fullName, description, coords, callback, errors) {
    geocoder = new google.maps.Geocoder();
    if (geocoder) {
        geocoder.geocode({'address': countryName}, function (results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                coords.push({
                            position: results[0],
                            fullName: fullName,
                            country: countryName,
                            description: description
                        });
            }
            else {
                errors++;
                console.log("Not found for: " + countryName);
            }
            
            if(coords.length == (localNames.length - errors)) {
                if( typeof callback == 'function' ) {
                    callback(coords);
                }
            }
        });
    }
}

function addMarker(result, map, infoWindowContent) {
    var infowindow = new google.maps.InfoWindow({
        content: infoWindowContent,
        maxWidth: 200
    });
    var marker = new google.maps.Marker(
    {
        map: map,
        position: result.geometry.location
    });
    marker.addListener('click', function() {
      infowindow.open(map, marker);
    });
}

var allMapOptions = {
        center: new google.maps.LatLng(55.474628,12.01538),
        zoom: 3,
        zoomControl: true,
        zoomControlOptions: {
            style: google.maps.ZoomControlStyle.SMALL,
        },
        disableDoubleClickZoom: false,
        mapTypeControl: false,
        scaleControl: false,
        scrollwheel: false,
        panControl: false,
        streetViewControl: false,
        draggable : true,
        overviewMapControl: false,
        overviewMapControlOptions: {
            opened: false,
        },
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        styles: [
                    {
                        "featureType": "administrative",
                        "elementType": "labels.text.fill",
                        "stylers": [
                            {
                                "color": "#444444"
                            }
                        ]
                    },
                    {
                        "featureType": "administrative.country",
                        "elementType": "labels.text",
                        "stylers": [
                            {
                                "visibility": "off"
                            }
                        ]
                    },
                    {
                        "featureType": "administrative.province",
                        "elementType": "labels.text",
                        "stylers": [
                            {
                                "visibility": "off"
                            }
                        ]
                    },
                    {
                        "featureType": "administrative.locality",
                        "elementType": "labels.text",
                        "stylers": [
                            {
                                "visibility": "off"
                            }
                        ]
                    },
                    {
                        "featureType": "landscape",
                        "elementType": "all",
                        "stylers": [
                            {
                                "color": "#f2f2f2"
                            }
                        ]
                    },
                    {
                        "featureType": "poi",
                        "elementType": "all",
                        "stylers": [
                            {
                                "visibility": "off"
                            }
                        ]
                    },
                    {
                        "featureType": "road",
                        "elementType": "all",
                        "stylers": [
                            {
                                "saturation": -100
                            },
                            {
                                "lightness": 45
                            }
                        ]
                    },
                    {
                        "featureType": "road.highway",
                        "elementType": "all",
                        "stylers": [
                            {
                                "visibility": "simplified"
                            }
                        ]
                    },
                    {
                        "featureType": "road.arterial",
                        "elementType": "labels.icon",
                        "stylers": [
                            {
                                "visibility": "off"
                            }
                        ]
                    },
                    {
                        "featureType": "transit",
                        "elementType": "all",
                        "stylers": [
                            {
                                "visibility": "off"
                            }
                        ]
                    },
                    {
                        "featureType": "water",
                        "elementType": "all",
                        "stylers": [
                            {
                                "color": "#2e4496"
                            },
                            {
                                "visibility": "on"
                            }
                        ]
                    }
                ]
    }