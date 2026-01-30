import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QWidget, QFileDialog, QLabel, QProgressBar, QMessageBox, QComboBox)
from PyQt6.QtCore import QThread, pyqtSignal

# Решаем проблему с разными версиями moviepy (v1.0.3 vs v2.0+)
try:
    try:
        from moviepy.editor import VideoFileClip
    except ImportError:
        from moviepy import VideoFileClip
except ImportError:
    print("Ошибка: Библиотека moviepy не найдена. Установите её: pip install moviepy")

class AudioExtractorThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, video_path, format_ext):
        super().__init__()
        self.video_path = video_path
        self.format_ext = format_ext

    def run(self):
        video = None
        try:
            # Загружаем видео
            video = VideoFileClip(self.video_path)
            video_path_obj = Path(self.video_path)
            audio_path = str(video_path_obj.with_suffix(self.format_ext))
            
            if not video.audio:
                self.error.emit("В выбранном видео отсутствует аудиодорожка.")
                return

            # Настройки в зависимости от формата
            if self.format_ext == ".wav":
                # WAV 16kHz Mono — идеал для распознавания текста (STT)
                video.audio.write_audiofile(
                    audio_path, 
                    fps=16000, 
                    nbytes=2, 
                    codec='pcm_s16le', 
                    ffmpeg_params=["-ac", "1"], 
                    logger=None
                )
            else:
                # Обычный MP3 для экономии места
                video.audio.write_audiofile(audio_path, logger=None)
            
            self.finished.emit(audio_path)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            if video:
                video.close()
                # В новых версиях moviepy может потребоваться явное удаление объекта
                if hasattr(video, 'reader') and video.reader:
                    video.reader.close()
                if hasattr(video, 'audio') and video.audio and hasattr(video.audio, 'reader') and video.audio.reader:
                    video.audio.reader.close_all()

class VideoToAudioApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Extractor by Semyon v1.0")
        self.setFixedSize(450, 250)

        layout = QVBoxLayout()

        # Выбор формата
        self.label_fmt = QLabel("1. Выберите формат для будущего текста (STT):")
        layout.addWidget(self.label_fmt)

        self.format_chooser = QComboBox()
        self.format_chooser.addItems([".wav (Рекомендуется для распознавания)", ".mp3 (Сжатый файл)"])
        layout.addWidget(self.format_chooser)

        # Кнопка действия
        self.info_label = QLabel("2. Выберите видеофайл:")
        layout.addWidget(self.info_label)

        self.btn_open = QPushButton("ОТКРЫТЬ ВИДЕО И ИЗВЛЕЧЬ ЗВУК")
        self.btn_open.setStyleSheet("height: 50px; font-weight: bold; background-color: #e1e1e1;")
        self.btn_open.clicked.connect(self.select_file)
        layout.addWidget(self.btn_open)

        # Прогресс и статус
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        layout.addWidget(self.progress)

        self.status_label = QLabel("Статус: Ожидание")
        layout.addWidget(self.status_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def select_file(self):
        file_filter = "Video files (*.mp4 *.mkv *.avi *.mov *.wmv)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите видео", "", file_filter)
        
        if file_path:
            selected_text = self.format_chooser.currentText()
            ext = ".wav" if ".wav" in selected_text else ".mp3"
            self.start_processing(file_path, ext)

    def start_processing(self, path, ext):
        self.btn_open.setEnabled(False)
        self.format_chooser.setEnabled(False)
        self.status_label.setText(f"Статус: Обработка {os.path.basename(path)}...")
        self.progress.show()

        self.thread = AudioExtractorThread(path, ext)
        self.thread.finished.connect(self.on_success)
        self.thread.error.connect(self.on_error)
        self.thread.start()

    def on_success(self, audio_path):
        self.reset_ui()
        self.status_label.setText("Статус: Успешно завершено")
        QMessageBox.information(self, "Готово", f"Аудиофайл создан рядом с видео:\n{audio_path}")

    def on_error(self, message):
        self.reset_ui()
        self.status_label.setText("Статус: Ошибка")
        QMessageBox.critical(self, "Ошибка", f"Произошла ошибка:\n{message}")

    def reset_ui(self):
        self.btn_open.setEnabled(True)
        self.format_chooser.setEnabled(True)
        self.progress.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoToAudioApp()
    window.show()
    sys.exit(app.exec())