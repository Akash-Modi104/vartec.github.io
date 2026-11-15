<?php /** @var array $item */ ?>
<div class="page-head"><div><a class="back" href="/admin/media">← Images and video</a><h1>Details</h1></div></div>
<form method="post" class="card">
  <?= csrf_field() ?>
  <div class="grid-2">
    <div class="media-large"><?php if (($item['kind'] ?? 'image') === 'image'): ?><img src="<?= e(media_url($content, $id)) ?>" alt=""><?php else: ?><video src="<?= e(media_url($content, $id)) ?>" controls preload="metadata"></video><?php endif; ?></div>
    <div>
      <label>What does it show? <small>(read aloud by screen readers; used by search engines)</small><input type="text" name="alt" value="<?= e($item['alt'] ?? '') ?>" maxlength="200"<?= ($item['kind'] ?? 'image') === 'image' ? ' required' : '' ?>></label>
      <label>Where is it from?<input type="text" name="source" value="<?= e($item['source'] ?? '') ?>" maxlength="300" placeholder="e.g. Taken by our site team, or the stock library link"></label>
      <?php if (preg_match('#^https?://#', $item['source'] ?? '')): ?><p class="muted"><a href="<?= e($item['source']) ?>" target="_blank" rel="noopener noreferrer">Open the source</a></p><?php endif; ?>
      <label>Right to use it<select name="licence"><?php foreach (LICENCES as $key => $label): ?><option value="<?= e($key) ?>"<?= ($item['licence'] ?? 'unknown') === $key ? ' selected' : '' ?>><?= e($label) ?></option><?php endforeach; ?></select></label>
      <p class="muted">Choose "Licensed" only when you hold the receipt or written permission.</p>
      <p><strong>Used on:</strong> <?= $usage ? e(implode('; ', array_unique($usage))) : 'not used on any page' ?></p>
      <p class="muted">File: <?= e($item['file']) ?><?php if (isset($item['w'])): ?> · <?= (int) $item['w'] ?> × <?= (int) $item['h'] ?> pixels<?php endif; ?></p>
      <button type="submit" class="btn btn-primary">Save details</button>
    </div>
  </div>
</form>
