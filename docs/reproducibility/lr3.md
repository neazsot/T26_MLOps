# Протокол воспроизводимости ЛР3

Таблица версий:

Версия v1:
Git commit: 7174a36
DVC hash: 6876190b8c70d3f62e26fffc3ac68514
SHA-256: 3efed8a5044924e729a4d8c137a9a1ae0a0217432840ae5594d20710eb31df0b
Период: 2024-01-01 — 2024-01-05
Строк: 11
Контракт: 1.0.0
Результат: passed

Версия v2:
Git commit: 47f8f44
DVC hash: 6876190b8c70d3f62e26fffc3ac68514
SHA-256: 35ce3f1f75131bd9ae68dd2287dcc170c712c6e579265618e63f8c721f457
Период: 2024-01-01 — 2024-01-06
Строк: 13
Контракт: 1.0.0
Результат: passed

Команды восстановления v1:
git checkout 7174a36
dvc checkout
python src/validate_data.py data/flights_sample.csv data/contract.json

Команды восстановления v2:
git checkout 47f8f44
dvc checkout
python src/validate_data.py data/flights_sample.csv data/contract.jsonon```