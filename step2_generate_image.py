import requests
import json
import os

print("Generating robot arm image...")

# 저장된 프롬프트 읽기
try:
    with open('robot_arm_prompt.txt', 'r', encoding='utf-8') as f:
        prompt = f.read().strip()
    
    print(f"Using prompt: {prompt[:100]}...")
    
    # 고해상도 이미지 생성 요청
    data = {
        'prompt': prompt,
        'resolution': '1024x1024',
        'num_inference_steps': 20,
        'guidance_scale': 7.5
    }
    
    response = requests.post('http://localhost:8001/create_robot_image', json=data)
    if response.status_code == 200:
        result = response.json()
        print('=== Image Generation Result ===')
        print('Image Path:', result['image_path'])
        print('Generation Time:', result['generation_time'], 'seconds')
        print('Resolution:', result['metadata']['resolution'])
        print('Model:', result['metadata'].get('model', 'Unknown'))
        
        # 이미지 경로를 파일에 저장
        with open('robot_arm_image_path.txt', 'w') as f:
            f.write(result['image_path'])
        
        print('[SUCCESS] Image generated and path saved!')
        
    else:
        print('[ERROR] Failed to generate image:', response.status_code)
        print('Response:', response.text)

except FileNotFoundError:
    print('[ERROR] Prompt file not found. Please run step1 first.')
except Exception as e:
    print('[ERROR] Request failed:', str(e))