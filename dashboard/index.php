<?php
session_start();
require_once __DIR__ . "/core/debug.php";
require_once __DIR__ . "/config.php";

// Load core classes
require_once __DIR__ . "/core/Controller.php";
require_once __DIR__ . "/core/View.php";
require_once __DIR__ . "/core/Router.php";

// Start routing
$router = new Router();
$router->get("/login", "AuthController@login");
$router->post("/login", "AuthController@login");
$router->get("/logout", "AuthController@logout");
$router->get("/", "DashboardController@home");
$router->get("/thread", "DashboardController@thread");
$router->dispatch($_SERVER["REQUEST_URI"], $_SERVER["REQUEST_METHOD"]);
