import logging
from PyQt6.QtWidgets import QTextEdit, QFileDialog
from PyQt6.QtCore import QFileInfo, QByteArray
from PyQt6.QtGui import QTextDocument, QTextDocumentWriter
from PyQt6.QtPrintSupport import QPrinter

logger = logging.getLogger(__name__)


class TextEditSaver:
    """
    A class that handles saving the contents of a QTextEdit widget to a file.

    Attributes:
        current_text_edit (QTextEdit): The current QTextEdit widget to save.

    Methods:
        set_current_text_edit(text_edit): Sets the current QTextEdit widget to save.
        save_current_text(): Saves the current text in the QTextEdit widget to a file.

    """

    def __init__(self):
        self.current_text_edit = None

    def set_current_text_edit(self, text_edit):
        """
        Sets the current QTextEdit widget to save.

        Args:
            text_edit (QTextEdit): The QTextEdit widget to set as the current widget.

        """
        try:
            if isinstance(text_edit, QTextEdit):
                self.current_text_edit = text_edit
        except Exception as e:
            logger.error(f"Error in {__name__} {e}", exc_info=True)

    def save_current_text(self) -> None:
        """
        Save the current text in the text editor to a file.
        This function opens a dialog to select the file format and location for saving the text.
        It then saves the text in the chosen format and logs the file saving action.
        If an error occurs during the file saving process, it logs the error.

        """
        try:
            if self.current_text_edit is None:
                return

            options = "PDF Files (*.pdf);;Text Files (*.txt);;Markdown Files (*.md);;HTML Files (*.html)"
            filename, _ = QFileDialog.getSaveFileName(None, "Save File", "", options)

            if filename:
                file_extension = QFileInfo(filename).suffix().lower()

                if file_extension not in ["txt", "md", "html", "pdf"]:
                    filename += ".txt"  # Default to .txt if no valid extension is provided

                if file_extension == "pdf":
                    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
                    printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
                    printer.setOutputFileName(filename)
                    self.current_text_edit.document().print(printer)
                else:
                    with open(filename, 'w', encoding='utf-8') as file:
                        if file_extension == "html":
                            file.write(self.current_text_edit.toHtml())
                        elif file_extension == "txt":
                            file.write(self.current_text_edit.toPlainText())
                        elif file_extension == "md":
                            file.write(self.current_text_edit.toMarkdown())
                logger.info(f"Saved file: {filename}, Extension: {file_extension}")
            else:
                logger.info("File not saved")
        except Exception as e:
            logger.error(f"Error in {__name__} {e}", exc_info=True)
