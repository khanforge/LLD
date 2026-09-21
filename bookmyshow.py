# Assumption: There is just one screen in each show

"""
a) requirements:
1: Customer selects city
2: customer can browse movies
3: Customer can select the movie and view the theatre available in that city
4: Customer can select theatre
5: all the avaialable Shows for that movie in theatre be shown
6: Customer can select screen and shows
7: all the seats for that show will be shown
8: Customer can select the seats available 
9: Requests for booking and system books the seats
"""

"""
b) entities
1: Customer
2: City
3: Movies
4: Theatre
5: Screen
5: Show
6: Seat
7: SeatShow
8: Booking
"""

'''
c) Relationships
City(1) ---- Theatre(0..*)
Theatre(1) --- Screen(0..*)
Screen(1) --- Show(0..*) 
Screen(1) --- Seat(1..*)
movie(1) ---- show(0..*) 
show(0..*) --- seat(0,,*)
Customer(1) --- Booking(0...*) 
ShowSeat(1..*) --- Seat(1) 
ShowSeat(1..*) --- Show(1) 
Booking(1) --- ShowSeat(1..*) 
'''

from enum import Enum
from datetime import datetime, timedelta


# =========================================================
# ENUMS
# =========================================================

class SeatType(Enum):
    REGULAR = "regular"
    PREMIUM = "premium"
    RECLINER = "recliner"


