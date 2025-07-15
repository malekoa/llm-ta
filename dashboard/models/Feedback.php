<?php

class Feedback
{
    private PDO $pdo;

    public function __construct()
    {
        $this->pdo = Database::getConnection();
    }

    public function existsForMessage(string $message_id): bool
    {
        $stmt = $this->pdo->prepare("SELECT 1 FROM feedback WHERE message_id = ?");
        $stmt->execute([$message_id]);
        return (bool) $stmt->fetchColumn();
    }

    public function submit(string $message_id, string $vote, string $comment): void
    {
        $stmt = $this->pdo->prepare("
            INSERT INTO feedback (message_id, vote, comment, submitted_at)
            VALUES (?, ?, ?, ?)
        ");
        $stmt->execute([
            $message_id,
            $vote,
            $comment,
            time()
        ]);
    }
}
