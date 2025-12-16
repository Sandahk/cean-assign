# Cean Tech Interview – Quote Manager

This project is a minimal full-stack "Quote Manager" for sales reps to build quotes for ACME Inc.  
It uses **FastAPI** (Python) for the backend, **Postgres** as database (via Docker Compose), and a minimal **React + Vite + TypeScript** frontend.

---

## 🚀 Quick Start

### 1. Clone the Repo

```bash
git clone <your-repo-url>
cd <repo-root>
```

### 2. Run Backend & Database (Docker Compose)

Make sure you have Docker & Docker Compose installed.

```bash
docker compose up --build
```
- This starts:
  - Postgres database (`db` on port 5432)
  - FastAPI backend (`backend` on port 8000, hot-reloading)

The backend will **seed demo products and a kit** into the database on first run.

### 3. Run the Frontend (Vite + React)

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```
- Access the UI at [http://localhost:5173](http://localhost:5173)

### 4. (Optional) Run Frontend Simulation Script

To test the backend API without a full frontend, use:

```bash
python frontend_simulation.py
```
This script mimics a user: fetches products, builds a quote (with colors/kits), posts it, and fetches results.

---

## 🛠️ Project Structure

```
backend/
  app.py             # FastAPI app (models, endpoints, seed logic)
  requirements.txt
  Dockerfile

frontend/
  src/App.tsx        # Main frontend logic
  ...
frontend_simulation.py  # Python script to simulate frontend

docker-compose.yml      # Launches backend & Postgres
README.md
```

---

## 🗃️ Database Schema

- **Product**: `id`, `name`, `price`, `has_colors`, `colors`, `is_kit`, `kit_components`
- **Quote**: `id`, `customer`, `total`
- **QuoteItem**: `id`, `quote_id`, `product_id`, `quantity`, `color`, `order`, `is_kit_component`

**Kits** are special products that expand into component items (products). Custom kit ordering is supported in the quote.

---

## 🛣️ API Endpoints

### **Backend (FastAPI, port 8000)**
- `GET /products`  
  Get list of products and kits.
- `POST /quotes`  
  Create a quote.  
  **Body:**
  ```json
  {
    "customer": "Alice",
    "items": [
      {"product_id": 1, "quantity": 2},
      {"product_id": 2, "quantity": 1, "color": "white"},
      {"product_id": 4, "quantity": 1, "kit_order": [3, 1]}
    ]
  }
  ```
- `GET /quotes/{id}`  
  Get details for a specific quote.

**API docs available at:**  
[http://localhost:8000/docs](http://localhost:8000/docs)

---

## 💡 Design Decisions

- **Seeding**: On first run, the backend seeds representative products and a kit.
- **Kits**: Kits are products composed of other products; on quote creation, kits are expanded into their components. User-defined order is supported and persisted per quote.
- **Colors**: Products can support multiple colors; color selection is enforced and stored per line item.
- **Minimal frontend**: UI is intentionally basic to focus on API and logic clarity; core requirements covered.
- **Frontend simulation**: `frontend_simulation.py` allows demoing API flow without full UI.

---

## ⚡ Core Flow

1. User fetches products/kits.
2. Adds products/kits (selecting color if needed) to a quote.
3. For kits, user can reorder kit components (order is saved).
4. Creates the quote.
5. Views created quote: items, quantities, colors, kit expansion, and total.

---

## 📦 How to Reset/Reseed Database

If you need to reset data, stop Docker, delete the Docker volume or Postgres data folder, and re-run `docker compose up --build`.

---

## ✨ Future Improvements

- Add authentication & user management
- Support editing/deleting quotes
- Enhance frontend with shadcn/ui components and validation
- Add product/kit management endpoints

---

**Contact:**  
Sepaseh (Sanda) Hakiminejad  
[sanda.hakimi@gmail.com](mailto:sanda.hakimi@gmail.com) | [LinkedIn](http://www.linkedin.com/in/sepaseh-sanda-hakiminejad)
