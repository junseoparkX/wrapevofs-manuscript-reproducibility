$ErrorActionPreference = 'Stop'

$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$wrapper = (Resolve-Path (Join-Path $PSScriptRoot 'figure_s16_render_wrapper.html')).Path
$output = Join-Path $root 'figures\figure_s16.pdf'
$pngStem = Join-Path $root 'figures\figure_s16'
function Resolve-Renderer {
    param(
        [string]$Override,
        [string[]]$Commands,
        [string[]]$Fallbacks
    )
    if ($Override) {
        if (-not (Test-Path -LiteralPath $Override)) {
            throw "Configured renderer not found: $Override"
        }
        return (Resolve-Path -LiteralPath $Override).Path
    }
    foreach ($name in $Commands) {
        $command = Get-Command $name -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($command) { return $command.Source }
    }
    foreach ($path in $Fallbacks) {
        if (Test-Path -LiteralPath $path) { return $path }
    }
    throw "Required renderer was not found. Configure the corresponding executable environment variable."
}

$chrome = Resolve-Renderer -Override $env:CHROME_EXECUTABLE -Commands @('google-chrome', 'chromium', 'chrome', 'msedge') -Fallbacks @(
    'C:\Program Files\Google\Chrome\Application\chrome.exe',
    'C:\Program Files\Microsoft\Edge\Application\msedge.exe'
)
$pdftoppm = Resolve-Renderer -Override $env:PDFTOPPM_EXECUTABLE -Commands @('pdftoppm') -Fallbacks @()

foreach ($path in @($chrome, $pdftoppm)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Required renderer not found: $path"
    }
}
if (-not $output.StartsWith($root + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to write outside the manuscript source directory: $output"
}

$uri = ([Uri]$wrapper).AbsoluteUri
$arguments = @(
    '--headless=new',
    '--disable-gpu',
    '--no-pdf-header-footer',
    "--print-to-pdf=$output",
    $uri
)
$process = Start-Process -FilePath $chrome -ArgumentList $arguments -Wait -PassThru -WindowStyle Hidden
if ($process.ExitCode -ne 0) {
    throw "Chrome SVG-to-PDF rendering failed with exit code $($process.ExitCode)"
}

& $pdftoppm -singlefile -png -r 300 $output $pngStem
if ($LASTEXITCODE -ne 0) {
    throw "PDF-to-PNG rendering failed with exit code $LASTEXITCODE"
}

Get-FileHash -LiteralPath $output, (Join-Path $root 'figures\figure_s16.png') -Algorithm SHA256
