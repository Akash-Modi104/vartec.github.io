<?php
declare(strict_types=1);

/** Admin: sign-in, editing the draft, images, enquiries, settings, publish. */

require __DIR__ . '/admin_ui.php';

function admin_dispatch(string $path): void
{
    header('Cache-Control: no-store');
    header('X-Frame-Options: DENY');
    header('X-Content-Type-Options: nosniff');
    header('Referrer-Policy: same-origin');
    header("Content-Security-Policy: default-src 'self'; img-src 'self' data:; media-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; frame-ancestors 'none'; form-action 'self'; base-uri 'self'");

    $path = '/' . trim($path, '/');
    $post = ($_SERVER['REQUEST_METHOD'] ?? 'GET') === 'POST';

    // On the real website the admin is only ever used over an encrypted connection.
    $site = (string) (live_content()['settings']['site_url'] ?? '');
    if (!is_https() && str_starts_with($site, 'https://') && request_host() === parse_url($site, PHP_URL_HOST)) {
        redirect($site . ($_SERVER['REQUEST_URI'] ?? '/admin/'), 301);
    }

    if (!users()) {
        admin_setup($post);
        return;
    }
    if ($path === '/login') {
        admin_login($post);
        return;
    }
    if ($path === '/recover') {
        admin_recover($post);
        return;
    }
    $user = current_user();
    if (!$user) {
        redirect('/admin/login');
    }
    if ($post) {
        csrf_check();
    }
    // Someone given a password by another editor must choose their own before doing anything else.
    if (!empty(users()[$user]['must_change']) && !in_array($path, ['/settings/password', '/logout'], true)) {
        echo render('admin/auth', ['mode' => 'change', 'error' => flash()['message'] ?? '', 'user' => $user]);
        return;
    }
    $routes = [
        '/' => 'admin_dashboard', '/publish' => 'admin_publish', '/discard' => 'admin_discard', '/logout' => 'admin_logout',
        '/home' => 'admin_home', '/pages' => 'admin_pages', '/pages/order' => 'admin_pages_order', '/page' => 'admin_page',
        '/page/delete' => 'admin_page_delete', '/media' => 'admin_media', '/media/upload' => 'admin_media_upload',
        '/media/edit' => 'admin_media_edit', '/media/delete' => 'admin_media_delete', '/enquiries' => 'admin_enquiries',
        '/settings' => 'admin_settings', '/settings/password' => 'admin_password', '/settings/editors' => 'admin_editors',
        '/settings/two-step' => 'admin_two_step', '/settings/recovery' => 'admin_recovery_code',
        '/history' => 'admin_history', '/help' => 'admin_help', '/wording' => 'admin_wording', '/guide' => 'admin_guide',
    ];
    if (!isset($routes[$path])) {
        http_response_code(404);
        admin_page_out('Not found', '<div class="card"><h2>Page not found</h2><p><a href="/admin/">Back to the dashboard</a></p></div>', $user);
        return;
    }
    $routes[$path]($post, $user);
}

/** Wraps a screen in the admin frame (sidebar, publish bar). */
function admin_page_out(string $title, string $body, string $user, string $active = ''): void
{
    $content = draft_content();
    $new = count(array_filter(read_data('enquiries'), fn ($e) => ($e['status'] ?? '') === 'new'));
    echo render('admin/layout', ['title' => $title, 'body' => $body, 'user' => $user, 'active' => $active, 'changes' => has_unpublished_changes(),
        'new_enquiries' => $new, 'content' => $content, 'flash' => flash()]);
}

function clean_text(mixed $value, int $max = 5000): string
{
    $text = is_string($value) ? $value : '';
    $text = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/u', '', $text) ?? '';
    return mb_substr(trim(str_replace(["\r\n", "\r"], "\n", $text)), 0, $max);
}

function clean_line(mixed $value, int $max = 300): string
{
    return trim(preg_replace('/\s+/', ' ', clean_text($value, $max)) ?? '');
}

/** 'service', 'project' or 'info' from a request value; anything else counts as a service. */
function page_kind(mixed $value): string
{
    return is_string($value) && isset(PAGE_KINDS[$value]) ? $value : 'service';
}

function valid_media(array $content, mixed $id, ?string $kind = 'image'): string
{
    $id = is_string($id) ? $id : '';
    $item = $content['media'][$id] ?? null;
    return ($item && ($kind === null || ($item['kind'] ?? 'image') === $kind)) ? $id : '';
}

// ---------------------------------------------------------------- sign-in

function admin_setup(bool $post): void
{
    $code = setup_code(); // written to the private data folder
    $error = '';
    if ($post) {
        csrf_check();
        $name = strtolower(clean_line($_POST['username'] ?? '', 40));
        $password = (string) ($_POST['password'] ?? '');
        if (!rate_limit_ok('setup', 10, 900)) {
            $error = 'Too many attempts. Wait 15 minutes and try again.';
        } elseif (!hash_equals($code, strtoupper(trim((string) ($_POST['code'] ?? ''))))) {
            $error = 'That setup code is not right.';
        } elseif (!preg_match('/^[a-z0-9._-]{3,40}$/', $name)) {
            $error = 'Choose a username of 3 to 40 letters or numbers.';
        } elseif ($problem = password_problem($password, $name)) {
            $error = $problem;
        } else {
            write_data('users', [$name => ['hash' => password_hash($password, PASSWORD_DEFAULT), 'created' => gmdate('c'), 'epoch' => 0]]);
            @unlink(data_dir() . '/setup-code.php');
            sign_in($name);
            audit('First account created', $name);
            flash('Your account is ready. Welcome to the VARTEC admin.');
            redirect('/admin/');
        }
    }
    echo render('admin/auth', ['mode' => 'setup', 'error' => $error]);
}

