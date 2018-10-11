var RESTORING_STEPS = [
  {
    "message": "Creating a backup of the Encyclopedia...",
    "resource": "http://encyclopedia.che.engin.umich.edu/backup.php"
  },
  {
    "message": "Restoring from Google Drive...",
    "resource": "http://encyclopedia.che.engin.umich.edu/export.php"
  },
  {
    "message": "Indexing content for search...",
    "resource": "http://encyclopedia.che.engin.umich.edu/indexer.php"
  },
  {
    "message": "Merging and going live...",
    "resource": "http://encyclopedia.che.engin.umich.edu/merge.php"
  }
];

function roundTripToServer(resource, callback, seqnum) {
  console.log("sending request #" + seqnum);
  $.ajax(resource,
    { 
      method: 'POST',
      data: {
        access: GOOGLE_ACCESS_TOKEN,
        name: RESTORE_FILE_NAME
      },
      success: function (data, status, request) {
        if(data.status != undefined) {
          console.log("received error");
          $('#status-message').text(data.status);
          // destroy all hopes of progress
          $('progress.progress').addClass('progress-danger').val(666); 
          showOptionsToReturn();
        } else {
          // add progress
          $('progress.progress').val(seqnum + 1);
          // tell us what we just did
          console.log(data.completed);
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
      }
    });
}

function showOptionsToReturn() {
  $(".navigation-options").show('slow');
}

function createCompletedStep(message) {
  var messageList = $("#completed-message")
  var nextMessage = $('<li><i class="fa fa-check-circle text-success" aria-hidden="true"></i> '+message+'</li>');
  messageList.append(nextMessage);
  nextMessage.show('slow');
}

function replaceWithLoadingMessage(e) {
  $(e.target).val('Loading...');
}

function executeRestoringSequence(seqnum) {
  if(seqnum < RESTORING_STEPS.length) {
    $('#status-message').text(RESTORING_STEPS[seqnum].message);
    roundTripToServer(RESTORING_STEPS[seqnum].resource, executeRestoringSequence, seqnum);
  } else {
    // yay we've completed all steps in the sequence!
    $('progress.progress').addClass("progress-success").val(seqnum);
    $('#status-message').text("Publishing Complete!");
    showOptionsToReturn();
  }
}

function pageSetup() {
  console.log("running page setup");
  $('form.publish-form input.btn').click(replaceWithLoadingMessage);
  // make sure the access token exists
  try { GOOGLE_ACCESS_TOKEN; } catch (e) { return; } // return early if there's no token
  console.log(GOOGLE_ACCESS_TOKEN);
  try { RESTORE_FILE_NAME; } catch (e) { return; } // return early if there's no file name
  console.log(RESTORE_FILE_NAME);

  $('progress').attr('max', RESTORING_STEPS.length);

  executeRestoringSequence(0);
}

// Run page setup when document has loaded.
$(document).ready(pageSetup);