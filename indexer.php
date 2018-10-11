<?php 
  /*
  header("Content-Type: application/json");
  sleep(1);
  echo '{"completed": "Indexed articles for search"}';
  */

  if(isset($_REQUEST['access'])) {
    // check the token
    $VALIDATE = shell_exec('python validate.py ' . escapeshellarg($_REQUEST['access'] . ' 2> err.txt'));
    if(!isset($VALIDATE)) {
      echo '{"status": "ACCESS DENIED - UNAUTHENTICATED"}';
    }

    // do the indexing job
    $RESULT = shell_exec('python indexer.py 2> err.txt');
    header("Content-Type: application/json");
    if (isset($RESULT)) {
      echo '{"completed": "Indexed articles for search"}';
    } else {
      echo '{"status": "Export failed!"}';
    }
  }
?>