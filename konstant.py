import sys
import os
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import webbrowser

class LineNumberArea(QPlainTextEdit):
    def __init__(self, editor):
        super().__init__()
        self.code_editor = editor
        self.setReadOnly(True)

    def update_line_numbers(self):
        self.setPlainText("\n".join(str(i + 1) for i in range(self.code_editor.blockCount())))

class LuauSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(LuauSyntaxHighlighter, self).__init__(parent)
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#89CFF0"))
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#A9A9A9"))
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#B0E0E6"))
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#4682B4"))
        self.keywords = ["local", "function", "end", "return", "if", "then", "else", "elseif", "for", "in", "do", "while", "repeat", "until", "true", "false", "nil", "and", "or", "not", "break", "continue", "goto"]

    def highlightBlock(self, text):
        for keyword in self.keywords:
            index = text.find(keyword)
            while index >= 0:
                length = len(keyword)
                self.setFormat(index, length, self.keyword_format)
                index = text.find(keyword, index + length)

        if "--" in text:
            comment_index = text.find("--")
            self.setFormat(comment_index, len(text) - comment_index, self.comment_format)

        in_string = False
        for i, char in enumerate(text):
            if char == '"' or char == "'":
                if not in_string:
                    start = i
                    in_string = True
                else:
                    self.setFormat(start, i - start + 1, self.string_format)
                    in_string = False

        for word in text.split():
            if word.isdigit():
                index = text.find(word)
                self.setFormat(index, len(word), self.number_format)

class KonstantApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Konstant")
        self.setGeometry(100, 100, 800, 600)
        icon_path = os.path.join(os.path.dirname(__file__), 'icons', 'konstant.png')
        self.setWindowIcon(QIcon(icon_path))
        version = self.fetch_version()
        self.setWindowTitle(f"Konstant {version}")
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        self.text_edit_input = QPlainTextEdit(self)
        self.text_edit_input.setFont(QFont("Courier", 10))
        self.highlighter = LuauSyntaxHighlighter(self.text_edit_input.document())
        self.line_number_area = LineNumberArea(self.text_edit_input)
        layout.addWidget(QLabel("Input:"))
        layout.addWidget(self.text_edit_input)
        buttons_layout = QHBoxLayout()
        self.open_button = QPushButton("Open", self)
        self.open_button.clicked.connect(self.open_file)
        buttons_layout.addWidget(self.open_button)
        self.clear_button = QPushButton("Clear", self)
        self.clear_button.clicked.connect(self.clear_editor)
        buttons_layout.addWidget(self.clear_button)
        self.save_input_button = QPushButton("Save Input", self)
        self.save_input_button.clicked.connect(self.save_input)
        buttons_layout.addWidget(self.save_input_button)
        self.discord_button = QPushButton("Discord", self)
        self.discord_button.clicked.connect(self.open_discord)
        buttons_layout.addWidget(self.discord_button)
        self.decompile_button = QPushButton("Decompile", self)
        self.decompile_button.clicked.connect(self.decompile_script)
        buttons_layout.addWidget(self.decompile_button)
        layout.addLayout(buttons_layout)
        self.text_edit_output = QPlainTextEdit(self)
        self.text_edit_output.setReadOnly(True)
        layout.addWidget(QLabel("Output:"))
        layout.addWidget(self.text_edit_output)
        self.save_output_button = QPushButton("Save Output", self)
        self.save_output_button.clicked.connect(self.save_output)
        layout.addWidget(self.save_output_button)
        self.text_edit_input.blockCountChanged.connect(self.update_line_numbers)
        self.text_edit_input.updateRequest.connect(self.update_line_numbers)
    
    def update_line_numbers(self):
        self.line_number_area.update_line_numbers()

    def clear_editor(self):
        self.text_edit_input.clear()

    def open_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Your file.", "", "Lua Files (*.lua);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'r') as file:
                file_content = file.read()
                self.text_edit_input.setPlainText(file_content)

    def save_input(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Input", "", "Lua Files (*.lua);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'w') as file:
                file.write(self.text_edit_input.toPlainText())

    def save_output(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Output", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'w') as file:
                file.write(self.text_edit_output.toPlainText())

    def open_discord(self):
        discord_url = "https://discord.gg/79aMKGcvH5"
        webbrowser.open(discord_url)

    def decompile_script(self):
        input_script = self.text_edit_input.toPlainText()

        if not input_script:
            self.text_edit_output.setPlainText("Error: Input cannot be empty!")
            return

        try:
            decompiled_code = self.decompile_api_call(input_script)
            self.text_edit_output.setPlainText(decompiled_code)
        except Exception as e:
            self.text_edit_output.setPlainText(f"Error during decompilation: {e}")
    
    def decompile_api_call(self, script_code):
        API = "http://api.plusgiant5.com/konstant/decompile"
        response = requests.post(API, data=script_code, headers={"Content-Type": "text/plain"})
        if response.status_code == 200:
            return response.text
        else:
            return f"API Error: {response.status_code}\n{response.text}"

    def fetch_version(self):
        version_url = "https://raw.githubusercontent.com/Whatmanhere/KonstantApp/refs/heads/main/version.txt"
        try:
            response = requests.get(version_url)
            if response.status_code == 200:
                return response.text.strip()
            else:
                return "Unknown"
        except Exception:
            return "Unknown"

def main():
    app = QApplication(sys.argv)
    window = KonstantApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
