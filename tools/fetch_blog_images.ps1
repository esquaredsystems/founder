<#
    Downloads every image referenced by the imported Blogspot posts.

    Run from the repo root, in PowerShell:

        powershell -ExecutionPolicy Bypass -File tools\fetch_blog_images.ps1

    Reads tools/blog-images.txt (written by import_blogger.py), which is a
    tab-separated list of "remote URL <TAB> local path", and saves each file
    into assets/img/blog/. Files that already exist are skipped, so the script
    is safe to re-run.

    This has to run on your machine rather than in the session because Blogger's
    image hosts are not reachable from the sandbox.
#>

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$manifest = Join-Path $PSScriptRoot 'blog-images.txt'

if (-not (Test-Path $manifest)) {
    Write-Error "No manifest at $manifest — run import_blogger.py first."
}

$dest = Join-Path $repo 'assets\img\blog'
New-Item -ItemType Directory -Force -Path $dest | Out-Null

$ok = 0; $skip = 0; $fail = 0
$lines = Get-Content $manifest | Where-Object { $_.Trim() -ne '' }

foreach ($line in $lines) {
    $parts = $line -split "`t"
    if ($parts.Count -lt 2) { continue }
    $url = $parts[0].Trim()
    $out = Join-Path $repo ($parts[1].TrimStart('/') -replace '/', '\')

    if (Test-Path $out) { $skip++; continue }

    try {
        Invoke-WebRequest -Uri $url -OutFile $out -UseBasicParsing -TimeoutSec 60
        $ok++
        Write-Host "  ok   $([System.IO.Path]::GetFileName($out))"
    }
    catch {
        $fail++
        Write-Warning "  FAIL $url"
    }
}

Write-Host ""
Write-Host "downloaded: $ok   already present: $skip   failed: $fail"
if ($fail -gt 0) {
    Write-Host "Failed URLs are usually images deleted from Blogger years ago." -ForegroundColor Yellow
}
