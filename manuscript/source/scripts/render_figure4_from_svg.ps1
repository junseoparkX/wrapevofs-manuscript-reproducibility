$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$wrapper = (Resolve-Path (Join-Path $PSScriptRoot 'figure4_render_wrapper.html')).Path
$output = Join-Path $root 'figures\figure_4.png'
$profile = Join-Path $root '.tmp\chrome_figure4_profile'
$chrome = 'C:\Program Files\Google\Chrome\Application\chrome.exe'

if (-not (Test-Path -LiteralPath $chrome)) {
    throw "Chrome executable not found: $chrome"
}
if (-not $output.StartsWith($root + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to write outside the manuscript source directory: $output"
}

$uri = ([Uri]$wrapper).AbsoluteUri
$arguments = @(
    '--headless=new',
    '--disable-gpu',
    '--hide-scrollbars',
    "--user-data-dir=$profile",
    '--force-device-scale-factor=2',
    '--window-size=1205,1063',
    "--screenshot=$output",
    $uri
)
$process = Start-Process -FilePath $chrome -ArgumentList $arguments -Wait -PassThru -WindowStyle Hidden
if ($process.ExitCode -ne 0) {
    throw "Chrome SVG rendering failed with exit code $($process.ExitCode)"
}

$image = [System.Drawing.Image]::FromFile($output)
try {
    if ($image.Width -ne 2410 -or $image.Height -ne 2126) {
        throw "Unexpected Figure 4 dimensions: $($image.Width)x$($image.Height)"
    }
} finally {
    $image.Dispose()
}

Get-FileHash -LiteralPath $output -Algorithm SHA256
