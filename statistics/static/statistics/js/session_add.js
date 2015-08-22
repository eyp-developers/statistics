var counter_subtopics = 3;
var limit_subtopics = 30;
var table = document.getElementById("committees-table").getElementsByTagName('tbody')[0];

function addInput(divName, subtopicValue, subtopicId){
  var newdiv = document.createElement('div');
  newdiv.setAttribute("id", "subtopic-div-" + counter_subtopics);
  newdiv.innerHTML = '<label class="control-label col-sm-2" for="inputLarge"></label>' +
    '<div class="col-sm-8">' +
    '<input type="hidden" name="subtopic_pk[]" id="subtopic-pk-'+ counter_subtopics +'" value="'+ subtopicId +'">' +
    '<input class="form-control input-sm" type="text" name="subtopic[]" id="subtopic-'+ counter_subtopics +'" value="'+ subtopicValue +'">' +
    '</div>' +
    '<div class="col-sm-2">' +
    '<span class="input-group-btn">' +
    '<button class="btn btn-primary btn-material-'+ session_color +'-800 btn-sm" type="button" onclick="deleteInput(' + "'subtopic-div-" + counter_subtopics + "'" + ')">Delete</button>' +
    '</span>' +
    '</div>';
  document.getElementById(divName).appendChild(newdiv);
  counter_subtopics++;
}
Element.prototype.remove = function() {
    this.parentElement.removeChild(this);
};
NodeList.prototype.remove = HTMLCollection.prototype.remove = function() {
    for(var i = this.length - 1; i >= 0; i--) {
        if(this[i] && this[i].parentElement) {
            this[i].parentElement.removeChild(this[i]);
        }
    }
};
function deleteInput(divName){
  document.getElementById(divName).remove();
}

function deleteSubtopics(except) {
  var k = 1 + except;
  while (k < counter_subtopics){
    if ($('#subtopic-div-' + k).length !== 0) {
      deleteInput('subtopic-div-' + k);
    }
    k++;
  }
}

$('#committee-form').on('submit', function(event){
    event.preventDefault();
    console.log("form submitted!");  // sanity check
    submit_committee();
});
function submit_committee() {
    var i = 1;
    var j = 1;
    var subtopics_array = [];
    console.log("create post is working!"); // sanity check
    console.log($('#id_pk').val());
    console.log($('#id_name').val());
    console.log($('#id_topic').val());
    while (i <= counter_subtopics){
      if ($('#subtopic-' + i).val() !== undefined) {
        console.log($('#subtopic-' + i).val());
        subtopics_array.push({pk: $('#subtopic-pk-'+i).val(), subtopic: $('#subtopic-'+i).val()});
      }
      i++;
    }
    console.log(subtopics_array);
    $.ajax({
        url : committee_post_url, // the endpoint
        type : "POST", // http method
        data : { 'pk' : $('#id_pk').val(), 'name' : $('#id_name').val(), 'topic' : $('#id_topic').val(), 'subtopics': JSON.stringify(subtopics_array) }, // data sent with the post request

        // handle a successful response
        success : function(json) {
          if ($('#id_pk').val() !== '') {
            deleteInput('committee-row-' + json.pk);
          }
          // Adding the newly created session to the table of sessions.
          var row = table.insertRow(0);
          var id = row.insertCell(0);
          var name = row.insertCell(1);
          var topic = row.insertCell(2);
          var subtopics = row.insertCell(3);
          var actions = row.insertCell(4);
          $(row).attr('id', 'committee-row-' + json.pk);
          id.innerHTML = json.pk;
          name.innerHTML = $('#id_name').val();
          topic.innerHTML = $('#id_topic').val();
          subtopics.innerHTML = json.subtopics;
          actions.innerHTML = '<a href="javascript:void(0)" class="btn btn-primary btn-material-'+ session_color +'-800 btn-xs" onclick="editCommittee(' + "'" + json.pk + "'" + ')" ><span class="mdi-content-create" style="font-size: 10px; margin-right: 4px;"></span>Edit</a><a href="javascript:void(0)" class="btn btn-primary btn-danger btn-xs" onclick="deleteCommittee(' + "'" + json.pk + "'" + ')" >Delete</a>';
          $(row).css('display', 'none');
          $(row).fadeIn("slow");

          // Removing values from the form.
          $('#id_pk').val(''); // remove the value from the input
          $('#id_name').val(''); // remove the value from the input
          $('#id_topic').val(''); // remove the value from the input
          while (j <= counter_subtopics){
            if ($('#subtopic-' + j).val() !== undefined) {
              $('#subtopic-' + j).val('');
              $('#subtopic-pk-' + j).val('');
            }
            j++;
          }
          deleteSubtopics(1);
          $('#subtopic-1').val('General');
          counter_subtopics = 3;
          console.log(json); // log the returned json to the console
          console.log("success"); // another sanity check
        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            //$('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
            //    " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
}

function editCommittee(pk) {
  $.ajax({
    url: committees_api_url,
    data: "pk=" + pk,
    success: function (response) {
      console.log('ajax success for: ' + response.name);
      $('#id_pk').val(response.pk);
      $('#id_name').val(response.name);
      $('#id_topic').val(response.topic);
      deleteSubtopics(0);
      response.subtopics.forEach(function(subtopic) {
        if (subtopic.subtopic != 'General'){
          addInput('add_subtopics', subtopic.subtopic, subtopic.pk);
        }
      });
    },
    cache: false
  });
}

function deleteCommittee(committee_pk) {
  console.log('lets delete ' + committee_pk);
  if (confirm('Are you sure you want to delete this committee?') === true){
        $.ajax({
            url : committee_post_url, // the endpoint
            type : "POST", // http method
            data : { delete : true, pk : committee_pk }, // data sent with the delete request
            success : function(json) {
                // delete the post from the page
              deleteInput('committee-row-' + committee_pk);
              console.log("post deletion successful");
            },
            error : function(xhr,errmsg,err) {
                console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }
        });
    } else {
        return false;
    }
}

// This function gets cookie with a given name
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

/*
The functions below will create a header with csrftoken
*/

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
