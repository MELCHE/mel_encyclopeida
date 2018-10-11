function applyHoverHandler(locationTree, img, diagram_data) {
  img.mousemove(function(e) {
    var that = $(this)
    var frame = that.offset();
    var location = {'left': e.pageX - frame.left, 'top': e.pageY - frame.top};
    var bounds = {
      top: {
        start: 0,
        end: that.height()
      },
      left: {
        start: 0,
        end: that.width()
      }
    };
    var onARegion = inRegion(location, bounds, locationTree, diagram_data, true);
    if(onARegion && !that.hasClass('pointer')) {
      that.addClass('pointer');
    } else if (!onARegion && that.hasClass('pointer')){
      that.removeClass('pointer');
    }
  });


}

function applyClickHandler(locationTree, img, diagram_data) {
  console.log(locationTree, img, diagram_data);
  img.click(function(e) {
    console.log("hi");
    var that = $(this);
    var frame = that.offset();
    var location = {'left': e.pageX - frame.left, 'top': e.pageY - frame.top};
    var bounds = {
      top: {
        start: 0,
        end: that.height()
      },
      left: {
        start: 0,
        end: that.width()
      }
    };
    var reg = inSegment(location, bounds, locationTree, true);
    if(reg == undefined) return;
    else {
      var region = diagram_data.regions[reg];
      var widthRatio = diagram_data['width_ratio'];
      var heightRatio = diagram_data['height_ratio'];
      var edges = {
        'left': region.offset.left * widthRatio,
        'right': (region.offset.left + region.width) * widthRatio,
        'top': region.offset.top * heightRatio,
        'bottom': (region.offset.top + region.height) * heightRatio
      }
      var within_width = edges.left < location.left && location.left < edges.right;
      var within_hieght = edges.top < location.top && location.top < (edges.bottom);
      if (within_width && within_hieght) {
        window.location = region.href;
      }
    }
  });
}

function inRegion(location, bounds, locationTree, diagram_data, vert) {
  // return true if region is defined and that location is within it, else false
  var reg = inSegment(location, bounds, locationTree, true);
  if(reg == undefined) return false;
  else {
    var region = diagram_data.regions[reg];
    var widthRatio = diagram_data['width_ratio'];
    var heightRatio = diagram_data['height_ratio'];
    var edges = {
      'left': region.offset.left * widthRatio,
      'right': (region.offset.left + region.width) * widthRatio,
      'top': region.offset.top * heightRatio,
      'bottom': (region.offset.top + region.height) * heightRatio
    }
    var within_width = edges.left < location.left && location.left < edges.right;
    var within_hieght = edges.top < location.top && location.top < (edges.bottom);
    return within_width && within_hieght;
  }
}

function inSegment(location, bounds, locationTree, vert) {
  if(locationTree == undefined) return locationTree;
  if(typeof(locationTree) == typeof(0)) return locationTree;
  else {
    var horzDivide = (bounds.top.start + bounds.top.end) / 2;
    var vertDivide = (bounds.left.start + bounds.left.end) / 2;
    var within = true;
    if(vert && vertDivide < location.left) within = false;
    if(!vert && horzDivide < location.top) within = false;

    var newbounds = resizeBounds(bounds, (vert?vertDivide:horzDivide), vert, within);

    return inSegment(
      location, 
      newbounds, 
      (within?locationTree.within:locationTree.outside),
      !vert);
  }
}

function resizeBounds(bounds, divide, vert, within) {
  var newbounds = $.extend(true, {}, bounds);
  if (vert && within) newbounds.left.end = divide;
  else if (vert && !within) newbounds.left.start = divide;
  else if (!vert && within) newbounds.top.end = divide;
  else newbounds.top.start = divide;

  return newbounds;
}

var depths = [];
var calls = 0;
function createLocationTree(diagram_data, regions, bounds, vert, calls) {
  //console.log(bounds, regions);
  if (calls > 10) return;
  if (regions.length == 0) {depths.push(calls);return undefined};
  if (regions.length == 1) {depths.push(calls);return regions[0];}
  else {
    var horzDivide = (bounds.top.start + bounds.top.end) / 2;
    var vertDivide = (bounds.left.start + bounds.left.end) / 2;

    var vertWithinBounds = resizeBounds(bounds, vertDivide, true, true);
    var horzWithinBounds = resizeBounds(bounds, horzDivide, false, true);
    var vertOutsideBounds = resizeBounds(bounds, vertDivide, true, false);
    var horzOutsideBounds = resizeBounds(bounds, horzDivide, false, false);

    var widthRatio = diagram_data['width_ratio'];
    var heightRatio = diagram_data['height_ratio'];

    var regionsWithin = [];
    var regionsOutside = [];

    for(var i = 0; i < regions.length; i++) {
      var region = diagram_data.regions[regions[i]];
      if (vert) {
        var rightEdge = (region.offset.left + region.width) * widthRatio;
        var leftEdge = (region.offset.left) * widthRatio;
        if (leftEdge < vertDivide) {
          regionsWithin.push(regions[i]);
        }
        if (vertDivide < rightEdge){
          regionsOutside.push(regions[i]);
        }
      } else {
        var topEdge = (region.offset.top) * heightRatio;
        var botEdge = (region.offset.top + region.height) * heightRatio;
        if (topEdge < horzDivide) {
          regionsWithin.push(regions[i]);
        } 
        if (horzDivide < botEdge) {
          regionsOutside.push(regions[i]);
        }
      }
    }

    //console.log("inside:", regionsWithin, "outside:", regionsOutside);

    return {
      'within': createLocationTree(diagram_data, regionsWithin, 
        (vert?vertWithinBounds:horzWithinBounds), !vert, calls+1),
      'outside': createLocationTree(diagram_data, regionsOutside, 
        (vert?vertOutsideBounds:horzOutsideBounds), !vert, calls+1) 
    };
  }
}


$(document).ready(function() {
  var diagrams = $('img.diagram');
  for(var i = 0; i < diagrams.length; i++) {
    var img = $(diagrams[i]);
    var id = img.attr('id');
    if (id == undefined || id == "") continue;
    var diagram_data = window[id];
    diagram_data['height_ratio'] = img.height() / diagram_data.height;
    diagram_data['width_ratio'] = img.width() / diagram_data.width;

    var regions = [];
    for(var x = 0; x < diagram_data.regions.length; x++) {
      //console.log(i, diagram_data.regions[i].href);
      regions.push(x);
    }

    var locationTree = createLocationTree(diagram_data, regions,
      {
        top: {
          start: 0,
          end: img.height()
        },
        left: {
          start: 0,
          end: img.width()
        }
      }, true, 0);

    applyHoverHandler(locationTree, img, diagram_data);
    applyClickHandler(locationTree, img, diagram_data);
  }  
});