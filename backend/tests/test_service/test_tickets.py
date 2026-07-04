import pytest
from sqlalchemy.orm import Session
from app.service import TicketService
from app.schemas.tickets import TicketCreate, TicketUpdate
from app.database import StatusEnum, PriorityEnum
from fastapi import HTTPException


class TestTicketServiceCreate:
    def test_create_ticket_success(self, db_session: Session):
        ticket_create = TicketCreate(title="Test Ticket", description="Test description", priority=PriorityEnum.high)
        ticket = TicketService.create_ticket(db_session, ticket_create)
        assert ticket.title == "Test Ticket"
        assert ticket.description == "Test description"
        assert ticket.priority == PriorityEnum.high
        assert ticket.status == StatusEnum.new

    def test_create_ticket_without_description(self, db_session: Session):
        ticket_create = TicketCreate(title="Test Ticket")
        ticket = TicketService.create_ticket(db_session, ticket_create)
        assert ticket.title == "Test Ticket"
        assert ticket.description is None

    def test_create_ticket_default_priority(self, db_session: Session):
        ticket_create = TicketCreate(title="Test Ticket")
        ticket = TicketService.create_ticket(db_session, ticket_create)
        assert ticket.priority == PriorityEnum.normal


class TestTicketServiceRetrieval:
    def test_get_ticket_success(self, db_session: Session):
        ticket_create = TicketCreate(title="Test Ticket")
        created_ticket = TicketService.create_ticket(db_session, ticket_create)
        retrieved_ticket = TicketService.get_ticket(db_session, created_ticket.id)
        assert retrieved_ticket.id == created_ticket.id
        assert retrieved_ticket.title == "Test Ticket"

    def test_get_nonexistent_ticket(self, db_session: Session):
        with pytest.raises(HTTPException) as exc_info:
            TicketService.get_ticket(db_session, 999)
        assert exc_info.value.status_code == 404

    def test_get_tickets_empty(self, db_session: Session):
        tickets, total = TicketService.get_tickets(db_session)
        assert tickets == []
        assert total == 0

    def test_get_tickets_with_items(self, db_session: Session):
        ticket_create_1 = TicketCreate(title="Ticket 1")
        ticket_create_2 = TicketCreate(title="Ticket 2")
        TicketService.create_ticket(db_session, ticket_create_1)
        TicketService.create_ticket(db_session, ticket_create_2)
        tickets, total = TicketService.get_tickets(db_session)
        assert len(tickets) == 2
        assert total == 2


class TestTicketServiceSearch:
    def test_search_by_title(self, db_session: Session):
        TicketService.create_ticket(db_session, TicketCreate(title="Login Bug", description="OAuth issue"))
        TicketService.create_ticket(db_session, TicketCreate(title="Database Migration", description="Schema update"))
        tickets, total = TicketService.get_tickets(db_session, search="Login")
        assert total == 1
        assert tickets[0].title == "Login Bug"

    def test_search_by_description(self, db_session: Session):
        TicketService.create_ticket(db_session, TicketCreate(title="Testest1", description="OAuth issue"))
        TicketService.create_ticket(db_session, TicketCreate(title="Testest2", description="Cache problem"))
        tickets, total = TicketService.get_tickets(db_session, search="OAuth")
        assert total == 1
        assert tickets[0].description == "OAuth issue"

    def test_search_case_insensitive(self, db_session: Session):
        TicketService.create_ticket(db_session, TicketCreate(title="Login Bug", description="test"))
        tickets, total = TicketService.get_tickets(db_session, search="login")
        assert total == 1
        assert tickets[0].title == "Login Bug"


class TestTicketServiceFiltering:
    def test_filter_by_status(self, db_session: Session):
        ticket_create = TicketCreate(title="Test")
        ticketest1 = TicketService.create_ticket(db_session, ticket_create)
        ticketest2 = TicketService.create_ticket(db_session, ticket_create)

        TicketService.update_ticket_status(db_session, ticketest2.id, TicketUpdate(status=StatusEnum.in_progress))
        tickets, total = TicketService.get_tickets(db_session, status=StatusEnum.in_progress)

        assert total == 1
        assert tickets[0].id == ticketest2.id

    def test_filter_by_priority(self, db_session: Session):
        TicketService.create_ticket(db_session, TicketCreate(title="Test1", priority=PriorityEnum.high))
        TicketService.create_ticket(db_session, TicketCreate(title="Test2", priority=PriorityEnum.low))

        tickets, total = TicketService.get_tickets(db_session, priority=PriorityEnum.high)

        assert total == 1
        assert tickets[0].priority == PriorityEnum.high

    def test_filter_by_multiple_criteria(self, db_session: Session):
        TicketService.create_ticket(db_session, TicketCreate(title="Test1", priority=PriorityEnum.high))
        ticketest2 = TicketService.create_ticket(db_session, TicketCreate(title="Test2", priority=PriorityEnum.high))

        TicketService.update_ticket_status(
            db_session, ticketest2.id, TicketUpdate(status=StatusEnum.in_progress)
        )

        tickets, total = TicketService.get_tickets(db_session, status=StatusEnum.in_progress,
                                                   priority=PriorityEnum.high)

        assert total == 1
        assert tickets[0].id == ticketest2.id


