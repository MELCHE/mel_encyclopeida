<?php 
  header("Content-Type: application/json");
  sleep(1);
  echo '{"completed": "Compiled article metadata"}';
/*
  if(isset($_REQUEST['access'])) {
    $RESULT = shell_exec('python metadata.py export/Pages export');
  }

  if(isset($RESULT)) {
    echo '{"completed": "Compiled article metadata"}';
  } else {
    echo '{"status": "Export failed!"}';
  }
  */
?>