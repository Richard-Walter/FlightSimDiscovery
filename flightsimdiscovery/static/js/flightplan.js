function saveFlightPlan(document) {

    content = 'This is some content';
    filename = 'flight_plan.fpl';
    var text = 'Some data I want to export';
            
    const a = document.createElement('a');
    const file = new Blob([content], {type: 'text/plain'});
    
    a.href= URL.createObjectURL(file);
    a.download = filename;
    a.click();
    
    URL.revokeObjectURL(a.href);
    alert("saving flight plan")
};


function buildFlightPlan(document) {

}

function buildFlgihtPlanModalBody(document) {
    return "<p>Modal body text goes here!!!!.</p>"
}