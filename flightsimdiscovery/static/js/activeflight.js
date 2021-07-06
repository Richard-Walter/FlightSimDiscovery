// initial variables
// var user_id = getUserID();
var map = getMap();
let user_panned_map = false;
var show_plane_trail = true;
var auto_center = true;
var defaultZoomSet = false;
var updateInterval = 5000;
let updateIntervalID = null;

//create inital user marker info
var userMarkerInfo = null;


// //checkbox on main web page
// $("#get_active_flights_checkbox").click(function() {

//     if ($('#get_active_flights_checkbox').is(':checked')) {
        
//       user_panned_map = false;

//       //reset marker info if user disconnected
//       if (userMarkerInfo == null) {
//         userMarkerInfo = {
//           id: getUserID(),
//           map: map,
//           marker: null,
//           poly: null
//         }
//       }

//       updateDBShowChecked(true);
//       active_flight_flash("Establishing connection...please wait", 15000);

//       // //GET ACTIVE FLIGHT DATA FROM DATABASE EVERY 5S
//       updateIntervalID =setInterval(() => {
//           getActiveFlightData();
//       }, 5000 );

//     } else {
        
//         updateDBShowChecked(false);
//         removeActiveFlight();
//     }

//     //add listener in case user is trying to pan map so we can stop the autocentering when tracking a live flight
//     google.maps.event.addListener(map, 'dragend', function (event) {
      
//       if (user_panned_map==false) {
//         user_panned_map=true;
//         //turn off autocenter if user has manually panned the map
//         $('#af_autocenter').click();
//       } 
//     })
  
// });

function showActiveFlights() {

  
  // if ($('#get_active_flights_checkbox').is(':checked')) {
  if($('#af_show').val()=='on'){
        
    user_panned_map = false;

    //reset marker info if user disconnected
    if (userMarkerInfo == null) {
      userMarkerInfo = {
        id: getUserID(),
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
    
    if (user_panned_map==false) {
      user_panned_map=true;
      //turn off autocenter if user has manually panned the map
      $('#af_autocenter').click();
    } 
  })

}

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
      // console.log(response);
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
    data: {user_id: getUserID()},
  }).done(function(response) {

      console.log("get user location returned data")

      update_text = updateMap(response);

      if (update_text == "error"){
        removeSetInterval("No active flight detected.  Check that you are connected via the in-game Flight Sim Discovery toolbar panel (download at https://www.flightsim.to/) and try again");
        
      } else if (update_text == "timestamp_threshold_exceeded")
        removeSetInterval("No active flight detected.  Check that you are connected via the in-game Flight Sim Discovery toolbar panel (download at https://www.flightsim.to/) and try again");

    }).fail(function(){
      console.log('AJAX call to get_user_location from database failed.  Cant update database to show active flight checked');
      removeSetInterval("No active flight detected.  Check that you are connected via the Flight Sim Discovery toolbar panel within MSFS and try again");
  });

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

    // $('#get_active_flights_checkbox').prop('checked', false);
    $("#active_flight_flash").hide()
}

//removes continuous calls to update map but leaves marker and plane trail.
function removeSetInterval(flash_message='', timeout=null) {

  console.log("removing set interval")
  clearInterval(updateIntervalID);
  // $('#get_active_flights_checkbox').prop('checked', false);
  $('.af_options').prop('hidden', true);
  $('#af_show').click();
  $('#af_show').val('off');

  user_panned_map=false;
  active_flight_flash(flash_message, timeout);
}

