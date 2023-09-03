## Скрипт для работы с очередью в Asterisk и Bitrix24

Данный скрипт решает задачу синхронизации очереди Asterisk (AMI) с информацией из Bitrix24. Основная цель - обеспечить соответствие номеров в очереди Asterisk списку сотрудников из Bitrix24, у которых открыт рабочий день и выбран департамент.

### Переменные окружения:

- **ASTERISK_IP**: IP-адрес сервера Asterisk.
- **AMI_USERNAME**: Имя пользователя для подключения к AMI.
- **AMI_PASSWORD**: Пароль пользователя для подключения к AMI.
- **QUEUE_NAME**: (опционально) Имя очереди в Asterisk. Можно получить при запуске скрипта. docker-compose up
- **B24_HOOK**: Веб-хук для доступа к API Bitrix24.
- **B24_DEPARTMENT_ID**: ID отдела в Bitrix24.

### Основные функции:

1. **get_open_day_users_from_bitrix24()**: Запрашивает список сотрудников из Bitrix24, у которых открыт рабочий день.
2. **is_dynamic_number()**: Проверяет, является ли номер динамическим в очереди Asterisk.
3. **get_queue_status()**: Получает статус всех очередей в Asterisk.
4. **get_current_queue_numbers()**: Получает список номеров, находящихся в указанной очереди.
5. **add_expected_numbers_to_queue()**: Добавляет ожидаемые номера в очередь, если они там отсутствуют.
6. **remove_unexpected_numbers_from_queue()**: Удаляет неожиданные динамические номера из очереди.

### Начало работы:

1. Убедитесь, что у вас установлены библиотеки `requests` и `asterisk.manager`.
2. Установите все необходимые переменные окружения.
3. Запустите скрип

### Начало работы в docker
1. У вас должен быть установлен docker и docker-compose . Скрипт установки тут https://github.com/roysbike/scripts/blob/main/install_docker.sh
2. Скопируйте проект
3. docker-compose build
4. docker-compose up или docker-compose up -d как демон
