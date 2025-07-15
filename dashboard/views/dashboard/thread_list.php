<style>
    .list-item:hover {
        background-color: #fafafa;
        transition: background-color 0.2s ease;
    }
</style>
<section class="section">
    <div class="container">
        <h1 class="title">All Threads</h1>

        <div class="list">
            <?php foreach ($threads as $thread): ?>
                <?php
                $short_hash = substr($thread["sender_id"] ?? "", -8);
                $msg_count = (int) $thread["message_count"];
                ?>
                <a
                    class="is-flex is-justify-content-space-between is-align-items-center px-4 py-3 list-item"
                    href="/thread?thread_id=<?= htmlspecialchars($thread["thread_id"]) ?>"
                    style="border-bottom: 1px solid #eaeaea;">

                    <div>
                        <div class="has-text-weight-medium">
                            <?= htmlspecialchars($thread["thread_id"]) ?>
                        </div>
                        <div class="mt-1 is-size-7 has-text-grey">
                            👤 <?= $short_hash ? "...$short_hash" : "Unknown sender" ?> ·
                            📨 <?= $msg_count ?> message<?= $msg_count === 1 ? '' : 's' ?>
                        </div>
                    </div>

                    <div class="is-size-7 has-text-grey-light">
                        <?= date("Y-m-d H:i", $thread["latest_time"]) ?>
                    </div>
                </a>
            <?php endforeach; ?>
        </div>
    </div>
</section>