docker compose build web

docker compose up -d

docker compose ps

Invoke-RestMethod -Method Get -Uri "http://localhost:8080/timetable" -Headers @{"x-api-key"="dev-api-key"} | ConvertTo-Json -Depth 10
