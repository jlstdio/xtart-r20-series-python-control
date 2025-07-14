#!/usr/bin/env python3
"""
Xtark R20 기본 사용 예제
로봇의 기본적인 움직임과 센서 데이터 읽기를 보여주는 예제입니다.
"""

import time
import sys
import os

# 상위 디렉토리의 모듈 import를 위한 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xtark_r20_controller import XtarkR20Controller, RobotType

def basic_movement_demo(robot: XtarkR20Controller):
    """기본 움직임 데모"""
    print("\n=== 기본 움직임 데모 ===")
    
    # 전진
    print("전진 중...")
    robot.set_velocity(0.3, 0.0, 0.0)
    time.sleep(2.0)
    
    # 정지
    print("정지")
    robot.set_velocity(0.0, 0.0, 0.0)
    time.sleep(1.0)
    
    # 후진
    print("후진 중...")
    robot.set_velocity(-0.3, 0.0, 0.0)
    time.sleep(2.0)
    
    # 정지
    robot.set_velocity(0.0, 0.0, 0.0)
    time.sleep(1.0)
    
    # 좌회전
    print("좌회전 중...")
    robot.set_velocity(0.0, 0.0, 1.0)
    time.sleep(1.5)
    
    # 정지
    robot.set_velocity(0.0, 0.0, 0.0)
    time.sleep(1.0)
    
    # 우회전
    print("우회전 중...")
    robot.set_velocity(0.0, 0.0, -1.0)
    time.sleep(1.5)
    
    # 정지
    robot.set_velocity(0.0, 0.0, 0.0)
    time.sleep(1.0)

def side_movement_demo(robot: XtarkR20Controller):
    """측면 이동 데모 (메카넘/옴니 휠만)"""
    print("\n=== 측면 이동 데모 ===")
    print("※ 메카넘 휠 또는 옴니 휠에서만 동작합니다")
    
    # 좌측 이동
    print("좌측 이동 중...")
    robot.set_velocity(0.0, 0.3, 0.0)
    time.sleep(2.0)
    
    # 정지
    robot.set_velocity(0.0, 0.0, 0.0)
    time.sleep(1.0)
    
    # 우측 이동
    print("우측 이동 중...")
    robot.set_velocity(0.0, -0.3, 0.0)
    time.sleep(2.0)
    
    # 정지
    robot.set_velocity(0.0, 0.0, 0.0)
    time.sleep(1.0)
    
    # 대각선 이동
    print("대각선 이동 중...")
    robot.set_velocity(0.2, 0.2, 0.0)
    time.sleep(2.0)
    
    # 정지
    robot.set_velocity(0.0, 0.0, 0.0)

def sensor_reading_demo(robot: XtarkR20Controller):
    """센서 데이터 읽기 데모"""
    print("\n=== 센서 데이터 데모 ===")
    
    for i in range(10):
        print(f"\n--- 측정 {i+1}/10 ---")
        
        # 오도메트리 데이터
        odom = robot.get_odometry()
        print(f"위치: x={odom.x:.3f}m, y={odom.y:.3f}m, θ={odom.theta:.3f}rad")
        print(f"속도: vx={odom.vx:.3f}m/s, vy={odom.vy:.3f}m/s, vw={odom.vw:.3f}rad/s")
        
        # IMU 데이터
        imu = robot.get_imu_data()
        print(f"가속도: ax={imu.accel_x:.3f}, ay={imu.accel_y:.3f}, az={imu.accel_z:.3f}")
        print(f"각속도: gx={imu.gyro_x:.3f}, gy={imu.gyro_y:.3f}, gz={imu.gyro_z:.3f}")
        
        # 배터리 전압
        battery = robot.get_battery_voltage()
        print(f"배터리: {battery:.2f}V")
        
        time.sleep(1.0)

def led_and_sound_demo(robot: XtarkR20Controller):
    """LED 및 부저 데모"""
    print("\n=== LED 및 부저 데모 ===")
    
    # 부저 테스트
    print("부저 테스트...")
    robot.set_beeper(True)
    time.sleep(0.5)
    robot.set_beeper(False)
    time.sleep(0.5)
    
    # LED 색상 변경
    colors = [
        (255, 0, 0, "빨간색"),
        (0, 255, 0, "녹색"),
        (0, 0, 255, "파란색"),
        (255, 255, 0, "노란색"),
        (255, 0, 255, "자홍색"),
        (0, 255, 255, "청록색"),
        (255, 255, 255, "흰색")
    ]
    
    for r, g, b, name in colors:
        print(f"LED: {name}")
        robot.set_rgb_light(r, g, b)
        time.sleep(1.0)
    
    # LED 끄기
    print("LED 끄기")
    robot.set_rgb_light(0, 0, 0)

def main():
    """메인 함수"""
    print("=" * 50)
    print("  Xtark R20 기본 사용 예제")
    print("=" * 50)
    
    # 연결 설정
    port = input("시리얼 포트 (기본값: /dev/ttyUSB0): ").strip() or "/dev/ttyUSB0"
    
    print("\n로봇 타입을 선택하세요:")
    for i, robot_type in enumerate(RobotType, 1):
        print(f"  {i}. {robot_type.name}")
    
    try:
        choice = int(input("선택 (기본값: 1): ") or "1")
        robot_type = list(RobotType)[choice - 1]
    except (ValueError, IndexError):
        robot_type = RobotType.R20_MEC
    
    print(f"\n연결 정보:")
    print(f"  포트: {port}")
    print(f"  로봇 타입: {robot_type.name}")
    
    # 데모 선택
    print("\n실행할 데모를 선택하세요:")
    print("  1. 기본 움직임")
    print("  2. 측면 이동 (메카넘/옴니 휠만)")
    print("  3. 센서 데이터 읽기")
    print("  4. LED 및 부저")
    print("  5. 전체 데모")
    
    try:
        demo_choice = int(input("선택 (기본값: 5): ") or "5")
    except ValueError:
        demo_choice = 5
    
    # 로봇 연결 및 데모 실행
    try:
        print(f"\n{port} 포트로 연결 중...")
        
        with XtarkR20Controller(port, robot_type=robot_type) as robot:
            print("연결 성공!")
            
            if demo_choice == 1:
                basic_movement_demo(robot)
            elif demo_choice == 2:
                side_movement_demo(robot)
            elif demo_choice == 3:
                sensor_reading_demo(robot)
            elif demo_choice == 4:
                led_and_sound_demo(robot)
            elif demo_choice == 5:
                # 전체 데모
                basic_movement_demo(robot)
                time.sleep(1.0)
                
                if robot_type in [RobotType.R20_MEC, RobotType.R20_OMNI]:
                    side_movement_demo(robot)
                    time.sleep(1.0)
                
                sensor_reading_demo(robot)
                time.sleep(1.0)
                
                led_and_sound_demo(robot)
            
            print("\n데모 완료!")
            
    except ConnectionError as e:
        print(f"\n연결 오류: {e}")
        print("\n해결 방법:")
        print("1. OpenCTR 컨트롤러가 올바르게 연결되어 있는지 확인")
        print("2. 시리얼 포트 이름이 정확한지 확인")
        print("3. 다른 프로그램에서 포트를 사용하고 있지 않은지 확인")
        print("4. 시리얼 포트 접근 권한 확인")
        
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단됨")
        
    except Exception as e:
        print(f"\n예기치 않은 오류: {e}")

if __name__ == "__main__":
    main()
