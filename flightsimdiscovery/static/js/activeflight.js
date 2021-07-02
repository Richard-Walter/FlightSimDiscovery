// initial variables
var user_id = getUserID();
var map = getMap();
var user_panned_map = false;
var defaultZoomSet = false;
var updateInterval = 5000;
var updateIntervalID = null;

//create inital user marker info
var userMarkerInfo = null;



// var ajaxUserMarkerObj = { //Object to save cluttering the namespace.

//   options: {
//       type: 'POST',
//       url: "/users/get_user_location", //The resource that delivers loc data.
//       dataType: "text", //The type of data tp be returned by the server.
//       data: {user_id: user_id},
//   },

//   delay: 5000, // 5s the interval between successive gets.
//   errorCount: 0, //running total of ajax errors.
//   errorThreshold: 3, //the number of ajax errors beyond which the get cycle should cease.
//   ticker: null, //setTimeout reference - allows the get cycle to be cancelled with clearTimeout(ajaxUserMarkerObj.ticker);

//   get: function () { //a function which initiates

//       if (ajaxUserMarkerObj.errorCount < ajaxUserMarkerObj.errorThreshold) {
//          ajaxUserMarkerObj.ticker = setTimeout(getActiveFlightData, ajaxUserMarkerObj.delay);
//       } else {
//         console.log("tried to get active flight 3 times.  stopping now.  errorCount is:  ");
//         console.log(ajaxUserMarkerObj.errorCount);
//         // active_flight_flash("No active flight detected", false);
//         //rest error count in case user
//         ajaxUserMarkerObj.errorCount = 0;
//         clearTimeout(ajaxUserMarkerObj.ticker);
//         $('#get_active_flights_checkbox').prop('checked', false);
//         active_flight_flash("Cannot establish a connection to the server.  Please try again later", false);
//       }
//   },

//   fail: function (errorThrown) {

//       console.log('ajax error occured:   ' + errorThrown);
//       ajaxUserMarkerObj.errorCount++;
//       // active_flight_flash("No active flight detected", false);
//   }
// };



//checkbox on main web page
$("#get_active_flights_checkbox").click(function() {

    if ($('#get_active_flights_checkbox').is(':checked')) {
        
      user_panned_map = false;

      //reset marker info if user disconnected
      if (userMarkerInfo == null) {
        userMarkerInfo = {
          id: user_id,
          map: map,
          marker: null,
          poly: null
        }
      }

      updateDBShowChecked(true);
      active_flight_flash("Establishing connection...please wait", 15000);

      // //GET ACTIVE FLIGHT DATA FROM DATABASE EVERY 5S
      updateIntervalID =setInterval(() => {
          getActiveFlightData();
      }, 5000 );

    } else {
        
        updateDBShowChecked(false);
        removeActiveFlight();
    }

    //add listener in case user is trying to pan map so we can stop the autocentering when tracking a live flight
    google.maps.event.addListener(map, 'dragend', function (event) {
      
      user_panned_map=true;
      
    })
  
});

//updates flask database that notifies other functions that the user wants to track flight
function updateDBShowChecked(showChecked){

  // console.log(showChecked)
  $.ajax({
    url: "/users/show_active_flight_checkbox",
    method:"POST", 
    dataType: "text",
    data: {
      // showChecked: showChecked.toString(),
      showChecked: showChecked
    },
    }).done(function(response) {
      console.log(response);
    }).fail(function(){
      console.log('couldnt update database to show active flight checked');
   });
}

//Ajax routine to get users active flight
function getActiveFlightData() {

  console.log("getting active flight data");
  
  $.ajax({
    url: "/users/get_user_location",
    method:"POST", 
    dataType: "text",
    data: {user_id: user_id},
  }).done(function(response) {

      console.log("get user location returned data")

      update_text = updateMap(response);

      if (update_text == "error"){
        removeSetInterval("No active flight detected.  Check that you connected via the Flight Sim Discovery toolbar panel within MSFS and try again");
        
      } else if (update_text == "timestamp_threshold_exceeded")
        removeSetInterval("No active flight detected.  Check that you connected via the Flight Sim Discovery toolbar panel within MSFS and try again");

    }).fail(function(){
      console.log('AJAX call to get_user_location from database failed.  Cant update database to show active flight checked');
      removeSetInterval("No active flight detected.  Check that you connected via the Flight Sim Discovery toolbar panel within MSFS and try again");
  });

  // $.ajax(ajaxUserMarkerObj.options)
  //     .done(updateMap) //fires when ajax returns successfully
  //     .fail(ajaxUserMarkerObj.fail) //fires when an ajax error occurs
  //     .always(ajaxUserMarkerObj.get); //fires after ajax success or ajax error
}

