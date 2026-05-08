# Authentication Flow

## Explanation

Both rails issue and validate tokens via the same SimpleJWT primitives so
clients are interchangeable.

## Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant API as DRF or Ninja
    participant S as AuthService
    participant U as UserRepository
    participant J as SimpleJWT

    C->>API: POST /auth/login {email, password}
    API->>S: login(email, password)
    S->>U: by_email(email)
    U-->>S: User row
    S->>S: check password
    S->>J: RefreshToken.for_user(user)
    J-->>S: TokenPair
    S-->>API: {access, refresh}
    API-->>C: 200 {access, refresh}

    Note over C,API: Subsequent calls
    C->>API: GET /me  Authorization Bearer <access>
    API->>J: validate token
    J-->>API: user
    API-->>C: 200 user
```

## Real-world reasoning

- One issuer + one validator across both rails removes a class of bugs
  ("DRF accepts this token, Ninja rejects it").
- Refresh rotation is enabled to limit replay risk.

## Scaling considerations

- JWTs are stateless: any app replica can validate without a session
  store. That's why they fit horizontal scaling well.

## Possible bottlenecks

- Password hashing CPU on registration spikes.

## Optimization ideas

- Move heavy registration validation to a Celery task once registration
  is no longer in the synchronous path.
