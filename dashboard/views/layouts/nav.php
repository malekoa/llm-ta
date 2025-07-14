<style>
  .invert-logo {
  filter: invert(1) hue-rotate(180deg);
  transition: filter 0.3s ease;
}
</style>

<nav 
  x-data="themeNav()" 
  x-init="init()" 
  :class="darkMode ? 'navbar is-dark' : 'navbar is-light'" 
  role="navigation"
>
  <div class="navbar-brand">
    <a class="navbar-item" href="/">
      <img src="/public/logo.svg" alt="" :class="darkMode ? 'invert-logo' : ''">
    </a>
  </div>
  <div class="navbar-menu">
<div class="navbar-end">
  <div class="navbar-item">
    <?php if (!empty($_SESSION["user"])): ?>
      <p>Logged in as <strong><?= htmlspecialchars($_SESSION["user"]) ?></strong></p>
    <?php endif; ?>
  </div>
  <?php if ($_SESSION["admin"] ?? false): ?>
    <div class="navbar-item">
      <div class="buttons">
        <a href="/logout" class="button is-light">Logout</a>
      </div>
    </div>
  <?php else: ?>
    <div class="navbar-item">
      <div class="buttons">
        <a href="/login" class="button is-primary">Login</a>
      </div>
    </div>
  <?php endif; ?>
</div>
  </div>
</nav>

<script>
function themeNav() {
  return {
    darkMode: window.matchMedia('(prefers-color-scheme: dark)').matches,
    init() {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        this.darkMode = e.matches;
      });
    }
  }
}
</script>