function admin_login(bool $post): void
{
    if (current_user()) {
        redirect('/admin/');
    }
    $error = '';
    $mode = 'login';
    start_session();
    $pending = $_SESSION['pending_user'] ?? null;
    if ($post) {
        csrf_check();
        if (isset($_POST['code']) && $pending && isset(users()[$pending]['totp'])) {
            // Second step: the six-digit code from the authenticator app.
            $mode = 'code';
            $all = users();
            if (!rate_limit_ok('login-code', 6, 900, true, $pending)) {
                unset($_SESSION['pending_user']);
                $mode = 'login';
                $error = 'Too many wrong codes. Wait 15 minutes and sign in again.';
            } elseif (($used = totp_verify($all[$pending]['totp'], (string) $_POST['code'], (int) ($all[$pending]['totp_last'] ?? 0))) !== null) {
                $all[$pending]['totp_last'] = $used;
                write_data('users', $all);
                rate_limit_clear('login-code', $pending);
                sign_in($pending);
                audit('Signed in (password and code)', $pending);
                redirect('/admin/');
            } else {
                $error = 'That code is not right. Enter the current code from your app.';
            }
        } else {
            $name = strtolower(clean_line($_POST['username'] ?? '', 40));
            $record = users()[$name] ?? null;
            // Two limits: per visitor, and per account (so many computers cannot share the guessing).
            $allowed = rate_limit_ok('login', 8, 900) && rate_limit_ok('login-user', 20, 900, true, $name);
            // Always run a hash check so the response time does not reveal whether the username exists.
            $ok = password_verify((string) ($_POST['password'] ?? ''), $record['hash'] ?? '$2y$10$usesomesillystringfore7hnbRJHxXVLeakoG8K30oukPsA.ztMG') && $record;
            if (!$allowed) {
                $error = 'Too many attempts. Wait 15 minutes and try again.';
            } elseif ($ok) {
                rate_limit_clear('login');
                rate_limit_clear('login-user', $name);
                if (!empty($record['totp'])) {
                    $_SESSION['pending_user'] = $name;
                    $mode = 'code';
                } else {
                    sign_in($name);
                    audit('Signed in', $name);
                    redirect('/admin/');
                }
            } else {
                audit('Failed sign-in for "' . $name . '"');
                $error = 'The username or password is not right.';
            }
        }
    }
    echo render('admin/auth', ['mode' => $mode, 'error' => $error, 'notice' => $error === '' ? (flash()['message'] ?? '') : '']);
}

/**
 * Forgotten password: anyone who knows the recovery code may set a new password for an account.
 * The code is created under Settings, shown once, and only its hash is kept on the server.
 */
function admin_recover(bool $post): void
{
    if (current_user()) {
        redirect('/admin/settings#account');
    }
    start_session();
    $error = '';
    $stored = (string) (read_data('recovery')['hash'] ?? '');
    if ($post) {
        csrf_check();
        $all = users();
        $name = strtolower(clean_line($_POST['username'] ?? '', 40));
        $code = strtoupper(preg_replace('/[^A-Za-z0-9]/', '', (string) ($_POST['code'] ?? '')) ?? '');
        $new = (string) ($_POST['new_password'] ?? '');
        // Always run the hash check, so the response time does not reveal whether a code is set.
        $match = password_verify($code, $stored !== '' ? $stored : '$2y$10$usesomesillystringfore7hnbRJHxXVLeakoG8K30oukPsA.ztMG') && $stored !== '';
        if (!rate_limit_ok('recover', 5, 900)) {
            $error = 'Too many attempts. Wait 15 minutes and try again.';
        } elseif (!$match || !isset($all[$name])) {
            audit('Failed password recovery for "' . $name . '"');
            $error = 'The username or the recovery code is not right.';
        } elseif ($problem = password_problem($new, $name)) {
            $error = $problem;
        } else {
            $all[$name]['hash'] = password_hash($new, PASSWORD_DEFAULT);
            $all[$name]['epoch'] = ($all[$name]['epoch'] ?? 0) + 1;     // signs the account out everywhere
            unset($all[$name]['must_change']);
            write_data('users', $all);
            rate_limit_clear('recover');
            audit('Password reset with the recovery code', $name);
            flash('Password changed. Sign in with your new password.');
            redirect('/admin/login');
        }
    }
    echo render('admin/auth', ['mode' => 'recover', 'error' => $error]);
}

function admin_logout(bool $post, string $user): void
{
    if ($post) {
        audit('Signed out', $user);
        $_SESSION = [];
        session_destroy();
        setcookie('vartec_admin', '', ['expires' => 1, 'path' => '/', 'secure' => is_https(), 'httponly' => true, 'samesite' => 'Lax']);
    }
    redirect('/admin/login');
}

