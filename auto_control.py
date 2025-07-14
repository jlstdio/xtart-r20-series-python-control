#!/usr/bin/env python3
"""
Xtark R20 로봇 자동 제어 예제
미리 정의된 패턴으로 로봇을 자동 제어합니다.

패턴:
1. 사각형 경로
2. 원형 경로  
3. 지그재그 경로
4. LED 효과와 함께 춤추기
"""

import time
import math
import threading
from xtark_r20_controller import XtarkR20Controller, RobotType

class AutoController:
    """자동 제어 클래스"""
    
    def __init__(self, controller: XtarkR20Controller):
        self.controller = controller
        self.is_running = False
        
    def rectangle_pattern(self, size: float = 1.0, speed: float = 0.3):
        """사각형 경로 패턴"""
        print(f"사각형 패턴 시작 (크기: {size}m, 속도: {speed}m/s)")
        
        side_time = size / speed
        
        for i in range(4):
            if not self.is_running:
                break
                
            print(f"변 {i+1}/4 이동 중...")
            
            # 직진
            self.controller.set_velocity(speed, 0.0, 0.0)
            time.sleep(side_time)
            
            # 정지
            self.controller.set_velocity(0.0, 0.0, 0.0)
            time.sleep(0.5)
            
            # 90도 회전
            print("회전 중...")
            self.controller.set_velocity(0.0, 0.0, math.pi/2)  # 90도/초
            time.sleep(1.0)
            
            # 정지
            self.controller.set_velocity(0.0, 0.0, 0.0)
            time.sleep(0.5)
        
        print("사각형 패턴 완료")
    
    def circle_pattern(self, radius: float = 0.5, duration: float = 10.0):
        """원형 경로 패턴"""
        print(f"원형 패턴 시작 (반지름: {radius}m, 시간: {duration}초)")
        
        # 원주 속도와 각속도 계산
        circumference = 2 * math.pi * radius
        linear_speed = circumference / duration
        angular_speed = 2 * math.pi / duration
        
        print(f"선속도: {linear_speed:.2f}m/s, 각속도: {angular_speed:.2f}rad/s")
        
        start_time = time.time()
        while self.is_running and (time.time() - start_time) < duration:
            self.controller.set_velocity(linear_speed, 0.0, angular_speed)
            time.sleep(0.1)
        
        self.controller.set_velocity(0.0, 0.0, 0.0)
        print("원형 패턴 완료")
    
    def zigzag_pattern(self, length: float = 2.0, width: float = 0.5, speed: float = 0.3):
        """지그재그 경로 패턴 (메카넘 휠 전용)"""
        print(f"지그재그 패턴 시작 (길이: {length}m, 폭: {width}m, 속도: {speed}m/s)")
        
        forward_time = length / speed
        side_time = width / speed
        
        for i in range(3):  # 3번 지그재그
            if not self.is_running:
                break
                
            print(f"지그재그 {i+1}/3")
            
            # 전진
            self.controller.set_velocity(speed, 0.0, 0.0)
            time.sleep(forward_time)
            
            # 측면 이동
            side_direction = 1 if i % 2 == 0 else -1
            self.controller.set_velocity(0.0, speed * side_direction, 0.0)
            time.sleep(side_time)
            
            # 정지
            self.controller.set_velocity(0.0, 0.0, 0.0)
            time.sleep(0.5)
        
        print("지그재그 패턴 완료")
    
    def dance_pattern(self, duration: float = 20.0):
        """춤 패턴 (LED 효과와 함께)"""
        print(f"춤 패턴 시작 (시간: {duration}초)")
        
        start_time = time.time()
        step = 0
        
        while self.is_running and (time.time() - start_time) < duration:
            elapsed = time.time() - start_time
            
            # 속도 패턴 (사인파 기반)
            vx = 0.3 * math.sin(elapsed * 0.5)
            vy = 0.2 * math.cos(elapsed * 0.3)
            vw = 0.5 * math.sin(elapsed * 0.7)
            
            self.controller.set_velocity(vx, vy, vw)
            
            # LED 효과
            r = int(127 * (1 + math.sin(elapsed * 2)))
            g = int(127 * (1 + math.cos(elapsed * 1.5)))
            b = int(127 * (1 + math.sin(elapsed * 3)))
            
            self.controller.set_rgb_light(r, g, b)
            
            # 부저 효과 (가끔)
            if step % 50 == 0:
                self.controller.set_beeper(True)
                threading.Timer(0.1, lambda: self.controller.set_beeper(False)).start()
            
            step += 1
            time.sleep(0.1)
        
        # 정지 및 LED 끄기
        self.controller.set_velocity(0.0, 0.0, 0.0)
        self.controller.set_rgb_light(0, 0, 0)
        print("춤 패턴 완료")
    
    def figure_eight_pattern(self, size: float = 1.0, duration: float = 16.0):
        """8자 패턴"""
        print(f"8자 패턴 시작 (크기: {size}m, 시간: {duration}초)")
        
        start_time = time.time()
        
        while self.is_running and (time.time() - start_time) < duration:
            elapsed = time.time() - start_time
            
            # 8자 궤적을 위한 파라미터
            t = elapsed * 2 * math.pi / duration
            
            # 8자 형태의 속도 계산
            vx = size * 0.5 * math.cos(t)
            vy = size * 0.3 * math.sin(2 * t)
            
            # 궤적에 따른 각속도
            vw = math.sin(t) * 0.5
            
            self.controller.set_velocity(vx, vy, vw)
            time.sleep(0.1)
        
        self.controller.set_velocity(0.0, 0.0, 0.0)
        print("8자 패턴 완료")
    
    def start(self):
        """자동 제어 시작"""
        self.is_running = True
    
    def stop(self):
        """자동 제어 정지"""
        self.is_running = False
        self.controller.set_velocity(0.0, 0.0, 0.0)


