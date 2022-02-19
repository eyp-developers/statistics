var chart_gender;

function requestStatisticsData() {
    $.ajax({
        url: gender_statistics_url,
        success: function(response) {

            var chart_gender = $('#gender').highcharts();
            chart_gender.xAxis[0].setCategories(response.categories, false);
            chart_gender.series[0].setData(response.female, false);
            chart_gender.series[1].setData(response.male, false);
            chart_gender.series[2].setData(response.other, false);
            chart_gender.redraw();

            // call it again after two seconds
            setTimeout(requestStatisticsData, 2000);
        },
        cache: false
    });
}

$(document).ready(function() {
    chart_gender = new Highcharts.Chart({
        chart: {
            renderTo: 'gender',
            defaultSeriesType: 'bar',
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
                text: 'Gender Statistics'
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
        plotOptions: {
            bar: {
                stacking: 'percent',
                dataLabels: {
                    enabled: false,
                    color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white',
                    style: {
                        textShadow: '0 0 3px black'
                    }
                }
            }
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
        series: [{
            name: 'Female',
            data: [],
            color: '#428FCD'
        },
        {
            name: 'Male',
            data: [],
            color: '#2E4496'
        },
        {
            name: 'Other',
            data: [],
            color: '#FEEB36'
        }]
    });
});
