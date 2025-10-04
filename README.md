Here’s a README-friendly version of your instructions:

---

# SmartMedical Booking API

This guide explains how to set up the application using Docker Compose and how to interact with the SmartMedical Booking API.

---

## 🛠 Setup

1. **Build the Docker Image:**

```shell script
docker compose build web
```


2. **Start the Service:**

```shell script
docker compose up -d
```


3. **Check Running Containers:**

```shell script
docker compose ps
```


---

## 🗓 Retrieve Timetable

The `timetable` endpoint provides the current schedule data. Use the following command to call it:

```textmate
Invoke-RestMethod -Method Get -Uri "http://localhost:8080/timetable" -Headers @{"x-api-key"="dev-api-key"} | ConvertTo-Json -Depth 10
```


**Note:** Replace `dev-api-key` with the actual API key if required.

---

## 📅 Create a Booking

Follow these steps to create a new booking via the API.

1. **Define the API Endpoint and API Key:**

```textmate
$Uri = "http://localhost:8080/book"
$Headers = @{"x-api-key" = "dev-api-key"}  # Replace with the correct API key as needed
```


2. **Define the Booking Payload:**

```textmate
$Body = @{
       date = "2025-10-10"
       time = "12:00"
       first_name = "Test"
       last_name = "User"
       phone = "+37100000000"
       notes = "PyTest booking trial - safe no-submit"
   } | ConvertTo-Json -Depth 10
```


3. **Send the POST Request:**

```textmate
Invoke-RestMethod -Method Post -Uri $Uri -Headers $Headers -Body $Body -ContentType "application/json"
or
Invoke-RestMethod -Method Post -Uri "http://localhost:8080/book" -Headers @{"x-api-key"="dev-api-key"} -Body (@{date="2025-10-10"; time="12:00"; first_name="Test"; last_name="User"; phone="+37100000000"; notes="PyTest booking trial - safe no-submit"} | ConvertTo-Json -Depth 10) -ContentType "application/json"
```


---

## 🔧 Debugging

1. Ensure that the Docker container is running (`docker compose ps`).
2. Verify that the API key is valid for your setup.
3. Check the application logs to identify any backend issues.

---

With these steps, you'll be able to set up the API and interact with its endpoints. For more information, refer to the official documentation or contact support. Let us know if you run into issues! 🚀