#!/usr/bin/env python3
"""
Xtark R20 로봇 키보드 제어 프로그램
실시간 키보드 입력으로 로봇을 제어합니다.
"""

import sys
import time
import threading

# 상위 디렉토리의 모듈 import를 위한 경로 추가
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xtark_r20_controller import XtarkR20Controller, RobotType

try:
    import keyboard  # pip install keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("Warning: 'keyboard' 라이브러리를 찾을 수 없습니다. 수동 입력 모드로 전환됩니다.")
    print("         'pip install keyboard'로 설치할 수 있습니다 (Windows/Linux에서 sudo 필요).")


class KeyboardController:
    """키보드 제어 클래스"""
    
    def __init__(self, controller: XtarkR20Controller):
        self.controller = controller
        self.is_running = False
        self.current_velocity = {'vx': 0.0, 'vy': 0.0, 'vw': 0.0}
        self.speed_step = 0.3  # 기본 속도
        self.max_speed = 1.0   # 최대 속도
    
    def start(self):
        """키보드 제어 시작"""
        if not KEYBOARD_AVAILABLE:
            self._manual_control()
            return
            
        print("\n키보드 제어 모드 시작 (Press-and-Hold)")
        print("조작법:")
        print("  W/S: 전진/후진     A/D: 좌회전/우회전")
        print("  Q/E: 좌측이동/우측이동 (메카넘/옴니 휠)")
        print("  Space: 긴급 정지")
        print("  B: 부저  L: LED 테스트  I: IMU 캘리브레이션")
        print("  P: 상태 출력  ESC: 종료")
        
        self.is_running = True
        
        # ### 변경된 부분: 각 키를 직접 명시적으로 등록 ###
        # Press 이벤트
        keyboard.on_press_key('w', lambda e: self._update_velocity(vx=self.speed_step), suppress=True)
        keyboard.on_press_key('s', lambda e: self._update_velocity(vx=-self.speed_step), suppress=True)
        keyboard.on_press_key('d', lambda e: self._update_velocity(vw=-self.speed_step * 1.5), suppress=True)
        keyboard.on_press_key('a', lambda e: self._update_velocity(vw=self.speed_step * 1.5), suppress=True)
        keyboard.on_press_key('e', lambda e: self._update_velocity(vy=-self.speed_step), suppress=True)
        keyboard.on_press_key('q', lambda e: self._update_velocity(vy=self.speed_step), suppress=True)
        
        # Release 이벤트
        keyboard.on_release_key('w', lambda e: self._update_velocity(vx=0), suppress=True)
        keyboard.on_release_key('s', lambda e: self._update_velocity(vx=0), suppress=True)
        keyboard.on_release_key('d', lambda e: self._update_velocity(vw=0), suppress=True)
        keyboard.on_release_key('a', lambda e: self._update_velocity(vw=0), suppress=True)
        keyboard.on_release_key('e', lambda e: self._update_velocity(vy=0), suppress=True)
        keyboard.on_release_key('q', lambda e: self._update_velocity(vy=0), suppress=True)

        # 기능 키
        keyboard.on_press_key('space', lambda e: self._stop(), suppress=True)
        keyboard.on_press_key('b', lambda e: self._beep(), suppress=True)
        keyboard.on_press_key('l', lambda e: self._led_test(), suppress=True)
        keyboard.on_press_key('i', lambda e: self._calibrate_imu(), suppress=True)
        keyboard.on_press_key('p', lambda e: self._print_status(), suppress=True)
        keyboard.on_press_key('esc', lambda e: self._stop_control(), suppress=True)

        print("\n로봇을 제어하세요...")
        while self.is_running:
            time.sleep(0.1)

        keyboard.unhook_all()
        self._stop()
        print("\n제어 종료.")

    def _update_velocity(self, vx=None, vy=None, vw=None):
        """속도 값을 업데이트하고 컨트롤러에 전송"""
        if vx is not None: self.current_velocity['vx'] = vx
        if vy is not None: self.current_velocity['vy'] = vy
        if vw is not None: self.current_velocity['vw'] = vw
        
        self.controller.set_velocity(
            self.current_velocity['vx'],
            self.current_velocity['vy'],
            self.current_velocity['vw']
        )
        
    def _manual_control(self):
        """수동 제어 모드 (keyboard 라이브러리 없이)"""
        print("\n수동 제어 모드")
        print("명령어를 입력하세요 (한 글자 + Enter):")
        print("  w: 전진  s: 후진  a: 좌회전  d: 우회전")
        print("  q: 좌측이동  e: 우측이동  x: 정지")
        print("  b: 부저  l: LED  i: IMU 캘리브레이션")
        print("  p: 상태 출력  quit: 종료")
        
        while True:
            try:
                cmd = input("\n명령: ").strip().lower()
                
                if cmd == 'quit':
                    break
                elif cmd == 'w':
                    self.controller.set_velocity(0.3, 0.0, 0.0)
                    print("전진")
                elif cmd == 's':
                    self.controller.set_velocity(-0.3, 0.0, 0.0)
                    print("후진")
                elif cmd == 'a':
                    self.controller.set_velocity(0.0, 0.0, 0.5)
                    print("좌회전")
                elif cmd == 'd':
                    self.controller.set_velocity(0.0, 0.0, -0.5)
                    print("우회전")
                elif cmd == 'q':
                    self.controller.set_velocity(0.0, 0.3, 0.0)
                    print("좌측이동")
                elif cmd == 'e':
                    self.controller.set_velocity(0.0, -0.3, 0.0)
                    print("우측이동")
                elif cmd == 'x':
                    self.controller.set_velocity(0.0, 0.0, 0.0)
                    print("정지")
                elif cmd == 'b':
                    self._beep()
                elif cmd == 'l':
                    self._led_test()
                elif cmd == 'i':
                    self._calibrate_imu()
                elif cmd == 'p':
                    self._print_status()
                else:
                    print("알 수 없는 명령어")
                    
            except KeyboardInterrupt:
                break
        
        self._stop()
    
    def _stop(self):
        """정지"""
        self.current_velocity = {'vx': 0.0, 'vy': 0.0, 'vw': 0.0}
        self.controller.set_velocity(0.0, 0.0, 0.0)
        print("긴급 정지!")
    
    def _stop_control(self):
        """제어 종료"""
        self.is_running = False

    def _beep(self):
        """부저 테스트"""
        self.controller.set_beeper(True)
        threading.Timer(0.3, lambda: self.controller.set_beeper(False)).start()
        print("부저 ON/OFF")
    
    def _led_test(self):
        """LED 테스트"""
        def led_sequence():
            self.controller.set_rgb_light(255, 0, 0)
            time.sleep(0.3)
            self.controller.set_rgb_light(0, 255, 0)
            time.sleep(0.3)
            self.controller.set_rgb_light(0, 0, 255)
            time.sleep(0.3)
            self.controller.set_rgb_light(0, 0, 0)
        
        threading.Thread(target=led_sequence, daemon=True).start()
        print("LED 테스트 시작")
    
    def _calibrate_imu(self):
        """IMU 캘리브레이션"""
        self.controller.calibrate_imu()
        print("IMU 캘리브레이션 시작 (5초간 정지 상태 유지)")
    
    def _change_speed(self, delta):
        """속도 변경"""
        self.speed_step = max(0.1, min(self.max_speed, self.speed_step + delta))
        print(f"속도 설정: {self.speed_step:.1f}")
    
    def _print_status(self):
        """상태 출력"""
        vel = self.controller.get_current_velocity()
        odom = self.controller.get_odometry()
        imu = self.controller.get_imu_data()
        battery = self.controller.get_battery_voltage()
        
        print(f"\n=== 로봇 상태 ===")
        print(f"제어 속도: vx={vel.vx:.2f}, vy={vel.vy:.2f}, vw={vel.vw:.2f}")
        print(f"추정 위치: x={odom.x:.2f}, y={odom.y:.2f}, θ={odom.theta:.2f}")
        print(f"실제 속도: vx={odom.vx:.2f}, vy={odom.vy:.2f}, vw={odom.vw:.2f}")
        print(f"가속도: ax={imu.accel_x:.2f}, ay={imu.accel_y:.2f}, az={imu.accel_z:.2f}")
        print(f"각속도: gx={imu.gyro_x:.2f}, gy={imu.gyro_y:.2f}, gz={imu.gyro_z:.2f}")
        print(f"배터리: {battery:.2f}V")
        print("="*17)

