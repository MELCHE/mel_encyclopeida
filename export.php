<?php 
  
  /*
  header("Content-Type: application/json");
  sleep(1);
  echo '{"completed": "Exported ____ files from Google Drive"}';
  */

  // tell the client that the response is json
  header('Content-Type: application/json');


  if(isset($_REQUEST['access']) && isset($_REQUEST['force'])) {
    // check token
    $VALIDATE = shell_exec('python validate.py ' . escapeshellarg($_REQUEST['access'] . ' 2> err.txt'));
    if(!isset($VALIDATE)) {
      echo '{"status": "ACCESS DENIED - UNAUTHENTICATED"}';
    }

    // do the export job
    $FORCE = $_REQUEST['force'] == 'true' ? 'FORCE' : 'NEW';
    $EXPORT_RESULT = shell_exec('python export.py ' . escapeshellarg($_REQUEST['access']) . ' ' . $FORCE .' 2> err.txt');

    // If the export works, send back the response. Otherwise send back an error json
    if(isset($EXPORT_RESULT)) {
      echo '{"completed": "Exported ' . $EXPORT_RESULT . ' files from Google Drive"}';
    } else {
      echo '{"status": "Export failed!"}';
    }
  } else if (isset($_REQUEST['access']) && isset($_REQUEST['name'])) {
    // check token
    $VALIDATE = shell_exec('python validate.py ' . escapeshellarg($_REQUEST['access'] . ' 2> err.txt'));
    if(!isset($VALIDATE)) {
      echo '{"status": "ACCESS DENIED - UNAUTHENTICATED"}';
    }

    // do a restore job
    $RESTORE_RESULT = shell_exec('python restore.py ' . escapeshellarg($_REQUEST['access']) . ' ' . escapeshellarg($_REQUEST['name']) . ' 2> err.txt');

    
    if(isset($RESTORE_RESULT)) {
      echo '{"completed": "Restored backup file from Google Drive"}';
    } else {
      echo '{"status": "Restore failed!"}';
    }
  } else {
    echo '{"status": "Restore failed!"}';
  }
  

?>