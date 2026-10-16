# MoJobs Backend API

> A high-performance, multi-domain marketplace backend engineered with **Django REST Framework**, **PostgreSQL**, **Docker**, and **Safaricom M-Pesa STK Push**.

MoJobs is a unified digital economy backend serving the localized gig economy, job dispatching, business advertising, and peer-to-peer e-commerce marketplace ecosystem.

---

## 🏛️ Core Architecture & Domain Separation

The system is designed as a **modular monolith** with clean context boundaries isolating core business domains:

| Domain Module     | Primary Architecture & Key Responsibilities                                                                                |
| :---------------- | :------------------------------------------------------------------------------------------------------------------------- |
| **`accounts`**    | Role-based access control (`FUNDI`, `CLIENT`, `BUSINESS`, `SELLER`) managed via custom JWT lifecycle authentication.       |
| **`fundis`**      | Gig directory with automated 7-day trial windows, gated job access rules, and public directory visibility toggles.         |
| **`marketplace`** | Peer-to-peer seller marketplace powered by an automated tiered fee calculation engine based on historical inventory state. |
| **`jobs`**        | Paid job dispatch system requiring payment verification before public distribution and application access.                 |
| **`ads`**         | Targeted advertisement placement engine with pay-to-publish workflows.                                                     |
| **`payments`**    | Centralized ledger and webhook callback processor for Safaricom M-Pesa (Daraja) STK Push.                                  |

---

## 💡 Engine Highlights & Technical Depth

### 1. Dynamic Marketplace Tiered Fee Engine

To maximize seller onboarding while maintaining platform revenue, the marketplace engine dynamically computes item listing fees contextually utilizing Python’s exact `Decimal` arithmetic:

- **Low-Value Inventory (< KES 5,000.00):** First item listed is **100% free** to incentivize onboarding; subsequent low-value items incur a flat `KES 50.00` fee.
- **High-Value Inventory (≥ KES 5,000.00):** First luxury/high-ticket item incurs a `5%` platform listing fee; subsequent high-value items scale to a `10%` platform fee.
- **Automated Onboarding State:** Django Signals automatically handle state transitions (`is_paid=True`, `is_active=True`) for first-time free listings, avoiding redundant payment gateway calls.

### 2. Event-Driven M-Pesa Payment Pipeline

- **Asynchronous Webhooks:** Handled Safaricom M-Pesa STK Push integration with real-time asynchronous callbacks (`MPESA_CALLBACK_URL`).
- **Idempotency & State Integrity:** Validates incoming gateway callbacks to prevent double-crediting or duplicate processing during gateway retry attempts.
- **Domain Reaction:** On payment verification, the engine automatically updates domain models (`Subscription`, `Job`, `Ad`, `Item`) to unlock service features seamlessly.

---

## 🛠️ Tech Stack

- **Language:** Python 3.11+
- **Framework:** Django 5.x / Django REST Framework (DRF)
- **Database:** PostgreSQL
- **Authentication:** JWT (JSON Web Tokens with access/refresh token workflow)
- **Storage & CDN:** Cloudinary (Static/Media management via WhiteNoise/Cloudinary)
- **Integrations:** Safaricom M-Pesa Daraja API (STK Push)
- **DevOps & Infrastructure:** Docker, Docker Compose, Render

---

## ⚙️ Quickstart (Local Docker Environment)

### Prerequisites

- Docker Engine & Docker Compose installed locally.

### Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/<your-new-username>/mojobs-backend.git
   cd mojobs-backend
   ```

2. **Configure Environment Variables:**

   ```bash
   cp .env.example .env
   ```

   _Update `.env` with your database credentials and M-Pesa API keys._

3. **Spin Up Containers:**

   ```bash
   docker-compose up --build -d
   ```

4. **Apply Migrations:**

   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Create Superuser (Optional):**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

---

## 📡 API Documentation

Interactive OpenAPI/Swagger documentation is served directly from the application instance:

```text
http://localhost:8000/api/swagger-docs/
```

---

---

## 🧪 Testing Checklist

- [x] JWT Token Lifecycle (Register, Authenticate, Refresh)
- [x] Trial Access Control Gates (Active trial vs. Expired state)
- [x] Marketplace Fee Logic Edge Cases (First cheap item vs. subsequent items)
- [x] M-Pesa Callback Validation & Idempotence
- [x] Docker Container Orchestration & Health Checks

---

> _Note: This project was originally conceptualized, architected, and migrated from my previous developer profile (formerly under the working title **AjiriNow**)._
