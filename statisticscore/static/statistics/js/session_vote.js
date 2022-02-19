var chart_votes;

function requestVoteData() {
    $.ajax({
        url: voting_url,
        success: function(response) {

            var chart_votes = $('#votes').highcharts();
            chart_votes.xAxis[0].setCategories(response.committees, false);
            chart_votes.series[0].setData(response.in_favour, false);
            chart_votes.series[1].setData(response.against, false);
            chart_votes.series[2].setData(response.abstentions, false);
            chart_votes.series[3].setData(response.absent, false);
            chart_votes.redraw();

            $('#total_votes').html('Total Votes: ' + response.total_votes);
            $('#total_in_favour').html('Total In Favour: ' + response.total_in_favour);
            $('#total_against').html('Total Against: ' + response.total_against);
            $('#total_abstentions').html('Total Abstentions: ' + response.total_abstentions);
            $('#total_absent').html('Total Absent: ' + response.total_absent);

            // call it again after one second
            setTimeout(requestData, 1000);
        },
        cache: false
    });
}

$(document).ready(function() {
    chart_votes = new Highcharts.Chart({
        chart: {
          renderTo: 'votes',
          defaultSeriesType: 'column',
          backgroundColor: '#fff',
          events: {
              load: requestVoteData
          }
        },
        title: false,
        credits: false,
        xAxis: {
          categories: [],
          crosshair: true
        },
        yAxis: {
          min: 0,
          title: {
            text: 'Votes'
          }
        },
        tooltip: {
          headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
          pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                '<td style="padding:0"><b>{point.y}</b></td></tr>',
          footerFormat: '</table>',
          shared: true,
          useHTML: true
        },
        series: [{
          name: 'In Favour',
          data: [],
          color: '#4CAF50'
        }, {
          name: 'Against',
          data: [],
          color: '#F44336'
        }, {
          name: 'Abstentions',
          data: [],
          color: '#3F51B5'
        }, {
          name: 'Absent',
          data: [],
          color: '#FFC107'
        }]
    });
});
