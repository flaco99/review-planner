document.addEventListener('DOMContentLoaded', function(event) {
    const eventHour = localStorage.getItem("event_hour");
    if (eventHour == null) {
        // first visit to page
    } else {
        document.querySelector("#eventhour").value=eventHour;
    }
})
function setDefaultTime(){
    if (document.querySelector("#defaulteventtimeswitch").checked) {
    localStorage.setItem('event_hour',document.querySelector("#eventhour").value);
    }
}