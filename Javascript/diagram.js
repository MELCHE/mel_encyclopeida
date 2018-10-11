function uploadFile() {
  $("#img-upload").hide(300);
  $("#img-upload-submit").val("Loading...");
  $("progress").show(300);

  // HTTP REQUEST STUFF
  var fd = new FormData();
  fd.append("img-upload", document.getElementById("img-upload").files[0]);
  fd.append("image", "1");
  var xhr = new XMLHttpRequest();
  xhr.upload.addEventListener("progress", uploadProgress, false);
  xhr.addEventListener("load", uploadComplete, false);
  xhr.addEventListener("error", uploadError, false);
  xhr.addEventListener("abort", uploadAbort, false);
  xhr.open("POST", "diagram-upload.php");
  xhr.send(fd);
}

function uploadProgress(e) {
  if(e.lengthComputable) {
    var percentComplete = Math.round(e.loaded * 100 / e.total);
    $("progress").val(percentComplete);
  }
}

var imgDim = {};

function uploadComplete(e) {
  if (e.target.status != 200) {
    $("progress").val(100);
    $("progress").addClass("progress-danger");
    $("#upload-form, progress, #upload-form").hide(300);
    return;
  } 

  $("progress").val(100);
  $("progress").addClass("progress-success");
  $("#upload-form, progress, #upload-form").hide(300);

  var data = JSON.parse(e.target.response);

  $("#img-bg")
    .css("background-image", 'url("' + data.target_file + '")')
    .height(data.height)
    .width(data.width);

    imgDim = data;
    
  $(".link-blanket-bay").show(300);

}

function uploadError(e) {
  console.log("error:", e);
}

function uploadAbort(e) {
  console.log("abort:", e);
}

var anchor_regions = {};
var stack = [];
var start = undefined;
var helper = $('<div class="anchor-bay-helper"></div>');

function findDimensions(start, end) {
  var offset = {'top': Math.min(start.y, end.y), 'left': Math.min(start.x, end.x)};
  var width = Math.max(start.x, end.x) - Math.min(start.x, end.x) ;
  var height = Math.max(start.y, end.y) - Math.min(start.y, end.y);
  return {'offset': offset, 'width': width, 'height': height};
}

function getCoordWrt(e, elt) {
  var mouse = {"x": e.pageX, "y": e.pageY};
  var box = $(elt).offset();
  return {"x": mouse.x - box.left, "y": mouse.y - box.top};
}

function setDimsOn(elt, dim) {
  return elt
    .css('top', dim.offset.top+'px')
    .css('left', dim.offset.left+'px')
    .css('width', dim.width+'px')
    .css('height', dim.height+'px');
}

function startDrawing(e) {
  start = getCoordWrt(e, '#img-bg');
  helper.css({"top": start.y+'px', "left": start.x+'px', 'height': 0, 'width': 0});
  $("#img-bg").append(helper);
}

function updateHelper(e) {
  if(start) {
    var cur = getCoordWrt(e, '#img-bg');
    var dim = findDimensions(start, cur);
    setDimsOn(helper, dim);
  }
}

function overlap(r1, r2) {
  var y0 = r1.offset.top;
  var y1 = r1.offset.top + r1.offset.height;
  var x0 = r1.offset.left;
  var x1 = r1.offset.left + r1.offset.width;
  var a = r2.offset.top;
  var b = r2.offset.left;
  return y0 < a && a < y1 && x0 < b && b < x1;
}

function endDrawing(e) {
  if (start == undefined) return;

  helper.remove();

  var end = getCoordWrt(e, '#img-bg');
  var dim = findDimensions(start, end);

  // reject 0 size regions
  if (dim.width == 0 || dim.height == 0) {
    start = undefined;
    return;
  }

  // reject a region that overlaps with prev regions
  for(var i = 0; i < stack.length; i++) {
    var id = stack[i];
    if (overlap(anchor_regions[id], dim)) {
      start = undefined;
      return;
    }
  }


  var id = 'a' + dim.offset.top +'-'+ dim.offset.left +'-'+ dim.width +'-'+ dim.height; 

  anchor_regions[id] = (dim);
  stack.push(id);

  var anchor_bay = '<div class="anchor-bay"></div>';
  var elt = setDimsOn($(anchor_bay), dim).attr('id', id);

  $('#img-bg').append(elt);
  start = undefined;
} 

