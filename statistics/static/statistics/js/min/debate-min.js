function requestData(){$.ajax({url:debate_url,success:function(t){var e=$("#points").highcharts();e.xAxis[0].setCategories(t.committees_list,!1),e.series[0].setData(t.drs_made,!1),e.series[1].setData(t.points_made,!1),e.redraw();var s=$("#committee_votes").highcharts();s.xAxis[0].setCategories(t.committees_voted_list,!1),s.series[0].setData(t.committees_in_favour,!1),s.series[1].setData(t.committees_against,!1),s.series[2].setData(t.committees_abstentions,!1),s.series[3].setData(t.committees_absent,!1),s.redraw();var a=$("#debate_votes").highcharts();a.xAxis[0].setCategories(t.committee_name,!1),a.series[0].setData(t.debate_in_favour,!1),a.series[1].setData(t.debate_against,!1),a.series[2].setData(t.debate_abstentions,!1),a.series[3].setData(t.debate_absent,!1),a.redraw();var o=$("#subtopics").highcharts();for(o.xAxis[0].setCategories(t.subtopics,!1),i_subtopics=0;i_subtopics<t.subtopic_points.length;++i_subtopics)o.series[i_subtopics].setData(t.subtopic_points[i_subtopics],!1);o.redraw(),$("#total_points").html("Total Points: "+t.points_total),$("#total_type").html("("+t.type_point+" Points, "+t.type_dr+" Direct Responses)"),$("#latest_point").html("Latest Point By: "+t.latest_point_name);var i="On: ";for(i_latest=0;i_latest<t.latest_point_subtopics.length;++i_latest)i+=t.latest_point_subtopics[i_latest]+", ";$("#latest_on").html(i),$("#total_counted").html("Votes Counted: "+t.total_counted),$("#committees_counted").html("Committees Counted: "+t.committees_voted+"/"+t.committees_count),$("#in_favour").html("In Favour: "+t.debate_in_favour[0]),$("#against").html("Against: "+t.debate_against[0]),$("#abstentions").html("Abstentions: "+t.debate_abstentions[0]),$("#absent").html("Absent: "+t.debate_absent[0]),setTimeout(requestData,1e3)},cache:!1})}var chart_points,chart_subtopics,chart_committee_votes,chart_debate_votes,i_subtopics,i_latest,debate_url="http://localhost:8000/api/session/"+session+"/debate/"+committee;$(document).ready(function(){chart_points=new Highcharts.Chart({chart:{renderTo:"points",defaultSeriesType:"column",events:{load:requestData}},title:!1,xAxis:{categories:[]},yAxis:{min:0,title:{text:"Number of Points"},stackLabels:{enabled:!0,style:{fontWeight:"bold",color:Highcharts.theme&&Highcharts.theme.textColor||"gray"}}},credits:{enabled:!1},legend:{align:"right",x:-30,verticalAlign:"top",y:25,floating:!0,backgroundColor:Highcharts.theme&&Highcharts.theme.background2||"white",borderColor:"#CCC",borderWidth:1,shadow:!1},tooltip:{formatter:function(){return"<b>"+this.x+"</b><br/>"+this.series.name+": "+this.y+"<br/>Total: "+this.point.stackTotal}},plotOptions:{column:{stacking:"normal",dataLabels:{enabled:!1,color:Highcharts.theme&&Highcharts.theme.dataLabelsColor||"white",style:{textShadow:"0 0 3px black"}}}},series:[{name:"Direct Response",data:[],color:"#b62424"},{name:"Point",data:[],color:"#1e4e8a"}]}),chart_committee_votes=new Highcharts.Chart({chart:{renderTo:"committee_votes",defaultSeriesType:"column"},title:!1,credits:!1,xAxis:{categories:[],crosshair:!0},yAxis:{min:0,title:{enabled:!1}},legend:{enabled:!1},tooltip:{headerFormat:'<span style="font-size:10px">{point.key}</span><table>',pointFormat:'<tr><td style="color:{series.color};padding:0">{series.name}: </td><td style="padding:0"><b>{point.y}</b></td></tr>',footerFormat:"</table>",shared:!0,useHTML:!0},series:[{name:"For",data:[],color:"#02c75f"},{name:"Against",data:[],color:"#b62424"},{name:"Abstentions",data:[],color:"#1e4e8a"},{name:"Absent",data:[],color:"#ffd326"}]}),chart_debate_votes=new Highcharts.Chart({chart:{renderTo:"debate_votes",defaultSeriesType:"column"},title:{text:"Total Standing"},credits:!1,xAxis:{categories:[],crosshair:!1},yAxis:{min:0,title:{text:"Votes"}},tooltip:{headerFormat:'<span style="font-size:10px">{point.key}</span><table>',pointFormat:'<tr><td style="color:{series.color};padding:0">{series.name}: </td><td style="padding:0"><b>{point.y}</b></td></tr>',footerFormat:"</table>",shared:!0,useHTML:!0},series:[{name:"In Favour",data:[],color:"#02c75f"},{name:"Against",data:[],color:"#b62424"},{name:"Abstentions",data:[],color:"#1e4e8a"},{name:"Absent",data:[],color:"#ffd326"}]}),chart_subtopics=new Highcharts.Chart({chart:{renderTo:"subtopics",type:"bar"},title:!1,xAxis:{categories:[],crosshair:!0},yAxis:{min:0,title:!1,reversedStacks:!1},tooltip:{headerFormat:'<span style="font-size:10px">{point.key}</span><table>',pointFormat:'<tr><td style="color:{series.color};padding:0">{series.name}: </td><td style="padding:0"><b>{point.y}</b></td></tr>',footerFormat:"</table>",shared:!0,useHTML:!0},legend:{reversed:!1},credits:!1,plotOptions:{series:{stacking:"normal"}},series:[]});var t=1,e,s;for(s=["#fff","#1e4e8a","#ffd326","#02c75f","#b62424","#b61db1","#323232"];t<=max_rounds;)e="Round "+t,chart_subtopics.addSeries({name:e,data:[],color:s[t]}),t++});