def run_pattern_menu(controller: XtarkR20Controller):
    """패턴 선택 메뉴"""
    auto_ctrl = AutoController(controller)
    
    while True:
        print("\n" + "="*40)
        print("  자동 제어 패턴 선택")
        print("="*40)
        print("1. 사각형 패턴")
        print("2. 원형 패턴")
        print("3. 지그재그 패턴 (메카넘 휠만)")
        print("4. 춤 패턴 (LED + 음악)")
        print("5. 8자 패턴")
        print("6. 사용자 정의 패턴")
        print("7. 상태 모니터링")
        print("0. 종료")
        
        try:
            choice = input("\n선택 (0-7): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                size = float(input("사각형 크기 (m, 기본값: 1.0): ") or "1.0")
                speed = float(input("이동 속도 (m/s, 기본값: 0.3): ") or "0.3")
                
                auto_ctrl.start()
                try:
                    auto_ctrl.rectangle_pattern(size, speed)
                except KeyboardInterrupt:
                    print("\n패턴 중단됨")
                finally:
                    auto_ctrl.stop()
                    
            elif choice == '2':
                radius = float(input("원 반지름 (m, 기본값: 0.5): ") or "0.5")
                duration = float(input("지속 시간 (초, 기본값: 10): ") or "10")
                
                auto_ctrl.start()
                try:
                    auto_ctrl.circle_pattern(radius, duration)
                except KeyboardInterrupt:
                    print("\n패턴 중단됨")
                finally:
                    auto_ctrl.stop()
                    
            elif choice == '3':
                print("※ 메카넘 휠 로봇에서만 정상 동작합니다")
                length = float(input("전진 거리 (m, 기본값: 2.0): ") or "2.0")
                width = float(input("측면 거리 (m, 기본값: 0.5): ") or "0.5")
                speed = float(input("이동 속도 (m/s, 기본값: 0.3): ") or "0.3")
                
                auto_ctrl.start()
                try:
                    auto_ctrl.zigzag_pattern(length, width, speed)
                except KeyboardInterrupt:
                    print("\n패턴 중단됨")
                finally:
                    auto_ctrl.stop()
                    
            elif choice == '4':
                duration = float(input("춤 시간 (초, 기본값: 20): ") or "20")
                
                print(f"\n{duration}초간 춤을 춥니다! (Ctrl+C로 중단)")
                auto_ctrl.start()
                try:
                    auto_ctrl.dance_pattern(duration)
                except KeyboardInterrupt:
                    print("\n댄스 중단됨")
                finally:
                    auto_ctrl.stop()
                    
            elif choice == '5':
                size = float(input("8자 크기 (m, 기본값: 1.0): ") or "1.0")
                duration = float(input("지속 시간 (초, 기본값: 16): ") or "16")
                
                auto_ctrl.start()
                try:
                    auto_ctrl.figure_eight_pattern(size, duration)
                except KeyboardInterrupt:
                    print("\n패턴 중단됨")
                finally:
                    auto_ctrl.stop()
                    
            elif choice == '6':
                custom_pattern(controller)
                
            elif choice == '7':
                monitor_status(controller)
                
            else:
                print("잘못된 선택입니다.")
                
        except ValueError:
            print("숫자를 입력하세요.")
        except KeyboardInterrupt:
            print("\n메뉴로 돌아갑니다.")


def custom_pattern(controller: XtarkR20Controller):
    """사용자 정의 패턴"""
    print("\n사용자 정의 패턴 모드")
    print("명령 형식: vx,vy,vw,duration")
    print("예제: 0.3,0,0,2  (2초간 0.3m/s로 전진)")
    print("      0,0,1.57,1  (1초간 90도 회전)")
    print("빈 줄 입력 시 종료")
    
    commands = []
    
    while True:
        cmd = input("명령: ").strip()
        if not cmd:
            break
        
        try:
            parts = cmd.split(',')
            if len(parts) != 4:
                print("형식: vx,vy,vw,duration")
                continue
            
            vx = float(parts[0])
            vy = float(parts[1])
            vw = float(parts[2])
            duration = float(parts[3])
            
            commands.append((vx, vy, vw, duration))
            print(f"추가됨: vx={vx}, vy={vy}, vw={vw}, 시간={duration}초")
            
        except ValueError:
            print("숫자 형식이 잘못되었습니다.")
    
    if commands:
        print(f"\n{len(commands)}개 명령 실행 시작...")
        
        for i, (vx, vy, vw, duration) in enumerate(commands, 1):
            print(f"명령 {i}/{len(commands)}: vx={vx}, vy={vy}, vw={vw}, {duration}초")
            
            controller.set_velocity(vx, vy, vw)
            time.sleep(duration)
            
            controller.set_velocity(0, 0, 0)
            time.sleep(0.5)
        
        print("사용자 정의 패턴 완료")


def monitor_status(controller: XtarkR20Controller):
    """상태 모니터링"""
    print("\n실시간 상태 모니터링 (Ctrl+C로 종료)")
    print("=" * 60)
    
    try:
        while True:
            vel = controller.get_current_velocity()
            odom = controller.get_odometry()
            imu = controller.get_imu_data()
            battery = controller.get_battery_voltage()
            
            print(f"\r시간: {time.strftime('%H:%M:%S')} | "
                  f"속도: vx={vel.vx:+.2f} vy={vel.vy:+.2f} vw={vel.vw:+.2f} | "
                  f"위치: x={odom.x:+.2f} y={odom.y:+.2f} θ={odom.theta:+.2f} | "
                  f"배터리: {battery:.1f}V", end="")
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n모니터링 종료")


def main():
    """메인 함수"""
    print("=" * 50)
    print("  Xtark R20 자동 제어 프로그램")
    print("=" * 50)
    
    # 시리얼 포트 설정
    port = input("시리얼 포트를 입력하세요 (기본값: /dev/ttyUSB0): ").strip()
    if not port:
        port = "/dev/ttyUSB0"
    
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
            
            # 패턴 메뉴 실행
            run_pattern_menu(controller)
            
    except ConnectionError as e:
        print(f"\n연결 오류: {e}")
        print("OpenCTR 컨트롤러 연결을 확인하세요.")
    except KeyboardInterrupt:
        print("\n프로그램 종료")
    except Exception as e:
        print(f"\n오류 발생: {e}")


if __name__ == "__main__":
    main()
