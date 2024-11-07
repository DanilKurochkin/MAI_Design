Задание третьей лабораторной работы

1. Создайте сервис на Python который реализует сервисы, спроектированные в
первом задании (по проектированию). Должно быть реализовано как минимум
два сервиса (управления пользователем, и хотя бы один «бизнес» сервис)
2. Сервис должен поддерживать аутентификацию с использованием JWT-token
3. Сервис должен реализовывать как минимум GET/POST методы
4. Данные сервиса должны храниться в памяти
5. В целях проверки должен быть заведён мастер-пользователь (имя admin,
пароль secret)
Дополнение третьей ЛР:
6. Данные должны храниться в СУБД PostgreSQL;
7. Должны быть созданы таблицы для каждой сущности из вашего задания;
8. Должен быть создан скрипт по созданию базы данных и таблиц, а также
наполнению СУБД тестовыми значениями;
9. Для сущности, должны быть созданы запросы к БД (CRUD) согласно ранее
разработанной архитектуре
10. Данные о пользователе должны включать логин и пароль. Пароль должен
храниться в закрытом виде (хэширован) – в этом задании опционально
11. Должно применяться индексирования по полям, по которым будет
производиться поиск
Работа должны содержать docker-compose.yml, который:
- запускает приложение app в контейнере (собирается из dockerfile), которое
выполняет выриант задания
- запускает базу данных PostgreSQL в отдельном контейнере
- проводит первоначальную инициализацию базы данных




https://360.yandex.ru/disk/
Приложение должно содержать следующие данные:
- папка
- файл
- пользователь
Реализовать API:
- Создание нового пользователя
- Поиск пользователя по логину
- Поиск пользователя по маске имя и фамилии
- Создание новой папки
- Получение списка всех папок
- Создание файла в папке
- Получение файла по имение
- Удаление фалйла
- Удаление папки