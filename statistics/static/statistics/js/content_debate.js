var latest_pk,
    offset,
    total;

var total_displayed = 0;

function requestContentPointData() {
  $.ajax({
    url: content_url,
    data: "offset=" + 0 + "&count=" + 10,
    success: function (response) {
      var table = document.getElementById("content-table").getElementsByTagName('tbody')[0];
      latest_pk = response.contentpoints[0].pk;
      total = response.totalpoints;
      offset = 10;
      if (typeof response.contentpoints[0].contentpoint !== "undefined"){
        for (point of response.contentpoints){
          total_displayed++;
          var row = table.insertRow(table.rows.length);
          var committee = row.insertCell(0);
          var content = row.insertCell(1);
          var type = row.insertCell(2);
          $(row).attr('id', point.pk)
          committee.innerHTML = point.committee_by;
          content.innerHTML = point.contentpoint;
          type.innerHTML = point.point_type;
          $(row).css('display', 'none');
          $(row).fadeIn("slow");
        }
      }
    },
    cache: false
  });
};
function requestMoreContent() {
  $.ajax({
    url: content_url,
    data: "offset=" + offset + "&count=" + 10,
    success: function (response) {
      var table = document.getElementById("content-table").getElementsByTagName('tbody')[0];
      total = response.totalpoints;
      offset += 10;
      if (typeof response.contentpoints[0].contentpoint !== "undefined"){
        for (point of response.contentpoints){
          total_displayed++;
          var row = table.insertRow(table.rows.length);
          var committee = row.insertCell(0);
          var content = row.insertCell(1);
          var type = row.insertCell(2);
          $(row).attr('id', point.pk)
          committee.innerHTML = point.committee_by;
          content.innerHTML = point.contentpoint;
          type.innerHTML = point.point_type;
          $(row).css('display', 'none');
          $(row).fadeIn("slow");
        }
      }
    },
    cache: false
  });
};
function requestNewContent(){
  $.ajax({
    url: newcontenturl,
    data: "pk=" + latest_pk,
    success: function (response) {
      var table = document.getElementById("content-table").getElementsByTagName('tbody')[0];
      latest_pk = response.contentpoints[0].pk;
      total = response.totalpoints;
      if (typeof response.contentpoints[0].contentpoint !== "undefined") {
        for (point of response.contentpoints){
          offset++;
          total_displayed++;
          var row = table.insertRow(0);
          var committee = row.insertCell(0);
          var content = row.insertCell(1);
          var type = row.insertCell(2);
          $(row).attr('id', point.pk)
          committee.innerHTML = point.committee_by;
          content.innerHTML = point.contentpoint;
          type.innerHTML = point.point_type;
          $(row).css('display', 'none');
          $(row).fadeIn("slow");
        }
      }
      setTimeout(requestNewContent, 3000);
    },
    cache: false
  });
};

$(document).ready(function(){
  requestContentPointData();
  setTimeout(function () {
        requestNewContent();
    }, 5000);
});

jQuery(
  function($)
  {
    $('#content-div').on('scroll', function()
    {
      if($(this).scrollTop() + $(this).innerHeight()>=$(this)[0].scrollHeight)
      {
        if (total_displayed < total) {
          requestMoreContent();
        }
      }
    })
  }
);
