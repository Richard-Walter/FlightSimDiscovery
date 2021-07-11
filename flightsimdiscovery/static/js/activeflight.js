var map = getMap();
let user_panned_map = false;
var show_plane_trail = true;
var auto_center = true;
var defaultZoomSet = false;
var updateInterval = 5000;
let updateIntervalID = null;

//create inital user marker info
var userMarkerInfo = null;

//active flight current details dictionary
let af_details = { 'last_update_ms': 0 };


function showActiveFlights() {

  // if ($('#get_active_flights_checkbox').is(':checked')) {
  if ($('#Map_ActiveFlight_Btn').val() == 'on') {

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
    updateIntervalID = setInterval(() => {

      //THis updates cvlient-side active flight details from server side
      updateActiveFlightData(updateMap);

      //get client side details

      //update map
      // update_text = updateMap();

      // if (update_text == "error"){
      //   removeSetInterval("No active flight detected.  Check that you are connected via the in-game Flight Sim Discovery toolbar panel (download at https://www.flightsim.to/) and try again");

      // } else if (update_text == "timestamp_threshold_exceeded")
      //   removeSetInterval("No active flight detected.  Check that you are connected via the in-game Flight Sim Discovery toolbar panel (download at https://www.flightsim.to/) and try again");

    }, 5000);

  } else {

    updateDBShowChecked(false);
    removeActiveFlight();
  }

  //add listener in case user is trying to pan map so we can stop the autocentering when tracking a live flight
  google.maps.event.addListener(map, 'dragend', function (event) {

    if (user_panned_map == false) {
      user_panned_map = true;
      //turn off autocenter if user has manually panned the map
      $('#af_autocenter').click();
    }
  })

}

//updates flask database that notifies other functions that the user wants to track flight
function updateDBShowChecked(showChecked) {

  // console.log(showChecked)
  $.ajax({
    url: "/users/show_active_flight_checkbox",
    method: "POST",
    dataType: "text",
    data: {
      // showChecked: showChecked.toString(),
      showChecked: showChecked
    },
  }).done(function (response) {
    // console.log(response);
  }).fail(function () {
    console.log('couldnt update database to show active flight checked');
  });
}

//Ajax routine to get users active flight
function updateActiveFlightData(callback) {

  console.log("getting active flight data");

  $.ajax({
    url: "/users/get_user_location",
    method: "POST",
    dataType: "text",
    data: { user_id: getUserID() },
  }).success(function (response) {

    console.log("get user location returned data")
    updateAFDict(response);
    callback();

  }).error(function () {
    console.log('AJAX call to get_user_location from database failed.  Cant update database to show active flight checked');
    removeSetInterval("No active flight detected.  Check that you are connected via the Flight Sim Discovery toolbar panel within MSFS and try again");
  });

}

function updateAFDict(response) {

  coordinates = JSON.parse(response);
  if (jQuery.isEmptyObject(coordinates)) {
    console.log("In updateMap - no data.  Probably user has never had an active flight and hasnt go the ingame panel installed")
    af_details['last_update_ms'] = 0;
    return;
  }

  last_update = coordinates['last_update'];
  user_lat = coordinates['lat'];
  user_lng = coordinates['lng'];
  altitude_m = Math.round(coordinates['alt']);
  altitude = Math.round(altitude_m * 3.281);
  ground_speed = Math.round(coordinates['ground_speed']);
  ias = coordinates['ias'];
  heading_true = coordinates['heading_true'];
  last_update_ms = new Date(last_update).getTime();

  //update client side active flight details dictioary
  af_details['last_update'] = last_update;
  af_details['user_lat'] = user_lat;
  af_details['user_lng'] = user_lng;
  af_details['altitude'] = altitude;
  af_details['ground_speed'] = ground_speed;
  af_details['ias'] = ias;
  af_details['heading_true'] = heading_true;
  af_details['last_update_ms'] = last_update_ms;
}

function getAFDetails() {
  return af_details;
}

//stop tracking flight and remove marker/trail from map
function removeActiveFlight() {

  console.log("removing active flight")

  if (userMarkerInfo.marker) {
    userMarkerInfo.marker.setMap(null);
    userMarkerInfo.marker = null;
  }
  if (userMarkerInfo.poly) {
    userMarkerInfo.poly.setMap(null);
    userMarkerInfo.poly = null;
  }

  userMarkerInfo = null;
  user_panned_map = false;

  clearInterval(updateIntervalID);

  // $('#get_active_flights_checkbox').prop('checked', false);
  $("#active_flight_flash").hide()
}

//removes continuous calls to update map but leaves marker and plane trail.
function removeSetInterval(flash_message = '', timeout = null) {

  console.log("removing set interval")
  active_flight_flash(flash_message, timeout);
  clearInterval(updateIntervalID);


  // $('.af_options').prop('hidden', true);
  // $('#af_show').click();
  $('#Map_ActiveFlight_Btn').val('off');
  $(".af_btn-text").html('Show Active Flight');
  $(".Map_ActiveFlight").hide();
  user_panned_map = false;

  //need to disconnect form poi audio if playing and hide toggle button
  $("#poi_audio_div").attr("hidden",true)
  $('.pa_toolbar').addClass("d-none");
  $('.pa_toolbar').removeClass("d-flex");
  $('#af_poi_audio').val('off');
  $("#af_poi_audio").removeAttr("checked");
  pa_disconnect();

 
}

