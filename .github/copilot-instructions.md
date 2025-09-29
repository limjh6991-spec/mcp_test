# Copilot Instructions for AI Agents

## Project Overview
This repository is a Windows-focused developer environment diagnostic tool. The main script, `dev_env_check.ps1`, collects system, toolchain, GPU, and environment information, outputting a detailed report to `dev_env_report.json`. Perfect for CI/CD pipelines and environment validation.

## Key Files
- `dev_env_check.ps1`: PowerShell script that checks:
  - Developer tools (Python, Node, Git, Docker, etc.)
  - System specs (CPU, RAM, disk space)
  - GPU and CUDA capabilities
  - VS Code extensions
  - Python/ML environment details
  - Common development ports (80,443,3000,5173,7860,8000,8080,8888,6006)
- `dev_env_report.json`: Output file with structured diagnostics data

## How It Works
1. Checks for developer tools using `Test-Cmd` function pattern
2. Gathers system info via Windows CIM interface
3. Queries GPU info using `Win32_VideoController`
4. Checks VS Code extensions via `code --list-extensions`
5. Runs inline Python code to detect PyTorch/CUDA capabilities
6. Scans listening ports for common development services
7. Outputs everything as structured JSON

## Project-Specific Patterns
- PowerShell-First: All checks use PowerShell idioms (no Bash)
  ```powershell
  # 도구 버전 확인 패턴 예시:
  function Test-Cmd($cmd){
    $exists = (Get-Command $cmd -ErrorAction SilentlyContinue) -ne $null
    $ver = if($exists){ & $cmd --version } else { 'N/A' }
    return @{ cmd=$cmd; exists=$exists; version=$ver }
  }
  ```
- Error Handling: Uses `$ErrorActionPreference = 'SilentlyContinue'` with try/catch blocks
  ```powershell
  $cudaver = try { 
    & nvcc --version 2>$null | Select-Object -First 1 
  } catch { 
    'N/A' 
  }
  ```
- Structure: Ordered dictionaries (`[ordered]@{}`) maintain JSON field order
- Python Integration: Smart detection of Python environment
  ```powershell
  # Python 실행 환경 감지를 위한 대체 패턴
  $pyExe = (Get-Command python -ErrorAction SilentlyContinue).Source
  if (-not $pyExe) { 
    $pyExe = (Get-Command py -ErrorAction SilentlyContinue).Source
    $pyCmd = 'py -3' 
  } else { 
    $pyCmd = 'python' 
  }
  ```
- Port Scanning: Focuses on common dev ports (80,443,3000,5173,7860,8000,8080,8888,6006)

## Developer Workflow
1. Run script: `powershell -ExecutionPolicy Bypass -File dev_env_check.ps1`
2. Review JSON output in `dev_env_report.json`
3. To extend checks:
   - Add new command to `$items` array
   - Or create new section in the results dictionary
   - Ensure errors are properly handled

## Conventions
- UTF-8 output encoding for JSON
- PowerShell ordered dictionaries for predictable JSON structure
- Commands checked via `Get-Command` then `--version`
- Nested data limited to 6 levels deep in JSON
- All paths use Windows-style separators

## Integration Points
- CI/CD: Run script to validate development environments
- Environment Compliance: Parse JSON to check required tools
- System Requirements: Verify hardware/software prerequisites
- GPU/ML Readiness: Check CUDA and PyTorch capabilities

## Example Extensions
1. Add new tool check:
   ```powershell
   $items += 'new-tool'
   ```
2. Add new system check:
   ```powershell
   $sys['NewCheck'] = Get-SomeWindowsMetric
   ```
3. Custom Python checks:
   ```powershell
   $customCheck = & $pyCmd -c '여기에 파이썬 코드 작성'
   ```

---
For questions or to extend this guide, edit `.github/copilot-instructions.md`.
