"""Ground-side decoder for ROCKET M1-MK0 LoRa telemetry packets."""

from __future__ import annotations

import struct
from enum import IntEnum
from typing import Any


class FlightState(IntEnum):
    """Flight state enumeration shared with firmware."""

    IDLE = 0
    ARMED = 1
    BOOST_DETECT = 2
    COAST = 3
    APOGEE_DETECT = 4
    DROGUE_DEPLOY = 5
    MAIN_DEPLOY = 6
    DESCENT = 7
    LANDED = 8
    SAFE = 9


PACKET_STRUCT = struct.Struct("<BBHhhhffHIIHH")
PACKET_SIZE_BYTES = 32


def crc16_ccitt(data: bytes, initial: int = 0xFFFF) -> int:
    """Compute CRC-16/CCITT checksum.

    Args:
        data: Byte sequence to check.
        initial: Initial CRC register value.

    Returns:
        Unsigned 16-bit checksum.

    Units:
        Bytes and dimensionless checksum.

    Aerospace Application:
        Protects compact flight telemetry packets against link corruption.
    """

    crc = initial
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def encode_packet(fields: dict[str, Any]) -> bytes:
    """Encode a telemetry packet for tests and replay.

    Args:
        fields: Packet fields using engineering units.

    Returns:
        32-byte packet.

    Units:
        Altitude in meters, velocity in m/s, acceleration in m/s^2.

    Aerospace Application:
        Enables deterministic host-side validation of the telemetry protocol.
    """

    values = [
        int(fields.get("packet_id", 0x42)),
        int(fields.get("flight_state", FlightState.IDLE)),
        int(round(float(fields.get("altitude_m", 0.0)) * 10.0)),
        int(round(float(fields.get("velocity_ms", 0.0)) * 100.0)),
        int(round(float(fields.get("accel_z_ms2", 0.0)) * 100.0)),
        int(round(float(fields.get("temp_c", 0.0)) * 10.0)),
        float(fields.get("latitude", 0.0)),
        float(fields.get("longitude", 0.0)),
        int(round(float(fields.get("battery_v", 0.0)) * 1000.0)),
        int(fields.get("timestamp_ms", 0)),
        int(fields.get("loop_count", 0)),
        0,
        int(fields.get("reserved", 0)),
    ]
    packet_without_crc = bytearray(PACKET_STRUCT.pack(*values))
    checksum = crc16_ccitt(bytes(packet_without_crc[:28]))
    struct.pack_into("<H", packet_without_crc, 28, checksum)
    return bytes(packet_without_crc)


def decode_packet(packet: bytes) -> dict[str, Any]:
    """Decode one 32-byte telemetry packet.

    Args:
        packet: Raw packet bytes.

    Returns:
        Human-readable fields with units and CRC validity.

    Units:
        Altitude in meters, velocity in m/s, acceleration in m/s^2.

    Aerospace Application:
        Ground-station parser for compact LoRa telemetry.
    """

    if len(packet) != PACKET_SIZE_BYTES:
        raise ValueError(f"Expected {PACKET_SIZE_BYTES} bytes, received {len(packet)} bytes.")
    unpacked = PACKET_STRUCT.unpack(packet)
    (
        packet_id,
        flight_state,
        altitude_dm,
        velocity_cms,
        accel_z_cms2,
        temp_dc,
        latitude,
        longitude,
        battery_mv,
        timestamp_ms,
        loop_count,
        checksum_crc16,
        reserved,
    ) = unpacked
    computed_crc = crc16_ccitt(packet[:28])
    state_name = FlightState(flight_state).name if flight_state in FlightState._value2member_map_ else "UNKNOWN"
    return {
        "packet_id": packet_id,
        "flight_state": flight_state,
        "state_name": state_name,
        "altitude_m": altitude_dm / 10.0,
        "velocity_ms": velocity_cms / 100.0,
        "accel_z_ms2": accel_z_cms2 / 100.0,
        "temp_c": temp_dc / 10.0,
        "latitude": latitude,
        "longitude": longitude,
        "battery_v": battery_mv / 1000.0,
        "timestamp_ms": timestamp_ms,
        "loop_count": loop_count,
        "checksum_crc16": checksum_crc16,
        "computed_crc16": computed_crc,
        "crc_valid": checksum_crc16 == computed_crc,
        "reserved": reserved,
    }


def phi_filter(new_val: float, prev_val: float) -> float:
    """Apply Fibonacci complementary filter.

    Args:
        new_val: New sensor value in arbitrary engineering units.
        prev_val: Previous filtered value in the same units.

    Returns:
        Filtered value.

    Units:
        Same units as the input signal.

    Aerospace Application:
        Matches firmware phi-weighted sensor fusion for host-side tests.
    """

    phi = 1.6180339887
    return (new_val / (phi * phi)) + (prev_val / phi)


def next_state(state: FlightState, accel_z_ms2: float, altitude_delta_m: float, altitude_agl_m: float, armed: bool) -> FlightState:
    """Host-side state transition helper for tests.

    Args:
        state: Current flight state.
        accel_z_ms2: Z acceleration in meters per second squared.
        altitude_delta_m: Change in altitude since previous sample in meters.
        altitude_agl_m: Current altitude above ground in meters.
        armed: Arm-switch state.

    Returns:
        Next flight state.

    Units:
        SI units.

    Aerospace Application:
        Validates firmware state logic without connecting hardware.
    """

    if state == FlightState.IDLE and armed:
        return FlightState.ARMED
    if state == FlightState.ARMED and accel_z_ms2 > 2.5 * 9.80665:
        return FlightState.BOOST_DETECT
    if state == FlightState.BOOST_DETECT and accel_z_ms2 < 11.0:
        return FlightState.COAST
    if state == FlightState.COAST and altitude_delta_m < -0.5:
        return FlightState.APOGEE_DETECT
    if state == FlightState.APOGEE_DETECT:
        return FlightState.DROGUE_DEPLOY
    if state == FlightState.DROGUE_DEPLOY and altitude_agl_m < 150.0:
        return FlightState.MAIN_DEPLOY
    if state == FlightState.MAIN_DEPLOY and altitude_agl_m < 3.0:
        return FlightState.LANDED
    if state == FlightState.LANDED and not armed:
        return FlightState.SAFE
    return state


def format_packet_table(decoded: dict[str, Any]) -> str:
    """Format a decoded packet as a compact text table."""

    rows = [
        ("state", decoded["state_name"]),
        ("altitude_m", f"{decoded['altitude_m']:.1f}"),
        ("velocity_ms", f"{decoded['velocity_ms']:.2f}"),
        ("accel_z_ms2", f"{decoded['accel_z_ms2']:.2f}"),
        ("battery_v", f"{decoded['battery_v']:.2f}"),
        ("crc_valid", str(decoded["crc_valid"])),
    ]
    return "\n".join(f"{key:14s} | {value}" for key, value in rows)


if __name__ == "__main__":
    sample = encode_packet(
        {
            "flight_state": FlightState.COAST,
            "altitude_m": 123.4,
            "velocity_ms": 42.25,
            "accel_z_ms2": 9.81,
            "temp_c": 27.5,
            "battery_v": 7.8,
            "timestamp_ms": 1000,
            "loop_count": 100,
        }
    )
    print(format_packet_table(decode_packet(sample)))
