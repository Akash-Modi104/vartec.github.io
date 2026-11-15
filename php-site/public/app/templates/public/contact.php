<?php
/** @var array $content */
$s = $content['settings'];
$c = $content['home']['contact'];
$w = fn (string $key): string => e(wording($content, $key));
?>
<section class="contact-section" id="contact">
  <div class="shell contact-grid">
    <div class="contact-copy" data-reveal>
      <p class="eyebrow"><?= $w('label_contact') ?></p>
      <h2><?= e($c['heading']) ?></h2>
      <?php foreach ($c['text'] as $p): ?><?php if (trim($p) !== ''): ?><p><?= e($p) ?></p><?php endif; ?><?php endforeach; ?>
      <dl>
        <div><span class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg></span><dt><?= $w('contact_phone') ?></dt><dd><a href="tel:<?= e(preg_replace('/[^0-9+]/', '', $s['phone'])) ?>"><?= e($s['phone']) ?></a></dd></div>
        <div><span class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="3"/><path d="m3 7 9 6 9-6"/></svg></span><dt><?= $w('contact_email') ?></dt><dd><a href="mailto:<?= e($s['contact_email']) ?>"><?= e($s['contact_email']) ?></a></dd></div>
        <div><span class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg></span><dt><?= $w('contact_hours') ?></dt><dd><?= e($s['office_hours_weekdays']) ?><br><?= e($s['office_hours_weekend']) ?></dd></div>
      </dl>
    </div>
    <div class="contact-panel" data-reveal>
      <h2><?= e($c['form_heading']) ?></h2>
      <?php /* Posts to the existing send_mail.php with the field names it already expects. */ ?>
      <form method="post" action="/send_mail.php" data-contact-form data-page="<?= e($return_path) ?>" data-thanks="<?= $w('form_thanks') ?>">
        <div style="display:none" aria-hidden="true"><input type="text" name="website" tabindex="-1" autocomplete="off"></div>
        <div class="field-row">
          <label><?= $w('form_first') ?><input type="text" name="firstName" autocomplete="given-name" maxlength="100" required></label>
          <label><?= $w('form_last') ?><input type="text" name="lastName" autocomplete="family-name" maxlength="100" required></label>
        </div>
        <label><?= $w('form_email') ?><input type="email" name="email" autocomplete="email" maxlength="254" required></label>
        <label><?= $w('form_phone') ?><input type="tel" inputmode="tel" name="phone" autocomplete="tel" maxlength="60" required></label>
        <label><?= $w('form_message') ?><textarea name="message" rows="5" maxlength="5000" required></textarea></label>
        <div class="form-errors" data-contact-error hidden><?= $w('form_error') ?></div>
        <button class="button" type="submit"><?= $w('btn_send') ?> <span class="arrow" aria-hidden="true">→</span></button>
      </form>
    </div>
  </div>
</section>
