var flightPath_data = []

function saveFlightPlan(document, flightPath_data) {

    filename = 'flight_plan.pln';
    content = buildFlightPlan(flightPath_data);
   
    const a = document.createElement('a');
    const file = new Blob([content], {type: 'text/xml'});
    
    a.href= URL.createObjectURL(file);
    a.download = filename;
    a.click();
    
    URL.revokeObjectURL(a.href);

}

function buildFlightPlan(flightPath_data) {

    var content = '';
    const title_txt = 'Custom departure to Custom Arrival';
    const crusing_altitude = '008500.00';

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

    // Create the XML document
    var parser = new DOMParser();
    var xmlDoc = parser.parseFromString('<?xml version="1.0" encoding="utf-8"?><SimBase.Document></SimBase.Document>', "application/xml");

    //Build the xml nodes and attributes
    var simbase_element = xmlDoc.getElementsByTagName("SimBase.Document");
    simbase_element[0].setAttribute("Type", "AceXML");
    simbase_element[0].setAttribute("version", "1,0");

    var desc_node = xmlDoc.createElement("Descr");
    desc_node.innerHTML = "AceXML Document";
    simbase_element[0].appendChild(desc_node);

    var flightplan_node = xmlDoc.createElement("FlightPlan.FlightPlan");
    simbase_element[0].appendChild(flightplan_node)

    var title_node = xmlDoc.createElement("Title");
    title_node.innerHTML = title_txt;
    flightplan_node.appendChild(title_node);

    var FPType_node = xmlDoc.createElement("FPType");
    FPType_node.innerHTML = "VFR"
    flightplan_node.appendChild(FPType_node);

    var RouteType_node = xmlDoc.createElement("RouteType");
    RouteType_node.innerHTML = "LowAlt"
    flightplan_node.appendChild(RouteType_node);

    var CruisingAlt_node = xmlDoc.createElement("CruisingAlt");
    CruisingAlt_node.innerHTML = crusing_altitude;
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
    DestinationLLA_node.innerHTML = departure_lla;
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

    buildATCWapoints(xmlDoc, flightplan_node, flightPath_data, crusing_altitude);


    // const header =          '<?xml version="1.0" encoding="UTF-8"?>\n' +
    //                         '\n'+
    //                         '<SimBase.Document Type="AceXML" version="1,0">\n'+
    //                         '    <Descr>AceXML Document</Descr>\n'+
    //                         '    <FlightPlan.FlightPlan>\n';
    // const title =           `        <Title>${title_txt}</Title>` + '\n';
    // const FPTType =         `        <FPType>VFR</FPType>` + '\n';
    // const CruisingAlt =     `        <CruisingAlt>${crusing_altitude}</CruisingAlt>` + '\n';
    // const DepartureID =     `        <DepartureID>${departure_id}</DepartureID>` + '\n';
    // const DepartureLLA =    `        <DepartureLLA>${departure_lla}</DepartureLLA>` + '\n';
    // const DestinationID =   `        <DestinationID>${destination_id}</DestinationID>` + '\n';
    // const DestinationLLA =  `        <DestinationLLA>${destination_lla}</DestinationLLA>` + '\n';
    // const Descr =           `        <Descr>${description}</Descr>` + '\n';
    // const DepartureName =   `        <DepartureName>${departure_name}</DepartureName>` + '\n';
    // const DestinationName = `        <DestinationName>${destination_name}</DestinationName>` + '\n';
    // const app_details =     '        <AppVersion>\n' +
    //                         '            <AppVersionMajor>11</AppVersionMajor>\n' +
    //                         '            <AppVersionBuild>282174</AppVersionBuild>\n' +
    //                         '        </AppVersion>\n'
    // const footer =          '    </FlightPlan.FlightPlan>\n' +
    //                         '</SimBase.Document>\n'

    // content += header + title + FPTType + CruisingAlt + DepartureID + DepartureLLA + DestinationID + DestinationLLA + Descr + 
    //             DepartureName + DestinationName + app_details + buildATCWapoints(flightPath_data, crusing_altitude) + footer;


    xmlDoc_string = new XMLSerializer().serializeToString(xmlDoc)

    xml_formatted = formatXml(xmlDoc_string);
    
    console.log(xml_formatted);

    return xml_formatted;
}

function buildATCWapoints(xmlDoc, flightplan_node, flightPath_data, crusing_altitude) {


    var name;
    var lat;
    var lng;
    var ATCWaypoint_node;
    var ATCWaypointType_node;
    var WorldPosition_node;
    var ICAO_node;
    var ICAOIdent_node;

    for (var i = 0; i < flightPath_data.length; i++) {

        if (i==0) {
            name = 'CUSTD';
        } else if (i ==flightPath_data.length-1) {
            name = 'CUSTA';
        } else {
            name = flightPath_data[i]['waypoint'];
        }
        
        lat = convertDDToDMS(flightPath_data[i]['latLng'][0], "90", 2);
        lng = convertDDToDMS(flightPath_data[i]['latLng'][1], "180", 2);

        ATCWaypoint_node = xmlDoc.createElement("ATCWaypoint");
        ATCWaypoint_node.setAttribute("id", `${name}`);
        flightplan_node.appendChild(ATCWaypoint_node)

        ATCWaypointType_node = xmlDoc.createElement("ATCWaypointType");
        ATCWaypointType_node.innerHTML = "Intersection";
        ATCWaypoint_node.appendChild(ATCWaypointType_node);

        WorldPosition_node = xmlDoc.createElement("WorldPosition");
        WorldPosition_node.innerHTML = `${lat},${lng},+${crusing_altitude}`;
        ATCWaypoint_node.appendChild(WorldPosition_node);
        
        // only build the ICAO section for departure and arrival waypoints
        if ((i == 0) || (i ==flightPath_data.length-1)) {

            ICAO_node = xmlDoc.createElement("ICAO");
            ATCWaypoint_node.appendChild(ICAO_node);
            
            ICAOIdent_node = xmlDoc.createElement("ICAOIdent");
            ICAOIdent_node.innerHTML = `${name}`;
            ICAO_node.appendChild(ICAOIdent_node);
        }
    }     
}

function buildFlightPlanModalBody(flightPath_data) {


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

function formatXml(xml) {
    var formatted = '';
    var reg = /(>)(<)(\/*)/g;
    xml = xml.replace(reg, '$1\r\n$2$3');
    var pad = 0;
    jQuery.each(xml.split('\r\n'), function(index, node) {
        var indent = 0;
        if (node.match( /.+<\/\w[^>]*>$/ )) {
            indent = 0;
        } else if (node.match( /^<\/\w/ )) {
            if (pad != 0) {
                pad -= 1;
            }
        } else if (node.match( /^<\w[^>]*[^\/]>.*$/ )) {
            indent = 1;
        } else {
            indent = 0;
        }

        var padding = '';
        for (var i = 0; i < pad; i++) {
            padding += '  ';
        }

        formatted += padding + node + '\r\n';
        pad += indent;
    });

    return formatted;
}