<?php
/** @var array $content @var array $usage */
$items = $content['media'];
if ($filter === 'check') {
    $items = array_filter($items, fn ($item) => media_needs_check($item));
} elseif ($filter === 'unused') {
    $items = array_filter($items, fn ($item, $id) => empty($usage[$id]), ARRAY_FILTER_USE_BOTH);
}
$needCheck = count(array_filter($content['media'], fn ($item) => media_needs_check($item)));
?>
<div class="page-head"><div><h1>Images and video</h1><p>Everything you can place on a page. Record where each picture came from, so every image on the website has a clear right to be there.</p></div></div>

<section class="card">
  <h2>Upload</h2>
  <form method="post" action="/admin/media/upload" enctype="multipart/form-data" class="upload">
    <?= csrf_field() ?>
    <label>File <small>(JPG, PNG, WebP, GIF or MP4, up to <?= (int) floor($max_upload / 1048576) ?> MB)</small><input type="file" name="file" accept="image/jpeg,image/png,image/webp,image/gif,video/mp4" required></label>
    <label>What does it show?<input type="text" name="alt" maxlength="200" placeholder="e.g. Solar carport at a hospital car park" required></label>
    <label>Where is it from?<input type="text" name="source" maxlength="300" placeholder="e.g. Taken by our site team, or the stock library link"></label>
    <label>Right to use it<select name="licence"><?php foreach (LICENCES as $key => $label): ?><option value="<?= e($key) ?>"><?= e($label) ?></option><?php endforeach; ?></select></label>
    <button type="submit" class="btn btn-primary">Upload</button>
  </form>
  <p class="muted">Large pictures are resized to 1600 pixels wide automatically.</p>
</section>

<nav class="tabs" aria-label="Filter">
  <a href="/admin/media"<?= $filter === 'all' ? ' class="active"' : '' ?>>All (<?= count($content['media']) ?>)</a>
  <a href="/admin/media?show=check"<?= $filter === 'check' ? ' class="active"' : '' ?>>No licence on record (<?= $needCheck ?>)</a>
  <a href="/admin/media?show=unused"<?= $filter === 'unused' ? ' class="active"' : '' ?>>Not used on any page</a>
</nav>

<section class="media-grid">
  <?php if (!$items): ?><p class="muted">Nothing to show here.</p><?php endif; ?>
  <?php foreach ($items as $id => $item): $used = $usage[$id] ?? []; ?>
  <article class="media-card">
    <a class="media-thumb" href="/admin/media/edit?id=<?= e(rawurlencode((string) $id)) ?>">
      <?php if (($item['kind'] ?? 'image') === 'image'): ?><img loading="lazy" src="<?= e(media_url($content, (string) $id)) ?>" alt=""><?php else: ?><span class="tile-video">VIDEO</span><?php endif; ?>
    </a>
    <div class="media-body">
      <strong><?= e($item['alt'] ?: $item['file']) ?></strong>
      <?= licence_badge($item) ?>
      <small><?= $used ? 'Used on: ' . e(implode('; ', array_slice(array_unique($used), 0, 3))) . (count(array_unique($used)) > 3 ? ' and more' : '') : 'Not used on any page' ?></small>
      <div class="row">
        <a class="btn btn-small" href="/admin/media/edit?id=<?= e(rawurlencode((string) $id)) ?>">Details</a>
        <?php if (!$used): ?><form method="post" action="/admin/media/delete" data-confirm="Remove this file from the library?"><?= csrf_field() ?><input type="hidden" name="id" value="<?= e((string) $id) ?>"><button type="submit" class="btn btn-small btn-quiet">Remove</button></form><?php endif; ?>
      </div>
    </div>
  </article>
  <?php endforeach; ?>
</section>
