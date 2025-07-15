<style>
    .message-body p {
        word-break: break-word;
        white-space: pre-wrap;
    }
</style>

<script>
    function feedbackWidget({
        vote = null,
        messageId,
        senderHash
    }) {
        // Check for URL-based vote override
        const params = new URLSearchParams(window.location.search);
        const urlVote = params.get("vote");
        const urlMessageId = params.get("message_id");

        if (!vote && urlMessageId === messageId && (urlVote === "up" || urlVote === "down")) {
            vote = urlVote;
        }

        return {
            vote,
            comment: '',
            submitting: false,
            submitted: false,
            senderHash,
            submitFeedback() {
                if (!this.vote) return;

                this.submitting = true;

                fetch('/feedback', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: new URLSearchParams({
                        message_id: messageId,
                        vote: this.vote,
                        comment: this.comment,
                        sender_hash: this.senderHash
                    })
                }).then(res => {
                    this.submitting = false;
                    if (res.status === 409) {
                        this.submitted = true; // Already submitted
                    } else if (res.ok) {
                        this.submitted = true;
                    } else {
                        alert('Failed to submit feedback.');
                    }
                }).catch(err => {
                    console.error(err);
                    alert('Failed to submit feedback.');
                    this.submitting = false;
                });
            }
        };
    }
</script>

<section class="section">
    <div class="container">
        <div class="mb-4 columns is-vcentered is-mobile">
            <div class="column">
                <h1 class="mb-0 title">Conversation Thread</h1>
            </div>
            <div class="column is-narrow">
                <button
                    class="button is-small is-link is-light"
                    onclick="copyThreadLink('<?= $thread_id ?>', this)">
                    🔗 Copy Thread Link
                </button>
            </div>
        </div>

        <?php foreach ($messages as $msg): ?>
            <?php
            $msgId = $msg['id'] ?? null;
            $isBot = $msg["is_from_bot"];
            $isTargeted = $msgId && $message_id === $msgId;
            $initialVote = $isTargeted ? $vote : null;
            ?>
            <article
                <?= $msgId ? 'id="' . htmlspecialchars($msgId) . '"' : '' ?>
                class="message <?= $isBot ? "is-info" : "is-dark" ?>"
                x-data='feedbackWidget({
    vote: <?= json_encode($initialVote) ?>,
    messageId: <?= json_encode($msgId) ?>,
    senderHash: <?= json_encode($sender_hash ?? "") ?>
})'>
                <div class="message-header">
                    <p><?= $isBot ? "TA Bot" : "User" ?></p>
                    <small><?= date("Y-m-d H:i", $msg["timestamp"]) ?></small>
                </div>

                <div class="message-body">
                    <p><strong><?= htmlspecialchars($msg["subject"]) ?></strong></p>
                    <p><?= (htmlspecialchars($msg["body"])) ?></p>

                    <div class="is-flex is-flex-wrap-wrap is-align-items-center mt-3" style="gap: 0.5rem;">
                        <?php if ($isBot): ?>
                            <?php if ($can_vote): ?>
                                <button
                                    class="button is-small"
                                    :class="vote === 'up' ? 'is-success' : 'is-light'"
                                    @click="vote = 'up'">👍 Upvote</button>

                                <button
                                    class="button is-small"
                                    :class="vote === 'down' ? 'is-danger' : 'is-light'"
                                    @click="vote = 'down'">👎 Downvote</button>
                            <?php else: ?>
                                <button class="button is-small is-light" disabled>👍 Upvote</button>
                                <button class="button is-small is-light" disabled>👎 Downvote</button>
                            <?php endif; ?>
                        <?php endif; ?>

                        <!-- Always show the Get Link button -->
                        <button
                            class="button is-small is-link is-light"
                            onclick="copyLink('<?= $thread_id ?>', '<?= $msgId ?>', this)">
                            🔗 Get Link
                        </button>
                    </div>

                    <?php if ($isBot): ?>
                        <div x-show="vote" x-transition>
                            <template x-if="!submitted">
                                <form class="mt-3" @submit.prevent="submitFeedback">
                                    <div class="field">
                                        <label class="label">Optional comment:</label>
                                        <div class="control">
                                            <textarea class="textarea" x-model="comment" placeholder="Your feedback..."></textarea>
                                        </div>
                                    </div>
                                    <div class="is-grouped field">
                                        <div class="control">
                                            <button class="button is-link" type="submit" x-bind:disabled="submitting">
                                                <span x-show="submitting">Submitting…</span>
                                                <span x-show="!submitting">Submit Feedback</span>
                                            </button>
                                        </div>
                                    </div>
                                </form>
                            </template>

                            <template x-if="submitted">
                                <div class="mt-3 notification is-success">
                                    ✅ Thank you for your feedback!
                                </div>
                            </template>
                        </div>
                    <?php endif; ?>
                </div>
            </article>
        <?php endforeach; ?>
        <div class="mt-6 has-text-grey has-text-centered">
            <p>— End of thread —</p>
        </div>
    </div>
</section>

<script>
    window.addEventListener("load", () => {
        const params = new URLSearchParams(window.location.search);
        const messageId = params.get("message_id");

        if (messageId) {
            const el = document.getElementById(messageId);
            if (el) {
                el.scrollIntoView({
                    behavior: "smooth",
                    block: "center"
                });
                el.classList.add("highlight-ring");
            }
        }
    });
</script>

<style>
    .highlight-ring {
        position: relative;
        animation: ring-pulse 2s ease-out infinite;
        box-shadow: 0 0 0 4px rgba(72, 138, 255, 0.6);
        border-radius: 6px;
        transition: box-shadow 0.3s ease;
    }

    @keyframes ring-pulse {
        0% {
            box-shadow: 0 0 0 4px rgba(72, 138, 255, 0.8);
        }

        70% {
            box-shadow: 0 0 0 10px rgba(72, 138, 255, 0);
        }

        100% {
            box-shadow: 0 0 0 4px rgba(72, 138, 255, 0);
        }
    }
</style>

<script>
    function copyLink(threadId, messageId, btn) {
        const url = `${window.location.origin}/thread?thread_id=${encodeURIComponent(threadId)}&message_id=${encodeURIComponent(messageId)}`;
        navigator.clipboard.writeText(url).then(() => {
            btn.classList.add('is-success');
            btn.textContent = "✅ Link copied!";
            setTimeout(() => {
                btn.classList.remove('is-success');
                btn.textContent = "🔗 Get Link";
            }, 2000);
        }).catch(err => {
            console.error("Failed to copy link:", err);
            alert("Copy failed. Try again.");
        });
    }

    window.addEventListener("load", () => {
        const params = new URLSearchParams(window.location.search);
        const messageId = params.get("message_id");

        if (messageId) {
            const el = document.getElementById(messageId);
            if (el) {
                el.scrollIntoView({
                    behavior: "smooth",
                    block: "center"
                });
                el.classList.add("highlight-ring");
            }
        }
    });

    function copyThreadLink(threadId, btn) {
        const url = `${window.location.origin}/thread?thread_id=${encodeURIComponent(threadId)}`;
        navigator.clipboard.writeText(url).then(() => {
            btn.classList.add('is-success');
            btn.textContent = "✅ Link copied!";
            setTimeout(() => {
                btn.classList.remove('is-success');
                btn.textContent = "🔗 Copy Thread Link";
            }, 2000);
        }).catch(err => {
            console.error("Failed to copy thread link:", err);
            alert("Copy failed. Try again.");
        });
    }
</script>