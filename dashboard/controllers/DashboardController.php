<?php

require_once __DIR__ . '/../models/Message.php';
require_once __DIR__ . '/../models/Comment.php';

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
        $vote = $_GET["vote"] ?? null;
        $sender_id = $_GET["sender_id"] ?? null;

        if (!$thread_id) {
            echo "Missing thread ID.";
            return;
        }

        $msg = new Message();
        $messages = $msg->getMessagesByThread($thread_id);


        // After getting $messages
        $comment_model = new Comment();
        foreach ($messages as &$message) {
            $message["comments"] = $comment_model->getByMessageId($message["id"]);
        }



        if (!$messages) {
            echo "Thread not found.";
            return;
        }

        $can_vote = false;
        if ($sender_id) {
            $can_vote = $msg->threadExistsForSender($thread_id, $sender_id);
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

    public function postComment()
    {
        $message_id = $_POST["message_id"] ?? null;
        $content = trim($_POST["content"] ?? "");
        $sender_id = $_POST["sender_id"] ?? null;

        if (!$message_id || !$content || !$sender_id) {
            http_response_code(400);
            echo "Missing content, message ID, or sender ID.";
            return;
        }

        // Only allow if the sender_id is valid for the thread
        $msg = new Message();
        $thread_id = $msg->getThreadIdByMessageId($message_id);
        if (!$msg->threadExistsForSender($thread_id, $sender_id)) {
            http_response_code(403);
            echo "Not authorized to comment.";
            return;
        }

        $author = "sender:$sender_id";

        $comment_model = new Comment();
        $comment_model->add($message_id, $author, $content);

        header("Location: " . $_SERVER["HTTP_REFERER"]);
    }


    public function deleteComment()
    {
        $this->verify_csrf_token_or_die();

        $comment_id = $_POST["comment_id"] ?? null;

        if (!$comment_id) {
            http_response_code(400);
            echo "Missing comment ID.";
            return;
        }

        if (!($_SESSION["admin"] ?? false)) {
            http_response_code(403);
            echo "Unauthorized.";
            return;
        }

        $comment_model = new Comment();
        $comment_model->delete($comment_id);

        header("Location: " . $_SERVER["HTTP_REFERER"]);
    }
}
