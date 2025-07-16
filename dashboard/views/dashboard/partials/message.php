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
        senderId: <?= json_encode($sender_id ?? "") ?>
    })'>
    <div class="message-header">
        <p><?= $isBot ? "TA Bot" : "User" ?></p>
        <small><?= date("Y-m-d H:i", $msg["timestamp"]) ?></small>
    </div>

    <div class="message-body">
        <p><strong><?= htmlspecialchars($msg["subject"]) ?></strong></p>
        <p><?= htmlspecialchars($msg["body"]) ?></p>

        <?php if ($isBot && ($can_vote || ($_SESSION["admin"] ?? false))): ?>
            <?php include __DIR__ . '/comment_block.php'; ?>
        <?php endif; ?>

        <?php if ($isBot && ($can_vote || ($_SESSION["admin"] ?? false))): ?>
            <?php include __DIR__ . '/feedback_block.php'; ?>
        <?php endif; ?>

    </div>
</article>