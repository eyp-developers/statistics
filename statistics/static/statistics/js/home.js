google.maps.event.addDomListener(window, 'load', init);
var map;
function init() {
    var mapOptions = allMapOptions;
    var mapElement = document.getElementById('stats-home-map');
    var map = new google.maps.Map(mapElement, mapOptions);
    var locations = [

    ];
    for (i = 0; i < locations.length; i++) {
        if (locations[i][1] =='undefined'){ description ='';} else { description = locations[i][1];}
        if (locations[i][2] =='undefined'){ telephone ='';} else { telephone = locations[i][2];}
        if (locations[i][3] =='undefined'){ email ='';} else { email = locations[i][3];}
       if (locations[i][4] =='undefined'){ web ='';} else { web = locations[i][4];}
       if (locations[i][7] =='undefined'){ markericon ='';} else { markericon = locations[i][7];}
        marker = new google.maps.Marker({
            icon: markericon,
            position: new google.maps.LatLng(locations[i][5], locations[i][6]),
            map: map,
            title: locations[i][0],
            desc: description,
            tel: telephone,
            email: email,
            web: web
        });
        link = '';
    }

    geocoder = new google.maps.Geocoder();

    for (i = 0; i < localNames.length - 1; i++) {
        console.log(i);
        geocoder.geocode( { 'address': localNames[i]}, function(results, status)
        {
            if (status == google.maps.GeocoderStatus.OK)
            {
                addMarker(results[0], map);
            } else if (status = google.maps.GeocoderStatus.ZERO_RESULTS) {
                geocoder.geocode( { 'address': countryNames[i]}, function(results, status)
                    {
                        if (status == google.maps.GeocoderStatus.OK)
                        {
                            addMarker(results[0], map);
                        } else {
                            console.log("Geocode was not successful for the following reason: " + status);
                        }
                    });
            }
            else
            {
                console.log("Geocode was not successful for the following reason: " + status);
            }
        });
    }

}

function addMarker(result, map) {
    var infowindow = new google.maps.InfoWindow({
      content: "Hello there!"
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
        center: new google.maps.LatLng(50.861444,11.136474),
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