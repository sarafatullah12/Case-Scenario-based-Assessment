from datetime import datetime, timedelta

from models import Car, Bike, Truck, MonthlyPass, SingleEntryPass
from parking_lot import ParkingLot
from pricing import PricingEngine
from gates import EntryGate, ExitGate


def run_demo():
    lot = ParkingLot(capacity=300)
    pricing = PricingEngine()
    entry_gate = EntryGate(lot)
    exit_gate = ExitGate(lot, pricing)

    print("Urban City Parking system is running.")
    print(f"Spaces available: {lot.available()} / {lot.capacity}\n")

    car = Car("DHA-5678")
    ticket = entry_gate.enter(car)
    print(f"Entry approved for {car.plate}. Ticket: {ticket.ticket_id}")

    ticket.entry_time = datetime.now() - timedelta(hours=2, minutes=10)

    payment = exit_gate.exit(car.plate, method="card")
    print(f"Exit done for {car.plate}. Paid: {payment.amount:.2f} ({payment.method})\n")

    bike = Bike("SYL-1111")
    monthly = MonthlyPass("MP-001", "SYL-1111", datetime.now() + timedelta(days=30))
    entry_gate.enter(bike, monthly)
    print(f"{bike.plate} entered using monthly pass {monthly.pass_id}.")
    exit_gate.exit(bike.plate)
    print(f"{bike.plate} exited. No payment needed.\n")

    truck = Truck("CTG-9090")
    single = SingleEntryPass("SP-009", "CTG-9090", datetime.now() + timedelta(days=1))
    entry_gate.enter(truck, single)
    print(f"{truck.plate} entered using single-entry pass {single.pass_id} (now used={single.used}).")
    exit_gate.exit(truck.plate)
    print(f"{truck.plate} exited. Pass session completed.\n")

    print(f"Spaces available now: {lot.available()} / {lot.capacity}")
    print("\nRecent activity:")
    for line in lot.log[-10:]:
        print("  ", line)


if __name__ == "__main__":
    run_demo()
