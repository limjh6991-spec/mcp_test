# 🤖 MCP Robot Design System

**AI-Powered Robot Design Automation with Model Context Protocol**

이 프로젝트는 Model Context Protocol(MCP)을 사용하여 프롬프트 생성부터 3D 모델링까지 완전 자동화된 로봇 디자인 워크플로우를 제공합니다.

## ✨ 주요 특징

- **🚀 빠른 프로토타이핑**: 0.1초 만에 로봇 목업 이미지 생성
- **🎨 3D 자동화**: Blender를 통한 자동 3D 씬 구성  
- **☁️ 클라우드 AI 통합**: HuggingFace/Stability AI API 지원
- **🔧 Windows 최적화**: PowerShell 스크립트로 완전 자동화

## 🏗️ 시스템 아키텍처

```
사용자 요청 → GitHub Copilot → MCP 서버들 → 최종 결과물
                    ↓
    ┌─────────────────┼─────────────────┐
    │   Prompt Gen    │  Stable Diff    │  Blender
    │     MCP         │      MCP        │    MCP
    │   (Port 8000)   │   (Port 8001)   │ (Port 8002)
    └─────────────────┼─────────────────┘
                    ↓
          완전 자동화된 로봇 디자인
```

## 🚀 빠른 시작

### 1. 환경 설정
```powershell
# Miniconda 환경 생성
conda create -n mcp_env python=3.11
conda activate mcp_env

# 의존성 설치
pip install -r requirements.txt
```

### 2. 서버 시작
```powershell
# MCP 서버들 시작
.\run_servers_fixed.ps1 -Action start
```

### 3. 워크플로우 실행
```powershell
# Step 1: 프롬프트 생성
python step1_generate_prompt.py

# Step 2: 빠른 목업 이미지 생성
python tools\mockup_generator.py

# Step 3: Blender 3D 씬 준비
python tools\simple_blender_test.py
```

## 📁 프로젝트 구조

```
mcp_test/
├── src/                          # MCP 서버들
│   ├── prompt_generator_mcp/     # 프롬프트 생성 서버
│   ├── stable_diffusion_mcp/     # AI 이미지 생성 서버
│   ├── blender_mcp/             # Blender 자동화 서버
│   ├── env_manager_mcp/         # 환경 관리 서버
│   └── github_mcp/              # GitHub 연동 서버
├── tools/                       # 개선된 도구들
│   ├── mockup_generator.py      # 빠른 목업 생성기 (0.1초)
│   ├── simple_blender_test.py   # Blender 자동화
│   └── blender_robot_script.py  # Blender 실행 스크립트
├── tests/                       # 테스트 코드
├── step1_generate_prompt.py     # 워크플로우 1단계
├── step2_generate_image.py      # 워크플로우 2단계
└── run_servers_fixed.ps1       # 서버 관리 스크립트
```

## 🔧 MCP 서버들

| 서버 | 포트 | 기능 | 상태 |
|-----|------|------|------|
| **Prompt Generator** | 8000 | 사용자 요청 → 상세 AI 프롬프트 변환 | ✅ 완료 |
| **Stable Diffusion** | 8001 | AI 이미지 생성 (클라우드/로컬 하이브리드) | ✅ 완료 |
| **Blender Automation** | 8002 | 3D 씬 자동 구성 및 렌더링 | ✅ 완료 |
| **Environment Manager** | 8003 | Python/Conda 환경 관리 | 🟡 부분 완료 |
| **GitHub Integration** | 8004 | Git 연동 및 버전 관리 | 🟡 부분 완료 |

## ⚡ 성능 개선

### 이미지 생성 속도 최적화
- **기존**: 로컬 SD 2.1 모델 (20-30초, 5GB 메모리)
- **개선**: 다중 백엔드 시스템
  1. **빠른 목업** (0.1초) - 즉시 프로토타입
  2. **HuggingFace API** (5-10초) - 무료 고품질
  3. **Stability AI** (3-5초) - 프리미엄 품질
  4. **로컬 모델** (20-30초) - 백업용

## 🎯 사용 예시

### 산업용 로봇 팔 디자인
```python
# 1. 프롬프트 생성
prompt = "industrial robotic arm for precision manufacturing"

# 2. 목업 생성 (0.1초)
python tools/mockup_generator.py

# 3. Blender 3D 씬
python tools/simple_blender_test.py
```

**결과**: 
- 📸 `generated_images/robot_mockup_*.png` - 목업 이미지
- 🎨 `blender_robot_script.py` - 3D 씬 스크립트

## 🛠️ API 통합

### HuggingFace Integration
```python
# 무료 AI 이미지 생성
api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
```

### Stability AI Integration
```python
# 프리미엄 품질 (API 키 필요)
api_url = "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image"
```

## 📚 기술 스택

### Backend
- **FastAPI** - 비동기 REST API 서버
- **Uvicorn** - ASGI 서버 런타임
- **Pydantic** - 데이터 검증 및 직렬화

### AI/ML
- **Stable Diffusion 2.1** - 이미지 생성
- **PyTorch** - 딥러닝 프레임워크
- **Transformers & Diffusers** - Hugging Face 라이브러리

### 3D Graphics
- **Blender Python API** - 3D 씬 자동화
- **PIL/Pillow** - 이미지 처리

### DevOps
- **Windows PowerShell** - 자동화 스크립트
- **Miniconda** - Python 환경 관리
- **Git** - 버전 관리

## 🔍 트러블슈팅

### 일반적인 문제들

1. **서버 시작 실패**
   ```powershell
   # 포트 확인 및 정리
   Get-NetTCPConnection -LocalPort 8000-8004
   ```

2. **메모리 부족**
   ```powershell
   # Python 프로세스 정리
   Get-Process python | Stop-Process -Force
   ```

3. **환경 문제**
   ```powershell
   # Conda 환경 재생성
   conda env remove -n mcp_env
   conda create -n mcp_env python=3.11
   ```

## � Daily Logs

프로젝트의 일일 진행 상황과 주요 업데이트를 기록합니다.

### 최근 업데이트
- **2025-09-30**: [MCP 로봇 시스템 완료](./daily_log/2025-09-30_mcp_robot_system_completion.md) - 성능 최적화 및 GitHub 업로드 완료

### 로그 폴더
📁 [`daily_log/`](./daily_log/) - 모든 일일 작업 로그 보기

## �📈 향후 계획

### 단기 목표
- [ ] HuggingFace API 키 설정으로 실제 AI 이미지 생성
- [ ] Blender 자동 실행 통합
- [ ] 웹 UI 인터페이스 추가

### 장기 목표
- [ ] ComfyUI 워크플로우 통합
- [ ] 실시간 3D 프리뷰
- [ ] 다중 로봇 타입 지원 (산업용, 서비스, 휴머노이드)

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능합니다.

## 🤝 기여하기

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

**Made with ❤️ by MCP Robot Design Team**

🚀 **빠른 프로토타이핑부터 완성된 3D 모델까지, 모든 것을 자동화합니다!**