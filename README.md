# 🎬 Video-To-Text Scripts

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![PyQt6](https://img.shields.io/badge/UI-PyQt6-green?style=for-the-badge&logo=qt)
![CUDA](https://img.shields.io/badge/GPU-NVIDIA_CUDA-76B900?style=for-the-badge&logo=nvidia)
![Yandex Cloud](https://img.shields.io/badge/Yandex_Cloud-AI_Powered-red?style=for-the-badge&logo=yandex)

**Video-To-Text Scripts** — это профессиональный программный комплекс, предназначенный для трансформации медиа-контента в структурированные аналитические данные. Система идеально подходит для обработки медицинских конференций, учебных лекций и экспертных выступлений, обеспечивая полный цикл: от извлечения аудио до формирования финального медицинского конспекта.

Система работает локально для обеспечения приватности данных (распознавание речи) и использует нейросети Yandex Cloud для интеллектуальной обработки текста.

---

## 🚀 Key Features

### 🎞️ Media Processing Engine
* **High-Fidelity Audio Extraction:** Модуль `audio_extractor.py` преобразует любые видео-контейнеры (MP4, MKV, AVI) в оптимизированный аудиопоток WAV (16kHz, Mono). Это критически важно для минимизации галлюцинаций нейросетей при транскрибации.
* **FFmpeg Integration:** Использует мощные алгоритмы сжатия и фильтрации для подготовки чистого звука без потерь качества речи.

### 🎙️ AI Transcription (Local & Secure)
* **Faster-Whisper Implementation:** Модуль `whisper_transcriptor.py` использует современную реализацию OpenAI Whisper. В отличие от стандартных библиотек, `faster-whisper` обеспечивает 4-кратное ускорение обработки.
* **GPU Acceleration:** Полная поддержка NVIDIA CUDA. На видеокартах уровня GTX 1060 Ti и выше распознавание происходит в несколько раз быстрее реального времени записи.
* **Privacy First:** Весь процесс перевода речи в текст происходит локально на вашем сервере. Медицинские данные и экспертные обсуждения не покидают периметр вашей сети.

### 🧠 Intelligence & Summarization
* **YandexGPT Integration:** Модуль `yandex_summarizer.py` автоматически исправляет опечатки распознавания (например, корректирует специфические термины: "КТР", "ТВП", "хориальность").
* **Smart TL;DR:** Система анализирует огромные объемы текста (100к+ знаков), выделяет ключевые тезисы и формирует структурированный конспект с заголовками и логическими блоками.
* **On-the-fly Configuration:** Интуитивный UI позволяет вводить Folder ID и API Key прямо в окне программы, обеспечивая мгновенный доступ к облачным нейросетям Yandex Cloud.

---

## 🛠️ Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Grishin-Semyon/Video-To-Text-scripts.git](https://github.com/Grishin-Semyon/Video-To-Text-scripts.git)
    cd Video-To-Text-scripts
    ```

2.  **Set up Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Python Dependencies:**
    ```bash
    pip install PyQt6 moviepy faster-whisper requests torch
    ```

4.  **CUDA Support (Optional but Recommended):**
    Убедитесь, что у вас установлены драйверы NVIDIA и библиотека `cuDNN` для корректной работы Whisper на видеокарте.

---

## 📖 Operational Workflow

Для получения максимального качества придерживайтесь следующего порядка:

1.  **Extract:** Запустите `audio_extractor.py`, выберите видео.
2.  **Transcribe:** Полученный файл `.wav` загрузите в `whisper_transcriptor.py`. Дождитесь появления `.txt`.
3.  **Summarize:** Откройте `yandex_summarizer.py`, введите ваши учетные данные Yandex Cloud и получите финальный результат в файле `_yandex_ready.txt`.

---

## ⚙️ Requirements

* **Python:** 3.10 or higher
* **Hardware:** NVIDIA GPU with 6GB+ VRAM (GTX 1060 or newer)
* **Connectivity:** Требуется доступ к сети для обращения к API Yandex Cloud (только на этапе саммаризации).

---
*Developed for medical professionals and IT directors to streamline knowledge management.*