# Профильное задание
## Python-разработчик


## Django-сервис друзей.
### Сервис предоставляет возможности:

- зарегистрировать нового пользователя 
- отправить одному пользователю заявку в друзья другому
- принять/отклонить пользователю заявку в друзья от другого пользователя
- посмотреть пользователю список своих исходящих и входящих заявок в друзья
- посмотреть пользователю список своих друзей
- получить пользователю статус дружбы с каким-то другим пользователем (нет ничего / есть исходящая заявка / есть входящая заявка / уже друзья)
- удалить пользователю другого пользователя из своих друзей
- если пользователь1 отправляет заявку в друзья пользователю2, а пользователь2 отправляет заявку пользователю1, то они автоматом становятся друзьями, их заявки автоматом принимаются

### Результаты:

- написан сервис на Django по данной спецификации
- описан REST интерфейс сервиса с помощью OpenAPI
- написана краткая документация ([DOCUMENTATION.md](./DOCUMENTATION.md)) с примерами запуска сервера и вызова его API
- написан Dockerfile для упаковки в контейнер

### P. S.

- ТЗ не описывает способ авторизации (токены, jwt и т. д.), поэтому авторизации как таковой нет


