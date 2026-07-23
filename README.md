# URL Shortener

> **Note:** If you want to deploy a pre-built production stack using Docker Hub images, check out the [url-shortener-prod](https://github.com/mugmold/url-shortener-prod) repository.

A simple full-stack URL shortener web application built with FastAPI, MongoDB, and React.

## Features

* **Short Links & Custom Aliases:** Generate random short codes or choose your own custom aliases.
* **Link Expiration:** Set optional expiration dates on links. Expired links will automatically redirect users to a not-found page.
* **User Accounts:** Register, login, and manage your personal links through a dashboard.
* **Rate Limiting:** Basic protection against spam and abuse on public and user endpoints.

## Tech Stack

* **Backend:** Python, FastAPI, Beanie (MongoDB ODM), SlowAPI
* **Frontend:** React, Vite, Tailwind CSS, DaisyUI
* **Gateway:** NGINX (acting as a reverse proxy)
* **Database:** MongoDB
* **DevOps:** Docker and GitHub Actions

## Environment Variables

You must create a `.env` file in the root folder before starting the project.

| Variable | Required | Description | Default |
|---|---|---|---|
| `DOMAIN_NAME` | Yes | Domain name or `localhost` for testing | `localhost` |
| `MONGO_URL` | Yes | MongoDB connection string | `mongodb://mongodb:27017` |
| `MONGO_DB_NAME` | Yes | Mongo database name | `url_shortener_db` |
| `SECRET_KEY` | Yes | Secret key for JWT hashing (`openssl rand -hex 32`) | `your_secret_key` |
| `DEBUG` | No | Set to `True` to enable Swagger API docs | `False` |
| `CORS_ORIGINS` | Yes | Allowed origins formatted as a JSON array | `["http://localhost"]` |
| `ALGORITHM` | No | JWT hashing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Access token lifespan in minutes | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | Refresh token lifespan in days | `7` |

## Local Development Setup

### Prerequisites
* Docker Engine
* Docker Compose v2+

### Running the App

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mugmold/url-shortener.git
   cd url-shortener
   ```

2. **Create your `.env` file:**
   * **Linux / macOS:**
     ```bash
     cp .env.example .env
     ```
   * **Windows:**
     ```cmd
     copy .env.example .env
     ```
   *(Make sure to open `.env` in a text editor and configure your variables before starting.)*

3. **Build and start all services:**
   ```bash
   docker compose up --build
   ```

4. Open `http://localhost` in your browser.

## API Documentation

Swagger UI docs are disabled by default. To view them during local development, set `DEBUG=True` in your `.env` file and restart the stack.

* **Swagger UI:** `http://localhost/docs`

## CI/CD Automated Builds

This repository includes a GitHub Actions workflow that automatically builds and pushes Docker images to Docker Hub on every commit pushed to the `main` branch. 

To enable automated publishing to your Docker Hub registry, add these two secrets under your GitHub repository settings (**Settings > Secrets and variables > Actions**):
* `DOCKERHUB_USERNAME`: Your Docker Hub account username.
* `DOCKERHUB_TOKEN`: A Docker Hub Personal Access Token with write permissions.

## System Architecture

```text
[ Client ] ---> ( Port 80 ) ---> [ NGINX Gateway ]
                                         |
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
     [ Frontend (Port 3000) ]                        [ Backend (Port 8000) ]
                                                                 |
                                                                 ▼
                                                     [ MongoDB (Port 27017) ]
```