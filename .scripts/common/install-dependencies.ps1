# PowerShell script to install dependencies

# Get the script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# Execute the services dependencies installation script
& "$scriptPath\install-dependencies-services.ps1"

# Execute the web dependencies installation script
& "$scriptPath\install-dependencies-web.ps1" 
