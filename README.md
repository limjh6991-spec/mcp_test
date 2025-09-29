# MCP 로봇 디자인 자동화 시스템

Windows 환경에서 실행되는 Model Context Protocol (MCP) 기반 로봇 디자인 자동화 시스템입니다. AI 프롬프트 생성부터 3D 모델링까지의 전체 워크플로우를 자동화합니다.

## 시스템 개요

```
사용자 요청 → Copilot Agent → [MCP 서버들] → 최종 결과물
                    ↓
    ┌─────────────────┼─────────────────┐
    │                 │                 │
PromptGen MCP    StableDiff MCP    Blender MCP
    │                 │                 │
프롬프트 생성     →   이미지 생성     →   3D 씬 구성
```

## 주요 구성 요소

### A. 핵심 클라이언트: GitHub Copilot (VS Code)
- 모든 MCP 서버를 오케스트레이션하는 중앙 Agent
- 사용자 요청을 분석하고 적절한 서버 조합을 호출

### B. MCP 서버들
1. **PromptGeneratorMcp** (포트 8000) - 프롬프트 생성
2. **StableDiffusionMcp** (포트 8001) - AI 이미지 생성  
3. **BlenderMcp** (포트 8002) - 3D 씬 자동화
4. **EnvManagerMcp** (포트 8003) - 개발 환경 관리
5. **GitHubMcp** (포트 8004) - 형상 관리

## 설치 및 설정

### 1. 환경 요구사항 확인
```powershell
# 현재 환경 진단
powershell -ExecutionPolicy Bypass -File dev_env_check.ps1
```

### 2. Python 환경 설정
```powershell
# Conda 환경 생성 (이미 설치된 경우)
conda create -n mcp_env python=3.11 -y
conda activate mcp_env

# 필수 패키지 설치  
pip install -r requirements.txt
```

### 3. VS Code 설정
`.vscode/settings.json`에 MCP 서버가 자동 등록되어 있습니다.

## 사용법

### 서버 실행

**Python 스크립트 사용:**
```bash
# 모든 서버 시작
python run_servers.py start

# 특정 서버만 시작
python run_servers.py start --server prompt_generator

# 포그라운드에서 실행 (디버깅용)
python run_servers.py start --foreground

# 서버 상태 확인
python run_servers.py status

# 서버 중지
python run_servers.py stop
```

**PowerShell 스크립트 사용:**
```powershell
# 모든 서버 시작
.\run_servers.ps1 -Action start

# 특정 서버만 시작
.\run_servers.ps1 -Action start -Server stable_diffusion

# 서버 상태 확인 (권장)
C:/Users/loved/miniconda3/Scripts/conda.exe run -n mcp_env python simple_test.py

# 서버 재시작
.\run_servers_fixed.ps1 -Action restart

# 서버 중지
.\run_servers_fixed.ps1 -Action stop
```

### 🚀 실제 사용 순서

```powershell
# 1. 서버 시작
.\run_servers_fixed.ps1 -Action start

# 2. 상태 확인 (옵션)
C:/Users/loved/miniconda3/Scripts/conda.exe run -n mcp_env python simple_test.py

# 3. VS Code에서 GitHub Copilot Chat 사용
```

### 전체 워크플로우 예시

VS Code에서 GitHub Copilot Chat에게 다음과 같이 요청:

```
"새로운 산업용 로봇 팔 디자인을 만들고, 이를 Blender에 불러와서 작업 환경을 준비해 줘."

"청소 로봇 디자인을 생성하고 3D 모델링까지 해줘"

"의료용 로봇의 프롬프트를 만들어서 이미지 생성해줘"
```

Copilot Agent가 자동으로:
1. PromptGeneratorMcp로 상세 프롬프트 생성
2. StableDiffusionMcp로 로봇 이미지 생성  
3. BlenderMcp로 3D 씬 구성 및 렌더링

## API 엔드포인트

### PromptGeneratorMcp (포트 8000)
- `POST /generate_3d_robot_prompt` - 3D 로봇 프롬프트 생성
- `GET /health` - 서버 상태 확인

### StableDiffusionMcp (포트 8001)  
- `POST /create_robot_image` - 로봇 이미지 생성
- `GET /supported_resolutions` - 지원 해상도 목록
- `GET /health` - 서버 상태 확인

### BlenderMcp (포트 8002)
- `POST /import_image_and_prepare_scene` - 이미지 → 3D 씬 변환
- `GET /camera_presets` - 카메라 프리셋 목록
- `GET /health` - 서버 상태 확인

## 테스트 실행

```bash
# 단위 테스트
C:/Users/loved/miniconda3/Scripts/conda.exe run -n mcp_env python -m pytest tests/test_unit.py -v

# 통합 테스트 (서버가 실행 중일 때)
C:/Users/loved/miniconda3/Scripts/conda.exe run -n mcp_env python -m pytest tests/test_mcp_integration.py -v

# 간단한 상태 확인 테스트 (권장)
C:/Users/loved/miniconda3/Scripts/conda.exe run -n mcp_env python simple_test.py
```

## 개발 환경

### 프로젝트 구조
```
mcp_test/
├── src/                          # MCP 서버 소스코드
│   ├── prompt_generator_mcp/
│   ├── stable_diffusion_mcp/
│   ├── blender_mcp/
│   ├── env_manager_mcp/
│   └── github_mcp/
├── tests/                        # 테스트 코드
├── .vscode/                      # VS Code 설정
├── requirements.txt              # Python 의존성
├── mcp.json                      # MCP 서버 설정
├── run_servers.py               # 서버 실행 스크립트 (Python)
├── run_servers.ps1              # 서버 실행 스크립트 (PowerShell)
└── dev_env_check.ps1            # 환경 진단 도구
```

### 새 MCP 서버 추가하기

1. `src/` 디렉토리에 새 모듈 생성
2. FastAPI 앱 구현
3. `run_servers.py`와 `run_servers.ps1`에 서버 설정 추가
4. `mcp.json`에 설정 추가
5. `.vscode/settings.json`에 에이전트 등록

## 문제 해결

### 일반적인 문제들

**CUDA/GPU 관련 오류:**
- GPU가 없어도 CPU 모드로 동작합니다
- CUDA 설치 시 PyTorch 재설치 필요할 수 있습니다

**Blender 관련 오류:**
- Blender가 설치되지 않은 경우 해당 기능만 비활성화됩니다
- Blender Python API 스크립트는 자동 생성됩니다

**포트 충돌:**
- `mcp.json`에서 포트 번호를 변경할 수 있습니다
- 실행 전 `netstat -an`으로 포트 사용 현황 확인

### 로그 확인

```bash
# 개별 서버 로그 확인 (포그라운드 실행)
python run_servers.py start --server prompt_generator --foreground
```

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여하기

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 추가 정보

- [MCP 공식 문서](https://modelcontextprotocol.io/)
- [GitHub Copilot Agent 가이드](https://aka.ms/vscode-instructions-docs)
- [FastAPI 문서](https://fastapi.tiangolo.com/)

---

환경 문제나 버그 발견 시 GitHub Issues에 보고해 주세요.