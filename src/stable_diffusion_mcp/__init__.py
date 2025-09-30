from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
from diffusers import StableDiffusionPipeline
import os
from datetime import datetime
from typing import Optional
import base64
from io import BytesIO
from PIL import Image
import requests
import asyncio

app = FastAPI(title="Stable Diffusion MCP (Cloud Enhanced)", version="2.0.0")

# 글로벌 파이프라인 변수
pipeline = None

# 클라우드 API 설정
CLOUD_APIS = {
    'huggingface': {
        'enabled': True,
        'url': 'https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1',
        'key': os.getenv('HF_API_KEY', 'hf_dummy')
    },
    'stability': {
        'enabled': bool(os.getenv('STABILITY_API_KEY')),
        'url': 'https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image',
        'key': os.getenv('STABILITY_API_KEY')
    }
}

class ImageRequest(BaseModel):
    prompt: str
    resolution: str = '1024x1024'
    num_inference_steps: int = 20
    guidance_scale: float = 7.5
    seed: Optional[int] = None
    negative_prompt: Optional[str] = "blurry, low quality, distorted"

class ImageResponse(BaseModel):
    image_path: str
    image_base64: Optional[str] = None
    metadata: dict
    generation_time: float

def initialize_pipeline():
    """Stable Diffusion 파이프라인 초기화"""
    global pipeline
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"GPU 사용 가능: {torch.cuda.is_available()}, 디바이스: {device}")
        
        # Stable Diffusion 2.1 모델 로드
        model_id = "stabilityai/stable-diffusion-2-1"
        pipeline = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32
        )
        pipeline = pipeline.to(device)
        
        # 메모리 최적화
        if device == "cuda":
            pipeline.enable_attention_slicing()
            pipeline.enable_model_cpu_offload()
            
        print("Stable Diffusion 파이프라인 초기화 완료")
        return True
    except Exception as e:
        print(f"파이프라인 초기화 실패: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 파이프라인 초기화"""
    success = initialize_pipeline()
    if not success:
        print("경고: Stable Diffusion 파이프라인 초기화 실패. 더미 모드로 실행됩니다.")

async def generate_with_huggingface(prompt: str, **kwargs):
    """HuggingFace Inference API로 이미지 생성 (무료, 빠름)"""
    api_config = CLOUD_APIS['huggingface']
    headers = {"Authorization": f"Bearer {api_config['key']}"}
    payload = {"inputs": prompt}
    
    response = requests.post(api_config['url'], headers=headers, json=payload, timeout=30)
    
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"HuggingFace API 오류: {response.status_code}")

async def generate_with_stability(prompt: str, **kwargs):
    """Stability AI API로 이미지 생성 (유료, 최고품질)"""
    api_config = CLOUD_APIS['stability']
    if not api_config['enabled']:
        raise Exception("Stability API 키 없음")
    
    headers = {
        "Authorization": f"Bearer {api_config['key']}",
        "Content-Type": "application/json"
    }
    
    width, height = map(int, kwargs.get('resolution', '1024x1024').split('x'))
    payload = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": kwargs.get('guidance_scale', 7.5),
        "steps": kwargs.get('num_inference_steps', 20),
        "width": width,
        "height": height
    }
    
    response = requests.post(api_config['url'], headers=headers, json=payload, timeout=60)
    
    if response.status_code == 200:
        data = response.json()
        return base64.b64decode(data['artifacts'][0]['base64'])
    else:
        raise Exception(f"Stability API 오류: {response.status_code}")

@app.post('/create_robot_image', response_model=ImageResponse)
async def create_robot_image(request: ImageRequest):
    """
    프롬프트를 기반으로 3D 로봇 이미지 생성
    우선순위: HuggingFace API → Stability AI → 로컬 → 더미
    """
    start_time = datetime.now()
    
    try:
        # 해상도 파싱
        width, height = map(int, request.resolution.split('x'))
        
        # 출력 디렉토리 생성
        output_dir = "generated_images"
        os.makedirs(output_dir, exist_ok=True)
        
        image_data = None
        api_used = "none"
        
        # 1순위: HuggingFace API (무료, 빠름)
        try:
            print("🚀 HuggingFace API 시도 중...")
            image_data = await generate_with_huggingface(request.prompt, resolution=request.resolution)
            api_used = "huggingface"
            print("✅ HuggingFace API 성공!")
        except Exception as e:
            print(f"❌ HuggingFace API 실패: {e}")
            
            # 2순위: Stability AI API (유료, 고품질)
            try:
                print("🚀 Stability AI API 시도 중...")
                image_data = await generate_with_stability(request.prompt, 
                                                         resolution=request.resolution,
                                                         guidance_scale=request.guidance_scale,
                                                         num_inference_steps=request.num_inference_steps)
                api_used = "stability"
                print("✅ Stability AI API 성공!")
            except Exception as e2:
                print(f"❌ Stability AI API 실패: {e2}")
                
                # 3순위: 로컬 파이프라인
                if pipeline is not None:
                    try:
                        print("🚀 로컬 파이프라인 시도 중...")
                        generator = torch.Generator().manual_seed(request.seed) if request.seed else None
                        
                        image = pipeline(
                            prompt=request.prompt,
                            negative_prompt=request.negative_prompt,
                            num_inference_steps=request.num_inference_steps,
                            guidance_scale=request.guidance_scale,
                            width=width,
                            height=height,
                            generator=generator
                        ).images[0]
                        
                        buffered = BytesIO()
                        image.save(buffered, format="PNG")
                        image_data = buffered.getvalue()
                        api_used = "local"
                        print("✅ 로컬 파이프라인 성공!")
                    except Exception as e3:
                        print(f"❌ 로컬 파이프라인 실패: {e3}")
        
        # 이미지 처리
        if image_data:
            image = Image.open(BytesIO(image_data))
        else:
            # 4순위: 더미 이미지 (최종 백업)
            print("🔧 더미 이미지 생성 중...")
            image = Image.new('RGB', (width, height), color='lightblue')
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            image_data = buffered.getvalue()
            api_used = "dummy"
        
        # 이미지 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_path = os.path.join(output_dir, f"robot_{api_used}_{timestamp}.png")
        
        image.save(image_path)
        
        # Base64 인코딩 (선택적)
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # 생성 시간 계산
        generation_time = (datetime.now() - start_time).total_seconds()
        
        # 메타데이터
        metadata = {
            "prompt": request.prompt,
            "resolution": request.resolution,
            "steps": request.num_inference_steps,
            "guidance_scale": request.guidance_scale,
            "seed": request.seed,
            "api_used": api_used,
            "device": "cuda" if torch.cuda.is_available() else "cpu",
            "model": f"{api_used}-api" if api_used != "local" else "stabilityai/stable-diffusion-2-1",
            "timestamp": datetime.now().isoformat()
        }
        
        return ImageResponse(
            image_path=os.path.abspath(image_path),
            image_base64=img_base64,
            metadata=metadata,
            generation_time=generation_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이미지 생성 실패: {str(e)}")

@app.get('/supported_resolutions')
async def get_supported_resolutions():
    """지원되는 해상도 목록 반환"""
    return {
        "resolutions": [
            "512x512", "768x768", "1024x1024", 
            "512x768", "768x512", "1024x768", "768x1024"
        ],
        "recommended": "1024x1024"
    }

@app.get('/health')
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "healthy",
        "service": "stable_diffusion_mcp",
        "gpu_available": torch.cuda.is_available(),
        "pipeline_loaded": pipeline is not None
    }
