/** @type {import('./src/config').GlnConfig} */
module.exports = {
  "gitignore": true,
  "includePatterns": [
    "**/*.py",
    "**/*.php"
  ],
  "blocks": {
    "bot": [
      "bot/database.py",
      "bot/gmail_client.py",
      "bot/main.py",
      "bot/responder.py",
      "shared/schema.sql"
    ],
    "dashboard": [
      "shared/schema.sql",
      "dashboard/config.php",
      "dashboard/controllers/AuthController.php",
      "dashboard/controllers/DashboardController.php",
      "dashboard/core/Controller.php",
      "dashboard/core/Database.php",
      "dashboard/core/Router.php",
      "dashboard/core/View.php",
      "dashboard/core/debug.php",
      "dashboard/core/setup.php",
      "dashboard/index.php",
      "dashboard/models/Comment.php",
      "dashboard/models/Feedback.php",
      "dashboard/models/Message.php",
      "dashboard/models/Sender.php",
      "dashboard/views/auth/login.php",
      "dashboard/views/dashboard/home.php",
      "dashboard/views/dashboard/partials/comment_block.php",
      "dashboard/views/dashboard/partials/feedback_block.php",
      "dashboard/views/dashboard/partials/message.php",
      "dashboard/views/dashboard/thread.php",
      "dashboard/views/dashboard/thread_list.php",
      "dashboard/views/layouts/footer.php",
      "dashboard/views/layouts/head.php",
      "dashboard/views/layouts/nav.php"
    ]
  }
};
