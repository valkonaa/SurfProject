# Этап 4: Тестирование и багфикс

**Промпт для ИИ:**
> "Действуй как QA Engineer. Напиши тест-кейсы для API бронирования мастер-классов. Один из тест-кейсов должен проверять поведение системы, когда на мастер-класс закончились свободные места (slots = 0)."

### Тест-кейсы
1. **TC-01: Получение списка мастер-классов.** Отправить `GET /workshops`. Ожидаемый результат: Статус 200, возвращается массив из 3-х объектов.
2. **TC-02: Успешное бронирование.** Отправить `POST /bookings` с `workshop_id: 2`. Ожидаемый результат: Статус 200, бронь создана, количество `slots` для id 2 уменьшилось с 2 до 1.
3. **TC-03: Бронирование при отсутствии мест (Негативный).** Отправить `POST /bookings` с `workshop_id: 3` (где `slots: 0`). Ожидаемый результат: Статус 400 Bad Request, ошибка "Нет свободных мест".

### Обнаруженный баг
* **Симптом:** При выполнении TC-03 (запись на "Скульптуру", где 0 мест), система возвращает статус 200 OK и успешно создает бронь. Происходит овербукинг. Кроме того, при успешных бронях общее число `slots` в каталоге не уменьшается.

### Исправление (Багфикс)
В файле `main.py` изменяем эндпоинт `POST /bookings`. 

**Новый исправленный код эндпоинта:**
```python
@app.post("/bookings", response_model=BookingResponse)
def create_booking(booking: BookingCreate):
    global booking_id_counter
    
    workshop = next((w for w in workshops_db if w["id"] == booking.workshop_id), None)
    if not workshop:
        raise HTTPException(status_code=404, detail="Мастер-класс не найден")
    
    # ИСПРАВЛЕНИЕ БАГА: Проверка наличия мест
    if workshop["slots"] <= 0:
        raise HTTPException(status_code=400, detail="Нет свободных мест на этот мастер-класс")
    
    # ИСПРАВЛЕНИЕ БАГА: Уменьшение количества мест
    workshop["slots"] -= 1
    
    new_booking = {
        "id": booking_id_counter,
        "workshop_id": booking.workshop_id,
        "client_name": booking.client_name,
        "client_phone": booking.client_phone
    }
    bookings_db.append(new_booking)
    booking_id_counter += 1
    return new_booking