class ShowSeatStatus(Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    BOOKED = "booked"


class BookingStatus(Enum):
    PENDING = "pending"
    BOOKED = "booked"
    CANCELLED = "cancelled"


SEAT_PRICE_MAP = {
    SeatType.REGULAR: 100,
    SeatType.PREMIUM: 200,
    SeatType.RECLINER: 400
}


# =========================================================
# CUSTOMER
# =========================================================

class Customer:
    def __init__(self, id, name, phone, email):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email


class CustomerService:

    @staticmethod
    def register_customer(id, name, phone, email):
        return Customer(id, name, phone, email)


# =========================================================
# CITY
# =========================================================

class City:
    def __init__(self, id, name):
        self.id = id
        self.name = name


# =========================================================
# MOVIE
# =========================================================

class Movie:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class MovieService:

    @staticmethod
    def create_movie(id, name):
        return Movie(id, name)


# =========================================================
# SEAT
# =========================================================

class Seat:
    def __init__(self, id, seat_number, seat_type):
        self.id = id
        self.seat_number = seat_number
        self.seat_type = seat_type

    @property
    def price(self):
        return SEAT_PRICE_MAP[self.seat_type]


# =========================================================
# SCREEN
# =========================================================

class Screen:
    def __init__(self, id, name):
        self.id = id
        self.name = name

        self.shows = []
        self.seats = []

    def add_show(self, show):
        self.shows.append(show)

    def add_seat(self, seat):
        self.seats.append(seat)


# =========================================================
# THEATRE
# =========================================================

class Theatre:
    def __init__(self, id, name, city):
        self.id = id
        self.name = name
        self.city = city

        self.screens = []

    def add_screen(self, screen):
        self.screens.append(screen)


# =========================================================
# SHOW
# =========================================================

class Show:
    def __init__(self, id, movie, start_time, duration, screen):
        self.id = id
        self.movie = movie
        self.start_time = start_time
        self.duration = duration
        self.screen = screen


# =========================================================
# SHOW SEAT
# =========================================================

class ShowSeat:
    """
    Represents a physical seat for a particular show.

    Example:
        Show = Avengers 7 PM
        Seat = A1
        Status = AVAILABLE / RESERVED / BOOKED
    """

    def __init__(
        self,
        id,
        show,
        seat,
        reservation_duration=5
    ):
        self.id = id
        self.show = show
        self.seat = seat

        self.status = ShowSeatStatus.AVAILABLE

        self.customer = None

        self.reservation_duration = reservation_duration
        self.reservation_time = None


    def mark_available(self):

        if self.status != ShowSeatStatus.RESERVED:
            raise ValueError(
                "Only a reserved seat can become available."
            )

        if self.reservation_time is None:
            raise ValueError(
                "Reservation time does not exist."
            )

        reservation_expired = (
            datetime.now() - self.reservation_time
            > timedelta(minutes=self.reservation_duration)
        )

        if not reservation_expired:
            raise ValueError(
                "Reservation has not expired yet."
            )

        self.status = ShowSeatStatus.AVAILABLE
        self.customer = None
        self.reservation_time = None


    def mark_reserved(self, customer):

        if not customer:
            raise ValueError(
                "Customer is required."
            )

        if self.status != ShowSeatStatus.AVAILABLE:
            raise ValueError(
                "Seat is not available."
            )

        self.customer = customer
        self.reservation_time = datetime.now()
        self.status = ShowSeatStatus.RESERVED


    def mark_booked(self, customer):

        if self.status != ShowSeatStatus.RESERVED:
            raise ValueError(
                "Seat must be reserved before booking."
            )

        if self.customer != customer:
            raise ValueError(
                "Seat was reserved by another customer."
            )

        self.status = ShowSeatStatus.BOOKED


# =========================================================
# BOOKING
# =========================================================

class Booking:
    def __init__(
        self,
        id,
        customer,
        show_seats,
        total_price
    ):
        self.id = id
        self.customer = customer
        self.show_seats = show_seats
        self.total_price = total_price

        self.status = BookingStatus.PENDING


    def mark_booked(self):

        if self.status != BookingStatus.PENDING:
            raise ValueError(
                "Only a pending booking can be confirmed."
            )

        self.status = BookingStatus.BOOKED


    def mark_cancelled(self):

        # Our current assumption:
        # confirmed booking cannot be cancelled.

        if self.status != BookingStatus.PENDING:
            raise ValueError(
                "Only pending booking can be cancelled."
            )

        self.status = BookingStatus.CANCELLED


# =========================================================
# BOOKING SERVICE
# =========================================================

class BookingService:

    @staticmethod
    def validate(customer, show_seats):

        if not show_seats:
            raise ValueError(
                "At least one seat must be selected."
            )

        expected_show = show_seats[0].show

        for show_seat in show_seats:

            # All seats must belong to same show
            if show_seat.show != expected_show:
                raise ValueError(
                    "All seats must belong to the same show."
                )

            # All seats must already be reserved
            if show_seat.status != ShowSeatStatus.RESERVED:
                raise ValueError(
                    f"Seat {show_seat.seat.seat_number} "
                    "is not reserved."
                )

            # Reservation must belong to same customer
            if show_seat.customer != customer:
                raise ValueError(
                    f"Seat {show_seat.seat.seat_number} "
                    "was reserved by another customer."
                )


    @staticmethod
    def create_booking(
        id,
        customer,
        show_seats
    ):

        # Step 1: validate selected seats
        BookingService.validate(
            customer,
            show_seats
        )

        # Step 2: calculate price
        total_price = sum(
            show_seat.seat.price
            for show_seat in show_seats
        )

        # Step 3: create pending booking
        booking = Booking(
            id,
            customer,
            show_seats,
            total_price
        )

        # Step 4: mark seats booked
        for show_seat in show_seats:
            show_seat.mark_booked(customer)

        # Step 5: confirm booking
        booking.mark_booked()

        return booking


# =========================================================
# DEMO / DRIVER CODE
# =========================================================

if __name__ == "__main__":

    # -----------------------------------------------------
    # 1. Create City
    # -----------------------------------------------------

    city = City(
        1,
        "Delhi"
    )


    # -----------------------------------------------------
    # 2. Create Theatre
    # -----------------------------------------------------

    theatre = Theatre(
        1,
        "PVR Select Citywalk",
        city
    )


    # -----------------------------------------------------
    # 3. Create Screen
    # -----------------------------------------------------

    screen = Screen(
        1,
        "Screen 1"
    )

    theatre.add_screen(screen)


    # -----------------------------------------------------
    # 4. Create physical seats
    # -----------------------------------------------------

    seat_a1 = Seat(
        1,
        "A1",
        SeatType.REGULAR
    )

    seat_a2 = Seat(
        2,
        "A2",
        SeatType.REGULAR
    )

    seat_a3 = Seat(
        3,
        "A3",
        SeatType.PREMIUM
    )

    seat_r1 = Seat(
        4,
        "R1",
        SeatType.RECLINER
    )


    screen.add_seat(seat_a1)
    screen.add_seat(seat_a2)
    screen.add_seat(seat_a3)
    screen.add_seat(seat_r1)


    # -----------------------------------------------------
    # 5. Create Movie
    # -----------------------------------------------------

    movie = MovieService.create_movie(
        1,
        "Avengers"
    )


    # -----------------------------------------------------
    # 6. Create Show
    # -----------------------------------------------------

    show = Show(
        1,
        movie,
        datetime(2026, 9, 23, 19, 0),
        180,
        screen
    )

    screen.add_show(show)


    # -----------------------------------------------------
    # 7. Create ShowSeats
    #
    # Physical seats become bookable for this Show.
    # -----------------------------------------------------

    show_seat_a1 = ShowSeat(
        1,
        show,
        seat_a1
    )

    show_seat_a2 = ShowSeat(
        2,
        show,
        seat_a2
    )

    show_seat_a3 = ShowSeat(
        3,
        show,
        seat_a3
    )

    show_seat_r1 = ShowSeat(
        4,
        show,
        seat_r1
    )


    # -----------------------------------------------------
    # 8. Register Customer
    # -----------------------------------------------------

    customer = CustomerService.register_customer(
        1,
        "Parvej",
        "9999999999",
        "parvej@example.com"
    )


    # -----------------------------------------------------
    # 9. Customer selects A1 and A3
    # -----------------------------------------------------

    selected_seats = [
        show_seat_a1,
        show_seat_a3
    ]


    # -----------------------------------------------------
    # 10. Temporarily reserve selected seats
    # -----------------------------------------------------

    for show_seat in selected_seats:
        show_seat.mark_reserved(customer)


    # -----------------------------------------------------
    # 11. Create booking
    # -----------------------------------------------------

    booking = BookingService.create_booking(
        1,
        customer,
        selected_seats
    )


    # -----------------------------------------------------
    # 12. Print booking
    # -----------------------------------------------------

    print("Booking ID:", booking.id)

    print(
        "Customer:",
        booking.customer.name
    )

    print(
        "Movie:",
        booking.show_seats[0].show.movie.name
    )

    print(
        "Seats:",
        [
            show_seat.seat.seat_number
            for show_seat in booking.show_seats
        ]
    )

    print(
        "Total Price:",
        booking.total_price
    )

    print(
        "Booking Status:",
        booking.status.value
    )