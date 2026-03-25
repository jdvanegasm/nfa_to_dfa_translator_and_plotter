from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from nfa_plotter.algorithms import (
    DFAConversionResult,
    ReachabilityPruner,
    SubsetConstructionConverter,
)
from nfa_plotter.domain import Automaton, DFA, NFA
from nfa_plotter.regex import (
    RegexNormalizer,
    RegexParser,
    RegexValidator,
    ThompsonConstructor,
)
from nfa_plotter.visualization import AutomatonRenderer, SubsetTableFormatter


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("NFA Plotter - AFN to AFD Translator")
        self.setMinimumSize(1450, 920)

        self.validator = RegexValidator()
        self.normalizer = RegexNormalizer()
        self.parser = RegexParser()
        self.thompson_constructor = ThompsonConstructor()
        self.subset_converter = SubsetConstructionConverter()
        self.reachability_pruner = ReachabilityPruner()
        self.renderer = AutomatonRenderer()
        self.table_formatter = SubsetTableFormatter()

        self.output_dir = Path.cwd() / "generated"

        self.current_nfa: NFA | None = None
        self.current_dfa: DFA | None = None

        self.regex_input = QLineEdit()
        self.regex_input.setPlaceholderText("Ejemplo: (0|010)*")
        self.regex_input.textChanged.connect(self._handle_regex_changed)

        self.validate_button = QPushButton("Validar y parsear")
        self.validate_button.clicked.connect(self._handle_validate)

        self.generate_nfa_button = QPushButton("Generar AFN")
        self.generate_nfa_button.clicked.connect(self._handle_generate_nfa)

        self.convert_button = QPushButton("Convertir AFN → AFD")
        self.convert_button.clicked.connect(self._handle_convert_to_dfa)

        self.clear_button = QPushButton("Limpiar")
        self.clear_button.clicked.connect(self._handle_clear)

        self.status_label = QLabel("Estado: pendiente")
        self.normalized_label = QLabel("Regex normalizada: -")
        self.postfix_label = QLabel("Postfix: -")

        self.message_box = QTextEdit()
        self.message_box.setReadOnly(True)

        self.nfa_summary_box = QTextEdit()
        self.nfa_summary_box.setReadOnly(True)

        self.dfa_summary_box = QTextEdit()
        self.dfa_summary_box.setReadOnly(True)

        self.state_mapping_box = QTextEdit()
        self.state_mapping_box.setReadOnly(True)

        self.nfa_image_label = QLabel("Aquí se mostrará el AFN.")
        self.nfa_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.dfa_image_label = QLabel("Aquí se mostrará el AFD.")
        self.dfa_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.nfa_image_scroll = QScrollArea()
        self.nfa_image_scroll.setWidgetResizable(True)
        self.nfa_image_scroll.setWidget(self.nfa_image_label)

        self.dfa_image_scroll = QScrollArea()
        self.dfa_image_scroll.setWidgetResizable(True)
        self.dfa_image_scroll.setWidget(self.dfa_image_label)

        self.subset_table = QTableWidget()
        self.subset_table.setColumnCount(len(self.table_formatter.HEADERS))
        self.subset_table.setHorizontalHeaderLabels(self.table_formatter.HEADERS)
        self.subset_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self._build_ui()

    def _build_ui(self) -> None:
        container = QWidget()
        main_layout = QVBoxLayout(container)

        input_group = QGroupBox("Entrada")
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Expresión regular:"))
        input_layout.addWidget(self.regex_input)
        input_layout.addWidget(self.validate_button)
        input_layout.addWidget(self.generate_nfa_button)
        input_layout.addWidget(self.convert_button)
        input_layout.addWidget(self.clear_button)
        input_group.setLayout(input_layout)

        analysis_group = QGroupBox("Análisis de la expresión")
        analysis_layout = QGridLayout()
        analysis_layout.addWidget(self.status_label, 0, 0)
        analysis_layout.addWidget(self.normalized_label, 1, 0)
        analysis_layout.addWidget(self.postfix_label, 2, 0)
        analysis_group.setLayout(analysis_layout)

        messages_group = QGroupBox("Mensajes")
        messages_layout = QVBoxLayout()
        messages_layout.addWidget(self.message_box)
        messages_group.setLayout(messages_layout)

        nfa_text_group = QGroupBox("Resumen del AFN")
        nfa_text_layout = QVBoxLayout()
        nfa_text_layout.addWidget(self.nfa_summary_box)
        nfa_text_group.setLayout(nfa_text_layout)

        dfa_text_group = QGroupBox("Resumen del AFD")
        dfa_text_layout = QVBoxLayout()
        dfa_text_layout.addWidget(self.dfa_summary_box)
        dfa_text_group.setLayout(dfa_text_layout)

        mapping_group = QGroupBox("Mapeo de estados del AFD")
        mapping_layout = QVBoxLayout()
        mapping_layout.addWidget(self.state_mapping_box)
        mapping_group.setLayout(mapping_layout)

        subset_group = QGroupBox("Tabla del método de subconjuntos")
        subset_layout = QVBoxLayout()
        subset_layout.addWidget(self.subset_table)
        subset_group.setLayout(subset_layout)

        nfa_image_group = QGroupBox("Visualización del AFN")
        nfa_image_layout = QVBoxLayout()
        nfa_image_layout.addWidget(self.nfa_image_scroll)
        nfa_image_group.setLayout(nfa_image_layout)

        dfa_image_group = QGroupBox("Visualización del AFD")
        dfa_image_layout = QVBoxLayout()
        dfa_image_layout.addWidget(self.dfa_image_scroll)
        dfa_image_group.setLayout(dfa_image_layout)

        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        left_top_widget = QWidget()
        left_top_layout = QVBoxLayout(left_top_widget)
        left_top_layout.addWidget(nfa_text_group)
        left_top_layout.addWidget(dfa_text_group)
        left_top_layout.addWidget(mapping_group)

        right_top_widget = QWidget()
        right_top_layout = QVBoxLayout(right_top_widget)
        right_top_layout.addWidget(subset_group)

        top_splitter.addWidget(left_top_widget)
        top_splitter.addWidget(right_top_widget)
        top_splitter.setSizes([520, 900])

        bottom_splitter = QSplitter(Qt.Orientation.Horizontal)
        bottom_splitter.addWidget(nfa_image_group)
        bottom_splitter.addWidget(dfa_image_group)
        bottom_splitter.setSizes([700, 700])

        main_layout.addWidget(input_group)
        main_layout.addWidget(analysis_group)
        main_layout.addWidget(messages_group)
        main_layout.addWidget(top_splitter, 1)
        main_layout.addWidget(bottom_splitter, 1)

        self.setCentralWidget(container)

    def _handle_regex_changed(self) -> None:
        """Limpia resultados previos cuando cambia la expresión."""
        self.current_nfa = None
        self.current_dfa = None
        self._clear_generated_outputs()
        self.status_label.setText("Estado: pendiente")
        self.normalized_label.setText("Regex normalizada: -")
        self.postfix_label.setText("Postfix: -")
        self.message_box.setPlainText("La expresión cambió. Vuelve a validar o generar.")

    def _handle_clear(self) -> None:
        """Limpia por completo la interfaz."""
        self.regex_input.clear()
        self.current_nfa = None
        self.current_dfa = None
        self.status_label.setText("Estado: pendiente")
        self.normalized_label.setText("Regex normalizada: -")
        self.postfix_label.setText("Postfix: -")
        self.message_box.clear()
        self._clear_generated_outputs()

    def _handle_validate(self) -> None:
        regex = self.regex_input.text()
        validation = self.validator.validate(regex)

        if not validation.is_valid:
            self._set_invalid_state(validation.errors)
            return

        normalized = self.normalizer.insert_concatenation(regex)
        postfix = self.parser.to_postfix(regex)

        self.status_label.setText("Estado: válida")
        self.normalized_label.setText(f"Regex normalizada: {normalized}")
        self.postfix_label.setText(f"Postfix: {' '.join(postfix)}")
        self.message_box.setPlainText("Sin errores.")

    def _handle_generate_nfa(self) -> None:
        try:
            self.current_nfa = self._build_nfa_from_input()
            self.current_dfa = None

            self.nfa_summary_box.setPlainText(
                self._format_automaton_summary(self.current_nfa)
            )
            self.dfa_summary_box.clear()
            self.state_mapping_box.clear()
            self._clear_table()
            self._clear_image(self.dfa_image_label, "Aquí se mostrará el AFD.")

            rendered_path = self.renderer.render_png(
                self.current_nfa,
                self.output_dir / "nfa",
            )
            self._load_image(self.nfa_image_label, rendered_path)

            self.message_box.setPlainText(
                "AFN generado correctamente.\n"
                "Ahora puedes visualizarlo o ejecutar la conversión AFN → AFD."
            )
            self.status_label.setText("Estado: AFN generado correctamente")
        except Exception as exc:
            self._set_build_error(str(exc))

    def _handle_convert_to_dfa(self) -> None:
        try:
            self.current_nfa = self._build_nfa_from_input()

            conversion_result = self.subset_converter.convert(self.current_nfa)
            self.current_dfa = self.reachability_pruner.prune(conversion_result.dfa)

            self.nfa_summary_box.setPlainText(
                self._format_automaton_summary(self.current_nfa)
            )
            self.dfa_summary_box.setPlainText(
                self._format_automaton_summary(self.current_dfa)
            )
            self.state_mapping_box.setPlainText(
                self._format_state_mapping(conversion_result)
            )

            nfa_path = self.renderer.render_png(self.current_nfa, self.output_dir / "nfa")
            dfa_path = self.renderer.render_png(self.current_dfa, self.output_dir / "dfa")

            self._load_image(self.nfa_image_label, nfa_path)
            self._load_image(self.dfa_image_label, dfa_path)
            self._populate_subset_table(conversion_result)

            self.message_box.setPlainText(
                "Conversión AFN → AFD completada correctamente.\n"
                "Se generó la tabla de subconjuntos, el mapeo Kᵢ y el AFD final."
            )
            self.status_label.setText("Estado: conversión completada")
        except Exception as exc:
            self._set_build_error(str(exc))

    def _build_nfa_from_input(self) -> NFA:
        regex = self.regex_input.text()
        validation = self.validator.validate(regex)

        if not validation.is_valid:
            self._set_invalid_state(validation.errors)
            raise ValueError("La expresión regular ingresada es inválida.")

        normalized = self.normalizer.insert_concatenation(regex)
        postfix = self.parser.to_postfix(regex)
        nfa = self.thompson_constructor.build_from_postfix(postfix)

        self.normalized_label.setText(f"Regex normalizada: {normalized}")
        self.postfix_label.setText(f"Postfix: {' '.join(postfix)}")

        return nfa

    def _populate_subset_table(self, conversion_result: DFAConversionResult) -> None:
        rows = self.table_formatter.build_rows(conversion_result)
        self.subset_table.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            for column_index, cell_value in enumerate(row):
                self.subset_table.setItem(
                    row_index,
                    column_index,
                    QTableWidgetItem(cell_value),
                )

        self.subset_table.resizeColumnsToContents()
        self.subset_table.resizeRowsToContents()

    def _clear_generated_outputs(self) -> None:
        self.nfa_summary_box.clear()
        self.dfa_summary_box.clear()
        self.state_mapping_box.clear()
        self._clear_table()
        self._clear_image(self.nfa_image_label, "Aquí se mostrará el AFN.")
        self._clear_image(self.dfa_image_label, "Aquí se mostrará el AFD.")

    def _clear_table(self) -> None:
        self.subset_table.clearContents()
        self.subset_table.setRowCount(0)

    def _set_invalid_state(self, errors: list[str]) -> None:
        self.status_label.setText("Estado: inválida")
        self.normalized_label.setText("Regex normalizada: -")
        self.postfix_label.setText("Postfix: -")
        self.message_box.setPlainText("\n".join(errors))
        self._clear_generated_outputs()

    def _set_build_error(self, error_message: str) -> None:
        self.status_label.setText("Estado: error")
        self.message_box.setPlainText(error_message)
        self.dfa_summary_box.clear()
        self.state_mapping_box.clear()

    @staticmethod
    def _clear_image(label: QLabel, placeholder_text: str) -> None:
        label.setPixmap(QPixmap())
        label.setText(placeholder_text)

    @staticmethod
    def _load_image(label: QLabel, image_path: str) -> None:
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            label.setText(f"No se pudo cargar la imagen: {image_path}")
            return

        label.setText("")
        label.setPixmap(pixmap)
        label.adjustSize()

    @staticmethod
    def _format_automaton_summary(automaton: Automaton) -> str:
        lines: list[str] = []

        lines.append("Estados:")
        for state_id in sorted(automaton.states):
            state = automaton.states[state_id]
            tags: list[str] = []
            if state.is_start:
                tags.append("inicial")
            if state.is_accepting:
                tags.append("aceptación")

            suffix = f" ({', '.join(tags)})" if tags else ""
            lines.append(f"  - {state.id}{suffix}")

        lines.append("")
        lines.append(f"Estado inicial: {automaton.start_state_id}")
        lines.append(
            "Estados de aceptación: "
            + (", ".join(sorted(automaton.accepting_state_ids)) or "-")
        )

        lines.append("")
        lines.append("Transiciones:")
        for transition in sorted(
            automaton.transitions,
            key=lambda item: (item.source_id, item.symbol, item.target_id),
        ):
            lines.append(
                f"  δ({transition.source_id}, {transition.symbol}) = {transition.target_id}"
            )

        lines.append("")
        lines.append(f"Cantidad de estados: {len(automaton.states)}")
        lines.append(f"Cantidad de transiciones: {len(automaton.transitions)}")

        return "\n".join(lines)

    def _format_state_mapping(self, conversion_result: DFAConversionResult) -> str:
        lines = ["Mapeo de estados del AFD:"]
        lines.append("")

        visible_state_ids = set(self.current_dfa.states) if self.current_dfa else set()

        for state_name in sorted(conversion_result.state_mapping):
            if visible_state_ids and state_name not in visible_state_ids:
                continue

            subset = conversion_result.state_mapping[state_name]
            subset_text = self._format_subset(subset)
            accepting_marker = ""
            if self.current_dfa and state_name in self.current_dfa.accepting_state_ids:
                accepting_marker = " [aceptación]"
            if self.current_dfa and state_name == self.current_dfa.start_state_id:
                accepting_marker = " [inicial]" + accepting_marker

            lines.append(f"{state_name} = {subset_text}{accepting_marker}")

        return "\n".join(lines)

    @staticmethod
    def _format_subset(subset: frozenset[str]) -> str:
        if not subset:
            return "∅"
        return "{" + ", ".join(sorted(subset)) + "}"