function deleteInput(t){document.getElementById(t).remove()}function requestPoints(t,e){$.ajax({url:data_url,data:"data_type=predict&offset="+t+"&count="+e+"&committee_id="+committee_id,success:function(t){total=t.totaldata,point_offset+=e,"undefined"!=typeof t.datapoints[0].committee_by&&t.datapoints.forEach(function(t){createPoint(-1,t.pk,t.last_changed,t.active_debate,t.round_no,t.point_type,t.subtopics),total_displayed++}),new_point===!1&&("undefined"!=typeof t.datapoints[0].pk&&(latest_pk=t.datapoints[0].pk),requestNewPoints(),new_point=!0)},cache:!1})}function requestNewPoints(){$.ajax({url:data_latest_url,data:"data_type=predict&pk="+latest_pk+"&committee_id="+committee_id,success:function(t){"undefined"!=typeof t.datapoints[0].pk&&(latest_pk=t.datapoints[0].pk),total=t.totaldata,"undefined"!=typeof t.datapoints[0].committee_by&&t.datapoints.forEach(function(t){point_offset++,createPoint(0,t.pk,t.last_changed,t.active_debate,t.round_no,t.point_type,t.subtopics),total_displayed++}),setTimeout(requestNewPoints,3e3)},cache:!1})}function createPoint(t,e,o,n,i,s,a){var r=document.getElementById("point-table").getElementsByTagName("tbody")[0],l=r.insertRow(t),c=l.insertCell(0),d=l.insertCell(1),p=l.insertCell(2),u=l.insertCell(3),f=l.insertCell(4),m=l.insertCell(5),_=l.insertCell(-1);$(l).attr("id","point-"+e),$(l).css("display","none"),c.innerHTML=e,d.innerHTML=o,p.innerHTML=n,u.innerHTML=i,"P"===s?f.innerHTML='<img src="'+point_img+'" height="30" >':f.innerHTML='<img src="'+dr_img+'" height="30" >',m.innerHTML=a,_.innerHTML='<a href="javascript:void(0)" class="btn btn-xs btn-primary btn-raised mdi-content-create" data-toggle="modal" data-target="#edit-subtopics" onclick="editPoint(\''+e+'\')" ><i class="material-icons" style="font-size: 18px">mode_edit</i></a>',$(l).fadeIn("slow")}function editPoint(t){var e="data_type=predict&pk="+t;$.ajax({url:data_pk_url,data:e,success:function(t){$("#point_id_pk").val(t.pk);for(var e=document.getElementById("point_id_subtopics"),o=0;e.options.length>0;)e.options.remove(0);all_subtopics=[],t.all_subtopics.forEach(function(t){all_subtopics.push({pk:t.pk.toString()});var n=document.createElement("option");n.text=t.subtopic,$(n).attr("id",t.pk),$(n).attr("value",t.pk),e.options.add(n,o),o++}),console.log(all_subtopics),t.subtopics.forEach(function(t){e.options.namedItem(t.pk).selected=!0})}})}function savePoint(){var t=[];$("#point_id_subtopics").val().forEach(function(e){t.push({pk:e})}),$.ajax({url:data_pk_url,type:"POST",data:{"data-type":"predict",pk:$("#point_id_pk").val(),subtopics:JSON.stringify(t),all_subtopics:JSON.stringify(all_subtopics)},success:function(t){console.log("success!"),console.log(t),deleteInput("point-"+t.pk),createPoint(0,t.pk,t.last_changed,t.debate,t.round_no,t.point_type,t.subtopics),$("#edit-subtopics").modal("hide"),$("#results").html('<div class="alert alert-dismissable alert-success"><button type="button" class="close" data-dismiss="alert">×</button>Point Saved</a>.</div>'),window.setTimeout(function(){$(".alert").fadeTo(500,0).slideUp(500,function(){$(this).remove()})},5e3)},error:function(t,e,o){$("#results").html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+e+" <a href='#' class='close'>&times;</a></div>"),console.log(t.status+": "+t.responseText),$("#results").html('<div class="alert alert-dismissable alert-danger"><button type="button" class="close" data-dismiss="alert">×</button>There was an error, check your internet and try again!</a>.</div>'),window.setTimeout(function(){$(".alert").fadeTo(500,0).slideUp(500,function(){$(this).remove()})},5e3)},cache:!1})}function getCookie(t){var e=null;if(document.cookie&&""!=document.cookie)for(var o=document.cookie.split(";"),n=0;n<o.length;n++){var i=jQuery.trim(o[n]);if(i.substring(0,t.length+1)==t+"="){e=decodeURIComponent(i.substring(t.length+1));break}}return e}function csrfSafeMethod(t){return/^(GET|HEAD|OPTIONS|TRACE)$/.test(t)}function sameOrigin(t){var e=document.location.host,o=document.location.protocol,n="//"+e,i=o+n;return t==i||t.slice(0,i.length+1)==i+"/"||t==n||t.slice(0,n.length+1)==n+"/"||!/^(\/\/|http:|https:).*/.test(t)}var point_offset=0,total=0,total_displayed=0,latest_pk=0,new_point=!1,all_subtopics;Element.prototype.remove=function(){this.parentElement.removeChild(this)},NodeList.prototype.remove=HTMLCollection.prototype.remove=function(){for(var t=this.length-1;t>=0;t--)this[t]&&this[t].parentElement&&this[t].parentElement.removeChild(this[t])},$("#point-form").on("submit",function(t){t.preventDefault(),console.log("Point form submitted!"),savePoint()}),jQuery(function($){$("#point-div").bind("scroll",function(){$(this).scrollTop()+$(this).innerHeight()>=$(this)[0].scrollHeight&&total>total_displayed&&requestPoints(point_offset,10)})}),requestPoints(point_offset,10);var csrftoken=getCookie("csrftoken");$.ajaxSetup({beforeSend:function(t,e){!csrfSafeMethod(e.type)&&sameOrigin(e.url)&&t.setRequestHeader("X-CSRFToken",csrftoken)}});