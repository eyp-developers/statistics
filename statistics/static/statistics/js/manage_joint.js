var offset_point,
    offset_content,
    total_point,
    total_content,
    total_points_displayed = 0,
    total_content_displayed = 0,
    latest_point_pk = 0,
    latest_content_pk = 0;

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
  point_action.innerHTML = '<a href="javascript:void(0)" class="btn btn-xs btn-material-' + session_color + '-800 btn-fab btn-raised mdi-content-create" data-toggle="modal" data-target="#edit-point" onclick="" ></a><a href="javascript:void(0)" class="btn btn-danger btn-fab btn-raised mdi-action-delete" onclick="" ></a>';
  //Adding pretty color classes
  $(point_by).addClass('label-material-' + color + '-400');
  $(point_by).css('color', text_color);
  $(row).fadeIn("slow");
}
