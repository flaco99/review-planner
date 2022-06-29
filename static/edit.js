function setDefaultTime(){
    if (document.querySelector("#defaulteventtimeswitch").checked) {
    localStorage.setItem('event_hour',document.querySelector("#eventhour").value);
    localStorage.setItem('event_minute',document.querySelector("#eventminute").value);
    }
}

function changeFormAction() {
    document.querySelector("#applyChangesForm").action = "/apply_changes_to_all";
}