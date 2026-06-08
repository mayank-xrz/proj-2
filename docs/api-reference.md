# API Reference

Interactive Swagger docs are available at `http://localhost:8000/docs` when the backend is running.

## Authentication

Currently the API is unauthenticated (designed for internal/trusted network use). For production, add JWT or API key middleware before the router.

## Endpoints

### Health

#### `GET /health`

Returns service health status.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-06-08T12:00:00Z",
  "version": "1.0.0"
}
```

---

### Webhooks

#### `POST /api/v1/webhooks/omnidim`

Receives post-call events from OmniDimension. The server must respond with HTTP 200.

**Headers:**
- `X-Omnidim-Signature`: HMAC-SHA256 signature (verified against `OMNIDIM_WEBHOOK_SECRET`)

**Body:** OmniDimension post-call payload (see [webhook schema](../backend/app/schemas/webhook.py))

---

### Calls

#### `GET /api/v1/calls`

List call logs, newest first.

**Query params:**
- `skip` (int, default 0): pagination offset
- `limit` (int, default 50, max 200): page size

**Response:**
```json
{
  "total": 25,
  "items": [
    {
      "id": "uuid",
      "omnidim_call_id": "omni_abc123",
      "caller_number": "+15550001234",
      "caller_name": "Jane Smith",
      "status": "completed",
      "outcome": "appointment_booked",
      "duration_seconds": 185.0,
      "summary": "Caller booked a routine cleaning for Tuesday at 10am.",
      "started_at": "2025-06-08T10:30:00Z",
      "ended_at": "2025-06-08T10:33:05Z",
      "created_at": "2025-06-08T10:30:00Z"
    }
  ]
}
```

**Call outcomes:** `appointment_booked` | `faq_answered` | `transferred` | `voicemail` | `hung_up` | `unknown`

#### `GET /api/v1/calls/{id}`

Get a single call log by its internal UUID.

---

### Appointments

#### `GET /api/v1/appointments`

List appointments, upcoming first.

**Query params:**
- `skip`, `limit`: pagination
- `status`: filter by status (`pending` | `confirmed` | `cancelled` | `completed` | `no_show`)

#### `POST /api/v1/appointments`

Manually create an appointment.

**Body:**
```json
{
  "patient_name": "Jane Smith",
  "patient_phone": "+15550001234",
  "patient_email": "jane@example.com",
  "service": "Routine Cleaning",
  "appointment_dt": "2025-07-15T10:00:00",
  "duration_minutes": 45,
  "notes": "First-time patient",
  "price_usd": 120.0
}
```

#### `PATCH /api/v1/appointments/{id}`

Partial update. All fields optional.

```json
{
  "status": "cancelled",
  "appointment_dt": "2025-07-16T11:00:00"
}
```

#### `DELETE /api/v1/appointments/{id}`

Cancel an appointment (sets status to `cancelled`). Returns 204 No Content.

---

### FAQ

#### `GET /api/v1/faq`

Return all FAQ entries from `business_config.yaml`.

#### `POST /api/v1/faq/query`

Find the best matching FAQ answer for a question.

**Body:**
```json
{ "question": "Do you accept insurance?" }
```

**Response:**
```json
{
  "question": "Do you accept insurance?",
  "answer": "Yes, we accept Delta Dental, Cigna...",
  "confidence": 0.872,
  "matched": true
}
```
