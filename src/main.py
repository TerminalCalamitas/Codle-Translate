from gui.Codle_Translate import Ui_MainWindow
import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from src.translator import translate


def main():
    app = QApplication(sys.argv)
    window = TranslationUI()
    window.show()
    sys.exit(app.exec())


class TranslationUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Connect the button click to your function
        self.ui.RunTranslation.clicked.connect(self.translate_text)

        # Load example code on button click
        self.ui.LoadExample.clicked.connect(self.load_language_from_file)

    def load_language_from_file(self):
        language_name = self.ui.InputLanguage.currentText()
        filename = f"{language_name}.code"

        try:
            with open(filename, "r") as f:
                text = f.read()
            self.ui.InputBox.setPlainText(text)
        except FileNotFoundError:
            self.ui.InputBox.setPlainText(f"File not found: {filename}")
        except Exception as e:
            self.ui.InputBox.setPlainText(f"Error loading file: {e}")

    def translate_text(self):
        # Get text from input box
        input_language = self.ui.InputLanguage.currentText()
        output_language = self.ui.OutputLanguage.currentText()
        code = self.ui.InputBox.toPlainText()

        if input_language == output_language:
            self.ui.OutputBox.setText(code)
            return

        print("Calling translate")
        translated_code = translate(input_language, output_language, code)
        print("translate finished")

        # Set it to output box
        self.ui.OutputBox.setText(translated_code)


if __name__ == "__main__":
    main()
