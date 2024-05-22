"""
Module for testing calendar model
"""
from models import CalendarModel


def test_create_document(db_session):
    """
    Test creating document model.
    """
    rules = {
        "night_time": False,
        "reservation_more_24_hours": False,
        "in_advance_hours": 24,
        "in_advance_minutes": 14,
        "in_advance_day": 14
    }
    db_obj = CalendarModel(
        calendar_id="c_19586a3da50ca06566ef62012d6829ebf4e3026108212"
                    "e9f9d0cc2fc6bc7c44a@group.calendar.google.com",
        service_alias="klub",
        reservation_type="Entire Space",
        event_name="Celý Prostor/Entire Space",
        max_people=10,
        collision_with_itself=True,
        club_member_rules=rules,
        active_member_rules=rules,
        manager_rules=rules,
        mini_services=[]
    )

    db_session.add(db_obj)
    db_session.commit()
    db_session.refresh(db_obj)
    assert db_obj is not None


def test_get_created_user(db_session):
    """
    Test get creating document model.
    """
    db_obj = db_session.get(CalendarModel,
                            "c_19586a3da50ca06566ef62012d6829"
                            "ebf4e3026108212e9f9d0cc2fc6bc7c44a"
                            "@group.calendar.google.com")
    assert db_obj.service_alias == "klub"
    assert db_obj.collision_with_itself
    assert db_obj.reservation_type == "Entire Space"
    assert db_obj.event_name == "Celý Prostor/Entire Space"
    assert db_obj.max_people == 10
