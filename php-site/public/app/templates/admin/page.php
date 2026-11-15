<?php
/** @var array $content @var array $page */
$kindLabel = $page['kind'] === 'service' ? 'service' : 'project';
$types = ['paragraph' => 'Paragraph', 'bullet' => 'Bullet point', 'numbered' => 'Numbered point', 'subheading' => 'Small heading'];
$section_block = function (array $section, int $i) use ($content, $types) { ob_start(); ?>
  <fieldset class="block" data-section>
    <div class="block-head"><strong data-section-label>Section <?= $i + 1 ?></strong>
      <span><button type="button" class="iconbtn" data-move="-1" aria-label="Move section up"><?= icon('up') ?></button><button type="button" class="iconbtn" data-move="1" aria-label="Move section down"><?= icon('down') ?></button><button type="button" class="iconbtn danger" data-remove aria-label="Remove section"><?= icon('trash') ?></button></span></div>
    <div class="grid-2">
      <div>
        <label>Heading<input type="text" name="sections[<?= $i ?>][heading]" data-name="heading" value="<?= e($section['heading']) ?>" maxlength="300"></label>
        <label>Text <small>(optional)</small><textarea name="sections[<?= $i ?>][body]" data-name="body" rows="4"><?= e($section['body']) ?></textarea></label>
      </div>
      <div><span class="label">Picture <small>(optional)</small></span><?= picker_field($content, "sections[$i][image]", $section['image'] ?? '', 'image', 'image') ?></div>
    </div>
    <div class="items" data-items>
      <?php foreach ($section['items'] as $j => $item): ?>
      <div class="item" data-item>
        <select name="sections[<?= $i ?>][items][<?= $j ?>][type]" data-name="type" aria-label="Type"><?php foreach ($types as $key => $label): ?><option value="<?= $key ?>"<?= $item['type'] === $key ? ' selected' : '' ?>><?= $label ?></option><?php endforeach; ?></select>
        <input type="text" name="sections[<?= $i ?>][items][<?= $j ?>][text]" data-name="text" value="<?= e($item['text']) ?>" aria-label="Text">
        <button type="button" class="iconbtn" data-move="-1" aria-label="Move up"><?= icon('up') ?></button><button type="button" class="iconbtn" data-move="1" aria-label="Move down"><?= icon('down') ?></button><button type="button" class="iconbtn danger" data-remove aria-label="Remove"><?= icon('trash') ?></button>
      </div>
      <?php endforeach; ?>
    </div>
    <div class="row"><button type="button" class="btn btn-small" data-add-item="bullet"><?= icon('plus') ?> Add bullet point</button><button type="button" class="btn btn-small" data-add-item="paragraph"><?= icon('plus') ?> Add paragraph</button></div>
  </fieldset>
<?php return ob_get_clean(); };
?>
<div class="page-head"><div><a class="back" href="/admin/pages?kind=<?= e($page['kind']) ?>">← All <?= e($kindLabel) ?>s</a><h1><?= $isNew ? 'New ' . e($kindLabel) : e($page['title']) ?></h1></div>
  <?php if (!$isNew): ?><a class="btn" href="<?= e(page_path($page)) ?>?preview=1" target="_blank" rel="noopener"><?= icon('eye') ?> Preview this page</a><?php endif; ?></div>

<?php foreach ($errors as $error): ?><div class="notice notice-error" role="alert"><?= e($error) ?></div><?php endforeach; ?>

<form method="post" data-page-form>
  <?= csrf_field() ?>
  <section class="card">
    <h2>Page</h2>
    <div class="grid-2">
      <div>
        <label>Title<input type="text" name="title" value="<?= e($page['title']) ?>" maxlength="160" required></label>
        <label>Introduction <small>(shown under the title, and on the home page card)</small><textarea name="intro" rows="4"><?= e($page['intro']) ?></textarea></label>
        <label class="switch"><input type="checkbox" name="visible" value="1"<?= !empty($page['visible']) ? ' checked' : '' ?>><i></i><span>Shown on website</span></label>
      </div>
      <div><span class="label">Card picture <small>(shown on the home page)</small></span><?= picker_field($content, 'card_image', $page['card_image'] ?? '') ?></div>
    </div>
  </section>

  <section class="card">
    <div class="card-head"><h2>Sections</h2><small class="muted">Each section is a block of text with an optional picture. They appear on the page in this order.</small></div>
    <div data-sections>
      <?php foreach ($page['sections'] as $i => $section): echo $section_block($section, $i); endforeach; ?>
    </div>
    <button type="button" class="btn" data-add-section><?= icon('plus') ?> Add section</button>
  </section>

  <details class="card"<?= ($page['seo_title'] || $page['seo_description']) ? ' open' : '' ?>>
    <summary><h2>Search engines and web address</h2></summary>
    <p class="muted">Leave these empty to use the page title and introduction.</p>
    <label>Title in search results <small>(about 60 characters)</small><?= counted_input('seo_title', $page['seo_title'], 60) ?></label>
    <label>Description in search results <small>(about 155 characters)</small><?= counted_input('seo_description', $page['seo_description'], 155, true) ?></label>
    <label>Web address <small>(letters, numbers and hyphens)</small><span class="prefix"><span><?= $page['kind'] === 'service' ? '/services/' : '/projects/' ?></span><input type="text" name="slug" value="<?= e($page['slug']) ?>" maxlength="80" placeholder="made from the title"></span></label>
    <?php if (!$isNew): ?><p class="muted">Changing the address of a published page breaks links other sites have made to it.</p><?php endif; ?>
  </details>

  <div class="savebar">
    <button type="submit" class="btn btn-primary">Save draft</button>
    <a class="btn btn-quiet" href="/admin/pages?kind=<?= e($page['kind']) ?>">Cancel</a>
  </div>
</form>

<?php if (!$isNew): ?>
<form method="post" action="/admin/page/delete" class="danger-zone" data-confirm="Remove this page from the draft? It stays on the live website until you publish.">
  <?= csrf_field() ?><input type="hidden" name="id" value="<?= e($page['id']) ?>">
  <button type="submit" class="btn btn-danger"><?= icon('trash') ?> Delete this <?= e($kindLabel) ?></button>
</form>
<?php endif; ?>

<template data-section-template><?= $section_block(['heading' => '', 'body' => '', 'image' => '', 'items' => []], 0) ?></template>
<template data-item-template>
  <div class="item" data-item>
    <select data-name="type" aria-label="Type"><?php foreach ($types as $key => $label): ?><option value="<?= $key ?>"><?= $label ?></option><?php endforeach; ?></select>
    <input type="text" data-name="text" aria-label="Text">
    <button type="button" class="iconbtn" data-move="-1" aria-label="Move up"><?= icon('up') ?></button><button type="button" class="iconbtn" data-move="1" aria-label="Move down"><?= icon('down') ?></button><button type="button" class="iconbtn danger" data-remove aria-label="Remove"><?= icon('trash') ?></button>
  </div>
</template>
