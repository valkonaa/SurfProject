from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Гончарная мастерская «Глиняный Уют»")

# Имитация базы данных
workshops_db = [
    {"id": 1, "title": "Ваза на гончарном круге", "price": 2500, "slots": 5},
    {"id": 2, "title": "Лепка чайной кружки", "price": 1800, "slots": 2},
    {"id": 3, "title": "Скульптура: Интерьерное плато", "price": 3000, "slots": 0}  # Мест нет
]

bookings_db = []
booking_id_counter = 1


# Модели данных
class BookingCreate(BaseModel):
    workshop_id: int
    client_name: str
    client_phone: str


class BookingResponse(BaseModel):
    id: int
    workshop_id: int
    client_name: str
    client_phone: str


# 1: Получение списка мастер-классов
@app.get("/workshops")
def get_workshops():
    return workshops_db


# 2: Создание бронирования
@app.post("/bookings", response_model=BookingResponse)
def create_booking(booking: BookingCreate):
    global booking_id_counter

    # 1. Ищем мастер-класс в нашей базе данных
    workshop = next((w for w in workshops_db if w["id"] == booking.workshop_id), None)
    if not workshop:
        raise HTTPException(status_code=404, detail="Мастер-класс не найден")

    # 2. ИСПРАВЛЕНИЕ БАГА: Проверяем, есть ли свободные места
    if workshop["slots"] <= 0:
        raise HTTPException(status_code=400, detail="Нет свободных мест на этот мастер-класс")

    # 3. ИСПРАВЛЕНИЕ БАГА: Уменьшаем количество доступных мест на 1
    workshop["slots"] -= 1

    # 4. Создаем и сохраняем бронь
    new_booking = {
        "id": booking_id_counter,
        "workshop_id": booking.workshop_id,
        "client_name": booking.client_name,
        "client_phone": booking.client_phone
    }
    bookings_db.append(new_booking)
    booking_id_counter += 1
    return new_booking


# 3: Просмотр бронирований для админа.
@app.get("/admin/bookings")
def get_admin_bookings():
    return bookings_db


# Фронтенд.
@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head><title>Гончарная мастерская</title></head>
        <body style="font-family: Arial, sans-serif; margin: 40px;">
            <h1>Добро пожаловать в Гончарную мастерскую!</h1>
            <p>Наше приложение запущено. Чтобы протестировать функции и сделать бронирование, перейдите в интерактивный UI:</p>
            <a href="/docs" style="padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px;">Открыть Swagger UI (Тестирование API)</a>
        </body>
    </html>
    """