class TestTicketServiceSorting:
    def test_sort_by_created_at_desc(self, db_session: Session):
        ticketest1 = TicketService.create_ticket(db_session, TicketCreate(title="First"))
        ticketest2 = TicketService.create_ticket(db_session, TicketCreate(title="Second"))

        tickets, _ = TicketService.get_tickets(db_session, sort_by="created_at", sort_order="desc")

        assert tickets[0].id == ticketest2.id
        assert tickets[1].id == ticketest1.id

    def test_sort_by_created_at_asc(self, db_session: Session):
        ticketest1 = TicketService.create_ticket(db_session, TicketCreate(title="First"))
        ticketest2 = TicketService.create_ticket(db_session, TicketCreate(title="Second"))
        tickets, _ = TicketService.get_tickets(db_session, sort_by="created_at", sort_order="asc")
        assert tickets[0].id == ticketest1.id
        assert tickets[1].id == ticketest2.id

    def test_sort_by_priority_asc(self, db_session: Session):
        TicketService.create_ticket(db_session, TicketCreate(title="Test1", priority=PriorityEnum.low))
        TicketService.create_ticket(db_session, TicketCreate(title="Test2", priority=PriorityEnum.high))
        tickets, _ = TicketService.get_tickets(db_session, sort_by="priority", sort_order="asc")
        assert tickets[0].priority == PriorityEnum.low
        assert tickets[1].priority == PriorityEnum.high

    def test_sort_by_priority_desc(self, db_session: Session):
        TicketService.create_ticket(db_session, TicketCreate(title="Test1", priority=PriorityEnum.low))
        TicketService.create_ticket(db_session, TicketCreate(title="Test2", priority=PriorityEnum.high))
        tickets, _ = TicketService.get_tickets(db_session, sort_by="priority", sort_order="desc")
        assert tickets[0].priority == PriorityEnum.high
        assert tickets[1].priority == PriorityEnum.low


class TestTicketServicePagination:
    def test_pagination_first_page(self, db_session: Session):
        for i in range(15):
            TicketService.create_ticket(db_session, TicketCreate(title=f"Ticket {i}"))
        tickets, total = TicketService.get_tickets(db_session, page=1, page_size=10)
        assert len(tickets) == 10
        assert total == 15

    def test_pagination_second_page(self, db_session: Session):
        for i in range(15):
            TicketService.create_ticket(db_session, TicketCreate(title=f"Ticket {i}"))
        tickets, total = TicketService.get_tickets(db_session, page=2, page_size=10)
        assert len(tickets) == 5
        assert total == 15

    def test_pagination_custom_page_size(self, db_session: Session):
        for i in range(25):
            TicketService.create_ticket(db_session, TicketCreate(title=f"Ticket {i}"))
        tickets, total = TicketService.get_tickets(db_session, page=1, page_size=5)
        assert len(tickets) == 5
        assert total == 25


class TestTicketServiceStatusUpdate:
    def test_update_ticket_status(self, db_session: Session):
        ticket = TicketService.create_ticket(db_session, TicketCreate(title="Test"))
        updated_ticket = TicketService.update_ticket_status(
            db_session, ticket.id, TicketUpdate(status=StatusEnum.in_progress)
        )
        assert updated_ticket.status == StatusEnum.in_progress

    def test_cannot_modify_done_ticket(self, db_session: Session):
        ticket = TicketService.create_ticket(db_session, TicketCreate(title="Test"))
        TicketService.update_ticket_status(db_session, ticket.id, TicketUpdate(status=StatusEnum.done))
        with pytest.raises(HTTPException) as exc_info:
            TicketService.update_ticket_status(db_session, ticket.id, TicketUpdate(status=StatusEnum.in_progress))
        assert exc_info.value.status_code == 400

    def test_update_nonexistent_ticket(self, db_session: Session):
        with pytest.raises(HTTPException) as exc_info:
            TicketService.update_ticket_status(db_session, 999, TicketUpdate(status=StatusEnum.in_progress))
        assert exc_info.value.status_code == 404


class TestTicketServiceDeletion:
    def test_delete_ticket(self, db_session: Session):
        ticket = TicketService.create_ticket(db_session, TicketCreate(title="Test"))
        TicketService.delete_ticket(db_session, ticket.id)
        with pytest.raises(HTTPException):
            TicketService.get_ticket(db_session, ticket.id)

    def test_cannot_delete_done_ticket(self, db_session: Session):
        ticket = TicketService.create_ticket(db_session, TicketCreate(title="Test"))
        TicketService.update_ticket_status(db_session, ticket.id, TicketUpdate(status=StatusEnum.done))
        with pytest.raises(HTTPException) as exc_info:
            TicketService.delete_ticket(db_session, ticket.id)
        assert exc_info.value.status_code == 400

    def test_delete_nonexistent_ticket(self, db_session: Session):
        with pytest.raises(HTTPException) as exc_info:
            TicketService.delete_ticket(db_session, 999)
        assert exc_info.value.status_code == 404
