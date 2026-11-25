param([Parameter(Mandatory = $true)][ValidateSet('Update', 'Start', 'Stop')][string]$Action)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$runtimeDir = Join-Path $projectRoot '.runtime'
$pythonExe = Join-Path $projectRoot '.venv/Scripts/python.exe'
$appFile = Join-Path $projectRoot 'backend/app.py'
$pidFile = Join-Path $runtimeDir 'backend.pid'
$siteUrl = 'http://127.0.0.1:5000/'

function Stop-Backend {
    if (-not (Test-Path -LiteralPath $pidFile)) { return }
    $savedProcessId = 0
    if (-not [int]::TryParse((Get-Content -LiteralPath $pidFile -Raw).Trim(), [ref]$savedProcessId)) {
        throw 'The saved process ID is invalid.'
    }
    $process = Get-CimInstance Win32_Process -Filter "ProcessId=$savedProcessId" -ErrorAction SilentlyContinue
    if ($process) {
        # 只关闭这个项目启动的进程，避免误关其他Python程序。
        if (-not $process.CommandLine -or $process.CommandLine.IndexOf($appFile, [StringComparison]::OrdinalIgnoreCase) -lt 0) {
            throw 'The saved process ID belongs to another program.'
        }
        Get-CimInstance Win32_Process -Filter "ParentProcessId=$savedProcessId" -ErrorAction SilentlyContinue |
            Where-Object { $_.CommandLine -and $_.CommandLine.IndexOf($appFile, [StringComparison]::OrdinalIgnoreCase) -ge 0 } |
            ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
        Stop-Process -Id $savedProcessId -Force -ErrorAction SilentlyContinue
        for ($attempt = 0; $attempt -lt 20; $attempt++) {
            if (-not (Get-Process -Id $savedProcessId -ErrorAction SilentlyContinue)) { break }
            Start-Sleep -Milliseconds 200
        }
    }
    Remove-Item -LiteralPath $pidFile
}

function Run-Tool([string]$Executable, [string[]]$ToolArguments, [string]$Folder) {
    Push-Location -LiteralPath $Folder
    try {
        & $Executable @ToolArguments
        if ($LASTEXITCODE -ne 0) { throw "Command failed: $Executable (exit $LASTEXITCODE)" }
    } finally { Pop-Location }
}

function Find-Python {
    $launcher = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($launcher) {
        foreach ($version in @('-3.11', '-3.12')) {
            try {
                $candidate = & $launcher.Source $version -c 'import sys; print(sys.executable)' 2>$null
                if ($LASTEXITCODE -eq 0 -and $candidate -and (Test-Path -LiteralPath $candidate.Trim())) {
                    return $candidate.Trim()
                }
            } catch { }
        }
    }
    $command = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($command) {
        $version = & $command.Source -c "import sys; print(str(sys.version_info.major) + '.' + str(sys.version_info.minor))"
        if ($LASTEXITCODE -eq 0 -and $version.Trim() -in @('3.11', '3.12')) { return $command.Source }
    }
    throw 'Python 3.11 or 3.12 was not found. Install it and run this file again.'
}

