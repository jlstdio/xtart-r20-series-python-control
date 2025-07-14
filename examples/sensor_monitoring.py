#!/usr/bin/env python3
"""
Xtark R20 센서 데이터 모니터링 예제
실시간으로 센서 데이터를 출력합니다.
"""

import sys
import os
import time
import threading
# from xtark_r20_controller import XtarkR20Controller, RobotType, GRAVITY
# 부모 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from xtark_r20_controller import XtarkR20Controller, RobotType, GRAVITY
except ImportError as e:
    print(f"Error importing xtark_r20_controller: {e}")
    print("Please make sure you're running this from the python_controller directory")
    print("or install the package using: python setup.py install")
    sys.exit(1)

class SensorMonitor:
    """센서 데이터 모니터링 클래스"""
    
    def __init__(self, controller: XtarkR20Controller):
        self.controller = controller
        self.is_running = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """모니터링 시작"""
        if self.is_running: return
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("센서 모니터링 시작 (Ctrl+C로 종료)")
    
    def stop_monitoring(self):
        """모니터링 종료"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
    
    def _monitor_loop(self):
        """모니터링 루프"""
        while self.is_running:
            try:
                odom = self.controller.get_odometry()
                imu = self.controller.get_imu_data()
                battery = self.controller.get_battery_voltage()
                velocity = self.controller.get_current_velocity()
                
                # 화면 지우기 (ANSI escape code)
                print("\033[2J\033[H", end="")
                
                print("=" * 60)
                print("           Xtark R20 센서 데이터 모니터링")
                print("=" * 60)
                
                # 배터리
                # PDF(p15) 기반 전압 범위: 9.84V (0%) ~ 12.6V (100%) [cite: 621]
                battery_percent = max(0, min(100, (battery - 9.84) / (12.6 - 9.84) * 100))
                battery_bar = "█" * int(battery_percent / 5) + "░" * (20 - int(battery_percent / 5))
                print(f"\n🔋 배터리: {battery:.2f}V [{battery_bar}] {battery_percent:.1f}%")
                
                # 오도메트리
                print(f"\n📍 오도메트리 (통합 속도 기반 추정):")
                print(f"   위치 (x, y, θ): ({odom.x:6.3f} m, {odom.y:6.3f} m, {odom.theta:6.3f} rad)")
                print(f"   속도 (vx, vy, vw): ({odom.vx:6.3f} m/s, {odom.vy:6.3f} m/s, {odom.vw:6.3f} rad/s)")

                # IMU
                print(f"\n🧭 IMU (단위: m/s², rad/s):")
                print(f"   가속도 (x,y,z): ({imu.accel_x:6.3f}, {imu.accel_y:6.3f}, {imu.accel_z-GRAVITY:6.3f})")
                print(f"   각속도 (x,y,z): ({imu.gyro_x:6.3f}, {imu.gyro_y:6.3f}, {imu.gyro_z:6.3f})")
                
                # 현재 설정 속도
                print(f"\n🎮 현재 제어 속도:")
                print(f"   vx: {velocity.vx:.2f} m/s, vy: {velocity.vy:.2f} m/s, vw: {velocity.vw:.2f} rad/s")
                
                print("-" * 60)
                print(f"⏰ 마지막 업데이트: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                print("\n(Ctrl+C를 눌러 종료)")
                
                time.sleep(0.1)  # 10Hz 업데이트
                
            except Exception as e:
                print(f"모니터링 오류: {e}")
                time.sleep(1.0)

def main():
    """메인 함수"""
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    print(f"시리얼 포트: {port}")
    
    try:
        # PDF 기반으로 R20_MEC(메카넘)을 기본값으로 설정
        with XtarkR20Controller(port, robot_type=RobotType.R20_MEC) as controller:
            monitor = SensorMonitor(controller)
            monitor.start_monitoring()
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n프로그램 종료 중...")
    except ConnectionError as e:
        print(f"연결 오류: {e}")
        print("OpenCTR 컨트롤러가 올바르게 연결되었는지, 포트 이름이 맞는지 확인하세요.")
    finally:
        print("프로그램 종료됨")

if __name__ == "__main__":
    main()