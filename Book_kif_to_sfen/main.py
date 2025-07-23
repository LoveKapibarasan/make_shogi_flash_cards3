import sys
import os
import shogi
import shogi.KIF
from PyQt6.QtGui import QIcon

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QLabel, QTextEdit, QMessageBox
)


def kif_to_sfen(kif_string):
    try:
        kif = shogi.KIF.Parser.parse_str(kif_string)[0]
        sfen_string = "startpos moves "
        for move in kif['moves']:
            sfen_string += move + " "
        return sfen_string.strip()
    except Exception as e:
        return f"# Error parsing KIF: {e}"


class KifToSfenConverter(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("KIF to SFEN Converter")
        self.setWindowIcon(QIcon("../ico/Book.ico"))
        self.setGeometry(100, 100, 600, 300)

        self.input_folder = ""
        self.output_file = ""

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.status_box = QTextEdit()
        self.status_box.setReadOnly(True)
        layout.addWidget(self.status_box)

        self.btn_select_folder = QPushButton("Select Input Folder (KIF files)")
        self.btn_select_folder.clicked.connect(self.select_input_folder)
        layout.addWidget(self.btn_select_folder)

        self.btn_select_output = QPushButton("Select Output File (.sfen)")
        self.btn_select_output.clicked.connect(self.select_output_file)
        layout.addWidget(self.btn_select_output)

        self.btn_run = QPushButton("Convert")
        self.btn_run.clicked.connect(self.run_conversion)
        layout.addWidget(self.btn_run)

    def select_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select KIF Folder")
        if folder:
            self.input_folder = folder
            self.status_box.append(f"Selected input folder: {folder}")

    def select_output_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Select Output File", "", "Sfen Files (*.sfen)")
        if file_path:
            self.output_file = file_path
            self.status_box.append(f"Selected output file: {file_path}")

    def run_conversion(self):
        if not self.input_folder or not self.output_file:
            QMessageBox.warning(self, "Warning", "Please select both input folder and output file.")
            return

        try:
            self.status_box.append("Starting conversion...")
            count = 0
            with open(self.output_file, "w", encoding="utf-8") as out_f:
                for filename in os.listdir(self.input_folder):
                    if not filename.lower().endswith(".kif"):
                        continue
                    file_path = os.path.join(self.input_folder, filename)
                    with open(file_path, encoding="utf-8") as f:
                        kif_string = f.read()
                        sfen_string = kif_to_sfen(kif_string)
                        out_f.write(sfen_string + "\n")
                        self.status_box.append(f"Processed: {filename}")
                        count += 1

            self.status_box.append(f"Conversion complete. {count} files processed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KifToSfenConverter()
    window.show()
    sys.exit(app.exec())
