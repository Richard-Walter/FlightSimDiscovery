var flightPath_data = []

function saveFlightPlan(document, flightPath_data) {

    filename = 'flight_plan.pln';
    content = buildFlightPlan(flightPath_data);
   
    const a = document.createElement('a');
    const file = new Blob([content], {type: 'text/plain'});
    
    a.href= URL.createObjectURL(file);
    a.download = filename;
    a.click();
    
    URL.revokeObjectURL(a.href);

}


function buildFlightPlan(flightPath_data) {

    var content = '';
    const title_txt = 'Custom departure to Custom Arrival';
    const crusing_altitude = '8500.000';

    const departure_id = 'CUSTD';
    const dep_lat = convertDDToDMS(flightPath_data[0]['latLng'][0], "90", 2);
    const dep_lng = convertDDToDMS(flightPath_data[0]['latLng'][1], "180", 2);
    const departure_lla = dep_lat + ','+ dep_lng + `,+${crusing_altitude}`;

    const destination_id = 'CUSTA';
    const dest_lat = convertDDToDMS(flightPath_data[flightPath_data.length-1]['latLng'][0], "90", 2);
    const dest_lng = convertDDToDMS(flightPath_data[flightPath_data.length-1]['latLng'][1], "180", 2);
    const destination_lla = dest_lat + ','+ dest_lng + `,+${crusing_altitude}`;

    const description = `Custom departure to Custom Arrival`;
    const departure_name = `Custom departure`;
    const destination_name = `Custom Arrival`;

    const header =          '<?xml version="1.0" encoding="UTF-8"?>\n' +
                            '\n'+
                            '<SimBase.Document Type="AceXML" version="1,0">\n'+
                            '    <Descr>AceXML Document</Descr>\n'+
                            '    <FlightPlan.FlightPlan>\n';
    const title =           `        <Title>${title_txt}</Title>` + '\n';
    const FPTType =         `        <FPType>VFR</FPType>` + '\n';
    const CruisingAlt =     `        <CruisingAlt>${crusing_altitude}</CruisingAlt>` + '\n';
    const DepartureID =     `        <DepartureID>${departure_id}</DepartureID>` + '\n';
    const DepartureLLA =    `        <DepartureLLA>${departure_lla}</DepartureLLA>` + '\n';
    const DestinationID =   `        <DestinationID>${destination_id}</DestinationID>` + '\n';
    const DestinationLLA =  `        <DestinationLLA>${destination_lla}</DestinationLLA>` + '\n';
    const Descr =           `        <Descr>${description}</Descr>` + '\n';
    const DepartureName =   `        <DepartureName>${departure_name}</DepartureName>` + '\n';
    const DestinationName = `        <DestinationName>${destination_name}</DestinationName>` + '\n';
    const app_details =     '        <AppVersion>\n' +
                            '            <AppVersionMajor>11</AppVersionMajor>\n' +
                            '            <AppVersionBuild>282174</AppVersionBuild>\n' +
                            '        </AppVersion>\n'
    const footer =          '    </FlightPlan.FlightPlan>\n' +
                            '</SimBase.Document>\n'

    content += header + title + FPTType + CruisingAlt + DepartureID + DepartureLLA + DestinationID + DestinationLLA + Descr + 
                DepartureName + DestinationName + app_details + buildATCWapoints(flightPath_data, crusing_altitude) + footer;


    console.log(content);

    return content;
}

function buildATCWapoints(flightPath_data, crusing_altitude) {

const ATCWaypointType =          '            <ATCWaypointType>User</ATCWaypointType>\n';
    const ATCWaypoint_close =    '        </ATCWaypoint>\n'
    const ICAO_open =            '            <ICAO>\n'
    const ICAO_close =           '            </ICAO>\n'

    var atc_content = ''

    var name;
    var lat;
    var lng;

    for (var i = 0; i < flightPath_data.length; i++) {

        if (i==0) {
            name = 'CUSTD';
        } else if (i ==flightPath_data.length-1) {
            name = 'CUSTA';
        } else {
            name = flightPath_data[i]['waypoint'];
        }
        
        // lat = flightPath_data[i]['latLng'][0];
        // lng = flightPath_data[i]['latLng'][1];
        lat = convertDDToDMS(flightPath_data[i]['latLng'][0], "90", 2);
        lng = convertDDToDMS(flightPath_data[i]['latLng'][1], "180", 2);
        
        
        atc_content += `        <ATCWaypoint id="${name}">` +'\n';
        atc_content += ATCWaypointType;
        atc_content += `            <WorldPosition>${lat},${lng},+${crusing_altitude}</WorldPosition>` +'\n';
        // only build the ICAO section for departure and arrival waypoints
        if ((i == 0) || (i ==flightPath_data.length-1)) {
            atc_content += ICAO_open;
            atc_content += `                <ICAOIdent>${name}</ICAOIdent>`+'\n';
            atc_content += ICAO_close;
        }
        atc_content += ATCWaypoint_close;
    }     

    console.log(atc_content);
    
    return atc_content;
}

function buildFlightPlanModalBody(flightPath_data) {

    console.log(flightPath_data);

    var body_html = "<p>No flight plan created.  Please add at least two waypoints.<br /><br />  Start creating a flight plan by clicking on a Point of Interest and 'add to Flight Plan'.</p>";
    
    if (Array.isArray(flightPath_data) && flightPath_data.length>1) {
        body_html = '<p>We have detected flight plan data</p><br><p>';
        for (var i = 0; i < flightPath_data.length; i++) {
            body_html += flightPath_data[i]['waypoint'] + " --> ";
          }
        body_html = body_html.substring(0, body_html.length-5);  //remove the -->
        body_html += '</p>'
        
    }
        
    return body_html;
}


function convertDDToDMS(
    a, // decimal value (ex. -14.23463)
    b, // boundary; accepts "90" (Latitude) or "180" (Longitude)
    c  // precision for seconds
  ){
    var 
      // get the direction indicator
      H='NSEW'[
        2*(b!=90)      // expressions in brackets are booleans, that get coerced into 0 or 1
        +(a<0)         // is the decimal value less than 0, coerced into 0 or 1
      ],  
      a=(a<0?-a:a)%b,  // convert value to absolute. shorten than Math.abs(a)
                       // also get the modulo of the value and the boundary
  
      D=0|a,          // Degress: get the integer value; like Math.floor(a)
      a=(a-D)*60,     // calulate the rest and multiply by 60
      M=0|a,          // Minutes
      a=(a-M)*60, 
      S=a.toFixed(c); // Seconds
  
      // return formatted values joined by non-breaking space
      return [H+D+'°',M+'′',S+'"'].join('\xA0')
}