import requests
import json

# 산업용 로봇 팔 디자인 요청
data = {
    'goal': 'industrial robotic arm for precision manufacturing and assembly operations',
    'style_guide': 'industrial',
    'complexity': 'high',
    'color_scheme': 'metallic silver and safety orange'
}

print("Generating enhanced prompt for industrial robotic arm...")

try:
    response = requests.post('http://localhost:8000/generate_3d_robot_prompt', json=data)
    if response.status_code == 200:
        result = response.json()
        print('=== Generated Prompt ===')
        print('Original:', result['prompt'])
        print()
        print('Enhanced:', result['enhanced_prompt'])
        
        # 프롬프트를 파일에 저장
        with open('robot_arm_prompt.txt', 'w', encoding='utf-8') as f:
            f.write(result['enhanced_prompt'])
        print()
        print('[SUCCESS] Prompt saved to robot_arm_prompt.txt')
        
        # 다음 단계를 위해 프롬프트를 반환
        with open('current_prompt.txt', 'w', encoding='utf-8') as f:
            f.write(result['enhanced_prompt'])
            
    else:
        print('[ERROR] Failed to generate prompt:', response.status_code)
        print('Response:', response.text)
except Exception as e:
    print('[ERROR] Request failed:', str(e))