//stop tracking flight and remove marker/trail from map
function removeActiveFlight(){
   
    console.log("removing active flight")

    if(userMarkerInfo.marker) {
        userMarkerInfo.marker.setMap(null);
        userMarkerInfo.marker = null;
    }
    if(userMarkerInfo.poly) {
        userMarkerInfo.poly.setMap(null);
        userMarkerInfo.poly = null;
    }

    userMarkerInfo = null;
    user_panned_map=false;
    
    clearInterval(updateIntervalID);

    $('#get_active_flights_checkbox').prop('checked', false);
    $("#active_flight_flash").hide()
}

//removes continuous calls to update map but leaves marker and plane trail.
function removeSetInterval(flash_message='', timeout=null) {

  console.log("removing set interval")
  clearInterval(updateIntervalID);
  $('#get_active_flights_checkbox').prop('checked', false);
  user_panned_map=false;
  active_flight_flash(flash_message, timeout);
}

//update map active flight marker, text and line.
function updateMap(data) {

  coordinates = JSON.parse(data);
  if (jQuery.isEmptyObject(data)) {
    console.log("In updateMap - no data.  Probably no active flight")
    return "error"
  }
  
  last_update = coordinates['last_update'];
  user_lat = coordinates['lat'];
  user_lng = coordinates['lng'];
  altitude_m = Math.round(coordinates['alt']);
  altitude = Math.round(altitude_m*3.28);
  ground_speed = Math.round(coordinates['ground_speed']);

  ias = coordinates['ias'];
  heading_true = coordinates['heading_true'];

  label_txt = ground_speed.toString() + 'kts  ' + altitude.toString() + 'ft';

  var last_update_ms = new Date(last_update).getTime();
  var current_date_ms = Date.now();
  const diff_millis = current_date_ms - last_update_ms;
  console.log(`seconds elapsed = ${Math.floor(diff_millis / 1000)}`);

  //check timestamp to see if flight data is being update from msfs
  if (diff_millis > 9000) {
    console.log('timestamp has not been updated for at least 9s' )

    return "timestamp_threshold_exceeded"
  }

  //We have an active flight that is being updated!
  active_flight_flash("Tracking active flight");

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

    //update label
    var label = userMarkerInfo.marker.getLabel();
    label.text = label_txt;
    userMarkerInfo.marker.setLabel(label);


    //update user plane trail
    const path = userMarkerInfo.poly.getPath();
    // Because path is an MVCArray, we can simply append a new coordinate and it will automatically appear.
    path.push(new google.maps.LatLng(user_lat, user_lng));

    // return marker;
  }
  
  // auto pan to map only if user hasn't manuall pan map previous
  if (user_panned_map == false) {
    map.panTo(userMarkerInfo.marker.getPosition());
  }
  
  //only do this intitally-let user decide afterwards
  if (defaultZoomSet == false) {
    map.setZoom(9);
    defaultZoomSet = true;
  }

  return "success"

  // active_flight_flash("Tracking active flight");
  
}


function createNewUserMarker(user_lat,user_lng, ground_speed, heading_true, map) {

  label_txt = ground_speed.toString() + 'kts  ' + altitude.toString() + 'ft';
  marker = new google.maps.Marker({

    position: new google.maps.LatLng(user_lat, user_lng),
    icon: {
          // url:'/static/img/marker/user_marker_airplane1.png', //Marker icon.
          path:google.maps.SymbolPath.FORWARD_CLOSED_ARROW,//Marker icon.
          fillColor: "blue",
          fillOpacity: 0.8,
          scale: 5,
          strokeWeight: 1,
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
    strokeColor: "blue",
    // strokeColor: "#000000",
    strokeOpacity: 0.8,
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

function active_flight_flash(display_text, timeout=null) {

    //remove info flash html
    $('#tips-and-tricks_flash').hide();

    $('#active_flight_flash_text').text(display_text);
    $("#active_flight_flash").show();
    if (timeout) {
      setTimeout(function() { $("#active_flight_flash").hide(); }, timeout);
    }
}

function testFunction(){
  alert("YES")
}