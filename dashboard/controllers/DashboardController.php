<?php

class DashboardController extends Controller
{
    public function home()
    {
        $this->requireLogin();
        $this->render("dashboard/home", ["title" => "Dashboard"]);
    }
}
