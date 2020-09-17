var flightPath_data = []

function saveFlightPlan(document, flightPath_data) {

    filename = 'flight_plan.txt';
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
    const crusing_altitude = '7500.000';
    const departure_id = 'CUSTD';
    const departure_lla = `S35° 18' 35.73",E146° 48' 40.22",+001500.00`;
    const destination_id = 'CUSTA';
    const destination_lla = `S35° 27' 43.54",E147° 59' 49.78",+001640.42`;

    const header =          '<?xml version="1.0" encoding="UTF-8"?>\n' +
                            '\n'+
                            '<SimBase.Document Type="AceXML" version="1,0"></SimBase.Document>\n'+
                            '    <Descr>AceXML Document</Descr>\n'+
                            '    <FlightPlan.FlightPlan>\n';
    const title =           `        <Title>${title_txt}</Title>` + '\n';
    const FPTType =         `        <FPType>VFR</FPType>` + '\n';
    const CruisingAlt =     `        <CruisingAlt>${crusing_altitude}</CruisingAlt>` + '\n';
    const DepartureID =     `        <DepartureID>${departure_id}</DepartureID>` + '\n';
    const DepartureLLA =    `        <DepartureLLA>${departure_lla}</DepartureLLA>` + '\n';
    const DestinationID =   `        <DestinationID>${destination_id}</DestinationID>` + '\n';
    const DestinationLLA =  `        <DestinationLLA>${destination_lla}</DestinationLLA>` + '\n';


    content += header + title + FPTType + CruisingAlt + DepartureID + DepartureID + DepartureLLA + DestinationID + DestinationLLA;

    console.log(content);


    // if (Array.isArray(flightPath_data) && flightPath_data.length>1) {
    
    //     for (var i = 0; i < flightPath_data.length; i++) {
    //         content += flightPath_data[i]['waypoint'] + " --> ";
    //       }
    //     content = content.substring(0, content.length-5);  //remove the -->
    // }

    return content;
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