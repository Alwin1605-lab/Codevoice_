"""Prometheus metrics helpers with a defensive fallback when prometheus_client
is not installed. This lets the application start in environments where the
package is not available while providing no-op counters.
"""

try:
    from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST  # type: ignore
    PROM_AVAILABLE = True
except Exception:
    PROM_AVAILABLE = False


if PROM_AVAILABLE:
    # Counters for AI usage
    ai_requests_total = Counter('ai_requests_total', 'Total AI generation requests', ['provider', 'model'])
    ai_errors_total = Counter('ai_errors_total', 'Total AI generation errors', ['provider', 'model'])

    # Task counters
    generation_tasks_total = Counter('generation_tasks_total', 'Total project generation tasks', ['status'])

    def metrics_response():
        """Return Prometheus metrics payload and content-type header."""
        return generate_latest(), CONTENT_TYPE_LATEST

else:
    # No-op stubs so other modules can call .labels(...).inc() safely
    class _NoopMetric:
        def labels(self, *a, **k):
            return self

        def inc(self, *a, **k):
            return None

    ai_requests_total = _NoopMetric()
    ai_errors_total = _NoopMetric()
    generation_tasks_total = _NoopMetric()

    def metrics_response():
        # Return a plain-text payload so /metrics still responds
        return b"# prometheus_client not installed - metrics disabled\n", "text/plain; version=0.0.4"
