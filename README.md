# Feature Gates

Small, deterministic feature flags for Python services.

Feature Gates provides typed flag definitions, percentage rollouts stable per user, environment targeting, kill switches, and an audit trail. It is designed for services that need predictable behavior without introducing a hosted control plane.

```python
from feature_gates import Flag, GateSet

gates = GateSet([Flag("new_checkout", enabled=True, rollout=25)])
if gates.enabled("new_checkout", subject="user-123"):
    checkout_v2()
```

## Guarantees

- Same subject always receives the same rollout decision for a flag
- Disabled flags short-circuit before rollout evaluation
- Unknown flags fail closed
- Decisions are immutable records suitable for structured logging
- No runtime dependencies; Python 3.11+

```bash
python -m pip install -e ".[dev]"
pytest -q
ruff check .
```

MIT licensed. See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).
