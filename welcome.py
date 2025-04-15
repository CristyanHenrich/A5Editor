import os
import sys
import json
from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QListWidget, QListWidgetItem, QListView
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import newBook

class WelcomeWindow:
    def __init__(self):
        self.load_ui()
        self.carregar_livros_recentes()

    def load_ui(self):
        loader = QUiLoader()
        ui_file = QFile("welcome.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file)
        ui_file.close()

        self.ui.resize(1280, 720)

        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.ui.width()) // 2
        y = (screen_geometry.height() - self.ui.height()) // 2
        self.ui.move(x, y)

        self.ui.findChild(QWidget, "btnNew").clicked.connect(self.novo_livro)
        self.ui.findChild(QWidget, "btnOpen").clicked.connect(self.abrir_livro)

        self.lista_livros = self.ui.findChild(QListView, "listaLivros")

        if self.lista_livros:
            from PySide6.QtCore import QStringListModel, Qt, QModelIndex
            self.modelo_livros = QStringListModel()
            self.lista_livros.setModel(self.modelo_livros)
            self.lista_livros.clicked.connect(self.abrir_livro_recente)

            self.caminhos_html = []

        self.ui.show()

    def carregar_livros_recentes(self):
        """Carrega os livros recentes do arquivo JSON central para exibição na tela inicial"""
        if not self.lista_livros:
            return

        print("Carregando livros recentes...")

        # Limpar listas
        self.caminhos_html = []
        nomes_livros = []

        # Carregar livros do JSON central
        home_dir = os.path.expanduser("~")
        central_dir = os.path.join(home_dir, "EditorA5")
        json_path = os.path.join(central_dir, "livros_recentes.json")

        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    livros = json.load(f)

                # Processar cada livro
                for livro in livros:
                    nomes_livros.append(livro["nome"])
                    self.caminhos_html.append(livro["html"])

                # Atualizar o modelo com os nomes dos livros
                self.modelo_livros.setStringList(nomes_livros)

            except Exception as e:
                print(f"Erro ao carregar livros recentes: {e}")

    def novo_livro(self):
        """Abre o diálogo para criar um novo livro"""
        dialog = newBook.openBook()
        if hasattr(dialog, 'html_path') and dialog.html_path:
            self.ui.close()

    def abrir_livro(self):
        """Abre um livro existente através de diálogo de seleção de arquivo"""
        path, _ = QFileDialog.getOpenFileName(
            self.ui, "Abrir Livro", "", "Arquivos HTML (*.html)"
        )
        if path:
            from editor import abrir_editor
            self.editor_window = abrir_editor(path)
            self.ui.close()

    def abrir_livro_recente(self, index):
        """Abre um livro recente da lista"""
        if 0 <= index.row() < len(self.caminhos_html):
            html_path = self.caminhos_html[index.row()]
            if html_path and os.path.exists(html_path):
                # Importar aqui para evitar importação circular
                from editor import abrir_editor
                self.editor_window = abrir_editor(html_path)
                self.ui.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WelcomeWindow()
    sys.exit(app.exec())
