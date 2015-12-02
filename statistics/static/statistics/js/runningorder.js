Element.prototype.remove = function() {
  this.parentElement.removeChild(this);
};
NodeList.prototype.remove = HTMLCollection.prototype.remove = function() {
  for (var i = this.length - 1; i >= 0; i--) {
    if (this[i] && this[i].parentElement) {
      this[i].parentElement.removeChild(this[i]);
    }
  }
};

function deleteInput(id) {
  document.getElementById(id).remove();
}
var backlog_count,
    last_postition;

function getCommittees() {
  $.ajax({
    url: runningorder_url,
    success: function(response) {
      response.committees.forEach(function(committee) {
        var subtopicHTML = "";
        if (committee.next_subtopics[0] === undefined) {
          subtopicHTML += '<span class="label label-material-' + session_color + '">None</span>';
        } else {
          committee.next_subtopics.forEach(function(subtopic) {
            subtopicHTML += '<span class="label label-material-' + subtopic.color + '" style="color: ' + subtopic.text_color + '">' + subtopic.subtopic + '</span> ';
          });
        }
        document.getElementById("subtopics-" + committee.pk).innerHTML = subtopicHTML;
        document.getElementById("debate-" + committee.pk).innerHTML = committee.debate_total;
        document.getElementById("session-" + committee.pk).innerHTML = committee.session_total;
        committee_box = document.getElementById("committee-" + committee.pk);

        $(committee_box).css('height', committee.height + "%");

        backlog_count = 0;
        response.backlog.forEach(function(point){
          backlog_count++;
          if ($('#backlog' + point.position)[0] !== undefined) {
            deleteInput('backlog' + point.position);
          }
          createPoint('backlog', 'backlog' + point.position, point.position, 0, point.by, point.on, point.round, point.type, point.subtopics);
        });

        response.queue.forEach(function(point){
          if ($('#queue-' + point.position)[0] !== undefined) {
            deleteInput('queue-' + point.position);
          }
          last_postition = point.position;
          createPoint('point', 'queue-' + point.position, point.position, -1, point.by, point.on, point.round, point.type, point.subtopics);
        });
      });
      setTimeout(getCommittees, 1000);
    },
    cache: false
  });
}

getCommittees();

function addToRunningOrder(by, type) {
  $.ajax({
    url: runningorder_url,
    type: "POST",
    data: {
      'by': by,
      'type': type
    },
    success: function(response) {

    },
    error: function(xhr, errmsg, err) {
      $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: " + errmsg +
        " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
      console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
      $('#results').html('<div class="alert alert-dismissable alert-danger">'+
                          '<button type="button" class="close" data-dismiss="alert">×</button>'+
                          'There was an error, check your internet and try again!</a>.'+
                          '</div>');
      window.setTimeout(function() {
        $(".alert").fadeTo(500, 0).slideUp(500, function(){
          $(this).remove();
        });
      }, 5000);
    },
  });
}

function clearAction(action){
  if (confirm('Are you sure you want to clear the queue?') === true) {
    runningOrderAction(action);
  }
}

function runningOrderAction(action) {
  $.ajax({
    url: runningorder_url,
    type: "POST",
    data: {
      'action': action
    },
    success: function(response) {
      if (action === 'R') {
        deleteInput('queue-' + last_postition);
      }
      if (action === 'C') {
        var i = 0;
        while (i < last_postition) {
          i++;
          deleteInput('queue-' + i);
        }
      }
    },
    error: function(xhr, errmsg, err) {
      $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: " + errmsg +
        " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
      console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
      $('#results').html('<div class="alert alert-dismissable alert-danger">'+
                          '<button type="button" class="close" data-dismiss="alert">×</button>'+
                          'There was an error, check your internet and try again!</a>.'+
                          '</div>');
      window.setTimeout(function() {
        $(".alert").fadeTo(500, 0).slideUp(500, function(){
          $(this).remove();
        });
      }, 5000);
    }
  });
}

function deletePoint(position) {
  $.ajax({
    url: runningorder_url,
    type: "POST",
    data: {
      'action': 'delete',
      'position': position
    },
    success: function(response) {
      deleteInput('queue-' + last_postition);
    },
    error: function(xhr, errmsg, err) {
      $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: " + errmsg +
        " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
      console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
      $('#results').html('<div class="alert alert-dismissable alert-danger">'+
                          '<button type="button" class="close" data-dismiss="alert">×</button>'+
                          'There was an error, check your internet and try again!</a>.'+
                          '</div>');
      window.setTimeout(function() {
        $(".alert").fadeTo(500, 0).slideUp(500, function(){
          $(this).remove();
        });
      }, 5000);
    }
  });
}

function movePoint(direction, position) {
  $.ajax({
    url: runningorder_url,
    type: "POST",
    data: {
      'action': 'move',
      'direction': direction,
      'position': position
    },
    success: function(response) {

    },
    error: function(xhr, errmsg, err) {
      $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: " + errmsg +
        " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
      console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
      $('#results').html('<div class="alert alert-dismissable alert-danger">'+
                          '<button type="button" class="close" data-dismiss="alert">×</button>'+
                          'There was an error, check your internet and try again!</a>.'+
                          '</div>');
      window.setTimeout(function() {
        $(".alert").fadeTo(500, 0).slideUp(500, function(){
          $(this).remove();
        });
      }, 5000);
    }
  });
}

var queue_points = 0,
    backlog_points = 0;

function createPoint(kind, id, pos, where, by, on, round, type, subtopics) {
  //Setting up the new row in the table
  var table = document.getElementById("runningorder-table").getElementsByTagName('tbody')[0],
    row = table.insertRow(where),
    point_order = row.insertCell(0),
    point_by = row.insertCell(1),
    point_on = row.insertCell(2),
    point_round = row.insertCell(3),
    point_type = row.insertCell(4),
    point_subtopics = row.insertCell(5),
    point_action = row.insertCell(6);
  //Giving the row a point-specific id.
  queue_points++;
  $(row).attr('id', id);
  //Hiding the row so we can fade it in.
  //Assigning cell values
  point_order.innerHTML = pos;
  point_by.innerHTML = by;
  point_on.innerHTML = on;
  point_round.innerHTML = round;
  if (type === 'P') {
    point_type.innerHTML = 'Point';
  } else {
    point_type.innerHTML = 'DR';
  }

  var pointsubtopicHTML = "";
  if (subtopics[0] === undefined) {
    pointsubtopicHTML += '<span class="label label-material-' + session_color + '">None</span>';
  } else {
    subtopics.forEach(function(subtopic) {
      pointsubtopicHTML += '<span class="label label-material-' + subtopic.color + '" style="color: ' + subtopic.text_color + '">' + subtopic.subtopic + '</span> ';
    });
  }
  point_subtopics.innerHTML = pointsubtopicHTML;
  if (kind === 'point') {
    point_action.innerHTML = '<a href="javascript:void(0)" class="btn btn-info btn-fab btn-raised mdi-navigation-expand-less" onclick="movePoint('+ "'up'," + pos + ')" ></a><a href="javascript:void(0)" class="btn btn-info btn-fab btn-raised mdi-navigation-expand-more" onclick="movePoint('+ "'down'," + pos + ')" ></a><a href="javascript:void(0)" class="btn btn-danger btn-fab btn-raised mdi-action-delete" onclick="deletePoint(' + pos + ')" ></a>';
  } else {
    point_action.innerHTML = '';
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
