# SLVSH INDEX frontend

Production is a static Next.js export deployed to Firebase Hosting. API requests
use `/api/**`, which Hosting rewrites to Cloud Run in Tokyo (`asia-northeast1`).

## Local development

Run the backend on port 8000, then run:

```sh
npm ci
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

## Build and deploy

```sh
npm ci
npm run build
npx firebase-tools@15.34.0 deploy --only hosting --project slvsh-indexx
```

`cloudbuild.yaml` performs these steps automatically on pushes to `main`.
The `out/` directory contains the deployable site.
