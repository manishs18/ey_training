# NutriGuard AI

Local-first NutriGuard setup:

- Frontend: React + Vite
- Backend API: FastAPI
- AI Orchestrator: FastAPI + LangGraph + Gemini
- Database: PostgreSQL through Docker
- Queue pattern: local `outbox_events` table first
- RAG: mock local retriever first

## Local Architecture

```text
React frontend
  -> Backend API
  -> PostgreSQL
  -> outbox_events table
  -> backend local outbox publisher
  -> AI Orchestrator /process-meal with full-day meal timeline
  -> LangGraph agents
  -> Gemini API
  -> PostgreSQL day-aware report + flags
  -> frontend polls daily report
```

For local development, Azure Service Bus is not required. The backend starts a background outbox publisher automatically.

## Ports

```text
Frontend:        http://localhost:5173
Backend API:     http://localhost:8000
AI Orchestrator: http://localhost:8001
PostgreSQL host: localhost:5434
PostgreSQL Docker container port: 5432
```

Postgres uses host port `5434` because local `5432` may already be occupied.

## Environment

Backend local database URL:

```text
postgresql://nutriguard_user:nutriguard_pass@localhost:5434/nutriguard_db
```

Backend local settings:

```text
AI_ORCHESTRATOR_URL=http://localhost:8001
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
ENABLE_OUTBOX_PUBLISHER=true
OUTBOX_PUBLISH_INTERVAL_SECONDS=5
```

AI orchestrator uses:

```text
GEMINI_MODEL=gemini-3-flash-preview
USE_MOCK_RAG=true
```

## Start Local Services

Start PostgreSQL:

```bash
cd infra
docker compose up -d postgres
```

Start the AI orchestrator:

```bash
cd services/ai-orchestrator
python -m uvicorn app.main:app --reload --port 8001
```

Start the backend API:

```bash
cd services/backend-api
python -m uvicorn app.main:app --reload --port 8000
```

The backend starts the local outbox publisher automatically. It reads `PENDING` events, sends the full day meal timeline to the AI orchestrator, saves flags and reports, then marks meals `COMPLETED`.

Start the frontend:

```bash
cd frontend
npm install
npm run dev
```

The frontend includes signup/login, health profile setup, report text upload/paste, meal logging, report polling, and meal history.

## Local Test Flow

Create a user:

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Manish",
    "email": "manish@example.com",
    "password": "strongpass123"
  }'
```

Login:

```bash
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "manish@example.com",
    "password": "strongpass123"
  }'
```

Create a profile:

Use the `id` returned by `POST /users` in place of `1` if your database already has users.

```bash
curl -X POST http://localhost:8000/users/1/profile \
  -H "Content-Type: application/json" \
  -d '{
    "goals": ["fat_loss", "reduce_deficiency"],
    "diet_type": "vegetarian",
    "health_conditions": ["iron_deficiency"],
    "deficiencies": ["iron_deficiency", "vitamin_d"],
    "supplements": ["iron_tablet"]
  }'
```

Submit a meal:

Use the same user id in `user_id`.

```bash
curl -X POST http://localhost:8000/meals \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "meal_type": "breakfast",
    "meal_time": "2026-06-22T08:30:00+05:30",
    "foods_text": "poha",
    "drinks_text": "tea",
    "supplements_text": "iron tablet",
    "notes_text": "small portion"
  }'
