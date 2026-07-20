# setup.ps1 - Levanta todo el sistema desde cero en cualquier PC
# Uso: .\setup.ps1

if (-not (Test-Path ".env")) {
    Write-Output "ERROR: No existe el archivo .env"
    Write-Output "Copia .env.example como .env y completa los valores."
    exit 1
}

Write-Output "=== Limpiando contenedores e imagenes anteriores ==="
docker compose down --volumes --remove-orphans
docker rmi backend_runner-nmap backend_runner-sqlmap backend_runner-nuclei backend_runner-xsstrike --force 2>$null

Write-Output ""
Write-Output "=== Construyendo y levantando todos los servicios ==="
docker compose up --build -d

Write-Output ""
Write-Output "=== Sistema listo ==="
Write-Output "api_gateway    -> http://localhost:8002/docs"
Write-Output "tool_registry  -> http://localhost:8003/docs"
Write-Output "tool_executor  -> http://localhost:8004/docs"
Write-Output ""
Write-Output "El seeder registrara las herramientas automaticamente."
Write-Output "Revisa los logs con: docker logs runner-seeder"
