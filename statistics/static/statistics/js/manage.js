var offset_point = 0,
  offset_content = 0,
  total_point,
  total_content,
  total_points_displayed = 0,
  total_content_displayed = 0,
  latest_point_pk = 0,
  latest_content_pk = 0,
  new_point = false,
  new_content = false;

var offset_vote = 0,
  total_vote,
  total_votes_displayed = 0,
  latest_vote_pk = 0,
  new_vote = false;

var all_subtopics;

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

function requestData(type, offset, count) {
  $.ajax({
    url: data_url,
    data: "data_type=" + type + "&offset=" + offset + "&count=" + count,
    success: function(response) {
      if (type === 'point') {
        total_point = response.totaldata;
        offset_point += count;
        if (typeof response.datapoints[0].committee_by !== "undefined") {
          response.datapoints.forEach(function(point) {
            createPoint(-1, point.pk, point.last_changed, point.committee_by, point.active_debate, point.round_no, point.point_type, point.subtopics, point.committee_color, point.committee_text_color);
            total_points_displayed++;
          });
        }
        if (new_point === false) {
          if (typeof response.datapoints[0].pk !== "undefined") {
            latest_point_pk = response.datapoints[0].pk;
          }
          requestNewData('point');
          new_point = true;
        }
      } else if (type === 'content') {
        total_content = response.totaldata;
        offset_content += count;
        if (typeof response.datapoints[0].content !== "undefined") {
          response.datapoints.forEach(function(content) {
            createContent(-1, content.pk, content.last_changed, content.committee_by, content.active_debate, content.content, content.point_type, content.committee_color, content.committee_text_color);
            total_content_displayed++;
          });
        }
        if (new_content === false) {
          if (typeof response.datapoints[0].pk !== "undefined") {
            latest_content_pk = response.datapoints[0].pk;
          }
          requestNewData('content');
          new_content = true;
        }
      } else if (type === 'vote') {
        total_vote = response.totaldata;
        offset_vote += count;
        if (typeof response.datapoints[0].committee_by !== "undefined") {
          response.datapoints.forEach(function(vote) {
            createVote(-1, vote.pk, vote.last_changed, vote.committee_by, vote.active_debate, vote.in_favour, vote.against, vote.abstentions, vote.absent, vote.committee_color, vote.committee_text_color);
            total_votes_displayed++;
          });
        }
        if (new_vote === false) {
          if (typeof response.datapoints[0].pk !== "undefined") {
            latest_vote_pk = response.datapoints[0].pk;
          }
          requestNewData('vote');
          new_vote = true;
        }
      }
    },
    cache: false
  });
}

function requestNewData(type) {
  var new_latest;
  if (type === 'point') {
    new_latest = latest_point_pk;
  } else if (type === 'content') {
    new_latest = latest_content_pk;
  } else if (type === 'vote') {
    new_latest = latest_vote_pk;
  }
  $.ajax({
    url: data_latest_url,
    data: "data_type=" + type + "&pk=" + new_latest,
    success: function(response) {
      if (type === 'point') {
        if (typeof response.datapoints[0].pk !== "undefined") {
          latest_point_pk = response.datapoints[0].pk;
        }
        total_point = response.totaldata;
        if (typeof response.datapoints[0].committee_by !== "undefined") {
          response.datapoints.forEach(function(point) {
            offset_point++;
            createPoint(0, point.pk, point.last_changed, point.committee_by, point.active_debate, point.round_no, point.point_type, point.subtopics, point.committee_color, point.committee_text_color);
            total_points_displayed++;
          });
        }
      } else if (type === 'content') {
        if (typeof response.datapoints[0].pk !== "undefined") {
          latest_content_pk = response.datapoints[0].pk;
        }
        total_content = response.totaldata;
        if (typeof response.datapoints[0].content !== "undefined") {
          response.datapoints.forEach(function(content) {
            offset_content++;
            createContent(0, content.pk, content.last_changed, content.committee_by, content.active_debate, content.content, content.point_type, content.committee_color, content.committee_text_color);
            total_content_displayed++;
          });
        }
      } else if (type === 'vote') {
        if (typeof response.datapoints[0].pk !== "undefined") {
          latest_vote_pk = response.datapoints[0].pk;
        }
        total_vote = response.totaldata;
        if (typeof response.datapoints[0].committee_by !== "undefined") {
          response.datapoints.forEach(function(vote) {
            offset_vote++;
            createVote(0, vote.pk, vote.last_changed, vote.committee_by, vote.active_debate, vote.in_favour, vote.against, vote.abstentions, vote.absent, vote.committee_color, vote.committee_text_color);
            total_votes_displayed++;
          });
        }
      }

      setTimeout(requestNewData, 3000, type);
    },
    cache: false
  });
}