// ---------------------------------------------------------------- dashboard, publish

function admin_dashboard(bool $post, string $user): void
{
    $content = draft_content();
    $usage = media_usage($content);
    $flagged = array_filter($content['media'], fn ($item, $id) => isset($usage[$id]) && media_needs_check($item), ARRAY_FILTER_USE_BOTH);
    admin_page_out('Dashboard', render('admin/dashboard', ['content' => $content, 'flagged' => $flagged, 'usage' => $usage,
        'welcome' => empty(users()[$user]['guide_hidden']) && is_file(GUIDE_FILE),
        'enquiries' => array_slice(read_data('enquiries'), 0, 5), 'changes' => has_unpublished_changes()]), $user, 'dashboard');
}

function admin_publish(bool $post, string $user): void
{
    if ($post && has_unpublished_changes()) {
        publish_draft($user);
        audit('Published the website', $user);
        purge_removed_media();
        flash('Published. Your changes are now live on the website.');
    }
    redirect('/admin/');
}

function admin_discard(bool $post, string $user): void
{
    if ($post) {
        @unlink(data_dir() . '/draft.php');
        audit('Discarded unpublished changes', $user);
        purge_removed_media();
        flash('Unpublished changes were discarded. The admin now matches the live website.');
    }
    redirect('/admin/');
}

// ---------------------------------------------------------------- home page

function admin_home(bool $post, string $user): void
{
    $content = draft_content();
    if ($post) {
        $in = $_POST;
        $home = &$content['home'];
        $home['hero']['eyebrow'] = clean_line($in['hero_eyebrow'] ?? '', 120);
        $home['hero']['title'] = clean_line($in['hero_title'] ?? '', 120) ?: $home['hero']['title'];
        $home['hero']['summary'] = clean_text($in['hero_summary'] ?? '', 600);
        $home['hero']['points'] = array_values(array_filter(array_map(fn ($p) => clean_line($p, 60), (array) ($in['hero_points'] ?? []))));
        $home['hero']['slides'] = array_values(array_unique(array_filter(array_map(fn ($id) => valid_media($content, $id), (array) ($in['slides'] ?? [])))));
        $home['about']['heading'] = clean_line($in['about_heading'] ?? '', 120);
        $home['about']['paragraphs'] = array_values(array_filter(array_map(fn ($p) => clean_text($p, 3000), (array) ($in['about_paragraphs'] ?? []))));
        $home['about']['video_label'] = clean_line($in['video_label'] ?? '', 80);
        $home['about']['video'] = valid_media($content, $in['video'] ?? '', 'video');
        $home['about']['poster'] = valid_media($content, $in['poster'] ?? '');
        $home['capabilities']['eyebrow'] = clean_line($in['cap_eyebrow'] ?? '', 120);
        $home['capabilities']['heading'] = clean_line($in['cap_heading'] ?? '', 160);
        $home['capabilities']['intro'] = clean_text($in['cap_intro'] ?? '', 600);
        $cards = [];
        foreach ((array) ($in['cards'] ?? []) as $card) {
            $title = clean_line($card['title'] ?? '', 120);
            if ($title !== '') {
                $cards[] = ['title' => $title, 'body' => clean_text($card['body'] ?? '', 600)];
            }
        }
        $home['capabilities']['cards'] = $cards;
        $home['services_heading'] = clean_line($in['services_heading'] ?? '', 160);
        $home['projects_heading'] = clean_line($in['projects_heading'] ?? '', 160);
        $home['contact']['heading'] = clean_line($in['contact_heading'] ?? '', 160);
        $home['contact']['text'] = array_values(array_filter(array_map(fn ($p) => clean_text($p, 600), (array) ($in['contact_text'] ?? []))));
        $home['contact']['form_heading'] = clean_line($in['form_heading'] ?? '', 160);
        unset($home);
        save_draft($content);
        flash('Home page saved as a draft. Preview it, then publish when you are happy.');
        redirect('/admin/home');
    }
    admin_page_out('Home page', render('admin/home', ['content' => $content]), $user, 'home');
}

// ---------------------------------------------------------------- services and projects

function admin_pages(bool $post, string $user): void
{
    $kind = page_kind($_GET['kind'] ?? '');
    $content = draft_content();
    admin_page_out(PAGE_KINDS[$kind][0], render('admin/pages', ['content' => $content, 'kind' => $kind,
        'pages' => array_values(array_filter($content['pages'], fn ($p) => $p['kind'] === $kind))]), $user, $kind);
}

/** Saves the order (and visibility switches) of the services or projects list. */
function admin_pages_order(bool $post, string $user): void
{
    $kind = page_kind($_POST['kind'] ?? '');
    if ($post) {
        $content = draft_content();
        $ids = array_map('strval', (array) ($_POST['ids'] ?? []));
        $visible = array_map('strval', (array) ($_POST['visible'] ?? []));
        $mine = $other = [];
        foreach ($content['pages'] as $page) {
            if ($page['kind'] === $kind) {
                $page['visible'] = in_array($page['id'], $visible, true);
                $mine[$page['id']] = $page;
            } else {
                $other[] = $page;
            }
        }
        $ordered = [];
        foreach ($ids as $id) {
            if (isset($mine[$id])) {
                $ordered[] = $mine[$id];
                unset($mine[$id]);
            }
        }
        $ordered = array_merge($ordered, array_values($mine));
        $content['pages'] = $kind === 'service' ? array_merge($ordered, $other) : array_merge($other, $ordered);
        save_draft($content);
        flash('Order and visibility saved as a draft.');
    }
    redirect('/admin/pages?kind=' . $kind);
}

