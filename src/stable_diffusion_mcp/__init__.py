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

app = FastAPI(title="Stable Diffusion MCP", version="1.0.0")

# 글로벌 파이프라인 변수
pipeline = None

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

@app.post('/create_robot_image', response_model=ImageResponse)
async def create_robot_image(request: ImageRequest):
    """
    프롬프트를 기반으로 3D 로봇 이미지 생성
    """
    start_time = datetime.now()
    
    try:
        # 해상도 파싱
        width, height = map(int, request.resolution.split('x'))
        
        # 출력 디렉토리 생성
        output_dir = "generated_images"
        os.makedirs(output_dir, exist_ok=True)
        
        if pipeline is None:
            # 더미 이미지 생성 (파이프라인이 없는 경우)
            image = Image.new('RGB', (width, height), color='lightgray')
            image_path = os.path.join(output_dir, f"dummy_robot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        else:
            # 실제 이미지 생성
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
            
            # 이미지 저장
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_path = os.path.join(output_dir, f"robot_{timestamp}.png")
        
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
            "device": "cuda" if torch.cuda.is_available() else "cpu",
            "model": "stabilityai/stable-diffusion-2-1" if pipeline else "dummy",
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
