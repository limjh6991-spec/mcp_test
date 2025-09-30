"""
로컬 더미 이미지 생성 - 빠른 테스트용
실제 AI 대신 빠른 프로토타입 이미지 생성
"""

from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

def create_robot_mockup(prompt: str, resolution: str = "512x512"):
    """
    로봇 디자인 목업 이미지 생성 (즉시 완성)
    실제 AI 대신 빠른 프로토타입용
    """
    
    print(f"🚀 로봇 목업 이미지 생성 중...")
    print(f"📝 프롬프트: {prompt[:100]}...")
    
    # 해상도 파싱
    width, height = map(int, resolution.split('x'))
    
    # 배경 생성 (그라데이션 효과)
    image = Image.new('RGB', (width, height), color='#1a1a2e')
    draw = ImageDraw.Draw(image)
    
    # 그라데이션 배경
    for y in range(height):
        r = int(26 + (y / height) * 30)
        g = int(26 + (y / height) * 40) 
        b = int(46 + (y / height) * 50)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # 로봇 아암 기본 형태 그리기
    # 베이스
    draw.rectangle([width//4, height*3//4, width*3//4, height-20], 
                  fill='#4a5568', outline='#718096', width=3)
    
    # 관절 1 (베이스)
    center_x = width // 2
    draw.ellipse([center_x-30, height*3//4-15, center_x+30, height*3//4+15], 
                fill='#2d3748', outline='#4a5568', width=2)
    
    # 아암 링크 1
    draw.rectangle([center_x-15, height//2, center_x+15, height*3//4], 
                  fill='#e2e8f0', outline='#cbd5e0', width=2)
    
    # 관절 2
    draw.ellipse([center_x-20, height//2-10, center_x+20, height//2+10], 
                fill='#2d3748', outline='#4a5568', width=2)
    
    # 아암 링크 2
    end_x = center_x + 80
    draw.line([(center_x, height//2), (end_x, height//3)], 
              fill='#e2e8f0', width=30)
    
    # 엔드 이펙터
    draw.ellipse([end_x-25, height//3-25, end_x+25, height//3+25], 
                fill='#f56565', outline='#e53e3e', width=3)
    
    # 그리퍼
    draw.rectangle([end_x-5, height//3-35, end_x+5, height//3-25], 
                  fill='#4a5568')
    draw.rectangle([end_x-5, height//3+25, end_x+5, height//3+35], 
                  fill='#4a5568')
    
    # 제목 텍스트 추가
    try:
        font = ImageFont.load_default()
        text = "INDUSTRIAL ROBOT ARM - PROTOTYPE"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        draw.text(((width - text_width) // 2, 20), text, 
                 fill='#f7fafc', font=font)
        
        # 사양 정보
        specs = [
            "• 6-DOF Articulated Arm",
            "• Payload: 5kg", 
            "• Reach: 800mm",
            "• Repeatability: ±0.1mm"
        ]
        
        for i, spec in enumerate(specs):
            draw.text((20, height - 100 + i * 20), spec, 
                     fill='#e2e8f0', font=font)
            
    except:
        # 폰트 로드 실패 시 기본 텍스트
        draw.text((width//2-50, 20), "ROBOT ARM", fill='white')
    
    # 출력 디렉토리 생성
    os.makedirs("generated_images", exist_ok=True)
    
    # 파일 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    image_path = f"generated_images/robot_mockup_{timestamp}.png"
    image.save(image_path)
    
    result = {
        "success": True,
        "image_path": os.path.abspath(image_path),
        "generation_time": 0.1,  # 즉시 생성
        "api_used": "local_mockup",
        "model": "procedural_generation",
        "resolution": f"{width}x{height}",
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"✅ 목업 이미지 완성! (0.1초)")
    print(f"📁 저장 위치: {image_path}")
    
    return result

def main():
    """메인 실행"""
    
    # 프롬프트 읽기
    try:
        with open('robot_arm_prompt.txt', 'r', encoding='utf-8') as f:
            prompt = f.read().strip()
    except FileNotFoundError:
        prompt = "Industrial robotic arm prototype"
        print("⚠️ 프롬프트 파일 없음. 기본 프롬프트 사용")
    
    print("=" * 60)
    print("🤖 로봇 아암 목업 이미지 생성 (즉시 완성)")
    print("=" * 60)
    
    # 목업 이미지 생성
    result = create_robot_mockup(prompt, resolution="800x600")
    
    print("\n" + "=" * 60)
    print("🎉 프로토타입 이미지 완성!")
    print(f"⚡ 성능: 즉시 생성 ({result['generation_time']}초)")
    print(f"💾 경로: {result['image_path']}")
    print("📝 참고: 실제 AI 생성을 위해서는 클라우드 API 키가 필요합니다")
    print("=" * 60)
    
    return result

if __name__ == "__main__":
    main()