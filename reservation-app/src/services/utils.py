"""Utils for services."""

import datetime as dt

from core.application.exceptions import SoftValidationError
from core.models import ReservationServiceModel
from core.schemas import Rules, ServiceValidity


def first_standard_check(
    services: list[ServiceValidity],
    reservation_service: ReservationServiceModel,
    start_time,
    end_time,
):
    """
    Check if the user is reserving the service user has.

    That user can't reserve before current date.

    :param services: UserLite services from IS.
    :param reservation_service: Reservation Service object in db.
    :param start_time: Start time of the reservation.
    :param end_time: End time of the reservation.

    :return: True indicating if the reservation
    is made rightly or message if not.
    """
    # Check of the membership
    if not service_availability_check(services, reservation_service.alias):
        raise SoftValidationError(f"You don't have {reservation_service.alias} service!")

    # Check error reservation
    if start_time < dt.datetime.now():
        raise SoftValidationError("You can't make a reservation before the present time!")

    if end_time < start_time:
        raise SoftValidationError("The end of a reservation cannot be before its beginning!")


def reservation_in_advance(start_time, user_rules):
    """
    Check if the reservation is made within the specified advance and prior time.

    :param start_time: Start time of the reservation.
    :param user_rules: Rules object containing reservation rules.
    reservation is made in advance or in prior.

    :return: True indicating if the reservation
    is made within the specified advance or prior time or message if not.
    """
    # Reservation in advance
    if not control_res_in_advance_or_prior(start_time, user_rules, True):
        raise SoftValidationError(
            f"You have to make reservations "
            f"{user_rules.in_advance_hours} hours and "
            f"{user_rules.in_advance_minutes} minutes in advance!"
        )

    # Reservation prior than
    if not control_res_in_advance_or_prior(start_time, user_rules, False):
        raise SoftValidationError(
            f"You can't make reservations earlier than {user_rules.in_prior_days} days in advance!"
        )


def dif_days_res(start_datetime, end_datetime, user_rules: Rules) -> bool:
    """
    Check if the reservation duration is less than 24 hours.

    :param start_datetime: Start datetime of the reservation.
    :param end_datetime: End datetime of the reservation.
    :param user_rules: Rules object containing reservation rules.

    :return: Boolean indicating if the reservation duration is less than 24
    """
    time_difference = abs(end_datetime - start_datetime)
    return not time_difference > dt.timedelta(hours=user_rules.max_reservation_hours)


def control_res_in_advance_or_prior(
    start_time,
    user_rules: Rules,
    in_advance: bool,
) -> bool:
    """
    Check if the reservation is made within the specified advance or prior time.

    :param start_time: Start time of the reservation.
    :param user_rules: Rules object containing reservation rules.
    :param in_advance: Boolean indicating whether to check if the
    reservation is made in advance or in prior.

    :return: Boolean indicating if the reservation
    is made within the specified advance or prior time.
    """
    current_time = dt.datetime.now()

    time_difference = abs(start_time - current_time)

    if in_advance:
        if time_difference < dt.timedelta(
            minutes=user_rules.in_advance_minutes,
            hours=user_rules.in_advance_hours,
        ):
            return False
    else:
        if time_difference > dt.timedelta(days=user_rules.in_prior_days):
            return False
    return True


def service_availability_check(services: list[ServiceValidity], service_alias) -> bool:
    """
    Check if the user is reserving the service user has.

    :param services: List of available user services on IS.
    :param service_alias: The alias of the service user wants to reserve .

    :return: Boolean indicating if a user have this service or not.
    """
    return any(service.service.alias == service_alias for service in services)
