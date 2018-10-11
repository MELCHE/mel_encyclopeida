<?php 
/*
  header("Content-Type: application/json");
  sleep(1);
  echo '{"completed": "Saved the glossary and updated articles with definitions."}';
  */

  if(isset($_REQUEST['access'])) {
    // check the token
    $VALIDATE = shell_exec('python validate.py ' . escapeshellarg($_REQUEST['access'] . ' 2> err.txt'));
    if(!isset($VALIDATE)) {
      echo '{"status": "ACCESS DENIED - UNAUTHENTICATED"}';
    }

    // do the merging
    $RESULT = shell_exec('python glossary.py '. escapeshellarg($_REQUEST['access']) .' 2> err.txt');
    header("Content-Type: application/json");
    if (isset($RESULT)) {
      echo '{"completed": "Saved the glossary and updated articles with definitions"}';
    } else {
      echo '{"status": "Export failed!"}';
    }
  }
?>