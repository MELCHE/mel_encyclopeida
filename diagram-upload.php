<?php
  if(isset($_REQUEST['image']) && $_REQUEST['image'] == 1) {
    $target_dir = "Diagrams/";

    $given_name = $target_dir . basename($_FILES["img-upload"]["name"]);
    $imageFileType = pathinfo($given_name,PATHINFO_EXTENSION);
    $target_file = $target_dir . strval(microtime(TRUE)*1000) . '.'. $imageFileType;
    // Check if image file is a actual image or fake image
    $check = getimagesize($_FILES["img-upload"]["tmp_name"]);
    if($check !== false && (strtolower($imageFileType) == "jpg" || $imageFileType == "png" || $imageFileType == "jpeg")) {  
      move_uploaded_file($_FILES["img-upload"]["tmp_name"], $target_file);

      header("Content-Type: application/json");
      echo '{"target_file":"' . $target_file . '", "width":' . $check[0] . ', "height":' . $check[1] . '}';
    } else {
      header("HTTP/1.1 400 BAD REQUEST");
    }
  } else {
    $jsontext = json_encode(json_decode(file_get_contents('php://input')));
    $filename = strval(microtime(TRUE)*1000) . '.json';
    $pathname = 'Diagrams/' . $filename;
    $handle = fopen($pathname, 'w') or die(print_r(error_get_last(),true));
    fwrite($handle, $jsontext);
    fclose($handle);
    header("Content-Type: application/json");
    echo '{"file-name":"' . $filename . '","file-path":"'. $pathname .'","file-contents":' . $jsontext . '}';
  }

  

?>