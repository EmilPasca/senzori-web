# Cloud and Deployment Security

## Deployment source

The repository defines a Docker image and Docker Compose service:

- The Flask process listens on container port `5000` and Compose publishes host port `8001`.
- SQLite is stored in the `sqlite_data` volume mounted at `/data`.
- `SECRET_KEY` is read from Compose, with a source-visible development fallback.
- The Dockerfile and Compose configuration control debug behavior and database location.

## Source-confirmed concerns

- A populated SQLite database is copied into the image.
- Debug mode is enabled in the Dockerfile.
- Production transport security is not represented in the repository.
- Backup files can retain credential material unless they are explicitly protected.

## Deployment checklist

1. Remove database files from the build image and initialize a volume-backed database at startup.
2. Disable Flask debug mode outside local development.
3. Supply `SECRET_KEY` from an external secret store or deployment environment.
4. Place TLS termination in front of Flask and set secure cookie attributes.
5. Verify which environments consume the Compose file and whether overrides change security settings.

Deployment-specific facts require owner observation or a safely isolated local configuration check; do not infer live proxy or cloud policy from this repository alone.