function createPoint(where, pk, last_changed, by, on, round, type, subtopics, color, text_color) {
  //Setting up the new row in the table
  var table = document.getElementById("point-table").getElementsByTagName('tbody')[0],
    row = table.insertRow(where),
    point_id = row.insertCell(0),
    point_last_changed = row.insertCell(1),
    point_by = row.insertCell(2),
    point_on = row.insertCell(3),
    point_round = row.insertCell(4),
    point_type = row.insertCell(5),
    point_subtopics = row.insertCell(6),
    point_action = row.insertCell(7);
  //Giving the row a point-specific id.
  $(row).attr('id', 'point-' + pk);
  //Hiding the row so we can fade it in.
  $(row).css('display', 'none');
  //Assigning cell values
  point_id.innerHTML = pk;
  point_last_changed.innerHTML = last_changed;
  point_by.innerHTML = by;
  point_on.innerHTML = on;
  point_round.innerHTML = round;
  if (type === 'P') {
    point_type.innerHTML = '<img src="' + point_img + '" height="30" >';
  } else {
    point_type.innerHTML = '<img src="' + dr_img + '" height="30" >';
  }
  point_subtopics.innerHTML = subtopics;
  point_action.innerHTML = '<a href="javascript:void(0)" class="btn btn-xs btn-primary btn-raised" data-toggle="modal" data-target="#edit-point" onclick="editPoint(' + "'" + pk + "'" + ')" ><i class="material-icons" style="font-size: 18px">mode_edit</i></a><a href="javascript:void(0)" class="btn btn-danger btn-xs btn-raised" onclick="deleteData(' + "'point', " + "'" + pk + "'" + ')" ><i class="material-icons" style="font-size: 18px">delete</i></a>';
  //Adding pretty color classes
  $(point_by).addClass(color);
  $(point_by).css('color', text_color);
  $(row).fadeIn("slow");
}


function createContent(where, pk, last_changed, by, on, content, type, color, text_color) {
  //Setting up the new row in the table
  var table = document.getElementById("content-table").getElementsByTagName('tbody')[0],
    row = table.insertRow(where),
    content_id = row.insertCell(0),
    content_last_changed = row.insertCell(1),
    content_by = row.insertCell(2),
    content_on = row.insertCell(3),
    content_content = row.insertCell(4),
    content_type = row.insertCell(5),
    content_action = row.insertCell(6);
  //Giving row a content specific id.
  $(row).attr('id', 'content-' + pk);
  //Hiding the row so we can fade it in
  $(row).css('display', 'none');
  content_id.innerHTML = pk;
  content_last_changed.innerHTML = last_changed;
  content_by.innerHTML = by;
  content_on.innerHTML = on;
  content_content.innerHTML = content;
  if (type === 'P') {
    content_type.innerHTML = '<img src="' + point_img + '" height="30" >';
  } else {
    content_type.innerHTML = '<img src="' + dr_img + '" height="30" >';
  }
  content_action.innerHTML = '<a href="javascript:void(0)" class="btn btn-xs btn-primary btn-raised" data-toggle="modal" data-target="#edit-content" onclick="editContent(' + "'" + pk + "'" + ')" ><i class="material-icons" style="font-size: 18px">mode_edit</i></a><a href="javascript:void(0)" class="btn btn-danger btn-xs btn-raised" onclick="deleteData(' + "'content', " + "'" + pk + "'" + ')" ><i class="material-icons" style="font-size: 18px">delete</i></a>';
  //Adding pretty color classes and fading in
  $(content_by).addClass(color);
  $(content_by).css('color', text_color);
  $(row).fadeIn("slow");
}


