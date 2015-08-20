var counter_subtopics = 1;
var limit_subtopics = 10;
function addInput(divName){
     if (counter_subtopics == limit_subtopics)  {
          alert("More than 10 subtopics is just confusing!");
     }
     else {
          var newdiv = document.createElement('div');
          newdiv.innerHTML = "<label class='control-label col-sm-2' for='inputLarge'></label><div class='col-sm-8'><input class='form-control input-sm' type='text' id='subtopic' value=''></div><div class='col-sm-2'><span class='input-group-btn'><button class='btn btn-primary btn-sm' type='button'>Delete</button></span></div>";
          document.getElementById(divName).appendChild(newdiv);
          counter_subtopics++;
     }
}
