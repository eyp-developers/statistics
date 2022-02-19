var offset,
  total;

var total_displayed = 0;
var latest_pk = 0;

function requestContentPointData() {
  $.ajax({
    url: content_url,
    data: "offset=" + 0 + "&count=" + 20,
    success: function(response) {
      var table = document.getElementById("content-table").getElementsByTagName('tbody')[0];
      if (typeof response.contentpoints[0].pk !== "undefined") {
        latest_pk = response.contentpoints[0].pk;
      }
      total = response.totalpoints;
      offset = 20;
      if (typeof response.contentpoints[0].contentpoint !== "undefined") {
        response.contentpoints.forEach(function(point) {
          total_displayed++;
          var row = table.insertRow(table.rows.length);
          var committee = row.insertCell(0);
          var content = row.insertCell(1);
          var type = row.insertCell(2);
          $(row).attr('id', point.pk);
          committee.innerHTML = point.committee_by;
          content.innerHTML = point.contentpoint;
          if (point.point_type === 'P') {
            type.innerHTML = '<img src="' + point_img + '" height="30" >';
          } else {
            type.innerHTML = '<img src="' + dr_img + '" height="30" >';
          }
          $(row).css('display', 'none');
          $(committee).addClass(point.committee_color);
          $(committee).css('color', point.committee_text_color);
          $(row).fadeIn("slow");
        });
      }
    },
    cache: false
  });
}

function requestMoreContent() {
  $.ajax({
    url: content_url,
    data: "offset=" + offset + "&count=" + 10,
    success: function(response) {
      var table = document.getElementById("content-table").getElementsByTagName('tbody')[0];
      total = response.totalpoints;
      offset += 10;
      if (typeof response.contentpoints[0].contentpoint !== "undefined") {
        response.contentpoints.forEach(function(point) {
          total_displayed++;
          var row = table.insertRow(table.rows.length);
          var committee = row.insertCell(0);
          var content = row.insertCell(1);
          var type = row.insertCell(2);
          $(row).attr('id', point.pk);
          committee.innerHTML = point.committee_by;
          content.innerHTML = point.contentpoint;
          if (point.point_type === 'P') {
            type.innerHTML = '<img src="' + point_img + '" height="30" >';
          } else {
            type.innerHTML = '<img src="' + dr_img + '" height="30" >';
          }
          $(row).css('display', 'none');
          $(committee).addClass(point.committee_color);
          $(committee).css('color', point.committee_text_color);
          $(row).fadeIn("slow");
        });
      }
    },
    cache: false
  });
}

function requestNewContent() {
  $.ajax({
    url: newcontenturl,
    data: "pk=" + latest_pk,
    success: function(response) {
      var table = document.getElementById("content-table").getElementsByTagName('tbody')[0];
      latest_pk = response.contentpoints[0].pk;
      total = response.totalpoints;
      if (typeof response.contentpoints[0].contentpoint !== "undefined") {
        response.contentpoints.forEach(function(point) {
          offset++;
          total_displayed++;
          var row = table.insertRow(0);
          var committee = row.insertCell(0);
          var content = row.insertCell(1);
          var type = row.insertCell(2);
          $(row).attr('id', point.pk);
          committee.innerHTML = point.committee_by;
          content.innerHTML = point.contentpoint;
          if (point.point_type === 'P') {
            type.innerHTML = '<img src="' + point_img + '" height="30" >';
          } else {
            type.innerHTML = '<img src="' + dr_img + '" height="30" >';
          }
          $(row).css('display', 'none');
          $(committee).addClass(point.committee_color);
          $(committee).css('color', point.committee_text_color);
          $(row).fadeIn("slow");
        });
      }
      setTimeout(requestNewContent, 3000);
    },
    cache: false
  });
}

$(document).ready(function() {
  requestContentPointData();
  setTimeout(function() {
    requestNewContent();
  }, 5000);
});

jQuery(
  function($) {
    $('#content-div').bind('scroll', function() {
      if ($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {
        if (total_displayed < total) {
          requestMoreContent();
        }
      }
    });
  }
);
