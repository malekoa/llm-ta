<?php

define("DB_PATH", dirname(__DIR__) . "/bot/data.db");
// Map of username => password hash
define("USERS", [
    "admin" => '$2y$12$WBiFrCDM1Ud8n9yXJ2wzUOKRKP2nX9Y16hmP5vhsiV5dwyQWAzvbe',
    "ta" => '$2y$12$hgkuQgLcbtZ7bILczZ4JmeYiVFnfmcyh2m0t77bqc4tjiiCZVbwAy',
    // Add more users here
    // To generate a password hash, run: 
    // php -r "echo password_hash('yourpassword', PASSWORD_DEFAULT);"
]);