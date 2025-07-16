<?php

class Vote
{
    private PDO $pdo;

    public function __construct()
    {
        $this->pdo = Database::getConnection();
    }

    public function existsForMessage(string $message_id): bool
    {
        $stmt = $this->pdo->prepare("SELECT 1 FROM votes WHERE message_id = ?");
        $stmt->execute([$message_id]);
        return (bool) $stmt->fetchColumn();
    }

    public function submit(string $message_id, string $vote): void
    {
        $stmt = $this->pdo->prepare("
            INSERT INTO votes (message_id, vote)
            VALUES (?, ?)
            ON CONFLICT(message_id) DO UPDATE SET vote = excluded.vote
        ");
        $stmt->execute([$message_id, $vote]);
    }
}