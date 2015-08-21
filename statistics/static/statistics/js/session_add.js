var counter_subtopics = 2;
var limit_subtopics = 30;
Element.prototype.remove = function() {
    this.parentElement.removeChild(this);
}
NodeList.prototype.remove = HTMLCollection.prototype.remove = function() {
    for(var i = this.length - 1; i >= 0; i--) {
        if(this[i] && this[i].parentElement) {
            this[i].parentElement.removeChild(this[i]);
        }
    }
}
function deleteInput(divName){
  document.getElementById(divName).remove();
}
$('#committee-form').on('submit', function(event){
    event.preventDefault();
    console.log("form submitted!")  // sanity check
    submit_committee();
});
function submit_committee() {
    console.log("create post is working!") // sanity check
    console.log($('#id_pk').val())
    console.log($('#id_name').val())
    console.log($('#id_topic').val())
    console.log($('#subtopic-1').val())
};
