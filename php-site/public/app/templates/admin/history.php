<?php /** @var array $versions */ ?>
<div class="page-head"><div><a class="back" href="/admin/settings">← Settings</a><h1>Earlier versions</h1><p>The last <?= HISTORY_KEEP ?> published versions are kept. Restoring one loads it as a draft, so you can preview it before it goes live.</p></div></div>
<section class="card">
  <?php if (!$versions): ?><p class="muted">Nothing has been published from this admin yet, so there is no earlier version to go back to.</p><?php endif; ?>
  <?php foreach ($versions as $version): ?>
  <div class="list-row"><span><strong>Live until <?= e(date('j M Y, H:i', strtotime($version['saved_at']))) ?> UTC</strong><small>Replaced by a publish from <?= e($version['replaced_by']) ?></small></span>
    <form method="post" data-confirm="Load this version as your draft? Any unpublished changes you have now will be replaced."><?= csrf_field() ?><input type="hidden" name="id" value="<?= e($version['id']) ?>"><button type="submit" class="btn btn-small">Restore as draft</button></form></div>
  <?php endforeach; ?>
</section>
