<?php
/** @var array $content */
$s = $content['settings'];
?>
<div class="page-head"><div><h1>Settings</h1></div></div>
<form method="post" data-settings-form>
  <?= csrf_field() ?>
  <section class="card">
    <h2>Contact details</h2>
    <p class="muted">Shown in the contact block and footer of every page. This does not change where contact form emails are delivered.</p>
    <div class="grid-2">
      <label>Email shown on the website<input type="email" name="contact_email" value="<?= e($s['contact_email']) ?>" required></label>
      <label>Phone<input type="text" name="phone" value="<?= e($s['phone']) ?>" maxlength="40"></label>
      <label>Office hours, weekdays<input type="text" name="office_hours_weekdays" value="<?= e($s['office_hours_weekdays']) ?>" maxlength="80"></label>
      <label>Office hours, weekend<input type="text" name="office_hours_weekend" value="<?= e($s['office_hours_weekend']) ?>" maxlength="80"></label>
    </div>
  </section>
  <section class="card">
    <h2>Footer</h2>
    <label>Short description<textarea name="footer_about" rows="2"><?= e($s['footer_about']) ?></textarea></label>
    <label>Copyright line <small>(write {year} where the year should go)</small><input type="text" name="footer_copyright" value="<?= e($s['footer_copyright']) ?>" maxlength="200"></label>
    <span class="label">Logo</span><?= picker_field($content, 'logo', $s['logo'] ?? '') ?>
  </section>
  <section class="card">
    <h2>Search engines</h2>
    <label>Website address <small>(only this address is offered to Google; test addresses stay hidden)</small><input type="url" name="site_url" value="<?= e($s['site_url']) ?>" required></label>
    <label>Home page title in search results <small>(about 60 characters)</small><?= counted_input('seo_title', $s['seo_title'], 60) ?></label>
    <label>Home page description in search results <small>(about 155 characters)</small><?= counted_input('seo_description', $s['seo_description'], 155, true) ?></label>
    <label>Google Search Console verification code <small>(optional; paste the code or the whole line Google gives you)</small><input type="text" name="google_verification" value="<?= e($s['google_verification']) ?>" maxlength="400" autocomplete="off"></label>
  </section>
  <section class="card">
    <h2>Social media links</h2>
    <p class="muted">Optional. Any link you fill in is shown at the bottom of every page and passed to search engines.</p>
    <div class="grid-2">
      <?php foreach (SOCIAL as $key => $label): ?>
      <label><?= e($label) ?><input type="url" name="social[<?= e($key) ?>]" value="<?= e($s['social'][$key] ?? '') ?>" placeholder="https://" maxlength="300"></label>
      <?php endforeach; ?>
    </div>
  </section>
  <section class="card">
    <h2>Help chat</h2>
    <label class="switch"><input type="checkbox" name="chat_enabled" value="1"<?= !empty($s['chat_enabled']) ? ' checked' : '' ?>><i></i><span>Show the help chat button on the website</span></label>
    <div class="grid-2">
      <label>Chat title<input type="text" name="chat_title" value="<?= e($s['chat_title']) ?>" maxlength="80"></label>
      <label>Welcome message<input type="text" name="chat_welcome" value="<?= e($s['chat_welcome']) ?>" maxlength="240"></label>
    </div>
    <span class="label">Answers <small>(the chat gives the first answer whose words appear in the visitor's question; the first three topics are shown as quick buttons)</small></span>
    <div data-list data-answers>
      <?php foreach ($s['chat_answers'] as $i => $a): ?>
      <div class="item item-answer" data-list-item>
        <input type="text" name="answers[<?= $i ?>][topic]" data-name="topic" value="<?= e($a['topic'] ?? '') ?>" placeholder="Topic, e.g. Battery storage" aria-label="Topic" maxlength="40">
        <input type="text" name="answers[<?= $i ?>][keywords]" data-name="keywords" value="<?= e($a['keywords'] ?? '') ?>" placeholder="Words to listen for, separated by commas" aria-label="Words to listen for" maxlength="300">
        <span class="item-buttons"><button type="button" class="iconbtn" data-move="-1" aria-label="Move up"><?= icon('up') ?></button><button type="button" class="iconbtn" data-move="1" aria-label="Move down"><?= icon('down') ?></button><button type="button" class="iconbtn danger" data-remove aria-label="Remove answer"><?= icon('trash') ?></button></span>
        <textarea name="answers[<?= $i ?>][answer]" data-name="answer" rows="2" placeholder="The answer the chat gives" aria-label="Answer" maxlength="600"><?= e($a['answer'] ?? '') ?></textarea>
      </div>
      <?php endforeach; ?>
    </div>
    <button type="button" class="btn btn-small" data-add-answer><?= icon('plus') ?> Add answer</button>
    <template data-answer-template><div class="item item-answer" data-list-item>
        <input type="text" data-name="topic" value="" placeholder="Topic, e.g. Battery storage" aria-label="Topic" maxlength="40">
        <input type="text" data-name="keywords" value="" placeholder="Words to listen for, separated by commas" aria-label="Words to listen for" maxlength="300">
        <span class="item-buttons"><button type="button" class="iconbtn" data-move="-1" aria-label="Move up"><?= icon('up') ?></button><button type="button" class="iconbtn" data-move="1" aria-label="Move down"><?= icon('down') ?></button><button type="button" class="iconbtn danger" data-remove aria-label="Remove answer"><?= icon('trash') ?></button></span>
        <textarea data-name="answer" rows="2" placeholder="The answer the chat gives" aria-label="Answer" maxlength="600"></textarea>
      </div></template>
    <label>Answer when nothing matches<textarea name="chat_fallback" rows="2" maxlength="600"><?= e($s['chat_fallback']) ?></textarea></label>
    <p class="muted">Where an answer says "contact our team" or "contact us", the chat turns those words into a link to the contact form.</p>
  </section>
  <div class="savebar"><button type="submit" class="btn btn-primary">Save draft</button></div>
</form>

<section class="card" id="account">
  <h2>Your password</h2>
  <form method="post" action="/admin/settings/password" class="grid-2">
    <?= csrf_field() ?>
    <label>Current password<input type="password" name="current_password" autocomplete="current-password" required></label>
    <label>New password <small>(at least 10 characters)</small><input type="password" name="new_password" autocomplete="new-password" minlength="10" required></label>
    <div><button type="submit" class="btn">Change password</button></div>
  </form>
</section>

<section class="card" id="two-step">
  <h2>Two-step sign-in</h2>
  <?php if ($two_step_on): ?>
    <p><span class="badge badge-own">On</span> You are asked for a code from your authenticator app each time you sign in.</p>
    <form method="post" action="/admin/settings/two-step" class="grid-2">
      <?= csrf_field() ?><input type="hidden" name="action" value="disable">
      <label>Your password, to turn it off<input type="password" name="current_password" autocomplete="current-password" required></label>
      <div><button type="submit" class="btn btn-danger">Turn off two-step sign-in</button></div>
    </form>
  <?php elseif ($two_step_setup): ?>
    <ol class="steps">
      <li>Open an authenticator app on your phone (Google Authenticator, Microsoft Authenticator or similar).</li>
      <li>Add an account by typing this key: <code class="key"><?= e(trim(chunk_split($two_step_setup, 4, ' '))) ?></code> (account name: VARTEC admin, type: time-based).</li>
      <li>Enter the six-digit code the app now shows.</li>
    </ol>
    <form method="post" action="/admin/settings/two-step" class="row">
      <?= csrf_field() ?><input type="hidden" name="action" value="confirm">
      <input type="text" name="code" inputmode="numeric" autocomplete="one-time-code" placeholder="Six-digit code" aria-label="Six-digit code" class="narrow" required>
      <button type="submit" class="btn btn-primary">Turn on</button>
    </form>
    <form method="post" action="/admin/settings/two-step"><?= csrf_field() ?><input type="hidden" name="action" value="cancel"><button type="submit" class="btn btn-quiet btn-small">Cancel</button></form>
  <?php else: ?>
    <p class="muted">Adds a second check when you sign in: a six-digit code from an app on your phone. With it, a stolen password alone cannot open the admin.</p>
    <form method="post" action="/admin/settings/two-step"><?= csrf_field() ?><input type="hidden" name="action" value="start"><button type="submit" class="btn">Set up two-step sign-in</button></form>
  <?php endif; ?>
</section>

<section class="card" id="editors">
  <h2>Editors</h2>
  <p class="muted">Everyone listed here can edit and publish the website.</p>
  <?php foreach ($editors as $name): ?>
  <div class="list-row"><span><strong><?= e($name) ?></strong><?= $name === $user ? ' <small>(you)</small>' : '' ?></span>
    <?php if ($name !== $user): ?><form method="post" action="/admin/settings/editors" data-confirm="Remove this editor? They will no longer be able to sign in."><?= csrf_field() ?><input type="hidden" name="action" value="remove"><input type="hidden" name="username" value="<?= e($name) ?>"><button type="submit" class="btn btn-small btn-quiet">Remove</button></form><?php endif; ?></div>
  <?php endforeach; ?>
  <form method="post" action="/admin/settings/editors" class="grid-2 add-editor">
    <?= csrf_field() ?>
    <label>New editor's username<input type="text" name="username" autocomplete="off" pattern="[a-z0-9._\-]{3,40}" required></label>
    <label>A temporary password for them <small>(at least 10 characters; they must change it at first sign-in)</small><input type="password" name="password" autocomplete="new-password" minlength="10" required></label>
    <div><button type="submit" class="btn">Add editor</button></div>
  </form>
</section>

<section class="card" id="activity">
  <h2>Recent activity</h2>
  <p class="muted">Sign-ins, publishing and account changes. Check this if anything looks unfamiliar.</p>
  <?php foreach ($activity as $entry): ?>
  <div class="list-row"><span><?= e($entry['event']) ?><?= $entry['user'] ? ' <small>by ' . e($entry['user']) . '</small>' : '' ?></span><small><?= e(date('j M Y, H:i', strtotime($entry['at']))) ?> UTC<?= $entry['ip'] ? ' · ' . e($entry['ip']) : '' ?></small></div>
  <?php endforeach; ?>
</section>

<section class="card">
  <h2>Earlier versions</h2>
  <p class="muted">Every time you publish, the version it replaced is kept. You can bring one back at any time.</p>
  <a class="btn" href="/admin/history">See earlier versions</a>
</section>
