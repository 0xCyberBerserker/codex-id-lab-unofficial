#!/usr/bin/env python3
"""Native KDE companion for Codex I+D Lab - Unofficial."""

from __future__ import annotations

import argparse
import json
import locale
import math
import os
from pathlib import Path
import re
import random
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from collections.abc import Callable
from datetime import datetime
from typing import Any

from codex_lab_account import AccountCache, AccountClient, SharedAccountClient, TaskAttention, read_loaded_tasks, task_status


APP_NAME = "Codex Lab Tools"
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
        "remaining": "{value}% remaining",
        "tasks_unavailable": "Desktop task status unavailable: no verified bridge",
        "tasks_snapshot": "Loaded threads: {count} · active: {active} · attention: {attention}",
        "tasks_partial": "Bounded snapshot; other desktop tasks may not be visible",
        "tasks_attention_title": "Codex needs your review",
        "tasks_attention_body": "{count} loaded thread(s) need attention. Review them in the main application.",
        "account_changed": "Account changed; previous quota data was cleared",
        "stale": "Last valid data is stale ({minutes} min old)",
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
        "qr_ready": "QR content copied with a KDE history hint; other clipboard clients may still read it",
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
        "remaining": "{value}% restante",
        "tasks_unavailable": "Estado de tareas del desktop no disponible: falta un puente verificado",
        "tasks_snapshot": "Hilos cargados: {count} · activos: {active} · atención: {attention}",
        "tasks_partial": "Snapshot acotado; otras tareas del escritorio pueden no ser visibles",
        "tasks_attention_title": "Codex necesita tu revisión",
        "tasks_attention_body": "{count} hilo(s) cargado(s) necesitan atención. Revísalos en la aplicación principal.",
        "account_changed": "La cuenta ha cambiado; se han descartado sus cuotas anteriores",
        "stale": "Último dato válido obsoleto ({minutes} min de antigüedad)",
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
        "qr_ready": "QR copiado con una indicación para el historial KDE; otros clientes aún pueden leerlo",
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


TEXT["ca"] = {
    "title": "Ús de Codex",
    "usage_limits": "Límits d'ús",
    "activity": "Activitat",
    "refresh": "Actualitza",
    "open_codex": "Obre Codex",
    "close": "Tanca",
    "loading": "Llegint les dades locals del compte...",
    "updated": "Actualitzat a les {time}",
    "error": "No s'ha pogut llegir l'ús de Codex",
    "used": "{value}% utilitzat",
    "remaining": "{value}% restant",
    "tasks_unavailable": "Estat de les tasques del desktop no disponible: manca un pont verificat",
    "tasks_snapshot": "Fils carregats: {count} · actius: {active} · atenció: {attention}",
    "tasks_partial": "Snapshot acotat; altres tasques de l'escriptori poden no ser visibles",
    "tasks_attention_title": "Codex necessita la teva revisió",
    "tasks_attention_body": "{count} fil(s) carregat(s) necessiten atenció. Revisa'ls a l'aplicació principal.",
    "account_changed": "El compte ha canviat; s'han descartat les quotes anteriors",
    "stale": "Última dada vàlida obsoleta ({minutes} min d'antiguitat)",
    "resets": "Es reinicia el {time}",
    "no_reset": "Hora de reinici no disponible",
    "primary": "principal",
    "secondary": "secundari",
    "period_minutes": "{value} min",
    "period_hours": "{value} h",
    "period_days": "{value} dies",
    "latest_day": "Últim dia registrat",
    "lifetime": "Tokens acumulats",
    "current_streak": "Ratxa actual",
    "longest_streak": "Ratxa més llarga",
    "days": "{value} dies",
    "reset_credits": "Reinicis complets disponibles",
    "unknown": "No disponible",
    "tray_usage": "Ús de Codex",
    "tray_ocr": "Captura text (OCR)",
    "tray_qr": "Captura QR",
    "tray_crashes": "Informes d'errors",
    "tray_quit": "Tanca el companion",
    "capture_cancelled": "Captura cancel·lada",
    "ocr_ready": "Text copiat al porta-retalls",
    "qr_ready": "QR copiat amb una indicació per a l'historial KDE; altres clients encara el poden llegir",
    "capture_error": "La captura ha fallat",
    "missing_command": "No s'ha trobat l'ordre necessària: {command}",
    "missing_ocr_language": "Instal·la les dades d'anglès o espanyol de Tesseract",
    "no_text": "No s'ha detectat text",
    "no_qr": "No s'ha detectat cap codi QR",
    "crash_title": "S'ha detectat un error d'aplicació",
    "crash_body": "{process} ha fallat. Prem la notificació per revisar metadades segures.",
    "crash_report_title": "Informe de metadades d'error d'aplicació",
    "crash_privacy": "S'exclouen el contingut del core, les variables d'entorn i els arguments d'execució.",
    "crash_time": "Detectat el",
    "journal_time": "Marca temporal del registre",
    "field_process": "Procés",
    "field_executable": "Executable",
    "field_pid": "PID",
    "field_uid": "UID",
    "field_gid": "GID",
    "field_signal": "Senyal",
    "field_signal_number": "Número de senyal",
    "field_system_unit": "Unitat del sistema",
    "field_user_unit": "Unitat d'usuari",
    "field_package": "Paquet",
    "field_package_version": "Versió del paquet",
    "field_boot_id": "ID d'arrencada",
    "crash_reports_missing": "Encara no hi ha informes d'errors",
    "brand": "Made with 🖤 in Barcelona City 🇪🇸",
}


