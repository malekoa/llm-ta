<?php

require_once __DIR__ . '/../models/Message.php';
require_once __DIR__ . '/../models/Vote.php';

class DashboardController extends Controller
{
    public function home()
    {
        $this->requireLogin();

        $msg = new Message();
        $thread_count = $msg->countThreads();
        $unique_senders = $msg->countUniqueSenders();

        $this->render("dashboard/home", [
            "title" => "Dashboard",
            "thread_count" => $thread_count,
            "unique_senders" => $unique_senders
        ]);
    }

    public function threadList()
    {
        $this->requireLogin();

        $msg = new Message();
        $threads = $msg->getAllThreads();

        $this->render("dashboard/thread_list", [
            "title" => "All Threads",
            "threads" => $threads
        ]);
    }

    public function threadView()
    {
        $csrf_token = $this->generate_csrf_token();

        $thread_id = $_GET["thread_id"] ?? null;
        $message_id = $_GET["message_id"] ?? null;
        $sender_id = $_GET["sender_id"] ?? null;

        $vote = null;
        $can_vote = false;

        if (!$thread_id) {
            echo "Missing thread ID.";
            return;
        }

        $msg = new Message();
        $messages = $msg->getMessagesByThread($thread_id);

        if (!$messages) {
            echo "Thread not found.";
            return;
        }

        // Validate sender and assign can_vote
        if ($sender_id && $msg->threadExistsForSender($thread_id, $sender_id)) {
            $can_vote = true;
            // Only allow vote if can_vote is true
            $vote_param = $_GET["vote"] ?? null;
            if (in_array($vote_param, ["up", "down"], true)) {
                $vote = $vote_param;
            }
        }

        $this->render("dashboard/thread", [
            "title" => "Thread View",
            "messages" => $messages,
            "thread_id" => $thread_id,
            "message_id" => $message_id,
            "vote" => $vote,
            "sender_id" => $sender_id,
            "can_vote" => $can_vote,
            "csrf_token" => $csrf_token
        ]);
    }

    public function submitVote()
    {
        $this->verify_csrf_token_or_die();

        $message_id = $_POST["message_id"] ?? null;
        $vote = $_POST["vote"] ?? null;
        $sender_id = $_POST["sender_id"] ?? null;

        if (!$message_id || !$sender_id) {
            http_response_code(400);
            echo json_encode(["error" => "Missing parameters."]);
            return;
        }

        $msg = new Message();
        $thread_id = $msg->getThreadIdByMessageId($message_id);
        if (!$thread_id || !$msg->threadExistsForSender($thread_id, $sender_id)) {
            http_response_code(403);
            echo json_encode(["error" => "Unauthorized."]);
            return;
        }

        $vote_model = new Vote();

        if ($vote === '') {
            $vote_model->remove($message_id);
        } elseif (in_array($vote, ["up", "down"], true)) {
            $vote_model->submit($message_id, $vote);
        } else {
            http_response_code(400);
            echo json_encode(["error" => "Invalid vote."]);
            return;
        }

        echo json_encode(["success" => true]);
    }

    public function feedbackView()
    {
        $message_id = $_GET["message_id"] ?? null;
        $vote = $_GET["vote"] ?? null;

        if (!$message_id || !in_array($vote, ['up', 'down'])) {
            echo "Invalid feedback link.";
            return;
        }

        $msg = new Message();
        $message = $msg->getMessageById($message_id);

        if (!$message) {
            echo "Message not found.";
            return;
        }

        // Store the vote (overwrite if exists)
        $voteModel = new Vote();
        $voteModel->submit($message_id, $vote);

        // Render confirmation view
        $this->render("dashboard/feedback_confirmation", [
            "vote" => $vote,
            "message_id" => $message["id"],
            "thread_id" => $message["thread_id"]
        ]);
    }
}
