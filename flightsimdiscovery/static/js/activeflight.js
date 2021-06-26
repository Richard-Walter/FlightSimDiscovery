var user_id = getUserID();
var map = getMap();
var defaultZoomSet = false;

//create inital user marker info
userMarkerInfo = {
  id: user_id,
  map: map,
  marker: null,
  poly: null
}

var ajaxUserMarkerObj = { //Object to save cluttering the namespace.

  options: {
      type: 'POST',
      url: "/users/get_user_location", //The resource that delivers loc data.
      dataType: "text", //The type of data tp be returned by the server.
      data: {user_id: user_id},
  },

  delay: 5000, // 5s the interval between successive gets.
  errorCount: 0, //running total of ajax errors.
  errorThreshold: 2, //the number of ajax errors beyond which the get cycle should cease.
  ticker: null, //setTimeout reference - allows the get cycle to be cancelled with clearTimeout(ajaxUserMarkerObj.ticker);

  get: function () { //a function which initiates

      if (ajaxUserMarkerObj.errorCount < ajaxUserMarkerObj.errorThreshold) {
         ajaxUserMarkerObj.ticker = setTimeout(getActiveFlightData, ajaxUserMarkerObj.delay);
      } else {
        console.log("tried to get active flight 3 times.  stopping now");
        active_flight_flash("No active flight detected");
        // $('#get_active_flights_checkbox').prop('checked', false);
      }
  },

  fail: function (jqXHR, textStatus, errorThrown) {

      console.log(errorThrown);
      ajaxUserMarkerObj.errorCount++;
  }
};

//
$("#get_active_flights_checkbox").click(function() {

    if ($('#get_active_flights_checkbox').is(':checked')) {
        // $('#get_active_flights_checkbox').prop('checked', false);
        getActiveFlightData();

    }
    else {
        // $('#get_active_flights_checkbox').prop('checked', true);
        
        removeActiveFlight();
    }
});

//stop tracking flight and remove marker/trail from map
function removeActiveFlight(){

    
    console.log("removing active flight")

    if(userMarkerInfo.marker) {
        userMarkerInfo.marker.setMap(null);
    }
    if(userMarkerInfo.poly) {
        userMarkerInfo.poly.setMap(null);
    }
    clearTimeout(ajaxUserMarkerObj.ticker);
    $("#active_flight_flash").hide()
}

//Ajax routine to get users active flight
function getActiveFlightData() {


  $.ajax(ajaxUserMarkerObj.options)
      .done(updateUserMarker) //fires when ajax returns successfully
      .fail(ajaxUserMarkerObj.fail) //fires when an ajax error occurs
      .always(ajaxUserMarkerObj.get); //fires after ajax success or ajax error
}

function updateUserMarker(data) {

  // alert(data)
  coordinates = JSON.parse(data);
  if (jQuery.isEmptyObject(data)) {
    console.log("no active flight")
    active_flight_flash("No connection with MSFS.  Please login into FSD from within MSFS via the FSD toolbar panel.");
    ajaxUserMarkerObj.errorCount = ajaxUserMarkerObj.errorThreshold;
    return
  }
  
  last_update = coordinates['last_update'];
  user_lat = coordinates['lat'];
  user_lng = coordinates['lng'];
  altitude_m = Math.round(coordinates['alt']);
  altitude = Math.round(coordinates['alt']);
  ground_speed = Math.round(coordinates['ground_speed']);

  ias = coordinates['ias'];
  heading_true = coordinates['heading_true'];

  var last_update_ms = new Date(last_update).getTime();
  var current_date_ms = Date.now();
  const diff_millis = current_date_ms - last_update_ms;
  console.log(`seconds elapsed = ${Math.floor(diff_millis / 1000)}`);

  //check timestamp to see if flight data is being update from msfs
  if (diff_millis > 9000) {
    active_flight_flash("No connection with MSFS.  Please login into FSD from within MSFS via the FSD toolbar panel.");
    ajaxUserMarkerObj.errorCount = ajaxUserMarkerObj.errorThreshold;
    return
  }

  //create new user marker and plane trail if one doesnt already exist and info box
  if (userMarkerInfo.marker == null) {
    userMarkerInfo.marker = createNewUserMarker(user_lat,user_lng, ground_speed, heading_true, map);
    userMarkerInfo.poly = createUserPlaneTrail(user_lat,user_lng, map);

  } else {
    //update location of existing marker
    userMarkerInfo.marker.setPosition(new google.maps.LatLng(user_lat, user_lng));
    var icon = marker.getIcon();
    icon.rotation = heading_true;
    marker.setIcon(icon);

    //update user plane trail
    const path = userMarkerInfo.poly.getPath();
    // Because path is an MVCArray, we can simply append a new coordinate and it will automatically appear.
    path.push(new google.maps.LatLng(user_lat, user_lng));

    // return marker;
  }
  
  map.panTo(userMarkerInfo.marker.getPosition());
  
  //only do this intitally-let user decide afterwards
  if (defaultZoomSet == false) {
    map.setZoom(9);
    defaultZoomSet = true;
  }

  active_flight_flash("Tracking active flight");
  
}


function createNewUserMarker(user_lat,user_lng, ground_speed, heading_true, map) {

  label_txt = ground_speed.toString() + 'kts  ' + altitude.toString() + 'ft';
  marker = new google.maps.Marker({

    position: new google.maps.LatLng(user_lat, user_lng),
    icon: {
          // url:'/static/img/marker/user_marker_airplane1.png', //Marker icon.
          path:google.maps.SymbolPath.FORWARD_CLOSED_ARROW,//Marker icon.
          scale: 5,
          strokeWeight: 2,
          strokeColor: '#000',
          // strokeColor: '#00F',
          
          labelOrigin: new google.maps.Point(0, 15),

          // url:'/static/img/marker/user_marker_airplane1.png', //Marker icon.
          // labelOrigin: new google.maps.Point(12, 45),
          rotation: heading_true,
          },
    map: map,
    label:{
            text:label_txt,
            fontSize: "14px",
            fontWeight: "bold",
            color:'black',
            // fontFamily: '"Courier New", Courier,Monospace',
          },
    opacity:0.8,

  });
  return marker;
}

function createUserPlaneTrail(user_lat,user_lng, map) {

  // This converts a polyline to a dashed line, by setting the opacity of the polyline to 0,
  // and drawing an opaque symbol at a regular interval on the polyline.
  const lineSymbol = {
    path: "M 0,-1 0,1",
    strokeOpacity: 1,
    scale: 2,
  };

  label_txt = user_lat.toFixed(2).toString() + ' , ' + user_lng.toFixed(2).toString()
  poly = new google.maps.Polyline({
    path: [
      { lat: user_lat, lng: user_lng },
    ],
    strokeColor: "#000000",
    strokeOpacity: 0,
    strokeWeight: 3,
    icons: [
      {
        icon: lineSymbol,
        offset: "0",
        repeat: "10px",
      },
    ],
  });
  poly.setMap(map);

  return poly;

}

function active_flight_flash(display_text) {

    //remove info flash html
    $('#tips-and-tricks_flash').hide();

    $('#active_flight_flash_text').text(display_text);
    $("#active_flight_flash").show();
      setTimeout(function() { $("#active_flight_flash").hide(); }, 10000);
}