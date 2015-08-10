var chart_points;
var chart_votes;

function requestData() {
    $.ajax({
        url: session_url,
        success: function(response) {

            var chart_points = $('#points').highcharts();
            chart_points.xAxis[0].setCategories(response.committees, false);
            chart_points.series[0].setData(response.drs, false);
            chart_points.series[1].setData(response.points, false);
            chart_points.redraw();

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
  var $debates = $('.debates')
        $debates.masonry({
            itemSelector: '.debate-box',
            columnWidth: '.debate-box',
            transitionDuration: 0
        });
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
    chart_votes = new Highcharts.Chart({
        chart: {
          renderTo: 'votes',
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
