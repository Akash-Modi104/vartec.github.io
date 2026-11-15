<?php
/** @var array $content */
$h = $content['home'];
$slides = array_values(array_filter($h['hero']['slides'], fn ($id) => media_url($content, $id) !== ''));
$services = visible_pages($content, 'service');
$projects = visible_pages($content, 'project');
$q = $preview ? '?preview=1' : '';
$video = media_url($content, $h['about']['video'] ?? '');
?>
<section class="hero" data-hero>
  <div class="hero-media" <?php if ($slides): ?>style="background-image:url('<?= e(media_url($content, $slides[0])) ?>')"<?php endif; ?>></div>
  <div class="hero-shade"></div>
  <div class="shell hero-content">
    <p class="eyebrow eyebrow-light"><?= e($h['hero']['eyebrow']) ?></p>
    <h1<?= mb_strlen($h['hero']['title']) < 30 ? ' class="hero-title-compact"' : '' ?>><?= e($h['hero']['title']) ?></h1>
    <p><?= e($h['hero']['summary']) ?></p>
    <div class="hero-actions"><?php if ($services): ?><a class="button" href="#services">Our Services</a><?php endif; ?><a class="button button-outline" href="#contact">Discuss a project</a></div>
    <div class="hero-proof" aria-label="VARTEC project capabilities">
      <?php foreach ($h['hero']['points'] as $n => $point): ?><span><b><?= sprintf('%02d', $n + 1) ?></b><strong><?= e($point) ?></strong></span><?php endforeach; ?>
    </div>
  </div>
  <div class="hero-slides" hidden><?php foreach ($slides as $id): ?><span data-src="<?= e(media_url($content, $id)) ?>" data-alt="<?= e($content['media'][$id]['alt'] ?? '') ?>"></span><?php endforeach; ?></div>
</section>

<section class="section" id="about">
  <div class="shell split-layout">
    <div class="section-copy"><p class="eyebrow"><?= e($h['about']['heading']) ?></p><h2><?= e($h['about']['heading']) ?></h2><?php foreach ($h['about']['paragraphs'] as $p): ?><?php if (trim($p) !== ''): ?><p><?= e($p) ?></p><?php endif; ?><?php endforeach; ?></div>
    <?php if ($video): ?><div class="media-frame video-frame"><span class="video-label"><i></i> <?= e($h['about']['video_label']) ?></span><video data-autoplay-video autoplay muted loop playsinline controls preload="metadata" disablepictureinpicture poster="<?= e(media_url($content, $h['about']['poster'] ?? '')) ?>" aria-label="VARTEC solar engineering project overview"><source src="<?= e($video) ?>" type="video/mp4"></video></div><?php endif; ?>
  </div>
</section>

<?php if (!empty($h['capabilities']['cards'])): ?>
<section class="section feature-section theme-light">
  <div class="shell"><div class="section-heading"><p class="eyebrow"><?= e($h['capabilities']['eyebrow']) ?></p><h2><?= e($h['capabilities']['heading']) ?></h2><?php if ($h['capabilities']['intro']): ?><p><?= e($h['capabilities']['intro']) ?></p><?php endif; ?></div>
    <div class="feature-grid"><?php foreach ($h['capabilities']['cards'] as $n => $card): ?><article class="feature-card"><span><?= sprintf('%02d', $n + 1) ?></span><h3><?= e($card['title']) ?></h3><p><?= e($card['body']) ?></p></article><?php endforeach; ?></div>
  </div>
</section>
<?php endif; ?>

<?php if ($services): ?>
<section class="section services-section" id="services">
  <div class="shell"><div class="section-heading"><p class="eyebrow">Services</p><h2><?= e($h['services_heading']) ?></h2></div>
    <div class="card-grid"><?php foreach ($services as $item): ?><a class="media-card" href="<?= e(page_path($item) . $q) ?>"><?= img_tag($content, $item['card_image'] ?? '', $item['title']) ?><div><p>Services</p><h3><?= e($item['title']) ?></h3><span>Explore service →</span></div></a><?php endforeach; ?></div>
  </div>
</section>
<?php endif; ?>

<?php if ($projects): ?>
<section class="section projects-section" id="projects">
  <div class="shell"><div class="section-heading"><p class="eyebrow eyebrow-light">Projects</p><h2><?= e($h['projects_heading']) ?></h2></div>
    <div class="project-grid"><?php foreach ($projects as $n => $item): ?><a class="project-card" href="<?= e(page_path($item) . $q) ?>"><?= img_tag($content, $item['card_image'] ?? '', $item['title']) ?><div><span><?= sprintf('%02d', $n + 1) ?></span><h3><?= e($item['title']) ?></h3><p><?= e(truncate_words($item['intro'], 24)) ?></p><strong>View project →</strong></div></a><?php endforeach; ?></div>
  </div>
</section>
<?php endif; ?>
<?= render('public/contact', ['content' => $content, 'return_path' => '/']) ?>
