# dev_env_check.ps1 (Windows)
# Windows 개발 환경 진단 도구
$ErrorActionPreference = 'SilentlyContinue'

function Test-Cmd($cmd){
  $exists = (Get-Command $cmd -ErrorAction SilentlyContinue) -ne $null
  $ver = if($exists){ & $cmd --version 2>$null | Select-Object -First 1 } else { 'N/A' }
  return @{ cmd=$cmd; exists=$exists; version=$ver }
}

function Get-GPU(){
  try{ Get-CimInstance Win32_VideoController | Select-Object Name, AdapterRAM, DriverVersion }
  catch{ Write-Output 'N/A' }
}

$items = @('python','pip','node','npm','npx','git','code','docker','blender','ros2','conda') | ForEach-Object { Test-Cmd $_ }

$sys = [ordered]@{
  Hostname     = $env:COMPUTERNAME
  OS           = (Get-CimInstance Win32_OperatingSystem).Caption
  OSVersion    = (Get-CimInstance Win32_OperatingSystem).Version
  CPU          = (Get-CimInstance Win32_Processor | Select-Object -First 1 -Expand Name)
  RAM_GB       = [math]::Round((Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum).Sum/1GB,2)
  Disk_GB_Free = [math]::Round((Get-PSDrive -Name C).Free/1GB,2)
  PythonPath   = (Get-Command python -ErrorAction SilentlyContinue).Source
  VscodePath   = (Get-Command code   -ErrorAction SilentlyContinue).Source
}

$gpu        = Get-GPU
$extensions = try{ code --list-extensions } catch { @() }
$cudaver    = try{ & nvcc --version 2>$null | Select-Object -First 1 } catch { 'N/A' }

# Python 실행 환경 감지 및 설정
$pyExe = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pyExe) { $pyExe = (Get-Command py -ErrorAction SilentlyContinue).Source; $pyCmd = 'py -3' } else { $pyCmd = 'python' }

$torch = try {
  & $pyCmd -c @'
import json
try:
    import torch
    print(json.dumps({
        "torch": getattr(torch, "__version__", None),
        "cuda_available": bool(getattr(torch.cuda, "is_available", lambda: False)()),
        "cuda_version": getattr(torch.version, "cuda", None),
        "gpu_name": (torch.cuda.get_device_name(0) if (hasattr(torch, "cuda") and torch.cuda.is_available()) else None)
    }))
except Exception:
    print("{}")
'@
} catch { '{}' }
# 개발 서버 포트 스캔

$ports = Get-NetTCPConnection -State Listen |
  Where-Object { $_.LocalPort -in (80,443,3000,5173,7860,8000,8080,8888,6006) } |
  Select-Object LocalPort, OwningProcess

$result = [ordered]@{
  Timestamp        = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
  System           = $sys
  Commands         = $items
  GPU              = $gpu
  VSCodeExtensions = $extensions
  CUDA             = $cudaver
  Torch            = $torch
  ListeningPorts   = $ports
}

$result | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 dev_env_report.json
Write-Host "Saved: dev_env_report.json"