function admin_page(bool $post, string $user): void
{
    $content = draft_content();
    $id = (string) ($_GET['id'] ?? '');
    $index = null;
    foreach ($content['pages'] as $n => $candidate) {
        if ($candidate['id'] === $id) {
            $index = $n;
        }
    }
    $isNew = $index === null;
    $kind = $isNew ? page_kind($_GET['kind'] ?? '') : $content['pages'][$index]['kind'];
    if ($id !== '' && $isNew) {
        flash('That page no longer exists.', 'error');
        redirect('/admin/pages?kind=' . $kind);
    }
    $page = $isNew ? ['id' => '', 'kind' => $kind, 'slug' => '', 'title' => '', 'intro' => '', 'seo_title' => '', 'seo_description' => '',
        'card_image' => '', 'banner_image' => '', 'visible' => true, 'sections' => []] : $content['pages'][$index];
    $errors = [];

    if ($post) {
        $in = $_POST;
        $page['title'] = clean_line($in['title'] ?? '', 160);
        $page['intro'] = clean_text($in['intro'] ?? '', 1200);
        $page['card_image'] = valid_media($content, $in['card_image'] ?? '');
        $page['banner_image'] = valid_media($content, $in['banner_image'] ?? '');
        $page['visible'] = !empty($in['visible']);
        $page['seo_title'] = clean_line($in['seo_title'] ?? '', 120);
        $page['seo_description'] = clean_line($in['seo_description'] ?? '', 400);
        $sections = [];
        foreach (array_values((array) ($in['sections'] ?? [])) as $n => $raw) {
            $items = [];
            foreach (array_values((array) ($raw['items'] ?? [])) as $item) {
                $text = clean_text($item['text'] ?? '', 2000);
                $type = in_array($item['type'] ?? '', ['paragraph', 'bullet', 'numbered', 'subheading'], true) ? $item['type'] : 'paragraph';
                if ($text !== '') {
                    $items[] = ['type' => $type, 'text' => $text];
                }
            }
            $section = ['id' => 's' . ($n + 1), 'heading' => clean_line($raw['heading'] ?? '', 300), 'body' => clean_text($raw['body'] ?? '', 4000),
                'image' => valid_media($content, $raw['image'] ?? ''), 'items' => $items];
            if ($section['heading'] !== '' || $section['body'] !== '' || $section['image'] !== '' || $items) {
                $sections[] = $section;
            }
        }
        $page['sections'] = $sections;
        if ($page['title'] === '') {
            $errors[] = 'Give the page a title.';
        }
        $slug = slugify(clean_line($in['slug'] ?? '', 80) ?: $page['title']);
        foreach ($content['pages'] as $n => $other) {
            if ($other['kind'] === $kind && $other['slug'] === $slug && $n !== $index) {
                $errors[] = 'Another ' . PAGE_KINDS[$kind][1] . ' already uses the address "' . $slug . '". Choose a different one.';
            }
        }
        if ($kind === 'info' && in_array($slug, RESERVED_SLUGS, true)) {
            $errors[] = 'The address "' . $slug . '" is used by the website itself. Choose a different one.';
        }
        if (!$errors) {
            $page['slug'] = $slug;
            if ($isNew) {
                $page['id'] = $kind . '-' . $slug . '-' . bin2hex(random_bytes(2));
                $content['pages'][] = $page;
            } else {
                $content['pages'][$index] = $page;
            }
            save_draft($content);
            flash('"' . $page['title'] . '" saved as a draft. Preview it, then publish when you are happy.');
            redirect('/admin/page?id=' . rawurlencode($page['id']));
        }
    }
    admin_page_out($isNew ? 'New ' . PAGE_KINDS[$kind][1] : $page['title'], render('admin/page', ['content' => $content, 'page' => $page, 'isNew' => $isNew,
        'errors' => $errors]), $user, $kind);
}

function admin_page_delete(bool $post, string $user): void
{
    $content = draft_content();
    $id = (string) ($_POST['id'] ?? '');
    $kind = 'service';
    foreach ($content['pages'] as $n => $page) {
        if ($page['id'] === $id && $post) {
            $kind = $page['kind'];
            array_splice($content['pages'], $n, 1);
            save_draft($content);
            flash('"' . $page['title'] . '" was removed from the draft. It stays on the live website until you publish. Discard changes to bring it back.');
            break;
        }
    }
    redirect('/admin/pages?kind=' . $kind);
}

// ---------------------------------------------------------------- images and video

function admin_media(bool $post, string $user): void
{
    $content = draft_content();
    admin_page_out('Images and video', render('admin/media', ['content' => $content, 'usage' => media_usage($content),
        'filter' => (string) ($_GET['show'] ?? 'all'), 'max_upload' => upload_limit_bytes()]), $user, 'media');
}

