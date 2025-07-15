<?php

class DashboardController extends Controller
{
    public function home()
    {
        $this->requireLogin();
        $this->render("dashboard/home", ["title" => "Dashboard"]);
    }

    public function thread()
    {
        $thread_id = $_GET["thread_id"] ?? null;
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

            $this->render("dashboard/thread", [
                "title" => "Thread View",
                "messages" => $messages,
                "thread_id" => $thread_id
            ]);
            return;
        }

        // Case 2: show thread list only if logged in
        if (!($_SESSION["admin"] ?? false)) {
            echo "Missing thread ID.";
            return;
        }

        // Get distinct threads with latest message
        $stmt = $pdo->query("
        SELECT thread_id, MAX(timestamp) as latest_time
        FROM messages
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
