import os
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QFileDialog, QMessageBox,
    QFontComboBox, QComboBox, QWidget, QInputDialog,
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QGridLayout
)
from PySide6.QtGui import QFont, QTextCursor, QTextListFormat, QAction, QIcon, QTextCharFormat, QTextBlockFormat, QImage, QPixmap
from PySide6.QtCore import QFile, Qt, QUrl
from PySide6.QtUiTools import QUiLoader
import json


class RedimensionarImagemDialog(QDialog):
    def __init__(self, caminho_imagem, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Redimensionar Imagem")
        self.caminho_imagem = caminho_imagem
        self.imagem = QImage(caminho_imagem)

        if self.imagem.isNull():
            QMessageBox.warning(self, "Erro", "Não foi possível carregar a imagem.")
            return

        # Layouts
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        # Largura e Altura
        self.largura_input = QLineEdit(str(self.imagem.width()))
        self.altura_input = QLineEdit(str(self.imagem.height()))

        form_layout.addWidget(QLabel("Largura:"))
        form_layout.addWidget(self.largura_input)
        form_layout.addWidget(QLabel("Altura:"))
        form_layout.addWidget(self.altura_input)

        # Manter a proporção
        self.manter_proporcao_check = QCheckBox("Manter a proporção")
        self.manter_proporcao_check.setChecked(True)  # Marcar por padrão

        # Botões de ação
        self.botao_ok = QPushButton("Aplicar")
        self.botao_cancelar = QPushButton("Cancelar")

        layout.addLayout(form_layout)
        layout.addWidget(self.manter_proporcao_check)
        layout.addWidget(self.botao_ok)
        layout.addWidget(self.botao_cancelar)

        self.setLayout(layout)

        # Conectar os botões
        self.botao_ok.clicked.connect(self.aplicar_redimensionamento)
        self.botao_cancelar.clicked.connect(self.reject)

    def aplicar_redimensionamento(self):
        largura = int(self.largura_input.text())
        altura = int(self.altura_input.text())

        if self.manter_proporcao_check.isChecked():
            # Redimensionar mantendo a proporção
            self.imagem = self.imagem.scaled(largura, altura, Qt.KeepAspectRatio)
        else:
            # Redimensionar sem manter a proporção
            self.imagem = self.imagem.scaled(largura, altura, Qt.IgnoreAspectRatio)

        self.accept()

class EditorWindow(QMainWindow):
    def __init__(self, html_path=None):
        super().__init__()

        loader = QUiLoader()
        ui_file = QFile("editor.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file)
        ui_file.close()

        self.setCentralWidget(self.ui)
        self.setWindowTitle("Editor A5")
        self.resize(1280, 720)

        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

        self.current_file_path = html_path
        self.arquivo_alterado = False

        self.setup_ui()
        self.conectar_sinais()

        if html_path and os.path.exists(html_path):
            self.carregar_arquivo(html_path)
            self.setWindowTitle(f"Editor A5 - {os.path.basename(html_path)}")

        action_inicio = self.ui.findChild(QAction, "actionInicio")
        if action_inicio:
            action_inicio.triggered.connect(self.voltar_ao_inicio)

        self.show()

    def setup_ui(self):
        self.editor = self.ui.findChild(QTextEdit, "textEdit")
        self.editor.setAcceptRichText(True)
        self.definir_formatacao_padrao()
        self.editor.textChanged.connect(self.marcar_como_alterado)

        self.combo_fonte = self.ui.findChild(QFontComboBox, "comboFonte")
        if not self.combo_fonte:
            self.combo_fonte = QFontComboBox(self)
            self.ui.horizontalLayout.addWidget(self.combo_fonte)
        self.combo_fonte.currentFontChanged.connect(self.aplicar_fonte)

        self.combo_tamanho = self.ui.findChild(QComboBox, "comboTamanho")
        tamanhos = ["8", "9", "10", "11", "12", "14", "16", "18", "20", "22", "24", "26", "28", "32", "36", "42", "48", "56", "72"]
        self.combo_tamanho.addItems(tamanhos)
        self.combo_tamanho.setCurrentText("12")
        self.combo_tamanho.currentTextChanged.connect(self.aplicar_tamanho)

        self.definir_icones_fallback()

    def definir_formatacao_padrao(self):
        formato = QTextCharFormat()
        formato.setFont(QFont("Times New Roman", 12))
        self.editor.mergeCurrentCharFormat(formato)

    def definir_icones_fallback(self):
        actions_icons = {
            "actionNovo": "icons/novo.png",
            "actionAbrir": "icons/abrir.png",
            "actionSalvar": "icons/salvar.png",
            "actionDesfazer": "icons/desfazer.png",
            "actionRefazer": "icons/refazer.png",
            "actionNegrito": "icons/negrito.png",
            "actionItalico": "icons/italico.png",
            "actionSublinhado": "icons/sublinhado.png",
            "actionListaNumerada": "icons/lista_numerada.png",
            "actionListaMarcadores": "icons/lista_marcadores.png",
            "actionAlinharEsquerda": "icons/al_esquerda.png",
            "actionCentralizar": "icons/centralizar.png",
            "actionAlinharDireita": "icons/al_direita.png",
            "actionJustificar": "icons/justificar.png",
            "actionInicio": "icons/inicio.png",
        }

        for action_name, icon_path in actions_icons.items():
            action = self.ui.findChild(QAction, action_name)
            if action and action.icon().isNull() and os.path.exists(icon_path):
                action.setIcon(QIcon(icon_path))

    def conectar_sinais(self):
        self.ui.findChild(QAction, "actionNovo").triggered.connect(self.novo_documento)
        self.ui.findChild(QAction, "actionAbrir").triggered.connect(self.abrir_arquivo)
        self.ui.findChild(QAction, "actionSalvar").triggered.connect(self.salvar_arquivo)

        self.ui.findChild(QAction, "actionDesfazer").triggered.connect(self.editor.undo)
        self.ui.findChild(QAction, "actionRefazer").triggered.connect(self.editor.redo)

        self.ui.findChild(QAction, "actionNegrito").triggered.connect(self.toggle_negrito)
        self.ui.findChild(QAction, "actionItalico").triggered.connect(self.toggle_italico)
        self.ui.findChild(QAction, "actionSublinhado").triggered.connect(self.toggle_sublinhado)

        self.ui.findChild(QAction, "actionListaNumerada").triggered.connect(self.aplicar_lista_numerada)
        self.ui.findChild(QAction, "actionListaMarcadores").triggered.connect(self.aplicar_lista_marcadores)

        self.ui.findChild(QAction, "actionAlinharEsquerda").triggered.connect(lambda: self.aplicar_alinhamento(Qt.AlignLeft))
        self.ui.findChild(QAction, "actionCentralizar").triggered.connect(lambda: self.aplicar_alinhamento(Qt.AlignCenter))
        self.ui.findChild(QAction, "actionAlinharDireita").triggered.connect(lambda: self.aplicar_alinhamento(Qt.AlignRight))
        self.ui.findChild(QAction, "actionJustificar").triggered.connect(lambda: self.aplicar_alinhamento(Qt.AlignJustify))

        self.ui.findChild(QAction, "actionTitulo").triggered.connect(self.formatar_titulo)
        self.ui.findChild(QAction, "actionSubtitulo").triggered.connect(self.formatar_subtitulo)
        self.ui.findChild(QAction, "actionTexto").triggered.connect(self.formatar_texto)

        self.ui.findChild(QAction, "actionImagem").triggered.connect(self.adicionar_imagem)

    def adicionar_imagem(self):
            # Abrir o diálogo para escolher a imagem
            caminho_imagem, _ = QFileDialog.getOpenFileName(self, "Selecionar Imagem", "", "Imagens (*.png *.jpg *.jpeg *.bmp *.gif)")

            if caminho_imagem:
                # Exibir a janela de redimensionamento
                dialogo = RedimensionarImagemDialog(caminho_imagem, self)

                if dialogo.exec_() == QDialog.Accepted:
                    # Obter a imagem redimensionada
                    imagem_redimensionada = dialogo.imagem

                    # Criar um QTextImageFormat com a imagem redimensionada
                    image_format = QTextImageFormat()
                    image_format.setWidth(imagem_redimensionada.width())
                    image_format.setHeight(imagem_redimensionada.height())

                    # Inserir a imagem redimensionada no QTextEdit
                    cursor = self.ui.textEdit.textCursor()
                    cursor.insertImage(image_format)

    def formatar_titulo(self):
        cursor = self.ui.textEdit.textCursor()
        format = QTextCharFormat()
        format.setFontFamily("Times New Roman")
        format.setFontPointSize(24)
        format.setFontWeight(QFont.Bold)
        cursor.mergeCharFormat(format)

    def formatar_subtitulo(self):
        cursor = self.ui.textEdit.textCursor()
        format = QTextCharFormat()
        format.setFontFamily("Times New Roman")
        format.setFontPointSize(18)
        format.setFontWeight(QFont.Bold)
        cursor.mergeCharFormat(format)

    def formatar_texto(self):
        cursor = self.ui.textEdit.textCursor()
        format = QTextCharFormat()
        format.setFontFamily("Times New Roman")
        format.setFontPointSize(12)
        format.setFontWeight(QFont.Normal)
        format.setFontItalic(False)
        cursor.mergeCharFormat(format)

    def marcar_como_alterado(self):
        self.arquivo_alterado = True

    def aplicar_fonte(self, fonte):
        fmt = QTextCharFormat()
        fmt.setFont(fonte)
        self.editor.mergeCurrentCharFormat(fmt)

    def aplicar_tamanho(self, tamanho):
        fmt = QTextCharFormat()
        fmt.setFontPointSize(float(tamanho))
        self.editor.mergeCurrentCharFormat(fmt)

    def toggle_negrito(self):
        fmt = QTextCharFormat()
        peso = QFont.Bold if not self.editor.fontWeight() == QFont.Bold else QFont.Normal
        fmt.setFontWeight(peso)
        self.editor.mergeCurrentCharFormat(fmt)

    def toggle_italico(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(not self.editor.fontItalic())
        self.editor.mergeCurrentCharFormat(fmt)

    def toggle_sublinhado(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(not self.editor.fontUnderline())
        self.editor.mergeCurrentCharFormat(fmt)

    def novo_documento(self):
        if self.arquivo_alterado:
            resp = QMessageBox.question(self, "Salvar alterações?", "Deseja salvar antes de criar um novo documento?")
            if resp == QMessageBox.Yes:
                self.salvar_arquivo()
        self.editor.clear()
        self.current_file_path = None
        self.arquivo_alterado = False

    def abrir_arquivo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Abrir arquivo", "", "HTML (*.html)")
        if path:
            self.carregar_arquivo(path)

    def carregar_arquivo(self, path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                self.editor.setHtml(conteudo)
                self.current_file_path = path
                self.arquivo_alterado = False

                self.atualizar_json_central(path)
            except Exception as e:
                QMessageBox.critical(self, "Erro ao Abrir", f"Não foi possível abrir o arquivo: {str(e)}")

    def salvar_arquivo(self):
        if not self.current_file_path:
            self.current_file_path, _ = QFileDialog.getSaveFileName(self, "Salvar como", "", "HTML (*.html)")
        if self.current_file_path:
            with open(self.current_file_path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toHtml())
            self.arquivo_alterado = False

    def salvar_em_arquivo(self, file_path):
        try:
            html_content = self.editor.toHtml()
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(html_content)
            self.current_file_path = file_path
            self.arquivo_alterado = False
            self.setWindowTitle(f"Editor A5 - {os.path.basename(file_path)}")

            self.atualizar_json_central(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Erro ao Salvar", f"Não foi possível salvar o arquivo: {str(e)}")

    def atualizar_json_central(self, file_path):
        try:
            home_dir = os.path.expanduser("~")
            central_dir = os.path.join(home_dir, "EditorA5")
            json_path = os.path.join(central_dir, "livros_recentes.json")

            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    livros = json.load(f)

                for livro in livros:
                    if livro.get("html") == file_path:
                        livros.remove(livro)
                        livros.insert(0, livro)
                        break

                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(livros, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Erro ao atualizar JSON central: {e}")

    def verificar_alteracoes(self):
        if self.arquivo_alterado:
            resposta = QMessageBox.question(
                self, "Arquivo Alterado",
                "O arquivo atual foi modificado. Deseja salvar as alterações?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )

            if resposta == QMessageBox.Save:
                self.salvar_arquivo()
                return True
            elif resposta == QMessageBox.Cancel:
                return False
        return True

    def aplicar_negrito(self, checked):
        fmt = self.editor.currentCharFormat()
        fmt.setFontWeight(QFont.Bold if checked else QFont.Normal)
        self.editor.setCurrentCharFormat(fmt)

    def aplicar_italico(self, checked):
        fmt = self.editor.currentCharFormat()
        fmt.setFontItalic(checked)
        self.editor.setCurrentCharFormat(fmt)

    def aplicar_sublinhado(self, checked):
        fmt = self.editor.currentCharFormat()
        fmt.setFontUnderline(checked)
        self.editor.setCurrentCharFormat(fmt)

    def aplicar_lista_numerada(self):
        cursor = self.editor.textCursor()

        if not cursor.hasSelection():
            cursor.select(QTextCursor.BlockUnderCursor)

        list_format = QTextListFormat()
        list_format.setStyle(QTextListFormat.ListDecimal)

        block_format = QTextBlockFormat()
        cursor.mergeBlockFormat(block_format)
        cursor.createList(list_format)

    def aplicar_lista_marcadores(self):
        cursor = self.editor.textCursor()

        if not cursor.hasSelection():
            cursor.select(QTextCursor.BlockUnderCursor)

        list_format = QTextListFormat()
        list_format.setStyle(QTextListFormat.ListDisc)

        block_format = QTextBlockFormat()
        cursor.mergeBlockFormat(block_format)
        cursor.createList(list_format)

    def aplicar_alinhamento(self, alinhamento):
        self.editor.setAlignment(alinhamento)

        self.ui.actionAlinharEsquerda.setChecked(alinhamento == Qt.AlignLeft)
        self.ui.actionCentralizar.setChecked(alinhamento == Qt.AlignCenter)
        self.ui.actionAlinharDireita.setChecked(alinhamento == Qt.AlignRight)
        self.ui.actionJustificar.setChecked(alinhamento == Qt.AlignJustify)

    def aplicar_fonte(self, font):
        fmt = self.editor.currentCharFormat()
        fmt.setFont(font)
        self.editor.setCurrentCharFormat(fmt)

    def aplicar_tamanho_fonte(self, size):
        fmt = self.editor.currentCharFormat()
        fmt.setFontPointSize(float(size))
        self.editor.setCurrentCharFormat(fmt)

    def atualizar_estado_formatacao(self):
        fmt = self.editor.currentCharFormat()

        self.ui.actionNegrito.setChecked(fmt.fontWeight() == QFont.Bold)

        self.ui.actionItalico.setChecked(fmt.fontItalic())

        self.ui.actionSublinhado.setChecked(fmt.fontUnderline())

        self.combo_fonte.setCurrentFont(fmt.font())

        if fmt.fontPointSize() > 0:
            self.combo_tamanho.setCurrentText(str(int(fmt.fontPointSize())))

    def voltar_ao_inicio(self):
        if self.verificar_alteracoes():
            self.hide()
            import welcome
            self.welcome_window = welcome.WelcomeWindow()
            self.close()

    def closeEvent(self, event):
        if self.verificar_alteracoes():
            event.accept()
        else:
            event.ignore()

def abrir_editor(html_path=None):
    return EditorWindow(html_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        editor = EditorWindow(sys.argv[1])
    else:
        editor = EditorWindow()

    sys.exit(app.exec())
