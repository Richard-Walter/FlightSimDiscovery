// var flightPath_data = [];
var flightplan_filename = "";

var dep_data;
var dest_data;
var departure_id;
var departure_name;
var dep_lat;
var dep_lng;
var dep_elev;
var departure_lla;

var destination_id;
var destination_name;
var dest_lat;
var dest_lng;
var dest_elev;
var destination_lla;

function exportFlightPlan(flightPath_data) {

  var fp_pois = [];
  flightplan_filename = $("#export-filename-input").val();
  share_flightplan = $('#export-share_fp').is(":checked");
  console.log(share_flightplan);

  // filename = "Flight Sim Discovery " + yyyymmdd() + ".pln";
  cruise_altitude = $("#cruise_altitude_value").val();
  content = buildFlightPlan(flightPath_data, cruise_altitude);

  const a = document.createElement("a");
  const file = new Blob([content], { type: "text/xml" });

  a.href = URL.createObjectURL(file);
  a.download = flightplan_filename + ".pln";
  a.click();

  URL.revokeObjectURL(a.href);

  $('#Flight_plan_modal').modal('hide');

  //mark any POI in exported flight plan as visited
  for (var i = 0; i < flightPath_data.length; i++) {
    waypoint = flightPath_data[i]['waypoint'];
    fp_pois.push(waypoint);
  }

  var postData = {
    fp_pois: fp_pois,
    fp_share: share_flightplan,
    fp_name: flightplan_filename,
    fp_altitude: cruise_altitude
  }

  // send flight plan waypoints and if user wants to share the flight plan with the community
  $.ajax({ 
    url: '/flightplans/export_fp_post', 
    type: 'POST', 
    data: JSON.stringify(postData),
    contentType: "application/json",
    success: function(response) {
      // console.log(response);
    },
    error: function(error) {
        console.log(error);
    }
  })
}

function buildFlightPlan(flightPath_data, cruise_altitude) {
  

  const title_txt = `${departure_id} to ${destination_id}`;
  const description = `${departure_name} to ${destination_name}`;

  // Create the XML document
  var parser = new DOMParser();
  var xmlDoc = parser.parseFromString(
    '<?xml version="1.0" encoding="utf-8"?><SimBase.Document></SimBase.Document>',
    "application/xml"
  );

  //Build the xml nodes and attributes
  var simbase_element = xmlDoc.getElementsByTagName("SimBase.Document");
  simbase_element[0].setAttribute("Type", "AceXML");
  simbase_element[0].setAttribute("version", "1,0");

  var desc_node = xmlDoc.createElement("Descr");
  desc_node.innerHTML = "AceXML Document";
  simbase_element[0].appendChild(desc_node);

  var flightplan_node = xmlDoc.createElement("FlightPlan.FlightPlan");
  simbase_element[0].appendChild(flightplan_node);

  var title_node = xmlDoc.createElement("Title");
  title_node.innerHTML = title_txt;
  flightplan_node.appendChild(title_node);

  var FPType_node = xmlDoc.createElement("FPType");
  FPType_node.innerHTML = "VFR";
  flightplan_node.appendChild(FPType_node);

  // var RouteType_node = xmlDoc.createElement("RouteType");
  // RouteType_node.innerHTML = "LowAlt";
  // flightplan_node.appendChild(RouteType_node);

  var CruisingAlt_node = xmlDoc.createElement("CruisingAlt");
  CruisingAlt_node.innerHTML = cruise_altitude;
  flightplan_node.appendChild(CruisingAlt_node);

  var DepartureID_node = xmlDoc.createElement("DepartureID");
  DepartureID_node.innerHTML = departure_id;
  flightplan_node.appendChild(DepartureID_node);

  var DepartureLLA_node = xmlDoc.createElement("DepartureLLA");
  DepartureLLA_node.innerHTML = departure_lla;
  flightplan_node.appendChild(DepartureLLA_node);

  var DestinationID_node = xmlDoc.createElement("DestinationID");
  DestinationID_node.innerHTML = destination_id;
  flightplan_node.appendChild(DestinationID_node);

  var DestinationLLA_node = xmlDoc.createElement("DestinationLLA");
  DestinationLLA_node.innerHTML = destination_lla;
  flightplan_node.appendChild(DestinationLLA_node);

  var Descr_fp_node = xmlDoc.createElement("Descr");
  Descr_fp_node.innerHTML = description;
  flightplan_node.appendChild(Descr_fp_node);

  var DepartureName_node = xmlDoc.createElement("DepartureName");
  DepartureName_node.innerHTML = departure_name;
  flightplan_node.appendChild(DepartureName_node);

  var DestinationName_node = xmlDoc.createElement("DestinationName");
  DestinationName_node.innerHTML = destination_name;
  flightplan_node.appendChild(DestinationName_node);

  var AppVersion_node = xmlDoc.createElement("AppVersion");
  flightplan_node.appendChild(AppVersion_node);

  var AppVersionMajor_node = xmlDoc.createElement("AppVersionMajor");
  AppVersionMajor_node.innerHTML = "11";
  AppVersion_node.appendChild(AppVersionMajor_node);

  var AppVersionBuild_node = xmlDoc.createElement("AppVersionBuild");
  AppVersionBuild_node.innerHTML = "282174";
  AppVersion_node.appendChild(AppVersionBuild_node);

  buildATCWapoints(
    xmlDoc,
    flightplan_node,
    flightPath_data,
    departure_id,
    departure_lla,
    destination_id,
    departure_lla,
    cruise_altitude
  );

  xmlDoc_string = new XMLSerializer().serializeToString(xmlDoc);
  xml_formatted = formatXml(xmlDoc_string);

  return xml_formatted;
  // return xml_formatted;
}

