var point_offset = 0,
    total = 0,
    total_displayed = 0,
    latest_pk = 0,
    new_point = false,
    all_subtopics;

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

function requestPoints(offset, count) {
  $.ajax({
    url: data_url,
    data: "data_type=predict&offset=" + offset + "&count=" + count + "&committee_id=" + committee_id,
    success: function(response) {
      total = response.totaldata;
      point_offset += count;
      if (typeof response.datapoints[0].committee_by !== "undefined") {
        response.datapoints.forEach(function(point) {
          createPoint(-1, point.pk, point.last_changed, point.active_debate, point.round_no, point.point_type, point.subtopics);
          total_displayed++;
        });
      }
      if (new_point === false) {
        if (typeof response.datapoints[0].pk !== "undefined") {
          latest_pk = response.datapoints[0].pk;
        }
        requestNewPoints();
        new_point = true;
      }
    },
    cache: false
  });
}

function requestNewPoints() {
  $.ajax({
    url: data_latest_url,
    data: "data_type=predict&pk=" + latest_pk + "&committee_id=" + committee_id,
    success: function(response) {
      if (typeof response.datapoints[0].pk !== "undefined") {
        latest_pk = response.datapoints[0].pk;
      }
      total = response.totaldata;
      if (typeof response.datapoints[0].committee_by !== "undefined") {
        response.datapoints.forEach(function(point) {
          point_offset++;
          createPoint(0, point.pk, point.last_changed, point.active_debate, point.round_no, point.point_type, point.subtopics);
          total_displayed++;
        });
      }
      setTimeout(requestNewPoints, 3000);
    },
    cache: false
  });
}

function createPoint(where, pk, last_changed, on, round, type, subtopics) {
  //Setting up the new row in the table
  var table = document.getElementById("point-table").getElementsByTagName('tbody')[0],
    row = table.insertRow(where),
    point_id = row.insertCell(0),
    point_last_changed = row.insertCell(1),
    point_on = row.insertCell(2),
    point_round = row.insertCell(3),
    point_type = row.insertCell(4),
    point_subtopics = row.insertCell(5),
    point_action = row.insertCell(-1);
  //Giving the row a point-specific id.
  $(row).attr('id', 'point-' + pk);
  //Hiding the row so we can fade it in.
  $(row).css('display', 'none');
  //Assigning cell values
  point_id.innerHTML = pk;
  point_last_changed.innerHTML = last_changed;
  point_on.innerHTML = on;
  point_round.innerHTML = round;
  if (type === 'P') {
    point_type.innerHTML = '<img src="' + point_img + '" height="30" >';
  } else {
    point_type.innerHTML = '<img src="' + dr_img + '" height="30" >';
  }
  point_subtopics.innerHTML = subtopics;
  point_action.innerHTML = '<a href="javascript:void(0)" class="btn btn-xs btn-primary btn-raised mdi-content-create" data-toggle="modal" data-target="#edit-subtopics" onclick="editPoint(' + "'" + pk + "'" + ')" ><i class="material-icons" style="font-size: 18px">mode_edit</i></a>';
  $(row).fadeIn("slow");
}

function editPoint(pk) {
  var data = "data_type=predict&pk=" + pk;
  $.ajax({
    url: data_pk_url,
    data: data,
    success: function(response) {
      $('#point_id_pk').val(response.pk);
      var subtopics_select = document.getElementById("point_id_subtopics"),
        j = 0;
      while (subtopics_select.options.length > 0) {
        subtopics_select.options.remove(0);
      }
      all_subtopics = [];
      response.all_subtopics.forEach(function(subtopic) {
        all_subtopics.push({
          'pk': subtopic.pk.toString()
        });
        var s = document.createElement("option");
        s.text = subtopic.subtopic;
        $(s).attr('id', subtopic.pk);
        $(s).attr('value', subtopic.pk);
        subtopics_select.options.add(s, j);
        j++;
      });
      console.log(all_subtopics);
      response.subtopics.forEach(function(subtopic) {
        subtopics_select.options.namedItem(subtopic.pk).selected = true;
      });
    }
  });
}

$('#point-form').on('submit', function(event) {
  event.preventDefault();
  console.log("Point form submitted!"); // sanity check
  savePoint();
});

function savePoint() {
  var subtopics_array = [];
  $('#point_id_subtopics').val().forEach(function(subtopic) {
    subtopics_array.push({
      'pk': subtopic
    });
  });
  $.ajax({
    url: data_pk_url,
    type: "POST",
    data: {
      'data-type': 'predict',
      'pk': $('#point_id_pk').val(),
      'subtopics': JSON.stringify(subtopics_array),
      'all_subtopics': JSON.stringify(all_subtopics)
    },
    success: function(json) {
      console.log('success!');
      console.log(json);
      deleteInput('point-' + json.pk);
      createPoint(0, json.pk, json.last_changed, json.debate, json.round_no, json.point_type, json.subtopics);
      $('#edit-subtopics').modal('hide');
      $('#results').html('<div class="alert alert-dismissable alert-success">'+
                          '<button type="button" class="close" data-dismiss="alert">×</button>'+
                          'Point Saved</a>.'+
                          '</div>');
      window.setTimeout(function() {
        $(".alert").fadeTo(500, 0).slideUp(500, function(){
          $(this).remove();
        });
      }, 5000);
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
    cache: false
  });
}

jQuery(
  function($) {
    $('#point-div').bind('scroll', function() {
      if ($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {
        if (total_displayed < total) {
          requestPoints(point_offset, 10);
        }
      }
    });
  }
);

requestPoints(point_offset, 10);

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
