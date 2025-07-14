<?php

class Controller
{
    protected function render($view, $data = [])
    {
        View::render($view, $data);
    }

    protected function requireLogin()
    {
        if (!($_SESSION["admin"] ?? false)) {
            header("Location: /login");
            exit();
        }
    }

    protected function generate_csrf_token()
    {
        $token = bin2hex(random_bytes(32));
        $_SESSION["csrf_token"] = $token;
        log_debug("NEW CSRF TOKEN GENERATED", $token);
        return $token;
    }

    protected function verify_csrf_token_or_die()
    {
        $postToken = $_POST["csrf_token"] ?? "";
        $sessionToken = $_SESSION["csrf_token"] ?? "";

        log_debug("POST CSRF", $postToken);
        log_debug("SESSION CSRF", $sessionToken);

        if ($postToken !== $sessionToken) {
            log_debug("CSRF ERROR", "Mismatch or missing token");
            die("Invalid CSRF token.");
        }
    }
}
