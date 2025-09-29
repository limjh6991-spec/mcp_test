import pytest
import requests
import json
from typing import Dict, Any

# 테스트용 기본 설정
BASE_URLS = {
    "prompt_generator": "http://localhost:8000",
    "stable_diffusion": "http://localhost:8001", 
    "blender": "http://localhost:8002",
    "env_manager": "http://localhost:8003",
    "github": "http://localhost:8004"
}

class TestMCPServers:
    """MCP 서버들의 통합 테스트"""
    
    def test_server_health_checks(self):
        """모든 서버의 health check 테스트"""
        for service, url in BASE_URLS.items():
            try:
                response = requests.get(f"{url}/health", timeout=5)
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "healthy"
                assert data["service"] == f"{service}_mcp"
                print(f"✓ {service} 서버 정상")
            except requests.exceptions.ConnectionError:
                pytest.skip(f"{service} 서버가 실행되지 않음")
    
    def test_prompt_generator_workflow(self):
        """프롬프트 생성기 워크플로우 테스트"""
        url = BASE_URLS["prompt_generator"]
        
        # 테스트 요청 데이터
        test_data = {
            "goal": "humanoid robot with advanced AI capabilities",
            "style_guide": "cyberpunk",
            "complexity": "high",
            "color_scheme": "blue and silver"
        }
        
        try:
            response = requests.post(f"{url}/generate_3d_robot_prompt", json=test_data)
            assert response.status_code == 200
            
            data = response.json()
            assert "prompt" in data
            assert "enhanced_prompt" in data
            assert "metadata" in data
            assert data["metadata"]["original_goal"] == test_data["goal"]
            print("✓ 프롬프트 생성 테스트 통과")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("프롬프트 생성기 서버가 실행되지 않음")
    
    def test_stable_diffusion_workflow(self):
        """이미지 생성 워크플로우 테스트"""
        url = BASE_URLS["stable_diffusion"]
        
        # 지원되는 해상도 확인
        try:
            response = requests.get(f"{url}/supported_resolutions")
            assert response.status_code == 200
            resolutions = response.json()["resolutions"]
            assert "1024x1024" in resolutions
            
            # 이미지 생성 테스트 (더미 모드에서도 작동)
            test_data = {
                "prompt": "futuristic humanoid robot, metallic surface, glowing blue eyes",
                "resolution": "512x512",
                "num_inference_steps": 10  # 빠른 테스트를 위해 낮은 값
            }
            
            response = requests.post(f"{url}/create_robot_image", json=test_data)
            assert response.status_code == 200
            
            data = response.json()
            assert "image_path" in data
            assert "metadata" in data
            assert "generation_time" in data
            print("✓ 이미지 생성 테스트 통과")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Stable Diffusion 서버가 실행되지 않음")
    
    def test_end_to_end_workflow(self):
        """전체 워크플로우 통합 테스트"""
        try:
            # 1. 프롬프트 생성
            prompt_data = {
                "goal": "industrial assembly robot",
                "style_guide": "realistic"
            }
            
            prompt_response = requests.post(
                f"{BASE_URLS['prompt_generator']}/generate_3d_robot_prompt", 
                json=prompt_data
            )
            assert prompt_response.status_code == 200
            prompt_result = prompt_response.json()
            
            # 2. 이미지 생성
            image_data = {
                "prompt": prompt_result["enhanced_prompt"],
                "resolution": "512x512",
                "num_inference_steps": 5
            }
            
            image_response = requests.post(
                f"{BASE_URLS['stable_diffusion']}/create_robot_image",
                json=image_data
            )
            assert image_response.status_code == 200
            image_result = image_response.json()
            
            # 3. Blender 씬 생성 (이미지 파일이 실제로 존재하는 경우에만)
            if "image_path" in image_result:
                scene_data = {
                    "image_path": image_result["image_path"],
                    "camera_preset": "perspective",
                    "lighting_preset": "studio"
                }
                
                # Blender 서버가 실행 중이고 Blender가 설치된 경우에만 테스트
                try:
                    scene_response = requests.post(
                        f"{BASE_URLS['blender']}/import_image_and_prepare_scene",
                        json=scene_data,
                        timeout=30
                    )
                    if scene_response.status_code == 200:
                        print("✓ 전체 워크플로우 테스트 통과")
                    else:
                        print("⚠ Blender 부분 실패 (Blender 미설치 가능성)")
                        
                except requests.exceptions.ConnectionError:
                    print("⚠ Blender 서버 연결 실패")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("필요한 서버가 실행되지 않음")

def test_individual_server_endpoints():
    """각 서버의 개별 엔드포인트 테스트"""
    
    # Blender 카메라 프리셋 테스트
    try:
        response = requests.get(f"{BASE_URLS['blender']}/camera_presets")
        if response.status_code == 200:
            presets = response.json()
            assert len(presets) > 0
            assert all("name" in preset for preset in presets)
            print("✓ Blender 카메라 프리셋 테스트 통과")
    except requests.exceptions.ConnectionError:
        pass

if __name__ == "__main__":
    # 직접 실행 시 간단한 테스트 수행
    print("MCP 서버 테스트 시작...")
    
    test_case = TestMCPServers()
    
    try:
        test_case.test_server_health_checks()
        test_case.test_prompt_generator_workflow()
        test_case.test_stable_diffusion_workflow()
        test_case.test_end_to_end_workflow()
        test_individual_server_endpoints()
        print("\n모든 테스트 완료!")
        
    except Exception as e:
        print(f"\n테스트 중 오류 발생: {e}")