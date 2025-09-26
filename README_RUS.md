# Voice Summarizer

CLI инструмент для автоматической транскрибации аудио и видео файлов с возможностью создания текстовых резюме. Использует API OpenAI для обработки
медиафайлов.

## Системные требования

- Python 3.12 или выше
- Менеджер зависимостей `uv`
- Установленные системные утилиты: `ffmpeg` и `ffprobe`
- Активный API ключ OpenAI

## Установка

### 1. Установка системных зависимостей

**macOS (через Homebrew):**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Скачайте ffmpeg с официального сайта https://ffmpeg.org/download.html

### 2. Установка Python зависимостей

```bash
# Установка зависимостей проекта
uv sync
```

### 3. Настройка переменных окружения

```bash
# Копирование шаблона конфигурации
cp .env.example .env

# Редактирование конфигурации
nano .env
```

Заполните следующие параметры в файле `.env`:

```bash
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_WHISPER_MODEL=whisper-1
OPENAI_SUMMARY_MODEL=gpt-4o-mini
```

## Структура проекта

```
voice/
├── main.py                  # Основной скрипт транскрибации
├── summarization_prompt.md  # Шаблон промпта для суммаризации
├── .env.example            # Пример конфигурации
├── Dockerfile              # Docker образ
├── docker-compose.yml      # Docker Compose конфигурация
├── input/                  # Директория для входных файлов
└── output/                 # Директория для результатов
```

## Использование

### Базовая транскрибация

```bash
# Транскрибация одного файла
python main.py input/recording.mp4

# Указание пользовательской директории вывода
python main.py input/recording.mp4 -o custom_output
```

### Транскрибация с суммаризацией

```bash
# Транскрибация с автоматическим созданием резюме
python main.py input/recording.mp4 --summarize

# Использование пользовательского промпта для суммаризации
python main.py input/recording.mp4 --summarize --prompt-file custom_prompt.md
```

### Настройка моделей

```bash
# Указание конкретной модели Whisper
python main.py input/recording.mp4 --whisper-model whisper-1

# Указание модели для суммаризации
python main.py input/recording.mp4 --summarize --summary-model gpt-4

# Полная настройка с пользовательскими параметрами
python main.py input/recording.mp4 \
    --whisper-model whisper-1 \
    --summarize \
    --summary-model gpt-4 \
    --prompt-file my_prompt.md \
    --api-key YOUR_API_KEY \
    --base-url https://custom-endpoint.com/v1
```

## Использование с Docker

Для пользователей, предпочитающих Docker, предоставлены готовые конфигурации.

### Быстрый старт с Docker

```bash
# 1. Подготовка окружения
cp .env.example .env
# Отредактируйте .env файл с вашим OpenAI API ключом

# 2. Поместите аудио/видео файлы в директорию input/
cp your-recording.mp4 input/

# 3. Сборка и запуск с Docker Compose
docker-compose build
docker-compose run voice-summarizer input/your-recording.mp4 --summarize
```

### Ручная сборка Docker образа

```bash
# Сборка образа
docker build -t voice-summarizer .

# Запуск контейнера
docker run -v $(pwd)/input:/app/input:ro \
           -v $(pwd)/output:/app/output \
           -v $(pwd)/.env:/app/.env:ro \
           voice-summarizer input/your-file.mp4 --summarize
```

### Docker Compose команды

```bash
# Показать справку
docker-compose run voice-summarizer --help

# Базовая транскрибация
docker-compose run voice-summarizer input/recording.mp4

# Транскрибация с суммаризацией
docker-compose run voice-summarizer input/recording.mp4 --summarize

# Использование custom модели
docker-compose run voice-summarizer input/recording.mp4 \
    --whisper-model whisper-1 \
    --summarize \
    --summary-model gpt-4

# Режим разработки (интерактивная оболочка)
docker-compose run voice-summarizer-dev
```

## Параметры командной строки

| Параметр | Описание |
|----------|----------|
| `input_file` | Путь к входному аудио/видео файлу |
| `-o, --output` | Директория для сохранения результатов (по умолчанию: Output) |
| `--api-key` | API ключ OpenAI (альтернатива переменной OPENAI_API_KEY) |
| `--base-url` | Базовый URL для API OpenAI (альтернатива переменной OPENAI_BASE_URL) |
| `--whisper-model` | Модель Whisper для транскрибации (по умолчанию: whisper-1) |
| `--summary-model` | Модель для создания резюме (по умолчанию: gpt-4o-mini) |
| `--summarize` | Включить создание текстового резюме |
| `--prompt-file` | Путь к файлу с промптом для суммаризации (по умолчанию: summarization_prompt.md) |

## Структура выходных файлов

После обработки создается следующая структура директорий:

```
output/
└── filename.ext/
    ├── filename_combined.md              # Объединенная транскрипция
    ├── filename_summary.md               # Резюме (если включено)
    └── segments/
        ├── filename_segment_001.mp3      # Аудио сегмент 1
        ├── filename_segment_001.md       # Транскрипция сегмента 1
        ├── filename_segment_002.mp3      # Аудио сегмент 2
        └── filename_segment_002.md       # Транскрипция сегмента 2
```

## Поддерживаемые форматы файлов

Инструмент поддерживает все форматы, совместимые с ffmpeg:

**Аудио:** MP3, WAV, FLAC, AAC, OGG, M4A
**Видео:** MP4, AVI, MOV, MKV, WMV, FLV

## Технические особенности

- Максимальная длительность сегмента: 570 секунд (9.5 минут)
- Автоматическое разбиение длинных файлов на сегменты
- Конвертация всех сегментов в формат MP3
- Логирование процесса обработки с временными метками
- Обработка ошибок API и файловых операций

## Создание пользовательского промпта

Для создания собственного промпта суммаризации:

1. Скопируйте файл `summarization_prompt.md`
2. Модифицируйте содержимое согласно требованиям
3. Промпт используется как системное сообщение, текст транскрипции передается отдельно
4. Укажите путь к файлу через параметр `--prompt-file` или переменную окружения `PROMPT_FILE`

## Лицензия

Этот проект лицензирован под лицензией MIT - см. файл [LICENSE](LICENSE) для подробностей.

