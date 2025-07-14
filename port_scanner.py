#!/usr/bin/env python3
"""
시리얼 포트 검색 및 테스트 유틸리티
연결된 모든 시리얼 포트를 찾고 OpenCTR 장치를 식별합니다.

사용법:
    python port_scanner.py
"""

import sys
import time
import platform

def find_serial_ports():
    """사용 가능한 시리얼 포트 찾기"""
    ports = []
    
    try:
        import serial.tools.list_ports
        available_ports = serial.tools.list_ports.comports()
        
        print("🔌 시리얼 포트 스캔 결과:")
        print("=" * 60)
        
        if not available_ports:
            print("❌ 감지된 시리얼 포트가 없습니다.")
            return ports
        
        for i, port in enumerate(available_ports, 1):
            print(f"{i}. 포트: {port.device}")
            print(f"   설명: {port.description}")
            print(f"   제조사: {port.manufacturer or 'Unknown'}")
            print(f"   VID:PID: {port.vid:04X}:{port.pid:04X}" if port.vid and port.pid else "   VID:PID: Unknown")
            print(f"   시리얼번호: {port.serial_number or 'Unknown'}")
            
            # OpenCTR 관련 키워드 확인
            keywords = ['USB', 'Serial', 'UART', 'CH340', 'CP210', 'FTDI', 'Arduino']
            is_likely_openctr = any(keyword.lower() in (port.description or '').lower() for keyword in keywords)
            
            if is_likely_openctr:
                print("   🎯 OpenCTR일 가능성이 높습니다!")
            
            print("-" * 60)
            ports.append(port.device)
        
        return ports
        
    except ImportError:
        print("❌ pyserial 라이브러리가 설치되지 않았습니다.")
        print("다음 명령으로 설치하세요: pip install pyserial")
        return []
    except Exception as e:
        print(f"❌ 포트 스캔 오류: {e}")
        return []

def manual_port_check():
    """수동으로 일반적인 포트들 확인"""
    print("\n🔍 수동 포트 확인:")
    print("=" * 60)
    
    # 플랫폼별 일반적인 포트들
    if platform.system() == "Windows":
        test_ports = [f"COM{i}" for i in range(1, 21)]  # COM1-COM20
    elif platform.system() == "Darwin":  # macOS
        import glob
        test_ports = glob.glob('/dev/tty.usb*') + glob.glob('/dev/cu.usb*') + ['/dev/ttyUSB0', '/dev/ttyACM0']
    else:  # Linux
        import glob
        test_ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyS*')
    
    available_ports = []
    
    for port in test_ports:
        try:
            import serial
            with serial.Serial(port, timeout=0.1) as ser:
                available_ports.append(port)
                print(f"✅ {port} - 사용 가능")
        except (serial.SerialException, FileNotFoundError, PermissionError):
            pass  # 포트가 없거나 사용 중
        except ImportError:
            print("❌ pyserial이 설치되지 않았습니다.")
            break
    
    if not available_ports:
        print("❌ 사용 가능한 포트를 찾을 수 없습니다.")
    
    return available_ports

def test_port_connection(port):
    """특정 포트에서 OpenCTR 통신 테스트"""
    print(f"\n🧪 {port} 포트 테스트 중...")
    print("-" * 40)
    
    try:
        import serial
        
        # 다양한 보드레이트로 테스트
        baudrates = [230400, 115200, 57600, 38400, 19200, 9600]
        
        for baudrate in baudrates:
            try:
                print(f"   보드레이트 {baudrate} 테스트...", end="")
                
                with serial.Serial(port, baudrate, timeout=1.0) as ser:
                    time.sleep(0.1)  # 연결 안정화
                    
                    # 간단한 테스트 패킷 전송 (로봇 타입 설정)
                    test_packet = bytes([0xAA, 0x55, 0x5A, 0x01, 0x01, 0x00])  # 헤더 + 명령 + 데이터 + 체크섬
                    ser.write(test_packet)
                    
                    # 응답 대기
                    response = ser.read(20)
                    
                    if len(response) > 0:
                        print(f" ✅ 응답 있음 ({len(response)} bytes)")
                        print(f"      응답 데이터: {' '.join([f'{b:02X}' for b in response])}")
                        return baudrate
                    else:
                        print(" ❌ 응답 없음")
                        
            except serial.SerialException as e:
                print(f" ❌ 오류: {e}")
                continue
            except Exception as e:
                print(f" ❌ 예외: {e}")
                continue
        
        print(f"   {port}에서 OpenCTR 응답을 받지 못했습니다.")
        return None
        
    except ImportError:
        print("❌ pyserial이 설치되지 않았습니다.")
        return None
    except Exception as e:
        print(f"❌ 테스트 오류: {e}")
        return None

