<?php
declare(strict_types=1);

/**
 * Shared foundations: paths, safe file storage, content (draft and live), sessions and users.
 *
 * Storage is plain files so the site needs no database. Every data file is a .php file that
 * starts with GUARD, so it reveals nothing even if a server were to serve the data folder.
 */

const APP_VERSION = '1.4.0';
const GUARD = "<?php http_response_code(404); exit; ?>\n";
const HISTORY_KEEP = 30;
const SESSION_IDLE_SECONDS = 7200;      // signed out after 2 hours without activity
const SESSION_MAX_SECONDS = 43200;      // and after 12 hours in any case

define('APP_DIR', __DIR__);
define('PUBLIC_DIR', dirname(__DIR__));
define('MEDIA_DIR', PUBLIC_DIR . '/media');

/** Private data folder: beside the web root when possible, otherwise the guarded /data folder. */
function data_dir(): string
{
    static $dir = null;
    if ($dir !== null) {
        return $dir;
    }
    $candidates = array_filter([getenv('VARTEC_DATA_DIR') ?: null, dirname(PUBLIC_DIR) . '/vartec-data', PUBLIC_DIR . '/data']);
    foreach ($candidates as $candidate) {
        if ((is_dir($candidate) || @mkdir($candidate, 0750, true)) && is_writable($candidate)) {
            if (!is_file($candidate . '/.htaccess')) {
                @file_put_contents($candidate . '/.htaccess', "Require all denied\n");
            }
            return $dir = $candidate;
        }
    }
    http_response_code(500);
    exit('The website cannot write to its data folder. Check folder permissions.');
}

// Stand-ins for optional PHP extensions, so the site runs on hosts that lack them.
if (!function_exists('mb_substr')) {
    function mb_substr(string $text, int $start, ?int $length = null): string
    {
        $chars = preg_split('//u', $text, -1, PREG_SPLIT_NO_EMPTY) ?: str_split($text);
        return implode('', array_slice($chars, $start, $length));
    }
}
if (!function_exists('mb_strlen')) {
    function mb_strlen(string $text): int
    {
        return count(preg_split('//u', $text, -1, PREG_SPLIT_NO_EMPTY) ?: str_split($text));
    }
}

