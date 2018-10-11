<?php
  $rawQueryString = $_REQUEST['q'];
  $queryList = preg_split('/\s+/', $rawQueryString);
  header("Content-Type: application/json");
  $queryShellArg = json_encode($queryList);
  $command = 'python search.py ' . escapeshellarg($queryShellArg) . ' 2> err.txt';
 $results = shell_exec($command);

  //echo $command;
  if(!isset($results)) {
    echo '[]';
  } else {
    echo $results;
  }

?>