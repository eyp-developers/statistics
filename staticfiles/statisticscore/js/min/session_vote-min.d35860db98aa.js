function requestVoteData(){$.ajax({url:voting_url,success:function(t){var a=$("#votes").highcharts();a.xAxis[0].setCategories(t.committees,!1),a.series[0].setData(t.in_favour,!1),a.series[1].setData(t.against,!1),a.series[2].setData(t.abstentions,!1),a.series[3].setData(t.absent,!1),a.redraw(),$("#total_votes").html("Total Votes: "+t.total_votes),$("#total_in_favour").html("Total In Favour: "+t.total_in_favour),$("#total_against").html("Total Against: "+t.total_against),$("#total_abstentions").html("Total Abstentions: "+t.total_abstentions),$("#total_absent").html("Total Absent: "+t.total_absent),setTimeout(requestData,1e3)},cache:!1})}var chart_votes;$(document).ready(function(){chart_votes=new Highcharts.Chart({chart:{renderTo:"votes",defaultSeriesType:"column",backgroundColor:"#fff",events:{load:requestVoteData}},title:!1,credits:!1,xAxis:{categories:[],crosshair:!0},yAxis:{min:0,title:{text:"Votes"}},tooltip:{headerFormat:'<span style="font-size:10px">{point.key}</span><table>',pointFormat:'<tr><td style="color:{series.color};padding:0">{series.name}: </td><td style="padding:0"><b>{point.y}</b></td></tr>',footerFormat:"</table>",shared:!0,useHTML:!0},series:[{name:"In Favour",data:[],color:"#4CAF50"},{name:"Against",data:[],color:"#F44336"},{name:"Abstentions",data:[],color:"#3F51B5"},{name:"Absent",data:[],color:"#FFC107"}]})});