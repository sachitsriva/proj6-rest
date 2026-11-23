<?php
$views = [
    'All saved control times' => 'listAll/json',
    'First 3 opening times' => 'listOpenOnly/csv?top=3',
];

$context = stream_context_create(['http' => ['timeout' => 5]]);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Brevet Control Time Exports</title>
</head>
<body>
    <h1>Brevet Time Exports</h1>

    <?php foreach ($views as $title => $path): ?>
        <?php $body = @file_get_contents("http://laptop-service/$path", false, $context); ?>
        <h2><?= htmlspecialchars($title) ?></h2>
        <pre><?= htmlspecialchars($body === false ? 'Could not load times.' : $body) ?></pre>
    <?php endforeach; ?>
</body>
</html>