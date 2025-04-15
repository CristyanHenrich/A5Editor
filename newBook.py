import os
import json
from datetime import datetime
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QObject
import editor

class NewBookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Novo Livro")

        loader = QUiLoader()
        ui_file = QFile("newBook.ui")
        if not ui_file.open(QFile.ReadOnly):
            print(f"Erro ao abrir o arquivo newBook.ui: {ui_file.errorString()}")
            return

        self.ui = loader.load(ui_file)
        ui_file.close()

        if not self.ui:
            print("Erro ao carregar a interface do usuário")
            return

        from PySide6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(self)
        layout.addWidget(self.ui)
        self.setLayout(layout)

        self.selected_path = ""
        self.cover_path = ""

        if hasattr(self.ui, "btnSelectPath"):
            self.ui.btnSelectPath.clicked.connect(self.choose_path)
        else:
            print("Botão 'btnSelectPath' não encontrado!")

        if hasattr(self.ui, "btnSelectCover"):
            self.ui.btnSelectCover.clicked.connect(self.choose_cover)
        else:
            print("Botão 'btnSelectCover' não encontrado!")

        if hasattr(self.ui, "btnSave"):
            self.ui.btnSave.clicked.connect(self.save_book)
        else:
            print("Botão 'btnSave' não encontrado!")

    def choose_path(self):
        path = QFileDialog.getExistingDirectory(self, "Escolher Pasta")
        if path and hasattr(self.ui, "bookPath"):
            self.selected_path = path
            self.ui.bookPath.setText(path)

    def choose_cover(self):
        file, _ = QFileDialog.getOpenFileName(self, "Escolher Capa", "", "Imagens (*.png *.jpg *.jpeg)")
        if file and hasattr(self.ui, "coverPath"):
            self.cover_path = file
            self.ui.coverPath.setText(file)

    def save_book(self):
        if not hasattr(self.ui, "bookName"):
            print("Campo 'bookName' não encontrado!")
            return False

        nome = self.ui.bookName.text().strip()
        if not nome or not self.selected_path:
            QMessageBox.warning(self, "Campos obrigatórios",
                               "Preencha o nome do livro e escolha um local para salvar.")
            return False

        book_dir = os.path.join(self.selected_path, nome)
        os.makedirs(book_dir, exist_ok=True)

        html_path = os.path.join(book_dir, f"{nome}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{nome}</title>
    </head>
    <body>
        <h1>{nome}</h1>
        <p>Seu livro começa aqui...</p>
    </body>
    </html>""")

        home_dir = os.path.expanduser("~")
        central_dir = os.path.join(home_dir, "EditorA5")
        os.makedirs(central_dir, exist_ok=True)

        central_json_path = os.path.join(central_dir, "livros_recentes.json")

        livros = []
        if os.path.exists(central_json_path):
            try:
                with open(central_json_path, "r", encoding="utf-8") as f:
                    livros = json.load(f)
            except json.JSONDecodeError:
                livros = []

        current_time = datetime.now()

        novo_livro = {
            "nome": nome,
            "pasta": book_dir,
            "html": html_path,
            "capa": self.cover_path or "",
            "data_criacao": current_time.isoformat()
        }

        livros = [livro for livro in livros if livro.get("pasta") != book_dir]

        livros.insert(0, novo_livro)

        with open(central_json_path, "w", encoding="utf-8") as f:
            json.dump(livros, f, ensure_ascii=False, indent=4)

        QMessageBox.information(self, "Sucesso", "Livro salvo com sucesso!")

        self.html_path = html_path
        self.accept()
        return True

def import_datetime():
    import datetime
    return datetime

def openBook():
    dialog = NewBookDialog()
    result = dialog.exec()

    if result == QDialog.Accepted and hasattr(dialog, 'html_path'):
        from editor import abrir_editor
        editor_window = abrir_editor(dialog.html_path)
        return dialog

    return dialog
