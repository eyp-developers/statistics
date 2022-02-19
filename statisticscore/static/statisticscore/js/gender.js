var total_offset = 0,
  total,
  total_displayed = 0,
  latest_pk = 0,
  new_gender = false;


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

function requestData(offset, count) {
  $.ajax({
    url: data_url,
    data: "data_type=gender&offset=" + offset + "&count=" + count,
    success: function(response) {
        total = response.totaldata;
        total_offset += count;
        if (typeof response.datapoints[0].gender !== "undefined") {
          response.datapoints.forEach(function(point) {
            createGender(-1, point.pk, point.last_changed, point.committee, point.gender);
            total_displayed++;
          });
        }
        if (new_gender === false) {
          if (typeof response.datapoints[0].pk !== "undefined") {
            latest_pk = response.datapoints[0].pk;
          }
          requestNewData('point');
          new_gender = true;
        }
    },
    cache: false
  });
}

function requestNewData(type) {
  var new_latest = latest_pk;
  $.ajax({
    url: data_latest_url,
    data: "data_type=gender&pk=" + new_latest,
    success: function(response) {
        if (typeof response.datapoints[0].pk !== "undefined") {
          latest_pk = response.datapoints[0].pk;
        }
        total = response.totaldata;
        if (typeof response.datapoints[0].gender !== "undefined") {
          response.datapoints.forEach(function(point) {
            total_offset++;
            createGender(0, point.pk, point.last_changed, point.committee, point.gender);
            total_displayed++;
          });
        }

      setTimeout(requestNewData, 3000, type);
    },
    cache: false
  });
}

function createGender(where, pk, last_changed, committee, gender) {
  //Setting up the new row in the table
  var table = document.getElementById("gender-table").getElementsByTagName('tbody')[0],
    row = table.insertRow(where),
    gender_id = row.insertCell(0),
    gender_last_changed = row.insertCell(1),
    gender_committee = row.insertCell(2),
    gender_gender = row.insertCell(3),
    gender_actions = row.insertCell(4);
  //Giving the row a point-specific id.
  $(row).attr('id', 'gender-' + pk);
  //Hiding the row so we can fade it in.
  $(row).css('display', 'none');
  //Assigning cell values
  gender_id.innerHTML = pk;
  gender_last_changed.innerHTML = last_changed;
  gender_committee.innerHTML = committee;
  gender_gender.innerHTML = gender;
  gender_actions.innerHTML = '<a href="javascript:void(0)" class="btn btn-danger btn-xs btn-raised" onclick="deleteData(' + "'gender', " + "'" + pk + "'" + ')" ><i class="material-icons" style="font-size: 18px">delete</i></a>';
  $(row).fadeIn("slow");
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
    $('#gender-div').bind('scroll', function() {
      if ($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {
        if (total_displayed < total) {
          requestData(total_offset, 10);
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
