<#
.SYNOPSIS
  Generic Tailscale status helper (no hostnames hardcoded).
.DESCRIPTION
  Prints Windows Tailscale service state, local IPv4, peer status, netcheck.
  Optional local readonly web UI on 127.0.0.1:8088.
.PARAMETER Help
  Show this help and exit.
.EXAMPLE
  .\tailscale_status.ps1
  $env:OPS_STATUS_NO_BROWSER=1; $env:OPS_STATUS_NO_PAUSE=1; .\tailscale_status.ps1
#>
param(
  [switch]$Help
)
if ($Help) {
  Get-Help -Full $MyInvocation.MyCommand.Path
  exit 0
}
$ErrorActionPreference = 'Continue'
$tailscale = 'C:\Program Files\Tailscale\tailscale.exe'
$tailscaleWebUrl = 'http://127.0.0.1:8088/'

function Open-TailscaleWeb {
  if ($env:OPS_STATUS_NO_BROWSER -eq '1') { return }
  try {
    $listener = Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 8088 -State Listen -ErrorAction SilentlyContinue
    if (-not $listener -and (Test-Path $tailscale)) {
      Start-Process -FilePath $tailscale -ArgumentList @('web', '--readonly', '--listen', '127.0.0.1:8088') -WindowStyle Hidden
      Start-Sleep -Seconds 1
    }
    Start-Process $tailscaleWebUrl
    Write-Host ('Tailscale web opened: ' + $tailscaleWebUrl)
  } catch {
    Write-Host ('Tailscale web open failed: ' + $_.Exception.Message) -ForegroundColor Yellow
  }
  Write-Host ''
}

function Wait-BeforeExit {
  if ($env:OPS_STATUS_NO_PAUSE -eq '1') { return }
  Write-Host ''
  Read-Host 'Press Enter to close'
}

Write-Host 'Tailscale Status' -ForegroundColor Cyan
Write-Host ('Time: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
Write-Host ''
Open-TailscaleWeb

Write-Host '[Windows Service]' -ForegroundColor Yellow
Get-Service -Name Tailscale -ErrorAction SilentlyContinue | Format-Table Name, Status, StartType -AutoSize

Write-Host ''
Write-Host '[Local Tailscale IP]' -ForegroundColor Yellow
if (Test-Path $tailscale) { & $tailscale ip -4 }
else { Write-Host "tailscale.exe not found: $tailscale" -ForegroundColor Red }

Write-Host ''
Write-Host '[Peer Status]' -ForegroundColor Yellow
if (Test-Path $tailscale) { & $tailscale status }

Write-Host ''
Write-Host '[Network Check]' -ForegroundColor Yellow
if (Test-Path $tailscale) { & $tailscale netcheck }

Wait-BeforeExit