function Update-System {
    $node = Get-Command node.exe -ErrorAction SilentlyContinue
    $npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
    if (-not $node -or -not $npm) { throw 'Node.js and npm were not found. Add Node.js to PATH first.' }
    $nodeVersion = & $node.Source -p "process.versions.node.split('.')[0]"
    if ($LASTEXITCODE -ne 0 -or [int]$nodeVersion -lt 20) { throw 'Use Node.js 20 or newer.' }
    $basePython = Find-Python
    Stop-Backend

    $envFile = Join-Path $projectRoot '.env'
    if (-not (Test-Path -LiteralPath $envFile)) {
        $text = Get-Content -LiteralPath (Join-Path $projectRoot '.env.example') -Raw
        $text = $text.Replace('belarus-tourism-change-this-flask-secret', ([guid]::NewGuid().ToString('N') + [guid]::NewGuid().ToString('N')))
        $text = $text.Replace('belarus-tourism-change-this-jwt-secret', ([guid]::NewGuid().ToString('N') + [guid]::NewGuid().ToString('N')))
        [IO.File]::WriteAllText($envFile, $text, (New-Object Text.UTF8Encoding($false)))
        Write-Host 'Created .env. Check its MySQL connection before continuing.'
    }
    if (-not (Test-Path -LiteralPath $pythonExe)) {
        Run-Tool $basePython @('-m', 'venv', (Join-Path $projectRoot '.venv')) $projectRoot
    }
    Write-Host '[1/4] Installing Python dependencies...'
    Run-Tool $pythonExe @('-m', 'pip', 'install', '--prefer-binary', '-r', 'backend/requirements.txt', '--disable-pip-version-check') $projectRoot
    Write-Host '[2/4] Installing frontend dependencies...'
    Run-Tool $npm.Source @('install', '--package-lock=false', '--no-audit', '--no-fund') (Join-Path $projectRoot 'frontend')
    Write-Host '[3/4] Building the website...'
    $oldPath = $env:PATH
    try {
        $env:PATH = (Split-Path -Parent $node.Source) + ';' + $env:PATH
        Run-Tool $npm.Source @('run', 'build') (Join-Path $projectRoot 'frontend')
    } finally { $env:PATH = $oldPath }
    Write-Host '[4/4] Replacing the project database with the project data...'
    Run-Tool $pythonExe @('-B', 'update_database.py', '--reset') (Join-Path $projectRoot 'backend')
    New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null
    [IO.File]::WriteAllText((Join-Path $runtimeDir 'ready.flag'), (Get-Date).ToString('s'))
    Write-Host 'Update complete. Double-click Start System.bat to open the website.'
}

function Start-System {
    if (-not (Test-Path -LiteralPath $pythonExe) -or -not (Test-Path -LiteralPath (Join-Path $projectRoot 'backend/static/web/index.html')) -or -not (Test-Path -LiteralPath (Join-Path $runtimeDir 'ready.flag'))) {
        throw 'Run Install or Update.bat first.'
    }
    if (Test-Path -LiteralPath $pidFile) {
        $savedProcessId = 0
        if ([int]::TryParse((Get-Content -LiteralPath $pidFile -Raw).Trim(), [ref]$savedProcessId)) {
            $process = Get-CimInstance Win32_Process -Filter "ProcessId=$savedProcessId" -ErrorAction SilentlyContinue
            if ($process -and $process.CommandLine -and $process.CommandLine.IndexOf($appFile, [StringComparison]::OrdinalIgnoreCase) -ge 0) {
                Write-Host "Already running: $siteUrl"
                if ($env:BELARUS_NO_BROWSER -ne '1') { Start-Process $siteUrl }
                return
            }
        }
        Remove-Item -LiteralPath $pidFile
    }
    if (Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue) {
        throw 'Port 5000 is being used by another program.'
    }
    New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null
    $stderrFile = Join-Path $runtimeDir 'backend.stderr.log'
    $process = Start-Process -FilePath $pythonExe -ArgumentList @('-B', ('"' + $appFile + '"')) -WorkingDirectory (Join-Path $projectRoot 'backend') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtimeDir 'backend.stdout.log') -RedirectStandardError $stderrFile -PassThru
    [IO.File]::WriteAllText($pidFile, [string]$process.Id)
    # 接口能读到数据库之后再打开网页。
    $ready = $false
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        if ($process.HasExited) { break }
        try {
            $response = Invoke-WebRequest -UseBasicParsing -Uri ($siteUrl + 'api/attractions?per_page=1&view=card') -TimeoutSec 2
            if ($response.StatusCode -eq 200) { $ready = $true; break }
        } catch { }
        Start-Sleep -Milliseconds 500
    }
    if (-not $ready) {
        Stop-Backend
        if (Test-Path -LiteralPath $stderrFile) { Get-Content -LiteralPath $stderrFile -Tail 15 }
        throw 'The website did not start. Check the MySQL connection in .env.'
    }
    Write-Host "Running: $siteUrl"
    if ($env:BELARUS_NO_BROWSER -ne '1') { Start-Process $siteUrl }
}

try {
    switch ($Action) {
        'Update' { Update-System }
        'Start' { Start-System }
        'Stop' { Stop-Backend; Write-Host 'The system is stopped.' }
    }
    exit 0
} catch {
    Write-Host ('ERROR: ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
