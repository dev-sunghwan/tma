# Tennis Match Analyzer

테니스 경기 영상 분석을 통한 플레이어 스타일 자동 분류 시스템

## 프로젝트 개요
- Computer Vision 기반 테니스 경기 분석
- OpenCV를 활용한 공 추적 및 코트 분석
- 플레이 스타일 자동 분류 (베이스라이너, 서브앤발리 등)

## 개발 환경
- Python 3.11.13
- OpenCV 4.10.0
- macOS

## 설치 방법
```bash
# 가상환경 생성
conda create -n tennis-analyzer python=3.11

# 활성화
conda activate tennis-analyzer

# 패키지 설치
pip install --only-binary :all: opencv-python
pip install numpy pandas matplotlib

# 프로젝트 구조
tennis-match-analyzer/
├── src/           # 소스 코드
├── tests/         # 테스트 코드
├── data/          # 영상 데이터
├── notes/         # 학습 노트
└── docs/          # 문서
