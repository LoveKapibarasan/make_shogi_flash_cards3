import sys
import subprocess
import os
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QLabel, QTextEdit, QMessageBox
)

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now you can import from sibling dir_b

from Engines.engines_management import initialize_engine, read_output 





class ShogiEvaluator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shogi Evaluator")
        self.setWindowIcon(QIcon("../ico/Book2.ico"))
        self.setGeometry(100, 100, 500, 300)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Select a SFEN input file:")
        self.layout.addWidget(self.label)

        self.textbox = QTextEdit()
        self.textbox.setReadOnly(True)
        self.layout.addWidget(self.textbox)

        self.btn_select = QPushButton("Select File")
        self.btn_select.clicked.connect(self.select_file)
        self.layout.addWidget(self.btn_select)

        self.btn_run = QPushButton("Run Evaluation")
        self.btn_run.clicked.connect(self.run_evaluation)
        self.layout.addWidget(self.btn_run)

        self.btn_output = QPushButton("Select Output File")
        self.btn_output.clicked.connect(self.select_output_file)
        self.layout.addWidget(self.btn_output)

        self.input_file = ""
        self.output_file = ""

    def select_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select SFEN File", "", "Text Files (*.txt);;All Files (*)")
        if file_name:
            self.input_file = file_name
            self.textbox.append(f"Selected: {file_name}")
    def select_output_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Select Output File", "", "Text Files (*.txt)")
        if file_name:
            self.output_file = file_name
            self.textbox.append(f"Output File: {file_name}")

    def run_evaluation(self):
        if not self.input_file:
            QMessageBox.warning(self, "Warning", "No file selected.")
            return
        try:
            self.textbox.append("Starting engine evaluation...")
            run_engine(self.input_file, self.output_file)
            self.textbox.append("Evaluation complete.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

def run_engine(INPUT_FILE, OUTPUT_FILE):
    with open(INPUT_FILE, encoding="utf-8") as f:
        sfen_lines = f.read().splitlines()

    proc = initialize_engine()

    line_list = []
    index = 0
    while index < len(sfen_lines):
        if sfen_lines[index].startswith("<start>"):
            index += 1
            break
        line_list.append(sfen_lines[index])
        index += 1

    for i in range(index, len(sfen_lines)):
        move_list = []
        command = "position startpos moves"
        counter = 0
        for move in sfen_lines[i].split():
            if counter >= 60:
                break
            if "startpos" in move or "moves" in move:
                move_list.append(move)
                continue
            command = command + " " + move
            if counter > 20:
                cp, nodes, pv = read_output(proc, command)
                if not -200 < cp < 200:
                    break
            move_list.append(move)
            counter += 1
        line_list.append(" ".join(move_list))

    with open(INPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(line_list))
        f.write("\n<start>\n")
        f.write("\n".join(sfen_lines[i+1:]))
        f.write("\n")


    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write("\n".join(line_list))




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShogiEvaluator()
    window.show()
    sys.exit(app.exec())
