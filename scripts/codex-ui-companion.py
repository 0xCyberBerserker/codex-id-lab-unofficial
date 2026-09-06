#!/usr/bin/env python3
"""Native KDE companion for Codex UI Linux Port."""

from __future__ import annotations

import argparse
import json
import locale
import os
from pathlib import Path
import re
import selectors
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from datetime import datetime
from typing import Any


APP_NAME = "Codex UI Tools"
APP_VERSION = "1.0.0"
COREDUMP_MESSAGE_ID = "fc2e22bc6ee647b6b90729ab34a250b1"
CRASH_FIELDS = (
    ("COREDUMP_COMM", "field_process"),
    ("COREDUMP_EXE", "field_executable"),
    ("COREDUMP_PID", "field_pid"),
    ("COREDUMP_UID", "field_uid"),
    ("COREDUMP_GID", "field_gid"),
    ("COREDUMP_SIGNAL_NAME", "field_signal"),
    ("COREDUMP_SIGNAL", "field_signal_number"),
    ("COREDUMP_UNIT", "field_system_unit"),
    ("COREDUMP_USER_UNIT", "field_user_unit"),
    ("COREDUMP_PACKAGE_NAME", "field_package"),
    ("COREDUMP_PACKAGE_VERSION", "field_package_version"),
    ("_BOOT_ID", "field_boot_id"),
)

TEXT = {
    "en": {
        "title": "Codex usage",
        "usage_limits": "Usage limits",
        "activity": "Activity",
        "refresh": "Refresh",
        "open_codex": "Open Codex",
        "close": "Close",
        "loading": "Reading local account data...",
        "updated": "Updated {time}",
        "error": "Could not read Codex usage",
        "used": "{value}% used",
        "resets": "Resets {time}",
        "no_reset": "Reset time unavailable",
        "primary": "primary",
        "secondary": "secondary",
        "period_minutes": "{value} min",
        "period_hours": "{value} h",
        "period_days": "{value} days",
        "latest_day": "Latest recorded day",
        "lifetime": "Lifetime tokens",
        "current_streak": "Current streak",
        "longest_streak": "Longest streak",
        "days": "{value} days",
        "reset_credits": "Available full resets",
        "unknown": "Unavailable",
        "tray_usage": "Codex usage",
        "tray_ocr": "Capture text (OCR)",
        "tray_qr": "Capture QR",
        "tray_crashes": "Crash reports",
        "tray_quit": "Quit companion",
        "capture_cancelled": "Capture cancelled",
        "ocr_ready": "Text copied to the clipboard",
        "qr_ready": "QR content copied privately to the clipboard",
        "capture_error": "Capture failed",
        "missing_command": "Required command not found: {command}",
        "missing_ocr_language": "Install English or Spanish Tesseract language data",
        "no_text": "No text was detected",
        "no_qr": "No QR code was detected",
        "crash_title": "Application crash detected",
        "crash_body": "{process} crashed. Click this notification to review safe metadata.",
        "crash_report_title": "Application crash metadata report",
        "crash_privacy": "Core contents, environment variables and command-line arguments are intentionally excluded.",
        "crash_time": "Detected at",
        "journal_time": "Journal timestamp",
        "field_process": "Process",
        "field_executable": "Executable",
        "field_pid": "PID",
        "field_uid": "UID",
        "field_gid": "GID",
        "field_signal": "Signal",
        "field_signal_number": "Signal number",
        "field_system_unit": "System unit",
        "field_user_unit": "User unit",
        "field_package": "Package",
        "field_package_version": "Package version",
        "field_boot_id": "Boot ID",
        "crash_reports_missing": "No crash reports have been recorded",
        "brand": "Made with 🖤 in Barcelona City 🇪🇸",
    },
    "es": {
        "title": "Uso de Codex",
        "usage_limits": "Límites de uso",
        "activity": "Actividad",
        "refresh": "Actualizar",
        "open_codex": "Abrir Codex",
        "close": "Cerrar",
        "loading": "Leyendo datos locales de la cuenta...",
        "updated": "Actualizado a las {time}",
        "error": "No se pudo leer el uso de Codex",
        "used": "{value}% usado",
        "resets": "Se reinicia el {time}",
        "no_reset": "Hora de reinicio no disponible",
        "primary": "principal",
        "secondary": "secundario",
        "period_minutes": "{value} min",
        "period_hours": "{value} h",
        "period_days": "{value} días",
        "latest_day": "Último día registrado",
        "lifetime": "Tokens acumulados",
        "current_streak": "Racha actual",
        "longest_streak": "Racha más larga",
        "days": "{value} días",
        "reset_credits": "Reinicios completos disponibles",
        "unknown": "No disponible",
        "tray_usage": "Uso de Codex",
        "tray_ocr": "Capturar texto (OCR)",
        "tray_qr": "Capturar QR",
        "tray_crashes": "Informes de fallos",
        "tray_quit": "Cerrar el compañero",
        "capture_cancelled": "Captura cancelada",
        "ocr_ready": "Texto copiado al portapapeles",
        "qr_ready": "Contenido QR copiado de forma privada al portapapeles",
        "capture_error": "La captura ha fallado",
        "missing_command": "No se encontró el comando necesario: {command}",
        "missing_ocr_language": "Instala los datos de idioma inglés o español de Tesseract",
        "no_text": "No se detectó texto",
        "no_qr": "No se detectó ningún código QR",
        "crash_title": "Se ha detectado un fallo de aplicación",
        "crash_body": "{process} ha fallado. Pulsa la notificación para revisar metadatos seguros.",
        "crash_report_title": "Informe de metadatos de fallo de aplicación",
        "crash_privacy": "Se excluyen intencionadamente el contenido del core, las variables de entorno y los argumentos de ejecución.",
        "crash_time": "Detectado el",
        "journal_time": "Marca temporal del registro",
        "field_process": "Proceso",
        "field_executable": "Ejecutable",
        "field_pid": "PID",
        "field_uid": "UID",
        "field_gid": "GID",
        "field_signal": "Señal",
        "field_signal_number": "Número de señal",
        "field_system_unit": "Unidad del sistema",
        "field_user_unit": "Unidad de usuario",
        "field_package": "Paquete",
        "field_package_version": "Versión del paquete",
        "field_boot_id": "ID de arranque",
        "crash_reports_missing": "Todavía no hay informes de fallos",
        "brand": "Made with 🖤 in Barcelona City 🇪🇸",
    },
}


