# Distributed Systems Group 30 Architecture

This diagram is useful when presenting distributed-systems coursework or backend experiments. It highlights service separation, message flow, health checks, and resilience.

```mermaid
flowchart LR
    Client[Client] --> Gateway[API Gateway / Entry Service]
    Gateway --> ServiceA[Service A]
    Gateway --> ServiceB[Service B]
    ServiceA --> Broker[(Message Broker / Queue)]
    ServiceB --> Broker
    Broker --> Worker[Background Worker]
    ServiceA --> DB1[(Service A Database)]
    ServiceB --> DB2[(Service B Database)]
    Worker --> DB3[(Worker Storage)]
    Monitor[Logs / Metrics / Health Checks] --> Gateway
    Monitor --> ServiceA
    Monitor --> ServiceB
    Monitor --> Worker
```

## Failure-handling view

```mermaid
stateDiagram-v2
    [*] --> Healthy
    Healthy --> Degraded: timeout / failed dependency
    Degraded --> Retrying: retry policy starts
    Retrying --> Healthy: dependency recovers
    Retrying --> CircuitOpen: repeated failures
    CircuitOpen --> Fallback: serve safe response
    Fallback --> Healthy: health check passes
```

## README checklist for this repository

- Describe each service responsibility.
- Add local run commands.
- Add diagrams for message flow and failure recovery.
- Add test evidence or screenshots.
- Add CI badge and latest release badge.
