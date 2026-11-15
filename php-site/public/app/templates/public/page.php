<?php
/** @var array $content @var array $page */
$isService = $page['kind'] === 'service';
$q = $preview ? '?preview=1' : '';
?>
<section class="page-hero"><div class="shell"><a class="back-link" href="/<?= $q ?>#<?= $isService ? 'services' : 'projects' ?>">← All <?= $isService ? 'services' : 'projects' ?></a><p class="eyebrow"><?= $isService ? 'Services' : 'Projects' ?></p><h1><?= e($page['title']) ?></h1><?php if ($page['intro']): ?><p><?= e($page['intro']) ?></p><?php endif; ?><a class="button" href="#contact">Discuss a project</a></div></section>
<?php foreach ($page['sections'] as $n => $section): ?>
<section class="detail-section theme-<?= $n % 2 === 0 ? 'white' : 'gold' ?>">
  <div class="shell detail-grid layout-<?= $n % 2 === 0 ? 'text_left' : 'text_right' ?>">
    <div class="detail-copy"><?php if ($section['heading']): ?><h2><?= e($section['heading']) ?></h2><?php endif; ?><?php if ($section['body']): ?><p><?= e($section['body']) ?></p><?php endif; ?>
      <?php if ($section['items']): ?><div class="section-items"><?php foreach ($section['items'] as $item): ?><?php if ($item['type'] === 'subheading'): ?><h3><?= e($item['text']) ?></h3><?php elseif ($item['type'] === 'bullet' || $item['type'] === 'numbered'): ?><p class="list-item <?= $item['type'] === 'numbered' ? 'numbered' : '' ?>"><?= e($item['text']) ?></p><?php else: ?><p><?= e($item['text']) ?></p><?php endif; ?><?php endforeach; ?></div><?php endif; ?>
    </div>
    <?php $img = img_tag($content, $section['image'] ?? '', $section['heading']); if ($img): ?><div class="detail-media"><?= $img ?></div><?php endif; ?>
  </div>
</section>
<?php endforeach; ?>
<?= render('public/contact', ['content' => $content, 'return_path' => page_path($page)]) ?>
