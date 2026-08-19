$ErrorActionPreference = 'Stop'

$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$wrapper = (Resolve-Path (Join-Path $PSScriptRoot 'figure_1_render_wrapper.html')).Path
$svg = Join-Path $root 'figures\figure_1.svg'
$pdf = Join-Path $root 'figures\figure_1.pdf'
$pngStem = Join-Path $root 'figures\figure_1'
$png = Join-Path $root 'figures\figure_1.png'
$profile = Join-Path $root '.tmp\chrome_figure1_profile'
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

foreach ($path in @($svg, $wrapper, $chrome, $pdftoppm)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Required Figure 1 render input not found: $path"
    }
}
foreach ($path in @($pdf, $png)) {
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
    throw "Chrome Figure 1 SVG-to-PDF rendering failed with exit code $($process.ExitCode)"
}

& $pdftoppm -singlefile -png -scale-to-x 4016 -scale-to-y -1 $pdf $pngStem
if ($LASTEXITCODE -ne 0) {
    throw "Figure 1 PDF-to-PNG rendering failed with exit code $LASTEXITCODE"
}

Get-FileHash -LiteralPath $svg, $pdf, $png -Algorithm SHA256
