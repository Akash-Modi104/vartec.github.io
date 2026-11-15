<?php
/** @var array $content */
$s = $content['settings'];
$services = visible_pages($content, 'service');
$projects = visible_pages($content, 'project');
$logo = media_url($content, $s['logo'] ?? '');
$q = $preview ? '?preview=1' : '';
$active = $active ?? '';       // 'home', or the address of the page being shown
$phoneHref = 'tel:' . preg_replace('/[^0-9+]/', '', $s['phone']);
?><!doctype html>
<html lang="en-GB">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title><?= e($seo_title) ?></title>
  <meta name="description" content="<?= e($seo_description) ?>">
  <meta name="robots" content="<?= $indexable ? 'index,follow,max-image-preview:large' : 'noindex,nofollow' ?>">
  <?php if ($canonical): ?><link rel="canonical" href="<?= e($canonical) ?>"><?php endif; ?>
  <meta property="og:type" content="website">
  <meta property="og:locale" content="en_GB">
  <meta name="twitter:card" content="summary_large_image">
  <?php if ($social_image && media_url($content, $social_image)): ?><meta property="og:image" content="<?= e($site . media_url($content, $social_image)) ?>"><meta name="twitter:image" content="<?= e($site . media_url($content, $social_image)) ?>"><?php endif; ?>
  <meta property="og:title" content="<?= e($seo_title) ?>">
  <meta name="twitter:title" content="<?= e($seo_title) ?>">
  <meta name="twitter:description" content="<?= e($seo_description) ?>">
  <meta property="og:description" content="<?= e($seo_description) ?>">
  <meta property="og:site_name" content="<?= e($s['brand_name']) ?>">
  <?php if ($canonical): ?><meta property="og:url" content="<?= e($canonical) ?>"><?php endif; ?>
  <?php if ($preload_image && media_url($content, $preload_image)): ?><link rel="preload" as="image" href="<?= e(media_url($content, $preload_image)) ?>" fetchpriority="high"><?php endif; ?>
  <?php if ($logo): ?><link rel="icon" href="<?= e($logo) ?>"><?php endif; ?>
  <?php if ($logo): ?><link rel="apple-touch-icon" href="<?= e($logo) ?>"><?php endif; ?>
  <meta name="theme-color" content="#E19F26">
  <link rel="stylesheet" href="/assets/site.css?v=<?= APP_VERSION ?>">
  <?php
  $org = array_filter(['@type' => 'Organization', '@id' => $site . '/#organization', 'name' => $s['brand_name'], 'url' => $site . '/',
      'logo' => $logo ? $site . $logo : null, 'email' => $s['contact_email'], 'telephone' => $s['phone'], 'areaServed' => 'GB',
      'description' => $s['seo_description'] ?? null,
      'contactPoint' => ['@type' => 'ContactPoint', 'contactType' => 'customer service', 'telephone' => $s['phone'], 'email' => $s['contact_email'], 'areaServed' => 'GB', 'availableLanguage' => 'en']]);
  $graph = array_merge([$org], $schema ?? []);
  ?>
  <script type="application/ld+json"><?= json_encode(['@context' => 'https://schema.org', '@graph' => $graph], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_HEX_TAG) ?></script>
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to content</a>
  <header class="site-header" data-header>
    <div class="shell header-inner">
      <a class="brand" href="/<?= $q ?>" aria-label="<?= e($s['brand_name']) ?> home">
        <?php if ($logo): ?><img src="<?= e($logo) ?>" width="60" height="60" alt="<?= e($s['brand_name']) ?>"><?php endif; ?>
      </a>
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="primary-navigation"><span></span><span></span><span></span><span class="sr-only">Menu</span></button>
      <nav id="primary-navigation" class="primary-nav" aria-label="Primary navigation">
        <a href="/<?= $q ?>"<?= $active === 'home' ? ' aria-current="page"' : '' ?>>Home</a>
        <a href="/<?= $q ?>#about">About Us</a>
        <?php if ($services): ?>
        <div class="nav-group<?= str_starts_with($active, '/services/') ? ' current' : '' ?>">
          <button type="button" aria-expanded="false" aria-haspopup="true">Services <span aria-hidden="true">▾</span></button>
          <div class="nav-dropdown">
            <?php foreach ($services as $item): ?><a href="<?= e(page_path($item) . $q) ?>"<?= $active === page_path($item) ? ' aria-current="page"' : '' ?>><?= e($item['title']) ?></a><?php endforeach; ?>
          </div>
        </div>
        <?php endif; ?>
        <?php if ($projects): ?>
        <div class="nav-group<?= str_starts_with($active, '/projects/') ? ' current' : '' ?>">
          <button type="button" aria-expanded="false" aria-haspopup="true">Projects <span aria-hidden="true">▾</span></button>
          <div class="nav-dropdown">
            <?php foreach ($projects as $item): ?><a href="<?= e(page_path($item) . $q) ?>"<?= $active === page_path($item) ? ' aria-current="page"' : '' ?>><?= e($item['title']) ?></a><?php endforeach; ?>
          </div>
        </div>
        <?php endif; ?>
        <a class="nav-cta" href="#contact">Contact Us</a>
      </nav>
    </div>
  </header>

  <div class="messages shell" role="status" data-contact-status hidden><p></p></div>
  <main id="main-content"><?= $body ?></main>

  <footer class="site-footer">
    <div class="shell footer-grid">
      <div><?php if ($logo): ?><img class="footer-logo" src="<?= e($logo) ?>" width="84" height="84" alt="<?= e($s['brand_name']) ?>" loading="lazy"><?php endif; ?><p><?= e($s['footer_about']) ?></p></div>
      <?php if ($services): ?><nav aria-label="Services"><h2>Services</h2><?php foreach ($services as $item): ?><a href="<?= e(page_path($item) . $q) ?>"><?= e($item['title']) ?></a><?php endforeach; ?></nav><?php endif; ?>
      <?php if ($projects): ?><nav aria-label="Projects"><h2>Projects</h2><?php foreach ($projects as $item): ?><a href="<?= e(page_path($item) . $q) ?>"><?= e($item['title']) ?></a><?php endforeach; ?></nav><?php endif; ?>
      <div><h2>Contact Us</h2><a href="<?= e($phoneHref) ?>"><?= e($s['phone']) ?></a><a href="mailto:<?= e($s['contact_email']) ?>"><?= e($s['contact_email']) ?></a><small><?= e($s['office_hours_weekdays']) ?><br><?= e($s['office_hours_weekend']) ?></small></div>
    </div>
    <div class="footer-bottom-bar"><div class="shell footer-bottom"><span><?= e(str_replace('{year}', date('Y'), $s['footer_copyright'])) ?></span><a href="#main-content">Back to top ↑</a></div></div>
  </footer>

  <?php if (!empty($s['chat_enabled'])): ?>
  <aside class="chatbot" data-chatbot>
    <section class="chatbot-panel" id="vartec-chat" aria-label="<?= e($s['chat_title']) ?>" aria-hidden="true" inert>
      <header><span class="chatbot-mark">V</span><div><strong><?= e($s['chat_title']) ?></strong><small><i></i> Online help</small></div><button type="button" data-chat-close aria-label="Close chat">×</button></header>
      <div class="chatbot-messages" data-chat-messages aria-live="polite">
        <p class="chatbot-message bot"><?= e($s['chat_welcome']) ?></p>
      </div>
      <div class="chatbot-prompts" aria-label="Suggested questions">
        <button type="button" data-chat-question="What solar services do you provide?">Solar services</button>
        <button type="button" data-chat-question="Tell me about operations and maintenance.">O&amp;M support</button>
        <button type="button" data-chat-question="How can I request a quote?">Request a quote</button>
      </div>
      <form class="chatbot-form" data-chat-form>
        <label class="sr-only" for="chatbot-input">Ask VARTEC a question</label>
        <input id="chatbot-input" data-chat-input type="text" maxlength="240" autocomplete="off" placeholder="Ask about our services…">
        <button type="submit" aria-label="Send question">→</button>
      </form>
      <p class="chatbot-note">Quick guidance only. No personal data is stored.</p>
    </section>
    <button class="chatbot-launcher" type="button" data-chat-open aria-controls="vartec-chat" aria-expanded="false"><span>V</span><strong>How can we help?</strong></button>
  </aside>
  <?php endif; ?>
  <?php if ($preview): ?><div class="preview-bar">Preview of unpublished changes. Visitors cannot see this. <a href="/admin/">Back to the admin</a></div><?php endif; ?>
  <script src="/assets/site.js?v=<?= APP_VERSION ?>" defer></script>
  <script src="/assets/contact.js?v=<?= APP_VERSION ?>" defer></script>
</body>
</html>
