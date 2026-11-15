<?php
declare(strict_types=1);

/**
 * VARTEC website: single entry point for the public pages and the admin.
 * .htaccess sends every address that is not a real file here.
 */
$path = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH) ?: '/';
$path = '/' . ltrim(rawurldecode($path), '/');

// `php -S` (local testing) has no .htaccess: hand real files back to the built-in server,
// except the private folders and this file.
if (PHP_SAPI === 'cli-server') {
    $private = (bool) preg_match('#^/(app|data)(/|$)|/\.(?!well-known/)#', $path); // code, data and dot-files
    if (!$private && $path !== '/index.php' && is_file(__DIR__ . $path)) {
        return false;
    }
    // Test-only stand-ins (e.g. a fake send_mail.php) live outside the site and are never deployed.
    $extra = getenv('VARTEC_TEST_EXTRA');
    if ($extra && is_file($extra . $path)) {
        require $extra . $path;
        return;
    }
}

require __DIR__ . '/app/bootstrap.php';

if ($path === '/admin' || str_starts_with($path, '/admin/')) {
    require APP_DIR . '/admin.php';
    admin_dispatch(substr($path, 6) ?: '/');
} else {
    require APP_DIR . '/public.php';
    public_dispatch($path);
}
