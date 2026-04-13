# Module10AssignmentKV

**Author:** kverma19863020  
**Course:** IS601 – Module 10 Assignment  
**Tech Stack:** FastAPI · PostgreSQL · SQLAlchemy · Pydantic v2 · Docker · GitHub Actions

---

## 🚀 Features

- Secure `User` model with bcrypt-hashed passwords
- PostgreSQL via SQLAlchemy ORM with uniqueness constraints on `username` and `email`
- Pydantic v2 schemas (`UserCreate`, `UserRead`, `UserUpdate`) with field validation
- Full CRUD REST API built with FastAPI
- Dockerized with multi-service `docker-compose.yml`
- CI/CD pipeline: test → security scan (Trivy) → Docker Hub push

---

## 🐳 Docker Hub

Image: [`kverma19863020/module10assignmentkv`](https://hub.docker.com/r/kverma19863020/module10assignmentkv)

```bash
docker pull kverma19863020/module10assignmentkv:latest
```

---

## 🏃 Run Locally

### Prerequisites
- Docker & Docker Compose installed

### Start All Services
```bash
docker-compose up --build
```

API available at: http://localhost:8000  
Swagger UI: http://localhost:8000/docs

---

## 🧪 Run Tests Locally

### Option A: With Docker Compose (recommended)
```bash
docker-compose up -d db_test
export DATABASE_URL=postgresql://kvuser:kvpassword@localhost:5433/kvdb_test
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/ -v --cov=app
```

### Option B: Bare metal (requires local PostgreSQL)
```bash
# Create test DB first
createdb -U kvuser kvdb_test

pip install -r requirements.txt -r requirements-dev.txt
DATABASE_URL=postgresql://kvuser:kvpassword@localhost:5432/kvdb_test pytest tests/ -v
```

---

## 🔐 GitHub Actions Secrets Required

| Secret | Description |
|--------|-------------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Health status |
| POST | `/users/` | Create user |
| GET | `/users/` | List all users |
| GET | `/users/{id}` | Get user by ID |
| PATCH | `/users/{id}` | Update user |
| DELETE | `/users/{id}` | Delete user |

---

## 📁 Project Structure
cat > REFLECTION.md << 'EOF'
# Reflection Document — Module 10 Assignment

**Student:** kverma19863020  
**Project:** Module10AssignmentKV

---

## Key Experiences

### 1. Designing the Secure User Model
The most meaningful part of this assignment was building a User model that never stores plain-text passwords. Using `passlib` with bcrypt ensures passwords are salted and hashed before any DB write. I also applied `unique=True` on both `username` and `email` columns directly in SQLAlchemy, which enforces integrity at the database level rather than relying solely on application-layer checks.

### 2. Pydantic v2 Validation
Migrating to Pydantic v2's `field_validator` syntax (replacing v1's `@validator`) required careful attention. The `model_config = ConfigDict(from_attributes=True)` pattern in `UserRead` enables ORM mode cleanly. Writing regex validators for password strength and username format helped ensure data quality from the API surface.

### 3. Test Isolation with PostgreSQL Transactions
The trickiest challenge was ensuring tests don't pollute each other. The `conftest.py` uses a per-test transaction rollback strategy: each test opens a connection, starts a transaction, runs, then rolls back. This makes tests fast and independent without recreating the schema every time.

### 4. CI/CD Pipeline Design
Structuring the GitHub Actions workflow into three jobs — `test`, `security-scan`, and `build-and-push` — enforced a quality gate: Docker Hub only receives the image after tests pass and Trivy finds no critical vulnerabilities. Using `cache-from: type=gha` significantly sped up repeated builds.

### 5. Docker Hub Deployment
Tagging images with both `:latest` and the git SHA (`${{ github.sha }}`) enables rollback traceability. The `DOCKERHUB_TOKEN` secret approach is more secure than using a password directly.

---

## Challenges Faced

- **PostgreSQL vs SQLite:** SQLite doesn't support `UUID` columns natively, so switching entirely to PostgreSQL for both dev and tests required setting up a `db_test` service in docker-compose and a dedicated service in GitHub Actions.
- **Pydantic v2 breaking changes:** `orm_mode = True` no longer works; `ConfigDict(from_attributes=True)` is required. This caused initial test failures until corrected.
- **Trivy scan exit codes:** Setting `exit-code: "0"` was deliberate — a failing scan should not block the pipeline for a learning assignment, but in production this should be `"1"`.

---

## Takeaways

This assignment reinforced that security is not an afterthought — password hashing, schema validation, and DB-level uniqueness constraints must be baked in from day one. Automated CI/CD ensures these guarantees hold across every future commit.
