from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from typing import Optional

app = FastAPI(title="Prompt Generator MCP", version="1.0.0")

class PromptRequest(BaseModel):
    goal: str
    style_guide: str = 'photorealistic'
    complexity: str = 'medium'
    color_scheme: Optional[str] = None

class PromptResponse(BaseModel):
    prompt: str
    enhanced_prompt: str
    metadata: dict

@app.post('/generate_3d_robot_prompt', response_model=PromptResponse)
async def generate_3d_robot_prompt(request: PromptRequest):
    """
    고수준 목표를 3D 로봇 이미지 생성용 상세 프롬프트로 변환
    """
    try:
        # 기본 프롬프트 생성
        base_prompt = f"3D robot design, {request.style_guide} style, {request.goal}"
        
        # 규칙 기반 프롬프트 향상
        style_mappings = {
            "photorealistic": "photorealistic, hyperrealistic, 8K resolution, detailed textures",
            "cyberpunk": "cyberpunk style, neon lights, futuristic, dark atmosphere, glowing elements",
            "industrial": "industrial design, metallic surfaces, mechanical parts, practical functionality",
            "clean": "clean design, minimalist, white background, modern aesthetics",
            "realistic": "realistic rendering, proper lighting, detailed materials"
        }
        
        complexity_mappings = {
            "low": "simple design, basic shapes, minimal details",
            "medium": "moderate complexity, balanced detail level, functional elements",
            "high": "highly detailed, complex mechanical parts, intricate design elements"
        }
        
        # 향상된 프롬프트 생성
        enhanced_prompt = f"{base_prompt}, {style_mappings.get(request.style_guide, 'detailed rendering')}"
        enhanced_prompt += f", {complexity_mappings.get(request.complexity, 'moderate detail')}"
        enhanced_prompt += ", professional 3D rendering, studio lighting, high quality"
        
        # 색상 스키마 추가
        if request.color_scheme:
            enhanced_prompt += f", color scheme: {request.color_scheme}"
            
        # 메타데이터 생성
        metadata = {
            "original_goal": request.goal,
            "style_guide": request.style_guide,
            "complexity": request.complexity,
            "timestamp": "2025-09-29",
            "prompt_length": len(enhanced_prompt)
        }
        
        return PromptResponse(
            prompt=base_prompt,
            enhanced_prompt=enhanced_prompt,
            metadata=metadata
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프롬프트 생성 실패: {str(e)}")

@app.get('/health')
async def health_check():
    """서버 상태 확인"""
    return {"status": "healthy", "service": "prompt_generator_mcp"}
