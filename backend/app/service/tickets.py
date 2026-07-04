from sqlalchemy.orm import Session
from sqlalchemy import or_, case
from app.database import Ticket, StatusEnum, PriorityEnum
from app.schemas.tickets import TicketCreate, TicketUpdate
from fastapi import HTTPException
from typing import Optional


class TicketService:
    @staticmethod
    def create_ticket(db: Session, ticket_create: TicketCreate) -> Ticket:
        db_ticket = Ticket(title=ticket_create.title, description=ticket_create.description,
                           priority=ticket_create.priority)
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        return db_ticket

    @staticmethod
    def get_tickets(
            db: Session,
            search: Optional[str] = None,
            status: Optional[StatusEnum] = None,
            priority: Optional[PriorityEnum] = None,
            sort_by: str = "created_at",
            sort_order: str = "desc",
            page: int = 1,
            page_size: int = 10,
    ) -> tuple[list[Ticket], int]:
        query = db.query(Ticket)

        if search:
            search_filter = or_(
                Ticket.title.ilike(f"%{search}%"),
                Ticket.description.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        if status:
            query = query.filter(Ticket.status == status)

        if priority:
            query = query.filter(Ticket.priority == priority)

        total = query.count()

        if sort_by == "priority":
            priority_order = {"low": 0, "normal": 1, "high": 2}
            priority_case = case(priority_order, value=Ticket.priority)
            query = query.order_by(priority_case.asc() if sort_order == "asc" else priority_case.desc())
        else:
            sort_column = getattr(Ticket, sort_by, Ticket.created_at)
            if sort_order == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())

        skip = (page - 1) * page_size
        tickets = query.offset(skip).limit(page_size).all()

        return tickets, total

    @staticmethod
    def update_ticket_status(db: Session, ticket_id: int, status_update: TicketUpdate) -> Ticket:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(status_code=404, detail="Заявка не найдена")

        if ticket.status == StatusEnum.done:
            raise HTTPException(status_code=400,
                                detail="Невозможно изменить заявку, находящуюся в статусе \"Выполнено\".")

        if ticket.status == StatusEnum.done and status_update.status != StatusEnum.done:
            raise HTTPException(status_code=400, detail="Невозможно изменить статус выполненной заявки на другой.")

        ticket.status = status_update.status
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def delete_ticket(db: Session, ticket_id: int) -> None:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(status_code=404, detail="Заявка не найдена")

        if ticket.status == StatusEnum.done:
            raise HTTPException(status_code=400,
                                detail="Невозможно удалить заявку, находящуюся в статусе \"Выполнено\".")

        db.delete(ticket)
        db.commit()

    @staticmethod
    def get_ticket(db: Session, ticket_id: int) -> Ticket:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(status_code=404, detail="Заявка не найдена")
        return ticket
