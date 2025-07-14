<?php

class AuthController extends Controller
{
    public function login()
    {
        $error = "";

        // POST: handle form submission
        if ($_SERVER["REQUEST_METHOD"] === "POST") {
            $this->verify_csrf_token_or_die();

            $username = $_POST["username"] ?? "";
            $password = $_POST["password"] ?? "";

            if (
                isset(USERS[$username]) &&
                password_verify($password, USERS[$username])
            ) {
                $_SESSION["admin"] = true;
                $_SESSION["user"] = $username;
                header("Location: /");
                exit();
            } else {
                $error = "Invalid username or password.";
            }
        }

        // GET or after failed POST: show login form with a new CSRF token
        $csrf_token = $this->generate_csrf_token();
        $this->render("auth/login", compact("error", "csrf_token"));
    }

    public function logout()
    {
        session_destroy();
        header("Location: /login");
        exit();
    }
}