//update map active flight marker, text and line.
function updateMap(data) {

  coordinates = JSON.parse(data);
  if (jQuery.isEmptyObject(coordinates)) {
    console.log("In updateMap - no data.  Probably user has never had an active flight and hasnt go the ingame panel installed")
    return "error"
  }
  
  last_update = coordinates['last_update'];
  user_lat = coordinates['lat'];
  user_lng = coordinates['lng'];
  altitude_m = Math.round(coordinates['alt']);
  altitude = Math.round(altitude_m*3.281);
  ground_speed = Math.round(coordinates['ground_speed']);

  ias = coordinates['ias'];
  heading_true = coordinates['heading_true'];

  label_txt = ground_speed.toString() + 'kts  ' + altitude.toString() + 'ft';

  var last_update_ms = new Date(last_update).getTime();
  var current_date_ms = Date.now();
  const diff_millis = current_date_ms - last_update_ms;
  // console.log(`seconds elapsed = ${Math.floor(diff_millis / 1000)}`);

  //check timestamp to see if flight data is being update from msfs
  if (diff_millis > 9000) {
    console.log('timestamp has not been updated for at least 9s' )

    return "timestamp_threshold_exceeded"
  }

  //We have an active flight that is being updated!
  active_flight_flash("Tracking active flight");

  //create new user marker and plane trail if one doesnt already exist and info box if user wants
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
    if (userMarkerInfo.poly!= null){
      if (show_plane_trail==false) {
        //clear trail
        userMarkerInfo.poly.setMap(null);
        // userMarkerInfo.poly = null;
      } else{
        //re-add poly to map if null
        if (userMarkerInfo.poly.map == null){
          poly.setMap(map);
        }
        const path = userMarkerInfo.poly.getPath();
        // Because path is an MVCArray, we can simply append a new coordinate and it will automatically appear.
        path.push(new google.maps.LatLng(user_lat, user_lng));
      }
    } else {
      if (show_plane_trail==true) {
       //create trail
       userMarkerInfo.poly = createUserPlaneTrail(user_lat,user_lng, map);
      }
    }
    


    // return marker;
  }
  
  // auto pan to map only if user hasn't manually pan map previous
  if (user_panned_map == false){
    if(auto_center==true) {
      map.panTo(userMarkerInfo.marker.getPosition());
    }
  }
  
  //only do this intitally-let user decide afterwards
  if (defaultZoomSet == false) {
    map.setZoom(10);
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
          
          labelOrigin: new google.maps.Point(0, 13),
          anchor: new google.maps.Point(0, 2),

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

function active_flight_flash(display_text, timeout=null) {

    //remove info flash html
    $('#tips-and-tricks_flash').hide();

    $('#active_flight_flash_text').text(display_text);
    $("#active_flight_flash").show();
    if (timeout) {
      setTimeout(function() { $("#active_flight_flash").hide(); }, timeout);
    }
}

//handles and distributes events from the active flight panel on the map
function activeFlightPanelHandler(e){

  element_target = e.target;
  element_id = element_target.id;
  element_value = element_target.value;
  
  if (element_id == "af_show") {



    if (element_value=="off"){
      element_target.value="on";
      $('.af_options').removeProp('hidden');
      showActiveFlights();

    } else {
      $('.af_options').prop('hidden', true);
      element_target.value="off";
      removeActiveFlight();
    }

  } else if (element_id == "af_autocenter") {
    if (element_value=="off"){
      element_target.value="on";
      auto_center=true;
      user_panned_map=false;
    } else {
      element_target.value="off";
      auto_center=false;
    }
  } else if (element_id == "af_show_trail") {
    if (element_value=="off"){
      element_target.value="on";
      show_plane_trail = true;
    } else {
      element_target.value="off";
      show_plane_trail = false;
      if (userMarkerInfo.poly!= null){
        //clear trail
        userMarkerInfo.poly.setMap(null);
        // userMarkerInfo.poly = null;
      }
    }
    
  } else if (element_id == "af_poi_audio") {

    if (element_value=="off"){
      element_target.value="on";
    } else {
      element_target.value="off";
    }
    activeFlightPoiAudio(element_target.value);
  }
  
}
 
//handler for in-flight audio
function activeFlightPoiAudio(show_flag){

  if (show_flag=='on'){
    alert('POI audio is coming soon');

  }
}