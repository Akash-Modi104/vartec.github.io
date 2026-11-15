<?php
/**
 * One-off: puts the harbour floating-solar photo back into a site that was set up before it was restored.
 * Adds it to the library (as licensed), to the Floating Solar page's second section if that has no picture,
 * and to the home page banner. Safe to run twice. Run as the web server's user:
 *
 *     sudo -u www-data php tools/add_harbour_photo.php
 */
declare(strict_types=1);
if (PHP_SAPI !== 'cli') {
    exit(1);
}
require __DIR__ . '/../public/app/bootstrap.php';
$seed = seed_content();
$id = 'floating-solar-harbour';
foreach (['live', 'draft'] as $name) {
    $content = read_data($name);
    if (!$content) {
        continue;
    }
    $content['media'][$id] ??= $seed['media'][$id];
    foreach ($content['pages'] as $n => $page) {
        if ($page['kind'] === 'project' && $page['slug'] === 'floating-solar' && isset($page['sections'][1]) && ($page['sections'][1]['image'] ?? '') === '') {
            $content['pages'][$n]['sections'][1]['image'] = $id;
        }
    }
    if (!in_array($id, $content['home']['hero']['slides'], true)) {
        $content['home']['hero']['slides'][] = $id;
    }
    write_data($name, $content);
    echo "updated $name\n";
}
