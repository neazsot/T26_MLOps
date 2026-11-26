# LR5 Evidence Card — @neazsot

| Поле | Значение |
|------|----------|
| Студент | Третьякова Анастасия Владимировна, Т.МО41, команда 5, @neazsot |
| Роль | Data test engineer, Model test engineer, Evaluation test engineer |
| Задача | Issue #<номер твоего Issue> |
| Личный артефакт | Файлы tests/conftest.py, tests/test_pipeline.py, исправленный src/validate_data.py |
| Вклад | Написала параметризованные тесты, фикстуры, исправила валидатор для проверки дат |
| Контролируемый риск | Некорректные данные (DepHour=25, IsWeekend=2, неверная дата) и отсутствие колонки |
| Defect injection | (Если делала - опиши, если нет - оставь пустым или напиши "не проводился") |
| Диагностика | Тест падал с KeyError: 'target', исправлено добавлением функции load_data_from_frame |
| Воспроизведение | `python -m pytest tests/test_pipeline.py -v` |
| Использование ИИ | Сгенерировала тесты и структуру, проверила их локально в PyCharm |