function upload_limit_bytes(): int
{
    $toBytes = function (string $value): int {
        $number = (int) $value;
        return match (strtolower(substr(trim($value), -1))) { 'g' => $number << 30, 'm' => $number << 20, 'k' => $number << 10, default => $number };
    };
    return min($toBytes((string) ini_get('upload_max_filesize')), $toBytes((string) ini_get('post_max_size')));
}

/**
 * Stores an uploaded image or MP4 and returns [media id, record], or an error message.
 * Images are checked by reading them (not by trusting the file name), resized to at most
 * 1600px wide and saved as WebP when the server can do so.
 */
function store_upload(array $file, string $alt, string $source, string $licence, array $content): array|string
{
    if (($file['error'] ?? UPLOAD_ERR_NO_FILE) !== UPLOAD_ERR_OK || !is_uploaded_file($file['tmp_name'] ?? '')) {
        return ($file['error'] ?? 0) === UPLOAD_ERR_INI_SIZE ? 'That file is larger than this server accepts.' : 'Choose a file to upload.';
    }
    if ($alt === '') {
        return 'Describe what the image shows. Screen readers and search engines use this.';
    }
    $ext = strtolower(pathinfo((string) $file['name'], PATHINFO_EXTENSION));
    $base = slugify($alt);
    $base = substr($base, 0, 60) . '-' . bin2hex(random_bytes(3));
    if (!is_dir(MEDIA_DIR . '/uploads')) {
        mkdir(MEDIA_DIR . '/uploads', 0755, true);
    }
    $record = ['kind' => 'image', 'alt' => $alt, 'source' => $source, 'licence' => isset(LICENCES[$licence]) ? $licence : 'unknown', 'added' => gmdate('c')];

    if ($ext === 'mp4') {
        // An MP4 file carries the marker "ftyp" at bytes 4-8; checked directly so no extension is needed.
        $head = (string) file_get_contents($file['tmp_name'], false, null, 0, 12);
        $mime = class_exists('finfo') ? (new finfo(FILEINFO_MIME_TYPE))->file($file['tmp_name']) : 'video/mp4';
        if (substr($head, 4, 4) !== 'ftyp' || $mime !== 'video/mp4') {
            return 'That file is not a valid MP4 video.';
        }
        $record['kind'] = 'video';
        $record['file'] = 'uploads/' . $base . '.mp4';
        if (!move_uploaded_file($file['tmp_name'], MEDIA_DIR . '/' . $record['file'])) {
            return 'The video could not be saved.';
        }
    } else {
        $info = @getimagesize($file['tmp_name']);
        $types = [IMAGETYPE_JPEG => 'jpg', IMAGETYPE_PNG => 'png', IMAGETYPE_WEBP => 'webp', IMAGETYPE_GIF => 'gif'];
        if (!$info || !isset($types[$info[2]])) {
            return 'Upload a JPG, PNG, WebP or GIF image, or an MP4 video.';
        }
        [$width, $height] = $info;
        $saved = false;
        if (function_exists('imagecreatefromstring') && function_exists('imagewebp') && $width * $height <= 40_000_000) {
            $image = @imagecreatefromstring((string) file_get_contents($file['tmp_name']));
            if ($image) {
                if ($width > 1600) {
                    $scaled = imagescale($image, 1600);
                    if ($scaled) {
                        $image = $scaled;
                    }
                }
                imagepalettetotruecolor($image);
                imagesavealpha($image, true);
                $record['file'] = 'uploads/' . $base . '.webp';
                $saved = imagewebp($image, MEDIA_DIR . '/' . $record['file'], 82);
                [$width, $height] = [imagesx($image), imagesy($image)];
            }
        }
        if (!$saved) {
            $record['file'] = 'uploads/' . $base . '.' . $types[$info[2]];
            if (!move_uploaded_file($file['tmp_name'], MEDIA_DIR . '/' . $record['file'])) {
                return 'The image could not be saved.';
            }
        }
        $record['w'] = $width;
        $record['h'] = $height;
    }
    return [basename($record['file'], '.' . pathinfo($record['file'], PATHINFO_EXTENSION)), $record];
}

function admin_media_upload(bool $post, string $user): void
{
    $wantsJson = str_contains($_SERVER['HTTP_ACCEPT'] ?? '', 'application/json');
    $content = draft_content();
    $result = $post ? store_upload($_FILES['file'] ?? [], clean_line($_POST['alt'] ?? '', 200), clean_line($_POST['source'] ?? '', 300),
        (string) ($_POST['licence'] ?? 'unknown'), $content) : 'Choose a file to upload.';
    if (is_array($result)) {
        [$id, $record] = $result;
        $content['media'][$id] = $record;
        save_draft($content);
    }
    if ($wantsJson) {
        header('Content-Type: application/json; charset=utf-8');
        if (!is_array($result)) {
            http_response_code(422);
        }
        echo json_encode(is_array($result) ? ['ok' => true, 'id' => $result[0], 'url' => media_url($content, $result[0]), 'alt' => $result[1]['alt'],
            'kind' => $result[1]['kind'], 'check' => media_needs_check($result[1])] : ['ok' => false, 'error' => $result]);
        return;
    }
    is_array($result) ? flash('Uploaded. You can now choose it on any page.') : flash($result, 'error');
    redirect('/admin/media');
}

