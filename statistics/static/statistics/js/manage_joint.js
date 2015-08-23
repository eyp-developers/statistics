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
  $.ajax({
    url: data_pk_url,
    data: "data_type=point&pk=" + pk,
    success: function (response) {
      
    },
    cache: false
  });
}
function getTotal () {
  var in_favour = $('#id_in_favour'),
      against = $('#id_against'),
      abstentions = $('#id_abstentions'),
      absent = $('#id_absent');
  total = parseInt(in_favour.val()) + parseInt(against.val()) + parseInt(abstentions.val()) + parseInt(absent.val());
  $('#vote-total').html(total);
}

$( "input" ).keyup( getTotal );

$(document).ready( getTotal );

requestData('point', 0, 10);
requestData('content', 0, 10);
requestData('vote', 0, 10);
