<?php
declare(strict_types=1);

/** Public website: routing and page rendering. */

/** Addresses used by the previous Angular site -> where that content lives now. */
const LEGACY_REDIRECTS = [
    '/project/battery-storage' => '/projects/battery-storage/', '/project/batterystorage' => '/projects/battery-storage/',
    '/project/carports' => '/projects/carports/', '/project/carpots' => '/projects/carports/',
    '/project/ev-charging' => '/projects/ev-charging/', '/project/evcharging' => '/projects/ev-charging/',
    '/project/floating' => '/projects/floating-solar/', '/project/floating-solar' => '/projects/floating-solar/',
    '/project/security' => '/projects/security-systems/', '/project/security-systems' => '/projects/security-systems/',
    '/project/solar-parks' => '/projects/solar-parks/', '/project/solarparks' => '/projects/solar-parks/',
    '/services/operationmaintenance' => '/services/operation-maintenance/',
    '/home' => '/', '/home/about_us' => '/#about',
];

function public_dispatch(string $path): void
{
    header('X-Content-Type-Options: nosniff');
    header('Referrer-Policy: strict-origin-when-cross-origin');
    header('X-Frame-Options: DENY');

    if ($path === '/enquiry') {
        public_enquiry();
        return;
    }

    $preview = isset($_GET['preview']) && current_user() !== null;
    $content = $preview ? draft_content() : live_content();
    $site = rtrim($content['settings']['site_url'] ?? '', '/');
    $siteHost = strtolower((string) parse_url($site, PHP_URL_HOST));

    // One address for search engines: www.<site> -> <site>.
    if ($siteHost && request_host() === 'www.' . $siteHost) {
        redirect($site . ($_SERVER['REQUEST_URI'] ?? '/'), 301);
    }
    $legacy = LEGACY_REDIRECTS[strtolower(rtrim($path, '/'))] ?? null;
    if ($legacy) {
        redirect($legacy, 301);
    }

    // Only the real public address may be indexed; previews and test addresses never are.
    $indexable = !$preview && $siteHost !== '' && request_host() === $siteHost;
    $base = ['content' => $content, 'preview' => $preview, 'indexable' => $indexable, 'site' => $site ?: ((is_https() ? 'https://' : 'http://') . request_host())];

    if ($path === '/favicon.ico') {
        $logo = media_url($content, $content['settings']['logo'] ?? '');
        $logo ? redirect($logo, 302) : http_response_code(404);
        return;
    }
    if ($path === '/robots.txt') {
        header('Content-Type: text/plain; charset=utf-8');
        echo $indexable ? "User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: {$base['site']}/sitemap.xml\n" : "User-agent: *\nDisallow: /\n";
        return;
    }
    if ($path === '/sitemap.xml') {
        header('Content-Type: application/xml; charset=utf-8');
        echo '<?xml version="1.0" encoding="UTF-8"?>' . "\n" . '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' . "\n";
        echo '  <url><loc>' . e($base['site'] . '/') . "</loc></url>\n";
        foreach ($content['pages'] as $page) {
            if (!empty($page['visible'])) {
                echo '  <url><loc>' . e($base['site'] . page_path($page)) . "</loc></url>\n";
            }
        }
        echo "</urlset>\n";
        return;
    }
    $org = ['@id' => $base['site'] . '/#organization'];
    if ($path === '/') {
        echo render('public/layout', $base + [
            'seo_title' => $content['settings']['seo_title'], 'seo_description' => meta_description($content['settings']['seo_description']),
            'canonical' => $base['site'] . '/', 'social_image' => $content['home']['hero']['slides'][0] ?? '', 'return_path' => '/',
            'preload_image' => $content['home']['hero']['slides'][0] ?? '', 'active' => 'home',
            'schema' => [['@type' => 'WebSite', '@id' => $base['site'] . '/#website', 'url' => $base['site'] . '/', 'name' => $content['settings']['brand_name'], 'inLanguage' => 'en-GB', 'publisher' => $org]],
            'body' => render('public/home', $base),
        ]);
        return;
    }
    $page = null;
    if (preg_match('#^/(services|projects)/([a-z0-9-]+)(/?)$#', $path, $m)) {
        $page = find_page($content, $m[1] === 'services' ? 'service' : 'project', $m[2]);
        $slash = $m[3];
    } elseif (preg_match('#^/([a-z0-9-]+)(/?)$#', $path, $m)) {
        $page = find_page($content, 'info', $m[1]);      // privacy policy and similar
        $slash = $m[2];
    }
    if ($page && (!empty($page['visible']) || $preview)) {
        if ($slash === '') {
            redirect(page_path($page), 301);
        }
        $kind = $page['kind'];
        $url = $base['site'] . page_path($page);
        $description = meta_description($page['seo_description'] ?: $page['intro']);
        $image = media_url($content, $page['card_image'] ?? '') ?: media_url($content, page_banner($content, $page));
        $crumbs = [['@type' => 'ListItem', 'position' => 1, 'name' => wording($content, 'menu_home'), 'item' => $base['site'] . '/']];
        if ($kind !== 'info') {
            $crumbs[] = ['@type' => 'ListItem', 'position' => 2, 'name' => PAGE_KINDS[$kind][0], 'item' => $base['site'] . '/#' . ($kind === 'service' ? 'services' : 'projects')];
        }
        $crumbs[] = ['@type' => 'ListItem', 'position' => count($crumbs) + 1, 'name' => $page['title'], 'item' => $url];
        $isService = $kind === 'service';
        $schema = [
            ['@type' => 'BreadcrumbList', 'itemListElement' => $crumbs],
            array_filter(['@type' => $isService ? 'Service' : 'WebPage', '@id' => $url . '#page', 'url' => $url, 'name' => $page['title'],
                'description' => $description, 'image' => $image ? $base['site'] . $image : null,
                $isService ? 'provider' : 'publisher' => $org, 'areaServed' => $isService ? 'GB' : null,
                'serviceType' => $isService ? $page['title'] : null, 'inLanguage' => $isService ? null : 'en-GB']),
        ];
        $brand = $content['settings']['brand_name'];
        echo render('public/layout', $base + [
            'seo_title' => $page['seo_title'] ?: ($kind === 'info' ? $page['title'] . ' | ' . $brand : page_title($page['title'], $isService ? 'Solar services' : 'Solar projects', $brand)),
            'seo_description' => $description,
            'canonical' => $url, 'social_image' => ($page['card_image'] ?? '') ?: page_banner($content, $page), 'return_path' => page_path($page),
            'preload_image' => page_banner($content, $page), 'active' => page_path($page), 'schema' => $schema,
            'body' => render('public/page', $base + ['page' => $page]),
        ]);
        return;
    }
    http_response_code(404);
    echo render('public/layout', [
        'indexable' => false, 'seo_title' => 'Page not found | ' . $content['settings']['brand_name'], 'seo_description' => '',
        'canonical' => '', 'social_image' => '', 'return_path' => '/', 'preload_image' => '', 'body' => render('public/404', $base),
    ] + $base);
}

