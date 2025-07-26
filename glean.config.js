/** @type {import('./src/config').GlnConfig} */
module.exports = {
  "gitignore": true,
  "includePatterns": [
    "**/*.py",
    "**/*.php"
  ],
  "blocks": {
    "dashboard": [
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
      "dashboard/models/Message.php",
      "dashboard/models/Sender.php",
      "dashboard/models/Vote.php",
      "dashboard/views/auth/login.php",
      "dashboard/views/dashboard/home.php",
      "dashboard/views/dashboard/partials/comment_block.php",
      "dashboard/views/dashboard/partials/feedback_block.php",
      "dashboard/views/dashboard/partials/message.php",
      "dashboard/views/dashboard/thread.php",
      "dashboard/views/dashboard/thread_list.php",
      "dashboard/views/layouts/footer.php",
      "dashboard/views/layouts/head.php",
      "dashboard/views/layouts/nav.php",
      "shared/schema.sql",
      "dashboard/views/dashboard/feedback.php"
    ],
    "bot": [
      "bot/config.py",
      "bot/database.py",
      "bot/gmail_client.py",
      "bot/main.py",
      "bot/message_parser.py",
      "bot/responder.py",
      "bot/__init__.py",
      "bot/handler.py",
      "shared/schema.sql"
    ]
  }
};