$("#img-bg").mousedown(startDrawing);
$("#img-bg").mouseup(endDrawing);
$("#img-bg").mousemove(updateHelper);

function undoLink() {
  if(stack.length > 0) {
    var id = stack.pop();
    delete anchor_regions[id];
    //console.log('#'+id);
    document.getElementById(id).remove();
  }
}

function extractLinkRegions() {
  $('div.link-blanket-bay').hide(300);
  $('div.link-blanket-bay').remove();
  $('div.hyperlink-connector').show(300);
  var template = '<li><div class="link-row"><div class="img-snippet"></div><span class="link-input"><input type="text" class="form-control" placeholder="http://example.com/full/path/to/file.html"></span></div></li>';
  for(var i = 0; i < stack.length; i++) {
    var dim = anchor_regions[stack[i]];
    var inst = $(template);
    inst.find('.img-snippet')
      .css('background-image', 'url("' + imgDim.target_file + '")')
      .css('background-repeat', 'no-repeat')
      .css('background-attachment', 'scroll')
      .css('background-position', -dim.offset.left + 'px -' + dim.offset.top + 'px')
      .css('display', 'inline-block')
      .css('margin-right', '20px')
      .css('height', dim.height)
      .css('width', dim.width);
    inst.find('input')
      .css('margin-bottom', '50px');
    inst
      .css('list-style', 'none')
      .css('margin-bottom', '50px')
      .attr('id', stack[i]);

    $('div.hyperlink-connector ul').append(inst);
  }
  $('.hyperlink-connector input').each(function(i, elt) {
    console.log(elt);
    $(elt).on("input",function(e){
      if($(this).data("lastval")!= $(this).val()){
        $(this).data("lastval",$(this).val());
        
        $('.hyperlink-connector-error-message').hide(300);
      };
    });
  });
}

function validURL(value) {
  return /^(?:(?:(?:https?|ftp):)?\/\/)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})).?)(?::\d{2,5})?(?:[/?#]\S*)?$/i.test(value);
}

function validateURLs() {
  var inputs = $(".hyperlink-connector").find('input');
  console.log(inputs);
  for(var i = 0; i < inputs.length; i++) {
    var URL = $(inputs[i]).val();
    if(!validURL(URL) || URL == "") return false;
  }
  return true;
}

function sendInfoToServer(cb) {
  if (!validateURLs()) {
    $('.hyperlink-connector-error-message').show(300);
    return;
  }
  var items = $(".hyperlink-connector li");
  var data = {
    src: imgDim.target_file,
    height: imgDim.height,
    width: imgDim.width,
    regions: []
  }
  for(var i = 0; i < items.length; i++) {
    var id = $(items[i]).attr('id');
    anchor_regions[id].href = $(items[i]).find('input').val();
    data.regions.push(anchor_regions[id]);
  }
  $.ajax({
    url: 'diagram-upload.php',
    type: 'post',
    dataType: 'json',
    success: cb,
    error: function(e) {
      console.log(e);
    },
    data: JSON.stringify(data),
    contentType: "application/json; charset=utf-8"
  });
}

var server_data = null;

function displayAndDownload(data) {
  server_data = data;
  // hide the hyperlink connector
  $(".hyperlink-connector").hide(300);
  // display options to download vs embed
  $(".output-options-file-location").text(data["file-path"]);
  $(".output-options").show(300);

}

function downloadJSON() {
  download(
    JSON.stringify(server_data['file-contents']), 
    server_data['file-name'], 
    'application/json'
  );
}

function submitHyperlinks() {
  sendInfoToServer(displayAndDownload);
}
