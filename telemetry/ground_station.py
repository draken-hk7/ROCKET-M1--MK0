"""Dash/Plotly ground station for ROCKET M1-MK0 telemetry."""

from __future__ import annotations

import argparse
import csv
import sys
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT / "firmware" / "src" / "telemetry") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "firmware" / "src" / "telemetry"))

from packet_decoder import decode_packet


LOG_DIR = PROJECT_ROOT / "telemetry" / "logs"
PHI = 1.6180339887
LEFT_COLUMN = 61.8
RIGHT_COLUMN = 38.2
ACCENT_HUES = (0.0, 137.5, 275.0)


def open_session_log() -> tuple[Path, csv.DictWriter[str], Any]:
    """Open a timestamped telemetry session log."""

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    path = LOG_DIR / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    handle = path.open("w", newline="", encoding="utf-8")
    fieldnames = [
        "timestamp_ms",
        "state_name",
        "altitude_m",
        "velocity_ms",
        "accel_z_ms2",
        "temp_c",
        "latitude",
        "longitude",
        "battery_v",
        "crc_valid",
    ]
    writer: csv.DictWriter[str] = csv.DictWriter(handle, fieldnames=fieldnames)
    writer.writeheader()
    print(f"Saved: {path}")
    return path, writer, handle


def run_dashboard(port: str | None = None, baud: int = 115200) -> None:
    """Run the live dashboard at http://localhost:8050."""

    try:
        import dash
        import plotly.graph_objects as go
        import serial
        from dash import Input, Output, dcc, html
    except ImportError as exc:
        raise SystemExit(
            "Dash ground station requires dash, plotly, and pyserial. "
            "Install with: pip install dash plotly pyserial"
        ) from exc

    packets: deque[dict[str, Any]] = deque(maxlen=600)
    raw_rows: deque[dict[str, Any]] = deque(maxlen=10)
    _, writer, handle = open_session_log()
    serial_port = serial.Serial(port, baud, timeout=0.01) if port else None

    app = dash.Dash(__name__)
    app.layout = html.Div(
        style={"fontFamily": "Arial", "padding": "18px", "background": "#f8fafc"},
        children=[
            html.H1("ROCKET M1-MK0 GROUND STATION"),
            html.Div(id="state-badge", style={"fontWeight": "bold", "padding": "8px"}),
            html.Div(
                style={"display": "grid", "gridTemplateColumns": f"{LEFT_COLUMN}% {RIGHT_COLUMN}%", "gap": "14px"},
                children=[
                    dcc.Graph(id="altitude-plot"),
                    dcc.Graph(id="velocity-plot"),
                    dcc.Graph(id="accel-plot"),
                    dcc.Graph(id="gps-map"),
                    html.Div(id="health-row"),
                    html.Div(id="raw-table"),
                ],
            ),
            html.Div([html.Button("Arm Simulation", id="arm-button"), html.Button("Reset View", id="reset-button")]),
            dcc.Interval(id="tick", interval=500, n_intervals=0),
        ],
    )

    def poll_serial() -> None:
        if serial_port is None:
            return
        while serial_port.in_waiting >= 32:
            decoded = decode_packet(serial_port.read(32))
            packets.append(decoded)
            raw_rows.append(decoded)
            writer.writerow({key: decoded.get(key) for key in writer.fieldnames or []})
            handle.flush()

    @app.callback(
        Output("state-badge", "children"),
        Output("altitude-plot", "figure"),
        Output("velocity-plot", "figure"),
        Output("accel-plot", "figure"),
        Output("gps-map", "figure"),
        Output("health-row", "children"),
        Output("raw-table", "children"),
        Input("tick", "n_intervals"),
    )
    def update(_: int) -> tuple[Any, Any, Any, Any, Any, Any, Any]:
        poll_serial()
        data = list(packets)
        if not data:
            data = [
                {
                    "timestamp_ms": 0,
                    "state_name": "IDLE",
                    "altitude_m": 0,
                    "velocity_ms": 0,
                    "accel_z_ms2": 0,
                    "latitude": 0,
                    "longitude": 0,
                    "battery_v": 0,
                    "temp_c": 0,
                    "crc_valid": True,
                }
            ]
        times = [(row["timestamp_ms"] - data[0]["timestamp_ms"]) / 1000.0 for row in data]
        altitude_fig = go.Figure(data=[go.Scatter(x=times, y=[r["altitude_m"] for r in data], mode="lines")])
        altitude_fig.update_layout(title="Altitude, last 60 s", xaxis_title="s", yaxis_title="m")
        velocity_fig = go.Figure(data=[go.Scatter(x=times, y=[r["velocity_ms"] for r in data], mode="lines", line={"color": f"hsl({ACCENT_HUES[1]},60%,42%)"})])
        velocity_fig.update_layout(title="Velocity", xaxis_title="s", yaxis_title="m/s")
        accel_fig = go.Figure(data=[go.Scatter(x=times, y=[r["accel_z_ms2"] for r in data], mode="lines")])
        accel_fig.update_layout(title="Acceleration Z", xaxis_title="s", yaxis_title="m/s^2")
        gps_fig = go.Figure(data=[go.Scattermapbox(lat=[r["latitude"] for r in data], lon=[r["longitude"] for r in data], mode="markers")])
        gps_fig.update_layout(title="GPS Map", mapbox={"style": "open-street-map", "zoom": 2})
        latest = data[-1]
        health = f"Battery {latest['battery_v']:.2f} V | Temp {latest.get('temp_c', 0):.1f} C | Packets {len(data)}"
        table = html.Table([html.Tr([html.Th("Time"), html.Th("State"), html.Th("Alt m"), html.Th("CRC")])] + [
            html.Tr([html.Td(row["timestamp_ms"]), html.Td(row["state_name"]), html.Td(f"{row['altitude_m']:.1f}"), html.Td(str(row["crc_valid"]))])
            for row in raw_rows
        ])
        return latest["state_name"], altitude_fig, velocity_fig, accel_fig, gps_fig, health, table

    app.run(debug=False, host="127.0.0.1", port=8050)


def main() -> None:
    """Parse CLI args and start dashboard."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=None, help="Serial port such as COM5")
    parser.add_argument("--baud", default=115200, type=int)
    args = parser.parse_args()
    run_dashboard(args.port, args.baud)


if __name__ == "__main__":
    main()
