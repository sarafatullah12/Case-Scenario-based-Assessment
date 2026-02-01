from __future__ import annotations

from datetime import datetime
from models import Vehicle, Ticket, Pass, MonthlyPass, SingleEntryPass, ParkingSession, Payment
from parking_lot import ParkingLot
from pricing import PricingEngine


class EntryGate:
    def __init__(self, lot: ParkingLot) -> None:
        self.lot = lot

    def enter(self, vehicle: Vehicle, parking_pass: Pass | None = None) -> Ticket | None:
        now = datetime.now()

        if not self.lot.has_space():
            raise RuntimeError("Sorry, the parking is full right now.")

        if parking_pass is not None:
            if parking_pass.plate != vehicle.plate:
                raise RuntimeError("Pass plate doesn't match the vehicle.")

            if isinstance(parking_pass, MonthlyPass):
                if not parking_pass.is_valid(now):
                    raise RuntimeError("Monthly pass is expired.")
                self.lot.add(ParkingSession(vehicle=vehicle, started_at=now, parking_pass=parking_pass))
                return None

            if isinstance(parking_pass, SingleEntryPass):
                if not parking_pass.can_use(now):
                    raise RuntimeError("Single-entry pass is invalid or already used.")
                parking_pass.mark_used()
                self.lot.add(ParkingSession(vehicle=vehicle, started_at=now, parking_pass=parking_pass))
                return None

            if not parking_pass.is_valid(now):
                raise RuntimeError("Pass is expired.")
            self.lot.add(ParkingSession(vehicle=vehicle, started_at=now, parking_pass=parking_pass))
            return None

        ticket = Ticket(plate=vehicle.plate, entry_time=now)
        self.lot.add(ParkingSession(vehicle=vehicle, started_at=now, ticket=ticket))
        return ticket


class ExitGate:
    def __init__(self, lot: ParkingLot, pricing: PricingEngine) -> None:
        self.lot = lot
        self.pricing = pricing

    def exit(self, plate: str, method: str = "cash") -> Payment | None:
        now = datetime.now()
        session = self.lot.get(plate)

        if session.pass_based():
            p = session.parking_pass
            if p is None or not p.is_valid(now):
                raise RuntimeError("Pass isn't valid anymore. Please check with admin.")
            self.lot.remove(plate)
            return None

        if session.ticket is None:
            raise RuntimeError("Session is broken (no pass, no ticket).")

        session.ticket.close(now)
        amount = self.pricing.fee(session.vehicle, session.ticket)

        payment = None
        if amount > 0:
            payment = Payment(amount=amount, method=method, paid_at=now)
            self.lot.log.append(
                f"{now.isoformat()} | PAY   | {plate} | {amount:.2f} | {method} | {payment.payment_id}"
            )

        self.lot.remove(plate)
        return payment
