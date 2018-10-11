<?php 
  /*
  header("Content-Type: application/json");
  sleep(1);
  echo '{"completed": "Built and hooked up sidebars"}';
  */
  header("Content-Type: application/json");
  if(isset($_REQUEST['access'])) {
    // check the token
    $VALIDATE = shell_exec('python validate.py ' . escapeshellarg($_REQUEST['access'] . ' 2> err.txt'));
    if(!isset($VALIDATE)) {
      echo '{"status": "ACCESS DENIED - UNAUTHENTICATED"}';
    }

    // do the sidebar job
    $RESULT = shell_exec('python sidebar.py 2> err.txt');
    if (isset($RESULT)) {
      echo '{"completed": "Built and hooked up sidebars"}';
    } else {
      echo '{"status": "Export failed!"}';
    }
  }

  
  

?>