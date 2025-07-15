<?php

require_once __DIR__ . '/../models/Message.php';

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
        ]);
    }
}
