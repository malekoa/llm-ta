<?php

class Message
{
    private PDO $pdo;

    public function __construct()
    {
        $this->pdo = Database::getConnection();
    }

    public function countThreads(): int
    {
        $stmt = $this->pdo->query("SELECT COUNT(DISTINCT thread_id) FROM messages");
        return (int) $stmt->fetchColumn();
    }

    public function countUniqueSenders(): int
    {
        $stmt = $this->pdo->query("SELECT COUNT(DISTINCT sender_id) FROM messages WHERE is_from_bot = 0");
        return (int) $stmt->fetchColumn();
    }

    public function getAllThreads(): array
    {
        $stmt = $this->pdo->query("
            SELECT 
                thread_id,
                MAX(timestamp) as latest_time,
                COUNT(*) as message_count,
                (
                    SELECT sender_id 
                    FROM messages 
                    WHERE messages.thread_id = outer.thread_id AND is_from_bot = 0 
                    ORDER BY timestamp ASC 
                    LIMIT 1
                ) as sender_id
            FROM messages AS outer
            GROUP BY thread_id
            ORDER BY latest_time DESC
        ");
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function getMessagesByThread(string $thread_id): array
    {
        $stmt = $this->pdo->prepare("SELECT * FROM messages WHERE thread_id = ? ORDER BY timestamp ASC");
        $stmt->execute([$thread_id]);
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function threadExistsForSender(string $thread_id, string $sender_id): bool
    {
        $stmt = $this->pdo->prepare("
            SELECT 1
            FROM messages
            WHERE thread_id = ? AND is_from_bot = 0 AND sender_id = ?
            LIMIT 1
        ");
        $stmt->execute([$thread_id, $sender_id]);
        return (bool) $stmt->fetchColumn();
    }

    public function getThreadIdByMessageId(string $message_id): ?string
    {
        $stmt = $this->pdo->prepare("SELECT thread_id FROM messages WHERE id = ?");
        $stmt->execute([$message_id]);
        return $stmt->fetchColumn() ?: null;
    }
}
