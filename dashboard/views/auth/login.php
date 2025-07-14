<section class="section">
  <div class="container" style="max-width: 400px;">
    <h1 class="title">Admin Login</h1>
    <?php if ($error): ?>
      <div class="notification is-danger"><?= htmlspecialchars($error) ?></div>
    <?php endif; ?>
    <form method="POST">
      <input type="hidden" name="csrf_token" value="<?= htmlspecialchars(
          $csrf_token
      ) ?>">
      <div class="field">
        <label class="label">Username</label>
        <div class="control">
          <input class="input" type="text" name="username" required>
        </div>
      </div>
      <div class="field">
        <label class="label">Password</label>
        <div class="control">
          <input class="input" type="password" name="password" required>
        </div>
      </div>
      <div class="control">
        <button class="button is-link">Login</button>
      </div>
    </form>
  </div>
</section>
