<!doctype html>
<html lang="en-GB">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow">
  <title><?= $mode === 'setup' ? 'Set up' : 'Sign in' ?> | VARTEC admin</title>
  <link rel="icon" href="/favicon.ico">
  <link rel="stylesheet" href="/assets/admin.css?v=<?= APP_VERSION ?>">
</head>
<body class="auth">
  <main class="auth-card">
    <div class="brand"><span class="brand-mark">V</span><span><strong>VARTEC</strong><small>Website admin</small></span></div>
    <?php if ($mode === 'change'): ?>
      <h1>Choose your own password</h1>
      <p>Welcome, <?= e($user) ?>. The password you were given was only to get you in. Choose a new one that only you know.</p>
      <?php if ($error): ?><div class="notice notice-error" role="alert"><?= e($error) ?></div><?php endif; ?>
      <form method="post" action="/admin/settings/password">
        <?= csrf_field() ?>
        <label>The password you were given<input type="password" name="current_password" autocomplete="current-password" required autofocus></label>
        <label>Your new password <small>(at least 10 characters)</small><input type="password" name="new_password" autocomplete="new-password" minlength="10" required></label>
        <button type="submit" class="btn btn-primary btn-wide">Save and continue</button>
      </form>
      <form method="post" action="/admin/logout" class="auth-foot"><?= csrf_field() ?><button type="submit" class="btn btn-small btn-quiet">Sign out</button></form>
    </main></body></html>
    <?php return; endif; ?>
    <?php if ($mode === 'code'): ?>
      <h1>Enter your code</h1>
      <p>Open your authenticator app and enter the six-digit code for VARTEC.</p>
      <?php if ($error): ?><div class="notice notice-error" role="alert"><?= e($error) ?></div><?php endif; ?>
      <form method="post" action="/admin/login">
        <?= csrf_field() ?>
        <label>Six-digit code<input type="text" name="code" inputmode="numeric" autocomplete="one-time-code" pattern="[0-9 ]{6,7}" required autofocus></label>
        <button type="submit" class="btn btn-primary btn-wide">Sign in</button>
      </form>
      <p class="auth-foot"><a href="/admin/login">Start again</a> · Lost your phone? Ask another editor to remove your account and add you again.</p>
    </main></body></html>
    <?php return; endif; ?>
    <?php if ($mode === 'setup'): ?>
      <h1>Create the first account</h1>
      <p>To prove you manage this website's hosting, enter the setup code. You will find it in the file <code>setup-code.php</code> inside the <code>vartec-data</code> folder (or <code>data</code> folder) in the hosting File Manager.</p>
    <?php else: ?>
      <h1>Sign in</h1>
      <p>Use your VARTEC admin username and password.</p>
    <?php endif; ?>
    <?php if ($error): ?><div class="notice notice-error" role="alert"><?= e($error) ?></div><?php endif; ?>
    <form method="post" action="<?= $mode === 'setup' ? '/admin/' : '/admin/login' ?>">
      <?= csrf_field() ?>
      <?php if ($mode === 'setup'): ?><label>Setup code<input type="text" name="code" autocomplete="off" required></label><?php endif; ?>
      <label>Username<input type="text" name="username" autocomplete="username" required autofocus></label>
      <label>Password<?php if ($mode === 'setup'): ?> <small>(at least 10 characters)</small><?php endif; ?><input type="password" name="password" autocomplete="<?= $mode === 'setup' ? 'new-password' : 'current-password' ?>" required></label>
      <button type="submit" class="btn btn-primary btn-wide"><?= $mode === 'setup' ? 'Create account' : 'Sign in' ?></button>
    </form>
    <p class="auth-foot"><a href="/">Back to the website</a><?php if ($mode !== 'setup'): ?> · Forgotten your password? Ask another editor to add a new account for you in Settings.<?php endif; ?></p>
  </main>
</body>
</html>
