<div class="mt-5">
    <p class="mb-3 is-size-6 has-text-weight-semibold">💬 Comments</p>

    <div class="list is-hoverable">
        <?php foreach ($msg["comments"] as $c): ?>
            <div class="is-flex is-justify-content-space-between is-align-items-center mb-3 px-4 py-3 box is-light">
                <div class="is-flex-grow-1 mr-4 is-size-6 has-text-left">
                    <?= nl2br(htmlspecialchars($c["content"])) ?>
                </div>
                <div class="is-flex is-flex-shrink-0 is-align-items-center is-size-7 has-text-grey">
                    <?php
                    $author_display = "Anonymous";
                    if (str_starts_with($c["author"], "sender:")) {
                        $short = substr($c["author"], -8);
                        $author_display = "<strong>..." . htmlspecialchars($short) . "</strong>";
                    } elseif ($c["author"] === "admin") {
                        $author_display = "Admin";
                    } else {
                        $author_display = htmlspecialchars($c["author"]);
                    }
                    ?>
                    <span class="mr-3">Posted by <?= $author_display ?></span>

                    <?php if ($_SESSION["admin"] ?? false): ?>
                        <form method="POST" class="ml-2">
                            <input type="hidden" name="csrf_token" value="<?= htmlspecialchars($csrf_token) ?>">
                            <input type="hidden" name="comment_id" value="<?= htmlspecialchars($c["id"]) ?>">
                            <button
                                type="submit"
                                formaction="/comment/delete"
                                class="has-text-danger button is-white is-small"
                                onclick="return confirm('Delete this comment?')">
                                delete
                            </button>
                        </form>
                    <?php endif; ?>
                </div>
            </div>
        <?php endforeach; ?>
    </div>

    <?php if ($can_vote): ?>
        <?php $sender_label = $sender_id ? "<strong>..." . htmlspecialchars(substr($sender_id, -8)) . "</strong>" : "Anonymous"; ?>

        <form method="POST" class="mt-4">
            <input type="hidden" name="csrf_token" value="<?= htmlspecialchars($csrf_token) ?>">
            <input type="hidden" name="message_id" value="<?= htmlspecialchars($msg["id"]) ?>">
            <input type="hidden" name="sender_id" value="<?= htmlspecialchars($sender_id ?? '') ?>">

            <div class="mb-2 field">
                <p class="is-size-7 has-text-grey">Commenting as <?= $sender_label ?></p>
            </div>

            <div class="field">
                <div class="control">
                    <textarea class="textarea is-small" name="content" placeholder="Add a comment…" required></textarea>
                </div>
            </div>

            <div class="is-grouped is-justify-content-flex-end field">
                <div class="control">
                    <button type="submit" formaction="/comment" class="button is-link is-small">Submit</button>
                </div>
            </div>
        </form>
    <?php endif; ?>
</div>