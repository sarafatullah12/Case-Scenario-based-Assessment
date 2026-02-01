from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List
from models import ParkingSession


@dataclass
class ParkingLot:
    capacity: int = 300
    sessions: Dict[str, ParkingSession] = field(default_factory=dict)
    log: List[str] = field(default_factory=list)

    def available(self) -> int:
        return self.capacity - len(self.sessions)

    def has_space(self) -> bool:
        return len(self.sessions) < self.capacity

    def add(self, session: ParkingSession) -> None:
        if not self.has_space():
            raise RuntimeError("Lot is full.")
        if session.plate in self.sessions:
            raise RuntimeError("That vehicle is already inside.")
        self.sessions[session.plate] = session
        self.log.append(f"{datetime.now().isoformat()} | ENTRY | {session.plate}")

    def get(self, plate: str) -> ParkingSession:
        if plate not in self.sessions:
            raise KeyError("No active session for that plate.")
        return self.sessions[plate]

    def remove(self, plate: str) -> ParkingSession:
        session = self.get(plate)
        del self.sessions[plate]
        self.log.append(f"{datetime.now().isoformat()} | EXIT  | {plate}")
        return session