function buildATCWapoints(
  xmlDoc,
  flightplan_node,
  flightPath_data,
  departure_id,
  departure_lla,
  destination_id,
  destination_lla,
  cruise_altitude
) {
  var ATCWaypoint_node;
  var ATCWaypointType_node;
  var WorldPosition_node;
  var ICAO_node;
  var ICAOIdent_node;

  // build departure

  name = departure_id;
  waypoint_lla = departure_lla;
  waypoint_type = "Airport";
  buildNode(name, waypoint_lla, waypoint_type);
  buildICAO(name);

  // build poi waypoints
  for (var i = 0; i < flightPath_data.length; i++) {

    //first and last POIs if airport or then skip as they will be dpe and dest airports
    if ((i==0) || (i==(flightPath_data.length-1))) {
      if(flightPath_data[i]["category"].includes("Airport")){
        continue;
      }
    }

    name = flightPath_data[i]["waypoint"].trim();
    // name = 'wp' + (i+1).toString();
    lat = convertDDToDMS(flightPath_data[i]["latLng"][0], "90", 2);
    lng = convertDDToDMS(flightPath_data[i]["latLng"][1], "180", 2);
    waypoint_lla = `${lat},${lng},+000000.00`;
    waypoint_type = "User";
    buildNode(name, waypoint_lla, waypoint_type);
  }

  // build destination

  name = destination_id;

  waypoint_lla = destination_lla;
  waypoint_type = "Airport";
  buildNode(name, waypoint_lla, waypoint_type);
  buildICAO(name);

  function buildNode(name, lla, waypoint_type) {
    ATCWaypoint_node = xmlDoc.createElement("ATCWaypoint");
    //NOTE:  DUE TO BUG IN MSFS NOT SHOWING FLIGHT PATH IN G3X and G1000, must truncate to 6 chars
    ATCWaypoint_node.setAttribute("id", `${name.substring(0,6)}`);
    flightplan_node.appendChild(ATCWaypoint_node);

    ATCWaypointType_node = xmlDoc.createElement("ATCWaypointType");
    ATCWaypointType_node.innerHTML = waypoint_type;
    ATCWaypoint_node.appendChild(ATCWaypointType_node);

    WorldPosition_node = xmlDoc.createElement("WorldPosition");
    WorldPosition_node.innerHTML = lla;
    ATCWaypoint_node.appendChild(WorldPosition_node);
  }

  function buildICAO(name) {
    // only build the ICAO section for departure and arrival waypoints
    ICAO_node = xmlDoc.createElement("ICAO");
    ATCWaypoint_node.appendChild(ICAO_node);

    ICAOIdent_node = xmlDoc.createElement("ICAOIdent");
    ICAOIdent_node.innerHTML = `${name}`;
    ICAO_node.appendChild(ICAOIdent_node);
  }
}