function e(?string $text): string
{
    return htmlspecialchars((string) $text, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

function read_data(string $name, array $default = []): array
{
    $file = data_dir() . '/' . $name . '.php';
    if (!is_file($file)) {
        return $default;
    }
    $raw = (string) file_get_contents($file);
    $json = str_starts_with($raw, GUARD) ? substr($raw, strlen(GUARD)) : $raw;
    $value = json_decode($json, true);
    return is_array($value) ? $value : $default;
}

/** Atomic write: a half-written file can never replace a good one. */
function write_data(string $name, array $value): void
{
    $file = data_dir() . '/' . $name . '.php';
    if (!is_dir(dirname($file))) {
        mkdir(dirname($file), 0750, true);
    }
    $tmp = $file . '.' . bin2hex(random_bytes(4)) . '.tmp';
    $json = json_encode($value, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    if ($json === false || file_put_contents($tmp, GUARD . $json, LOCK_EX) === false || !rename($tmp, $file)) {
        @unlink($tmp);
        throw new RuntimeException('Could not save ' . $name);
    }
}

// ---------------------------------------------------------------- content

function seed_content(): array
{
    return json_decode((string) file_get_contents(APP_DIR . '/seed/content.json'), true);
}

/** The three kinds of page: [name in the admin menu, word for one page, start of its web address]. */
const PAGE_KINDS = [
    'service' => ['Services', 'service', '/services/'],
    'project' => ['Projects', 'project', '/projects/'],
    'info' => ['Other pages', 'page', '/'],
];

/** Addresses an "other page" may not take, because the site itself uses them. */
const RESERVED_SLUGS = ['admin', 'services', 'projects', 'service', 'project', 'media', 'assets', 'app', 'data', 'vartec-data',
    'enquiry', 'home', 'index', 'favicon', 'robots', 'sitemap', 'send-mail', 'cgi-bin', 'preview'];

/**
 * Short fixed wording on the public site that editors may change (Admin > Wording).
 * key => [group shown in the admin, what it is, the wording used when the box is left empty].
 */
const WORDING = [
    'menu_home' => ['Menu', 'Home link', 'Home'],
    'menu_about' => ['Menu', 'About link', 'About Us'],
    'menu_services' => ['Menu', 'Services menu', 'Services'],
    'menu_projects' => ['Menu', 'Projects menu', 'Projects'],
    'menu_contact' => ['Menu', 'Contact button', 'Contact Us'],
    'btn_services' => ['Buttons', 'Banner button to the services', 'Our Services'],
    'btn_discuss' => ['Buttons', 'Button to the contact form', 'Discuss a project'],
    'link_service' => ['Buttons', 'Link on a service card', 'Explore service'],
    'link_project' => ['Buttons', 'Link on a project card', 'View project'],
    'label_about' => ['Small lines above headings', 'About section', 'Who we are'],
    'label_services' => ['Small lines above headings', 'Services section', 'Services'],
    'label_projects' => ['Small lines above headings', 'Projects section', 'Projects'],
    'label_contact' => ['Small lines above headings', 'Contact section', 'Contact Us'],
    'more_services' => ['Small lines above headings', 'Heading under a service page', 'More services'],
    'more_projects' => ['Small lines above headings', 'Heading under a project page', 'More projects'],
    'form_first' => ['Contact form', 'First name box', 'First Name'],
    'form_last' => ['Contact form', 'Last name box', 'Last Name'],
    'form_email' => ['Contact form', 'Email box', 'Email Address'],
    'form_phone' => ['Contact form', 'Phone box', 'Phone Number'],
    'form_message' => ['Contact form', 'Message box', 'Message'],
    'btn_send' => ['Contact form', 'Send button', 'Send message'],
    'form_thanks' => ['Contact form', 'Shown after a message is sent', 'Thank you. Your message has been received.'],
    'form_error' => ['Contact form', 'Shown if sending fails', 'Your message could not be sent. Please try again, or email us directly.'],
    'contact_phone' => ['Contact details', 'Phone', 'Phone'],
    'contact_email' => ['Contact details', 'Email', 'Email'],
    'contact_hours' => ['Contact details', 'Office hours', 'Office hours'],
    'notfound_title' => ['Page not found', 'Heading', 'Page not found'],
    'notfound_text' => ['Page not found', 'Text', 'The page you are looking for has moved or no longer exists.'],
];

/** Starting answers for the help chat; editors change them under Settings. */
const CHAT_ANSWERS = [
    ['topic' => 'Solar services', 'keywords' => 'service, epc, engineering, design, procurement, construction', 'answer' => 'We provide engineering, detailed design, procurement, construction, commissioning and ongoing maintenance for solar and energy-storage projects.'],
    ['topic' => 'O&M support', 'keywords' => 'o&m, maintenance, operation, clean, testing, monitor', 'answer' => 'Our operations and maintenance support includes monitoring, diagnostics, electrical testing, panel cleaning and planned site maintenance.'],
    ['topic' => 'Request a quote', 'keywords' => 'quote, price, cost, contact, phone, email, speak', 'answer' => 'For a project discussion or quotation, please contact our team. We will connect you with the right specialist.'],
    ['topic' => 'Battery storage', 'keywords' => 'battery, storage, bess', 'answer' => 'VARTEC supports battery energy storage projects alongside solar PV, from engineering and procurement to construction support.'],
    ['topic' => 'Project experience', 'keywords' => 'project, experience, carport, floating, solar park, ev', 'answer' => 'Our project experience covers solar parks, floating solar, solar carports, EV charging, battery storage and site security systems.'],
    ['topic' => 'Greeting', 'keywords' => 'hello, hi, hey', 'answer' => 'Hello. I can help with VARTEC services, projects, operations and maintenance, battery storage, or contacting our team.'],
];
const CHAT_FALLBACK = 'I can provide general information about VARTEC services and projects. For a detailed answer, please contact our team.';
const SOCIAL = ['linkedin' => 'LinkedIn', 'facebook' => 'Facebook', 'instagram' => 'Instagram', 'youtube' => 'YouTube'];

/** Fills in anything added to the site after this content was first saved, so older saved content keeps working. */
function content_defaults(array $content): array
{
    $s = $content['settings'] ?? [];
    $s['wording'] = is_array($s['wording'] ?? null) ? $s['wording'] : [];
    $s['chat_answers'] = is_array($s['chat_answers'] ?? null) ? $s['chat_answers'] : CHAT_ANSWERS;
    $s['chat_fallback'] = (string) ($s['chat_fallback'] ?? CHAT_FALLBACK);
    $s['google_verification'] = (string) ($s['google_verification'] ?? '');
    $s['social'] = array_intersect_key((is_array($s['social'] ?? null) ? $s['social'] : []) + array_fill_keys(array_keys(SOCIAL), ''), SOCIAL);
    $content['settings'] = $s;
    foreach ($content['pages'] ?? [] as $n => $page) {
        $content['pages'][$n]['banner_image'] = (string) ($page['banner_image'] ?? '');
    }
    return $content;
}

/** One piece of editable wording, falling back to the standard text. */
function wording(array $content, string $key): string
{
    $text = trim((string) ($content['settings']['wording'][$key] ?? ''));
    return $text !== '' ? $text : (WORDING[$key][2] ?? '');
}

/** The published website. Created from the seed the first time the site runs. */
function live_content(): array
{
    $live = read_data('live');
    if (!$live) {
        $live = seed_content();
        write_data('live', $live);
    }
    return content_defaults($live);
}

/** The working copy editors change. Starts as a copy of the published site. */
function draft_content(): array
{
    $draft = read_data('draft');
    return $draft ? content_defaults($draft) : live_content();
}

function save_draft(array $content): void
{
    write_data('draft', $content);
}

function has_unpublished_changes(): bool
{
    $draft = read_data('draft');
    return $draft && content_defaults($draft) != live_content();
}

function publish_draft(string $user): void
{
    $live = live_content();
    $stamp = gmdate('Ymd-His');
    write_data('history/' . $stamp, ['saved_at' => gmdate('c'), 'replaced_by' => $user, 'content' => $live]);
    write_data('live', draft_content());
    $versions = glob(data_dir() . '/history/*.php') ?: [];
    sort($versions);
    foreach (array_slice($versions, 0, max(0, count($versions) - HISTORY_KEEP)) as $old) {
        @unlink($old);
    }
}

function history_versions(): array
{
    $out = [];
    foreach (glob(data_dir() . '/history/*.php') ?: [] as $file) {
        $id = basename($file, '.php');
        $data = read_data('history/' . $id);
        $out[] = ['id' => $id, 'saved_at' => $data['saved_at'] ?? '', 'replaced_by' => $data['replaced_by'] ?? ''];
    }
    return array_reverse($out);
}

function find_page(array $content, string $kind, string $slug): ?array
{
    foreach ($content['pages'] as $page) {
        if ($page['kind'] === $kind && $page['slug'] === $slug) {
            return $page;
        }
    }
    return null;
}

function page_path(array $page): string
{
    return (PAGE_KINDS[$page['kind']][2] ?? '/') . $page['slug'] . '/';
}

function media_item(array $content, ?string $id): ?array
{
    return ($id && isset($content['media'][$id])) ? $content['media'][$id] : null;
}

function media_url(array $content, ?string $id): string
{
    $item = media_item($content, $id);
    return $item ? '/media/' . str_replace('%2F', '/', rawurlencode($item['file'])) : '';
}

function slugify(string $text): string
{
    $plain = function_exists('iconv') ? (@iconv('UTF-8', 'ASCII//TRANSLIT//IGNORE', $text) ?: $text) : $text;
    $text = strtolower(trim(preg_replace('/[^A-Za-z0-9]+/', '-', $plain) ?? '', '-'));
    return $text !== '' ? $text : 'item';
}

const LICENCES = [
    'own' => 'Our own photo',
    'licensed' => 'Licensed (we hold proof)',
    'unlicensed' => 'No licence',
    'unknown' => 'Not sure',
];

/** Media that should not be on a public page until someone confirms the right to use it. */
function media_needs_check(array $item): bool
{
    return in_array($item['licence'] ?? 'unknown', ['unlicensed', 'unknown'], true);
}

/** Where each media item is used: id => list of human-readable places. */
function media_usage(array $content): array
{
    $use = [];
    $add = function (?string $id, string $where) use (&$use) {
        if ($id) {
            $use[$id][] = $where;
        }
    };
    $add($content['settings']['logo'] ?? '', 'Logo');
    foreach ($content['home']['hero']['slides'] ?? [] as $id) {
        $add($id, 'Home page banner');
    }
    $add($content['home']['about']['video'] ?? '', 'Home page video');
    $add($content['home']['about']['poster'] ?? '', 'Home page video cover');
    foreach ($content['pages'] as $page) {
        $add($page['card_image'] ?? '', $page['title'] . ' (card)');
        $add($page['banner_image'] ?? '', $page['title'] . ' (banner)');
        foreach ($page['sections'] as $section) {
            $add($section['image'] ?? '', $page['title'] . ': ' . ($section['heading'] ?: 'section'));
        }
    }
    return $use;
}

// ---------------------------------------------------------------- request helpers

function is_https(): bool
{
    return (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') || strtolower($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '') === 'https';
}

function request_host(): string
{
    return strtolower(preg_replace('/:\d+$/', '', $_SERVER['HTTP_HOST'] ?? 'localhost') ?? 'localhost');
}

function redirect(string $to, int $status = 302): never
{
    header('Location: ' . $to, true, $status);
    exit;
}

function client_key(): string
{
    return hash('sha256', ($_SERVER['REMOTE_ADDR'] ?? '') . '|vartec');
}

/** Simple counter-based limit, e.g. sign-in attempts. Returns true while under the limit. */
function rate_limit_ok(string $bucket, int $max, int $windowSeconds, bool $count = true, ?string $subject = null): bool
{
    $all = read_data('limits');
    $key = $bucket . ':' . ($subject !== null ? hash('sha256', $subject) : client_key());
    $now = time();
    $all = array_filter($all, fn ($entry) => ($entry['until'] ?? 0) > $now);
    $entry = $all[$key] ?? ['count' => 0, 'until' => $now + $windowSeconds];
    if ($count) {
        $entry['count']++;
        $all[$key] = $entry;
        write_data('limits', $all);
    }
    return $entry['count'] <= $max;
}

function rate_limit_clear(string $bucket, ?string $subject = null): void
{
    $all = read_data('limits');
    unset($all[$bucket . ':' . ($subject !== null ? hash('sha256', $subject) : client_key())]);
    write_data('limits', $all);
}

// ---------------------------------------------------------------- sessions and users

function start_session(): void
{
    if (session_status() === PHP_SESSION_ACTIVE) {
        return;
    }
    session_name('vartec_admin');
    session_set_cookie_params(['lifetime' => 0, 'path' => '/', 'secure' => is_https(), 'httponly' => true, 'samesite' => 'Lax']);
    session_start();
    $idle = isset($_SESSION['seen']) && time() - $_SESSION['seen'] > SESSION_IDLE_SECONDS;
    $tooOld = isset($_SESSION['started']) && time() - $_SESSION['started'] > SESSION_MAX_SECONDS;
    if ($idle || $tooOld) {
        $_SESSION = [];
        session_regenerate_id(true);
    }
    $_SESSION['seen'] = time();
    $_SESSION['started'] ??= time();
}

function current_user(): ?string
{
    if (!isset($_COOKIE['vartec_admin']) && session_status() !== PHP_SESSION_ACTIVE) {
        return null; // no session cookie: do not start one for ordinary visitors
    }
    start_session();
    $user = $_SESSION['user'] ?? null;
    $record = $user ? (users()[$user] ?? null) : null;
    // A password change raises the account's "epoch", which signs out every other browser.
    return ($record && ($_SESSION['epoch'] ?? 0) === ($record['epoch'] ?? 0)) ? $user : null;
}

function sign_in(string $user): void
{
    start_session();
    session_regenerate_id(true); // a fresh session id on sign-in defeats session fixation
    $_SESSION = ['user' => $user, 'epoch' => users()[$user]['epoch'] ?? 0, 'seen' => time(), 'started' => time()];
}

/** Returns a reason the password is too weak, or null when it is acceptable. */
function password_problem(string $password, string $username): ?string
{
    if (strlen($password) < 10) {
        return 'Choose a password of at least 10 characters.';
    }
    if (stripos($password, $username) !== false || count(array_unique(str_split(strtolower($password)))) < 5
        || in_array(strtolower($password), ['password123', 'qwertyuiop', '1234567890', 'vartec1234', 'solar12345', 'letmein1234'], true)) {
        return 'That password is too easy to guess. Use a longer phrase that does not include your username.';
    }
    return null;
}

/** Security record: who signed in, published or changed accounts, and when. */
function audit(string $event, string $user = ''): void
{
    $log = read_data('audit');
    array_unshift($log, ['at' => gmdate('c'), 'user' => $user, 'event' => $event, 'ip' => $_SERVER['REMOTE_ADDR'] ?? '']);
    write_data('audit', array_slice($log, 0, 300));
}

// ---- two-step sign-in: standard time-based codes (RFC 6238), as used by authenticator apps

function base32_encode_bytes(string $bytes): string
{
    $alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
    $bits = '';
    foreach (str_split($bytes) as $char) {
        $bits .= str_pad(decbin(ord($char)), 8, '0', STR_PAD_LEFT);
    }
    $out = '';
    foreach (str_split($bits, 5) as $chunk) {
        $out .= $alphabet[bindec(str_pad($chunk, 5, '0'))];
    }
    return $out;
}

function base32_decode_bytes(string $text): string
{
    $alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
    $bits = '';
    foreach (str_split(strtoupper(preg_replace('/[^A-Za-z2-7]/', '', $text) ?? '')) as $char) {
        $bits .= str_pad(decbin((int) strpos($alphabet, $char)), 5, '0', STR_PAD_LEFT);
    }
    $out = '';
    foreach (str_split($bits, 8) as $chunk) {
        if (strlen($chunk) === 8) {
            $out .= chr(bindec($chunk));
        }
    }
    return $out;
}

function totp_code(string $secret, int $counter): string
{
    $hash = hash_hmac('sha1', pack('J', $counter), base32_decode_bytes($secret), true);
    $offset = ord($hash[19]) & 0x0F;
    $number = (unpack('N', substr($hash, $offset, 4))[1] & 0x7FFFFFFF) % 1000000;
    return str_pad((string) $number, 6, '0', STR_PAD_LEFT);
}

/** Accepts the current code or its neighbours (clock drift). Returns the counter used, or null. */
function totp_verify(string $secret, string $code, int $lastUsed = 0): ?int
{
    $code = preg_replace('/\D/', '', $code) ?? '';
    $now = intdiv(time(), 30);
    foreach ([$now, $now - 1, $now + 1] as $counter) {
        if ($counter > $lastUsed && strlen($code) === 6 && hash_equals(totp_code($secret, $counter), $code)) {
            return $counter; // each code works once
        }
    }
    return null;
}

function users(): array
{
    return read_data('users');
}

function csrf_token(): string
{
    start_session();
    return $_SESSION['csrf'] ??= bin2hex(random_bytes(32));
}

function csrf_field(): string
{
    return '<input type="hidden" name="_csrf" value="' . e(csrf_token()) . '">';
}

function csrf_check(): void
{
    start_session();
    $sent = $_POST['_csrf'] ?? ($_SERVER['HTTP_X_CSRF_TOKEN'] ?? '');
    if (!is_string($sent) || !hash_equals($_SESSION['csrf'] ?? '', $sent)) {
        http_response_code(400);
        exit('This form has expired. Go back, reload the page and try again.');
    }
}

function flash(?string $message = null, string $type = 'ok'): ?array
{
    start_session();
    if ($message !== null) {
        $_SESSION['flash'] = ['message' => $message, 'type' => $type];
        return null;
    }
    $flash = $_SESSION['flash'] ?? null;
    unset($_SESSION['flash']);
    return $flash;
}

/** One-time code that proves whoever creates the first account controls the hosting. */
function setup_code(): string
{
    $data = read_data('setup-code');
    if (empty($data['code'])) {
        $data = ['code' => strtoupper(bin2hex(random_bytes(4))), 'note' => 'Enter this code on /admin/ to create the first account.'];
        write_data('setup-code', $data);
    }
    return $data['code'];
}

function render(string $template, array $vars = []): string
{
    extract($vars, EXTR_SKIP);
    ob_start();
    require APP_DIR . '/templates/' . $template . '.php';
    return (string) ob_get_clean();
}
