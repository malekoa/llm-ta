/** @type {import('./src/config').GlnConfig} */
module.exports = {
  "gitignore": true,
  "includePatterns": [
    "**/*.py"
  ],
  "blocks": {
    "dashboard": [
      "dashboard/config.php",
      "dashboard/controllers/AuthController.php",
      "dashboard/controllers/DashboardController.php",
      "dashboard/core/Controller.php",
      "dashboard/core/Router.php",
      "dashboard/core/View.php",
      "dashboard/core/debug.php",
      "dashboard/index.php",
      "dashboard/views/auth/login.php",
      "dashboard/views/dashboard/home.php",
      "dashboard/views/layouts/footer.php",
      "dashboard/views/layouts/head.php",
      "dashboard/views/layouts/nav.php"
    ]
  }
};