for code, labels in {
    "en": ("Linux features", "Save preferences", "Preferences saved; rebuild required. No installed runtime was changed.", "Experimental opt-in features. Saving does not install, grant permissions or rebuild.", "disabled", "enabled", "pending rebuild", "incompatible"),
    "es": ("Funciones Linux", "Guardar preferencias", "Preferencias guardadas; requieren rebuild. El runtime instalado no cambia.", "Funciones experimentales opt-in. Guardar no instala, concede permisos ni reconstruye.", "deshabilitada", "habilitada", "rebuild pendiente", "incompatible"),
    "ca": ("Funcions Linux", "Desar preferències", "Preferències desades; cal rebuild. El runtime instal·lat no canvia.", "Funcions experimentals opt-in. Desar no instal·la, concedeix permisos ni reconstrueix.", "desactivada", "activada", "rebuild pendent", "incompatible"),
}.items():
    TEXT[code].update(zip(("features_title", "features_save", "features_saved", "features_hint", "feature_disabled", "feature_enabled", "feature_pending-rebuild", "feature_incompatible"), labels))


def language() -> str:
    configured = os.environ.get("CODEX_LAB_LANG", os.environ.get("CODEXUI_LANG", ""))
    current = configured or locale.getlocale()[0] or os.environ.get("LANG", "en")
    for supported in ("es", "ca"):
        if current.lower().startswith(supported):
            return supported
    return "en"


def tr(key: str, **values: Any) -> str:
    return TEXT[language()][key].format(**values)


def codex_command() -> list[str]:
    configured = os.environ.get("CODEX_LAB_CODEX_COMMAND", os.environ.get("CODEXUI_CODEX_COMMAND"))
    if configured:
        command = shlex.split(configured)
    else:
        packaged = Path("/opt/codex-id-lab-unofficial/bin/codex-cli-wrapper")
        command = [str(packaged)] if packaged.is_file() else [shutil.which("codex") or ""]
    if not command or not command[0]:
        raise RuntimeError(tr("missing_command", command="codex"))
    return command


def account_client(cancelled: Callable[[], bool] | None = None) -> AccountClient:
    selected = os.environ.get("CODEX_LAB_SHARED_APP_SERVER_SOCKET")
    if selected:
        if selected == "auto":
            root = os.environ.get("XDG_RUNTIME_DIR", "")
            if not root or not Path(root).is_absolute():
                raise RuntimeError("Shared bridge requires an absolute XDG_RUNTIME_DIR")
            selected = str(Path(root) / "codex-id-lab-unofficial/app-server-bridge/app-server.sock")
        return SharedAccountClient(selected, cancelled)
    return AccountClient(codex_command() + ["-s", "read-only", "-a", "on-request", "app-server", "--stdio"], cancelled)


