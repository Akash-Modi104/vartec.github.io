<?php
/** @var array $content */
$menu = [
    ['dashboard', '/admin/', 'Dashboard'], ['home', '/admin/home', 'Home page'], ['service', '/admin/pages?kind=service', 'Services'],
    ['project', '/admin/pages?kind=project', 'Projects'], ['info', '/admin/pages?kind=info', 'Other pages'],
    ['media', '/admin/media', 'Images and video'], ['wording', '/admin/wording', 'Wording'],
    ['enquiries', '/admin/enquiries', 'Enquiries'], ['settings', '/admin/settings', 'Settings'], ['help', '/admin/help', 'Help'],
];
$usage = media_usage($content);
?><!doctype html>
<html lang="en-GB">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow">
  <title><?= e($title) ?> | VARTEC admin</title>
  <link rel="icon" href="/favicon.ico">
  <link rel="stylesheet" href="/assets/admin.css?v=<?= APP_VERSION ?>">
</head>
<body>
<div class="frame">
  <aside class="sidebar" id="sidebar">
    <a class="brand" href="/admin/"><span class="brand-mark">V</span><span><strong>VARTEC</strong><small>Website admin</small></span></a>
    <nav aria-label="Admin">
      <?php foreach ($menu as [$key, $href, $label]): ?>
      <a href="<?= e($href) ?>"<?= $active === $key ? ' class="active" aria-current="page"' : '' ?>><?= icon($key) ?><span><?= e($label) ?></span><?php if ($key === 'enquiries' && $new_enquiries): ?><b class="pill"><?= (int) $new_enquiries ?></b><?php endif; ?></a>
      <?php endforeach; ?>
    </nav>
    <div class="sidebar-foot">
      <a href="/" target="_blank" rel="noopener"><?= icon('eye') ?><span>View live website</span></a>
      <form method="post" action="/admin/logout"><?= csrf_field() ?><button type="submit" class="linklike"><?= icon('out') ?><span>Sign out (<?= e($user) ?>)</span></button></form>
    </div>
  </aside>
  <div class="main">
    <header class="topbar">
      <button type="button" class="menu-button" data-menu aria-controls="sidebar" aria-expanded="false">Menu</button>
      <?php if ($changes): ?>
        <span class="state state-draft"><i></i> You have changes that are not live yet</span>
        <a class="btn btn-small" href="/?preview=1" target="_blank" rel="noopener">Preview</a>
        <form method="post" action="/admin/publish"><?= csrf_field() ?><button type="submit" class="btn btn-small btn-primary">Publish to website</button></form>
      <?php else: ?>
        <span class="state state-live"><i></i> Everything is published</span>
      <?php endif; ?>
    </header>
    <main class="content">
      <?php if ($flash): ?><div class="notice notice-<?= e($flash['type']) ?>" role="status"><?= e($flash['message']) ?></div><?php endif; ?>
      <?= $body ?>
    </main>
  </div>
</div>

<dialog class="media-dialog" id="media-dialog" aria-label="Choose from the library">
  <div class="dialog-head"><h2 data-dialog-title>Choose an image</h2><button type="button" class="btn btn-small btn-quiet" data-dialog-close>Close</button></div>
  <form class="dialog-upload" data-dialog-upload>
    <strong>Upload a new one</strong>
    <input type="file" name="file" accept="image/jpeg,image/png,image/webp,image/gif,video/mp4" required>
    <input type="text" name="alt" placeholder="Describe what it shows" maxlength="200" required>
    <input type="text" name="source" placeholder="Where is it from? (e.g. our site team, Shutterstock)" maxlength="300">
    <select name="licence" aria-label="Licence"><?php foreach (LICENCES as $key => $label): ?><option value="<?= e($key) ?>"<?= $key === 'unknown' ? ' selected' : '' ?>><?= e($label) ?></option><?php endforeach; ?></select>
    <button type="submit" class="btn btn-small btn-primary">Upload and choose</button>
    <span class="dialog-error" data-dialog-error role="alert"></span>
  </form>
  <div class="dialog-grid" data-dialog-grid>
    <?php foreach ($content['media'] as $id => $item): ?>
    <button type="button" class="tile" data-tile data-id="<?= e((string) $id) ?>" data-kind="<?= e($item['kind'] ?? 'image') ?>" data-url="<?= e(media_url($content, (string) $id)) ?>" data-alt="<?= e($item['alt'] ?? '') ?>" data-check="<?= media_needs_check($item) ? '1' : '0' ?>">
      <?php if (($item['kind'] ?? 'image') === 'image'): ?><img loading="lazy" src="<?= e(media_url($content, (string) $id)) ?>" alt=""><?php else: ?><span class="tile-video">VIDEO</span><?php endif; ?>
      <span class="tile-name"><?= e($item['alt'] ?: $item['file']) ?></span><?= licence_badge($item) ?>
    </button>
    <?php endforeach; ?>
  </div>
</dialog>
<meta name="csrf" content="<?= e(csrf_token()) ?>">
<script src="/assets/admin.js?v=<?= APP_VERSION ?>" defer></script>
</body>
</html>
