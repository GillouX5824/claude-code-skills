---
name: observability
description: Observability patterns at Alter Domus. Use this skill when integrating Sentry error tracking, OpenTelemetry tracing/metrics, or Grafana dashboards into a service.
---

# Observability at Alter Domus

All services **MUST** integrate with both **Sentry** (error tracking) and **OpenTelemetry** (tracing and metrics).

## Sentry

Sentry is used for error tracking and performance monitoring.

### Sentry Instances

| Environment | Sentry URL |
|-------------|------------|
| Development | `sentry.alterdomus.dev` |
| Production | `sentry.alterdomus.com` |

### Python Integration

```bash
uv add sentry-sdk[fastapi]
```

```python
import sentry_sdk
import os

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment=os.environ.get("DEPLOY_ENV", "development"),
    traces_sample_rate=0.1,  # Adjust based on traffic
)
```

The `[fastapi]` extra automatically captures FastAPI request context, errors, and performance data.

### TypeScript Integration

```bash
pnpm add @sentry/node
```

```typescript
import * as Sentry from "@sentry/node";

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.DEPLOY_ENV || "development",
  tracesSampleRate: 0.1,
});
```

---

## OpenTelemetry

OpenTelemetry (OTel) provides distributed tracing and metrics collection. Traces are exported via OTLP to the platform's collector.

### Python Integration

```bash
uv add opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp opentelemetry-instrumentation-fastapi
```

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
import os

def setup_telemetry(app):
    resource = Resource.create({
        "service.name": os.environ.get("OTEL_SERVICE_NAME", "unknown"),
        "deployment.environment": os.environ.get("DEPLOY_ENV", "development"),
    })

    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(
        endpoint=os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app)
```

Call `setup_telemetry(app)` during application startup (e.g. in a FastAPI lifespan or after creating the app).

### TypeScript Integration

```bash
pnpm add @opentelemetry/api @opentelemetry/sdk-node @opentelemetry/exporter-trace-otlp-grpc @opentelemetry/instrumentation-express @opentelemetry/instrumentation-http
```

```typescript
import { NodeSDK } from "@opentelemetry/sdk-node";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-grpc";
import { ExpressInstrumentation } from "@opentelemetry/instrumentation-express";
import { HttpInstrumentation } from "@opentelemetry/instrumentation-http";

const sdk = new NodeSDK({
  serviceName: process.env.OTEL_SERVICE_NAME || "unknown",
  traceExporter: new OTLPTraceExporter({
    url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT || "http://localhost:4317",
  }),
  instrumentations: [
    new HttpInstrumentation(),
    new ExpressInstrumentation(),
  ],
});

sdk.start();
```

This must run **before** importing Express or any HTTP library.

---

## Helm Configuration

Both `SENTRY_DSN` and OpenTelemetry environment variables must be set in the Helm values:

```yaml
environment:
  enabled: true
  values:
    SENTRY_DSN: https://xxx@sentry.alterdomus.dev/X
    OTEL_SERVICE_NAME: my-api
    OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector:4317
    DEPLOY_ENV: development  # or "production"
```

`SENTRY_DSN` should be stored in AWS Secrets Manager for production. `OTEL_EXPORTER_OTLP_ENDPOINT` points to the cluster-local OpenTelemetry Collector.

---

## Grafana

Grafana is used for dashboards, metrics visualization, and alerting.

| Environment | Grafana URL |
|-------------|------------|
| Development | `grafana.alterdomus.dev` |
| Production | `grafana.alterdomus.com` |

---

## Related Skills

| Skill | When to use |
|-------|-------------|
| [APIs](skill://apis) | API development patterns, deployment checklist |
| [Kubernetes](skill://kubernetes) | Helm values configuration, environment variables |
