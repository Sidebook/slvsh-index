To index all new SLVSH matches:

```
python -m index_builder.main all
```

If any error occurs with youtube downloads, try updating yt-dlp to the latest version (Rebuild a dev container)

## Production hosting

The frontend is a static Next.js export on Firebase Hosting (`slvsh-indexx`),
served at https://slvshindex.ruwy.app. `/api/**` rewrites to the
`slvsh-index-backend` Cloud Run service in Tokyo (`asia-northeast1`).
The API image is also stored in Artifact Registry in Tokyo.

Pushes to `main` run `frontend/cloudbuild.yaml` for Hosting and
`cloudbuild.backend.yaml` for the API. The frontend uses the same-origin API
URL in production. No external load balancer or Cloud Armor policy is needed
for this configuration.

Manual frontend deployment after `npm ci && npm run build` in `frontend/`:

```sh
npx firebase-tools@15.34.0 deploy --only hosting --project slvsh-indexx
```
