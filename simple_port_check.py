#!/usr/bin/env python3
"""
간단한 포트 확인 유틸리티
pyserial이 없어도 기본적인 포트 확인이 가능합니다.

사용법:
    python simple_port_check.py
"""

import os
import platform
import glob
import sys

def check_basic_ports():
    """기본적인 포트 존재 여부 확인"""
    print("🔍 기본 포트 확인 (pyserial 불필요)")
    print("=" * 50)
    
    system = platform.system()
    found_ports = []
    
    if system == "Windows":
        print("Windows 시스템에서는 장치 관리자를 확인하세요:")
        print("1. Win + X 키를 누르고 '장치 관리자' 선택")
        print("2. '포트(COM & LPT)' 섹션 확인")
        print("3. COM 포트 번호를 확인하세요")
        print()
        
        # Windows에서는 COM 포트 파일 확인이 어려우므로 안내만 제공
        for i in range(1, 21):
            port = f"COM{i}"
            print(f"   테스트할 포트: {port}")
        
    elif system == "Darwin":  # macOS
        print("macOS 포트 확인:")
        
        # USB 시리얼 장치
        usb_ports = glob.glob('/dev/tty.usb*') + glob.glob('/dev/cu.usb*')
        
        if usb_ports:
            print("✅ USB 시리얼 포트 발견:")
            for port in usb_ports:
                print(f"   {port}")
                found_ports.append(port)
        else:
            print("❌ USB 시리얼 포트를 찾을 수 없습니다.")
        
        # 기타 시리얼 포트
        other_ports = glob.glob('/dev/tty.*') + glob.glob('/dev/cu.*')
        if other_ports:
            print(f"\n📋 기타 시리얼 포트 ({len(other_ports)}개):")
            for port in other_ports[:10]:  # 처음 10개만 표시
                print(f"   {port}")
        
    else:  # Linux
        print("Linux 포트 확인:")
        
        # USB 포트
        usb_ports = glob.glob('/dev/ttyUSB*')
        if usb_ports:
            print("✅ USB 포트 발견:")
            for port in usb_ports:
                print(f"   {port}")
                found_ports.append(port)
        else:
            print("❌ USB 포트(/dev/ttyUSB*)를 찾을 수 없습니다.")
        
        # ACM 포트 (Arduino 등)
        acm_ports = glob.glob('/dev/ttyACM*')
        if acm_ports:
            print("✅ ACM 포트 발견:")
            for port in acm_ports:
                print(f"   {port}")
                found_ports.append(port)
        else:
            print("❌ ACM 포트(/dev/ttyACM*)를 찾을 수 없습니다.")
        
        # 기본 시리얼 포트
        serial_ports = glob.glob('/dev/ttyS*')
        if serial_ports:
            print(f"📋 기본 시리얼 포트 ({len(serial_ports)}개):")
            for port in serial_ports[:5]:  # 처음 5개만 표시
                print(f"   {port}")
    
    return found_ports

def check_port_permissions(ports):
    """포트 권한 확인 (Linux/macOS)"""
    if platform.system() in ["Linux", "Darwin"] and ports:
        print(f"\n🔐 포트 권한 확인:")
        print("-" * 30)
        
        for port in ports:
            try:
                if os.path.exists(port):
                    if os.access(port, os.R_OK | os.W_OK):
                        print(f"✅ {port} - 읽기/쓰기 가능")
                    else:
                        print(f"❌ {port} - 권한 없음")
                        print(f"   💡 권한 부여: sudo chmod 666 {port}")
                else:
                    print(f"❌ {port} - 존재하지 않음")
            except Exception as e:
                print(f"❌ {port} - 확인 오류: {e}")

