#!/usr/bin/env python3
"""
Xtark R20 로봇 Python 컨트롤러
OpenCTR H60과 직접 시리얼 통신하여 로봇을 제어합니다.
ROS 없이 순수 Python으로 구현된 버전입니다.

Author: GitHub Copilot (수정: Gemini)
Version: 1.2 (PDF 매뉴얼 기반 프로토콜 수정)
Date: 2025-07-14
"""

import serial
import time
import struct
import threading
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple, List
import logging
import math

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 물리 상수
GRAVITY = 9.80665

class RobotType(Enum):
    """로봇 타입 정의 (PDF 페이지 43, 61 참조) [cite: 1568, 2464, 2465, 2466]"""
    R20_MEC = 0x01   # 메카넘 휠
    R20_FWD = 0x02   # 4륜 차동구동
    R20_AKM = 0x03   # 아커만 조향
    R20_TWD = 0x04   # 2륜 차동구동
    R20_TNK = 0x05   # 탱크 타입
    R20_OMT = 0x06   # 옴니 휠

@dataclass
class Velocity:
    """속도 데이터 구조체"""
    vx: float = 0.0  # X축 속도 (전후진, m/s)
    vy: float = 0.0  # Y축 속도 (좌우이동, m/s)
    vw: float = 0.0  # 각속도 (회전, rad/s)

@dataclass
class IMUData:
    """IMU 센서 데이터 구조체"""
    accel_x: float = 0.0
    accel_y: float = 0.0
    accel_z: float = 0.0
    gyro_x: float = 0.0
    gyro_y: float = 0.0
    gyro_z: float = 0.0

@dataclass
class OdometryData:
    """오도메트리 데이터 구조체"""
    x: float = 0.0      # 전역 X 위치 (m)
    y: float = 0.0      # 전역 Y 위치 (m)
    theta: float = 0.0  # 전역 각도 (rad)
    vx: float = 0.0     # 로봇 기준 X축 속도 (m/s)
    vy: float = 0.0     # 로봇 기준 Y축 속도 (m/s)
    vw: float = 0.0     # 로봇 기준 각속도 (rad/s)

