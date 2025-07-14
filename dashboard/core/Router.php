<?php

class Router
{
    private $routes = [];

    public function get($path, $callback)
    {
        $this->routes["GET"][$path] = $callback;
    }

    public function post($path, $callback)
    {
        $this->routes["POST"][$path] = $callback;
    }

    public function dispatch($uri, $method)
    {
        $path = parse_url($uri, PHP_URL_PATH);
        $callback = $this->routes[$method][$path] ?? null;

        if (!$callback) {
            http_response_code(404);
            echo "404 Not Found";
            return;
        }

        [$controller, $action] = explode("@", $callback);
        require_once __DIR__ . "/../controllers/" . $controller . ".php";
        require_once __DIR__ . "/Controller.php";
        require_once __DIR__ . "/View.php";
        (new $controller())->$action();
    }
}
