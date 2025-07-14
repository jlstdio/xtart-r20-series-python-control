#!/usr/bin/env python3
"""
Xtark R20 Python Controller 설정 스크립트
필요한 라이브러리를 설치하고 환경을 설정합니다.

사용법:
    python setup.py
"""

import sys
import subprocess
import platform
import os

def check_python_version():
    """Python 버전 확인"""
    print("🐍 Python 버전 확인 중...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("❌ Python 3.6 이상이 필요합니다.")
        print(f"   현재 버전: {version.major}.{version.minor}.{version.micro}")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} 사용 중")
        return True

def install_package(package_name, import_name=None):
    """패키지 설치"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name} 이미 설치됨")
        return True
    except ImportError:
        print(f"📦 {package_name} 설치 중...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"✅ {package_name} 설치 완료")
            return True
        except subprocess.CalledProcessError:
            print(f"❌ {package_name} 설치 실패")
            return False

def check_serial_ports():
    """사용 가능한 시리얼 포트 확인"""
    print("\n🔌 시리얼 포트 확인 중...")
    
    try:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        
        if ports:
            print("사용 가능한 시리얼 포트:")
            for port in ports:
                print(f"   - {port.device}: {port.description}")
        else:
            print("⚠️  감지된 시리얼 포트가 없습니다.")
            print("   OpenCTR을 연결했는지 확인해주세요.")
        
        return True
    except Exception as e:
        print(f"❌ 시리얼 포트 확인 오류: {e}")
        return False

def create_example_config():
    """예제 설정 파일 생성"""
    config_content = '''# Xtark R20 Python Controller 설정 파일
# 이 파일을 수정하여 기본 설정을 변경할 수 있습니다.

[DEFAULT]
# 시리얼 포트 설정
serial_port = /dev/ttyUSB0
baudrate = 230400

# 로봇 타입 (R20_MEC, R20_FWD, R20_AKM, R20_TWD, R20_TAK, R20_OMNI)
robot_type = R20_MEC

# 제어 파라미터
max_linear_velocity = 1.0    # m/s
max_angular_velocity = 2.0   # rad/s

# 센서 업데이트 주기
sensor_update_rate = 20      # Hz

[WINDOWS]
# Windows용 기본 포트
serial_port = COM3

[MACOS]
# macOS용 기본 포트
serial_port = /dev/tty.usbserial-*

[LINUX]
# Linux용 기본 포트
serial_port = /dev/ttyUSB0
'''
    
    config_file = os.path.join(os.path.dirname(__file__), 'config.ini')
    
    if not os.path.exists(config_file):
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            print(f"✅ 설정 파일 생성됨: {config_file}")
            return True
        except Exception as e:
            print(f"❌ 설정 파일 생성 실패: {e}")
            return False
    else:
        print(f"✅ 설정 파일 이미 존재: {config_file}")
        return True

def create_desktop_shortcuts():
    """데스크톱 바로가기 생성 (선택적)"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    shortcuts = [
        ("키보드 제어", "keyboard_control.py"),
        ("자동 제어", "auto_control.py"),
        ("센서 모니터링", "examples/sensor_monitoring.py"),
        ("LED 효과", "examples/led_effects.py"),
        ("테스트 프로그램", "test_controller.py"),
    ]
    
    try:
        desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        
        if not os.path.exists(desktop_dir):
            print("데스크톱 디렉토리를 찾을 수 없습니다.")
            return False
        
        print("\n🖥️  데스크톱 바로가기를 생성하시겠습니까? (y/n): ", end="")
        choice = input().strip().lower()
        
        if choice == 'y':
            for name, script in shortcuts:
                script_path = os.path.join(current_dir, script)
                if os.path.exists(script_path):
                    # 간단한 배치 파일 생성 (Windows)
                    if platform.system() == "Windows":
                        bat_content = f'''@echo off
cd /d "{current_dir}"
python "{script}"
pause
'''
                        bat_file = os.path.join(desktop_dir, f"Xtark R20 {name}.bat")
                        with open(bat_file, 'w', encoding='utf-8') as f:
                            f.write(bat_content)
                    
                    # 쉘 스크립트 생성 (Linux/macOS)
                    else:
                        sh_content = f'''#!/bin/bash
cd "{current_dir}"
python3 "{script}"
read -p "Press Enter to continue..."
'''
                        sh_file = os.path.join(desktop_dir, f"Xtark R20 {name}.sh")
                        with open(sh_file, 'w', encoding='utf-8') as f:
                            f.write(sh_content)
                        os.chmod(sh_file, 0o755)
            
            print("✅ 바로가기 생성 완료")
        else:
            print("바로가기 생성을 건너뜁니다.")
        
        return True
        
    except Exception as e:
        print(f"❌ 바로가기 생성 오류: {e}")
        return False

