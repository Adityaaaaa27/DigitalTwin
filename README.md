# Mental Health Digital Twin — API

A production-ready backend for explainable mental-health risk scoring powered by a Bayesian Network.

## Quick Start

```bash
# 1. Install dependencies
pip install --prefer-binary -r requirements.txt

# 2. Start the server
uvicorn main:app --reload
```

Open the interactive API docs at: **http://localhost:8000/docs**

---

## Project Structure

```
pgm/
├── main.py                          # FastAPI app + startup
├── config.py                        # Env-var driven configuration
├── requirements.txt
└── app/
    ├── models/
    │   └── bayesian_model.py        # pgmpy Bayesian Network + inference
    ├── services/
    │   ├── prediction_service.py    # Input discretisation + inference
    │   ├── explanation_service.py   # XAI via feature perturbation
    │   ├── trend_service.py         # Moving avg + linear regression
    │   └── recommendation_service.py# Alerts + recommendations
    ├── database/
    │   ├── schema.py                # DDL + connection factory
    │   └── db.py                    # Repository (insert / fetch)
    └── routes/
        ├── predict.py               # POST /predict
        ├── history.py               # GET  /history/{user_id}
        └── future.py                # GET  /future/{user_id}
```

---

## API Reference

### `POST /predict`

Run inference for a user and persist the result.

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "user_id":     "alice",
    "sleep":       3.0,
    "stress":      8.0,
    "social":      2.0,
    "workload":    9.0,
    "screen_time": 8.0,
    "exercise":    1.0
  }'
```

**Response:**
```json
{
  "user_id": "alice",
  "risk_score": 0.8747,
  "anxiety_probability": 0.9091,
  "depression_probability": 0.9091,
  "explanation": {
    "stress": 0.1667,
    "sleep": 0.1667,
    "workload": 0.1667,
    "screen_time": 0.1667,
    "social": 0.1667,
    "exercise": 0.1667
  },
  "alerts": [],
  "recommendations": [
    "🛌 Your sleep score is low ...",
    "🧘 High stress detected ..."
  ]
}
```

---

### `GET /history/{user_id}?limit=50`

Retrieve stored records + smoothed moving-average trend.

```bash
curl http://localhost:8000/history/alice
```

---

### `GET /future/{user_id}`

Predict the next 3 risk values using linear regression.

```bash
curl http://localhost:8000/future/alice
```

**Response:**
```json
{
  "user_id": "alice",
  "history_points": 7,
  "future_risk": [0.8747, 0.8747, 0.8747],
  "trend_direction": "stable"
}
```

---

## Input Schema

All values are in the range **[0, 10]**:

| Field | Description | High value means |
|---|---|---|
| `sleep` | Sleep quality | Good (protective) |
| `stress` | Perceived stress | Bad (risk) |
| `social` | Social engagement | Good (protective) |
| `workload` | Work intensity | Bad (risk) |
| `screen_time` | Daily screen time | Bad (risk) |
| `exercise` | Physical activity | Good (protective) |

---

## Bayesian Network

```
Sleep ──┐  Stress ──┐  Social ──┬──► Anxiety ──┐
         │           │           │                ├──► Risk
Workload─┤  Exercise─┘  ScreenTime              │
         └──────────────────────────► Depression─┘
```

Inference: `pgmpy.inference.VariableElimination`  
States: `Low=0 | Medium=1 | High=2`

---

## Configuration (env vars)

| Variable | Default | Description |
|---|---|---|
| `SQLITE_PATH` | `./mental_health.db` | DB file path |
| `TREND_WINDOW` | `5` | Moving-average window |
| `FUTURE_STEPS` | `3` | Future predictions |
| `ALERT_CONSECUTIVE_INCREASE` | `3` | Alert trigger count |
| `LOW_THRESHOLD` | `3.5` | Discretisation boundary |
| `HIGH_THRESHOLD` | `6.5` | Discretisation boundary |

---

## Cloud Deployment (AWS)

The codebase is designed for easy migration:

1. **Replace database**: Swap `app/database/db.py` for a DynamoDB / RDS adapter — all services use the same function signatures.
2. **Containerise**: `uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4`
3. **Deploy**: ECS Fargate, Elastic Beanstalk, or Lambda (with Mangum adapter).
4. **Config**: Pass env vars via ECS Task Definition or Parameter Store.
