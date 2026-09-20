from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime

class Rider:
    def __init__(self, id, name, phone):
        self.id = id
        self.name = name
        self.phone = phone

    def get_name(self):
        return self.name

    def get_phone(self):
        return self.phone

class Driver:
    def __init__(self, id, name, phone, vehicle):
        self.id = id
        self.name = name
        self.phone = phone
        self.vehicle = vehicle
        self.current_location = None
        self.is_available = True

    def mark_current_location(self, location):
        self.current_location = location

    def mark_availability(self):
        self.is_available = True

    def mark_unavailability(self):
        self.is_available = False  

class Location:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

class RiderService:
    @staticmethod
    def register_rider(id, name, phone):
        return Rider(id, name, phone)

class DriverService:
    @staticmethod
    def register_driver(id, name, phone, vehicle):
        return Driver(id, name, phone, vehicle)    

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
    _vehicle_types = {
        "car": Car,
        "bike": Bike,
        "auto": Auto
    }
    @staticmethod
    def create_vehicle(vehicle_type, registration_number):
        vehicle_class = VehicleFactory._vehicle_types.get(vehicle_type.lower())
        if vehicle_class:
            return vehicle_class(registration_number)
        else:
            raise ValueError(f"Unknown vehicle type: {vehicle_type}")


class DistanceService:
    @staticmethod
    def calculate_distance(source, destination):
        return ((destination.latitude-source.latitude)**2 + (destination.longitude-source.longitude)**2) ** 0.5   

class PricingService:
    @staticmethod
    def calculate_price(distance, vehicle):
        return distance * vehicle.price_per_km()

class PricingRule(ABC):
    @abstractmethod
    def apply(self, price):
        pass

class SurgePricingRule(PricingRule):
    def __init__(self, surge_multiplier):
        self.surge_multiplier = surge_multiplier

    def apply(self, price):
        return price * self.surge_multiplier

class CouponPricingRule(PricingRule):
    def __init__(self, discount_percentage):
        self.discount_percentage = discount_percentage

    def apply(self, price):
        return price - (price * self.discount_percentage / 100)

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
        self.price = price
        self.rider = rider
        self.source = source
        self.destination = destination
        self.distance = distance
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

class DriverMatchingService:
    @staticmethod
    def find_available_driver(drivers, source):
        available_drivers = [
            driver
            for driver in drivers
            if driver.is_available
            and driver.current_location is not None
        ]
        if not available_drivers:
            return None
        # Sort drivers by distance to the source location
        available_drivers.sort(key=lambda driver: DistanceService.calculate_distance(driver.current_location, source))
        return available_drivers[0]  # Return the closest available driver

class TripService:
    
    def __init__(self):
        self.distance_service = DistanceService()
        self.pricing_service = PricingService()
        self.pricing_rules = [
            SurgePricingRule(1.5),
            CouponPricingRule(10)
        ]  # Example rules, can be extended

    def create_trip(
       self, id, vehicle, rider, source, destination
    ):
        distance = self.distance_service.calculate_distance(source, destination)
        price = self.pricing_service.calculate_price(distance, vehicle)
        for rule in self.pricing_rules:
            price = rule.apply(price)

        return Trip(id, vehicle, distance, price, rider, source, destination)

rider = RiderService.register_rider(1, "Parvej", "343223444222")
print(f"Rider {rider.name} created.")
vehicle1 = VehicleFactory.create_vehicle("car", "KA-01-AB-1234")
vehicle2 = VehicleFactory.create_vehicle("car", "KA-01-AB-1233")
vehicle3 = VehicleFactory.create_vehicle("car", "KA-01-AB-1232")


source = Location(12, 77)
destination = Location(13, 78)

trip_service = TripService()
trip = trip_service.create_trip(
    1, vehicle1, rider, source, destination
)

print(f"trip with id : {trip.id} for rider: {rider.name} created.")
      
driver1 = DriverService.register_driver(1, "John Doe", "1233243421", vehicle1)
driver1.mark_current_location(Location(100,1000))
driver2 = DriverService.register_driver(2, "Martin Rodrigues", "1234243421", vehicle2)
driver2.mark_current_location(Location(13,80))
driver3 = DriverService.register_driver(3, "Shyam", "1233353421", vehicle3)
driver3.mark_current_location(Location(50,66))

matched_driver = DriverMatchingService.find_available_driver(
            [driver1, driver2, driver3], source
        )
print(f"Driver matching matched driver: {matched_driver.name}")

if not matched_driver:
    print(f"no driver is currently available.")
else:
    matched_driver.mark_unavailability()
    trip.assign_driver(matched_driver)

    print(f"Driver {matched_driver.name} has been assigned to rider : {rider.name}")
    print(f"trip status = {trip.status}")