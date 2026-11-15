<?php
/** @var array $content @var array $page */
$isService = $page['kind'] === 'service';
$q = $preview ? '?preview=1' : '';
$group = $isService ? 'Services' : 'Projects';
$bannerId = page_banner($content, $page);
$banner = media_item($content, $bannerId);
$others = array_slice(array_values(array_filter(visible_pages($content, $page['kind']), fn ($p) => $p['id'] !== $page['id'])), 0, 3);
?>
<section class="page-hero<?= $banner ? '' : ' plain' ?>">
  <?php if ($banner): ?><img src="<?= e(media_url($content, $bannerId)) ?>" alt=""<?= isset($banner['w'], $banner['h']) ? ' width="' . (int) $banner['w'] . '" height="' . (int) $banner['h'] . '"' : '' ?> fetchpriority="high" decoding="async"><?php endif; ?>
  <div class="shell">
    <nav aria-label="Breadcrumb"><ol class="breadcrumb"><li><a href="/<?= $q ?>">Home</a></li><li><a href="/<?= $q ?>#<?= strtolower($group) ?>"><?= $group ?></a></li><li aria-current="page"><?= e($page['title']) ?></li></ol></nav>
    <h1><?= e($page['title']) ?></h1>
  </div>
</section>
<?php if (trim($page['intro']) !== ''): ?>
<section class="page-lead"><div class="shell"><p><?= e($page['intro']) ?></p><a class="button" href="#contact">Discuss a project</a></div></section>
<?php endif; ?>
<?php foreach ($page['sections'] as $n => $section): ?>
<?php $img = img_tag($content, $section['image'] ?? '', $section['heading']); ?>
<section class="detail-section">
  <div class="shell detail-grid layout-<?= $n % 2 === 0 ? 'text_left' : 'text_right' ?><?= $img ? '' : ' no-media' ?>">
    <div class="detail-copy" data-reveal><?php if ($section['heading']): ?><h2><?= e($section['heading']) ?></h2><?php endif; ?><?php if ($section['body']): ?><p><?= e($section['body']) ?></p><?php endif; ?>
      <?php if ($section['items']): ?><div class="section-items"><?php foreach ($section['items'] as $item): ?><?php if ($item['type'] === 'subheading'): ?><h3><?= e($item['text']) ?></h3><?php elseif ($item['type'] === 'bullet' || $item['type'] === 'numbered'): ?><p class="list-item <?= $item['type'] === 'numbered' ? 'numbered' : '' ?>"><?= e($item['text']) ?></p><?php else: ?><p><?= e($item['text']) ?></p><?php endif; ?><?php endforeach; ?></div><?php endif; ?>
    </div>
    <?php if ($img): ?><div class="detail-media" data-reveal><?= $img ?></div><?php endif; ?>
  </div>
</section>
<?php endforeach; ?>
<?php if ($others): ?>
<section class="related">
  <div class="shell"><div class="section-heading"><p class="eyebrow"><?= $group ?></p><h2><?= $isService ? 'More services' : 'More projects' ?></h2></div>
    <div class="card-grid"><?php foreach ($others as $item): ?><?= render('public/card', ['content' => $content, 'item' => $item, 'q' => $q, 'more' => $isService ? 'Explore service' : 'View project']) ?><?php endforeach; ?></div>
  </div>
</section>
<?php endif; ?>
<?= render('public/contact', ['content' => $content, 'return_path' => page_path($page)]) ?>
