#!/usr/bin/env python3
"""
Xtark R20 FWD (4륜 차동 구동) 모델 기본 동작 테스트
직진, 후진, 좌회전, 우회전을 각각 3초씩 수행합니다.
"""

import sys
import time
import os

# 상위 디렉토리의 모듈 import를 위한 경로 추가
# 이 스크립트가 xtark_r20_controller.py와 같은 폴더에 있다면 이 부분은 필요 없습니다.
# 하지만 다른 폴더에 있다면 경로를 맞게 설정해야 합니다.
try:
    from xtark_r20_controller import XtarkR20Controller, RobotType
except ImportError:
    # 경로가 다른 경우를 대비하여 상위 폴더를 추가
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from xtark_r20_controller import XtarkR20Controller, RobotType


def run_test_sequence(controller: XtarkR20Controller, duration: float = 3.0, speed: float = 0.3):
    """
    정의된 동작 시퀀스를 실행합니다.
    
    :param controller: 연결된 XtarkR20Controller 객체
    :param duration: 각 동작의 지속 시간 (초)
    :param speed: 로봇의 이동 속도 (m/s 또는 rad/s)
    """
    
    print(f"\n▶️  테스트 시퀀스를 시작합니다. (각 동작 {duration}초)")
    
    try:
        # 1. 직진
        print(f"1. ⬆️  직진 ({duration}초)")
        controller.set_velocity(speed, 0.0, 0.0)
        time.sleep(duration)
        
        # 정지
        print("   ⏹️  정지 (1초)")
        controller.set_velocity(0.0, 0.0, 0.0)
        time.sleep(1.0)
        
        # 2. 후진
        print(f"2. ⬇️  후진 ({duration}초)")
        controller.set_velocity(-speed, 0.0, 0.0)
        time.sleep(duration)
        
        # 정지
        print("   ⏹️  정지 (1초)")
        controller.set_velocity(0.0, 0.0, 0.0)
        time.sleep(1.0)
        
        # 3. 좌로 회전 (제자리 회전)
        # FWD 모델은 vy(좌우 이동)가 없으므로 vw(각속도)를 사용합니다.
        print(f"3. ↪️  좌로 회전 ({duration}초)")
        controller.set_velocity(0.0, 0.0, speed * 1.5) # 회전 속도를 조금 더 빠르게 설정
        time.sleep(duration)
        
        # 정지
        print("   ⏹️  정지 (1초)")
        controller.set_velocity(0.0, 0.0, 0.0)
        time.sleep(1.0)
        
        # 4. 우로 회전 (제자리 회전)
        print(f"4. ↩️  우로 회전 ({duration}초)")
        controller.set_velocity(0.0, 0.0, -speed * 1.5)
        time.sleep(duration)
        
        # 최종 정지
        controller.set_velocity(0.0, 0.0, 0.0)
        print("\n✅ 테스트 시퀀스 완료!")
        
    except KeyboardInterrupt:
        print("\n사용자에 의해 테스트가 중단되었습니다.")
    finally:
        # 테스트 종료 시 반드시 로봇을 정지시킵니다.
        controller.set_velocity(0.0, 0.0, 0.0)
        print("로봇을 정지시켰습니다.")


def main():
    """메인 함수"""
    print("=" * 50)
    print("  Xtark R20 FWD 모델 동작 테스트 프로그램")
    print("=" * 50)
    
    # 시리얼 포트 설정
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        # 운영체제에 따라 기본 포트 설정
        default_port = 'COM3' if os.name == 'nt' else '/dev/ttyUSB0'
        port = input(f"시리얼 포트를 입력하세요 (기본값: {default_port}): ").strip()
        if not port:
            port = default_port

    print(f"\n연결 정보:")
    print(f"  - 포트: {port}")
    print(f"  - 로봇 모델: {RobotType.R20_FWD.name}")

    # 컨트롤러 연결
    try:
        # with 구문을 사용하여 프로그램 종료 시 자동으로 연결 해제
        with XtarkR20Controller(port, robot_type=RobotType.R20_FWD) as controller:
            print("\n✅ 로봇에 성공적으로 연결되었습니다.")
            
            # 테스트 시퀀스 실행
            run_test_sequence(controller)
            
    except ConnectionError as e:
        print(f"\n❌ 연결 오류: {e}")
        print("다음을 확인하세요:")
        print("  1. OpenCTR 컨트롤러가 올바르게 연결되었는지 확인하세요.")
        print("  2. 시리얼 포트 이름이 정확한지 확인하세요 ('/dev/ttyUSB0', 'COM3' 등).")
        print("  3. (Linux/macOS) 시리얼 포트 접근 권한이 있는지 확인하세요.")
    except Exception as e:
        print(f"\n알 수 없는 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()