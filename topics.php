<?php 
  /*
  header("Content-Type: application/json");
  sleep(1);
  echo '{"completed": "Built all reference pages"}';
  */
  header("Content-Type: application/json");
  if(isset($_REQUEST['access'])) {
    // check the token
    $VALIDATE = shell_exec('python validate.py ' . escapeshellarg($_REQUEST['access'] . ' 2> err.txt'));
    if(!isset($VALIDATE)) {
      echo '{"status": "ACCESS DENIED - UNAUTHENTICATED"}';
    }

    // do the menu job
    $RESULT = shell_exec('python topics.py export/Pages export 2> err.txt');

    if (isset($RESULT)) {
      echo '{"completed": "Built all menu pages"}';
    } else {
      echo '{"status": "Export failed!"}';
    }
  }
  
?>