def show_usage_guide():
    """사용법 안내"""
    print("\n" + "="*60)
    print("📚 사용법 안내")
    print("="*60)
    print("""
주요 프로그램:

1. 키보드 제어:
   python keyboard_control.py [시리얼포트]
   
2. 자동 제어 패턴:
   python auto_control.py [시리얼포트]
   
3. 센서 모니터링:
   python examples/sensor_monitoring.py [시리얼포트]
   
4. LED 효과 데모:
   python examples/led_effects.py [시리얼포트]
   
5. 전체 테스트:
   python test_controller.py [시리얼포트]

기본 사용 예제:
   # Linux/macOS
   python keyboard_control.py /dev/ttyUSB0
   
   # Windows
   python keyboard_control.py COM3

프로그래밍 예제:
   from xtark_r20_controller import XtarkR20Controller, RobotType
   
   controller = XtarkR20Controller('/dev/ttyUSB0')
   if controller.connect():
       controller.set_velocity(0.3, 0.0, 0.0)  # 전진
       time.sleep(1.0)
       controller.set_velocity(0.0, 0.0, 0.0)  # 정지
       controller.disconnect()

더 자세한 정보는 README.md를 참조하세요.
""")

def main():
    """메인 함수"""
    print("🚀 Xtark R20 Python Controller 설정 프로그램")
    print("=" * 60)
    
    # Python 버전 확인
    if not check_python_version():
        return
    
    # 필수 패키지 설치
    print("\n📦 필수 패키지 설치 중...")
    required_packages = [
        ("pyserial", "serial"),
    ]
    
    optional_packages = [
        ("keyboard", "keyboard"),
    ]
    
    # 필수 패키지
    all_success = True
    for package, import_name in required_packages:
        if not install_package(package, import_name):
            all_success = False
    
    # 선택적 패키지
    print("\n📦 선택적 패키지 설치 중...")
    for package, import_name in optional_packages:
        if not install_package(package, import_name):
            print(f"⚠️  {package}는 선택사항입니다. 키보드 제어 기능이 제한될 수 있습니다.")
    
    if not all_success:
        print("\n❌ 일부 필수 패키지 설치에 실패했습니다.")
        print("수동으로 설치해주세요: pip install pyserial")
        return
    
    # 시리얼 포트 확인
    check_serial_ports()
    
    # 설정 파일 생성
    print("\n⚙️  설정 파일 생성 중...")
    create_example_config()
    
    # 바로가기 생성 (선택적)
    create_desktop_shortcuts()
    
    # 사용법 안내
    show_usage_guide()
    
    print("\n🎉 설정 완료!")
    print("이제 Xtark R20 Python Controller를 사용할 수 있습니다.")
    
    # 테스트 실행 여부 확인
    print("\n🧪 연결 테스트를 실행하시겠습니까? (y/n): ", end="")
    choice = input().strip().lower()
    
    if choice == 'y':
        print("\n테스트할 시리얼 포트를 입력하세요 (기본값: /dev/ttyUSB0): ", end="")
        port = input().strip()
        if not port:
            port = '/dev/ttyUSB0'
        
        print(f"\n🔍 {port}에서 OpenCTR 연결 테스트 중...")
        
        try:
            from xtark_r20_controller import XtarkR20Controller, RobotType
            
            controller = XtarkR20Controller(port)
            if controller.connect():
                print("✅ OpenCTR 연결 성공!")
                
                # 간단한 테스트
                print("🤖 LED 테스트 중...")
                controller.set_rgb_light(255, 0, 0)  # 빨간색
                import time
                time.sleep(0.5)
                controller.set_rgb_light(0, 255, 0)  # 녹색
                time.sleep(0.5)
                controller.set_rgb_light(0, 0, 255)  # 파란색
                time.sleep(0.5)
                controller.set_rgb_light(0, 0, 0)    # 끄기
                
                print("🔊 부저 테스트 중...")
                controller.set_beeper(True)
                time.sleep(0.2)
                controller.set_beeper(False)
                
                controller.disconnect()
                print("✅ 모든 테스트 완료!")
            else:
                print("❌ OpenCTR 연결 실패!")
                print("포트 이름과 연결 상태를 확인해주세요.")
                
        except Exception as e:
            print(f"❌ 테스트 오류: {e}")

if __name__ == "__main__":
    main()
