var chart_committee_votes;
var chart_debate_votes;

function requestVoteData() {
    $.ajax({
        url: vote_url,
        success: function(response) {

          var chart_committee_votes = $('#committee_votes').highcharts();
          chart_committee_votes.xAxis[0].setCategories(response.committees_voted_list, false);
          chart_committee_votes.series[0].setData(response.committees_in_favour, false);
          chart_committee_votes.series[1].setData(response.committees_against, false);
          chart_committee_votes.series[2].setData(response.committees_abstentions, false);
          chart_committee_votes.series[3].setData(response.committees_absent, false);
          chart_committee_votes.redraw();

          var chart_debate_votes = $('#debate_votes').highcharts();
          chart_debate_votes.xAxis[0].setCategories(response.committee_name, false);
          chart_debate_votes.series[0].setData(response.debate_in_favour, false);
          chart_debate_votes.series[1].setData(response.debate_against, false);
          chart_debate_votes.series[2].setData(response.debate_abstentions, false);
          chart_debate_votes.series[3].setData(response.debate_absent, false);
          chart_debate_votes.redraw();

          $('#total_counted').html('Votes Counted: ' + response.total_counted);
          $('#committees_counted').html('Committees Counted: ' + response.committees_voted + '/' + response.committees_count);
          $('#in_favour').html('In Favour: ' + response.debate_in_favour[0]);
          $('#against').html('Against: ' + response.debate_against[0]);
          $('#abstentions').html('Abstentions: ' + response.debate_abstentions[0]);
          $('#absent').html('Absent: ' + response.debate_absent[0]);

          // call it again after one second
          setTimeout(requestVoteData, 1000);
        },
        cache: false
      });
}

$(document).ready(function() {
  chart_committee_votes = new Highcharts.Chart({
      chart: {
        renderTo: 'committee_votes',
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
          enabled: false
        }
      },
      legend: {
        enabled: false
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
  chart_debate_votes = new Highcharts.Chart({
      chart: {
        renderTo: 'debate_votes',
        defaultSeriesType: 'column',
        backgroundColor: '#fff'
      },
      title: {
        text: 'Total Standing'
      },
      credits: false,
      xAxis: {
        categories: [],
        crosshair: false
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
