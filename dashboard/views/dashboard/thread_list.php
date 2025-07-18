<section class="section" x-data="{ groupBySender: false }">
    <div class="container">
        <h1 class="title">All Threads</h1>

        <!-- Group by Sender Toggle -->
        <div class="mb-5 field">
            <label class="checkbox">
                <input type="checkbox" x-model="groupBySender">
                Group by sender
            </label>
        </div>

        <!-- Thread List -->
        <template x-if="!groupBySender">
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
        </template>

        <template x-if="groupBySender">
            <div class="list">
                <?php
                $grouped = [];
                foreach ($threads as $thread) {
                    $sender = $thread["sender_id"] ?? "Unknown";
                    $grouped[$sender][] = $thread;
                }
                ksort($grouped);
                ?>

                <?php foreach ($grouped as $sender_id => $sender_threads): ?>
                    <div class="mb-4 box">
                        <p class="mb-2 has-text-weight-bold">
                            👤 <?= $sender_id === "Unknown" ? "Unknown sender" : "..." . substr($sender_id, -8) ?>
                        </p>

                        <?php foreach ($sender_threads as $thread): ?>
                            <a
                                class="is-flex is-justify-content-space-between is-align-items-center px-4 py-3 list-item"
                                href="/thread?thread_id=<?= htmlspecialchars($thread["thread_id"]) ?>"
                                style="border-bottom: 1px solid #eaeaea;">
                                <div>
                                    <div class="has-text-weight-medium">
                                        <?= htmlspecialchars($thread["thread_id"]) ?>
                                    </div>
                                    <div class="mt-1 is-size-7 has-text-grey">
                                        📨 <?= $thread["message_count"] ?> message<?= $thread["message_count"] === 1 ? '' : 's' ?>
                                    </div>
                                </div>

                                <div class="is-size-7 has-text-grey-light">
                                    <?= date("Y-m-d H:i", $thread["latest_time"]) ?>
                                </div>
                            </a>
                        <?php endforeach; ?>
                    </div>
                <?php endforeach; ?>
            </div>
        </template>
    </div>
</section>
