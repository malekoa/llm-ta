<?php

function log_debug($label, $value)
{
    $logPath = __DIR__ . "/../debug.log";
    $time = date("Y-m-d H:i:s");
    $dump = is_scalar($value) ? $value : var_export($value, true);
    file_put_contents($logPath, "[$time] $label: $dump\n", FILE_APPEND);
}
