<?php

  if(isset($_REQUEST['code'])) {
    $ACCESS_TOKEN = shell_exec('python oauth2.py '. escapeshellarg($_REQUEST['code']) . ' publish' );
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
                  <h3>Visual Encyclopedia of Chemical Engineering</h3>
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
          <h1> Publishing tool </h1>

          <p> MEL publishing tool. This page gives access to MEL module contributers to start a publish process. In doing so, the MEL website will be automatically updated with new changes made since the last publish.</p>

          <?php if (!isset($_REQUEST['code'])) { ?>
          <!-- Default welcome message and instructions -->
          <p> To publish, complete the following: </p>
          <ol>
            <li>Make sure you have a good internet connection</li>
            <li>Click "Publish" to publish new changes</li>
            <li>Follow on-screen directions to authenticate yourself to Google if prompted</li>
            <li>Confirm the new version of the website reflects your most recent changes</li>
          </ol>
          <form class="publish-form" action="https://accounts.google.com/o/oauth2/auth">
            <input type="hidden" name="response_type" value="code">
            <input type="hidden" name="client_id" value="209742625618-6t7ef6kfhu2e01hmi21n45b16hmqkj1m.apps.googleusercontent.com">
            <input type="hidden" name="redirect_uri" value="http://encyclopedia.che.engin.umich.edu/publish.php">
            <input type="hidden" name="scope" value="https://www.googleapis.com/auth/drive email">
            <input type="hidden" name="access_type" value="online">
            <div class="input-group col-xs-6">
              <div class="form-check">
                <label class="form-check-label">
                    <input class="form-check-input" type="checkbox" name="state" value="force"> &nbsp;
                    Force Publish. (Note: this will cause the publisher to do a forced sync, which could take up to 10 minutes.)
                </label>
              </div>
              <input class="btn btn-primary" type="submit" value="Publish!">
            </div>
          </form>
          <?php } else if (!isset($ACCESS_TOKEN) || $ACCESS_TOKEN == "NO_AUTH") { ?>
          <!-- Alert for denied auth -->
          <div class="alert alert-danger fade in" role="alert">
            <p><strong>Authentication Failed!</strong> The server was unable to establish your identity as a MEL contributer. Perhaps you are looking for our <a href="http://encyclopedia.che.engin.umich.edu">home page</a>.</p>
            <p> If you are indeed a MEL contributer and received this message in error, ensure you have been given proper permissions to Google Drive and are signed in with your umich Google account.</p>
          </div>
          <?php } else {?>
            <!-- Successful authentication! -->
            <p id="status-message"> </p>
            <progress class="progress progress-striped progress-animated" value="0" max="7"></progress>
            <ul id="completed-message"></ul>
            <div class="navigation-options">
              <a class="btn btn-primary" href="http://encyclopedia.che.engin.umich.edu">Return to MEL Homepage</a>
              <a class="btn btn-secondary" href="publish.php">Return to Publish Screen</a>
              <br><br>
            </div>
            <script type="text/javascript">
              var GOOGLE_ACCESS_TOKEN = "<?php echo $ACCESS_TOKEN?>";
            </script>
          <?php } ?>          
        </div>
      </div>
    </div>

    <!-- jQuery first, then Tether, then Bootstrap JS. -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js" integrity="sha384-3ceskX3iaEnIogmQchP8opvBy3Mi7Ce34nWjpBIwVTHfGYWQS9jwHDVRnpKKHJg7" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tether/1.3.7/js/tether.min.js" integrity="sha384-XTs3FgkjiBgo8qjEjBk0tGmf3wPrWtA6coPfQDfFEY8AnYJwjalXCiosYRBIBZX8" crossorigin="anonymous"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha.5/js/bootstrap.min.js" integrity="sha384-BLiI7JTZm+JWlgKa0M0kGRpJbF2J8q+qreVrKBC47e3K6BW78kGLrCkeRX6I9RoK" crossorigin="anonymous"></script>
    <script src="http://encyclopedia.che.engin.umich.edu/Javascript/publish.js"></script>
  </body>
</html>