function admin_media_edit(bool $post, string $user): void
{
    $content = draft_content();
    $id = (string) ($_GET['id'] ?? '');
    if (!isset($content['media'][$id])) {
        redirect('/admin/media');
    }
    if ($post) {
        $alt = clean_line($_POST['alt'] ?? '', 200);
        if ($alt === '' && $content['media'][$id]['kind'] === 'image') {
            flash('Describe what the image shows.', 'error');
            redirect('/admin/media/edit?id=' . rawurlencode($id));
        }
        $content['media'][$id]['alt'] = $alt;
        $content['media'][$id]['source'] = clean_line($_POST['source'] ?? '', 300);
        $content['media'][$id]['licence'] = isset(LICENCES[$_POST['licence'] ?? '']) ? $_POST['licence'] : 'unknown';
        save_draft($content);
        flash('Details saved as a draft.');
        redirect('/admin/media');
    }
    admin_page_out('Image details', render('admin/media_edit', ['content' => $content, 'id' => $id, 'item' => $content['media'][$id],
        'usage' => media_usage($content)[$id] ?? []]), $user, 'media');
}

/**
 * Deletes picture and video files that are in neither the live website's library nor the draft's.
 * This is what makes "remove" real: a removed photo is no longer reachable at its old address.
 * Returns how many files were deleted.
 */
function purge_removed_media(): int
{
    $keep = [];
    foreach ([live_content(), draft_content()] as $content) {
        foreach ($content['media'] ?? [] as $item) {
            $keep[(string) ($item['file'] ?? '')] = true;
        }
    }
    if (count($keep) < 1) {
        return 0; // never empty the folder because a library could not be read
    }
    $deleted = 0;
    // The starter pictures sit in media/, uploaded ones in media/uploads/.
    foreach (array_merge(glob(MEDIA_DIR . '/*') ?: [], glob(MEDIA_DIR . '/uploads/*') ?: []) as $file) {
        $name = substr($file, strlen(MEDIA_DIR) + 1);
        if (is_file($file) && !isset($keep[$name]) && @unlink($file)) {
            $deleted++;
        }
    }
    if ($deleted) {
        audit('Deleted ' . $deleted . ' removed file' . ($deleted === 1 ? '' : 's') . ' from the server');
    }
    return $deleted;
}

function admin_media_delete(bool $post, string $user): void
{
    $content = draft_content();
    $id = (string) ($_POST['id'] ?? '');
    if ($post && isset($content['media'][$id])) {
        if (!empty(media_usage($content)[$id])) {
            flash('That file is still used on a page. Remove it from the page first.', 'error');
        } else {
            // A file the live website still lists stays until the next publish, so the live site never shows
            // a broken picture. After that it is deleted from the server for good (see purge_removed_media).
            unset($content['media'][$id]);
            save_draft($content);
            $gone = purge_removed_media();
            flash($gone ? 'Removed from the library and deleted from the server.' : 'Removed from the library. The file is deleted from the server when you next publish.');
        }
    }
    redirect('/admin/media');
}

// ---------------------------------------------------------------- enquiries

function admin_enquiries(bool $post, string $user): void
{
    $all = read_data('enquiries');
    if ($post) {
        $id = (string) ($_POST['id'] ?? '');
        $action = (string) ($_POST['action'] ?? '');
        foreach ($all as $n => $entry) {
            if ($entry['id'] !== $id) {
                continue;
            }
            if ($action === 'delete') {
                array_splice($all, $n, 1);
            } elseif (in_array($action, ['new', 'done'], true)) {
                $all[$n]['status'] = $action;
            }
            break;
        }
        write_data('enquiries', $all);
        redirect('/admin/enquiries');
    }
    admin_page_out('Enquiries', render('admin/enquiries', ['enquiries' => $all]), $user, 'enquiries');
}

// ---------------------------------------------------------------- settings, editors, history, help

