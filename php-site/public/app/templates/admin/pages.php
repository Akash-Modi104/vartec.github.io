<?php
/** @var array $pages */
$label = PAGE_KINDS[$kind][1];
$about = $kind === 'info'
    ? 'Pages that are not a service or a project, such as a privacy policy or terms. Each one gets a link at the bottom of every page.'
    : 'Open a page to edit it. Use the arrows to change the order shown in the menu and on the home page.';
?>
<div class="page-head"><div><h1><?= e(PAGE_KINDS[$kind][0]) ?></h1><p><?= e($about) ?></p></div>
  <a class="btn btn-primary" href="/admin/page?kind=<?= e($kind) ?>"><?= icon('plus') ?> Add a <?= e($label) ?></a></div>

<form method="post" action="/admin/pages/order" class="card" data-sortable-form>
  <?= csrf_field() ?><input type="hidden" name="kind" value="<?= e($kind) ?>">
  <?php if (!$pages): ?><p class="muted">Nothing here yet. Press "Add a <?= e($label) ?>" to make the first one<?= $kind === 'info' ? ', for example a privacy policy' : '' ?>.</p><?php endif; ?>
  <div data-sortable>
  <?php foreach ($pages as $page): ?>
    <div class="sort-row" data-sort-item>
      <input type="hidden" name="ids[]" value="<?= e($page['id']) ?>">
      <span class="sort-arrows"><button type="button" class="iconbtn" data-move="-1" aria-label="Move up"><?= icon('up') ?></button><button type="button" class="iconbtn" data-move="1" aria-label="Move down"><?= icon('down') ?></button></span>
      <span class="thumb"><?php if (media_url($content, $page['card_image'] ?? '')): ?><img loading="lazy" src="<?= e(media_url($content, $page['card_image'])) ?>" alt=""><?php endif; ?></span>
      <a class="sort-title" href="/admin/page?id=<?= e(rawurlencode($page['id'])) ?>"><strong><?= e($page['title']) ?></strong><small><?= e(page_path($page)) ?> · <?= count($page['sections']) ?> section<?= count($page['sections']) === 1 ? '' : 's' ?></small></a>
      <label class="switch"><input type="checkbox" name="visible[]" value="<?= e($page['id']) ?>"<?= !empty($page['visible']) ? ' checked' : '' ?>><i></i><span>Shown on website</span></label>
      <a class="btn btn-small" href="/admin/page?id=<?= e(rawurlencode($page['id'])) ?>">Edit</a>
    </div>
  <?php endforeach; ?>
  </div>
  <?php if ($pages): ?><div class="form-foot"><button type="submit" class="btn btn-primary">Save order and visibility</button></div><?php endif; ?>
</form>