def check_permissions(port):
    """포트 권한 확인 (Linux/macOS)"""
    if platform.system() in ["Linux", "Darwin"]:
        import os
        import stat
        
        try:
            st = os.stat(port)
            mode = st.st_mode
            
            print(f"\n🔐 {port} 권한 정보:")
            print(f"   파일 모드: {stat.filemode(mode)}")
            print(f"   소유자: {st.st_uid}")
            print(f"   그룹: {st.st_gid}")
            
            # 읽기/쓰기 권한 확인
            if os.access(port, os.R_OK | os.W_OK):
                print("   ✅ 읽기/쓰기 권한 있음")
                return True
            else:
                print("   ❌ 읽기/쓰기 권한 없음")
                print(f"   💡 권한 부여 방법: sudo chmod 666 {port}")
                print(f"   💡 또는 사용자를 dialout 그룹에 추가: sudo usermod -a -G dialout $USER")
                return False
                
        except FileNotFoundError:
            print(f"❌ {port} 파일을 찾을 수 없습니다.")
            return False
        except Exception as e:
            print(f"❌ 권한 확인 오류: {e}")
            return False
    
    return True  # Windows는 별도 권한 확인 불필요

def system_info():
    """시스템 정보 출력"""
    print("💻 시스템 정보:")
    print("=" * 60)
    print(f"운영체제: {platform.system()} {platform.release()}")
    print(f"Python 버전: {sys.version}")
    print(f"아키텍처: {platform.machine()}")
    
    # pyserial 버전 확인
    try:
        import serial
        print(f"pyserial: 설치됨")
        
        # pyserial 버전 확인 시도
        try:
            import pkg_resources
            version = pkg_resources.get_distribution("pyserial").version
            print(f"pyserial 버전: {version}")
        except:
            print("pyserial 버전: 확인 불가")
            
    except ImportError:
        print("pyserial: 설치되지 않음")

def interactive_test():
    """대화형 포트 테스트"""
    print("\n🎮 대화형 포트 테스트")
    print("=" * 60)
    
    # 포트 스캔
    ports = find_serial_ports()
    
    if not ports:
        ports = manual_port_check()
    
    if not ports:
        print("\n❌ 테스트할 포트가 없습니다.")
        return
    
    print(f"\n📋 발견된 포트: {len(ports)}개")
    for i, port in enumerate(ports, 1):
        print(f"{i}. {port}")
    
    # 사용자 선택
    try:
        print(f"\n테스트할 포트 번호를 선택하세요 (1-{len(ports)}, 0=모두 테스트): ", end="")
        choice = int(input())
        
        if choice == 0:
            # 모든 포트 테스트
            print("\n🔄 모든 포트 테스트 중...")
            for port in ports:
                check_permissions(port)
                baudrate = test_port_connection(port)
                if baudrate:
                    print(f"🎉 {port}에서 OpenCTR 발견! (보드레이트: {baudrate})")
                print()
        elif 1 <= choice <= len(ports):
            # 선택된 포트만 테스트
            selected_port = ports[choice - 1]
            check_permissions(selected_port)
            baudrate = test_port_connection(selected_port)
            if baudrate:
                print(f"🎉 {selected_port}에서 OpenCTR 발견! (보드레이트: {baudrate})")
                
                # 연결 명령 제안
                print(f"\n💡 다음 명령으로 연결하세요:")
                print(f"   python keyboard_control.py {selected_port}")
                print(f"   python examples/sensor_monitoring.py {selected_port}")
        else:
            print("❌ 잘못된 선택입니다.")
            
    except ValueError:
        print("❌ 숫자를 입력해주세요.")
    except KeyboardInterrupt:
        print("\n\n👋 종료합니다.")

def main():
    """메인 함수"""
    print("🔍 Xtark R20 시리얼 포트 스캐너")
    print("=" * 60)
    
    # 시스템 정보
    system_info()
    print()
    
    # 포트 검색 및 테스트
    interactive_test()
    
    print("\n" + "=" * 60)
    print("📚 도움말:")
    print("- OpenCTR이 연결되어 있는지 확인하세요")
    print("- USB 케이블이 데이터 전송을 지원하는지 확인하세요")
    print("- 드라이버가 설치되어 있는지 확인하세요")
    print("- 다른 프로그램이 포트를 사용하고 있지 않은지 확인하세요")

if __name__ == "__main__":
    main()
