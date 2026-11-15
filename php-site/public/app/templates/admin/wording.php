<?php
/** @var array $content */
$groups = [];
foreach (WORDING as $key => [$group, $label, $default]) {
    $groups[$group][$key] = [$label, $default];
}
$saved = $content['settings']['wording'] ?? [];
?>
<div class="page-head"><div><h1>Wording</h1><p>The short fixed texts on the website: menu names, buttons and form labels. Leave a box empty to use the standard wording shown in grey.</p></div></div>
<form method="post">
  <?= csrf_field() ?>
  <?php foreach ($groups as $group => $items): ?>
  <section class="card">
    <h2><?= e($group) ?></h2>
    <div class="grid-2">
      <?php foreach ($items as $key => [$label, $default]): ?>
      <label><?= e($label) ?><input type="text" name="w[<?= e($key) ?>]" value="<?= e($saved[$key] ?? '') ?>" placeholder="<?= e($default) ?>" maxlength="160"></label>
      <?php endforeach; ?>
    </div>
  </section>
  <?php endforeach; ?>
  <div class="savebar"><button type="submit" class="btn btn-primary">Save draft</button></div>
</form>
