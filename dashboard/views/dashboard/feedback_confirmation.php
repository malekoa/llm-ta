<section class="section">
  <div class="container" style="max-width: 600px;">
    <article class="message is-info">
      <div class="message-header">
        <p>Feedback Recorded</p>
      </div>
      <div class="message-body">
        <p>✅ Thank you! Your <strong><?= htmlspecialchars($vote) ?></strong> vote has been recorded.</p>

        <?php if (!empty($thread_id) && !empty($message_id)): ?>
          <p class="mt-3">
            <a class="button is-small is-link is-light" href="/thread?thread_id=<?= htmlspecialchars($thread_id) ?>&message_id=<?= htmlspecialchars($message_id) ?>">
              🔗 View this thread
            </a>
          </p>
        <?php endif; ?>
      </div>
    </article>
  </div>
</section>
