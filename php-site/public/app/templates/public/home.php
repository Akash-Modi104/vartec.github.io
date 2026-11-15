<?php
/** @var array $content */
$h = $content['home'];
$slides = array_values(array_filter($h['hero']['slides'], fn ($id) => media_url($content, $id) !== ''));
$services = visible_pages($content, 'service');
$projects = visible_pages($content, 'project');
$q = $preview ? '?preview=1' : '';
$w = fn (string $key): string => e(wording($content, $key));
$video = media_url($content, $h['about']['video'] ?? '');
$first = $slides ? media_item($content, $slides[0]) : null;
$points = array_values(array_filter($h['hero']['points'], fn ($p) => trim($p) !== ''));
?>
<section class="hero" data-hero>
  <div class="hero-stage" data-hero-stage>
    <?php if ($first): ?><img class="hero-img is-active" src="<?= e(media_url($content, $slides[0])) ?>" alt="<?= e($first['alt'] ?? '') ?>"<?= isset($first['w'], $first['h']) ? ' width="' . (int) $first['w'] . '" height="' . (int) $first['h'] . '"' : '' ?> fetchpriority="high" decoding="async"><?php endif; ?>
  </div>
  <div class="hero-shade"></div>
  <div class="shell hero-content">
    <h1><?php if (trim($h['hero']['eyebrow']) !== ''): ?><span class="hero-kicker"><?= e($h['hero']['eyebrow']) ?></span> <?php endif; ?><span class="hero-word<?= mb_strlen($h['hero']['title']) < 14 ? ' compact' : '' ?>"><?= e($h['hero']['title']) ?></span></h1>
    <p class="hero-summary"><?= e($h['hero']['summary']) ?></p>
    <div class="hero-actions"><?php if ($services): ?><a class="button" href="#services"><?= $w('btn_services') ?></a><?php endif; ?><a class="button button-outline" href="#contact"><?= $w('btn_discuss') ?></a></div>
  </div>
  <div class="hero-bar">
    <div class="shell hero-bar-inner">
      <?php if ($points): ?><ul class="hero-points" aria-label="What <?= e($content['settings']['brand_name']) ?> does"><?php foreach ($points as $n => $point): ?><li><b><?= sprintf('%02d', $n + 1) ?></b><?= e($point) ?></li><?php endforeach; ?></ul><?php endif; ?>
      <?php if (count($slides) > 1): ?>
      <div class="hero-controls" data-hero-controls hidden>
        <button class="hero-arrow" type="button" data-hero-prev aria-label="Previous photo">←</button>
        <div class="hero-dots" data-hero-dots></div>
        <button class="hero-arrow" type="button" data-hero-next aria-label="Next photo">→</button>
      </div>
      <?php endif; ?>
    </div>
  </div>
  <div hidden data-hero-list><?php foreach ($slides as $id): ?><span data-src="<?= e(media_url($content, $id)) ?>" data-alt="<?= e($content['media'][$id]['alt'] ?? '') ?>"></span><?php endforeach; ?></div>
</section>

<section class="section" id="about">
  <div class="shell split-layout">
    <div class="section-copy" data-reveal><p class="eyebrow"><?= $w('label_about') ?></p><h2><?= e($h['about']['heading']) ?></h2><?php foreach ($h['about']['paragraphs'] as $p): ?><?php if (trim($p) !== ''): ?><p><?= e($p) ?></p><?php endif; ?><?php endforeach; ?></div>
    <?php if ($video): ?><div class="media-frame" data-reveal><span class="video-label"><i></i> <?= e($h['about']['video_label']) ?></span><video data-inview-video muted loop playsinline controls preload="none" disablepictureinpicture poster="<?= e(media_url($content, $h['about']['poster'] ?? '')) ?>" aria-label="<?= e($content['settings']['brand_name']) ?> solar engineering project overview"><source src="<?= e($video) ?>" type="video/mp4"></video></div><?php endif; ?>
  </div>
</section>

<?php if (!empty($h['capabilities']['cards'])): ?>
<section class="section section-cream" id="capabilities">
  <div class="shell"><div class="section-heading" data-reveal><p class="eyebrow"><?= e($h['capabilities']['eyebrow']) ?></p><h2><?= e($h['capabilities']['heading']) ?></h2><?php if ($h['capabilities']['intro']): ?><p><?= e($h['capabilities']['intro']) ?></p><?php endif; ?></div>
    <div class="feature-grid"><?php foreach ($h['capabilities']['cards'] as $n => $card): ?><article class="feature-card" data-reveal><span aria-hidden="true"><?= sprintf('%02d', $n + 1) ?></span><h3><?= e($card['title']) ?></h3><p><?= e($card['body']) ?></p></article><?php endforeach; ?></div>
  </div>
</section>
<?php endif; ?>

<?php if ($services): ?>
<section class="section" id="services">
  <div class="shell"><div class="section-heading" data-reveal><p class="eyebrow"><?= $w('label_services') ?></p><h2><?= e($h['services_heading']) ?></h2></div>
    <div class="card-grid"><?php foreach ($services as $item): ?><?= render('public/card', ['content' => $content, 'item' => $item, 'q' => $q, 'tag' => wording($content, 'label_services'), 'more' => wording($content, 'link_service')]) ?><?php endforeach; ?></div>
  </div>
</section>
<?php endif; ?>

<?php if ($projects): ?>
<section class="section section-cream" id="projects">
  <div class="shell"><div class="section-heading" data-reveal><p class="eyebrow"><?= $w('label_projects') ?></p><h2><?= e($h['projects_heading']) ?></h2></div>
    <div class="project-grid"><?php foreach ($projects as $n => $item): ?><?= render('public/card', ['content' => $content, 'item' => $item, 'q' => $q, 'number' => $n + 1, 'more' => wording($content, 'link_project'), 'class' => 'project-card']) ?><?php endforeach; ?></div>
  </div>
</section>
<?php endif; ?>
<?= render('public/contact', ['content' => $content, 'return_path' => '/']) ?>
