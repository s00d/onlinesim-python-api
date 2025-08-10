# Инструкция по публикации через GitHub

## 🚀 Автоматическая публикация в PyPI через GitHub Actions

### Как это работает

1. **Создается git тег** с версией (например, `v2.1.0`)
2. **GitHub Actions автоматически запускается** при пуше тега
3. **Пакет собирается** с помощью modern Python tools
4. **Загружается в PyPI** с использованием API токена
5. **Создается GitHub Release** с собранными файлами

### 📋 Предварительная настройка (только один раз)

#### Шаг 1: Создание API токена PyPI

1. Зайдите на [PyPI](https://pypi.org/) и войдите в свой аккаунт
2. Перейдите в **Account settings** → **API tokens**
3. Нажмите **Add API token**
4. Выберите **Entire account (all projects)**
5. Скопируйте созданный токен (выглядит как `pypi-...`)

#### Шаг 2: Настройка GitHub Secrets

1. Перейдите в ваш GitHub репозиторий
2. Нажмите **Settings** → **Secrets and variables** → **Actions**
3. Нажмите **New repository secret**
4. Создайте секрет с именем `PYPI_API_TOKEN` и значением вашего PyPI токена

#### Шаг 3: Настройка Environment

1. В том же разделе **Secrets and variables** → **Actions**
2. Перейдите на вкладку **Environments**
3. Нажмите **New environment**
4. Назовите среду `pypi`
5. В разделе **Environment protection rules** можете добавить правила (опционально)

### 🔄 Процесс публикации новой версии

#### Шаг 1: Обновить версию

Обновите версию в `pyproject.toml`:

```toml
[project]
name = "onlinesimru"
version = "2.1.0"  # Измените на новую версию
```

**Важно**: Версия теперь управляется только в `pyproject.toml`. Файл `_version.py` больше не используется.

#### Шаг 2: Обновить CHANGELOG.md

Добавьте запись о новой версии в начало файла:

```markdown
## [2.1.0] - 2025-08-10
### Added
- Новые функции

### Changed
- Изменения

### Fixed
- Исправления
```

#### Шаг 3: Зафиксировать изменения

```bash
git add .
git commit -m "Bump version to 2.1.0"
git push origin main
```

#### Шаг 4: Создать тег и запустить публикацию

```bash
./deploy.sh
```

Этот скрипт:
- Создает git тег с версией
- Пушит тег в GitHub
- Запускает автоматическую публикацию

### 📊 Мониторинг процесса

#### GitHub Actions
1. Перейдите в **Actions** в вашем репозитории
2. Найдите workflow **Publish to PyPI**
3. Следите за выполнением шагов

#### GitHub Releases
1. После успешной публикации автоматически создается Release
2. Перейдите в **Releases** в вашем репозитории
3. Скачайте собранные файлы

#### PyPI
1. Проверьте [PyPI](https://pypi.org/project/onlinesimru/)
2. Убедитесь, что новая версия доступна

### ✅ Преимущества этого подхода

- 🔒 **Безопасность**: API токен хранится в GitHub Secrets
- 🤖 **Автоматизация**: Не нужно вручную собирать и загружать
- 🆕 **Современность**: Использует современные инструменты сборки
- 📝 **Аудит**: Все действия логируются в GitHub Actions
- 🎯 **Контроль**: Можно настроить правила для environment
- 🏷️ **Теги**: Четкая связь между git тегами и версиями PyPI

### 🚨 Troubleshooting

#### Если workflow не запускается:
1. Проверьте, что тег создан в правильном формате (`v*`)
2. Убедитесь, что тег запушен в GitHub
3. Проверьте настройки в **Settings** → **Actions** → **General**

#### Если публикация в PyPI не удалась:
1. Проверьте логи в GitHub Actions
2. Убедитесь, что `PYPI_API_TOKEN` правильно настроен
3. Проверьте, что environment `pypi` создан

#### Если пакет не собирается:
1. Проверьте синтаксис `pyproject.toml`
2. Убедитесь, что все зависимости указаны правильно
3. Проверьте, что Python версия совместима

### 🔧 Ручная сборка (если нужно)

Если нужно собрать пакет локально:

```bash
# Установить зависимости
pip install build twine

# Собрать пакет
python -m build --wheel --sdist

# Загрузить в PyPI (требует настройки ~/.pypirc)
python -m twine upload dist/*
```

### 📚 Полезные ссылки

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyPI API Tokens](https://pypi.org/help/api-tokens/)
- [Python Packaging User Guide](https://packaging.python.org/)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github)

---

**Теперь ваша публикация полностью автоматизирована! 🎉**

Просто обновите версию, создайте тег через `./deploy.sh`, и GitHub Actions сделает все остальное.
