<?php
/** One linked card for a service or project. @var array $content @var array $item */
$intro = truncate_words($item['intro'] ?? '', 22);
?>
<a class="<?= e($class ?? 'media-card') ?>" href="<?= e(page_path($item) . ($q ?? '')) ?>" data-reveal>
  <div class="card-media"><?= img_tag($content, $item['card_image'] ?? '', $item['title']) ?><?php if (!empty($number)): ?><span class="card-number" aria-hidden="true"><?= sprintf('%02d', $number) ?></span><?php endif; ?></div>
  <div class="card-body"><?php if (!empty($tag)): ?><p class="card-tag"><?= e($tag) ?></p><?php endif; ?><h3><?= e($item['title']) ?></h3><?php if ($intro !== ''): ?><p><?= e($intro) ?></p><?php endif; ?><span class="card-link"><?= e($more ?? 'Read more') ?> <span class="arrow" aria-hidden="true">→</span></span></div>
</a>