def main():
    """메인 함수"""
    print("=" * 50)
    print("  Xtark R20 키보드 제어 프로그램")
    print("=" * 50)
    
    # ... (main 함수 나머지 부분은 원본과 동일합니다) ...
    # 명령행 인수 처리
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        # 윈도우와 맥/리눅스 기본값 다르게 설정
        default_port = 'COM3' if platform.system() == "Windows" else '/dev/ttyUSB0'
        port = input(f"시리얼 포트를 입력하세요 (기본값: {default_port}): ").strip()
        if not port:
            port = default_port
    
    # 로봇 타입 선택
    print("\n로봇 타입을 선택하세요:")
    for i, robot_type in enumerate(RobotType, 1):
        print(f"  {i}. {robot_type.name}")
    
    try:
        choice = int(input("선택 (1-6, 기본값: 1): ") or "1")
        robot_type = list(RobotType)[choice - 1]
    except (ValueError, IndexError):
        robot_type = RobotType.R20_MEC
    
    print(f"\n연결 설정:")
    print(f"  포트: {port}")
    print(f"  로봇 타입: {robot_type.name}")
    
    # 컨트롤러 연결
    try:
        with XtarkR20Controller(port, robot_type=robot_type) as controller:
            print("\n연결 성공!")
            
            # 키보드 제어 시작
            keyboard_ctrl = KeyboardController(controller)
            keyboard_ctrl.start()
            
    except ConnectionError as e:
        print(f"\n연결 오류: {e}")
        print("다음을 확인하세요:")
        print("1. OpenCTR 컨트롤러가 올바르게 연결되어 있는지")
        print("2. 시리얼 포트 이름이 정확한지")
        print("3. 시리얼 포트 접근 권한이 있는지 (Linux/macOS)")
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n오류 발생: {e}")

if __name__ == "__main__":
    import platform
    main()
