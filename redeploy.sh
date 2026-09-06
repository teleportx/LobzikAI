#!/usr/bin/env bash

set -e

# Список доступных сервисов
SERVICES=("asr" "audio_preprocessor" "bot" "lecture_processor" "web")

# Если параметры переданы — используем их
# Иначе деплоим все сервисы, кроме asr
if [ $# -gt 0 ]; then
  TARGET_SERVICES=("$@")
else
  TARGET_SERVICES=("${SERVICES[@]}")
  TARGET_SERVICES=("${TARGET_SERVICES[@]/asr}")
fi

echo "Deploying services: ${TARGET_SERVICES[*]}"

# Проверка существования сервиса
is_valid_service() {
  local service=$1

  for s in "${SERVICES[@]}"; do
    if [[ "$s" == "$service" ]]; then
      return 0
    fi
  done

  return 1
}

# Остановка сервиса
down_service() {
  local service=$1
  docker compose -f "apps/${service}/compose.yml" down
}

# Запуск сервиса
up_service() {
  local service=$1
  docker compose -f "apps/${service}/compose.yml" up -d --build
}

# Проверяем все переданные сервисы
for service in "${TARGET_SERVICES[@]}"; do
  if ! is_valid_service "$service"; then
    echo "Unknown service: $service"
    echo "Available services: ${SERVICES[*]}"
    exit 1
  fi
done

# Остановка сервисов
for service in "${TARGET_SERVICES[@]}"; do
  echo "Stopping $service..."
  down_service "$service"
done

# Обновление кода
echo "Pulling latest changes..."
git fetch && git pull

# Запуск сервисов
for service in "${TARGET_SERVICES[@]}"; do
  echo "Starting $service..."
  up_service "$service"
done

echo "Deploy completed."