"""Host-side tests for firmware telemetry logic."""

from __future__ import annotations

import sys
from pathlib import Path

TELEMETRY_PATH = Path(__file__).resolve().parents[1] / "firmware" / "src" / "telemetry"
sys.path.insert(0, str(TELEMETRY_PATH))

from packet_decoder import FlightState, crc16_ccitt, decode_packet, encode_packet, next_state, phi_filter


def test_crc16_known_vector() -> None:
    """CRC-16/CCITT known vector."""

    assert crc16_ccitt(b"123456789") == 0x29B1


def test_packet_encode_decode_roundtrip() -> None:
    """Telemetry packet should round-trip with valid CRC."""

    packet = encode_packet(
        {
            "flight_state": FlightState.COAST,
            "altitude_m": 123.4,
            "velocity_ms": 12.34,
            "accel_z_ms2": 9.81,
            "temp_c": 24.5,
            "latitude": 12.5,
            "longitude": 77.6,
            "battery_v": 7.4,
            "timestamp_ms": 100,
            "loop_count": 5,
        }
    )
    decoded = decode_packet(packet)
    assert decoded["crc_valid"]
    assert decoded["state_name"] == "COAST"
    assert abs(decoded["altitude_m"] - 123.4) < 0.1


def test_state_machine_transitions() -> None:
    """Host transition helper should follow the firmware path."""

    state = next_state(FlightState.IDLE, 0.0, 0.0, 0.0, True)
    assert state == FlightState.ARMED
    state = next_state(state, 25.0, 0.0, 0.0, True)
    assert state == FlightState.BOOST_DETECT
    state = next_state(state, 9.81, 0.0, 50.0, True)
    assert state == FlightState.COAST


def test_phi_filter_convergence() -> None:
    """Phi filter should converge to a constant signal."""

    value = 0.0
    for _ in range(1000):
        value = phi_filter(1.0, value)
    assert abs(value - 1.0) < 1e-6
