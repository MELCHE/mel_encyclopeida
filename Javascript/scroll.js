// set up highlighting scroll here
var navs = []
var shift = $('#article-content').offset().top + 15;
var fullScrollLength = $('body').height();
var lastPos = shift;

// Set up smooth scrolling
$(".table-of-contents-links a").on('click', function(e) {
  e.preventDefault();
  var hash = this.hash;
  $('html, body').animate({
      scrollTop: $(hash).offset().top
    }, 300, function(){});
});

// Returns the largest number in array that is
// less than bound. If bound is the less than or
// equal to the smallest element e in array, then
// e is returned.
//
// comp must be a comparator that can that items 
// i, j from array and returns if i compares less than j
function getNextNavLink(array, bound) {
  var minDelta = Number.MAX_SAFE_INTEGER;
  var minDeltaIndex = 0;
  for(var i = 0; i < array.length; i++) {
    var delta = Math.abs(array[i].offset - bound);
    if(delta < minDelta) {
     // console.log("hi");
      minDelta = delta;
      minDeltaIndex = i;
    }
  }
  return array[minDeltaIndex];
}
window.onload = function() {

  $('.main-content-body').css('margin-bottom', $(window).height() + 'px');

  $('.table-of-contents-links a').each(function(index, anchor) {
    var hash = $(anchor).attr('href');
    heading = {
      offset: $(hash).offset().top + shift,
      anchor: $(anchor)
    }
    navs.push(heading);
  });

  $(document).scroll(function() {
    var fromTop = $(document).scrollTop()+shift;
    navlink = getNextNavLink(navs, fromTop);
    if(!navlink.anchor.hasClass('active')) {
      $('.table-of-contents-links .active').removeClass('active');
      navlink.anchor.addClass('active');
    }
  });

  getNextNavLink(navs, $(document).scrollTop()).anchor.addClass('active');
}
