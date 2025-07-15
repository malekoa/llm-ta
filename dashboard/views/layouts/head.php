<?php

/** @var string|null $title */
?>
<!DOCTYPE html>
<html lang="en">
<style>
  #page-loader {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: white;
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: opacity 0.3s ease;
  }

  #page-loader.hidden {
    opacity: 0;
    pointer-events: none;
  }
</style>
<script>
  document.addEventListener("DOMContentLoaded", () => {
    const loader = document.getElementById("page-loader");
    if (loader) loader.classList.add("hidden");
  });
</script>

<head>
  <meta charset="UTF-8">
  <title><?= $title ?? "Dashboard" ?></title>
  <link rel="shortcut icon" href="/public/favicon.png" type="image/x-icon">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@1.0.4/css/bulma.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.14.8/dist/cdn.min.js"></script>
</head>
<!-- <body> -->

<body x-data x-init="$el.classList.add('fade-in')">

  <style>
    .fade-in {
      opacity: 0;
      animation: fadeIn 0.4s ease-out forwards;
    }

    @keyframes fadeIn {
      to {
        opacity: 1;
      }
    }
  </style>
  <div id="page-loader">
    <button class="is-outlined button is-loading is-white is-large">Loading…</button>
  </div>