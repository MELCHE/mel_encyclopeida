<?php 
  /*
  header("Content-Type: application/json");
  sleep(1);
  echo '{"completed": "Merged latest updates and pushed to live"}';
  */

  if(isset($_REQUEST['access'])) {
    // check the token
    $VALIDATE = shell_exec('python validate.py ' . escapeshellarg($_REQUEST['access'] . ' 2> err.txt'));
    if(!isset($VALIDATE)) {
      echo '{"status": "ACCESS DENIED - UNAUTHENTICATED"}';
    }

    // do the merging
    $RESULT = shell_exec('python merge.py 2> err.txt');
    header("Content-Type: application/json");
    if (isset($RESULT)) {
      echo '{"completed": "Merged latest updates and pushed to live"}';
    } else {
      echo '{"status": "Export failed!"}';
    }
  }

?>