def language() -> str:
    configured = os.environ.get("CODEXUI_LANG", "")
    current = configured or locale.getlocale()[0] or os.environ.get("LANG", "en")
    return "es" if current.lower().startswith("es") else "en"


def tr(key: str, **values: Any) -> str:
    return TEXT[language()][key].format(**values)


def codex_command() -> list[str]:
    configured = os.environ.get("CODEXUI_CODEX_COMMAND")
    if configured:
        command = shlex.split(configured)
    else:
        packaged = Path("/opt/codex-ui-linux-port/bin/codex-cli-wrapper")
        command = [str(packaged)] if packaged.is_file() else [shutil.which("codex") or ""]
    if not command or not command[0]:
        raise RuntimeError(tr("missing_command", command="codex"))
    return command


def query_codex_account(
    timeout: float = 12.0,
    cancelled: Callable[[], bool] | None = None,
) -> dict[str, Any]:
    command = codex_command() + [
        "-s",
        "read-only",
        "-a",
        "on-request",
        "app-server",
        "--stdio",
    ]
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    requests = (
        {
            "id": 1,
            "method": "initialize",
            "params": {
                "clientInfo": {"name": "codex-ui-linux-port", "version": APP_VERSION},
                "capabilities": {"experimentalApi": True},
            },
        },
        {"method": "initialized", "params": {}},
        {"id": 2, "method": "account/usage/read", "params": None},
        {"id": 3, "method": "account/rateLimits/read", "params": None},
    )
    responses: dict[int, dict[str, Any]] = {}
    error_text = ""
    selector: selectors.BaseSelector | None = None
    try:
        assert process.stdin is not None
        assert process.stdout is not None
        for request in requests:
            process.stdin.write(json.dumps(request, separators=(",", ":")) + "\n")
        process.stdin.flush()

        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and not {1, 2, 3}.issubset(responses):
            if cancelled and cancelled():
                raise RuntimeError("Codex usage read cancelled")
            for key, _ in selector.select(timeout=0.25):
                line = key.fileobj.readline()
                if not line:
                    break
                message = json.loads(line)
                request_id = message.get("id")
                if isinstance(request_id, int):
                    responses[request_id] = message
        if not {2, 3}.issubset(responses):
            raise RuntimeError("Codex app-server timed out")
        for request_id in (2, 3):
            if "error" in responses[request_id]:
                raise RuntimeError(str(responses[request_id]["error"]))
        return normalize_account_data(responses[2]["result"], responses[3]["result"])
    finally:
        if selector is not None:
            selector.close()
        if process.stdin is not None:
            process.stdin.close()
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=1)
        if process.stderr is not None:
            error_text = process.stderr.read().strip()
            process.stderr.close()
        if process.stdout is not None:
            process.stdout.close()
        if process.returncode not in (0, -15) and error_text and not responses:
            raise RuntimeError(error_text[-600:])


