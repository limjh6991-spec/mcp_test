# MCP Server Management Script (PowerShell)
# Usage: .\run_servers.ps1 -Action start|stop|status|restart [-Server server_name] [-Foreground]

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "status", "restart")]
    [string]$Action,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("prompt_generator", "stable_diffusion", "blender", "env_manager", "github")]
    [string]$Server,
    
    [Parameter(Mandatory=$false)]
    [switch]$Foreground
)

# Server Configuration
$Servers = @{
    "prompt_generator" = @{
        "module" = "src.prompt_generator_mcp:app"
        "port" = 8000
        "description" = "Prompt Generator Server"
    }
    "stable_diffusion" = @{
        "module" = "src.stable_diffusion_mcp:app" 
        "port" = 8001
        "description" = "Stable Diffusion Image Generation Server"
    }
    "blender" = @{
        "module" = "src.blender_mcp:app"
        "port" = 8002
        "description" = "Blender Automation Server"
    }
    "env_manager" = @{
        "module" = "src.env_manager_mcp:app"
        "port" = 8003
        "description" = "Environment Management Server"
    }
    "github" = @{
        "module" = "src.github_mcp:app"
        "port" = 8004
        "description" = "GitHub Integration Server"
    }
}

# Global Variables
$global:RunningProcesses = @{}

function Start-MCPServer {
    param(
        [string]$ServerName,
        [bool]$Detached = $true
    )
    
    if (-not $Servers.ContainsKey($ServerName)) {
        Write-Host "Unknown server: $ServerName" -ForegroundColor Red
        return $false
    }
    
    $config = $Servers[$ServerName]
    
    $arguments = @(
        "-m", "uvicorn",
        $config.module,
        "--host", "0.0.0.0",
        "--port", $config.port.ToString(),
        "--reload",
        "--log-level", "info"
    )
    
    Write-Host "Starting $($config.description) on port $($config.port)..." -ForegroundColor Yellow
    
    try {
        $condaArgs = @("run", "-n", "mcp_env", "python") + $arguments
        
        if ($Detached) {
            $process = Start-Process -FilePath "C:/Users/loved/miniconda3/Scripts/conda.exe" -ArgumentList $condaArgs -PassThru -WindowStyle Hidden
        } else {
            $process = Start-Process -FilePath "C:/Users/loved/miniconda3/Scripts/conda.exe" -ArgumentList $condaArgs -PassThru -NoNewWindow
        }
        
        $global:RunningProcesses[$ServerName] = $process
        
        Start-Sleep -Seconds 3
        
        if (-not $process.HasExited) {
            Write-Host "Server $ServerName started successfully (PID: $($process.Id))" -ForegroundColor Green
            return $true
        } else {
            Write-Host "Failed to start server $ServerName" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "Error starting server $ServerName : $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Stop-MCPServer {
    param([string]$ServerName)
    
    if ($global:RunningProcesses.ContainsKey($ServerName)) {
        $process = $global:RunningProcesses[$ServerName]
        
        try {
            if (-not $process.HasExited) {
                $process.Kill()
                $process.WaitForExit(5000)
            }
            Write-Host "Server $ServerName stopped" -ForegroundColor Yellow
        }
        catch {
            Write-Host "Server $ServerName force terminated" -ForegroundColor Red
        }
        finally {
            $global:RunningProcesses.Remove($ServerName)
        }
    }
}

function Start-AllServers {
    param([bool]$Detached = $true)
    
    Write-Host "Starting all MCP servers..." -ForegroundColor Yellow
    
    $successCount = 0
    foreach ($serverName in $Servers.Keys) {
        if (Start-MCPServer -ServerName $serverName -Detached $Detached) {
            $successCount++
        }
        Start-Sleep -Seconds 2
    }
    
    Write-Host "Successfully started $successCount/$($Servers.Count) servers" -ForegroundColor Green
    
    if ($successCount -gt 0) {
        Write-Host "Running servers:" -ForegroundColor Cyan
        foreach ($name in $Servers.Keys) {
            if ($global:RunningProcesses.ContainsKey($name)) {
                $config = $Servers[$name]
                Write-Host "  $($config.description): http://localhost:$($config.port)" -ForegroundColor White
            }
        }
    }
    
    return $successCount
}

function Stop-AllServers {
    Write-Host "Stopping all servers..." -ForegroundColor Yellow
    
    foreach ($serverName in @($global:RunningProcesses.Keys)) {
        Stop-MCPServer -ServerName $serverName
    }
    
    Write-Host "All servers stopped" -ForegroundColor Green
}

function Show-ServerStatus {
    Write-Host "Server Status:" -ForegroundColor Cyan
    
    foreach ($serverName in $Servers.Keys) {
        $config = $Servers[$serverName]
        
        if ($global:RunningProcesses.ContainsKey($serverName)) {
            $process = $global:RunningProcesses[$serverName]
            if (-not $process.HasExited) {
                $status = "Running (PID: $($process.Id))"
                $color = "Green"
            } else {
                $status = "Stopped"
                $color = "Red"
                $global:RunningProcesses.Remove($serverName)
            }
        } else {
            $status = "Stopped"
            $color = "Red"
        }
        
        Write-Host "  $($config.description): $status" -ForegroundColor $color
    }
}

# Ctrl+C handler
$null = Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action {
    Write-Host "Exit signal received. Cleaning up servers..." -ForegroundColor Yellow
    Stop-AllServers
}

# Main Logic
switch ($Action) {
    "start" {
        if ($Server) {
            $success = Start-MCPServer -ServerName $Server -Detached (-not $Foreground)
            if ($success -and -not $Foreground) {
                Write-Host "Server running in background. Stop with: .\run_servers.ps1 -Action stop -Server $Server" -ForegroundColor Cyan
            }
        } else {
            $successCount = Start-AllServers -Detached (-not $Foreground)
            if ($successCount -gt 0 -and -not $Foreground) {
                Write-Host "Servers running in background." -ForegroundColor Cyan
                Write-Host "Stop all servers: .\run_servers.ps1 -Action stop" -ForegroundColor Cyan
                Write-Host "Check status: .\run_servers.ps1 -Action status" -ForegroundColor Cyan
                
                if (-not $Foreground) {
                    Write-Host "Press Ctrl+C to monitor and exit..." -ForegroundColor Yellow
                    try {
                        while ($true) {
                            Start-Sleep -Seconds 1
                        }
                    }
                    catch {
                        # Ctrl+C handling
                    }
                }
            }
        }
    }
    
    "stop" {
        if ($Server) {
            Stop-MCPServer -ServerName $Server
        } else {
            Stop-AllServers
        }
    }
    
    "status" {
        Show-ServerStatus
    }
    
    "restart" {
        if ($Server) {
            Write-Host "Restarting server $Server..." -ForegroundColor Yellow
            Stop-MCPServer -ServerName $Server
            Start-Sleep -Seconds 1
            Start-MCPServer -ServerName $Server -Detached (-not $Foreground)
        } else {
            Write-Host "Restarting all servers..." -ForegroundColor Yellow
            Stop-AllServers
            Start-Sleep -Seconds 2
            Start-AllServers -Detached (-not $Foreground)
        }
    }
}