function admin_settings(bool $post, string $user): void
{
    $content = draft_content();
    if ($post) {
        $s = &$content['settings'];
        $in = $_POST;
        $email = clean_line($in['contact_email'] ?? '', 254);
        $url = rtrim(clean_line($in['site_url'] ?? '', 200), '/');
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            flash('Enter a valid contact email address.', 'error');
            redirect('/admin/settings');
        }
        if (!preg_match('#^https?://[a-z0-9.-]+$#i', $url)) {
            flash('The website address should look like https://vartec.global', 'error');
            redirect('/admin/settings');
        }
        $s['contact_email'] = $email;
        $s['site_url'] = $url;
        $s['phone'] = clean_line($in['phone'] ?? '', 40);
        $s['office_hours_weekdays'] = clean_line($in['office_hours_weekdays'] ?? '', 80);
        $s['office_hours_weekend'] = clean_line($in['office_hours_weekend'] ?? '', 80);
        $s['footer_about'] = clean_text($in['footer_about'] ?? '', 400);
        $s['footer_copyright'] = clean_line($in['footer_copyright'] ?? '', 200);
        $s['seo_title'] = clean_line($in['seo_title'] ?? '', 120);
        $s['seo_description'] = clean_line($in['seo_description'] ?? '', 400);
        $s['logo'] = valid_media($content, $in['logo'] ?? '') ?: $s['logo'];
        $s['chat_enabled'] = !empty($in['chat_enabled']);
        $s['chat_title'] = clean_line($in['chat_title'] ?? '', 80);
        $s['chat_welcome'] = clean_line($in['chat_welcome'] ?? '', 240);
        $answers = [];
        foreach (array_values((array) ($in['answers'] ?? [])) as $raw) {
            $answer = ['topic' => clean_line($raw['topic'] ?? '', 40), 'keywords' => strtolower(clean_line($raw['keywords'] ?? '', 300)), 'answer' => clean_text($raw['answer'] ?? '', 600)];
            if ($answer['answer'] !== '' && ($answer['topic'] !== '' || $answer['keywords'] !== '')) {
                $answers[] = $answer;
            }
        }
        $s['chat_answers'] = array_slice($answers, 0, 30);
        $s['chat_fallback'] = clean_text($in['chat_fallback'] ?? '', 600) ?: CHAT_FALLBACK;
        // Accepts either the bare code or the whole <meta ...> line Google gives.
        $code = clean_line($in['google_verification'] ?? '', 400);
        if (preg_match('/content=["\']([^"\']+)["\']/i', $code, $found)) {
            $code = $found[1];
        }
        if ($code !== '' && !preg_match('/^[A-Za-z0-9_-]{10,120}$/', $code)) {
            flash('The Google verification code should be the long code Google shows, for example abc123XYZ_-…', 'error');
            redirect('/admin/settings');
        }
        $s['google_verification'] = $code;
        foreach (SOCIAL as $key => $label) {
            $link = clean_line($in['social'][$key] ?? '', 300);
            if ($link !== '' && !preg_match('#^https://[a-z0-9.-]+\.[a-z]{2,}(/[^\s"<>]*)?$#i', $link)) {
                flash('The ' . $label . ' link should start with https://', 'error');
                redirect('/admin/settings');
            }
            $s['social'][$key] = $link;
        }
        unset($s);
        save_draft($content);
        flash('Settings saved as a draft.');
        redirect('/admin/settings');
    }
    start_session();
    admin_page_out('Settings', render('admin/settings', ['content' => $content, 'user' => $user, 'editors' => array_keys(users()),
        'recovery' => read_data('recovery'), 'recovery_once' => (function () { $c = $_SESSION['recovery_once'] ?? null; unset($_SESSION['recovery_once']); return $c; })(),
        'two_step_on' => !empty(users()[$user]['totp']), 'two_step_setup' => $_SESSION['totp_setup'] ?? null, 'activity' => array_slice(read_data('audit'), 0, 15)]), $user, 'settings');
}

function admin_password(bool $post, string $user): void
{
    if ($post) {
        $all = users();
        $new = (string) ($_POST['new_password'] ?? '');
        if (!password_verify((string) ($_POST['current_password'] ?? ''), $all[$user]['hash'])) {
            flash('Your current password is not right.', 'error');
        } elseif ($problem = password_problem($new, $user)) {
            flash($problem, 'error');
        } elseif (password_verify($new, $all[$user]['hash'])) {
            flash('Choose a password that is different from the current one.', 'error');
        } else {
            $all[$user]['hash'] = password_hash($new, PASSWORD_DEFAULT);
            $all[$user]['epoch'] = ($all[$user]['epoch'] ?? 0) + 1; // signs out every other browser
            $wasFirst = !empty($all[$user]['must_change']);
            unset($all[$user]['must_change']);
            write_data('users', $all);
            sign_in($user);
            audit('Changed their password', $user);
            flash('Password changed. Any other browser signed in with this account has been signed out.');
            if ($wasFirst) {
                redirect('/admin/');
            }
        }
    }
    redirect(!empty(users()[$user]['must_change']) ? '/admin/' : '/admin/settings#account');
}

/** Creates (or replaces) the recovery code. It is shown once; the server keeps only its hash. */
function admin_recovery_code(bool $post, string $user): void
{
    if ($post) {
        if (!password_verify((string) ($_POST['current_password'] ?? ''), users()[$user]['hash'])) {
            flash('Your current password is not right.', 'error');
        } else {
            $raw = strtoupper(bin2hex(random_bytes(10)));
            write_data('recovery', ['hash' => password_hash($raw, PASSWORD_DEFAULT), 'created' => gmdate('c'), 'by' => $user]);
            start_session();
            $_SESSION['recovery_once'] = implode('-', str_split($raw, 5));
            audit('Created a new recovery code', $user);
            flash('A new recovery code was created. Write it down now: it is shown only once.');
        }
    }
    redirect('/admin/settings#recovery');
}

