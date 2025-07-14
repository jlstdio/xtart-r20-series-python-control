네, 사용자가 제공한 파일들과 제가 수정한 내용을 반영하여 `README.md` 파일을 최신화했습니다.

주요 변경 사항은 다음과 같습니다.

  - **`fwd_test.py` 추가**: 새로 생성한 FWD 모델 테스트 스크립트를 파일 구조와 빠른 시작 가이드에 추가했습니다.
  - **키보드 제어 설명 수정**: 제어 방식을 더 직관적인 'Press-and-Hold' 방식으로 변경하고, 주요 키(`Space`, `ESC` 등)의 역할을 명확히 수정했습니다.
  - **API 레퍼런스 업데이트**: `set_rgb_light` 함수에 `mode` 파라미터를 추가하고, 새로 추가된 `save_light_setting` 함수를 명시했습니다.
  - **문제 해결(Troubleshooting) 항목 추가**: 실제 발생했던 macOS에서의 `keyboard` 라이브러리 권한 문제를 해결하는 방법을 추가하여 문서의 실용성을 높였습니다.

-----

### \#\# 수정된 README.md

```markdown
# Xtark R20 Python Controller

ROS 없이 순수 Python으로 OpenCTR H60과 직접 통신하여 Xtark R20 로봇을 제어하는 프로그램입니다.

## 📋 특징

- [cite_start]**ROS 독립적**: ROS 설치 없이 순수 Python으로 구현 [cite: 1]
- [cite_start]**다양한 로봇 타입 지원**: 메카넘 휠, 차동구동, 아커만 조향 등 [cite: 1]
- [cite_start]**실시간 제어**: 키보드 및 자동 패턴 제어 [cite: 1]
- [cite_start]**센서 데이터 수신**: 오도메트리, IMU, 배터리 정보 [cite: 1]
- [cite_start]**크로스 플랫폼**: Windows, macOS, Linux 지원 [cite: 1]

## 📁 파일 구조

```

python\_controller/
├── xtark\_r20\_controller.py    \# 메인 컨트롤러 클래스
├── fwd\_test.py                \# FWD 모델 동작 테스트
├── keyboard\_control.py        \# 키보드 제어 프로그램
├── auto\_control.py            \# 자동 제어 패턴 프로그램
├── test\_controller.py         \# 전체 기능 테스트 프로그램
├── setup.py                   \# 설정 및 설치 스크립트
├── examples/                  \# 사용 예제들
│   ├── basic\_example.py       \# 기본 사용법
│   ├── sensor\_monitoring.py   \# 센서 데이터 모니터링
│   └── led\_effects.py         \# LED 효과 예제
├── config.ini                 \# 설정 파일 (setup.py 실행 후 생성)
└── README.md                  \# 이 파일

````

## 🚀 빠른 시작

### 1. 환경 설정 (처음 사용시)

```bash
python setup.py
````

[cite\_start]이 명령으로 필요한 라이브러리 설치, 설정 파일 생성, 연결 테스트를 한 번에 할 수 있습니다. [cite: 1]

### 2\. 키보드 제어

```bash
python keyboard_control.py [시리얼_포트]
```

**조작법 (Press-and-Hold):**

  - 키를 누르는 동안 해당 방향으로 움직이며, 키에서 손을 떼면 정지합니다.
  - `W/S`: 전진/후진
  - `A/D`: 좌회전/우회전
  - `Q/E`: 좌측이동/우측이동 (메카넘/옴니 휠 전용)
  - `Space`: 긴급 정지
  - `B`: 부저
  - `L`: LED 테스트
  - `I`: IMU 캘리브레이션
  - `P`: 현재 상태 출력
  - `ESC`: 종료

### 3\. 자동 제어 패턴

```bash
python auto_control.py [시리얼_포트]
```

**지원 패턴:**

  - [cite\_start]사각형, 원형, 8자, 춤 패턴 등 다양한 자동 경로 주행을 지원합니다. [cite: 1]

### 4\. FWD 모델 기본 동작 테스트

```bash
python fwd_test.py [시리얼_포트]
```

  - 4륜 차동구동(FWD) 모델의 직진, 후진, 좌회전, 우회전 기본 동작을 테스트합니다.

## 🤖 지원되는 로봇 타입

| 타입      | 설명         | 이동 방향     |
| --------- | ------------ | ------------- |
| `R20_MEC` | 메카넘 휠    | 전방향 이동   |
| `R20_FWD` | 4륜 차동구동 | 전후진, 회전  |
| `R20_AKM` | 아커만 조향  | 자동차 방식   |
| `R20_TWD` | 2륜 차동구동 | 전후진, 회전  |
| `R20_TAK` | 탱크 타입    | 궤도 방식     |
| `R20_OMNI`| 옴니 휠      | 전방향 이동   |

## 📊 API 레퍼런스

### XtarkR20Controller 클래스

#### 생성자

```python
XtarkR20Controller(port='/dev/ttyUSB0', baudrate=230400, robot_type=RobotType.R20_MEC)
```

#### 연결 관리

```python
connect() -> bool          # 컨트롤러에 연결
disconnect()               # 컨트롤러 연결 해제
```

#### 모션 및 기능 제어

```python
set_velocity(vx, vy, vw)   # 로봇의 속도 설정 (m/s, rad/s)
set_beeper(enable: bool)         # 부저 켜기/끄기
set_rgb_light(r, g, b, mode=1) # RGB LED 색상 및 모드 설정
save_light_setting()       # 현재 조명 설정을 EEPROM에 저장
calibrate_imu()            # IMU 센서 캘리브레이션
```

#### 데이터 조회

```python
get_odometry() -> OdometryData    # 오도메트리 데이터 조회
get_imu_data() -> IMUData         # IMU 데이터 조회
get_battery_voltage() -> float    # 배터리 전압 조회
get_current_velocity() -> Velocity # 현재 설정된 속도 조회
```

## 🐛 문제 해결

### 연결 문제

1.  [cite\_start]**시리얼 포트를 찾을 수 없음**: `lsusb`, `dmesg | tail` (Linux) 또는 장치 관리자(Windows)로 포트 이름을 확인하세요. [cite: 1]
2.  [cite\_start]**권한 거부(Permission Denied) 오류 (Linux)**: `sudo usermod -a -G dialout $USER` 명령으로 사용자에게 시리얼 포트 접근 권한을 부여하고 재부팅하세요. [cite: 1]
3.  [cite\_start]**포트가 사용 중(Port is already open)**: 다른 프로그램(예: ROS, 다른 터미널)이 포트를 사용하고 있는지 확인하고 종료하세요. [cite: 1]

### 키보드 제어 문제 (macOS)

  - **증상**: `sudo`로 실행해도 `OSError: Error 13` 또는 `Unrecognized character` 오류 발생
  - **원인**: macOS의 보안 정책으로 인해 `keyboard` 라이브러리가 키 입력을 감지하려면 별도의 권한이 필요합니다.
  - **해결책**: `시스템 설정 > 개인정보보호 및 보안 > 손쉬운 사용`에서 스크립트를 실행하는 **터미널 앱(Terminal, VS Code 등)을 목록에 추가하고 권한을 허용**해주세요. 권한 부여 후 반드시 터미널 앱을 재시작해야 합니다.

<!-- end list -->

```
```