function buildFlightPlanModalBody(flightPath_data, fp_name="") {


  if (flightPath_data.length > 0) {
    $('#fp_save_btn').removeAttr('disabled')
    $('#fp_delete_btn').removeAttr('disabled')
  }

  getDepDestAirports(flightPath_data).then(function (json) {

    var body_html;

    body_html =
      "<p>No flight plan created.</p><br><p>Please add at least one waypoint.  On the map, click on a 'Point of Interest' and select 'add to Flight Plan'</p>";

    if (Array.isArray(flightPath_data) && flightPath_data.length > 0) {

      var dep_data = json["dep_airport"];
      var dest_data = json["dest_airport"];

      departure_id = dep_data["ICAO"];
      departure_name = dep_data["Airport_Name"];
      dep_lat = convertDDToDMS(dep_data["lat"], "90", 2);
      dep_lng = convertDDToDMS(dep_data["lon"], "180", 2);
      dep_elev = dep_data["elev"];
      departure_lla = dep_lat + "," + dep_lng + `,+${dep_elev}`;

      destination_id = dest_data["ICAO"];
      destination_name = dest_data["Airport_Name"];
      dest_lat = convertDDToDMS(dest_data["lat"], "90", 2);
      dest_lng = convertDDToDMS(dest_data["lon"], "180", 2);
      dest_elev = dest_data["elev"];
      destination_lla = dest_lat + "," + dest_lng + `,+${dest_elev}`;


      body_html = `<div class="range-slider">
                    <p>Cruise Alitude (ft):</p>
                    <p><input id="cruise_altitude_value" class="range-slider__range" type="range" value="8000" min="1000" max="10000" step="500">
                    <span id="cruise_altitude_value" class="mx-1 mb-1 range-slider__value">0</span></p>
                  </div>`
      // body_html = "<p>";
      body_html += "<p>Departure: " + departure_id + "</p>";
      body_html += "<p class='font-weight-light'>";
      
      for (var i = 0; i < flightPath_data.length; i++) {

        //first and last POIs if airport then skip as they will be dpe and dest airports
        if ((i==0) || (i==(flightPath_data.length-1))) {
          if(flightPath_data[i]["category"].includes("Airport")){
            continue;
          }
        }
          body_html += "&nbsp;&nbsp;-> " + flightPath_data[i]["waypoint"] +"<br>";
      }

      //build flightpath name
      // flightplan_filename = "Flight Sim Discovery " + yyyymmdd();
      if (fp_name == "") {
        flightplan_filename = "FSD - " + departure_id + " to " + destination_id;
      } else {
        flightplan_filename = fp_name
      }

      // body_html = body_html.substring(0, body_html.length - 4); //remove the last -->
      body_html += "</p>";
      body_html += "<p>Destination: " + destination_id + "</p>";
      body_html += "<hr>";
      body_html += "<form>";
      body_html += "<div class='export-filename form-group mt-3'>";
      body_html += "<label class='mr-2' >Flight Plan Name: </label>";
      body_html += '<input required type="text" class="form-control" id="export-filename-input" value="' + flightplan_filename + '">';
      body_html += "</div>";
      body_html += "<div class='form-check mt-2'>";
      body_html += '<input type="checkbox" class="form-check-input" id="export-share_fp" checked>';
      body_html += "<label class='mr-2' >Save & Share Flight Plan</label>";
      body_html += "</div>";
      body_html += "</form>";
      body_html += 

        `<script>
                        
                // flight planner cruise alititude slider
                var rangeSlider = function(){
                  var slider = $('.range-slider'),
                      range = $('.range-slider__range'),
                      value = $('.range-slider__value');
                    
                  slider.each(function(){
                
                    value.each(function(){
                      var value = $(this).prev().attr('value');
                      $(this).html(value);
                    });
                
                    range.on('input', function(){
                      $(this).next(value).html(this.value);
                    });
                  });
                };
                
                rangeSlider();
        </script>`;

    }
    $("#Flight_plan_modal").modal("show");
    $(".flight_plan_modal_body").html(body_html);
  });

  // return body_html;
}

