var chart_points;

function requestData() {
    $.ajax({
        url: session_url,
        success: function(response) {

            var chart_points = $('#points').highcharts();
            chart_points.xAxis[0].setCategories(response.committees, false);
            chart_points.series[0].setData(response.drs, false);
            chart_points.series[1].setData(response.points, false);
            chart_points.redraw();

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
            backgroundColor: '#fff',
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
});
