var flightPath_data = []

function saveFlightPlan(document) {

    content = 'This is some content';
    filename = 'flight_plan.fpl';

    var doc = document.implementation.createDocument ('http://www.w3.org/1999/xhtml', 'html', null);
    var body = document.createElementNS('http://www.w3.org/1999/xhtml', 'body');
    body.setAttribute('id', 'abc');
    doc.documentElement.appendChild(body);
    content = doc

    
            
    const a = document.createElement('a');
    const file = new Blob([content], {type: 'text/plain'});
    
    a.href= URL.createObjectURL(file);
    a.download = filename;
    a.click();
    
    URL.revokeObjectURL(a.href);
    alert("saving flight plan")
}



function buildFlightPlan(document) {

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