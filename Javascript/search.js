function getParameterByName(name, url) {
    if (!url) {
      url = window.location.href;
    }
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

function addTheSpinner() {
  $('.results-space').append('<img src="http://encyclopedia.che.engin.umich.edu/Images/default.gif" class="mx-auto d-block spinner" style="display:none">');
}

function removeTheSpinner() {
  $('.spinner').remove();
}

function search(query, handler) {
  $.get(
    'search.php?q=' + encodeURIComponent(query),
    null,
    handler
  );
}

function displayResults(results) {
  removeTheSpinner();
  var html = '';
  if (results.length == 0) {
    html = '<p> Sorry, we couldn\'t find any results for "<b>'+getParameterByName('q')+'</b>". </p>';
  } else {
    for(var i = 0; i < results.length; i++) {
      html += '<h3 class="result-link"><a href="'+results[i]['linkhref']+'">'+results[i]['title']+"</a></h3>";
      html += '<p class="reference-link"><small>http://encyclopedia.che.engin.umich.edu/'+results[i]['linkhref']+"</small></p>";
      html += '<p class="highlight-text text-muted">'+results[i]['highlight']+"</p>";
    }
  }
  
  $('.results-space').append(html);
}

$(document).ready(function() {

  var query = getParameterByName('q');
  if(query) { // do a search
    addTheSpinner();
    $('#q').val(query);
    search(query, displayResults);
  }
});