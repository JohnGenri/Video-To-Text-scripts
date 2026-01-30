import sys
import os
import requests
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QWidget, QFileDialog, QLabel, QProgressBar, QMessageBox, 
                             QTextEdit, QLineEdit)
from PyQt6.QtCore import QThread, pyqtSignal

# Класс для работы с Yandex Cloud в фоновом режиме
class YandexGPTWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress_update = pyqtSignal(str)

    def __init__(self, input_path, system_prompt, api_key, folder_id, model_uri):
        super().__init__()
        self.input_path = input_path
        self.system_prompt = system_prompt
        self.api_key = api_key
        self.folder_id = folder_id
        self.model_uri = model_uri
        self.url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    def run(self):
        try:
            input_file = Path(self.input_path)
            output_file = input_file.with_name(input_file.stem + "_yandex_ready.txt")
            
            # Читаем и очищаем исходный текст
            with open(input_file, "r", encoding="utf-8") as f:
                text = f.read().strip()

            if not text:
                raise Exception("Файл пуст!")

            # Нарезаем текст на чанки по 8000 символов (безопасный лимит для Яндекса)
            chunk_size = 8000 
            raw_chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
            
            # Удаляем пустые блоки и лишние пробелы в чанках
            chunks = [c.strip() for c in raw_chunks if c.strip()]
            
            self.progress_update.emit(f"Текст разбит на {len(chunks)} частей. Начинаю обработку...")

            headers = {
                "Authorization": f"Api-Key {self.api_key}",
                "x-folder-id": self.folder_id
            }

            with open(output_file, "w", encoding="utf-8") as out_f:
                for i, chunk in enumerate(chunks):
                    self.progress_update.emit(f"Отправка блока {i+1} из {len(chunks)}...")
                    
                    # Формируем Payload согласно документации YandexGPT RC
                    payload = {
                        "modelUri": self.model_uri,
                        "completionOptions": {
                            "stream": False, 
                            "temperature": 0.3, 
                            "maxTokens": "2000"
                        },
                        "messages": [
                            {"role": "system", "text": self.system_prompt},
                            {"role": "user", "text": chunk}
                        ]
                    }
                    
                    response = requests.post(self.url, headers=headers, json=payload, timeout=90)
                    
                    if response.status_code == 200:
                        # Извлекаем текст ответа
                        result = response.json()['result']['alternatives'][0]['message']['text']
                        out_f.write(result + "\n\n")
                        out_f.flush() # Сохраняем сразу, чтобы не потерять данные
                    else:
                        raise Exception(f"Ошибка Yandex ({response.status_code}): {response.text}")

            self.finished.emit(str(output_file))
        except Exception as e:
            self.error.emit(str(e))

class YandexApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("YandexGPT Professional Summarizer")
        self.setFixedSize(600, 600)

        layout = QVBoxLayout()

        # Поля настроек (уже заполнены твоими данными)
        layout.addWidget(QLabel("API Key:"))
        self.api_key_input = QLineEdit("Your Key")
        layout.addWidget(self.api_key_input)

        layout.addWidget(QLabel("Folder ID:"))
        self.folder_id_input = QLineEdit("Folder")
        layout.addWidget(self.folder_id_input)

        layout.addWidget(QLabel("Model URI:"))
        self.model_uri_input = QLineEdit("Yandex GPT Model")
        layout.addWidget(self.model_uri_input)

        layout.addWidget(QLabel("Инструкция (System Prompt):"))
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlainText(
            "Ты — профессиональный  редактор. Твоя задача — пересказать суть лекции. "
            "Исправь опечатки (бейминстей -> беременности), удали технический мусор субтитров. "
            "Сделай текст структурированным: используй заголовки и логические блоки."
        )
        layout.addWidget(self.prompt_input)

        layout.addWidget(QLabel("Лог работы:"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: #fafafa;")
        layout.addWidget(self.log_output)

        self.btn_start = QPushButton("ВЫБРАТЬ ФАЙЛ И ОБРАБОТАТЬ")
        self.btn_start.setStyleSheet("height: 50px; font-weight: bold; background-color: #ffeba7;")
        self.btn_start.clicked.connect(self.select_file)
        layout.addWidget(self.btn_start)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        layout.addWidget(self.progress)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл с текстом", "", "Text files (*.txt)")
        if file_path:
            self.start_processing(file_path)

    def start_processing(self, path):
        self.btn_start.setEnabled(False)
        self.progress.show()
        self.log_output.append(f"Файл: {os.path.basename(path)}")
        
        # Запускаем поток
        self.thread = YandexGPTWorker(
            path, 
            self.prompt_input.toPlainText(), 
            self.api_key_input.text(), 
            self.folder_id_input.text(),
            self.model_uri_input.text()
        )
        self.thread.finished.connect(self.on_success)
        self.thread.error.connect(self.on_error)
        self.thread.progress_update.connect(lambda m: self.log_output.append(m))
        self.thread.start()

    def on_success(self, output_path):
        self.btn_start.setEnabled(True)
        self.progress.hide()
        QMessageBox.information(self, "Готово", f"Обработка завершена успешно!\nРезультат: {output_path}")

    def on_error(self, message):
        self.btn_start.setEnabled(True)
        self.progress.hide()
        QMessageBox.critical(self, "Ошибка API", f"Яндекс вернул ошибку:\n{message}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YandexApp()
    window.show()
    sys.exit(app.exec())