def check_usb_devices():
    """USB 장치 확인 (Linux/macOS)"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        print(f"\n💻 macOS USB 장치 확인:")
        print("-" * 30)
        
        try:
            import subprocess
            result = subprocess.run(['system_profiler', 'SPUSBDataType'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                usb_devices = []
                current_device = None
                
                for line in lines:
                    line = line.strip()
                    if 'Product ID:' in line or 'Vendor ID:' in line:
                        if current_device:
                            usb_devices.append(current_device)
                        current_device = line
                    elif current_device and ('Serial Number:' in line or 'Location ID:' in line):
                        current_device += ' | ' + line
                
                if usb_devices:
                    print("USB 장치들:")
                    for device in usb_devices[:10]:  # 처음 10개만
                        print(f"   {device}")
                else:
                    print("USB 장치 정보를 파싱할 수 없습니다.")
            else:
                print("system_profiler 실행 실패")
                
        except Exception as e:
            print(f"USB 장치 확인 오류: {e}")
    
    elif system == "Linux":
        print(f"\n💻 Linux USB 장치 확인:")
        print("-" * 30)
        
        try:
            import subprocess
            result = subprocess.run(['lsusb'], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                print("USB 장치들:")
                for line in lines:
                    if line.strip():
                        print(f"   {line}")
            else:
                print("lsusb 명령 실행 실패")
                
        except Exception as e:
            print(f"USB 장치 확인 오류: {e}")

def check_dmesg_logs():
    """시스템 로그에서 USB 연결 확인 (Linux/macOS)"""
    system = platform.system()
    
    if system == "Linux":
        print(f"\n📋 최근 USB 연결 로그 (dmesg):")
        print("-" * 40)
        
        try:
            import subprocess
            # 최근 USB 관련 로그만 확인
            result = subprocess.run(['dmesg', '|', 'grep', '-i', 'usb', '|', 'tail', '-10'], 
                                  shell=True, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    print(f"   {line}")
            else:
                print("USB 관련 로그를 찾을 수 없습니다.")
                
        except Exception as e:
            print(f"dmesg 확인 오류: {e}")

def manual_test_suggestions():
    """수동 테스트 제안"""
    print(f"\n🛠️  수동 확인 방법:")
    print("=" * 50)
    
    system = platform.system()
    
    if system == "Windows":
        print("Windows:")
        print("1. 장치 관리자 열기 (Win + X → 장치 관리자)")
        print("2. '포트(COM & LPT)' 확장")
        print("3. OpenCTR 장치 확인")
        print("4. COM 포트 번호 기록")
        print("5. 드라이버 상태 확인")
        
    elif system == "Darwin":  # macOS
        print("macOS:")
        print("1. 터미널에서 다음 명령 실행:")
        print("   ls /dev/tty.* | grep -i usb")
        print("   ls /dev/cu.* | grep -i usb")
        print("2. 시스템 정보 → USB 확인:")
        print("   system_profiler SPUSBDataType")
        print("3. OpenCTR 연결 전후 비교")
        
    else:  # Linux
        print("Linux:")
        print("1. 터미널에서 다음 명령 실행:")
        print("   ls /dev/ttyUSB*")
        print("   ls /dev/ttyACM*")
        print("2. USB 장치 확인:")
        print("   lsusb")
        print("3. 연결 로그 확인:")
        print("   dmesg | grep -i usb | tail -10")
        print("4. 권한 확인 및 부여:")
        print("   sudo chmod 666 /dev/ttyUSB0")
        print("   sudo usermod -a -G dialout $USER")

def main():
    """메인 함수"""
    print("🔍 Xtark R20 포트 확인 유틸리티 (Simple)")
    print("=" * 60)
    
    print(f"💻 시스템: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print()
    
    # 기본 포트 확인
    found_ports = check_basic_ports()
    
    # 권한 확인
    if found_ports:
        check_port_permissions(found_ports)
    
    # USB 장치 확인
    check_usb_devices()
    
    # 시스템 로그 확인
    check_dmesg_logs()
    
    # 수동 테스트 제안
    manual_test_suggestions()
    
    # 결과 요약
    print(f"\n📊 요약:")
    print("=" * 60)
    if found_ports:
        print(f"✅ 발견된 포트: {len(found_ports)}개")
        for port in found_ports:
            print(f"   - {port}")
        
        print(f"\n💡 다음 명령으로 테스트하세요:")
        for port in found_ports[:3]:  # 처음 3개만
            print(f"   python port_scanner.py  # 상세 테스트")
            print(f"   python examples/sensor_monitoring.py {port}")
            break
    else:
        print("❌ 사용 가능한 포트를 찾을 수 없습니다.")
        print("\n🔧 해결 방법:")
        print("1. OpenCTR이 올바르게 연결되었는지 확인")
        print("2. USB 케이블이 데이터 전송용인지 확인")
        print("3. 드라이버가 설치되었는지 확인")
        print("4. 다른 프로그램이 포트를 사용하고 있지 않은지 확인")

if __name__ == "__main__":
    main()