def tasks_text(tasks: dict[str, Any]) -> str:
    if tasks.get("status") != "loaded-thread-snapshot":
        return tr("tasks_unavailable")
    items = tasks.get("items", [])
    return tr("tasks_snapshot", count=len(items), active=sum(item["type"] == "active" for item in items),
              attention=sum(item["needs_attention"] for item in items)) + "\n" + tr("tasks_partial")


def query_codex_account(
    timeout: float = 12.0,
    cancelled: Callable[[], bool] | None = None,
) -> dict[str, Any]:
    client = account_client(cancelled)
    generation = [0]
    def notification(method: str, params: dict[str, Any]) -> None:
        if method == "account/updated":
            generation[0] += 1
    client.notification = notification
    try:
        client.start(timeout)
        current_generation = generation[0]
        limits = client.request("account/rateLimits/read", timeout=timeout)
        try:
            usage = client.request("account/usage/read", timeout=timeout)
            usage_status = "available"
        except RuntimeError:
            if cancelled and cancelled():
                raise
            usage = {}
            usage_status = "unavailable"
        if generation[0] != current_generation:
            raise RuntimeError("Account changed during quota refresh")
        data = normalize_account_data(usage, limits)
        data["usage_status"] = usage_status
        return data
    finally:
        client.close()


def normalize_account_data(
    usage_result: dict[str, Any], limits_result: dict[str, Any]
) -> dict[str, Any]:
    snapshots = limits_result.get("rateLimitsByLimitId") or {}
    if not isinstance(snapshots, dict):
        snapshots = {}
    if not snapshots and isinstance(limits_result.get("rateLimits"), dict):
        snapshot = limits_result["rateLimits"]
        snapshots = {snapshot.get("limitId") or "codex": snapshot}

    limits: list[dict[str, Any]] = []
    ordered_snapshots = sorted(
        snapshots.items(),
        key=lambda item: (item[0] != "codex", str((item[1] if isinstance(item[1], dict) else {}).get("limitName") or item[0]).lower()),
    )
    for limit_id, snapshot in ordered_snapshots:
        if not isinstance(snapshot, dict):
            continue
        name = snapshot.get("limitName") or ("Codex" if limit_id == "codex" else limit_id)
        for kind in ("primary", "secondary"):
            window = snapshot.get(kind)
            if not isinstance(window, dict):
                continue
            used = window.get("usedPercent")
            if isinstance(used, bool) or not isinstance(used, (int, float)) or not 0 <= used <= 100 or not math.isfinite(used):
                used = None
            limits.append(
                {
                    "bucket_id": str(snapshot.get("limitId") or limit_id),
                    "name": str(name),
                    "kind": kind,
                    "used_percent": used,
                    "remaining_percent": 100 - used if used is not None else None,
                    "window_minutes": window.get("windowDurationMins"),
                    "resets_at": window.get("resetsAt"),
                    "rate_limit_reached_type": snapshot.get("rateLimitReachedType"),
                }
            )

    buckets = usage_result.get("dailyUsageBuckets") or []
    buckets = [row for row in buckets if isinstance(row, dict) and isinstance(row.get("startDate"), str)] if isinstance(buckets, list) else []
    latest = max(buckets, key=lambda row: row.get("startDate", ""), default=None)
    summary = usage_result.get("summary") or {}
    if not isinstance(summary, dict):
        summary = {}
    credits = limits_result.get("rateLimitResetCredits") or {}
    reset_credits = credits.get("availableCount") if isinstance(credits, dict) else None
    if isinstance(reset_credits, bool) or not isinstance(reset_credits, int) or reset_credits < 0:
        reset_credits = None
    return {
        "limits": limits,
        "activity": {
            "latest_date": latest.get("startDate") if latest else None,
            "latest_tokens": latest.get("tokens") if latest else None,
            "lifetime_tokens": summary.get("lifetimeTokens"),
            "current_streak_days": summary.get("currentStreakDays"),
            "longest_streak_days": summary.get("longestStreakDays"),
        },
        "reset_credits": reset_credits,
        "tasks": {"status": "desktop-provider-unavailable", "items": []},
        "updated_at": int(time.time()),
    }


