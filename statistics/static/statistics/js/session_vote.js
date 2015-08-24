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
          name: 'For',
          data: [],
          color: '#02c75f'
        }, {
          name: 'Against',
          data: [],
          color: '#b62424'
        }, {
          name: 'Abstentions',
          data: [],
          color: '#1e4e8a'
        }, {
          name: 'Absent',
          data: [],
          color: '#ffd326'
        }]
    });
});
