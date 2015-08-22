var active_debate_on_load;
var latest_active_debate;

// Here we're getting the active debate json data and assign a value to active_debate_on_load which will stay the same the entire time the pages is not refreshed
$.getJSON(active_debate_url, function(result){
      active_debate_on_load = result.active_debate_pk;
  });

// This will check whether the active debate has changed every five seconds and assign the value to latest_active_debate
window.setInterval(function(){
  $.getJSON(active_debate_url, function(result){
        latest_active_debate = result.active_debate_pk;

    });
    if (latest_active_debate !== active_debate_on_load && latest_active_debate !== undefined && active_debate_on_load !== undefined) {
      window.location.replace("../" + latest_active_debate);
    }
}, 5000);