def compact_number(value: Any) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or (isinstance(value, float) and not math.isfinite(value)):
        return tr("unknown")
    number = int(value)
    for threshold, suffix in ((1_000_000_000, "B"), (1_000_000, "M"), (1_000, "K")):
        if abs(number) >= threshold:
            return f"{number / threshold:.2f} {suffix}"
    return f"{number:,}"


def period_text(minutes: Any) -> str:
    if isinstance(minutes, bool) or not isinstance(minutes, (int, float)) or minutes <= 0 or (isinstance(minutes, float) and not math.isfinite(minutes)):
        return tr("unknown")
    if minutes % 1440 == 0:
        return tr("period_days", value=minutes // 1440)
    if minutes % 60 == 0:
        return tr("period_hours", value=minutes // 60)
    return tr("period_minutes", value=minutes)


def reset_text(timestamp: Any) -> str:
    if isinstance(timestamp, bool) or not isinstance(timestamp, (int, float)) or not 0 <= timestamp <= 253402300799:
        return tr("no_reset")
    try:
        rendered = datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M")
    except (OverflowError, OSError, ValueError):
        return tr("no_reset")
    return tr("resets", time=rendered)


def popup_geometry(
    available: tuple[int, int, int, int],
    requested: tuple[int, int],
    anchor: tuple[int, int] | None = None,
) -> tuple[int, int, int, int]:
    left, top, screen_width, screen_height = available
    width = min(requested[0], screen_width)
    height = min(requested[1], screen_height)
    x = anchor[0] - width // 2 if anchor else left + (screen_width - width) // 2
    y = anchor[1] - height if anchor else top + (screen_height - height) // 2
    return max(left, min(x, left + screen_width - width)), max(top, min(y, top + screen_height - height)), width, height


def account_snapshot_signature(data: dict[str, Any]) -> str:
    return json.dumps({key: value for key, value in data.items() if key != "updated_at"}, sort_keys=True)


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
    return state_home / "codex-id-lab-unofficial" / "crashes"


def local_tessdata_directory() -> Path | None:
    data_home = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    directory = data_home / "codex-id-lab-unofficial" / "tessdata"
    return directory if any(directory.glob("*.traineddata")) else None


def companion_socket_path() -> str:
    configured = Path(os.environ.get("XDG_RUNTIME_DIR", ""))
    fallback = Path(f"/run/user/{os.getuid()}")
    runtime = configured if configured.is_absolute() else fallback
    if not runtime.is_dir():
        runtime = Path.home() / ".cache"
    directory = runtime / "codex-id-lab-unofficial"
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
        choices=("tray", "panel", "usage-json", "features", "features-json", "feature-profile-json", "ocr", "qr", "crashes"),
    )
    return parser.parse_args(argv)


def run_gui(command: str) -> int:
    try:
        from PySide6.QtCore import QByteArray, QMimeData, QObject, QProcess, Qt, QThread, QTimer, QUrl, Signal, Slot
        from PySide6.QtGui import QAction, QDesktopServices, QIcon, QPalette
        from PySide6.QtNetwork import QLocalServer, QLocalSocket
        from PySide6.QtWidgets import (
            QApplication,
            QCheckBox,
            QDialog,
            QFrame,
            QGridLayout,
            QHBoxLayout,
            QLabel,
            QMenu,
            QMessageBox,
            QProgressBar,
            QScrollArea,
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
        icon = QIcon.fromTheme("codex-lab")
        if not icon.isNull():
            return icon
        packaged = Path("/usr/share/icons/hicolor/scalable/apps/codex-lab.svg")
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
        account_invalidated = Signal()

        def __init__(self) -> None:
            super().__init__()
            self.refresh_event = threading.Event()
            self.refresh_event.set()

        def request_refresh(self) -> None:
            self.refresh_event.set()

        def run(self) -> None:
            backoff = 1.0
            while not self.isInterruptionRequested():
                try:
                    client = account_client(self.isInterruptionRequested)
                except Exception as error:
                    self.failed.emit(str(error))
                    return
                state: dict[str, Any] = {"usage": {}, "limits": None, "quota_updated_at": None, "tasks": None, "generation": 0, "signature": None, "usage_status": "unavailable"}

                def publish(force: bool = False) -> None:
                    if state["limits"] is None and state["tasks"] is None:
                        return
                    data = normalize_account_data(state["usage"], state["limits"] or {})
                    data["usage_status"] = state["usage_status"]
                    data["quota_status"] = "available" if state["limits"] is not None else "unavailable"
                    data["updated_at"] = state["quota_updated_at"] or time.time()
                    if state["tasks"] is not None:
                        data["tasks"] = state["tasks"]
                    signature = account_snapshot_signature(data)
                    if force or signature != state["signature"]:
                        state["signature"] = signature
                        self.succeeded.emit(data)

                def notification(method: str, params: dict[str, Any]) -> None:
                    if method == "account/updated":
                        state.update(usage={}, limits=None, quota_updated_at=None, tasks=None, signature=None, usage_status="unavailable")
                        state["generation"] += 1
                        self.account_invalidated.emit()
                        self.refresh_event.set()
                    elif method == "account/rateLimits/updated":
                        state["limits"] = params
                        state["quota_updated_at"] = time.time()
                        publish()
                    elif method == "thread/status/changed" and state["tasks"] is not None:
                        for item in state["tasks"]["items"]:
                            if item["id"] == params.get("threadId"):
                                try:
                                    item.update(task_status(params.get("status")))
                                except RuntimeError:
                                    state["tasks"] = None
                                    self.refresh_event.set()
                                publish()
                                break

                client.notification = notification
                try:
                    client.start()
                    next_refresh = time.monotonic()
                    next_tasks = time.monotonic()
                    while not self.isInterruptionRequested():
                        if isinstance(client, SharedAccountClient) and time.monotonic() >= next_tasks:
                            try:
                                state["tasks"] = read_loaded_tasks(client)
                            except RuntimeError:
                                state["tasks"] = None
                            publish()
                            next_tasks = time.monotonic() + 10 * random.uniform(0.9, 1.1)
                        if self.refresh_event.is_set() or time.monotonic() >= next_refresh:
                            self.refresh_event.clear()
                            generation = state["generation"]
                            limits = client.request("account/rateLimits/read")
                            if generation != state["generation"]:
                                self.refresh_event.set()
                                continue
                            state["limits"] = limits
                            state["quota_updated_at"] = time.time()
                            publish(force=True)
                            backoff = 1.0
                            try:
                                usage = client.request("account/usage/read")
                                usage_status = "available"
                            except RuntimeError:
                                if self.isInterruptionRequested():
                                    raise
                                usage = {}
                                usage_status = "unavailable"
                            if generation != state["generation"]:
                                self.refresh_event.set()
                                continue
                            state.update(usage=usage, usage_status=usage_status)
                            publish()
                            next_refresh = time.monotonic() + 300 * random.uniform(0.9, 1.1)
                        client.read_messages(0.25)
                except Exception as error:  # noqa: BLE001 - bounded reconnection; no auth prompts
                    if not self.isInterruptionRequested():
                        self.failed.emit(str(error))
                        next_attempt = time.monotonic() + backoff * random.uniform(0.9, 1.1)
                        while not self.isInterruptionRequested() and time.monotonic() < next_attempt:
                            if self.refresh_event.wait(0.25):
                                self.refresh_event.clear()
                                break
                        backoff = min(backoff * 2, 300)
                finally:
                    client.close()

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
            self.setObjectName("usagePanel")
            self.setWindowIcon(app_icon())
            self.setMinimumSize(360, 420)
            self.resize(400, 480)

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

            outer_root = root
            body = QWidget()
            root = QVBoxLayout(body)
            root.setContentsMargins(0, 0, 0, 0)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll.setFrameShape(QFrame.NoFrame)
            scroll.setWidget(body)
            outer_root.addWidget(scroll)

            self.status = QLabel(tr("loading"))
            self.status.setObjectName("usageStatus")
            self.status.setWordWrap(True)
            root.addWidget(self.status)
            self.tasks_status = QLabel(tr("tasks_unavailable"))
            self.tasks_status.setObjectName("taskProviderStatus")
            self.tasks_status.setWordWrap(True)
            root.addWidget(self.tasks_status)

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
            footer.addStretch()
            open_button = QPushButton(QIcon.fromTheme("codex-lab"), tr("open_codex"))
            open_button.clicked.connect(lambda: QProcess.startDetached("codex-lab", []))
            footer.addWidget(open_button)
            close_button = QPushButton(tr("close"))
            close_button.clicked.connect(self.hide)
            footer.addWidget(close_button)
            outer_root.addLayout(footer)
            outer_root.addWidget(self.brand, alignment=Qt.AlignHCenter)

        def set_loading(self) -> None:
            self.refresh_button.setEnabled(False)
            self.status.setText(tr("loading"))

        def set_error(self, message: str) -> None:
            self.refresh_button.setEnabled(True)
            self.status.setText(f"{tr('error')}: {message}")

        def set_data(self, data: dict[str, Any]) -> None:
            self.refresh_button.setEnabled(True)
            self.status.setText(tr("unknown") if data.get("quota_status") == "unavailable" else
                                tr("updated", time=datetime.fromtimestamp(data["updated_at"]).strftime("%H:%M")))
            self.tasks_status.setText(tasks_text(data.get("tasks", {})))
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
                name.setWordWrap(True)
                remaining = limit["remaining_percent"]
                value = QLabel(tr("remaining", value=f"{remaining:.1f}".rstrip("0").rstrip(".")) if remaining is not None else tr("unknown"))
                value.setObjectName("quotaRemaining")
                value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                bar = QProgressBar()
                bar.setRange(0, 100)
                bar.setValue(round(remaining) if remaining is not None else 0)
                bar.setVisible(remaining is not None)
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
                (tr("current_streak"), tr("days", value=activity["current_streak_days"]) if activity["current_streak_days"] is not None else tr("unknown")),
                (tr("longest_streak"), tr("days", value=activity["longest_streak_days"]) if activity["longest_streak_days"] is not None else tr("unknown")),
                (tr("reset_credits"), str(data["reset_credits"]) if data["reset_credits"] is not None else tr("unknown")),
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
            self.cache = AccountCache()
            self.task_attention = TaskAttention()
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
                ("features", tr("features_title"), "preferences-system"),
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
            self.tray_available = QSystemTrayIcon.isSystemTrayAvailable()
            if self.tray_available:
                self.tray.show()

            self.crash_watcher = CrashWatcher()
            self.crash_watcher.crash_detected.connect(self.record_crash)
            if not (os.environ.get("CODEX_LAB_TEST_MODE") == "1" and os.environ.get("CODEX_LAB_TEST_DISABLE_CRASH_WATCHER") == "1"):
                self.crash_watcher.start()
            app.aboutToQuit.connect(self.shutdown)
            self.refresh(force=False)

        @Slot()
        def accept_connection(self) -> None:
            while self.server.hasPendingConnections():
                socket = self.server.nextPendingConnection()
                socket.readyRead.connect(lambda current=socket: self.read_socket(current))
                if socket.bytesAvailable():
                    self.read_socket(socket)

        def read_socket(self, socket: QLocalSocket) -> None:
            buffer = bytes(socket.property("commandBuffer") or QByteArray()) + bytes(socket.readAll())
            if len(buffer) > 64:
                socket.disconnectFromServer()
                return
            socket.setProperty("commandBuffer", QByteArray(buffer))
            if b"\n" not in buffer:
                return
            action = buffer.partition(b"\n")[0].decode(errors="replace").strip()
            if action in {"panel", "features", "ocr", "qr", "crashes"}:
                self.dispatch(action)
            socket.disconnectFromServer()

        @Slot(QSystemTrayIcon.ActivationReason)
        def tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
            if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
                if self.dialog.isVisible():
                    self.dialog.hide()
                else:
                    self.dispatch("panel")

        def dispatch(self, action: str) -> None:
            if action == "panel":
                if not self.dialog.isVisible():
                    tray_rect = self.tray.geometry()
                    screen = QApplication.screenAt(tray_rect.center()) if tray_rect.isValid() else QApplication.primaryScreen()
                    if screen is not None:
                        available = screen.availableGeometry()
                        anchor = (tray_rect.center().x(), tray_rect.top()) if tray_rect.isValid() else None
                        x, y, width, height = popup_geometry(
                            (available.x(), available.y(), available.width(), available.height()),
                            (400, 480), anchor,
                        )
                        self.dialog.resize(width, height)
                        self.dialog.move(x, y)  # A hint only; Wayland may ignore positioning.
                self.dialog.show()
                self.dialog.raise_()
                self.dialog.activateWindow()
                self.refresh(force=False)
            elif action == "features":
                self.show_features()
            elif action == "ocr":
                QTimer.singleShot(0, lambda: self.capture("ocr"))
            elif action == "qr":
                QTimer.singleShot(0, lambda: self.capture("qr"))
            elif action == "crashes":
                self.open_crash_directory()

        def show_features(self) -> None:
            from codex_lab_features import feature_states, save_preferences
            try:
                states = feature_states()
            except (OSError, ValueError, KeyError) as error:
                QMessageBox.warning(self.dialog, APP_NAME, str(error))
                return
            self.feature_dialog = QDialog()
            self.feature_dialog.setObjectName("featureSelector")
            self.feature_dialog.setWindowTitle(tr("features_title"))
            self.feature_dialog.resize(400, 420)
            layout = QVBoxLayout(self.feature_dialog)
            hint = QLabel(tr("features_hint")); hint.setWordWrap(True); layout.addWidget(hint)
            checks = []
            for state in states:
                checkbox = QCheckBox(f"{state['title']} — {tr('feature_' + state['state'])}")
                checkbox.setObjectName("feature_" + state["id"])
                checkbox.setChecked(state["requested"])
                checkbox.setEnabled(not state["blocker"] or state["requested"])
                checkbox.setToolTip(state["blocker"] or state["stability"])
                layout.addWidget(checkbox)
                checks.append((state["id"], checkbox))
            layout.addStretch()
            save = QPushButton(tr("features_save"))
            def save_selected() -> None:
                try:
                    save_preferences([identifier for identifier, checkbox in checks if checkbox.isChecked()])
                except (OSError, ValueError) as error:
                    QMessageBox.warning(self.feature_dialog, APP_NAME, str(error))
                    return
                hint.setText(tr("features_saved"))
            save.clicked.connect(save_selected); layout.addWidget(save)
            self.feature_dialog.show()

        @Slot()
        def refresh(self, force: bool = True) -> None:
            if not force and not self.cache.needs_refresh() and self.cache.data is not None:
                self.dialog.set_data(self.cache.data)
                return
            self.dialog.set_loading()
            if self.worker and self.worker.isRunning():
                self.worker.request_refresh()
                return
            self.worker = UsageWorker()
            self.worker.succeeded.connect(self.set_data)
            self.worker.failed.connect(self.set_error)
            self.worker.account_invalidated.connect(self.invalidate_account)
            self.worker.finished.connect(self.usage_finished)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.start()

        def set_data(self, data: dict[str, Any]) -> None:
            age = max(0, time.time() - data["updated_at"])
            self.cache.update(data, now=time.monotonic() - age)
            if data.get("quota_status") == "unavailable":
                self.cache.failed()
            self.dialog.set_data(data)
            needed = self.task_attention.update(data.get("tasks", {}))
            if needed and self.tray_available and os.environ.get("CODEX_LAB_TASK_NOTIFICATIONS") == "1":
                self.notification_opens_report = False
                self.tray.showMessage(tr("tasks_attention_title"), tr("tasks_attention_body", count=needed), QSystemTrayIcon.Information)

        def set_error(self, message: str) -> None:
            self.cache.failed()
            if self.cache.data is not None:
                age = max(0, round((time.time() - self.cache.data["updated_at"]) / 60))
                message = f"{message} · {tr('stale', minutes=age)}"
            self.dialog.set_error(message)

        def invalidate_account(self) -> None:
            self.cache.account_changed()
            self.task_attention = TaskAttention()
            self.dialog.set_data(normalize_account_data({}, {}))
            self.dialog.status.setText(tr("account_changed"))

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
            with tempfile.TemporaryDirectory(prefix="codex-lab-capture-") as directory:
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
                languages = os.environ.get("CODEX_LAB_OCR_LANGUAGES", os.environ.get("CODEXUI_OCR_LANGUAGES", "spa+eng"))
                requested = [item for item in languages.split("+") if item]
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
                self.worker.request_refresh()
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
    QTimer.singleShot(0, lambda: controller.dispatch(command if command != "tray" else "panel") if command != "tray" or not controller.tray_available else None)
    if os.environ.get("CODEX_LAB_TEST_MODE") == "1" and os.environ.get("CODEX_LAB_TEST_FEATURE_REPORT") == "1":
        def report_features() -> None:
            dialog = controller.feature_dialog
            print(json.dumps({"visible": dialog.isVisible(), "locale": language(), "title": dialog.windowTitle(), "features": [{"name": checkbox.objectName(), "enabled": checkbox.isEnabled(), "checked": checkbox.isChecked()} for checkbox in dialog.findChildren(QCheckBox)]}, ensure_ascii=False), flush=True)
            if os.environ.get("CODEX_LAB_TEST_GUI_IMAGE"):
                dialog.grab().save(os.environ["CODEX_LAB_TEST_GUI_IMAGE"])
        QTimer.singleShot(300, report_features)
    if os.environ.get("CODEX_LAB_TEST_MODE") == "1" and os.environ.get("CODEX_LAB_TEST_GUI_REPORT") == "1":
        def report_gui() -> None:
            print(json.dumps({
                "locale": language(),
                "visible": controller.dialog.isVisible(),
                "width": controller.dialog.width(),
                "remaining": [label.text() for label in controller.dialog.findChildren(QLabel, "quotaRemaining")],
                "tasks": controller.dialog.tasks_status.text(),
                "tray_available": controller.tray_available,
                "popup_backend": "compatible-dialog",
                "palette": {
                    "window": app.palette().color(QPalette.Window).name(),
                    "text": app.palette().color(QPalette.WindowText).name(),
                },
            }, ensure_ascii=False), flush=True)
            image_path = os.environ.get("CODEX_LAB_TEST_GUI_IMAGE")
            if image_path:
                controller.dialog.grab().save(image_path)
        QTimer.singleShot(300, report_gui)
    test_quit_ms = int(os.environ.get("CODEX_LAB_TEST_QUIT_MS", os.environ.get("CODEXUI_TEST_QUIT_MS", "0")))
    if test_quit_ms > 0:
        QTimer.singleShot(test_quit_ms, app.quit)
    return app.exec()


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    if args.command == "usage-json":
        print(json.dumps(query_codex_account(), ensure_ascii=False, indent=2))
        return 0
    if args.command == "features-json":
        from codex_lab_features import feature_states
        print(json.dumps(feature_states(), ensure_ascii=False, indent=2))
        return 0
    if args.command == "feature-profile-json":
        from codex_lab_features import build_profile
        print(json.dumps(build_profile(), ensure_ascii=False, indent=2))
        return 0
    return run_gui(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
