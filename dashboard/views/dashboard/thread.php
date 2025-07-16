<style>
    .message-body p {
        word-break: break-word;
        white-space: pre-wrap;
    }

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
            <?php include __DIR__ . '/partials/message.php'; ?>
        <?php endforeach; ?>

        <div class="mt-6 has-text-grey has-text-centered">
            <p>— End of thread —</p>
        </div>
    </div>
</section>

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