def normalize_account_data(
    usage_result: dict[str, Any], limits_result: dict[str, Any]
) -> dict[str, Any]:
    snapshots = limits_result.get("rateLimitsByLimitId") or {}
    if not snapshots and limits_result.get("rateLimits"):
        snapshot = limits_result["rateLimits"]
        snapshots = {snapshot.get("limitId") or "codex": snapshot}

    limits: list[dict[str, Any]] = []
    ordered_snapshots = sorted(
        snapshots.items(),
        key=lambda item: (item[0] != "codex", str(item[1].get("limitName") or item[0]).lower()),
    )
    for limit_id, snapshot in ordered_snapshots:
        name = snapshot.get("limitName") or ("Codex" if limit_id == "codex" else limit_id)
        for kind in ("primary", "secondary"):
            window = snapshot.get(kind)
            if not window:
                continue
            limits.append(
                {
                    "name": str(name),
                    "kind": kind,
                    "used_percent": max(0, min(100, int(window.get("usedPercent", 0)))),
                    "window_minutes": window.get("windowDurationMins"),
                    "resets_at": window.get("resetsAt"),
                }
            )

    buckets = usage_result.get("dailyUsageBuckets") or []
    latest = max(buckets, key=lambda row: row.get("startDate", ""), default=None)
    summary = usage_result.get("summary") or {}
    return {
        "limits": limits,
        "activity": {
            "latest_date": latest.get("startDate") if latest else None,
            "latest_tokens": latest.get("tokens") if latest else None,
            "lifetime_tokens": summary.get("lifetimeTokens"),
            "current_streak_days": summary.get("currentStreakDays"),
            "longest_streak_days": summary.get("longestStreakDays"),
        },
        "reset_credits": int((limits_result.get("rateLimitResetCredits") or {}).get("availableCount", 0)),
        "updated_at": int(time.time()),
    }


def compact_number(value: Any) -> str:
    if value is None:
        return tr("unknown")
    number = int(value)
    for threshold, suffix in ((1_000_000_000, "B"), (1_000_000, "M"), (1_000, "K")):
        if abs(number) >= threshold:
            return f"{number / threshold:.2f} {suffix}"
    return f"{number:,}"


