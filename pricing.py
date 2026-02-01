from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, time
from models import Vehicle, Ticket


class PricingStrategy(ABC):
    @abstractmethod
    def calculate_fee(self, vehicle: Vehicle, ticket: Ticket) -> float:
        ...


class Rates:
    PER_HOUR = {
        "bike": 20.0,
        "car": 50.0,
        "truck": 80.0
    }


class OffPeak(PricingStrategy):
    def calculate_fee(self, vehicle: Vehicle, ticket: Ticket) -> float:
        hours = ticket.hours_ceiling()
        return Rates.PER_HOUR[vehicle.kind()] * hours * 1.0


class Peak(PricingStrategy):
    def calculate_fee(self, vehicle: Vehicle, ticket: Ticket) -> float:
        hours = ticket.hours_ceiling()
        return Rates.PER_HOUR[vehicle.kind()] * hours * 1.5


class Weekend(PricingStrategy):
    def calculate_fee(self, vehicle: Vehicle, ticket: Ticket) -> float:
        hours = ticket.hours_ceiling()
        return Rates.PER_HOUR[vehicle.kind()] * hours * 1.2


class PricingEngine:
    def __init__(self) -> None:
        self.peak_start = time(17, 0)
        self.peak_end = time(21, 0)

    def pick(self, entry: datetime, exit_: datetime) -> PricingStrategy:
        if exit_.weekday() in (5, 6):
            return Weekend()

        t = exit_.time()
        if self.peak_start <= t <= self.peak_end:
            return Peak()

        return OffPeak()

    def fee(self, vehicle: Vehicle, ticket: Ticket) -> float:
        if ticket.exit_time is None:
            raise ValueError("Close the ticket before calculating fee.")
        return float(self.pick(ticket.entry_time, ticket.exit_time).calculate_fee(vehicle, ticket))
