from PyQt5.QtWidgets import (
    QLabel, QListWidget, QProgressBar, QApplication,
    QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLineEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import time
import sys

tokenizer = AutoTokenizer.from_pretrained('meta-llama/Llama-3.1-8B-Instruct')
model = AutoModelForCausalLM.from_pretrained('meta-llama/Llama-3.1-8B-Instruct')
generator  = pipeline('text-generation', model=model, tokenizer=tokenizer)

history = []
def generate_response(prompt):
    global history
    response = generator(prompt, max_length=100)
    answer = response[0]['generated_text']
    history.append({'role': 'user', 'content': prompt})
    history.append({'role': 'assistant', 'content': answer})
    return answer

# Генерация ответа 
class WorkerThread(QThread):
    update_progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt
    
    def run(self):
        for i in range(10):
            time.sleep(0.1)
            self.update_progress.emit(i + 1)
        answer = generate_response(self.prompt)
        self.finished.emit(answer)

# Окно ассистента
class AssistantWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('AI-ассистент')
        self.setStyleSheet('background-color: lightblue;')
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # История промтов
        layout.addWidget(QLabel('История сообщений:'))
        self.history_text = QListWidget()
        layout.addWidget(self.history_text)

        # Запрос
        layout.addWidget(QLabel('Введите запрос:'))
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        input_layout.addWidget(self.input_field)
        self.send_button = QPushButton('Отправить')
        self.send_button.clicked.connect(self.handle_send)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(10)
        layout.addWidget(self.progress_bar)
        
        # Кнопка выхода
        self.exit_button = QPushButton('Выйти')
        self.exit_button.clicked.connect(self.close)
        layout.addWidget(self.exit_button)
        
        self.setLayout(layout)

    def handle_send(self):
        prompt = self.input_field.text()
        if not prompt: return
        self.thread = WorkerThread(prompt)
        self.thread.update_progress.connect(self.progress_bar.setValue)
        self.thread.finished.connect(self.display_response)
        self.thread.start()

    def display_response(self, answer):
        self.update_history_display()
        self.input_field.clear()
        self.progress_bar.setValue(0)
    
    def update_history_display(self):
        self.history_text.clear()
        for entry in history:
            role = entry['role']
            content = entry['content']
            self.history_text.addItem(f'{role}:\n{content}')
    
app = QApplication(sys.argv)
window = AssistantWindow()
window.show()
sys.exit(app.exec_())

        


       