/**
 * Keeps a copy of a website enquiry so it shows in the admin inbox.
 * The email itself is still sent by the existing send_mail.php; this never sends mail.
 */
function public_enquiry(): void
{
    header('Content-Type: application/json; charset=utf-8');
    if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
        http_response_code(405);
        echo '{"ok":false}';
        return;
    }
    $field = fn (string $name, int $max) => mb_substr(trim(preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/u', '', (string) ($_POST[$name] ?? '')) ?? ''), 0, $max);
    $entry = [
        'first_name' => $field('firstName', 100), 'last_name' => $field('lastName', 100), 'email' => $field('email', 254),
        'phone' => $field('phone', 60), 'message' => $field('message', 5000),
    ];
    $spam = !empty($_POST['website']); // hidden field real visitors never fill in
    if ($spam || $entry['first_name'] === '' || $entry['message'] === '' || !filter_var($entry['email'], FILTER_VALIDATE_EMAIL)) {
        http_response_code($spam ? 200 : 422);
        echo '{"ok":false}';
        return;
    }
    if (!rate_limit_ok('enquiry', 5, 600)) {
        http_response_code(429);
        echo '{"ok":false}';
        return;
    }
    $all = read_data('enquiries');
    array_unshift($all, $entry + ['id' => bin2hex(random_bytes(6)), 'received_at' => gmdate('c'), 'status' => 'new',
        'email_sent' => ($_POST['mailResult'] ?? '') === 'Success', 'page' => $field('page', 200)]);
    write_data('enquiries', array_slice($all, 0, 2000));
    echo '{"ok":true}';
}

/** Browser/search title: "Page | Group | Brand", dropping the group when that would be cut off in search results. */
function page_title(string $title, string $group, string $brand): string
{
    $full = $title . ' | ' . $group . ' | ' . $brand;
    return mb_strlen($full) <= 60 ? $full : $title . ' | ' . $brand;
}

/** Search-result summary: one line, cut at a word, no longer than search engines show. */
function meta_description(string $text, int $max = 158): string
{
    $text = trim(preg_replace('/\s+/u', ' ', $text) ?? '');
    if (mb_strlen($text) <= $max) {
        return $text;
    }
    $cut = mb_substr($text, 0, $max - 1);
    $space = strrpos($cut, ' ');
    return rtrim($space ? substr($cut, 0, $space) : $cut, " ,;:.-") . '…';
}

/** <img> with its real size, so the page does not jump while loading. */
function img_tag(array $content, ?string $id, string $alt, bool $lazy = true): string
{
    $item = media_item($content, $id);
    if (!$item || ($item['kind'] ?? 'image') !== 'image') {
        return '';
    }
    $size = isset($item['w'], $item['h']) ? ' width="' . (int) $item['w'] . '" height="' . (int) $item['h'] . '"' : '';
    return '<img' . ($lazy ? ' loading="lazy" decoding="async"' : '') . ' src="' . e(media_url($content, $id)) . '"' . $size . ' alt="' . e($item['alt'] ?: $alt) . '">';
}

/** The photo behind an inner page's title: the one chosen for it, else the first section photo, else the card picture. */
function page_banner(array $content, array $page): string
{
    $own = media_item($content, $page['banner_image'] ?? '');
    if ($own && ($own['kind'] ?? 'image') === 'image') {
        return $page['banner_image'];
    }
    foreach ($page['sections'] ?? [] as $section) {
        $item = media_item($content, $section['image'] ?? '');
        if ($item && ($item['kind'] ?? 'image') === 'image') {
            return $section['image'];
        }
    }
    return media_item($content, $page['card_image'] ?? '') ? $page['card_image'] : '';
}

function visible_pages(array $content, string $kind): array
{
    return array_values(array_filter($content['pages'], fn ($p) => $p['kind'] === $kind && !empty($p['visible'])));
}

function truncate_words(string $text, int $words): string
{
    $parts = preg_split('/\s+/', trim($text)) ?: [];
    return count($parts) > $words ? implode(' ', array_slice($parts, 0, $words)) . ' …' : $text;
}
