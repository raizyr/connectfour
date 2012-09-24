$(document).ready(function(){
  $("#board").delegate('td','mouseover mouseleave', function(e) {
    if (e.type == 'mouseover') {
      $("#board tr td:nth-child("+($(this).index()+1)+"):not(.played)").addClass("hover");
      $("#board tr td:nth-child("+($(this).index()+1)+"):not(.played):last").addClass("hover-target");
    } else {
      $("#board tr td:nth-child("+($(this).index()+1)+"):not(.played)").removeClass("hover");
      $("#board tr td:nth-child("+($(this).index()+1)+"):not(.played):last").removeClass("hover-target");
    }
  });
});