//update map active flight marker, text and line.
function updateMap() {

  last_update = af_details['last_update'];
  user_lat = af_details['user_lat'];
  user_lng = af_details['user_lng'];
  altitude = af_details['altitude'];
  ground_speed = af_details['ground_speed'];
  ias = af_details['ias'];
  heading_true = af_details['heading_true'];
  last_update_ms = af_details['last_update_ms'];
  current_date_ms = Date.now();
  diff_millis = current_date_ms - last_update_ms;
  // console.log(`seconds elapsed = ${Math.floor(diff_millis / 1000)}`);

  //check timestamp to see if flight data is being update from msfs
  if (diff_millis > 9000) {
    console.log('timestamp has not been updated for at least 9s')

    removeSetInterval("No active flight detected.  Check that you are connected via the in-game Flight Sim Discovery toolbar panel (download at https://www.flightsim.to/) and try again");
    return;
  }


  //We have an active flight that is being updated!
  active_flight_flash("Tracking active flight");
  $('#poi_audio_div').removeAttr('hidden');


  //create new user marker and plane trail if one doesnt already exist and info box if user wants
  if (userMarkerInfo.marker == null) {
    userMarkerInfo.marker = createNewUserMarker(user_lat, user_lng, ground_speed, heading_true, map);
    userMarkerInfo.poly = createUserPlaneTrail(user_lat, user_lng, map);

  } else {

    //update location of existing marker
    userMarkerInfo.marker.setPosition(new google.maps.LatLng(user_lat, user_lng));
    var icon = marker.getIcon();
    icon.rotation = heading_true;
    marker.setIcon(icon);

    //update label
    var label = userMarkerInfo.marker.getLabel();
    label.text = ground_speed.toString() + 'kts  ' + altitude.toString() + 'ft';;
    userMarkerInfo.marker.setLabel(label);

    //update user plane trail
    if (userMarkerInfo.poly != null) {
      if (show_plane_trail == false) {
        //clear trail
        userMarkerInfo.poly.setMap(null);
        // userMarkerInfo.poly = null;
      } else {
        //re-add poly to map if null
        if (userMarkerInfo.poly.map == null) {
          poly.setMap(map);
        }
        const path = userMarkerInfo.poly.getPath();
        // Because path is an MVCArray, we can simply append a new coordinate and it will automatically appear.
        path.push(new google.maps.LatLng(user_lat, user_lng));
      }
    } else {
      if (show_plane_trail == true) {
        //create trail
        userMarkerInfo.poly = createUserPlaneTrail(user_lat, user_lng, map);
      }
    }



    // return marker;
  }

  // auto pan to map only if user hasn't manually pan map previous
  if (user_panned_map == false) {
    if (auto_center == true) {
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

function createNewUserMarker(user_lat, user_lng, ground_speed, heading_true, map) {

  label_txt = ground_speed.toString() + 'kts  ' + altitude.toString() + 'ft';
  marker = new google.maps.Marker({

    position: new google.maps.LatLng(user_lat, user_lng),
    icon: {
      // url:'/static/img/marker/user_marker_airplane1.png', //Marker icon.
      path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,//Marker icon.
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
    label: {
      text: label_txt,
      fontSize: "14px",
      fontWeight: "bold",
      color: 'black',
      // fontFamily: '"Courier New", Courier,Monospace',
    },
    opacity: 0.8,

  });
  return marker;
}

function createUserPlaneTrail(user_lat, user_lng, map) {

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

function active_flight_flash(display_text, timeout = null) {

  //remove info flash html
  $('#tips-and-tricks_flash').hide();

  $('#active_flight_flash_text').text(display_text);
  $("#active_flight_flash").show();
  if (timeout) {
    setTimeout(function () { $("#active_flight_flash").hide(); }, timeout);
  }
}

//handles and distributes events from the active flight panel on the map
function activeFlightPanelHandler(e) {

  element_target = e.target;
  element_id = element_target.id;
  element_value = element_target.value;

  if (element_id == "af_show") {



    if (element_value == "off") {
      element_target.value = "on";
      $('.af_options').removeProp('hidden');
      showActiveFlights();

    } else {
      $('.af_options').prop('hidden', true);
      element_target.value = "off";
      removeActiveFlight();
    }

  } else if (element_id == "af_autocenter") {
    if (element_value == "off") {
      element_target.value = "on";
      auto_center = true;
      user_panned_map = false;
    } else {
      element_target.value = "off";
      auto_center = false;
    }
  } else if (element_id == "af_show_trail") {
    if (element_value == "off") {
      element_target.value = "on";
      show_plane_trail = true;
    } else {
      element_target.value = "off";
      show_plane_trail = false;
      if (userMarkerInfo.poly != null) {
        //clear trail
        userMarkerInfo.poly.setMap(null);
        // userMarkerInfo.poly = null;
      }
    }

  } else if (element_id == "af_poi_audio") {

    if (element_value == "off") {
      element_target.value = "on";
    } else {
      element_target.value = "off";
    }
    activeFlightPoiAudio(element_target.value);

  } 

}

//handler for in-flight audio
function activeFlightPoiAudio(show_flag) {

  if (show_flag == 'on') {
    
    $('.pa_toolbar').removeClass("d-none");
    $('.tips-and-tricks').addClass("d-none");
    map.controls[google.maps.ControlPosition.TOP_CENTER].pop(searchPOIDiv);
    map.controls[google.maps.ControlPosition.TOP_CENTER].push(paToolbarDiv);

    pa_init();

  } else {
    // $('.pa_toolbar').addClass("d-none");
    map.controls[google.maps.ControlPosition.TOP_CENTER].pop(paToolbarDiv);
    map.controls[google.maps.ControlPosition.TOP_CENTER].push(searchPOIDiv);
    pa_disconnect();
  }
}