def period_text(minutes: Any) -> str:
    if not isinstance(minutes, int):
        return tr("unknown")
    if minutes % 1440 == 0:
        return tr("period_days", value=minutes // 1440)
    if minutes % 60 == 0:
        return tr("period_hours", value=minutes // 60)
    return tr("period_minutes", value=minutes)


def reset_text(timestamp: Any) -> str:
    if not isinstance(timestamp, int):
        return tr("no_reset")
    rendered = datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M")
    return tr("resets", time=rendered)


def crash_report(event: dict[str, Any], detected_at: datetime | None = None) -> str:
    detected = detected_at or datetime.now().astimezone()
    lines = [
        tr("crash_report_title"),
        "=" * 44,
        "",
        tr("crash_privacy"),
        "",
        f"{tr('crash_time')}: {detected.isoformat(timespec='seconds')}",
    ]
    realtime = event.get("__REALTIME_TIMESTAMP")
    if realtime and str(realtime).isdigit():
        happened = datetime.fromtimestamp(int(realtime) / 1_000_000).astimezone()
        lines.append(f"{tr('journal_time')}: {happened.isoformat(timespec='seconds')}")
    for key, label_key in CRASH_FIELDS:
        value = event.get(key)
        if value not in (None, ""):
            lines.append(f"{tr(label_key)}: {value}")
    return "\n".join(lines) + "\n"


def crash_directory() -> Path:
    state_home = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state"))
    return state_home / "codex-ui-linux-port" / "crashes"


def local_tessdata_directory() -> Path | None:
    data_home = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    directory = data_home / "codex-ui-linux-port" / "tessdata"
    return directory if any(directory.glob("*.traineddata")) else None


def companion_socket_path() -> str:
    configured = Path(os.environ.get("XDG_RUNTIME_DIR", ""))
    fallback = Path(f"/run/user/{os.getuid()}")
    runtime = configured if configured.is_absolute() else fallback
    if not runtime.is_dir():
        runtime = Path.home() / ".cache"
    directory = runtime / "codex-ui-linux-port"
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(directory, 0o700)
    return str(directory / "companion.sock")


def write_crash_report(event: dict[str, Any]) -> Path:
    directory = crash_directory()
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(directory, 0o700)
    process = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(event.get("COREDUMP_COMM") or "process"))
    pid = re.sub(r"[^0-9]+", "", str(event.get("COREDUMP_PID") or "unknown")) or "unknown"
    path = directory / f"{datetime.now():%Y%m%d-%H%M%S}-{process}-{pid}.txt"
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(crash_report(event))
    return path


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=APP_NAME)
    parser.add_argument(
        "command",
        nargs="?",
        default="panel",
        choices=("tray", "panel", "usage-json", "ocr", "qr", "crashes"),
    )
    return parser.parse_args(argv)


