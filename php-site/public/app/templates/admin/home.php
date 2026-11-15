<?php
/** @var array $content */
$h = $content['home'];
$points = array_pad($h['hero']['points'], 4, '');
$about = array_pad($h['about']['paragraphs'], 2, '');
$contactText = array_pad($h['contact']['text'], 2, '');
?>
<div class="page-head"><div><h1>Home page</h1><p>The sections below are in the order they appear on the home page.</p></div>
  <a class="btn" href="/?preview=1" target="_blank" rel="noopener"><?= icon('eye') ?> Preview</a></div>

<form method="post" data-home-form>
  <?= csrf_field() ?>
  <section class="card">
    <h2>1. Banner</h2>
    <div class="grid-2">
      <div>
        <label>Small line above the title<input type="text" name="hero_eyebrow" value="<?= e($h['hero']['eyebrow']) ?>" maxlength="120"></label>
        <label>Title <small>(the main heading search engines read)</small><input type="text" name="hero_title" value="<?= e($h['hero']['title']) ?>" maxlength="120" required></label>
        <label>Summary<textarea name="hero_summary" rows="3"><?= e($h['hero']['summary']) ?></textarea></label>
      </div>
      <div>
        <span class="label">Four short points under the banner</span>
        <?php foreach ($points as $point): ?><input type="text" name="hero_points[]" value="<?= e($point) ?>" maxlength="60" aria-label="Point"><?php endforeach; ?>
      </div>
    </div>
    <span class="label">Banner pictures <small>(they rotate; the first one loads first)</small></span>
    <div class="slides" data-list>
      <?php foreach ($h['hero']['slides'] as $id): ?>
      <div class="slide" data-list-item><?= picker_field($content, 'slides[]', $id) ?>
        <span><button type="button" class="iconbtn" data-move="-1" aria-label="Move earlier"><?= icon('up') ?></button><button type="button" class="iconbtn" data-move="1" aria-label="Move later"><?= icon('down') ?></button><button type="button" class="iconbtn danger" data-remove aria-label="Remove picture"><?= icon('trash') ?></button></span></div>
      <?php endforeach; ?>
    </div>
    <button type="button" class="btn btn-small" data-add-slide><?= icon('plus') ?> Add banner picture</button>
    <template data-slide-template><div class="slide" data-list-item><?= picker_field($content, 'slides[]', '') ?>
      <span><button type="button" class="iconbtn" data-move="-1" aria-label="Move earlier"><?= icon('up') ?></button><button type="button" class="iconbtn" data-move="1" aria-label="Move later"><?= icon('down') ?></button><button type="button" class="iconbtn danger" data-remove aria-label="Remove picture"><?= icon('trash') ?></button></span></div></template>
  </section>

  <section class="card">
    <h2>2. About Us</h2>
    <div class="grid-2">
      <div>
        <label>Heading<input type="text" name="about_heading" value="<?= e($h['about']['heading']) ?>" maxlength="120"></label>
        <?php foreach ($about as $n => $p): ?><label>Paragraph <?= $n + 1 ?><textarea name="about_paragraphs[]" rows="6"><?= e($p) ?></textarea></label><?php endforeach; ?>
      </div>
      <div>
        <span class="label">Video <small>(MP4)</small></span><?= picker_field($content, 'video', $h['about']['video'] ?? '', 'video') ?>
        <label>Label on the video<input type="text" name="video_label" value="<?= e($h['about']['video_label']) ?>" maxlength="80"></label>
        <span class="label">Picture shown before the video plays</span><?= picker_field($content, 'poster', $h['about']['poster'] ?? '') ?>
      </div>
    </div>
  </section>

  <section class="card">
    <h2>3. What we do</h2>
    <label>Small line above the heading<input type="text" name="cap_eyebrow" value="<?= e($h['capabilities']['eyebrow']) ?>" maxlength="120"></label>
    <label>Heading<input type="text" name="cap_heading" value="<?= e($h['capabilities']['heading']) ?>" maxlength="160"></label>
    <label>Introduction<textarea name="cap_intro" rows="2"><?= e($h['capabilities']['intro']) ?></textarea></label>
    <span class="label">Cards</span>
    <div data-list data-cards>
      <?php foreach ($h['capabilities']['cards'] as $i => $card): ?>
      <div class="item item-card" data-list-item>
        <input type="text" name="cards[<?= $i ?>][title]" data-name="title" value="<?= e($card['title']) ?>" placeholder="Card title" aria-label="Card title" maxlength="120">
        <input type="text" name="cards[<?= $i ?>][body]" data-name="body" value="<?= e($card['body']) ?>" placeholder="One or two sentences" aria-label="Card text" maxlength="600">
        <button type="button" class="iconbtn" data-move="-1" aria-label="Move up"><?= icon('up') ?></button><button type="button" class="iconbtn" data-move="1" aria-label="Move down"><?= icon('down') ?></button><button type="button" class="iconbtn danger" data-remove aria-label="Remove card"><?= icon('trash') ?></button>
      </div>
      <?php endforeach; ?>
    </div>
    <button type="button" class="btn btn-small" data-add-card><?= icon('plus') ?> Add card</button>
    <template data-card-template><div class="item item-card" data-list-item>
      <input type="text" data-name="title" placeholder="Card title" aria-label="Card title" maxlength="120"><input type="text" data-name="body" placeholder="One or two sentences" aria-label="Card text" maxlength="600">
      <button type="button" class="iconbtn" data-move="-1" aria-label="Move up"><?= icon('up') ?></button><button type="button" class="iconbtn" data-move="1" aria-label="Move down"><?= icon('down') ?></button><button type="button" class="iconbtn danger" data-remove aria-label="Remove card"><?= icon('trash') ?></button></div></template>
  </section>

  <section class="card">
    <h2>4. Services and projects</h2>
    <p class="muted">The cards themselves come from your <a href="/admin/pages?kind=service">services</a> and <a href="/admin/pages?kind=project">projects</a>.</p>
    <div class="grid-2">
      <label>Heading above the services<input type="text" name="services_heading" value="<?= e($h['services_heading']) ?>" maxlength="160"></label>
      <label>Heading above the projects<input type="text" name="projects_heading" value="<?= e($h['projects_heading']) ?>" maxlength="160"></label>
    </div>
  </section>

  <section class="card">
    <h2>5. Contact</h2>
    <p class="muted">This block appears at the bottom of every page. Phone, email and office hours are under <a href="/admin/settings">Settings</a>.</p>
    <div class="grid-2">
      <div>
        <label>Heading<input type="text" name="contact_heading" value="<?= e($h['contact']['heading']) ?>" maxlength="160"></label>
        <?php foreach ($contactText as $n => $p): ?><label>Line <?= $n + 1 ?><textarea name="contact_text[]" rows="2"><?= e($p) ?></textarea></label><?php endforeach; ?>
      </div>
      <label>Heading above the form<input type="text" name="form_heading" value="<?= e($h['contact']['form_heading']) ?>" maxlength="160"></label>
    </div>
  </section>

  <div class="savebar"><button type="submit" class="btn btn-primary">Save draft</button></div>
</form>