function createVote(where, pk, last_changed, by, on, in_favour, against, abstentions, absent, color, text_color) {
  //Setting up the new row in the table
  var table = document.getElementById("vote-table").getElementsByTagName('tbody')[0],
    row = table.insertRow(where),
    vote_id = row.insertCell(0),
    vote_last_changed = row.insertCell(1),
    vote_by = row.insertCell(2),
    vote_on = row.insertCell(3),
    vote_in_favour = row.insertCell(4),
    vote_against = row.insertCell(5),
    vote_abstentions = row.insertCell(6),
    vote_absent = row.insertCell(7);
  vote_action = row.insertCell(8);
  //Giving row a content specific id.
  $(row).attr('id', 'vote-' + pk);
  //Hiding the row so we can fade it in
  $(row).css('display', 'none');
  vote_id.innerHTML = pk;
  vote_last_changed.innerHTML = last_changed;
  vote_by.innerHTML = by;
  vote_on.innerHTML = on;
  vote_in_favour.innerHTML = in_favour;
  vote_against.innerHTML = against;
  vote_abstentions.innerHTML = abstentions;
  vote_absent.innerHTML = absent;
  vote_action.innerHTML = '<a href="javascript:void(0)" class="btn btn-xs btn-primary btn-raised" data-toggle="modal" data-target="#edit-vote" onclick="editVote(' + "'" + pk + "'" + ')" ><i class="material-icons" style="font-size: 18px">mode_edit</i></a><a href="javascript:void(0)" class="btn btn-danger btn-xs btn-raised" onclick="deleteData(' + "'vote', " + "'" + pk + "'" + ')" ><i class="material-icons" style="font-size: 18px">delete</i></a>';
  //Adding pretty color classes and fading in
  $(vote_by).addClass(color);
  $(vote_by).css('color', text_color);
  $(row).fadeIn("slow");
}


function editPoint(pk) {
  var data = "data_type=point&pk=" + pk;
  $.ajax({
    url: data_pk_url,
    data: data,
    success: function(response) {
      $('#point_id_pk').val(response.pk);
      document.getElementById("point_id_committee").options.namedItem(response.committee_by).selected = true;
      document.getElementById("point_id_debate").options.namedItem(response.active_debate).selected = true;
      document.getElementById("point_id_round_no").options.namedItem(response.round_no).selected = true;
      document.getElementById("point_id_point_type").options.namedItem(response.point_type).selected = true;
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
    },
    cache: false
  });
}


function editContent(pk) {
  var data = "data_type=content&pk=" + pk;
  $.ajax({
    url: data_pk_url,
    data: data,
    success: function(response) {
      $('#content_id_pk').val(response.pk);
      $('#content_id_content').val(response.content);
      document.getElementById("content_id_committee").options.namedItem(response.committee_by).selected = true;
      document.getElementById("content_id_debate").options.namedItem(response.active_debate).selected = true;
      document.getElementById("content_id_point_type").options.namedItem(response.point_type).selected = true;
    },
    cache: false
  });
}

function editVote(pk) {
  var data = "data_type=vote&pk=" + pk;
  $.ajax({
    url: data_pk_url,
    data: data,
    success: function(response) {
      $('#vote_id_pk').val(response.pk);
      $('#vote_id_in_favour').val(response.in_favour);
      $('#vote_id_against').val(response.against);
      $('#vote_id_abstentions').val(response.abstentions);
      $('#vote_id_absent').val(response.absent);
      document.getElementById("vote_id_committee").options.namedItem(response.committee_by).selected = true;
      document.getElementById("vote_id_debate").options.namedItem(response.active_debate).selected = true;
      getTotal();
    },
    cache: false
  });
}


function getTotal() {
  var in_favour = $('#vote_id_in_favour'),
    against = $('#vote_id_against'),
    abstentions = $('#vote_id_abstentions'),
    absent = $('#vote_id_absent');
  total = parseInt(in_favour.val()) + parseInt(against.val()) + parseInt(abstentions.val()) + parseInt(absent.val());
  $('#vote-total').html(total);
}

$("input").keyup(getTotal);

$(document).ready(getTotal);

$('#point-form').on('submit', function(event) {
  event.preventDefault();
  console.log("Point form submitted!"); // sanity check
  savePoint();
});

