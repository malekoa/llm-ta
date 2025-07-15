<?php

class Database
{
    private static ?PDO $pdo = null;

    public static function getConnection(): PDO
    {
        if (self::$pdo === null) {
            self::$pdo = new PDO("sqlite:" . DB_PATH);
            self::$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

            // SQLite performance + concurrency enhancements
            self::$pdo->exec("PRAGMA journal_mode = WAL;");
            self::$pdo->exec("PRAGMA synchronous = NORMAL;");
            self::$pdo->exec("PRAGMA busy_timeout = 3000;"); // wait up to 3s if DB is locked
        }

        return self::$pdo;
    }
}
