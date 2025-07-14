<?php

class View
{
    public static function render($view, $data = [])
    {
        extract($data);
        include __DIR__ . "/../views/layouts/head.php";
        include __DIR__ . "/../views/layouts/nav.php";
        include __DIR__ . "/../views/" . $view . ".php";
        include __DIR__ . "/../views/layouts/footer.php";
    }
}
