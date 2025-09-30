
import bpy

# 기본 씬 정리
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 카메라 추가
bpy.ops.object.camera_add(location=(7, -7, 5))
camera = bpy.context.object

# 조명 설정
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))

# 로봇 아암 베이스
bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=0.5, location=(0, 0, 0.25))
base = bpy.context.object
base.name = "RobotBase"

# 아암 링크
bpy.ops.mesh.primitive_cube_add(scale=(0.2, 2, 0.2), location=(0, 1.5, 0.9))
link1 = bpy.context.object
link1.name = "Link1"

# 엔드 이펙터
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(0, 3, 0.9))
end_effector = bpy.context.object
end_effector.name = "EndEffector"

# 머티리얼 설정
metal_mat = bpy.data.materials.new(name="RobotMetal")
metal_mat.use_nodes = True
bsdf = metal_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = (0.8, 0.8, 0.9, 1.0)
bsdf.inputs[4].default_value = 1.0  # Metallic
bsdf.inputs[7].default_value = 0.1  # Roughness

# 머티리얼 적용
for obj in [base, link1, end_effector]:
    obj.data.materials.append(metal_mat)

# 씬 저장
bpy.ops.wm.save_as_mainfile(filepath="robot_scene.blend")

print("✅ Blender 로봇 씬 생성 완료!")