```

Check the report:

```bash
curl http://localhost:8000/meals/1/report
```

Check the latest day-level report:

```bash
curl http://localhost:8000/users/1/daily-report
```

Check the full day timeline with each meal's progressive combined report:

```bash
curl http://localhost:8000/users/1/daily-report/details
```

If the meal is still being processed, the report endpoint returns the current meal status. Poll it again after a few seconds.

## Automatic Processing Flow

When `POST /meals` is called:

1. Backend saves the meal in `meal_logs` with status `RECEIVED`.
2. Backend creates a `MealLogged` event in `outbox_events` with status `PENDING`.
3. The backend background publisher picks up the event.
4. The publisher reads the user's profile from `user_profiles`.
5. The publisher adds uploaded health report text, previous-meal timing context, and the full day meal timeline.
6. The publisher calls AI Orchestrator `POST /process-meal`.
7. The orchestrator runs LangGraph:
   - Meal Analyzer Agent
   - Health Risk Agent
   - Report Agent
8. The publisher saves day-aware `nutrition_flags` and `daily_reports`.
9. The publisher sets `meal_logs.status = COMPLETED`.
10. The publisher sets `outbox_events.status = PUBLISHED`.

The day timeline lets the agent catch combinations across logs, such as tea near an iron tablet or dahi/paneer/calcium-rich foods soon after an iron supplement.

## Run All With Docker Compose

```bash
cd infra
docker compose up --build
```

Inside Docker, services use the internal Postgres host:

```text
postgresql://nutriguard_user:nutriguard_pass@postgres:5432/nutriguard_db
```

## Azure deployment with GitHub Actions CI/CD

This repository includes a GitHub Actions workflow that builds the backend, orchestrator, and frontend Docker images, pushes them to Azure Container Registry, and deploys them to Azure App Service.

### 1. Prepare Azure resources

Create a resource group, ACR, PostgreSQL, and three App Services (Linux container):

```bash
az login
az group create --name NutriguardRG --location eastus
az acr create --resource-group NutriguardRG --name nutriguardacr --sku Standard
az postgres flexible-server create --resource-group NutriguardRG --name nutriguardpg --location eastus --admin-user nutriguard_user --admin-password "YourStrongPass1!" --sku-name Standard_B1ms --tier Burstable --storage-size 32
az appservice plan create --name NutriguardPlan --resource-group NutriguardRG --is-linux --sku B1
az webapp create --resource-group NutriguardRG --plan NutriguardPlan --name nutriguard-backend --deployment-container-image-name nginx
az webapp create --resource-group NutriguardRG --plan NutriguardPlan --name nutriguard-orchestrator --deployment-container-image-name nginx
az webapp create --resource-group NutriguardRG --plan NutriguardPlan --name nutriguard-frontend --deployment-container-image-name nginx
```

### 2. Create a GitHub service principal

Generate Azure credentials and save them as the `AZURE_CREDENTIALS` secret in GitHub:

```bash
az ad sp create-for-rbac --name "nutriguard-github" --role contributor --scopes /subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/NutriguardRG --sdk-auth
```

Copy the JSON output into the GitHub secret `AZURE_CREDENTIALS`.

### 3. Set required GitHub secrets

In GitHub repository Settings > Secrets and variables > Actions add:

- `AZURE_CREDENTIALS` — JSON from `az ad sp create-for-rbac`
- `AZURE_RESOURCE_GROUP` — `NutriguardRG`
- `ACR_NAME` — `nutriguardacr`
- `ACR_LOGIN_SERVER` — `nutriguardacr.azurecr.io`
- `ACR_USERNAME` — ACR username from Azure
- `ACR_PASSWORD` — ACR password from Azure
- `BACKEND_APP_NAME` — `nutriguard-backend`
- `ORCHESTRATOR_APP_NAME` — `nutriguard-orchestrator`
- `FRONTEND_APP_NAME` — `nutriguard-frontend`

### 4. Set App Service environment variables

Your backend and orchestrator containers need runtime variables. In the Azure Portal, open each App Service and add:

Backend app settings:
- `DATABASE_URL` = `postgresql://nutriguard_user:YourStrongPass1!@<postgres-host>:5432/nutriguard_db`
- `AI_ORCHESTRATOR_URL` = `http://<orchestrator-app-service-name>.azurewebsites.net`
- `CORS_ORIGINS` = `https://<frontend-app-service-name>.azurewebsites.net`
- `ENABLE_OUTBOX_PUBLISHER` = `true`
- `OUTBOX_PUBLISH_INTERVAL_SECONDS` = `5`

AI orchestrator app settings:
- `DATABASE_URL` = same PostgreSQL URL as backend
- `GEMINI_API_KEY` = your Gemini API key
- `GEMINI_MODEL` = `gemini-3-flash-preview`

Frontend app settings are not required for the static Docker image.

### 5. Push to GitHub

Push your code to `main`. The workflow `.github/workflows/azure-cicd.yml` will:

- build Docker images for backend, orchestrator, frontend
- push them to ACR
- configure each App Service container image
- restart each app

### 6. Open the deployed app

After deployment, open the frontend app URL from Azure. Verify backend and orchestrator are healthy by checking Azure logs and the running apps.

### Troubleshooting

- If the workflow fails, open Actions > workflow run for the exact error.
- If the app is blank, verify App Service settings and that the backend can access PostgreSQL.
- Use `az webapp log tail --name <app-name> --resource-group NutriguardRG` for runtime logs.

