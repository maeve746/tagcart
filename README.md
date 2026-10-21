# TagCart

TagCart is split into an existing React/Vite seller dashboard and a separate FastAPI service.

```text
tagcart/
├── frontend/   React + Tailwind seller dashboard
└── backend/    FastAPI + Supabase service
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite development server runs at `http://localhost:5173` by default.

## Backend

Python 3.9 or newer is required.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

Set `SUPABASE_URL` and the server-only `SUPABASE_SECRET_KEY` in `backend/.env`, then start the API:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Available checks:

- `GET http://127.0.0.1:8000/health` confirms FastAPI is running.
- `GET http://127.0.0.1:8000/health/db` performs a minimal `SELECT id` against the future `public.profiles` table.
- `/docs` exposes FastAPI's local OpenAPI interface.

Before Supabase variables are configured, `/health/db` returns `503 not_configured`. If Supabase responds but `public.profiles` has not been created by a future migration, it returns `503 migrations_pending`. No tables or authentication flows are created by this setup.

Keep `SUPABASE_SECRET_KEY` exclusively in the backend environment. Never add it to frontend code or any `VITE_` variable.

## Marketplace connections

Apply [the marketplace migration](backend/supabase/migrations/202610210001_marketplace_connections.sql) with your normal Supabase migration workflow before using these endpoints. It creates connection metadata, hashed one-time OAuth state, RLS policies and an atomic state-consumption function. Marketplace tokens are encrypted by FastAPI with `MARKETPLACE_TOKEN_ENCRYPTION_KEY` before they reach Supabase.

All browser-initiated marketplace routes require a valid Supabase access token:

```text
Authorization: Bearer <supabase-user-access-token>
```

Routes:

- `GET /api/marketplaces/status`
- `POST /api/marketplaces/amazon/connect`
- `GET /api/marketplaces/amazon/callback`
- `GET /api/marketplaces/myntra/configuration`
- `POST /api/marketplaces/myntra/connect`

Amazon redirects to the callback without the application's bearer header. That callback is authenticated with a cryptographically random, hashed, user-bound, single-use state value that expires after ten minutes. It never returns LWA tokens to the browser.

No marketplace publishing operation is implemented.

## Mock marketplace submissions

Set this in `backend/.env` for the college/demo workflow:

```dotenv
MARKETPLACE_MODE=mock
```

Mock mode is offline: it never calls Amazon or Myntra, does not require seller credentials, and never represents a product as published or live. The generated Amazon JSON and Myntra XLSX structures are clearly labeled TagCart illustrations; they are not claims of full marketplace-schema compliance. Production connection adapters remain available only when `MARKETPLACE_MODE=production`, while production listing submission is deliberately not implemented.

All routes below require `Authorization: Bearer <supabase-user-access-token>`:

- `POST /api/marketplaces/{marketplace}/listings/{listing_id}/validate`
- `POST /api/marketplaces/{marketplace}/listings/{listing_id}/submit`
- `GET /api/marketplaces/submissions`
- `GET /api/marketplaces/submissions/{submission_id}`
- `POST /api/marketplaces/submissions/{submission_id}/advance`
- `GET /api/marketplaces/amazon/listings/{listing_id}/sample.json`
- `GET /api/marketplaces/myntra/listings/{listing_id}/sample.xlsx`

Supported mock marketplace names are `amazon` and `myntra`. Submission starts at `accepted`; each explicit `advance` moves it to `processing`, then to a deterministic `completed` or `rejected` result. These are simulation states only.

Before using these routes:

1. A real backend `public.listings` table must already exist with `id uuid`, `user_id uuid`, and textual `status`, plus the listing fields used for validation. Frontend localStorage data is not accepted as proof of ownership or approval.
2. Apply [the marketplace submissions migration](backend/supabase/migrations/202610210002_marketplace_submissions.sql). It intentionally fails with a clear prerequisite error if `public.listings` is absent. It has not been assumed to be applied.
3. Store listings with the authenticated user's `user_id`; only a case-insensitive `approved` status can be submitted.
4. Configure `SUPABASE_URL` and the server-only `SUPABASE_SECRET_KEY`. Do not expose the secret key to the frontend.

The migration creates `marketplace_submissions`, `marketplace_submission_history`, ownership-preserving foreign keys, indexes, read-only owner RLS policies, and service-role-only atomic functions for creating and advancing simulations. Missing tables return an explicit `503 marketplace_submissions_migration_pending`; the API does not substitute in-memory success.

### Amazon SP-API prerequisites

TagCart still needs all of the following from an approved Amazon SP-API application:

- An active Professional Seller account and Solution Provider Portal developer registration.
- Amazon approval for every required SP-API role. Future listing publication will require the applicable Product Listing role; restricted roles require additional review if later used.
- The SP-API application ID, LWA client ID and LWA client secret.
- The exact regional Seller Central base URL for the sellers being connected.
- A registered redirect URI exactly matching `AMAZON_OAUTH_REDIRECT_URI`.
- For a public multi-seller application, Amazon Appstore publication/approval. Draft testing uses `AMAZON_APP_IS_DRAFT=true`; production must disable it.
- Each seller must grant the application permission through Amazon's Login with Amazon seller authorization flow.

The adapter follows Amazon's documented Seller Central consent and LWA authorization-code exchange. Only the long-lived refresh token is persisted, encrypted; short-lived access tokens are not returned or logged.

### Myntra Partner API prerequisites

TagCart still needs all values issued during Myntra MMIP/PPMP or Omni partner onboarding:

- Myntra partner approval and API access for the intended seller/merchant.
- The partner-specific API base URL supplied by Myntra.
- The Myntra merchant ID and shared secret key.
- Approval for the required API capabilities and seller stores. Listing or inventory permissions are not assumed.
- Confirmation from Myntra whether the merchant is enabled for PPMP, Omni and/or Listing Management APIs.

The connection adapter calls only Myntra's documented one-time `POST /authorization/generate_token` operation, using the `secret_key` request header and `merchant_id` JSON field. Myntra's documented `access_token` and `refresh_token` response headers are stored encrypted. The access token is marked with the documented 30-day lifetime. The API base URL is required from Myntra and is intentionally not guessed.

### Running tests

Tests use pytest plus mocked/in-memory boundaries; they do not contact Amazon, Myntra or Supabase. The earlier adapter tests remain compatible because pytest collects `unittest.TestCase` suites.

```bash
cd backend
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Protocol references:

- [Amazon SP-API website authorization workflow](https://developer-docs.amazon.com/sp-api/docs/website-authorization-workflow)
- [Amazon SP-API LWA token exchange](https://developer-docs.amazon.com/sp-api/docs/connecting-to-the-selling-partner-api)
- [Myntra Developer Centre](https://mmip.myntrainfo.com/)
- [Myntra Listing Management partner-token documentation](https://www.postman.com/myntra-pretr/myntra-pretr-api-s-public-workspace/documentation/2uq4865/partner-integration-layer-for-listing-management)
