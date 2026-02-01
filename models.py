from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
import math
import uuid


@dataclass(frozen=True)
class Vehicle(ABC):
    plate: str

    @abstractmethod
    def kind(self) -> str:
        ...


@dataclass(frozen=True)
class Car(Vehicle):
    def kind(self) -> str:
        return "car"


@dataclass(frozen=True)
class Bike(Vehicle):
    def kind(self) -> str:
        return "bike"


@dataclass(frozen=True)
class Truck(Vehicle):
    def kind(self) -> str:
        return "truck"


@dataclass
class Pass(ABC):
    pass_id: str
    plate: str
    valid_until: datetime

    def is_valid(self, when: datetime) -> bool:
        return when <= self.valid_until


@dataclass
class MonthlyPass(Pass):
    pass


@dataclass
class SingleEntryPass(Pass):
    used: bool = False

    def can_use(self, when: datetime) -> bool:
        return (not self.used) and self.is_valid(when)

    def mark_used(self) -> None:
        self.used = True


@dataclass
class Ticket:
    plate: str
    entry_time: datetime
    ticket_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    exit_time: datetime | None = None

    def close(self, exit_time: datetime) -> None:
        if exit_time < self.entry_time:
            raise ValueError("Exit time can't be earlier than entry time.")
        self.exit_time = exit_time

    def hours_ceiling(self) -> int:
        if self.exit_time is None:
            raise ValueError("Ticket isn't closed yet.")
        hours = (self.exit_time - self.entry_time).total_seconds() / 3600.0
        return max(1, math.ceil(hours))


@dataclass
class Payment:
    amount: float
    method: str
    paid_at: datetime
    payment_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])


@dataclass
class ParkingSession:
    vehicle: Vehicle
    started_at: datetime
    ticket: Ticket | None = None
    parking_pass: Pass | None = None

    @property
    def plate(self) -> str:
        return self.vehicle.plate

    def pass_based(self) -> bool:
        return self.parking_pass is not None
