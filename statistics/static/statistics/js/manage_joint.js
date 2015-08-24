var offset_point = 0,
    offset_content = 0,
    total_point,
    total_content,
    total_points_displayed = 0,
    total_content_displayed = 0,
    latest_point_pk = 0,
    latest_content_pk = 0;

var offset_vote = 0,
    total_vote,
    total_votes_displayed = 0,
    latest_vote_pk = 0;

var all_subtopics;

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
function deleteInput(id){
  document.getElementById(id).remove();
}

function requestData(type, offset, count) {
    $.ajax({
      url: data_url,
      data: "data_type=" + type + "&offset=" + offset + "&count=" + count,
      success: function (response) {
        if (type === 'point') {
          if (typeof response.datapoints[0].pk !== "undefined") {
            latest_point_pk = response.datapoints[0].pk;
          }
          total_point = response.totaldata;
          offset_point += count;
          if (typeof response.datapoints[0].committee_by !== "undefined") {
            response.datapoints.forEach(function(point) {
              createPoint(point.pk, point.last_changed, point.committee_by, point.active_debate, point.round_no, point.point_type, point.subtopics, point.committee_color, point.committee_text_color);
            });
          }
        } else if (type === 'content') {
          if (typeof response.datapoints[0].pk !== "undefined") {
            latest_content_pk = response.datapoints[0].pk;
          }
          total_content = response.totaldata;
          offset_content += count;
          if (typeof response.datapoints[0].content !== "undefined") {
            response.datapoints.forEach(function(content) {
              createContent(content.pk, content.last_changed, content.committee_by, content.active_debate, content.content, content.point_type, content.committee_color, content.committee_text_color);
            });
          }
        } else if (type === 'vote') {
          if (typeof response.datapoints[0].pk !== "undefined") {
            latest_vote_pk = response.datapoints[0].pk;
          }
          total_vote = response.totaldata;
          offset_vote += count;
          if (typeof response.datapoints[0].committee_by !== "undefined") {
            response.datapoints.forEach(function(vote) {
              createVote(vote.pk, vote.last_changed, vote.committee_by, vote.active_debate, vote.in_favour, vote.against, vote.abstentions, vote.absent, vote.committee_color, vote.committee_text_color);
            });
          }
        }
      },
      cache: false
    });
}

function createPoint(pk, last_changed, by, on, round, type, subtopics, color, text_color) {
  //Setting up the new row in the table
  var table = document.getElementById("point-table").getElementsByTagName('tbody')[0],
      row = table.insertRow(0),
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
  point_action.innerHTML = '<a href="javascript:void(0)" class="btn btn-xs btn-material-' + session_color + '-800 btn-fab btn-raised mdi-content-create" data-toggle="modal" data-target="#edit-point" onclick="editPoint(' + "'" + pk + "'" + ')" ></a><a href="javascript:void(0)" class="btn btn-danger btn-fab btn-raised mdi-action-delete" onclick="" ></a>';
  //Adding pretty color classes
  $(point_by).addClass('label-material-' + color + '-400');
  $(point_by).css('color', text_color);
  $(row).fadeIn("slow");
}


function createContent(pk, last_changed, by, on, content, type, color, text_color){
  //Setting up the new row in the table
  var table = document.getElementById("content-table").getElementsByTagName('tbody')[0],
      row = table.insertRow(0),
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
  content_action.innerHTML = '<a href="javascript:void(0)" class="btn btn-xs btn-material-' + session_color + '-800 btn-fab btn-raised mdi-content-create" data-toggle="modal" data-target="#edit-content" onclick="editContent(' + "'" + pk + "'" + ')" ></a><a href="javascript:void(0)" class="btn btn-danger btn-fab btn-raised mdi-action-delete" onclick="" ></a>';
  //Adding pretty color classes and fading in
  $(content_by).addClass('label-material-' + color + '-400');
  $(content_by).css('color', text_color);
  $(row).fadeIn("slow");
}


function createVote(pk, last_changed, by, on, in_favour, against, abstentions, absent, color, text_color){
  //Setting up the new row in the table
  var table = document.getElementById("vote-table").getElementsByTagName('tbody')[0],
      row = table.insertRow(0),
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
  vote_action.innerHTML = '<a href="javascript:void(0)" class="btn btn-xs btn-material-' + session_color + '-800 btn-fab btn-raised mdi-content-create" data-toggle="modal" data-target="#edit-vote" onclick="editVote(' + "'" + pk + "'" + ')" ></a><a href="javascript:void(0)" class="btn btn-danger btn-fab btn-raised mdi-action-delete" onclick="" ></a>';
  //Adding pretty color classes and fading in
  $(vote_by).addClass('label-material-' + color + '-400');
  $(vote_by).css('color', text_color);
  $(row).fadeIn("slow");
}


function editPoint(pk) {
  var data = "data_type=point&pk=" + pk;
  $.ajax({
    url: data_pk_url,
    data: data,
    success: function (response) {
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
        all_subtopics.push(subtopic.pk.toString());
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
    success: function (response) {
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
    success: function (response) {
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


function getTotal () {
  var in_favour = $('#vote_id_in_favour'),
      against = $('#vote_id_against'),
      abstentions = $('#vote_id_abstentions'),
      absent = $('#vote_id_absent');
  total = parseInt(in_favour.val()) + parseInt(against.val()) + parseInt(abstentions.val()) + parseInt(absent.val());
  $('#vote-total').html(total);
}

$( "input" ).keyup( getTotal );

$(document).ready( getTotal );

$('#point-form').on('submit', function(event){
    event.preventDefault();
    console.log("Point form submitted!");  // sanity check
    savePoint();
});

$('#content-form').on('submit', function(event){
    event.preventDefault();
    console.log("Content form submitted!");  // sanity check
    savePoint();
});

$('#vote-form').on('submit', function(event){
    event.preventDefault();
    console.log("Vote form submitted!");  // sanity check
    savePoint();
});

function savePoint() {
  console.log($('#point_id_pk').val());
  console.log($('#point_id_committee').val());
  console.log($('#point_id_debate').val());
  console.log($('#point_id_round_no').val());
  console.log($('#point_id_point_type').val());
  console.log($('#point_id_subtopics').val());
  console.log(all_subtopics);
  $.ajax({
    url: data_pk_url,
    type: "POST",
    data: {'data-type': 'point',
      'session': $('#point_id_session').val(),
      'pk': $('#point_id_pk').val(),
      'committee': $('#point_id_committee').val(),
      'debate': $('#point_id_debate').val(),
      'round_no': $('#point_id_pk').val(),
      'point_type': $('#point_id_point_type').val(),
      'subtopics': $('#point_id_subtopics').val(),
      'all_subtopics': all_subtopics
    },
    success: function(json) {
      deleteInput('point-' + $('#point_id_pk').val());
      createPoint(pk, last_changed, by, on, round, type, subtopics, color, text_color);
    },
    cache: false
  });
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


requestData('point', 0, 10);
requestData('content', 0, 10);
requestData('vote', 0, 10);
