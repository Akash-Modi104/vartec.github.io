<?php
// TEST STAND-IN ONLY. Mirrors the live script's interface without sending mail.
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    file_put_contents(getenv('VARTEC_DATA_DIR') . '/test-mail.log', json_encode($_POST) . "\n", FILE_APPEND);
    echo isset($_POST['firstName'], $_POST['lastName'], $_POST['email'], $_POST['phone'], $_POST['message']) ? 'Success' : 'Error';
} else { echo 'Invalid request'; }
