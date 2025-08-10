#!/bin/sh

# Получаем версию из pyproject.toml
value=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
echo "Версия: $value"

# Создаем git тег
git tag "v$value"
git push origin --tags

echo "Тег v$value создан и отправлен в GitHub."
echo "GitHub Actions автоматически соберет и загрузит пакет в PyPI."
echo "Следите за процессом здесь: https://github.com/s00d/onlinesim-python-api/actions"