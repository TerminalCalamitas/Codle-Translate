from gui.Codle_Translate import Ui_MainWindow
import sys
from PySide6.QtWidgets import QApplication, QMainWindow


class TranslationUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Connect the button click to your function
        self.ui.RunTranslation.clicked.connect(self.translate_text)

    def translate_text(self):
        # Get text from input box
        input_text = (
            self.ui.InputBox.toPlainText()
        )  # or .toPlainText() if it's a QTextEdit
        # Set it to output box
        self.ui.OutputBox.setText(input_text)  # or .setPlainText() if it's a QTextEdit


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TranslationUI()
    window.show()
    sys.exit(app.exec())
