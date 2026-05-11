# LibraCore Architecture

LibraCore should be presented as a production-style backend project. The diagram below highlights clean API layering, JWT-based security, database access, and deployment automation.

```mermaid
flowchart LR
    User[Web / Mobile Client] --> API[Spring Boot REST API]
    API --> Security[Spring Security Filter Chain]
    Security --> Auth[JWT Authentication Service]
    Security --> Controllers[REST Controllers]
    Controllers --> Services[Business Service Layer]
    Services --> Repositories[Repository Layer]
    Repositories --> DB[(MySQL / PostgreSQL)]
    Services --> Validation[DTO Validation + Mapping]
    API --> Docs[OpenAPI / Swagger Docs]
    CI[GitHub Actions CI] --> Tests[Unit + Integration Tests]
    Tests --> Docker[Docker Image / Compose]
    Docker --> Runtime[Deployment Runtime]
```

## Request flow

```mermaid
sequenceDiagram
    participant C as Client
    participant API as Spring Boot API
    participant S as Security Filter
    participant A as Auth Service
    participant DB as Database

    C->>API: HTTP request with JWT
    API->>S: Route through security filter chain
    S->>A: Validate token and roles
    A->>DB: Load user/permission data if needed
    DB-->>A: User details
    A-->>S: Authentication result
    S-->>API: Continue or reject request
    API-->>C: JSON response
```

## README checklist for this repository

- Add API setup steps.
- Add `.env.example`.
- Add database migration instructions.
- Add test command.
- Add Docker Compose command.
- Add CI badge and latest release badge.
