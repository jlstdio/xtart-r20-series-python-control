import time
import sys
import os

try:
    from xtark_r20_controller import XtarkR20Controller, RobotType
except ImportError:
    # 경로가 다른 경우를 대비하여 상위 폴더를 추가
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from xtark_r20_controller import XtarkR20Controller, RobotType

# 로봇 모델과 포트를 실제 환경에 맞게 수정하세요.
ROBOT_MODEL = RobotType.R20_FWD
SERIAL_PORT = '/dev/cu.usbserial-5A561356221'

try:
    with XtarkR20Controller(SERIAL_PORT, robot_type=ROBOT_MODEL) as controller:
        print("✅ 로봇에 연결되었습니다.")
        print("곡선 주행을 시작합니다...")

        # 앞으로 0.3m/s로 이동하면서, 초당 1.5rad 만큼 좌회전
        # => 로봇이 부드러운 좌회전 곡선을 그리며 주행합니다.
        controller.set_velocity(0.3, 0.0, 1.5) 
        time.sleep(5.0) # 5초간 곡선 주행
        
        # 정지
        controller.set_velocity(0.0, 0.0, 0.0)
        print("주행을 마쳤습니다.")

except ConnectionError as e:
    print(f"❌ 연결 오류: {e}")
except Exception as e:
    print(f"오류 발생: {e}")