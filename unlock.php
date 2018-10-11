<?php
  header("Content-Type: application/json");
  if(isset($_REQUEST['access'])) {
    // check the token
    $VALIDATE = shell_exec('python validate.py ' . escapeshellarg($_REQUEST['access'] . ' 2> err.txt'));
    if(!isset($VALIDATE)) {
      echo '{"status": "ACCESS DENIED - UNAUTHENTICATED"}';
    }

    // do the unlock
    $UNLOCKED = shell_exec('python unlock.py');
    if(isset($UNLOCKED)) {
      echo '{"completed": "Completed process"}';
    } else {
      echo '{"status": "Could not clean up properly"}';
    }
  }
?>