function admin_editors(bool $post, string $user): void
{
    if ($post) {
        $all = users();
        $name = strtolower(clean_line($_POST['username'] ?? '', 40));
        if (($_POST['action'] ?? '') === 'remove') {
            if ($name === $user) {
                flash('You cannot remove your own account.', 'error');
            } elseif (isset($all[$name])) {
                unset($all[$name]);
                write_data('users', $all);
                audit('Removed editor "' . $name . '"', $user);
                flash('Editor removed.');
            }
        } else {
            $password = (string) ($_POST['password'] ?? '');
            if (!preg_match('/^[a-z0-9._-]{3,40}$/', $name) || isset($all[$name])) {
                flash('Choose a new username of 3 to 40 letters or numbers.', 'error');
            } elseif ($problem = password_problem($password, $name)) {
                flash($problem, 'error');
            } else {
                $all[$name] = ['hash' => password_hash($password, PASSWORD_DEFAULT), 'created' => gmdate('c'), 'epoch' => 0, 'must_change' => true];
                write_data('users', $all);
                audit('Added editor "' . $name . '"', $user);
                flash('Editor added. Give them the username and password privately. They will be asked to choose their own password the first time they sign in.');
            }
        }
    }
    redirect('/admin/settings#editors');
}

/** Two-step sign-in: turn on (show key, confirm a code) or off (password required). */
function admin_two_step(bool $post, string $user): void
{
    if ($post) {
        start_session();
        $all = users();
        $action = (string) ($_POST['action'] ?? '');
        if ($action === 'start') {
            $_SESSION['totp_setup'] = base32_encode_bytes(random_bytes(20));
        } elseif ($action === 'cancel') {
            unset($_SESSION['totp_setup']);
        } elseif ($action === 'confirm' && !empty($_SESSION['totp_setup'])) {
            $used = totp_verify($_SESSION['totp_setup'], (string) ($_POST['code'] ?? ''));
            if ($used === null) {
                flash('That code is not right. Check the key in your app and enter the current code.', 'error');
            } else {
                $all[$user]['totp'] = $_SESSION['totp_setup'];
                $all[$user]['totp_last'] = $used;
                write_data('users', $all);
                unset($_SESSION['totp_setup']);
                audit('Turned on two-step sign-in', $user);
                flash('Two-step sign-in is on. From now on you will be asked for a code from your app when you sign in.');
            }
        } elseif ($action === 'disable') {
            if (!password_verify((string) ($_POST['current_password'] ?? ''), $all[$user]['hash'])) {
                flash('Your password is not right.', 'error');
            } else {
                unset($all[$user]['totp'], $all[$user]['totp_last']);
                write_data('users', $all);
                audit('Turned off two-step sign-in', $user);
                flash('Two-step sign-in is off.');
            }
        }
    }
    redirect('/admin/settings#two-step');
}

function admin_history(bool $post, string $user): void
{
    if ($post) {
        $id = preg_replace('/[^0-9-]/', '', (string) ($_POST['id'] ?? ''));
        $version = read_data('history/' . $id);
        if (!empty($version['content'])) {
            // Pictures deleted from the server since that version was saved are left out, not shown broken.
            foreach ($version['content']['media'] ?? [] as $mediaId => $item) {
                if (!is_file(MEDIA_DIR . '/' . ($item['file'] ?? ''))) {
                    unset($version['content']['media'][$mediaId]);
                }
            }
            save_draft($version['content']);
            audit('Restored an earlier version as a draft', $user);
            flash('That version is loaded as a draft. Preview it, then publish to make it live.');
            redirect('/admin/');
        }
        redirect('/admin/history');
    }
    admin_page_out('Earlier versions', render('admin/history', ['versions' => history_versions()]), $user, 'settings');
}

/** Short fixed wording on the public site: menu names, button texts, form labels. */
function admin_wording(bool $post, string $user): void
{
    $content = draft_content();
    if ($post) {
        $saved = [];
        foreach (WORDING as $key => [$group, $label, $default]) {
            $text = clean_line($_POST['w'][$key] ?? '', 160);
            if ($text !== '' && $text !== $default) {
                $saved[$key] = $text;
            }
        }
        $content['settings']['wording'] = $saved;
        save_draft($content);
        flash('Wording saved as a draft. Preview it, then publish when you are happy.');
        redirect('/admin/wording');
    }
    admin_page_out('Wording', render('admin/wording', ['content' => $content]), $user, 'wording');
}

const GUIDE_FILE = APP_DIR . '/guide/VARTEC-admin-guide.pdf';

/** The illustrated user guide (PDF). Only signed-in editors reach this; the file is not web-accessible itself. */
function admin_guide(bool $post, string $user): void
{
    if ($post) {
        $all = users();
        $all[$user]['guide_hidden'] = true;      // "Hide this" on the dashboard welcome card
        write_data('users', $all);
        redirect('/admin/');
    }
    if (!is_file(GUIDE_FILE)) {
        http_response_code(404);
        admin_page_out('Guide', '<div class="card"><h2>The guide is not installed</h2><p><a href="/admin/help">Open Help instead</a></p></div>', $user, 'help');
        return;
    }
    header_remove('Content-Security-Policy');     // lets the browser's own PDF viewer open it
    header('Content-Type: application/pdf');
    header('Content-Disposition: inline; filename="VARTEC-admin-guide.pdf"');
    header('Content-Length: ' . filesize(GUIDE_FILE));
    readfile(GUIDE_FILE);
}

function admin_help(bool $post, string $user): void
{
    admin_page_out('Help', render('admin/help', ['has_guide' => is_file(GUIDE_FILE)]), $user, 'help');
}
