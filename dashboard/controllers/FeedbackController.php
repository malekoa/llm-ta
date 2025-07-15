<?php

class FeedbackController extends Controller
{
    public function submit()
    {
        $message_id = $_POST["message_id"] ?? null;
        $vote = $_POST["vote"] ?? null;
        $comment = $_POST["comment"] ?? "";
        $sender_id = $_POST["sender_id"] ?? null;

        if (!$message_id || !in_array($vote, ["up", "down"]) || !$sender_id) {
            http_response_code(400);
            echo json_encode(["error" => "Missing or invalid parameters."]);
            return;
        }

        $pdo = new PDO("sqlite:" . DB_PATH);

        $stmt = $pdo->prepare("SELECT 1 FROM feedback WHERE message_id = ?");
        $stmt->execute([$message_id]);
        $alreadyExists = $stmt->fetchColumn();

        if ($alreadyExists) {
            http_response_code(409); // Conflict
            echo json_encode(["error" => "Feedback already submitted for this message."]);
            return;
        }

        // Make sure this sender_id was part of the thread (as a user)
        $stmt = $pdo->prepare("
            SELECT 1
            FROM messages
            WHERE thread_id = (
                SELECT thread_id FROM messages WHERE id = ?
            ) AND is_from_bot = 0 AND sender_id = ?
            LIMIT 1
        ");
        $stmt->execute([$message_id, $sender_id]);
        $valid = $stmt->fetchColumn();

        if (!$valid) {
            http_response_code(403);
            echo json_encode(["error" => "Unauthorized or mismatched sender."]);
            return;
        }

        // Store feedback
        $stmt = $pdo->prepare("
            INSERT INTO feedback (message_id, vote, comment, submitted_at)
            VALUES (?, ?, ?, ?)
        ");
        $stmt->execute([
            $message_id,
            $vote,
            $comment,
            time()
        ]);

        echo json_encode(["success" => true]);
    }
}
