from enum import Enum
from datetime import datetime
import math


# =========================================================
# ENUMS
# =========================================================

class VehicleType(Enum):
    CAR = "car"
    BIKE = "bike"
    TRUCK = "truck"


class ParkingSpotStatus(Enum):
    EMPTY = "empty"
    OCCUPIED = "occupied"


class ParkingSpotType(Enum):
    BIKE = "bike"
    COMPACT = "compact"
    LARGE = "large"


class TicketStatus(Enum):
    ACTIVE = "active"
    CLOSED = "closed"


# =========================================================
# VEHICLE
# =========================================================

class Vehicle:
    def __init__(self, id, registration_number, vehicle_type):
        self.id = id
        self.registration_number = registration_number
        self.type = vehicle_type


# =========================================================
# PARKING SPOT
# =========================================================

class ParkingSpot:
    def __init__(self, id, name, order, spot_type):
        self.id = id
        self.name = name
        self.order = order
        self.type = spot_type
        self.status = ParkingSpotStatus.EMPTY

    def mark_occupied(self):
        if self.status != ParkingSpotStatus.EMPTY:
            raise ValueError("Parking spot is already occupied")

        self.status = ParkingSpotStatus.OCCUPIED

    def mark_empty(self):
        if self.status != ParkingSpotStatus.OCCUPIED:
            raise ValueError("Parking spot is already empty")

        self.status = ParkingSpotStatus.EMPTY


# =========================================================
# LEVEL
# =========================================================

class Level:
    def __init__(self, id, name, order):
        self.id = id
        self.name = name
        self.order = order
        self.parking_spots = []

    def add_parking_spot(self, parking_spot):
        self.parking_spots.append(parking_spot)


# =========================================================
# PARKING LOT
# =========================================================

class ParkingLot:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.levels = []

    def add_level(self, level):
        self.levels.append(level)


# =========================================================
# PARKING TICKET
# =========================================================

class Ticket:
    def __init__(
        self,
        id,
        ticket_number,
        vehicle,
        parking_time,
        level,
        parking_spot
    ):
        self.id = id
        self.ticket_number = ticket_number
        self.vehicle = vehicle

        self.parking_time = parking_time
        self.exit_time = None

        # Keeping both because physical location is
        # identified as (level, spot) in this design.
        self.level = level
        self.parking_spot = parking_spot

        self.status = TicketStatus.ACTIVE
        self.fees = None

    @property
    def parking_duration(self):
        if self.exit_time is None:
            raise ValueError("Exit time has not been set")

        duration = self.exit_time - self.parking_time

        return duration.total_seconds() / 3600

    def set_exit_time(self, exit_time):
        self.exit_time = exit_time

    def close(self, fees):
        if self.status != TicketStatus.ACTIVE:
            raise ValueError("Only active tickets can be closed")

        self.fees = fees
        self.status = TicketStatus.CLOSED


# =========================================================
# PRICING SERVICE
# =========================================================

class PricingService:

    PRICE_MAPPING = {
        VehicleType.BIKE: 80,
        VehicleType.CAR: 100,
        VehicleType.TRUCK: 200
    }

    @staticmethod
    def calculate(ticket):

        price_per_hour = PricingService.PRICE_MAPPING.get(
            ticket.vehicle.type
        )

        if price_per_hour is None:
            raise ValueError("Vehicle type is not supported")

        billable_hours = math.ceil(ticket.parking_duration)

        return billable_hours * price_per_hour


# =========================================================
# SPOT ALLOCATION
# =========================================================

class SpotAllocation:

    @staticmethod
    def find_spot(vehicle, parking_lot):

        required_spot_type = (
            ParkingService.PARKING_COMPATIBILITY.get(vehicle.type)
        )

        if required_spot_type is None:
            raise ValueError("Vehicle type is not supported")

        # Lowest level first
        levels = sorted(
            parking_lot.levels,
            key=lambda level: level.order
        )

        for level in levels:

            # Nearest spot within that level first
            parking_spots = sorted(
                level.parking_spots,
                key=lambda spot: spot.order
            )

            for spot in parking_spots:

                if (
                    spot.type == required_spot_type
                    and
                    spot.status == ParkingSpotStatus.EMPTY
                ):
                    return level, spot

        raise ValueError("No compatible parking spot available")


# =========================================================
# PARKING SERVICE
# =========================================================

class ParkingService:

    PARKING_COMPATIBILITY = {
        VehicleType.BIKE: ParkingSpotType.BIKE,
        VehicleType.CAR: ParkingSpotType.COMPACT,
        VehicleType.TRUCK: ParkingSpotType.LARGE
    }

    @staticmethod
    def validate_spot(vehicle, parking_spot):

        required_spot_type = (
            ParkingService.PARKING_COMPATIBILITY.get(vehicle.type)
        )

        if required_spot_type is None:
            raise ValueError("Vehicle type is not supported")

        if parking_spot.type != required_spot_type:
            raise ValueError(
                "Parking spot and vehicle type are not compatible"
            )

        if parking_spot.status != ParkingSpotStatus.EMPTY:
            raise ValueError("Parking spot is not available")

    @staticmethod
    def create_parking(
        id,
        ticket_number,
        vehicle,
        parking_time,
        level,
        parking_spot
    ):

        # Validate before changing state
        ParkingService.validate_spot(
            vehicle,
            parking_spot
        )

        parking_spot.mark_occupied()

        return Ticket(
            id,
            ticket_number,
            vehicle,
            parking_time,
            level,
            parking_spot
        )

    @staticmethod
    def park_vehicle(
        id,
        ticket_number,
        vehicle,
        parking_lot
    ):

        level, parking_spot = SpotAllocation.find_spot(
            vehicle,
            parking_lot
        )

        return ParkingService.create_parking(
            id=id,
            ticket_number=ticket_number,
            vehicle=vehicle,
            parking_time=datetime.now(),
            level=level,
            parking_spot=parking_spot
        )

    @staticmethod
    def close_parking(ticket):

        if ticket.status != TicketStatus.ACTIVE:
            raise ValueError("Ticket is already closed")

        exit_time = datetime.now()

        ticket.set_exit_time(exit_time)

        fees = PricingService.calculate(ticket)

        ticket.close(fees)

        ticket.parking_spot.mark_empty()

        return ticket