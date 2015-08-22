var active_debate_on_load;
var latest_active_debate;

$.getJSON("http://localhost:8000/api/active_debate/2/", function(result){
      active_debate_on_load = result.active_debate_pk;
      console.log(active_debate_on_load + " on load");
  });

window.setInterval(function(){
  $.getJSON("http://localhost:8000/api/active_debate/2/", function(result){
        latest_active_debate = result.active_debate_pk;
        console.log(latest_active_debate + " latest");

    });
}, 2000);




window.setInterval(function(){
  console.log("checked");
  if (latest_active_debate !== active_debate_on_load) {
    window.location.replace("http://stackoverflow.com/");
  }
}, 3000);
