<?php

class Comment
{
    private $pdo;

    public function __construct()
    {
        $this->pdo = Database::getConnection();
    }

    public function getByMessageId($message_id)
    {
        $stmt = $this->pdo->prepare("SELECT * FROM comments WHERE message_id = ? ORDER BY timestamp ASC");
        $stmt->execute([$message_id]);
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function add($message_id, $author, $content)
    {
        $stmt = $this->pdo->prepare("INSERT INTO comments (message_id, author, content, timestamp) VALUES (?, ?, ?, ?)");
        return $stmt->execute([$message_id, $author, $content, time()]);
    }

    public function delete($comment_id)
    {
        $stmt = $this->pdo->prepare("DELETE FROM comments WHERE id = ?");
        return $stmt->execute([$comment_id]);
    }
}
