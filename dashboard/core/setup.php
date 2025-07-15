<?php

function initializeDatabaseIfMissing()
{
    require_once __DIR__ . '/../config.php';

    // If the DB file doesn't exist, create it and initialize schema
    if (!file_exists(DB_PATH)) {
        require_once __DIR__ . '/Database.php';
        $pdo = Database::getConnection();

        $pdo->exec("PRAGMA foreign_keys = ON;");

        $schemaPath = __DIR__ . "/../../shared/schema.sql";
        if (!file_exists($schemaPath)) {
            die("Schema file not found.");
        }

        $schema = file_get_contents($schemaPath);
        $pdo->exec($schema);

        file_put_contents(__DIR__ . '/../debug.log', "[Init] Created data.db and loaded schema at " . date("Y-m-d H:i:s") . "\n", FILE_APPEND);
    }
}
