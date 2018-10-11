<?php 
  
  header("Content-Type: application/json");
  if(isset($_REQUEST['access'])) {
    $VALIDATE = shell_exec('python validate.py ' . escapeshellarg($_REQUEST['access'] . ' 2> err.txt'));
    if(!isset($VALIDATE)) {
      echo '{"status": "ACCESS DENIED - UNAUTHENTICATED"}';
    }

    $UPLOADNAME = shell_exec('python backup.py '. escapeshellarg($_REQUEST['access']) . ' 2> err.txt');
    if(isset($UPLOADNAME)) {
      echo '{"completed": "Created a backup called '.$UPLOADNAME.' and saved it to Google Drive"}';
    } else {
      echo '{"status": "Export failed! here1"}';
    }
  } else {
    echo '{"status": "Export failed! here2"}';
  }
  

   // MOCK:
  /*
  header("Content-Type: application/json");
  sleep(1);
  echo '{"completed": "Created a backup called ___ and saved it to Google Drive"}';
  */
  
  
?>
