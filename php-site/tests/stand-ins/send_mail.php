<?php
// TEST STAND-IN ONLY. Mirrors the live script's interface without sending mail.
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $dir = getenv('VARTEC_DATA_DIR') ?: dirname(__DIR__) . '/vartec-data';   // same folder the site itself uses
    file_put_contents($dir . '/test-mail.log', json_encode($_POST) . "\n", FILE_APPEND);
    echo isset($_POST['firstName'], $_POST['lastName'], $_POST['email'], $_POST['phone'], $_POST['message']) ? 'Success' : 'Error';
} else { echo 'Invalid request'; }
