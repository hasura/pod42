# Pod42 Web-Server
- Point to the docs/content in `ingest.py` locally.
- Run `docker build -t pod42-server .`
- Populate all the required env in `env.txt`.
- Run `docker run --env-file env.txt -p 9000:8000 pod42-server`
