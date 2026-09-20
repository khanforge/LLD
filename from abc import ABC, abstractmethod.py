from abc import ABC, abstractmethod
from enum import Enum

class Vehicle(ABC):
    def __init__(self, registration_number):
        self.registration_number = registration_number

    @abstractmethod
    def price_per_km(self):
        pass

class Car(Vehicle):
    def price_per_km(self):
        return 15

class Bike(Vehicle):
    def price_per_km(self):
        return 10

class Auto(Vehicle):
    def price_per_km(self):
        return 5


class VehicleFactory:
    pass

class TripStatus(Enum):
    PENDING = "Pending"
    DRIVER_ASSIGNED = "Driver Assigned"
    DRIVER_ARRIVED = "Driver Arrived"
    ONGOING = "Ongoing"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class Trip:
    def __init__(self, id, vehicle, distance, price, rider, source, destination):
        self.id = id
        self.vehicle = vehicle
        self.distance = distance
        self.price = price
        self.rider = rider
        self.source = source
        self.destination = destination
        self.driver = None
        self.status = TripStatus.PENDING

    def assign_driver(self, driver):
            if self.status == TripStatus.PENDING:
                self.driver = driver
                self.status = TripStatus.DRIVER_ASSIGNED
            else:
                raise ValueError("Driver can only be assigned if the trip is pending.")

    def mark_arrived(self):
        if self.status == TripStatus.DRIVER_ASSIGNED:
            self.status = TripStatus.DRIVER_ARRIVED
        else:
            raise ValueError("Trip can only be marked as arrived if driver has been assigned.")

    def mark_ongoing(self):
        if self.status == TripStatus.DRIVER_ARRIVED:
            self.status = TripStatus.ONGOING
        else:
            raise ValueError("Trip can only be marked as ongoing if driver has been arrived.")

    def mark_completed(self):
        if self.status == TripStatus.ONGOING:
            self.status = TripStatus.COMPLETED
        else:
            raise ValueError("Trip can only be marked as completed if it is ongoing.")

    def mark_cancelled(self):
        if self.status in [TripStatus.PENDING, TripStatus.DRIVER_ASSIGNED, TripStatus.DRIVER_ARRIVED, TripStatus.ONGOING]:
            self.status = TripStatus.CANCELLED
        else:
            raise ValueError("Trip can only be marked as cancelled if it is pending or ongoing.")
    