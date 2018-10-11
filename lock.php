<?php
  header("Content-Type: application/json");
  if(isset($_REQUEST['access'])) {
    // check the token
    $VALIDATE = shell_exec('python validate.py ' . escapeshellarg($_REQUEST['access'] . ' 2> err.txt'));
    if(!isset($VALIDATE)) {
      echo '{"status": "ACCESS DENIED - UNAUTHENTICATED"}';
    }

    // do the lock
    $handle = fopen("lockfile", "r");
    $status = fread($handle, 1);
    if ($status !== false && $status == "u") {
      fclose($handle);
      $writehandle = fopen("lockfile", "w");
      fwrite($writehandle, "l");
      fclose($writehandle);
      echo '{"completed": "Ok to proceed with publish"}';
    } else {
      fclose($handle);
      echo '{"status": "Another publish is currently underway; Permission denied: '. $status .'"}';
    }
  }
?>