def run_gui(command: str) -> int:
    try:
        from PySide6.QtCore import QByteArray, QMimeData, QObject, QProcess, Qt, QThread, QTimer, QUrl, Signal, Slot
        from PySide6.QtGui import QAction, QDesktopServices, QIcon
        from PySide6.QtNetwork import QLocalServer, QLocalSocket
        from PySide6.QtWidgets import (
            QApplication,
            QDialog,
            QFrame,
            QGridLayout,
            QHBoxLayout,
            QLabel,
            QMenu,
            QMessageBox,
            QProgressBar,
            QPushButton,
            QStyle,
            QSystemTrayIcon,
            QToolButton,
            QVBoxLayout,
            QWidget,
        )
    except ImportError as error:
        print(f"{APP_NAME}: PySide6 is required: {error}", file=sys.stderr)
        return 2

    try:
        socket_name = companion_socket_path()
    except OSError as error:
        print(f"{APP_NAME}: cannot create local socket: {error}", file=sys.stderr)
        return 1

    app = QApplication(sys.argv[:1])
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)

    def app_icon() -> QIcon:
        icon = QIcon.fromTheme("codex-ui-linux")
        if not icon.isNull():
            return icon
        packaged = Path("/usr/share/icons/hicolor/scalable/apps/codex-ui-linux.svg")
        return QIcon(str(packaged)) if packaged.is_file() else app.style().standardIcon(QStyle.SP_ComputerIcon)

    def send_existing(action: str) -> bool:
        socket = QLocalSocket()
        socket.connectToServer(socket_name)
        if not socket.waitForConnected(300):
            return False
        socket.write((action + "\n").encode())
        socket.flush()
        socket.waitForBytesWritten(300)
        socket.disconnectFromServer()
        return True

    if send_existing("ping" if command == "tray" else command):
        return 0

    class UsageWorker(QThread):
        succeeded = Signal(dict)
        failed = Signal(str)

        def run(self) -> None:
            try:
                self.succeeded.emit(query_codex_account(cancelled=self.isInterruptionRequested))
            except Exception as error:  # noqa: BLE001 - surfaced in the local UI
                self.failed.emit(str(error))

    class CrashWatcher(QThread):
        crash_detected = Signal(dict)

        def __init__(self) -> None:
            super().__init__()
            self.process: subprocess.Popen[str] | None = None

        def run(self) -> None:
            command_line = [
                "journalctl",
                "--follow",
                "--lines=0",
                "--no-pager",
                "--output=json",
                f"MESSAGE_ID={COREDUMP_MESSAGE_ID}",
                f"_UID={os.getuid()}",
            ]
            try:
                self.process = subprocess.Popen(
                    command_line,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True,
                    bufsize=1,
                )
                assert self.process.stdout is not None
                for line in self.process.stdout:
                    if self.isInterruptionRequested():
                        break
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if str(event.get("COREDUMP_UID", os.getuid())) == str(os.getuid()):
                        self.crash_detected.emit(event)
            except (FileNotFoundError, OSError):
                return

        def stop(self) -> None:
            self.requestInterruption()
            if self.process and self.process.poll() is None:
                self.process.terminate()

    class UsageDialog(QDialog):
        refresh_requested = Signal()

        def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle(tr("title"))
            self.setWindowIcon(app_icon())
            self.setMinimumSize(520, 470)
            self.resize(560, 520)

            root = QVBoxLayout(self)
            root.setContentsMargins(20, 18, 20, 14)
            root.setSpacing(14)

            header = QHBoxLayout()
            title = QLabel(tr("title"))
            title_font = title.font()
            title_font.setPointSize(16)
            title_font.setBold(True)
            title.setFont(title_font)
            header.addWidget(title)
            header.addStretch()
            self.refresh_button = QToolButton()
            self.refresh_button.setIcon(QIcon.fromTheme("view-refresh", self.style().standardIcon(QStyle.SP_BrowserReload)))
            self.refresh_button.setToolTip(tr("refresh"))
            self.refresh_button.setFixedSize(34, 34)
            self.refresh_button.clicked.connect(self.refresh_requested)
            header.addWidget(self.refresh_button)
            root.addLayout(header)

            self.status = QLabel(tr("loading"))
            self.status.setWordWrap(True)
            root.addWidget(self.status)

            limits_title = QLabel(tr("usage_limits"))
            limits_title.setStyleSheet("font-weight: 600;")
            root.addWidget(limits_title)
            self.limits_widget = QWidget()
            self.limits_layout = QVBoxLayout(self.limits_widget)
            self.limits_layout.setContentsMargins(0, 0, 0, 0)
            self.limits_layout.setSpacing(10)
            root.addWidget(self.limits_widget)

            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setFrameShadow(QFrame.Sunken)
            root.addWidget(separator)

            activity_title = QLabel(tr("activity"))
            activity_title.setStyleSheet("font-weight: 600;")
            root.addWidget(activity_title)
            self.metrics = QGridLayout()
            self.metrics.setHorizontalSpacing(24)
            self.metrics.setVerticalSpacing(8)
            root.addLayout(self.metrics)
            root.addStretch()

            footer = QHBoxLayout()
            self.brand = QLabel(tr("brand"))
            self.brand.setStyleSheet("font-size: 10px;")
            footer.addWidget(self.brand)
            footer.addStretch()
            open_button = QPushButton(QIcon.fromTheme("codex-ui-linux"), tr("open_codex"))
            open_button.clicked.connect(lambda: QProcess.startDetached("codex-ui-linux", []))
            footer.addWidget(open_button)
            close_button = QPushButton(tr("close"))
            close_button.clicked.connect(self.hide)
            footer.addWidget(close_button)
            root.addLayout(footer)

        def set_loading(self) -> None:
            self.refresh_button.setEnabled(False)
            self.status.setText(tr("loading"))

        def set_error(self, message: str) -> None:
            self.refresh_button.setEnabled(True)
            self.status.setText(f"{tr('error')}: {message}")

        def set_data(self, data: dict[str, Any]) -> None:
            self.refresh_button.setEnabled(True)
            self.status.setText(tr("updated", time=datetime.now().strftime("%H:%M")))
            while self.limits_layout.count():
                item = self.limits_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            for limit in data["limits"]:
                row = QWidget()
                layout = QGridLayout(row)
                layout.setContentsMargins(0, 0, 0, 0)
                name = QLabel(
                    f"{limit['name']} · {period_text(limit['window_minutes'])} · {tr(limit['kind'])}"
                )
                value = QLabel(tr("used", value=limit["used_percent"]))
                value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                bar = QProgressBar()
                bar.setRange(0, 100)
                bar.setValue(limit["used_percent"])
                bar.setTextVisible(False)
                bar.setFixedHeight(10)
                reset = QLabel(reset_text(limit["resets_at"]))
                reset.setStyleSheet("font-size: 10px;")
                layout.addWidget(name, 0, 0)
                layout.addWidget(value, 0, 1)
                layout.addWidget(bar, 1, 0, 1, 2)
                layout.addWidget(reset, 2, 0, 1, 2)
                self.limits_layout.addWidget(row)

            while self.metrics.count():
                item = self.metrics.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            activity = data["activity"]
            latest = tr("unknown")
            if activity["latest_date"]:
                latest = f"{activity['latest_date']} · {compact_number(activity['latest_tokens'])}"
            rows = (
                (tr("latest_day"), latest),
                (tr("lifetime"), compact_number(activity["lifetime_tokens"])),
                (tr("current_streak"), tr("days", value=activity["current_streak_days"] or 0)),
                (tr("longest_streak"), tr("days", value=activity["longest_streak_days"] or 0)),
                (tr("reset_credits"), str(data["reset_credits"])),
            )
            for index, (label_text, value_text) in enumerate(rows):
                label = QLabel(label_text)
                value = QLabel(value_text)
                value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                value.setStyleSheet("font-weight: 600;")
                self.metrics.addWidget(label, index, 0)
                self.metrics.addWidget(value, index, 1)

    class Controller(QObject):
        def __init__(self) -> None:
            super().__init__()
            self.dialog = UsageDialog()
            self.dialog.refresh_requested.connect(self.refresh)
            self.worker: UsageWorker | None = None
            self.last_report: Path | None = None
            self.notification_opens_report = False

            self.server = QLocalServer(self)
            QLocalServer.removeServer(socket_name)
            if not self.server.listen(socket_name):
                raise RuntimeError(self.server.errorString())
            self.server.newConnection.connect(self.accept_connection)

            self.tray = QSystemTrayIcon(app_icon(), self)
            self.tray.setToolTip(APP_NAME)
            menu = QMenu()
            actions = (
                ("panel", tr("tray_usage"), "view-statistics"),
                ("ocr", tr("tray_ocr"), "edit-select-text"),
                ("qr", tr("tray_qr"), "view-barcode-qr"),
                ("crashes", tr("tray_crashes"), "tools-report-bug"),
            )
            for action_name, label, icon_name in actions:
                action = QAction(QIcon.fromTheme(icon_name), label, menu)
                action.triggered.connect(lambda checked=False, name=action_name: self.dispatch(name))
                menu.addAction(action)
            menu.addSeparator()
            quit_action = QAction(QIcon.fromTheme("application-exit"), tr("tray_quit"), menu)
            quit_action.triggered.connect(app.quit)
            menu.addAction(quit_action)
            self.tray.setContextMenu(menu)
            self.tray.activated.connect(self.tray_activated)
            self.tray.messageClicked.connect(self.open_last_report)
            self.tray.show()

            self.crash_watcher = CrashWatcher()
            self.crash_watcher.crash_detected.connect(self.record_crash)
            self.crash_watcher.start()
            app.aboutToQuit.connect(self.shutdown)

        @Slot()
        def accept_connection(self) -> None:
            while self.server.hasPendingConnections():
                socket = self.server.nextPendingConnection()
                socket.readyRead.connect(lambda current=socket: self.read_socket(current))
                if socket.bytesAvailable():
                    self.read_socket(socket)

        def read_socket(self, socket: QLocalSocket) -> None:
            action = bytes(socket.readAll()).decode(errors="replace").strip()
            if action and action != "ping":
                self.dispatch(action)
            socket.disconnectFromServer()

        @Slot(QSystemTrayIcon.ActivationReason)
        def tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
            if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
                self.dispatch("panel")

        def dispatch(self, action: str) -> None:
            if action == "panel":
                self.dialog.show()
                self.dialog.raise_()
                self.dialog.activateWindow()
                self.refresh()
            elif action == "ocr":
                QTimer.singleShot(0, lambda: self.capture("ocr"))
            elif action == "qr":
                QTimer.singleShot(0, lambda: self.capture("qr"))
            elif action == "crashes":
                self.open_crash_directory()

        @Slot()
        def refresh(self) -> None:
            if self.worker and self.worker.isRunning():
                return
            self.dialog.set_loading()
            self.worker = UsageWorker()
            self.worker.succeeded.connect(self.dialog.set_data)
            self.worker.failed.connect(self.dialog.set_error)
            self.worker.finished.connect(self.usage_finished)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.start()

        @Slot()
        def usage_finished(self) -> None:
            self.worker = None

        def capture(self, mode: str) -> None:
            try:
                text = self.capture_text(mode)
                mime = QMimeData()
                mime.setText(text)
                if mode == "qr":
                    mime.setData("x-kde-passwordManagerHint", QByteArray(b"secret"))
                QApplication.clipboard().setMimeData(mime)
                self.notification_opens_report = False
                self.tray.showMessage(
                    APP_NAME,
                    tr("qr_ready" if mode == "qr" else "ocr_ready"),
                    app_icon(),
                    5000,
                )
            except RuntimeError as error:
                self.tray.showMessage(APP_NAME, f"{tr('capture_error')}: {error}", app_icon(), 6000)

        def capture_text(self, mode: str) -> str:
            for command_name in ("spectacle", "zbarimg" if mode == "qr" else "tesseract"):
                if not shutil.which(command_name):
                    raise RuntimeError(tr("missing_command", command=command_name))
            with tempfile.TemporaryDirectory(prefix="codex-ui-capture-") as directory:
                image = Path(directory) / "capture.png"
                capture = subprocess.run(
                    ["spectacle", "--region", "--background", "--nonotify", "--output", str(image)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=180,
                    check=False,
                )
                if capture.returncode != 0 or not image.is_file() or image.stat().st_size == 0:
                    raise RuntimeError(tr("capture_cancelled"))
                if mode == "qr":
                    result = subprocess.run(
                        ["zbarimg", "--quiet", "--raw", str(image)],
                        capture_output=True,
                        text=True,
                        timeout=20,
                        check=False,
                    )
                    text = result.stdout.strip()
                    if result.returncode != 0 or not text:
                        raise RuntimeError(tr("no_qr"))
                    return text

                tessdata = local_tessdata_directory()
                tessdata_args = ["--tessdata-dir", str(tessdata)] if tessdata else []
                languages = subprocess.run(
                    ["tesseract", *tessdata_args, "--list-langs"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False,
                ).stdout.splitlines()[1:]
                available = {item.strip() for item in languages if item.strip()}
                requested = [item for item in os.environ.get("CODEXUI_OCR_LANGUAGES", "spa+eng").split("+") if item]
                selected = [item for item in requested if item in available]
                if not selected:
                    raise RuntimeError(tr("missing_ocr_language"))
                result = subprocess.run(
                    ["tesseract", *tessdata_args, str(image), "stdout", "-l", "+".join(selected)],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    check=False,
                )
                text = result.stdout.strip()
                if result.returncode != 0 or not text:
                    raise RuntimeError(tr("no_text"))
                return text

        @Slot(dict)
        def record_crash(self, event: dict[str, Any]) -> None:
            try:
                self.last_report = write_crash_report(event)
            except OSError:
                return
            process = str(event.get("COREDUMP_COMM") or event.get("COREDUMP_EXE") or "process")
            self.notification_opens_report = True
            self.tray.showMessage(
                tr("crash_title"),
                tr("crash_body", process=process),
                QIcon.fromTheme("tools-report-bug", app_icon()),
                12000,
            )

        @Slot()
        def open_last_report(self) -> None:
            if self.notification_opens_report and self.last_report and self.last_report.is_file():
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.last_report)))

        def open_crash_directory(self) -> None:
            directory = crash_directory()
            if directory.is_dir():
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(directory)))
            else:
                QMessageBox.information(self.dialog, APP_NAME, tr("crash_reports_missing"))

        @Slot()
        def shutdown(self) -> None:
            if self.worker and self.worker.isRunning():
                self.worker.requestInterruption()
                if not self.worker.wait(3500):
                    self.worker.wait()
            self.crash_watcher.stop()
            self.crash_watcher.wait(1500)
            self.server.close()
            QLocalServer.removeServer(socket_name)

    try:
        controller = Controller()
    except RuntimeError as error:
        print(f"{APP_NAME}: {error}", file=sys.stderr)
        return 1
    QTimer.singleShot(0, lambda: controller.dispatch(command) if command != "tray" else None)
    test_quit_ms = int(os.environ.get("CODEXUI_TEST_QUIT_MS", "0"))
    if test_quit_ms > 0:
        QTimer.singleShot(test_quit_ms, app.quit)
    return app.exec()


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    if args.command == "usage-json":
        print(json.dumps(query_codex_account(), ensure_ascii=False, indent=2))
        return 0
    return run_gui(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
