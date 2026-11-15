<?php /** @var array $enquiries */ ?>
<div class="page-head"><div><h1>Enquiries</h1><p>A copy of each message sent through the website's contact form. The message is also emailed, as before.</p></div></div>
<?php if (!$enquiries): ?><section class="card"><p class="muted">No enquiries have been recorded yet.</p></section><?php endif; ?>
<?php foreach ($enquiries as $entry): ?>
<article class="card enquiry" id="e-<?= e($entry['id']) ?>">
  <div class="card-head"><h2><?= e($entry['first_name'] . ' ' . $entry['last_name']) ?></h2><span class="badge badge-<?= e($entry['status']) ?>"><?= $entry['status'] === 'new' ? 'New' : 'Done' ?></span></div>
  <p class="muted"><?= e(date('j M Y, H:i', strtotime($entry['received_at']))) ?> UTC · <a href="mailto:<?= e($entry['email']) ?>"><?= e($entry['email']) ?></a><?= $entry['phone'] ? ' · ' . e($entry['phone']) : '' ?><?= empty($entry['email_sent']) ? ' · <strong>the email may not have been sent</strong>' : '' ?></p>
  <p class="message"><?= nl2br(e($entry['message'])) ?></p>
  <div class="row">
    <a class="btn btn-small" href="mailto:<?= e($entry['email']) ?>?subject=<?= rawurlencode('Your enquiry to VARTEC') ?>">Reply by email</a>
    <form method="post"><?= csrf_field() ?><input type="hidden" name="id" value="<?= e($entry['id']) ?>"><input type="hidden" name="action" value="<?= $entry['status'] === 'new' ? 'done' : 'new' ?>"><button type="submit" class="btn btn-small"><?= $entry['status'] === 'new' ? 'Mark as done' : 'Mark as new' ?></button></form>
    <form method="post" data-confirm="Delete this enquiry from the admin? The email you received is not affected."><?= csrf_field() ?><input type="hidden" name="id" value="<?= e($entry['id']) ?>"><input type="hidden" name="action" value="delete"><button type="submit" class="btn btn-small btn-quiet">Delete</button></form>
  </div>
</article>
<?php endforeach; ?>
