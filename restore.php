<?php

  if(isset($_REQUEST['code'])) {
    $ACCESS_TOKEN = shell_exec('python oauth2.py '. $_REQUEST['code'] . ' restore 2> err.txt');
  }
  if(isset($_REQUEST['state'])) {
    $STATE = $_REQUEST['state'];
  }

?>
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta http-equiv="x-ua-compatible" content="ie=edge">

    <!-- Fav icon -->
    <link rel='shortcut icon' href='http://encyclopedia.che.engin.umich.edu/Images/melicon.png' type='image/x-icon'/ >

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha.5/css/bootstrap.min.css" integrity="sha384-AysaV+vQoT3kOAXZkl02PThvDr8HYKPZhNT5h/CXfBThSRXQ6jW5DO2ekP5ViFdi" crossorigin="anonymous">
    <!-- Font Awesome -->
    <link href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet" integrity="sha384-wvfXpqpZZVQGK6TAh5PVlGOfQNHSoD2xbE+QkPxCAFlNEevoEH3Sl0sibVcOQVnN" crossorigin="anonymous">
    <!-- Custom fonts and CSS -->
    <link href="https://fonts.googleapis.com/css?family=Open+Sans" rel="stylesheet">
    <link rel="stylesheet" type="text/css" href="http://encyclopedia.che.engin.umich.edu/Stylesheets/main.css">
    <title>Visual Encyclopedia of Chemical Engineering</title>
  </head>
  <body>
    <div class="container-fluid">
      <!--Navigation Bar-->
      <div class="row nav-area">
        <div class="col-sm-12">
          <nav class="navbar navbar-fixed-top">
            <!--Navigation Brand Goes Here-->
            <div class="row">
              <div class="col-xs-4">
                <img src="http://encyclopedia.che.engin.umich.edu/Images/engineering_logo.svg" class="img-fluid">
              </div>
              <div class="col-xs-8">
                <a class="navbar-brand" href="http://encyclopedia.che.engin.umich.edu">
                  <h3>Encyclopedia of Chemical Engineering Equipment</h3>
                </a>
              </div>
            </div>
            <!--Navigation Links Go here-->
            <div class="row">
              <div class="col-xs-9">
                <ul class="nav navbar-nav">
                  <li class="nav-item">
                    <a class="nav-link" href="http://encyclopedia.che.engin.umich.edu">Home</a>
                  </li>
                  <li class="nav-item">
                    <a class="nav-link" href="http://encyclopedia.che.engin.umich.edu/Pages/menu.html">Menu</a>
                  </li>
                  <li class="nav-item">
                    <a class="nav-link" href="http://encyclopedia.che.engin.umich.edu/contributors.html">Contributors</a>
                  </li>
                  <li class="nav-item">
                    <a class="nav-link" href="http://encyclopedia.che.engin.umich.edu/license.html">License</a>
                  </li>
                </ul>
              </div>
              <!-- Search box -->
              <div class="col-xs-3">
                <form class="float-xs-right search" action="http://encyclopedia.che.engin.umich.edu/search.html">
                  <div class="input-group">
                        <input type="text" class="form-control" placeholder="Search" name="q">
                        <span class="input-group-btn">
                          <button class="btn btn-primary" type="submit">Go!</button>
                        </span>
                      </div>
                </form>
              </div>
            </div>
          </nav>
        </div>
      </div>
      
      <!-- Main Content -->
      <div class="row main-content">
        <div class="col-xs-10 offset-xs-1 main-content-body">
          <!-- Controls -->
          <br>
          <h1> Restore tool </h1>

          <p> MEL restore tool. This page gives access to MEL module contributers to restore the site to a previous backed up version. In doing so, the MEL website will be restored to an earlier version of the encyclopedia.</p>

          <?php if (!isset($_REQUEST['code'])) { ?>
          <!-- Default welcome message and instructions -->
          <p> To restore, complete the following: </p>
          <ol>
            <li>Make sure you have a good internet connection</li>
            <li>Click "Restore" to get a list of backups to restore from</li>
            <li>Follow on-screen directions to authenticate yourself to Google if prompted</li>
            <li>Select the desired backup version to restore the encyclopedia to</li>
            <li>Confirm the website is restored to the desired version</li>
          </ol>
          <form class="publish-form" action="https://accounts.google.com/o/oauth2/auth">
            <input type="hidden" name="response_type" value="code">
            <input type="hidden" name="client_id" value="209742625618-6t7ef6kfhu2e01hmi21n45b16hmqkj1m.apps.googleusercontent.com">
            <input type="hidden" name="redirect_uri" value="http://encyclopedia.che.engin.umich.edu/restore.php">
            <input type="hidden" name="scope" value="https://www.googleapis.com/auth/drive email">
            <input type="hidden" name="access_type" value="online">
            <div class="input-group col-xs-6">
              <input type="submit" class="btn btn-primary" value="Restore">
            </div>
          </form>
          <?php } else if (!isset($ACCESS_TOKEN) || $ACCESS_TOKEN == "NO_AUTH") { ?>
          <!-- Alert for denied auth -->
          <div class="alert alert-danger fade in" role="alert">
            <p><strong>Authentication Failed!</strong> The server was unable to establish your identity as a MEL contributer. Perhaps you are looking for our <a href="http://encyclopedia.che.engin.umich.edu">home page</a>.</p>
            <p> If you are indeed a MEL contributer and received this message in error, ensure you have been given proper permissions to Google Drive and are signed in with your umich Google account.</p>
          </div>
          <?php } else if (isset($STATE)) {
            // A file was selected. Start the restore process for that filename
          ?>
            <p id="status-message"> </p>
            <progress class="progress progress-striped progress-animated" value="0" max="7"></progress>
            <ul id="completed-message"></ul>
            <div class="navigation-options">
              <a class="btn btn-primary" href="http://encyclopedia.che.engin.umich.edu">Return to MEL Homepage</a>
              <a class="btn btn-secondary" href="restore.php">Return to Restore Screen</a>
              <br><br>
            </div>
            <script type="text/javascript">
              var GOOGLE_ACCESS_TOKEN = "<?php echo $ACCESS_TOKEN?>";
              var RESTORE_FILE_NAME = "<?php echo $STATE?>";
            </script>

          <?php } else {
            // Authentication was valid but no file was selected - aka no state.
            // Just list the possible files here
          ?>
            <p>Select the archive file that you would like to restore MEL to.</p>
            <p><span class="text-danger">Note: After restoring one of these versions, the website will not match the documents on Google Drive. This could undo changes that another contributer intended to make. Only restore from one of these backups if you are aware of all the changes you are undoing.</span></p>
            <script type="text/javascript">
              var GOOGLE_ACCESS_TOKEN = "<?php echo $ACCESS_TOKEN?>";
            </script>
          <?php
              $BACKUPS = shell_exec('python listbackups.py '. escapeshellarg($ACCESS_TOKEN) .' 2> err.txt');
              if(isset($BACKUPS)) {
                $backups = json_decode($BACKUPS, TRUE);
          ?>  
            <table class="table table-hover backuplist" style="height:100%">
              <tbody>
          <?php
                foreach ($backups['files'] as $file) {
                  $encodedTarget = 
                    "https://accounts.google.com/o/oauth2/auth" 
                    . "?response_type=" . "code"
                    . "&client_id=" . "209742625618-6t7ef6kfhu2e01hmi21n45b16hmqkj1m.apps.googleusercontent.com" 
                    . "&redirect_uri=" . urlencode("http://encyclopedia.che.engin.umich.edu/restore.php")
                    . "&scope=" . urlencode("https://www.googleapis.com/auth/drive email")
                    . "&access_type=" . "online"
                    . "&state=" . $file['id'];
              ?>
                  <tr>
                    <td>
                      <p>
                        <a href="<?php echo $encodedTarget?>" class="btn btn-primary">Restore this version</a>&nbsp;
                        <?php echo $file['name']?>&nbsp;&nbsp;
                        <?php 
                          $date = new DateTime($file['createdTime']);
                          echo '<span class="text-muted">' . $date->format('F jS, Y') . '</span>';
                        ?>
                      </p>
                    </td>
                  </tr>
              <?php
                }
          ?>
              </tbody>
            </table>
          <?php

              } else {
                // Print no backups available message
          ?>
            <p> No Backups available </p>
          <?php
              }
           } 
          ?>          
        </div>
      </div>
    </div>

    <!-- jQuery first, then Tether, then Bootstrap JS. -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js" integrity="sha384-3ceskX3iaEnIogmQchP8opvBy3Mi7Ce34nWjpBIwVTHfGYWQS9jwHDVRnpKKHJg7" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tether/1.3.7/js/tether.min.js" integrity="sha384-XTs3FgkjiBgo8qjEjBk0tGmf3wPrWtA6coPfQDfFEY8AnYJwjalXCiosYRBIBZX8" crossorigin="anonymous"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha.5/js/bootstrap.min.js" integrity="sha384-BLiI7JTZm+JWlgKa0M0kGRpJbF2J8q+qreVrKBC47e3K6BW78kGLrCkeRX6I9RoK" crossorigin="anonymous"></script>
    <script src="http://encyclopedia.che.engin.umich.edu/Javascript/restore.js"></script>
  </body>
</html>
