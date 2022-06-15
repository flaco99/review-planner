// go to the user's google calendar and get info on the event that they're editting and fill in the info

// localStorage.setItem('event_hour',document.querySelector("#eventhour").value);
// like this but without using local storage.

function setDefaultTime(){
    if (document.querySelector("#defaulteventtimeswitch").checked) {
    localStorage.setItem('event_hour',document.querySelector("#eventhour").value);
    }
}

function changeFormAction() {
    document.querySelector("#applyChangesForm").action = "/apply_changes_to_all";
}