$ErrorActionPreference = "Stop"
Clear-Host
Write-Host "== Grand Azure Hotel Setup ==" -ForegroundColor Cyan
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]"Administrator")
if (-not $isAdmin) { Start-Process powershell "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs; exit }
Write-Host "OK: Admin" -ForegroundColor Green
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir
Write-Host "OK: Folder $ScriptDir" -ForegroundColor Green
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
  Write-Host "Installing Chocolatey..." -ForegroundColor Yellow
  Set-ExecutionPolicy Bypass -Scope Process -Force
  [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
  Invoke-Expression ((New-Object System.Net.WebClient).DownloadString("https://community.chocolatey.org/install.ps1"))
  $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
} else { Write-Host "OK: Chocolatey" -ForegroundColor Green }
$pythonCmd = $null
foreach ($cmd in @("python","python3","py")) {
  try { $v = & $cmd --version 2>&1; if ($v -match "Python 3\.") { $pythonCmd = $cmd; Write-Host "OK: $v" -ForegroundColor Green; break } } catch {} }
if (-not $pythonCmd) {
  Write-Host "Installing Python..." -ForegroundColor Yellow
  choco install python311 -y --no-progress
  $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
  Start-Sleep 3; $pythonCmd = "python" }
$odbc = Get-OdbcDriver -Name "ODBC Driver*SQL Server*" -ErrorAction SilentlyContinue
if (-not $odbc) {
  Write-Host "Installing ODBC Driver..." -ForegroundColor Yellow
  $f2 = "$env:TEMP\odbc17.msi"
  (New-Object System.Net.WebClient).DownloadFile("https://go.microsoft.com/fwlink/?linkid=2187214",$f2)
  Start-Process msiexec.exe -ArgumentList "/i `"$f2`" /quiet /norestart IACCEPTMSODBCSQLLICENSETERMS=YES" -Wait -NoNewWindow
  Write-Host "OK: ODBC Driver" -ForegroundColor Green
} else { Write-Host "OK: ODBC Driver" -ForegroundColor Green }
$venvPath = Join-Path $ScriptDir "venv"
$pythonExe = Join-Path $venvPath "Scripts\python.exe"
$pipExe = Join-Path $venvPath "Scripts\pip.exe"
if (-not (Test-Path $venvPath)) { Write-Host "Creating venv..." -ForegroundColor Yellow; & $pythonCmd -m venv venv }
Write-Host "OK: venv" -ForegroundColor Green
& $pythonExe -m pip install --upgrade pip --quiet
Write-Host "Installing packages..." -ForegroundColor Yellow
& $pipExe install -r requirements.txt
Write-Host "OK: Packages installed" -ForegroundColor Green
$envFile = Join-Path $ScriptDir ".env"
if (-not (Test-Path $envFile)) {
  $s = Read-Host "SQL Server [localhost]"; if (!$s) { $s = "localhost" }
  $d = Read-Host "Database [HotelManagement]"; if (!$d) { $d = "HotelManagement" }
  $u = Read-Host "SQL Username [sa]"; if (!$u) { $u = "sa" }
  $p = Read-Host "SQL Password"
  $k = -join ((65..90)+(97..122)+(48..57) | Get-Random -Count 48 | % { [char]$_ })
  @("SECRET_KEY=$k","SQL_SERVER=$s","SQL_DATABASE=$d","SQL_USERNAME=$u","SQL_PASSWORD=$p","SQL_DRIVER=ODBC Driver 17 for SQL Server","HOTEL_NAME=Grand Azure Hotel","HOTEL_ADDRESS=1 Harbor Blvd","HOTEL_CITY=Miami FL","HOTEL_PHONE=555-0100","HOTEL_EMAIL=info@hotel.com","HOTEL_WEBSITE=www.hotel.com","TAX_RATE=0.12","FLASK_ENV=development","FLASK_DEBUG=1") | Set-Content $envFile -Encoding UTF8
  Write-Host "OK: .env created" -ForegroundColor Green
} else { Write-Host "OK: .env exists" -ForegroundColor Green }
$sc = Read-Host "Run database_schema.sql in SSMS yet? (1=Yes 2=Open it)"
if ($sc -eq "2") {
  $sf = Join-Path $ScriptDir "database_schema.sql"
  $ss = @("${env:ProgramFiles(x86)}\Microsoft SQL Server Management Studio 20\Common7\IDE\Ssms.exe","${env:ProgramFiles(x86)}\Microsoft SQL Server Management Studio 19\Common7\IDE\Ssms.exe","${env:ProgramFiles(x86)}\Microsoft SQL Server Management Studio 18\Common7\IDE\Ssms.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
  if ($ss) { Start-Process $ss "`"$sf`"" } else { Start-Process notepad.exe $sf }
  Read-Host "Press Enter when done" }
@("@echo off","title Grand Azure Hotel","cd /d ""%~dp0""","call venv\Scripts\activate","start http://localhost:5000","python app.py","pause") | Set-Content (Join-Path $ScriptDir "START_HOTEL.bat") -Encoding ASCII
Write-Host "== DONE! Starting app... ==" -ForegroundColor Green
Write-Host "Go to: http://localhost:5000/auth/setup-admin" -ForegroundColor Yellow
Write-Host "Then login: admin / admin123" -ForegroundColor Yellow
Start-Job { Start-Sleep 4; Start-Process "http://localhost:5000/auth/setup-admin" } | Out-Null
$env:FLASK_APP = "app.py"
& $pythonExe app.py