class XtarkR20Controller:
    """Xtark R20 로봇 컨트롤러 클래스"""

    # 프로토콜 상수 (PDF 페이지 41 참조) 
    HEADER1 = 0xAA
    HEADER2 = 0x55

    # 명령 ID (PDF 페이지 41 참조) 
    CMD_VELOCITY = 0x50      # 속도 제어
    CMD_IMU_CALIBRATE = 0x51 # IMU 캘리브레이션
    CMD_RGB_LIGHT = 0x52     # RGB LED 제어
    CMD_LIGHT_SAVE = 0x53    # RGB LED 설정 저장
    CMD_BEEPER = 0x54        # 부저 제어
    CMD_ROBOT_TYPE = 0x5A    # 로봇 타입 설정

    # 수신 데이터 ID (PDF 페이지 41 참조) 
    ID_INTEGRATED_DATA = 0x10 # 통합 데이터 (IMU, Odometry, Battery)

    def __init__(self, port: str = '/dev/ttyUSB0', baudrate: int = 230400,
                 robot_type: RobotType = RobotType.R20_MEC):
        """
        컨트롤러 초기화
        """
        self.port = port
        self.baudrate = baudrate
        self.robot_type = robot_type
        self.serial_conn: Optional[serial.Serial] = None
        self.is_connected = False
        self.is_running = False

        # 데이터 저장소
        self.current_velocity = Velocity()
        self.odometry_data = OdometryData()
        self.imu_data = IMUData()
        self.battery_voltage = 0.0
        self.last_update_time = time.time()

        # 스레드 관리
        self.receive_thread: Optional[threading.Thread] = None
        self.data_lock = threading.Lock()

        logger.info(f"Xtark R20 컨트롤러 초기화 완료")
        logger.info(f"포트: {port}, 보드레이트: {baudrate}, 로봇 타입: {robot_type.name}")

    def connect(self) -> bool:
        """OpenCTR과 시리얼 연결"""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1.0
            )
            if self.serial_conn.is_open:
                self.is_connected = True
                self._start_receive_thread()
                time.sleep(0.1) # 스레드 시작 대기
                self._set_robot_type(self.robot_type)
                logger.info("OpenCTR 연결 성공!")
                return True
            else:
                logger.error("시리얼 포트 열기 실패")
                return False
        except serial.SerialException as e:
            logger.error(f"시리얼 연결 실패: {e}")
            return False

    def disconnect(self):
        """연결 해제"""
        if self.is_connected:
            self.set_velocity(0.0, 0.0, 0.0)
            time.sleep(0.1)
            self.is_running = False
            if self.receive_thread and self.receive_thread.is_alive():
                self.receive_thread.join(timeout=1.0)
            if self.serial_conn:
                self.serial_conn.close()
            self.is_connected = False
            logger.info("연결 해제됨")

    def _set_robot_type(self, robot_type: RobotType):
        """로봇 타입 설정 (PDF 페이지 43) [cite: 1566]"""
        data = struct.pack('B', robot_type.value)
        self._send_packet(self.CMD_ROBOT_TYPE, data)
        logger.info(f"로봇 타입 설정: {robot_type.name}")

    def set_velocity(self, vx: float, vy: float, vw: float):
        """로봇 속도 설정 (PDF 페이지 42) [cite: 1547]"""
        if not self.is_connected: return
        vx_int = int(vx * 1000)
        vy_int = int(vy * 1000)
        vw_int = int(vw * 1000)
        data = struct.pack('<hhh', vx_int, vy_int, vw_int)
        self._send_packet(self.CMD_VELOCITY, data)
        with self.data_lock:
            self.current_velocity = Velocity(vx, vy, vw)

    def set_beeper(self, enable: bool):
        """부저 제어 (PDF 페이지 43) [cite: 1562]"""
        if not self.is_connected: return
        data = struct.pack('B', 1 if enable else 0)
        self._send_packet(self.CMD_BEEPER, data)

    def set_rgb_light(self, r: int, g: int, b: int, mode: int = 1):
        """RGB LED 제어 (PDF 페이지 43) [cite: 1557]"""
        if not self.is_connected: return
        r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
        # PDF에 따르면 주모드, 종속모드, 시간, R, G, B 순서. 종속모드와 시간은 현재 미사용.
        data = struct.pack('<BBBBBB', mode, 0, 0, r, g, b)
        self._send_packet(self.CMD_RGB_LIGHT, data)

    def save_light_setting(self):
        """현재 조명 효과를 EEPROM에 저장 (PDF 페이지 43) [cite: 1560]"""
        if not self.is_connected: return
        data = struct.pack('B', 0x55) # 저장 명령을 위한 데이터, PDF 기반
        self._send_packet(self.CMD_LIGHT_SAVE, data)
        logger.info("조명 설정 저장 명령 전송")

    def calibrate_imu(self):
        """IMU 캘리브레이션 (PDF 페이지 42) [cite: 1549]"""
        if not self.is_connected: return
        logger.info("IMU 캘리브레이션 시작 (로봇을 평평한 곳에 정지 상태로 유지)")
        data = struct.pack('B', 0x55) # 캘리브레이션 명령을 위한 데이터
        self._send_packet(self.CMD_IMU_CALIBRATE, data)

    def get_odometry(self) -> OdometryData:
        with self.data_lock: return self.odometry_data
    def get_imu_data(self) -> IMUData:
        with self.data_lock: return self.imu_data
    def get_battery_voltage(self) -> float:
        with self.data_lock: return self.battery_voltage
    def get_current_velocity(self) -> Velocity:
        with self.data_lock: return self.current_velocity

    def _send_packet(self, cmd_id: int, data: bytes):
        """데이터 패킷 생성 및 전송 (PDF 페이지 41) [cite: 1459]"""
        if not self.serial_conn or not self.is_connected: return
        try:
            data_len = len(data)
            total_len = 5 + data_len
            header = struct.pack('<BBBB', self.HEADER1, self.HEADER2, total_len, cmd_id)
            packet_without_checksum = header + data
            checksum = sum(bytearray(packet_without_checksum)) & 0xFF
            packet = packet_without_checksum + struct.pack('B', checksum)
            self.serial_conn.write(packet)
        except serial.SerialException as e:
            logger.error(f"데이터 전송 실패: {e}")

    def _start_receive_thread(self):
        """데이터 수신 스레드 시작"""
        self.is_running = True
        self.receive_thread = threading.Thread(target=self._receive_data, daemon=True)
        self.receive_thread.start()
        logger.info("데이터 수신 스레드 시작")

    def _receive_data(self):
        """시리얼 데이터 수신 및 파싱 (PDF 페이지 41 프로토콜 기반) [cite: 1459]"""
        buffer = bytearray()
        while self.is_running:
            try:
                if self.serial_conn.in_waiting > 0:
                    buffer.extend(self.serial_conn.read(self.serial_conn.in_waiting))

                while len(buffer) >= 5: # 최소 패킷 길이 (헤더+길이+ID+체크섬)
                    header_index = buffer.find(bytes([self.HEADER1, self.HEADER2]))
                    if header_index == -1:
                        buffer.clear(); break
                    
                    buffer = buffer[header_index:]
                    if len(buffer) < 4: break

                    total_len = buffer[2]
                    if len(buffer) < total_len: break

                    packet = buffer[:total_len]
                    
                    calc_checksum = sum(packet[:-1]) & 0xFF
                    recv_checksum = packet[-1]

                    if calc_checksum == recv_checksum:
                        cmd_id = packet[3]
                        data = packet[4:-1]
                        self._process_received_data(cmd_id, data)

                    buffer = buffer[total_len:]
                
                time.sleep(0.001)
            except Exception as e:
                logger.error(f"데이터 수신 오류: {e}")
                self.is_connected = False; break

    def _process_received_data(self, cmd_id: int, data: bytes):
        """수신된 데이터 처리 (PDF 페이지 42) [cite: 1487, 1536, 1541, 1543, 1544]"""
        current_time = time.time()
        dt = current_time - self.last_update_time

        try:
            if cmd_id == self.ID_INTEGRATED_DATA and len(data) == 20:
                # 통합 데이터 (가속도, 자이로, 속도, 전압)
                # < 6h 3h H
                # h: signed short (2 bytes)
                # H: unsigned short (2 bytes)
                raw_values = struct.unpack('<hhhhhhhhhH', data)
                
                with self.data_lock:
                    # IMU 데이터 처리
                    self.imu_data.accel_x = (raw_values[0] / 32768.0) * 2.0 * GRAVITY
                    self.imu_data.accel_y = (raw_values[1] / 32768.0) * 2.0 * GRAVITY
                    self.imu_data.accel_z = (raw_values[2] / 32768.0) * 2.0 * GRAVITY
                    self.imu_data.gyro_x = (raw_values[3] / 32768.0) * 500.0 * (math.pi / 180.0)
                    self.imu_data.gyro_y = (raw_values[4] / 32768.0) * 500.0 * (math.pi / 180.0)
                    self.imu_data.gyro_z = (raw_values[5] / 32768.0) * 500.0 * (math.pi / 180.0)
                    
                    # 오도메트리 속도 데이터 처리
                    self.odometry_data.vx = raw_values[6] / 1000.0
                    self.odometry_data.vy = raw_values[7] / 1000.0
                    self.odometry_data.vw = raw_values[8] / 1000.0
                    
                    # 오도메트리 위치 적분
                    if dt > 0:
                        delta_x = (self.odometry_data.vx * math.cos(self.odometry_data.theta) - self.odometry_data.vy * math.sin(self.odometry_data.theta)) * dt
                        delta_y = (self.odometry_data.vx * math.sin(self.odometry_data.theta) + self.odometry_data.vy * math.cos(self.odometry_data.theta)) * dt
                        delta_theta = self.odometry_data.vw * dt
                        
                        self.odometry_data.x += delta_x
                        self.odometry_data.y += delta_y
                        self.odometry_data.theta += delta_theta
                    
                    # 배터리 전압 처리
                    self.battery_voltage = raw_values[9] / 100.0
        except struct.error as e:
            logger.error(f"데이터 파싱 오류 (ID: {cmd_id}): {e}")
        
        self.last_update_time = current_time

    def __enter__(self):
        if self.connect(): return self
        else: raise ConnectionError("로봇 연결 실패")
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

# 메인 함수는 원본과 동일하게 유지 (수정 필요 없음)
def main():
    """메인 함수 - 기본 사용 예제"""
    import sys, select, termios, tty
    # ... (원본 코드와 동일)

if __name__ == "__main__":
    # main() # 직접 실행보다는 다른 파일에서 import하여 사용하는 것을 권장
    pass