from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import get_db, StatusEnum, PriorityEnum, SessionLocal
from app.schemas.tickets import TicketCreate, TicketUpdate, TicketResponse, TicketListResponse
from app.schemas.users import UserResponse, UserRegister
from app.service import UserService, TicketService
from app.auth import verify_admin, verify_credentials
from typing import Optional
from math import ceil
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")

    print(f"RECEIVED: {admin_username} {admin_password}")

    if admin_username and admin_password:
        db = SessionLocal()
        try:
            existing_user = UserService.get_user_by_username(db, admin_username)
            if existing_user:
                print("USER EXISTS")
                existing_user.is_admin = True
                db.commit()
            else:
                print("CREATING ADMIN USER")
                UserService.create_user(
                    db,
                    admin_username,
                    admin_password,
                    is_admin=True,
                )
        finally:
            db.close()
    yield

app = FastAPI(
    title="API Заявок",
    description="API для управления внутренними заявками",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


@app.post(
    "/api/tickets",
    response_model=TicketResponse,
    tags=["Заявки"],
    summary="Создание новой заявки",
    responses={
        201: {"description": "Заявка успешно создана"},
        422: {"description": "Ошибка валидации"},
    },
)
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    return TicketService.create_ticket(db, ticket)


@app.get(
    "/api/tickets",
    response_model=TicketListResponse,
    tags=["Заявки"],
    summary="Показать заявки",
    responses={
        200: {"description": "Список заявок успешно возвращен"},
    },
)
def list_tickets(
        search: Optional[str] = Query(None,
                                      description="Поиск заявок по заголовку или описанию (case-insensitive)", ),
        status: Optional[StatusEnum] = Query(None, description="Фильтр по статусу"),
        priority: Optional[PriorityEnum] = Query(None, description="Фильтр по уровню приоритета"),
        sort_by: str = Query("created_at", pattern="^(created_at|priority)$",
                             description="Сортировка по дате создания или приоритету"),
        sort_order: str = Query("desc", pattern="^(asc|desc)$",
                                description="Направление сортировки (убывающая/возрастающая)"),
        page: int = Query(1, ge=1, description="Номер страницы для пагинации (нумерация с 1)"),
        page_size: int = Query(10, ge=1, le=100, description="Размер страницы для пагинации (max=100)"),
        db: Session = Depends(get_db),
):
    tickets, total = TicketService.get_tickets(
        db,
        search=search,
        status=status,
        priority=priority,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )

    total_pages = ceil(total / page_size)

    return TicketListResponse(
        items=[TicketResponse.model_validate(t) for t in tickets],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@app.get(
    "/api/tickets/{ticket_id}",
    response_model=TicketResponse,
    tags=["Заявки"],
    summary="Полученте заявки по ID",
    responses={
        200: {"description": "Заявка успешно возращена"},
        404: {"description": "Заявка не найдена"},
    },
)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = TicketService.get_ticket(db, ticket_id)
    return TicketResponse.model_validate(ticket)


@app.patch(
    "/api/tickets/{ticket_id}",
    response_model=TicketResponse,
    tags=["Заявки"],
    summary="Обновление статуса заявки",
    responses={
        200: {"description": "Заявка успешно обновлена"},
        400: {"description": "Модифицировать завершенную заявку невозможно"},
        404: {"description": "Заявка не найдена"},
    },
)
def update_ticket(ticket_id: int, status_update: TicketUpdate = None, db: Session = Depends(get_db)):
    ticket = TicketService.update_ticket_status(db, ticket_id, status_update)
    return TicketResponse.model_validate(ticket)


@app.delete(
    "/api/tickets/{ticket_id}",
    status_code=204,
    tags=["Заявки"],
    summary="Удаление заявки",
    responses={
        204: {"description": "Заявка успешно удалена"},
        400: {"description": "Невозможно удалить завершенную заявку"},
        401: {"description": "Неверные данные для авторизации"},
        403: {"description": "Требуются права администратора"},
        404: {"description": "Заявка не найдена"},
    },
)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db), _: bool = Depends(verify_admin)):
    TicketService.delete_ticket(db, ticket_id)


@app.post(
    "/api/users/register",
    response_model=UserResponse,
    tags=["Пользователи"],
    summary="Создать пользователя",
    responses={
        201: {"description": "Пользователь успешно зарегистрирован"},
        400: {"description": "Пользователь с таким именем уже существует"},
        422: {"description": "Ошибка валидации"},
    },
)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    user = UserService.create_user(db, user_data.username, user_data.password)
    return UserResponse.model_validate(user)


@app.get(
    "/api/users/me",
    response_model=UserResponse,
    tags=["Пользователи"],
    summary="Получить информацию о текущем пользователе",
    responses={
        200: {"description": "Информация по текущему пользователю успешно возвращена"},
        401: {"description": "Неверные данные для авторизации"},
    },
)
def get_current_user(user=Depends(verify_credentials)):
    return UserResponse.model_validate(user)


if __name__ == '__main__':
    uvicorn.run(app, port=8000, host='0.0.0.0')