$('#content-form').on('submit', function(event) {
  event.preventDefault();
  console.log("Content form submitted!"); // sanity check
  saveContent();
});

$('#vote-form').on('submit', function(event) {
  event.preventDefault();
  console.log("Vote form submitted!"); // sanity check
  saveVote();
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
      'data-type': 'point',
      'session': $('#point_id_session').val(),
      'pk': $('#point_id_pk').val(),
      'committee': $('#point_id_committee').val(),
      'debate': $('#point_id_debate').val(),
      'round_no': $('#point_id_round_no').val(),
      'point_type': $('#point_id_point_type').val(),
      'subtopics': JSON.stringify(subtopics_array),
      'all_subtopics': JSON.stringify(all_subtopics)
    },
    success: function(json) {
      console.log('success!');
      console.log(json);
      deleteInput('point-' + json.pk);
      createPoint(0, json.pk, json.last_changed, json.by, json.debate, json.round_no, json.point_type, json.subtopics, json.committee_color, json.committee_text_color);
      $('#edit-point').modal('hide');
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

function saveContent() {
  $.ajax({
    url: data_pk_url,
    type: "POST",
    data: {
      'data-type': 'content',
      'session': $('#content_id_session').val(),
      'pk': $('#content_id_pk').val(),
      'committee': $('#content_id_committee').val(),
      'debate': $('#content_id_debate').val(),
      'point_type': $('#content_id_point_type').val(),
      'content': $('#content_id_content').val()
    },
    success: function(json) {
      console.log('success!');
      console.log(json);
      deleteInput('content-' + json.pk);
      createContent(0, json.pk, json.last_changed, json.by, json.debate, json.content, json.point_type, json.committee_color, json.committee_text_color);
      $('#edit-content').modal('hide');
      $('#results').html('<div class="alert alert-dismissable alert-success">'+
                          '<button type="button" class="close" data-dismiss="alert">×</button>'+
                          'Content Point Saved</a>.'+
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

function saveVote() {
  $.ajax({
    url: data_pk_url,
    type: "POST",
    data: {
      'data-type': 'vote',
      'session': $('#vote_id_session').val(),
      'pk': $('#vote_id_pk').val(),
      'committee': $('#vote_id_committee').val(),
      'debate': $('#vote_id_debate').val(),
      'in_favour': $('#vote_id_in_favour').val(),
      'against': $('#vote_id_against').val(),
      'abstentions': $('#vote_id_abstentions').val(),
      'absent': $('#vote_id_absent').val()
    },
    success: function(json) {
      console.log('success!');
      console.log(json);
      deleteInput('vote-' + json.pk);
      createVote(0, json.pk, json.last_changed, json.by, json.debate, json.in_favour, json.against, json.abstentions, json.absent, json.committee_color, json.committee_text_color);
      $('#edit-vote').modal('hide');
      $('#results').html('<div class="alert alert-dismissable alert-success">'+
                          '<button type="button" class="close" data-dismiss="alert">×</button>'+
                          'Vote Saved</a>.'+
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

function deleteData(type, pk) {
  if (confirm('Are you sure you want to delete this?') === true) {
    $.ajax({
      url: data_pk_url,
      type: "POST",
      data: {
        'delete': true,
        'data-type': type,
        'pk': pk
      },
      success: function(json) {
        console.log('Delete success!');
        deleteInput(type + '-' + pk);
      },
      error: function(xhr, errmsg, err) {
        $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: " + errmsg +
          " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
        console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
      },
      cache: false
    });
  }
}

jQuery(
  function($) {
    $('#content-div').bind('scroll', function() {
      if ($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {
        if (total_content_displayed < total_content) {
          requestData('content', offset_content, 10);
        }
      }
    });
  }
);

jQuery(
  function($) {
    $('#point-div').bind('scroll', function() {
      if ($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {
        if (total_points_displayed < total_point) {
          requestData('point', offset_point, 10);
        }
      }
    });
  }
);

jQuery(
  function($) {
    $('#vote-div').bind('scroll', function() {
      if ($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {
        if (total_votes_displayed < total_vote) {
          requestData('vote', offset_vote, 10);
        }
      }
    });
  }
);


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
