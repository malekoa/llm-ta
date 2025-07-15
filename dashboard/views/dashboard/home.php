<style>
  .hover-grow {
    transition: transform 0.2s ease;
  }

  .hover-grow:hover {
    transform: scale(1.03);
  }
</style>

<section class="section">
  <div class="container">
    <div class="mb-5">
      <h1 class="title is-3">Dashboard</h1>
      <p class="has-text-grey subtitle is-6">
        Overview of recent assistant activity and thread feedback.
      </p>
    </div>

    <div class="columns is-multiline">
      <!-- Card 1: Threads -->
      <div class="column is-4">
        <div class="card hover-grow">
          <a href="/threads" class="is-block card-content">
            <p class="title is-5">📬 View Email Threads</p>
            <p class="has-text-grey subtitle is-6">Browse all conversation threads</p>
            <p class="mt-2 is-size-7 has-text-grey-light">
              <strong><?= $thread_count ?></strong> thread<?= $thread_count === 1 ? '' : 's' ?> created by <strong><?= $unique_senders ?></strong> unique sender<?= $unique_senders === 1 ? '' : 's' ?>.
            </p>
          </a>
        </div>
      </div>

      <!-- Card 2: Placeholder for Insights -->
      <div class="column is-4">
        <div class="card hover-grow">
          <div class="card-content">
            <p class="title is-5">📊 Insights</p>
            <p class="has-text-grey subtitle is-6">Coming soon…</p>
          </div>
        </div>
      </div>

      <!-- Card 3: Placeholder for Settings -->
      <div class="column is-4">
        <div class="card hover-grow">
          <div class="card-content">
            <p class="title is-5">⚙️ Settings</p>
            <p class="has-text-grey subtitle is-6">Coming soon…</p>
          </div>
        </div>
      </div>

    </div>
  </div>
</section>