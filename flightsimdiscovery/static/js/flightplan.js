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

    var body_htm = "<p>No flight plan created.<br /><br />  Click on a Point of Interest and 'add to Flight Plan' first.</p>";
    
    if (Array.isArray(flightPath_data) && flightPath_data.length) {
        body_htm = '<p>We have detected flight plan data</p>';
    }
        
    return body_htm;
}