<?php
/** @var array $content */
$s = $content['settings'];
$c = $content['home']['contact'];
?>
<section class="contact-section" id="contact">
  <div class="shell contact-grid">
    <div class="contact-copy">
      <p class="eyebrow">Contact Us</p>
      <h2><?= e($c['heading']) ?></h2>
      <?php foreach ($c['text'] as $p): ?><?php if (trim($p) !== ''): ?><p><?= e($p) ?></p><?php endif; ?><?php endforeach; ?>
      <dl>
        <div><dt>Phone</dt><dd><a href="tel:<?= e(preg_replace('/[^0-9+]/', '', $s['phone'])) ?>"><?= e($s['phone']) ?></a></dd></div>
        <div><dt>Office hours</dt><dd><?= e($s['office_hours_weekdays']) ?><br><?= e($s['office_hours_weekend']) ?></dd></div>
        <div><dt>Email</dt><dd><a href="mailto:<?= e($s['contact_email']) ?>"><?= e($s['contact_email']) ?></a></dd></div>
      </dl>
    </div>
    <div class="contact-panel">
      <h2><?= e($c['form_heading']) ?></h2>
      <?php /* Posts to the existing send_mail.php with the field names it already expects. */ ?>
      <form method="post" action="/send_mail.php" data-contact-form data-page="<?= e($return_path) ?>">
        <div style="display:none" aria-hidden="true"><input type="text" name="website" tabindex="-1" autocomplete="off"></div>
        <div class="field-row">
          <label>First Name<input type="text" name="firstName" autocomplete="given-name" maxlength="100" required></label>
          <label>Last Name<input type="text" name="lastName" autocomplete="family-name" maxlength="100" required></label>
        </div>
        <label>Email Address<input type="email" name="email" autocomplete="email" maxlength="254" required></label>
        <label>Phone Number<input type="text" name="phone" autocomplete="tel" maxlength="60" required></label>
        <label>Message<textarea name="message" rows="5" maxlength="5000" required></textarea></label>
        <div class="form-errors" data-contact-error hidden>Your message could not be sent. Please try again, or email us directly.</div>
        <button class="button button-dark" type="submit">Submit</button>
      </form>
    </div>
  </div>
</section>