async function getDepDestAirports(flightPath_data) {
  var dep_dest_array = [];

  for (var i = 0; i < flightPath_data.length; i++) {
    airport_name = flightPath_data[i]["waypoint"];
    latlng_array = flightPath_data[i]["latLng"];
    lat = latlng_array[0];
    lng = latlng_array[1];
    coordinate = { airport_name: airport_name, lat: lat, lon: lng };
    dep_dest_array.push(coordinate);
  }

  jsonified_data = JSON.stringify(dep_dest_array);

  // let response = await fetch("/build_flightplan", {
  let response = await fetch("/flightplans/build_flightplan", {
    method: "POST",
    credentials: "include",
    body: jsonified_data,
    cache: "no-cache",
    headers: new Headers({
      "content-type": "application/json;charset=UTF-8",
    }),
  });

  let data = await response.json();
  return data;
}

function convertDDToDMS(
  a, // decimal value (ex. -14.23463)
  b, // boundary; accepts "90" (Latitude) or "180" (Longitude)
  c // precision for seconds
) {
  var // get the direction indicator
    H = "NSEW"[
      2 * (b != 90) + // expressions in brackets are booleans, that get coerced into 0 or 1
        (a < 0) // is the decimal value less than 0, coerced into 0 or 1
    ],
    a = (a < 0 ? -a : a) % b, // convert value to absolute. shorten than Math.abs(a)
    // also get the modulo of the value and the boundary

    D = 0 | a, // Degress: get the integer value; like Math.floor(a)
    a = (a - D) * 60, // calulate the rest and multiply by 60
    M = 0 | a, // Minutes
    a = (a - M) * 60,
    S = a.toFixed(c); // Seconds

  // return formatted values joined by non-breaking space
  return [H + D + "°", M + "'", S + '"'].join(" ");
}

function formatXml(xml) {
  var formatted = "";
  var reg = /(>)(<)(\/*)/g;
  xml = xml.replace(reg, "$1\r\n$2$3");
  var pad = 0;
  jQuery.each(xml.split("\r\n"), function (index, node) {
    var indent = 0;
    if (node.match(/.+<\/\w[^>]*>$/)) {
      indent = 0;
    } else if (node.match(/^<\/\w/)) {
      if (pad != 0) {
        pad -= 1;
      }
    } else if (node.match(/^<\w[^>]*[^\/]>.*$/)) {
      indent = 1;
    } else {
      indent = 0;
    }

    var padding = "";
    for (var i = 0; i < pad; i++) {
      padding += "  ";
    }

    formatted += padding + node + "\r\n";
    pad += indent;
  });

  return formatted;
}

function yyyymmdd() {
  var now = new Date();
  var y = now.getFullYear();
  var m = now.getMonth() + 1;
  var d = now.getDate();
  var mm = m < 10 ? "0" + m : m;
  var dd = d < 10 ? "0" + d : d;
  return "" + y + mm + dd;
}
