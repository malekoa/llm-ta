<?php

class Sender
{
    private PDO $pdo;

    public function __construct()
    {
        $this->pdo = Database::getConnection();
    }

    public function exists(string $sender_id): bool
    {
        $stmt = $this->pdo->prepare("SELECT 1 FROM senders WHERE id = ?");
        $stmt->execute([$sender_id]);
        return (bool) $stmt->fetchColumn();
    }
}
