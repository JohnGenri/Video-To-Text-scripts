import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QWidget, QFileDialog, QLabel, QProgressBar, QMessageBox, QTextEdit)
from PyQt6.QtCore import QThread, pyqtSignal
from faster_whisper import WhisperModel

class TranscriptionThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress_update = pyqtSignal(str)

    def __init__(self, audio_path):
        super().__init__()
        self.audio_path = audio_path

    def run(self):
        try:
            # Инициализация модели
            # 'base' - быстро и неплохо. Если сервер мощный, замени на 'small' или 'medium'
            model_size = "base"
            
            # device="cpu" для сервера без мощной видеокарты NVIDIA
            # compute_type="int8" позволяет потреблять меньше оперативной памяти
            model = WhisperModel(model_size, device="cpu", compute_type="int8")

            self.progress_update.emit("Модель загружена. Начинаю распознавание...")
            
            segments, info = model.transcribe(self.audio_path, beam_size=5, language="ru")

            full_text = []
            for segment in segments:
                # Собираем текст по кусочкам
                full_text.append(segment.text.strip())
                self.progress_update.emit(f"Распознано: {segment.text[:50]}...")

            # Формируем путь к текстовому файлу
            audio_path_obj = Path(self.audio_path)
            txt_path = str(audio_path_obj.with_suffix('.txt'))

            # Сохраняем результат
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write("\n".join(full_text))

            self.finished.emit(txt_path)
        except Exception as e:
            self.error.emit(str(e))

class RecognitionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("STT Recognizer by Semyon")
        self.setFixedSize(500, 400)

        layout = QVBoxLayout()

        self.label = QLabel("Выберите аудиофайл (.wav или .mp3):")
        layout.addWidget(self.label)

        self.btn_open = QPushButton("ВЫБРАТЬ АУДИО И НАЧАТЬ ТЕКСТ")
        self.btn_open.setStyleSheet("height: 50px; font-weight: bold; background-color: #d1ffd1;")
        self.btn_open.clicked.connect(self.select_file)
        layout.addWidget(self.btn_open)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Здесь будет отображаться процесс...")
        layout.addWidget(self.log_output)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        layout.addWidget(self.progress)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def select_file(self):
        file_filter = "Audio files (*.wav *.mp3 *.m4a *.flac)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть аудио", "", file_filter)
        
        if file_path:
            self.start_processing(file_path)

    def start_processing(self, path):
        self.btn_open.setEnabled(False)
        self.log_output.clear()
        self.log_output.append(f"Файл: {os.path.basename(path)}")
        self.progress.show()

        self.thread = TranscriptionThread(path)
        self.thread.finished.connect(self.on_success)
        self.thread.error.connect(self.on_error)
        self.thread.progress_update.connect(lambda text: self.log_output.append(text))
        self.thread.start()

    def on_success(self, txt_path):
        self.btn_open.setEnabled(True)
        self.progress.hide()
        QMessageBox.information(self, "Успех", f"Текст сохранен в:\n{txt_path}")

    def on_error(self, message):
        self.btn_open.setEnabled(True)
        self.progress.hide()
        QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {message}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RecognitionApp()
    window.show()
    sys.exit(app.exec())