<?php /** @var array $content */ ?>
<div class="page-head"><div><h1>Dashboard</h1><p>Edit anything here as a draft, preview it, then publish. Nothing changes on the live website until you press Publish.</p></div></div>

<?php if (!empty($welcome)): ?>
<section class="card card-welcome">
  <h2>New here? Start with the guide</h2>
  <p>A short illustrated guide shows how to change text and pictures, add a project, preview and publish. It takes about ten minutes to read.</p>
  <div class="row">
    <a class="btn btn-primary" href="/admin/guide" target="_blank" rel="noopener"><?= icon('help') ?> Open the guide (PDF)</a>
    <a class="btn" href="/admin/help">Quick help</a>
    <form method="post" action="/admin/guide"><?= csrf_field() ?><button type="submit" class="btn btn-quiet">Hide this</button></form>
  </div>
</section>
<?php endif; ?>

<?php if ($changes): ?>
<section class="card card-draft">
  <h2>You have unpublished changes</h2>
  <p>Your edits are saved as a draft. Visitors still see the previous version.</p>
  <div class="row">
    <a class="btn" href="/?preview=1" target="_blank" rel="noopener"><?= icon('eye') ?> Preview the draft</a>
    <form method="post" action="/admin/publish"><?= csrf_field() ?><button type="submit" class="btn btn-primary">Publish to website</button></form>
    <form method="post" action="/admin/discard" data-confirm="Discard every unpublished change? This cannot be undone."><?= csrf_field() ?><button type="submit" class="btn btn-quiet">Discard changes</button></form>
  </div>
</section>
<?php endif; ?>

<?php if ($flagged): ?>
<section class="card card-warn">
  <h2><?= icon('warn') ?> <?= count($flagged) ?> image<?= count($flagged) === 1 ? '' : 's' ?> on the website <?= count($flagged) === 1 ? 'has' : 'have' ?> no licence on record</h2>
  <p>Using a photo without the right to do so can lead to a copyright claim. Replace these with your own photos, or record the licence once you hold one.</p>
  <a class="btn btn-small" href="/admin/media?show=check">Review these images</a>
</section>
<?php endif; ?>

<section class="tiles">
  <a class="tile-link" href="/admin/home"><?= icon('home') ?><strong>Home page</strong><span>Banner, About Us, capability cards</span></a>
  <a class="tile-link" href="/admin/pages?kind=service"><?= icon('service') ?><strong>Services</strong><span><?= count(array_filter($content['pages'], fn ($p) => $p['kind'] === 'service')) ?> pages</span></a>
  <a class="tile-link" href="/admin/pages?kind=project"><?= icon('project') ?><strong>Projects</strong><span><?= count(array_filter($content['pages'], fn ($p) => $p['kind'] === 'project')) ?> pages</span></a>
  <a class="tile-link" href="/admin/pages?kind=info"><?= icon('info') ?><strong>Other pages</strong><span>Privacy policy, terms and similar</span></a>
  <a class="tile-link" href="/admin/media"><?= icon('media') ?><strong>Images and video</strong><span><?= count($content['media']) ?> files</span></a>
  <a class="tile-link" href="/admin/wording"><?= icon('wording') ?><strong>Wording</strong><span>Menu names, buttons, form labels</span></a>
  <a class="tile-link" href="/admin/settings"><?= icon('settings') ?><strong>Settings</strong><span>Contact details, search text, help chat, editors</span></a>
  <a class="tile-link" href="/admin/help"><?= icon('help') ?><strong>Help</strong><span>How to do common jobs</span></a>
</section>

<section class="card">
  <div class="card-head"><h2>Recent enquiries</h2><a href="/admin/enquiries">View all</a></div>
  <?php if (!$enquiries): ?><p class="muted">No enquiries have been recorded yet. Messages sent through the contact form will appear here as well as in your email.</p><?php endif; ?>
  <?php foreach ($enquiries as $entry): ?>
  <a class="list-row" href="/admin/enquiries#e-<?= e($entry['id']) ?>"><span><strong><?= e($entry['first_name'] . ' ' . $entry['last_name']) ?></strong><small><?= e(mb_substr($entry['message'], 0, 90)) ?></small></span><span class="badge badge-<?= e($entry['status']) ?>"><?= $entry['status'] === 'new' ? 'New' : 'Done' ?></span></a>
  <?php endforeach; ?>
</section>
