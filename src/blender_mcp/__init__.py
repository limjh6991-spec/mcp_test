from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
import tempfile
from datetime import datetime
from typing import Optional, List

app = FastAPI(title="Blender MCP", version="1.0.0")

class SceneRequest(BaseModel):
    image_path: str
    camera_preset: str = 'front'
    lighting_preset: str = 'studio'
    background_type: str = 'transparent'

class SceneResponse(BaseModel):
    scene_path: str
    render_path: Optional[str] = None
    metadata: dict

class CameraPreset(BaseModel):
    name: str
    location: tuple
    rotation: tuple
    description: str

def get_blender_executable():
    """Blender 실행 파일 경로 찾기"""
    common_paths = [
        r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
        "blender"  # PATH에 있는 경우
    ]
    
    for path in common_paths:
        if os.path.exists(path) or path == "blender":
            return path
    return None

def generate_blender_script(image_path: str, camera_preset: str, lighting_preset: str, background_type: str, output_path: str):
    """Blender Python 스크립트 생성"""
    script = f'''
import bpy
import bmesh
import os
from mathutils import Vector

# 기본 씬 정리
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 이미지 텍스처로 평면 생성
bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, 0))
plane = bpy.context.active_object
plane.name = "RobotImagePlane"

# 머티리얼 생성 및 이미지 텍스처 적용
material = bpy.data.materials.new(name="RobotMaterial")
material.use_nodes = True
plane.data.materials.append(material)

# 노드 설정
nodes = material.node_tree.nodes
links = material.node_tree.links

# 기존 노드 제거
for node in nodes:
    nodes.remove(node)

# 새 노드 추가
tex_image = nodes.new(type='ShaderNodeTexImage')
principled = nodes.new(type='ShaderNodeBsdf')
output = nodes.new(type='ShaderNodeOutputMaterial')

# 이미지 로드
if os.path.exists(r"{image_path}"):
    tex_image.image = bpy.data.images.load(r"{image_path}")

# 노드 연결
links.new(tex_image.outputs[0], principled.inputs[0])
links.new(principled.outputs[0], output.inputs[0])

# 카메라 설정
camera_presets = {{
    'front': {{
        'location': (0, -5, 1),
        'rotation': (1.2, 0, 0)
    }},
    'side': {{
        'location': (-5, 0, 1),
        'rotation': (1.2, 0, -1.57)
    }},
    'top': {{
        'location': (0, 0, 5),
        'rotation': (0, 0, 0)
    }},
    'perspective': {{
        'location': (-3, -3, 2),
        'rotation': (1.1, 0, -0.785)
    }}
}}

bpy.ops.object.camera_add()
camera = bpy.context.active_object
preset = camera_presets.get("{camera_preset}", camera_presets['front'])
camera.location = preset['location']
camera.rotation_euler = preset['rotation']

# 조명 설정
lighting_presets = {{
    'studio': [
        {{'type': 'SUN', 'location': (5, 5, 10), 'energy': 3}},
        {{'type': 'AREA', 'location': (-5, -5, 5), 'energy': 2}}
    ],
    'soft': [
        {{'type': 'AREA', 'location': (2, -2, 4), 'energy': 5}},
        {{'type': 'AREA', 'location': (-2, 2, 4), 'energy': 3}}
    ]
}}

lights = lighting_presets.get("{lighting_preset}", lighting_presets['studio'])
for light_config in lights:
    bpy.ops.object.light_add(type=light_config['type'], location=light_config['location'])
    bpy.context.active_object.data.energy = light_config['energy']

# 배경 설정
if "{background_type}" == "transparent":
    bpy.context.scene.render.film_transparent = True
elif "{background_type}" == "white":
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (1, 1, 1, 1)

# 렌더링 설정
bpy.context.scene.camera = camera
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.render.filepath = r"{output_path}"
bpy.context.scene.render.image_settings.file_format = 'PNG'

# 파일 저장
scene_path = r"{output_path}".replace('.png', '.blend')
bpy.ops.wm.save_as_mainfile(filepath=scene_path)

print(f"씬 저장 완료: {{scene_path}}")
'''
    return script

@app.post('/import_image_and_prepare_scene', response_model=SceneResponse)
async def import_image_and_prepare_scene(request: SceneRequest):
    """
    생성된 이미지를 Blender로 가져와서 3D 씬 준비
    """
    try:
        # Blender 실행 파일 확인
        blender_exe = get_blender_executable()
        if not blender_exe:
            raise HTTPException(status_code=400, detail="Blender 실행 파일을 찾을 수 없습니다.")
        
        # 입력 이미지 파일 존재 확인
        if not os.path.exists(request.image_path):
            raise HTTPException(status_code=400, detail="이미지 파일을 찾을 수 없습니다.")
        
        # 출력 디렉토리 생성
        output_dir = "blender_scenes"
        os.makedirs(output_dir, exist_ok=True)
        
        # 출력 파일 경로 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        scene_name = f"robot_scene_{timestamp}"
        scene_path = os.path.join(output_dir, f"{scene_name}.blend")
        render_path = os.path.join(output_dir, f"{scene_name}_render.png")
        
        # Blender 스크립트 생성
        script_content = generate_blender_script(
            request.image_path, 
            request.camera_preset, 
            request.lighting_preset,
            request.background_type,
            render_path
        )
        
        # 임시 스크립트 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as script_file:
            script_file.write(script_content)
            script_path = script_file.name
        
        try:
            # Blender 실행
            cmd = [blender_exe, "--background", "--python", script_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Blender 실행 실패: {result.stderr}"
                )
            
        finally:
            # 임시 스크립트 파일 삭제
            if os.path.exists(script_path):
                os.unlink(script_path)
        
        # 메타데이터
        metadata = {
            "source_image": request.image_path,
            "camera_preset": request.camera_preset,
            "lighting_preset": request.lighting_preset,
            "background_type": request.background_type,
            "blender_version": "Unknown",
            "timestamp": datetime.now().isoformat(),
            "render_engine": "CYCLES"
        }
        
        return SceneResponse(
            scene_path=os.path.abspath(scene_path),
            render_path=os.path.abspath(render_path) if os.path.exists(render_path) else None,
            metadata=metadata
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blender 씬 생성 실패: {str(e)}")

@app.get('/camera_presets', response_model=List[CameraPreset])
async def get_camera_presets():
    """사용 가능한 카메라 프리셋 목록"""
    return [
        CameraPreset(name="front", location=(0, -5, 1), rotation=(1.2, 0, 0), description="정면에서 촬영"),
        CameraPreset(name="side", location=(-5, 0, 1), rotation=(1.2, 0, -1.57), description="측면에서 촬영"),
        CameraPreset(name="top", location=(0, 0, 5), rotation=(0, 0, 0), description="위에서 촬영"),
        CameraPreset(name="perspective", location=(-3, -3, 2), rotation=(1.1, 0, -0.785), description="원근감 있는 각도")
    ]

@app.get('/health')
async def health_check():
    """서버 상태 확인"""
    blender_available = get_blender_executable() is not None
    return {
        "status": "healthy",
        "service": "blender_mcp",
        "blender_available": blender_available,
        "blender_path": get_blender_executable()
    }
