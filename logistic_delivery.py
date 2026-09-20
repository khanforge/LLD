"""
Logistics Delivery System - Low Level Design
Design Pattern: Factory Pattern

Problem Statement
-----------------
Design a logistics delivery system for a company that provides delivery
services using different types of vehicles.

The system allows a customer to create a delivery request by selecting a
vehicle type, pickup location, destination, and pickup time.

Requirements
------------
1. The system should support multiple vehicle types:
   - Bike
   - Car
   - Truck

2. Each vehicle type has a different price per kilometer.

3. The appropriate Vehicle object should be created dynamically based on
   the vehicle type selected by the customer.

4. A customer should contain basic information such as:
   - Customer ID
   - Name
   - Email
   - Phone number

5. A location should contain latitude and longitude.

6. The system should calculate the distance between the pickup and
   destination locations using a DistanceService.

7. The delivery price should be calculated using:
       total_price = distance * vehicle_rate_per_km

8. A Delivery should contain:
   - Delivery ID
   - Customer
   - Vehicle
   - Pickup location
   - Destination location
   - Distance
   - Price
   - Pickup time
   - Expected delivery time
   - Delivery status

9. A delivery should follow valid status transitions:

       PENDING
          |
          v
       PICKED_UP
          |
          v
       IN_TRANSIT
          |
          v
       DELIVERED

   A pending delivery may also be cancelled.

10. Invalid delivery status transitions should not be allowed.

11. DeliveryService should coordinate the delivery creation process by:
    - Creating the appropriate vehicle
    - Calculating the distance
    - Calculating the price
    - Creating and returning the Delivery object

Design Goals
------------
- Use an abstract Vehicle class for common vehicle behavior.
- Use inheritance for Bike, Car, and Truck.
- Use the Factory Pattern to centralize vehicle creation.
- Keep distance calculation and pricing logic in separate services.
- Keep delivery state-transition rules inside the Delivery entity.
- Keep DeliveryService responsible for orchestration rather than
  vehicle creation, pricing, or distance calculation.

Factory Pattern
---------------
The VehicleFactory encapsulates the creation of concrete Vehicle objects.

Instead of:

    if vehicle_type == "bike":
        vehicle = Bike()
    elif vehicle_type == "car":
        vehicle = Car()
    elif vehicle_type == "truck":
        vehicle = Truck()

throughout the application, clients use:

    vehicle = VehicleFactory.create_vehicle(vehicle_type)

This keeps object-creation logic centralized and allows the rest of the
system to work with the Vehicle abstraction.

Out of Scope
------------
- Driver assignment
- Driver acceptance
- Payment processing
- Live GPS tracking
- Fleet availability
- Route optimization
- Complex/surge pricing
- Database persistence
- External map APIs
"""

from abc import ABC, abstractmethod
from enum import Enum

class Vehicle(ABC):
    @abstractmethod
    def get_rate_per_km(self):
        pass

class Car(Vehicle):
    def get_rate_per_km(self):
        return 20

class Bike(Vehicle):
    def get_rate_per_km(self):
        return 10

class Truck(Vehicle):
    def get_rate_per_km(self):
        return 30 

class VehicleFactory:
    _vehicle_types = {
        "car": Car,
        "bike": Bike,
        "truck": Truck
    }
    @classmethod
    def create_vehicle(cls, vehicle_type):
        vehicle_class = cls._vehicle_types.get(vehicle_type.lower())
        if vehicle_class:
            return vehicle_class()
        else:
            raise ValueError(f"Unknown vehicle type: {vehicle_type}")

class Customer:
    def __init__(self, id, name, email, phone):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone

    def get_customer_info(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone
        }

class Location:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def get_location(self):
        return {
            'latitude': self.latitude,
            'longitude': self.longitude
        }

class DeliveryStatus(Enum):
    PENDING = "pending"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Delivery:
    def __init__(self, id, customer, vehicle, pickup_location, destination_location, distance, price, pickup_time, delivery_time):
        self.id = id
        self.customer = customer
        self.vehicle = vehicle
        self.pickup_location = pickup_location
        self.destination_location = destination_location
        self.pickup_time = pickup_time
        self.delivery_time = delivery_time
        self.status = DeliveryStatus.PENDING
        self.price = price
        self.distance = distance

    def get_price(self):
        return self.price
    
    def mark_pickedup(self):
        if self.status == DeliveryStatus.PENDING:
            self.status = DeliveryStatus.PICKED_UP
        else:
            raise ValueError("Cannot set status to 'Picked Up' unless the current status is 'pending'.")

    def mark_in_transit(self):
        if self.status == DeliveryStatus.PICKED_UP:
            self.status = DeliveryStatus.IN_TRANSIT
        else: 
            raise ValueError("Cannot set status to 'In Transit' unless the current status is 'picked_up'.")

    def mark_delivered(self):
        if self.status ==  DeliveryStatus.IN_TRANSIT:
            self.status = DeliveryStatus.DELIVERED
        else:
            raise ValueError("Cannot set status to 'Delivered' unless the current status is 'in_transit'.")

    def cancel_delivery(self):
        if self.status in [DeliveryStatus.PICKED_UP, DeliveryStatus.IN_TRANSIT, DeliveryStatus.DELIVERED]:
            raise ValueError("Cannot cancel delivery after it has been picked up or delivered.")
        else:
            self.status = "cancelled"

class DistanceService:
    @staticmethod
    def calculate_distance(pickup_location, destination_location):
        return 10 # for example

class PriceService:
    @staticmethod
    def calclulate_price(distance, vehicle):
        return distance * vehicle.get_rate_per_km()


class DeliveryService:
    def __init__(
            self, id, customer, vehicle_type, pickup_location, destination_location, pickup_time, delivery_time
    ):
        self.id = id
        self.customer = customer
        self.vehicle_type = vehicle_type
        self.pickup_location = pickup_location
        self.destination_location = destination_location
        self.pickup_time = pickup_time
        self.delivery_time = delivery_time

    def create_delivery(self):
        vehicle = VehicleFactory.create_vehicle(self.vehicle_type)
        distance = DistanceService.calculate_distance(self.pickup_location, self.destination_location)
        price = PriceService.calclulate_price(distance, vehicle)
        delivery = Delivery(
            self.id,
            self.customer,
            vehicle,
            self.pickup_location,
            self.destination_location,
            distance,
            price, 
            self.pickup_time,
            self.delivery_time
        )
        return delivery

customer = Customer(
    1, "parvej", "parvej@gmail.com", "6387480183"
)
source_location = Location(
    "123", "123"
)
destination_location = Location(
    "345","345"
)
deliveryService = DeliveryService(
    1, customer, "bike", source_location, destination_location, "12 sep 10 am", "14 sep 10 am"
)

delivery = deliveryService.create_delivery()
print("\n")
print("-"*40)
print(f"Delivery for customer: {delivery.customer.get_customer_info().get("name")} \nscheduled for pick up at: {delivery.pickup_time}")
print(f"Delivery status is: {delivery.status}")
delivery.mark_pickedup()
print(f"Delivery status updated: {delivery.status}")
delivery.mark_in_transit()
print(f"Delivery status updated: {delivery.status}")
delivery.mark_delivered()
print(f"Delivery status updated: {delivery.status}")
print("-"*40)
