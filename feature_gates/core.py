from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Iterable, Mapping


@dataclass(frozen=True)
class Flag:
    name: str
    enabled: bool = False
    rollout: int = 100
    environments: frozenset[str] = frozenset()
    attributes: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name or self.name.strip() != self.name:
            raise ValueError("flag name must be non-empty and trimmed")
        if not 0 <= self.rollout <= 100:
            raise ValueError("rollout must be between 0 and 100")


@dataclass(frozen=True)
class Decision:
    flag: str
    enabled: bool
    reason: str
    subject: str | None
    environment: str | None
    evaluated_at: str


class GateSet:
    def __init__(self, flags: Iterable[Flag], clock: Callable[[], datetime] | None = None):
        self._flags = {flag.name: flag for flag in flags}
        if len(self._flags) == 0:
            raise ValueError("at least one flag is required")
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def enabled(self, name: str, *, subject: str | None = None, environment: str | None = None, attributes: Mapping[str, str] | None = None) -> bool:
        return self.decide(name, subject=subject, environment=environment, attributes=attributes).enabled

    def decide(self, name: str, *, subject: str | None = None, environment: str | None = None, attributes: Mapping[str, str] | None = None) -> Decision:
        flag = self._flags.get(name)
        now = self._clock().astimezone(timezone.utc).isoformat()
        if flag is None:
            return Decision(name, False, "unknown_flag", subject, environment, now)
        if not flag.enabled:
            return Decision(name, False, "disabled", subject, environment, now)
        if flag.environments and environment not in flag.environments:
            return Decision(name, False, "environment_mismatch", subject, environment, now)
        supplied = attributes or {}
        if any(supplied.get(key) != value for key, value in flag.attributes.items()):
            return Decision(name, False, "attribute_mismatch", subject, environment, now)
        if subject is None:
            return Decision(name, False, "subject_required", subject, environment, now)
        bucket = int(hashlib.sha256(f"{name}:{subject}".encode()).hexdigest()[:8], 16) % 100
        return Decision(name, bucket < flag.rollout, "rollout", subject, environment, now)

    def snapshot(self) -> tuple[Flag, ...]:
        return tuple(self._flags[name] for name in sorted(self._flags))
