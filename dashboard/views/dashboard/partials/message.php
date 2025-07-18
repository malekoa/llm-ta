<?php

/** @var array $msg */
/** @var string|null $message_id */
/** @var string|null $vote */
/** @var string|null $sender_id */
/** @var bool $can_vote */
/** @var string $csrf_token */
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
        senderId: <?= json_encode($sender_id ?? "") ?>,
        csrfToken: <?= json_encode($csrf_token) ?>
    })'>
    <div class="is-justify-content-space-between message-header">
        <div>
            <p><?= $isBot ? "AutoTA" : "User" ?></p>
            <small><?= date("Y-m-d H:i", $msg["timestamp"]) ?></small>
        </div>

        <?php if ($msgId): ?>
            <button
                class="button is-small is-white is-light"
                onclick="copyLink('<?= $msg['thread_id'] ?>', '<?= $msgId ?>', this)">
                🔗 Get Link
            </button>
        <?php endif; ?>
    </div>


    <div class="message-body">
        <p><strong><?= htmlspecialchars($msg["subject"]) ?></strong></p>
        <p><?= htmlspecialchars($msg["body"]) ?></p>
    </div>
</article>