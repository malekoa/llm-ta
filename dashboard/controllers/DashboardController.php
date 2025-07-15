<?php

class DashboardController extends Controller
{
    public function home()
    {
        $this->requireLogin();

        $pdo = new PDO("sqlite:" . DB_PATH);

        // Count threads
        $stmt = $pdo->query("SELECT COUNT(DISTINCT thread_id) FROM messages");
        $thread_count = (int) $stmt->fetchColumn();

        // Count unique student senders
        $stmt = $pdo->query("SELECT COUNT(DISTINCT sender_id) FROM messages WHERE is_from_bot = 0");
        $unique_senders = (int) $stmt->fetchColumn();


        $this->render("dashboard/home", [
            "title" => "Dashboard",
            "thread_count" => $thread_count,
            "unique_senders" => $unique_senders
        ]);
    }

    public function thread()
    {
        $thread_id = $_GET["thread_id"] ?? null;
        $message_id = $_GET["message_id"] ?? null;
        $vote = $_GET["vote"] ?? null;
        $sender_id = $_GET["sender_id"] ?? null;

        $pdo = new PDO("sqlite:" . DB_PATH);

        // Case 1: show a specific thread
        if ($thread_id) {
            $stmt = $pdo->prepare("SELECT * FROM messages WHERE thread_id = ? ORDER BY timestamp ASC");
            $stmt->execute([$thread_id]);
            $messages = $stmt->fetchAll(PDO::FETCH_ASSOC);

            if (!$messages) {
                echo "Thread not found.";
                return;
            }

            // Check if the sender_id exists for this thread
            $can_vote = false;
            if ($sender_id) {
                $stmt = $pdo->prepare("SELECT 1 FROM messages WHERE thread_id = ? AND sender_id = ? LIMIT 1");
                $stmt->execute([$thread_id, $sender_id]);
                $can_vote = (bool) $stmt->fetchColumn();
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
            return;
        }

        // Case 2: show thread list only if logged in
        if (!($_SESSION["admin"] ?? false)) {
            echo "Missing thread ID.";
            return;
        }

        $stmt = $pdo->query("
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
        $threads = $stmt->fetchAll(PDO::FETCH_ASSOC);

        $this->render("dashboard/thread_list", [
            "title" => "All Threads",
            "threads" => $threads
        ]);
    }
}
