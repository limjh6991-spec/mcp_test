# GitHub 업로드 가이드

## 1. GitHub에서 새 저장소 생성
1. https://github.com 에 로그인
2. 우측 상단의 '+' → 'New repository' 클릭
3. Repository name: `mcp_test`
4. Description: `MCP Robot Design System - AI-powered robot design automation`
5. Public 선택
6. **Initialize this repository with a README 체크 해제**
7. 'Create repository' 클릭

## 2. 로컬에서 GitHub에 연결
GitHub에서 저장소 생성 후 나오는 명령어 중 "push an existing repository" 부분을 사용:

```bash
git remote add origin https://github.com/[YOUR_USERNAME]/mcp_test.git
git branch -M main
git push -u origin main
```

또는 SSH를 사용하는 경우:
```bash
git remote add origin git@github.com:[YOUR_USERNAME]/mcp_test.git
git branch -M main  
git push -u origin main
```

## 3. 현재 준비된 상태
- ✅ Git 저장소 초기화 완료
- ✅ 첫 커밋 생성 완료 (19개 파일)
- ✅ .gitignore 설정 완료
- ⏳ GitHub 원격 저장소 연결 대기

## 4. 포함된 파일들
```
.github/copilot-instructions.md  # AI 에이전트 가이드
src/                            # MCP 서버 소스코드
├── prompt_generator_mcp/       # 프롬프트 생성
├── stable_diffusion_mcp/       # AI 이미지 생성  
├── blender_mcp/               # Blender 자동화
├── env_manager_mcp/           # 환경 관리
└── github_mcp/                # GitHub 연동

tests/                         # 테스트 코드
step1_generate_prompt.py       # 워크플로우 스크립트
step2_generate_image.py
run_servers_fixed.ps1          # 서버 관리
SESSION_SUMMARY.md             # 작업 요약
README.md                      # 프로젝트 문서
requirements.txt               # Python 의존성
```

위 명령어들을 복사해서 GitHub에서 저장소 생성 후 실행해주세요!