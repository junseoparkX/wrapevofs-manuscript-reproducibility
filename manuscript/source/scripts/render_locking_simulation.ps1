$ErrorActionPreference = 'Stop'

$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$wrapper = (Resolve-Path (Join-Path $PSScriptRoot 'locking_simulation_render_wrapper.html')).Path
$svg = Join-Path $root 'figures\figure_s24.svg'
$pdf = Join-Path $root 'figures\figure_s24.pdf'
$pngStem = Join-Path $root 'figures\figure_s24'
$png = Join-Path $root 'figures\figure_s24.png'
$manifestPath = Join-Path $root 'supplementary_data\locking_rule_simulation\RENDER_MANIFEST.json'
$profile = Join-Path $root '.tmp\chrome_figure_s24_profile'
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

foreach ($path in @($svg, $chrome, $pdftoppm)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Required render input not found: $path"
    }
}
foreach ($path in @($pdf, $png, $manifestPath)) {
    if (-not $path.StartsWith($root + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to write outside the manuscript source directory: $path"
    }
}

$uri = ([Uri]$wrapper).AbsoluteUri
$arguments = @(
    '--headless=new',
    '--disable-gpu',
    "--user-data-dir=$profile",
    '--no-pdf-header-footer',
    "--print-to-pdf=$pdf",
    $uri
)
$process = Start-Process -FilePath $chrome -ArgumentList $arguments -Wait -PassThru -WindowStyle Hidden
if ($process.ExitCode -ne 0) {
    throw "Chrome SVG-to-PDF rendering failed with exit code $($process.ExitCode)"
}

& $pdftoppm -singlefile -png -r 300 $pdf $pngStem
if ($LASTEXITCODE -ne 0) {
    throw "PDF-to-PNG rendering failed with exit code $LASTEXITCODE"
}

$manifest = [ordered]@{
    renderer = 'Chrome headless plus Poppler pdftoppm'
    figure_width_mm = 170
    figure_height_mm = 67
    svg_sha256 = (Get-FileHash -LiteralPath $svg -Algorithm SHA256).Hash.ToLowerInvariant()
    pdf_sha256 = (Get-FileHash -LiteralPath $pdf -Algorithm SHA256).Hash.ToLowerInvariant()
    png_sha256 = (Get-FileHash -LiteralPath $png -Algorithm SHA256).Hash.ToLowerInvariant()
    png_dpi = 300
}
$manifest | ConvertTo-Json | Set-Content -LiteralPath $manifestPath -Encoding utf8
$manifest | ConvertTo-Json
