"""
클라우드 API 프록시 모듈
- Stability AI API
- Replicate API  
- Hugging Face Inference API
- 로컬 백업
"""

import os
import requests
import base64
from io import BytesIO
from PIL import Image
from typing import Optional, Dict, Any
import asyncio
import aiohttp
from datetime import datetime

class CloudImageGenerator:
    def __init__(self):
        self.apis = {
            'stability': StabilityAIAPI(),
            'huggingface': HuggingFaceAPI(),
            'replicate': ReplicateAPI(),
            'local': LocalFallbackAPI()
        }
        
    async def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        우선순위에 따라 API 시도:
        1. Stability AI (가장 빠름, 고품질)
        2. Hugging Face (무료, 중간 속도)
        3. Replicate (유료, 고품질)
        4. 로컬 (백업)
        """
        errors = []
        
        for api_name, api in self.apis.items():
            try:
                if api.is_available():
                    print(f"🚀 {api_name} API 사용 중...")
                    result = await api.generate(prompt, **kwargs)
                    result['api_used'] = api_name
                    return result
            except Exception as e:
                error_msg = f"{api_name}: {str(e)}"
                errors.append(error_msg)
                print(f"❌ {error_msg}")
                continue
        
        raise Exception(f"모든 API 실패: {'; '.join(errors)}")

class StabilityAIAPI:
    def __init__(self):
        self.api_key = os.getenv('STABILITY_API_KEY')
        self.base_url = "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        start_time = datetime.now()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "text_prompts": [{"text": prompt}],
            "cfg_scale": kwargs.get('guidance_scale', 7.5),
            "steps": kwargs.get('num_inference_steps', 20),
            "seed": kwargs.get('seed', 0),
            "width": int(kwargs.get('resolution', '1024x1024').split('x')[0]),
            "height": int(kwargs.get('resolution', '1024x1024').split('x')[1])
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    image_data = base64.b64decode(data['artifacts'][0]['base64'])
                    
                    # 이미지 저장
                    image = Image.open(BytesIO(image_data))
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    image_path = f"generated_images/robot_stability_{timestamp}.png"
                    os.makedirs("generated_images", exist_ok=True)
                    image.save(image_path)
                    
                    return {
                        'image_path': os.path.abspath(image_path),
                        'image_base64': base64.b64encode(image_data).decode(),
                        'generation_time': (datetime.now() - start_time).total_seconds(),
                        'model': 'stability-ai-v1.6'
                    }
                else:
                    raise Exception(f"Stability API 오류: {response.status}")

class HuggingFaceAPI:
    def __init__(self):
        self.api_key = os.getenv('HF_API_KEY', 'hf_dummy')  # 무료 사용 가능
        self.model_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
    
    def is_available(self) -> bool:
        return True  # 무료 API
    
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        start_time = datetime.now()
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"inputs": prompt}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.model_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    image_data = await response.read()
                    
                    # 이미지 저장
                    image = Image.open(BytesIO(image_data))
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    image_path = f"generated_images/robot_hf_{timestamp}.png"
                    os.makedirs("generated_images", exist_ok=True)
                    image.save(image_path)
                    
                    return {
                        'image_path': os.path.abspath(image_path),
                        'image_base64': base64.b64encode(image_data).decode(),
                        'generation_time': (datetime.now() - start_time).total_seconds(),
                        'model': 'huggingface-sd-2.1'
                    }
                else:
                    raise Exception(f"HuggingFace API 오류: {response.status}")

class ReplicateAPI:
    def __init__(self):
        self.api_key = os.getenv('REPLICATE_API_KEY')
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        # Replicate API 구현 (유료)
        raise Exception("Replicate API 키 필요")

class LocalFallbackAPI:
    def __init__(self):
        self.pipeline = None
    
    def is_available(self) -> bool:
        return True  # 항상 백업으로 사용 가능
    
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        # 기존 로컬 구현 사용
        from . import pipeline
        if pipeline is None:
            # 더미 이미지 생성
            width, height = map(int, kwargs.get('resolution', '1024x1024').split('x'))
            image = Image.new('RGB', (width, height), color='lightblue')
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_path = f"generated_images/robot_dummy_{timestamp}.png"
            os.makedirs("generated_images", exist_ok=True)
            image.save(image_path)
            
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            
            return {
                'image_path': os.path.abspath(image_path),
                'image_base64': base64.b64encode(buffered.getvalue()).decode(),
                'generation_time': 0.1,
                'model': 'local-dummy'
            }
        else:
            raise Exception("로컬 모델 구현 필요")