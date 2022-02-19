var chart_points;
var chart_subtopics;
var i_subtopics;
var i_latest;

function requestStatisticsData() {
    $.ajax({
        url: debate_url,
        success: function(response) {

            var chart_points = $('#points').highcharts();
            chart_points.xAxis[0].setCategories(response.committees_list, false);
            chart_points.series[0].setData(response.drs_made, false);
            chart_points.series[1].setData(response.points_made, false);
            chart_points.redraw();

            var chart_subtopics = $('#subtopics').highcharts();
            chart_subtopics.xAxis[0].setCategories(response.subtopics, false);
            for (i_subtopics = 0; i_subtopics < response.subtopic_points.length; ++i_subtopics) {
              chart_subtopics.series[i_subtopics].setData(response.subtopic_points[i_subtopics], false);
            }
            chart_subtopics.redraw();

            $('#total_points').html('Total Points: ' + response.points_total);
            $('#total_type').html('(' + response.type_point + ' Points, ' + response.type_dr + ' Direct Responses)');
            $('#latest_point').html('Latest Point By: ' + response.latest_point_name);

            var latest_on = 'On: ';
            for (i_latest = 0; i_latest < response.latest_point_subtopics.length; ++i_latest) {
              latest_on += response.latest_point_subtopics[i_latest] + ', ';
            }
            $('#latest_on').html(latest_on);

            if (response.running_order[0] !== undefined) {
              running_html = '<h2>Next Points:</h2>';
              var pos = 0;
              response.running_order.forEach(function(point){
                pos ++;
                running_html += '<h3>' + pos + '. ' + point + '</h3>';
              });
              $('#next').html(running_html);
            } else {
              $('#next').html('');
            }

            // call it again after two seconds
            setTimeout(requestStatisticsData, 2000);
        },
        cache: false
    });
}

$(document).ready(function() {
    chart_points = new Highcharts.Chart({
        chart: {
            renderTo: 'points',
            defaultSeriesType: 'column',
            backgroundColor: '#fff',
            events: {
                load: requestStatisticsData
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
            color: '#F44336'
        },
        {
            name: 'Point',
            data: [],
            color: '#3F51B5'
        }]
    });
    chart_subtopics = new Highcharts.Chart({
      chart: {
          renderTo: 'subtopics',
          type: 'bar',
          backgroundColor: '#fff'
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
    color_array = ["#fff", "#3F51B5", "#F44336", "#673AB7", "#009688",  "#E91E63", "#FFC107", "#607D8B", "#FF5722"];
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
