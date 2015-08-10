var chart_points;
var chart_subtopics;
var chart_committee_votes;
var chart_debate_votes;
var i_subtopics;
var i_latest;

function requestData() {
    $.ajax({
        url: debate_url,
        success: function(response) {

            var chart_points = $('#points').highcharts();
            chart_points.xAxis[0].setCategories(response.committees_list, false);
            chart_points.series[0].setData(response.drs_made, false);
            chart_points.series[1].setData(response.points_made, false);
            chart_points.redraw();

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

            var chart_subtopics = $('#subtopics').highcharts();
            chart_subtopics.xAxis[0].setCategories(response.subtopics, false);
            for (i_subtopics = 0; i_subtopics < response.subtopic_points.length; ++i_subtopics) {
              chart_subtopics.series[i_subtopics].setData(response.subtopic_points[i_subtopics], false);
            }
            chart_subtopics.redraw();

            $('#total_points').html('Total Points: ' + response.points_total);
            $('#total_type').html('(' + response.type_point + ' Points, ' + response.type_dr + ' Direct Responses)');
            $('#latest_point').html('Latest Point By: ' + response.latest_point_name);

            var latest_on = 'On: '
            for (i_latest = 0; i_latest < response.latest_point_subtopics.length; ++i_latest) {
              latest_on += response.latest_point_subtopics[i_latest] + ', '
            }
            $('#latest_on').html(latest_on);

            $('#total_counted').html('Votes Counted: ' + response.total_counted);
            $('#committees_counted').html('Committees Counted: ' + response.committees_voted + '/' + response.committees_count);
            $('#in_favour').html('In Favour: ' + response.debate_in_favour[0]);
            $('#against').html('Against: ' + response.debate_against[0]);
            $('#abstentions').html('Abstentions: ' + response.debate_abstentions[0]);
            $('#absent').html('Absent: ' + response.debate_absent[0]);

            // call it again after one second
            setTimeout(requestData, 1000);
        },
        cache: false
    });
}

$(document).ready(function() {
    chart_points = new Highcharts.Chart({
        chart: {
            renderTo: 'points',
            defaultSeriesType: 'column',
            events: {
                load: requestData
            }
        },
        title: false,
        xAxis: {
            categories: []
        },
        yAxis: {
            min: 0,
            title: {
                text: 'Number of Points'
            },
            stackLabels: {
                enabled: true,
                style: {
                    fontWeight: 'bold',
                    color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                }
            }
        },
        credits: {
            enabled: false
        },
        legend: {
            align: 'right',
            x: -30,
            verticalAlign: 'top',
            y: 25,
            floating: true,
            backgroundColor: (Highcharts.theme && Highcharts.theme.background2) || 'white',
            borderColor: '#CCC',
            borderWidth: 1,
            shadow: false
        },
        tooltip: {
            formatter: function () {
                return '<b>' + this.x + '</b><br/>' +
                    this.series.name + ': ' + this.y + '<br/>' +
                    'Total: ' + this.point.stackTotal;
            }
        },
        plotOptions: {
            column: {
                stacking: 'normal',
                dataLabels: {
                    enabled: false,
                    color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white',
                    style: {
                        textShadow: '0 0 3px black'
                    }
                }
            }
        },
        series: [{
            name: 'Direct Response',
            data: [],
            color: '#b62424'
        },
        {
            name: 'Point',
            data: [],
            color: '#1e4e8a'
        }]
    });
    chart_committee_votes = new Highcharts.Chart({
        chart: {
          renderTo: 'committee_votes',
          defaultSeriesType: 'column'
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
    chart_debate_votes = new Highcharts.Chart({
        chart: {
          renderTo: 'debate_votes',
          defaultSeriesType: 'column'
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
    chart_subtopics = new Highcharts.Chart({
      chart: {
          renderTo: 'subtopics',
          type: 'bar'
        },
        title: false,
        xAxis: {
            categories: [],
            crosshair: true
        },
        yAxis: {
            min: 0,
            title: false,
            reversedStacks: false
        },
        tooltip: {
          headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
          pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                '<td style="padding:0"><b>{point.y}</b></td></tr>',
          footerFormat: '</table>',
          shared: true,
          useHTML: true
        },
        legend: {
            reversed: false
        },
        credits: false,
        plotOptions: {
            series: {
                stacking: 'normal'
            }
        },
        series: []
    });
    var i = 1;
    var name;
    var color_array;
    color_array = ["#fff", "#1e4e8a", "#ffd326", "#02c75f", "#b62424", "#b61db1", "#323232"]
    while (i <= max_rounds) {
      name = 'Round ' + i;
      chart_subtopics.addSeries({
        name: name,
        data: [],
        color: color_array[i]
      });
      i++;
    }
});
