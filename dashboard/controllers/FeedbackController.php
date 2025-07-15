<?php

require_once __DIR__ . '/../models/Message.php';
require_once __DIR__ . '/../models/Feedback.php';

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

        $feedback = new Feedback();
        $message = new Message();

        if ($feedback->existsForMessage($message_id)) {
            http_response_code(409); // Conflict
            echo json_encode(["error" => "Feedback already submitted for this message."]);
            return;
        }

        $thread_id = $message->getThreadIdByMessageId($message_id);
        if (!$thread_id || !$message->threadExistsForSender($thread_id, $sender_id)) {
            http_response_code(403);
            echo json_encode(["error" => "Unauthorized or mismatched sender."]);
            return;
        }

        $feedback->submit($message_id, $vote, $comment);

        echo json_encode(["success" => true]);
    }
}
