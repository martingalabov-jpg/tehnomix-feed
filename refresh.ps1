# Daily refresh of tehnomix-openai-feed.csv. Run by Task Scheduler; see README.
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$log = Join-Path $PSScriptRoot 'refresh.log'
function Log($m) { "$(Get-Date -Format s)  $m" | Add-Content $log -Encoding utf8 }
try {
    git pull -q --rebase origin main
    $ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
    curl.exe -sSf --retry 3 --retry-delay 20 -o google-new.csv -A $ua -H 'Accept: text/csv,*/*' https://www.tehnomix.bg/media/feed/google-new.csv
    if ($LASTEXITCODE -ne 0) { throw "download failed (curl exit $LASTEXITCODE)" }
    if ((Get-Content google-new.csv -TotalCount 1) -notmatch '^ID,Item title,Final URL') { throw 'download is not the feed CSV (challenge page?)' }
    $out = python -I build_openai_feed.py google-new.csv tehnomix-openai-feed.csv 2>&1
    if ($LASTEXITCODE -ne 0) { throw "converter failed: $out" }
    $rows = python -I -c "import csv;print(sum(1 for _ in csv.DictReader(open('tehnomix-openai-feed.csv',encoding='utf-8-sig'))))"
    if ([int]$rows -lt 3000) { git checkout -- tehnomix-openai-feed.csv; throw "only $rows products - refusing to publish" }
    (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ') | Set-Content last_run.txt -Encoding ascii
    git add tehnomix-openai-feed.csv last_run.txt
    git diff --cached --quiet
    if ($LASTEXITCODE -ne 0) { git commit -q -m "Refresh feed $(Get-Date -Format yyyy-MM-dd)"; git push -q origin main }
    Log "OK  $out  rows=$rows"
} catch { Log "FAIL  $_"; exit 1 }
