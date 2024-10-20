import sys
import os
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import webbrowser
#whatman was here
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor(250, 261, 250))

        block = self.code_editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.code_editor.blockBoundingGeometry(block).translated(self.code_editor.contentOffset()).top())
        bottom = top + int(self.code_editor.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(Qt.black)
                painter.drawText(0, top, self.width(), self.code_editor.fontMetrics().height(), Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.code_editor.blockBoundingRect(block).height())
            block_number += 1

    def update_width(self):
        return self.fontMetrics().width(str(max(1, self.code_editor.blockCount()))) + 10
#im still here btw whatman
class CodeEditor(QPlainTextEdit):
    def __init__(self, *args):
        super().__init__(*args)
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def line_number_area_width(self):
        return self.line_number_area.update_width()

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        rect = self.contentsRect()
        self.line_number_area.setGeometry(QRect(rect.left(), rect.top(), self.line_number_area_width(), rect.height()))

    def highlight_current_line(self):
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            
        self.setExtraSelections(extra_selections)
#konstant only fr
class LuauSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(LuauSyntaxHighlighter, self).__init__(parent)
        
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#00FF00"))
        
        self.function_format = QTextCharFormat()
        self.function_format.setForeground(QColor("#FFD700"))
        
        self.variable_format = QTextCharFormat()
        self.variable_format.setForeground(QColor("#FF4500"))
        
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#A9A9A9"))
        
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#00BFFF"))
        
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#FF1493"))
        
        self.boolean_format = QTextCharFormat()
        self.boolean_format.setForeground(QColor("#FFA500"))
        
        self.operator_format = QTextCharFormat()
        self.operator_format.setForeground(QColor("#FF69B4"))

        self.keywords = ["local", "function", "end", "return", "if", "then", "else", "elseif", "for", "in", "do", "while", "repeat", "until", "true", "false", "nil", "and", "or", "not", "break", "continue", "goto"]
        self.functions = ["print", "pairs", "ipairs", "next", "type", "assert", "error", "require", "tonumber", "tostring", "math", "table", "string"]
        self.variables = ["self", "_G", "_ENV"]
        self.booleans = ["true", "false"]
        self.operators = ["+", "-", "*", "/", "=", "==", "<", ">", "<=", ">=", "~=", ".."]

    def highlightBlock(self, text):
        for keyword in self.keywords:
            index = text.find(keyword)
            while index >= 0:
                length = len(keyword)
                self.setFormat(index, length, self.keyword_format)
                index = text.find(keyword, index + length)
        
        for function in self.functions:
            index = text.find(function)
            while index >= 0:
                length = len(function)
                self.setFormat(index, length, self.function_format)
                index = text.find(function, index + length)
        
        for variable in self.variables:
            index = text.find(variable)
            while index >= 0:
                length = len(variable)
                self.setFormat(index, length, self.variable_format)
                index = text.find(variable, index + length)

        for boolean in self.booleans:
            index = text.find(boolean)
            while index >= 0:
                length = len(boolean)
                self.setFormat(index, length, self.boolean_format)
                index = text.find(boolean, index + length)

        for operator in self.operators:
            index = text.find(operator)
            while index >= 0:
                length = len(operator)
                self.setFormat(index, length, self.operator_format)
                index = text.find(operator, index + length)

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
        self.text_edit_input = CodeEditor(self)
        self.text_edit_input.setFont(QFont("Courier", 10))
        self.highlighter = LuauSyntaxHighlighter(self.text_edit_input.document())
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
        self.text_edit_output = CodeEditor(self)
        self.text_edit_output.setReadOnly(True)
        self.text_edit_output.setFont(QFont("Courier", 10))
        self.output_highlighter = LuauSyntaxHighlighter(self.text_edit_output.document())
        layout.addWidget(QLabel("Output:"))
        layout.addWidget(self.text_edit_output)
        self.save_output_button = QPushButton("Save Output", self)
        self.save_output_button.clicked.connect(self.save_output)
        layout.addWidget(self.save_output_button)
    def update_line_numbers(self):
        self.line_number_area.update_line_numbers()
    def clear_editor(self):
        self.text_edit_input.clear()

    def open_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Your file.", "", "Text Files (*.txt);;Lua Files (*.lua);;Luau Files (*.luau);;All Files (*)", options=options)
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
