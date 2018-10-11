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

function replaceWithLoadingMessage(e) {
  $(e.target).val('Loading...');
}

var PUBLISHING_STEPS = [
  {
    "message": "Acquiring permission to publish...",
    "resource": "http://encyclopedia.che.engin.umich.edu/lock.php"
  },
  {
    "message": "Creating a backup of the Encyclopedia...",
    "resource": "http://encyclopedia.che.engin.umich.edu/backup.php"
  },
  {
    "message": "Exporting from Google Drive... This could take a few minutes.",
    "resource": "http://encyclopedia.che.engin.umich.edu/export.php"
  },
  {
    "message": "Building menu pages...",
    "resource": "http://encyclopedia.che.engin.umich.edu/topics.php"
  },
  {
    "message": "Building sidebar content...",
    "resource": "http://encyclopedia.che.engin.umich.edu/sidebar.php"
  },
  {
    "message": "Indexing content for search...",
    "resource": "http://encyclopedia.che.engin.umich.edu/indexer.php"
  },
  {
    "message": "Merging and going live...",
    "resource": "http://encyclopedia.che.engin.umich.edu/merge.php"
  },
  {
    "message": "Cleaning up...",
    "resource": "http://encyclopedia.che.engin.umich.edu/unlock.php"
  }
]; 

var FORCE_PUBLISH = false;
/*
  Publishing Steps:
  1. Export from Google Drive
  2. Create Sidebar content
  3. Create Reference Pages
  ~4. Load Glossary
  ~5. Build Search Index
  4. Copy into new directory  
*/
function executePublishingSequence(seqnum) {
  if(seqnum < PUBLISHING_STEPS.length) {
    $('#status-message').text(PUBLISHING_STEPS[seqnum].message);
    roundTripToServer(PUBLISHING_STEPS[seqnum].resource, executePublishingSequence, seqnum);
  } else {
    // yay we've completed all steps in the sequence!
    $('progress.progress').addClass("progress-success").val(seqnum);
    $('#status-message').text("Publishing Complete!");
    showOptionsToReturn();
  }
}

var steps = ["Exporting from Google Drive&hellip; This could take a few minutes."];

function showOptionsToReturn() {
  $(".navigation-options").show('slow');
}

function createCompletedStep(message) {
  var messageList = $("#completed-message")
  var nextMessage = $('<li><i class="fa fa-check-circle text-success" aria-hidden="true"></i> '+message+'</li>');
  messageList.append(nextMessage);
  nextMessage.show('slow');
}

function earlyUnlock() {
  $.ajax({
    url: 'http://encyclopedia.che.engin.umich.edu/unlock.php',
    method: 'POST',
    data: {
      access: GOOGLE_ACCESS_TOKEN
    }
  });
}

function roundTripToServer(resource, callback, seqnum) {
  //console.log("sending request #" + seqnum);
  $.ajax(resource,
    { 
      method: 'POST',
      data: {
        access: GOOGLE_ACCESS_TOKEN,
        force: FORCE_PUBLISH
      },
      success: function (data, status, request) {
        if(data.status != undefined) {
          console.log("received error");
          $('#status-message').text(data.status);
          // destroy all hopes of progress
          $('progress.progress').addClass('progress-danger').val(666); 
          showOptionsToReturn();
          earlyUnlock();
        } else {
          // add progress
          $('progress.progress').val(seqnum + 1);
          // tell us what we just did
          //console.log(data.completed);
          createCompletedStep(data.completed);
          callback(seqnum + 1);
        }
      },
      error: function (request, status, error) {
        console.log(request);
        console.log(status);
        console.log(error);
        $('#status-message').text("An error occurred on the server: "+status);
        $('progress.progress').addClass('progress-danger').val(666); 
        showOptionsToReturn();
        earlyUnlock();
      }
    });
}

function pageSetup() {
  //console.log("running page setup");
  $('form.publish-form input.btn').click(replaceWithLoadingMessage);
  // make sure the access token exists
  try { GOOGLE_ACCESS_TOKEN; } catch (e) { return; }
  //console.log(GOOGLE_ACCESS_TOKEN);

  $('progress').attr('max', PUBLISHING_STEPS.length);

  FORCE_PUBLISH = getParameterByName('state') == 'force';

  $(window).on('unload', function() {
    $.ajax({
      url: 'http://encyclopedia.che.engin.umich.edu/unlock.php',
      method: 'POST',
      data: {
        access: GOOGLE_ACCESS_TOKEN
      }
    });
  });

  executePublishingSequence(0);
}

// Run page setup when document has loaded.
$(document).ready(pageSetup);


