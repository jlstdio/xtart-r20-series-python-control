#!/usr/bin/env python3
"""
Xtark R20 LED 효과 예제
다양한 LED 패턴과 효과를 보여줍니다.
"""
import sys
import os
import time
import math
import random

# 상위 디렉토리의 모듈 import를 위한 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xtark_r20_controller import XtarkR20Controller, RobotType

class LEDEffects:
    """LED 효과 클래스"""
    def __init__(self, controller: XtarkR20Controller):
        self.controller = controller
    
    def rainbow_cycle(self, duration: float = 5.0):
        """무지개 색상 순환"""
        print("🌈 무지개 효과 시작...")
        start_time = time.time()
        
        while time.time() - start_time < duration:
            # 현재 시간을 기반으로 색상 계산 (HSV -> RGB)
            hue = (time.time() - start_time) / duration * 360
            r, g, b = self._hsv_to_rgb(hue, 1.0, 1.0)
            
            self.controller.set_rgb_light(r, g, b)
            time.sleep(0.05)  # 20Hz 업데이트
        
        print("무지개 효과 완료")
    
    def breathing_effect(self, color: tuple = (0, 0, 255), duration: float = 4.0):
        """호흡 효과 (컨트롤러 내장 기능 사용)"""
        print(f"💨 호흡 효과 시작... 색상: RGB{color}")
        r, g, b = color
        # PDF p.24, mode 0x02는 호흡 효과 
        self.controller.set_rgb_light(r, g, b, mode=2)
        time.sleep(duration)
        print("호흡 효과 완료")
    
    def strobe_effect(self, color: tuple = (255, 255, 255), strobe_count: int = 10):
        """스트로브 효과"""
        print(f"⚡ 스트로브 효과 시작... 색상: RGB{color}, 횟수: {strobe_count}")
        r, g, b = color
        
        for i in range(strobe_count):
            # 켜기
            self.controller.set_rgb_light(r, g, b)
            time.sleep(0.1)
            
            # 끄기
            self.controller.set_rgb_light(0, 0, 0)
            time.sleep(0.1)
        
        print("스트로브 효과 완료")
    
    def police_lights(self, duration: float = 5.0):
        """경찰차 라이트 효과 (컨트롤러 내장 기능 사용)"""
        print("🚔 경찰차 라이트 효과 시작...")
        # PDF p.24, mode 0x04는 경광등 효과 
        self.controller.set_rgb_light(0, 0, 0, mode=4)
        time.sleep(duration)
        print("경찰차 라이트 효과 완료")
    
    def fire_effect(self, duration: float = 4.0):
        """불 효과 (빨간색-주황색 랜덤)"""
        print("🔥 불 효과 시작...")
        start_time = time.time()
        
        import random
        
        while time.time() - start_time < duration:
            # 빨간색을 기본으로 주황색 계열 랜덤 생성
            r = random.randint(200, 255)
            g = random.randint(0, 100)
            b = 0
            
            self.controller.set_rgb_light(r, g, b)
            time.sleep(0.1)
        
        print("불 효과 완료")
    
    def party_mode(self, duration: float = 10.0):
        """파티 모드 (랜덤 색상 + 부저)"""
        print("🎉 파티 모드 시작...")
        start_time = time.time()
        
        import random
        
        while time.time() - start_time < duration:
            # 랜덤 색상
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            
            self.controller.set_rgb_light(r, g, b)
            
            # 가끔 부저 울리기
            if random.random() < 0.3:  # 30% 확률
                self.controller.set_beeper(True)
                time.sleep(0.1)
                self.controller.set_beeper(False)
            
            time.sleep(0.2)
        
        print("파티 모드 완료")
    
    def color_wave(self, duration: float = 6.0):
        """색상 웨이브 효과"""
        print("🌊 색상 웨이브 효과 시작...")
        start_time = time.time()
        
        colors = [
            (255, 0, 0),    # 빨간색
            (255, 127, 0),  # 주황색
            (255, 255, 0),  # 노란색
            (0, 255, 0),    # 녹색
            (0, 0, 255),    # 파란색
            (75, 0, 130),   # 남색
            (148, 0, 211),  # 보라색
        ]
        
        while time.time() - start_time < duration:
            for color in colors:
                if time.time() - start_time >= duration:
                    break
                
                r, g, b = color
                self.controller.set_rgb_light(r, g, b)
                time.sleep(0.3)
        
        print("색상 웨이브 효과 완료")
    
    def _hsv_to_rgb(self, h: float, s: float, v: float) -> tuple:
        """HSV를 RGB로 변환"""
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(h / 360.0, s, v)
        return int(r * 255), int(g * 255), int(b * 255)

def show_menu():
    """메뉴 표시"""
    print("\n" + "="*50)
    print("       Xtark R20 LED 효과 데모")
    print("="*50)
    print("1. 무지개 순환 효과")
    print("2. 호흡 효과 (파란색)")
    print("3. 스트로브 효과")
    print("4. 경찰차 라이트")
    print("5. 불 효과")
    print("6. 파티 모드")
    print("7. 색상 웨이브")
    print("8. 모든 효과 순차 실행")
    print("9. LED 끄기")
    print("0. 종료")
    print("-" * 50)

def main():
    """메인 함수"""
    # 시리얼 포트 설정
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    
    print(f"Xtark R20 LED 효과 데모 프로그램")
    print(f"시리얼 포트: {port}")
    
    # 컨트롤러 생성 및 연결
    controller = XtarkR20Controller(port, robot_type=RobotType.R20_MEC)
    
    if not controller.connect():
        print("OpenCTR 연결 실패!")
        return
    
    # LED 효과 객체 생성
    led_effects = LEDEffects(controller)
    
    try:
        while True:
            show_menu()
            choice = input("선택하세요 (0-9): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                led_effects.rainbow_cycle()
            elif choice == '2':
                led_effects.breathing_effect()
            elif choice == '3':
                led_effects.strobe_effect()
            elif choice == '4':
                led_effects.police_lights()
            elif choice == '5':
                led_effects.fire_effect()
            elif choice == '6':
                led_effects.party_mode()
            elif choice == '7':
                led_effects.color_wave()
            elif choice == '8':
                print("\n🎪 모든 효과 순차 실행 시작...")
                led_effects.rainbow_cycle(3.0)
                time.sleep(0.5)
                led_effects.breathing_effect(duration=2.0)
                time.sleep(0.5)
                led_effects.strobe_effect(strobe_count=5)
                time.sleep(0.5)
                led_effects.police_lights(3.0)
                time.sleep(0.5)
                led_effects.fire_effect(2.0)
                time.sleep(0.5)
                led_effects.color_wave(3.0)
                print("🎪 모든 효과 완료!")
            elif choice == '9':
                controller.set_rgb_light(0, 0, 0)
                print("💡 LED 꺼짐")
            else:
                print("잘못된 선택입니다.")
            
            # LED 끄기
            controller.set_rgb_light(0, 0, 0)
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n\n프로그램 종료 중...")
    finally:
        # LED 끄기
        controller.set_rgb_light(0, 0, 0)
        controller.disconnect()
        print("프로그램 종료됨")

if __name__ == "__main__":
    main()
