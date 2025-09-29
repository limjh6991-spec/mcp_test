import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# 각 MCP 서버 모듈 임포트
try:
    from prompt_generator_mcp import app as prompt_app
    from stable_diffusion_mcp import app as diffusion_app
    from blender_mcp import app as blender_app
except ImportError as e:
    pytest.skip(f"모듈 임포트 실패: {e}", allow_module_level=True)

class TestPromptGeneratorMCP:
    """프롬프트 생성기 단위 테스트"""
    
    def setup_method(self):
        self.client = TestClient(prompt_app)
    
    def test_health_endpoint(self):
        """헬스 체크 엔드포인트 테스트"""
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_generate_prompt_basic(self):
        """기본 프롬프트 생성 테스트"""
        test_data = {
            "goal": "cleaning robot",
            "style_guide": "modern"
        }
        
        response = self.client.post("/generate_3d_robot_prompt", json=test_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "prompt" in data
        assert "enhanced_prompt" in data
        assert "metadata" in data
        assert data["metadata"]["original_goal"] == "cleaning robot"
    
    @patch('openai.chat.completions.create')
    def test_generate_prompt_with_openai(self, mock_openai):
        """OpenAI API와 함께 프롬프트 생성 테스트"""
        # Mock OpenAI 응답
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Enhanced robot prompt with AI details"
        mock_openai.return_value = mock_response
        
        test_data = {
            "goal": "medical assistant robot",
            "style_guide": "clean",
            "complexity": "high",
            "color_scheme": "white and blue"
        }
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            response = self.client.post("/generate_3d_robot_prompt", json=test_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "Enhanced robot prompt" in data["enhanced_prompt"]

class TestStableDiffusionMCP:
    """Stable Diffusion 서버 단위 테스트"""
    
    def setup_method(self):
        self.client = TestClient(diffusion_app)
    
    def test_health_endpoint(self):
        """헬스 체크 엔드포인트 테스트"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "gpu_available" in data
    
    def test_supported_resolutions(self):
        """지원 해상도 엔드포인트 테스트"""
        response = self.client.get("/supported_resolutions")
        assert response.status_code == 200
        
        data = response.json()
        assert "resolutions" in data
        assert "1024x1024" in data["resolutions"]
        assert data["recommended"] == "1024x1024"
    
    def test_create_image_dummy_mode(self):
        """더미 모드에서 이미지 생성 테스트"""
        test_data = {
            "prompt": "test robot",
            "resolution": "512x512",
            "num_inference_steps": 1
        }
        
        response = self.client.post("/create_robot_image", json=test_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "image_path" in data
        assert "metadata" in data
        assert "generation_time" in data
        assert data["metadata"]["resolution"] == "512x512"

class TestBlenderMCP:
    """Blender 서버 단위 테스트"""
    
    def setup_method(self):
        self.client = TestClient(blender_app)
    
    def test_health_endpoint(self):
        """헬스 체크 엔드포인트 테스트"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "blender_available" in data
    
    def test_camera_presets(self):
        """카메라 프리셋 엔드포인트 테스트"""
        response = self.client.get("/camera_presets")
        assert response.status_code == 200
        
        presets = response.json()
        assert len(presets) > 0
        
        # 필수 프리셋 확인
        preset_names = [p["name"] for p in presets]
        assert "front" in preset_names
        assert "side" in preset_names
        assert "perspective" in preset_names
        
        # 프리셋 구조 확인
        for preset in presets:
            assert "name" in preset
            assert "location" in preset
            assert "rotation" in preset
            assert "description" in preset

# 추가 유틸리티 테스트
class TestUtilityFunctions:
    """유틸리티 함수 테스트"""
    
    def test_blender_executable_detection(self):
        """Blender 실행 파일 감지 테스트"""
        from blender_mcp import get_blender_executable
        
        # 함수가 None이 아닌 값을 반환하거나 None을 반환해야 함
        result = get_blender_executable()
        assert result is None or isinstance(result, str)
    
    def test_blender_script_generation(self):
        """Blender 스크립트 생성 테스트"""
        from blender_mcp import generate_blender_script
        
        script = generate_blender_script(
            image_path="test.png",
            camera_preset="front",
            lighting_preset="studio", 
            background_type="transparent",
            output_path="output.png"
        )
        
        assert "import bpy" in script
        assert "test.png" in script
        assert "front" in script
        assert "studio" in script

if __name__ == "__main__":
    pytest.main([__file__, "-v"])