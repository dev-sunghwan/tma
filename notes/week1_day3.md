# Week 1 Day 3 - 영상 다운로드 및 OpenCV 기본 읽기

**날짜**: 2024-10-09  
**소요 시간**: 1시간  
**타입**: 코딩 & 실습

---

## 오늘의 목표
- 테니스 영상 다운로드
- OpenCV로 영상 읽기 및 정보 추출
- 첫 프레임 저장

---

## 완료 사항

### 1. yt-dlp 설치 및 사용
```bash
pip install yt-dlp
yt-dlp -f "best[height<=720]" -o "tennis_sample_1.mp4" "URL"
```

배운 점:

zsh에서 URL 특수문자 처리: 따옴표로 감싸기
화질 제한 옵션으로 적절한 크기 유지

### 2. 영상 다운로드 스크립트 작성

src/download_video.py 생성
yt-dlp Python API 활용
재사용 가능한 함수로 구현

### 3. 영상 읽기 테스트

tests/test_video_read.py 작성
OpenCV VideoCapture 사용
영상 메타데이터 추출

다운로드한 영상 정보:

파일명: tennis_sample_1.mp4
해상도: 1280 x 720 (HD)
FPS: 29.97
총 프레임: 2,689개
재생 시간: 89.72초

### 4. 첫 프레임 저장

cv2.imwrite() 사용
코트 전체가 보이는 풀샷 확인

#### 핵심코드
OpenCV로 영상 정보 추출
```
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
```

#### 프레임 읽기
```
ret, frame = cap.read()
if ret:
    cv2.imwrite(output_path, frame)
cap.release()
```

### 트러블슈팅
문제 1: zsh URL 파싱 에러
증상: no matches found 에러
원인: URL의 ? 문자를 zsh가 와일드카드로 해석
해결: URL을 따옴표로 감싸기
문제 2: 상대 경로 문제
증상: 파일을 찾을 수 없습니다 에러
원인: 실행 위치에 따라 상대 경로 변경
해결: os.path.abspath()로 절대 경로 사용
문제 3: ffmpeg 설치 실패 (macOS 12)
증상: Homebrew 빌드 에러
원인: macOS 버전 오래됨 (Tier 3 지원)
해결: ffmpeg 없이 진행 (현재는 불필요)

배운 개념
OpenCV VideoCapture

영상 파일 읽기의 핵심 클래스
cap.get() 메서드로 메타데이터 접근
프레임 단위로 순차 읽기 가능
반드시 cap.release()로 리소스 해제

영상의 기본 속성

FPS (Frames Per Second): 초당 프레임 수
Frame Count: 총 프레임 개수
Duration: frame_count / fps
해상도: width x height (픽셀)


다음 단계 (Day 4)

 OpenCV 색상 공간 학습 (BGR, HSV)
 기본 이미지 처리 (블러, 엣지 검출)
 간단한 색상 기반 필터링 실습
 테니스 공 색상(노란색) 분리 실험


참고 자료

OpenCV VideoCapture 문서
yt-dlp GitHub


회고
드디어 실제 영상을 다루기 시작했다!
OpenCV로 영상을 읽고 정보를 추출하는 것이 생각보다 간단했다.
프레임이 2,689개나 되는데, 이걸 하나하나 분석할 생각을 하니
앞으로 할 일이 많아 보인다. 하지만 첫 프레임을 저장하는 순간
뭔가 프로젝트가 구체화되는 느낌이 들었다.
내일은 색상 기반으로 테니스 공을 찾는 첫 시도를 해볼 예정!


---

## Part 2: GitHub에 업로드

### Step 1: GitHub에서 새 저장소 생성

1. https://github.com 접속 및 로그인
2. 우측 상단 `+` → `New repository` 클릭
3. 저장소 설정:
   - **Repository name**: `tennis-match-analyzer`
   - **Description**: `Tennis match video analysis using Computer Vision`
   - **Public** 선택 (포트폴리오용)
   - ❌ "Add a README file" 체크 해제 (이미 있음)
   - ❌ "Add .gitignore" 체크 해제 (이미 있음)
4. `Create repository` 클릭

### Step 2: 로컬에서 GitHub 연결
```bash
# 프로젝트 루트에서
cd ~/Documents/tma

# Day 3 노트 추가
git add notes/week1_day3.md
git commit -m "Add Day 3 learning notes"

# GitHub 원격 저장소 연결 (GitHub에서 보여주는 URL 사용)
git remote add origin https://github.com/[YOUR_USERNAME]/tennis-match-analyzer.git

# 원격 저장소 확인
git remote -v

# main 브랜치로 이름 변경 (필요시)
git branch -M main

# GitHub에 푸시
git push -u origin main

### Step 3: 푸시 시 인증
GitHub에서 비밀번호 대신 Personal Access Token 필요:

GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
Generate new token (classic) 클릭
Note: tennis-analyzer-token
Expiration: 90 days 선택
Scopes: repo 체크
Generate token 클릭
토큰 복사 (다시 볼 수 없으니 안전한 곳에 저장!)

푸시 시 Username과 Password 물으면:

Username: GitHub 사용자명
Password: 방금 복사한 토큰 붙여넣기

전체 실행 순서
```
# 1. 노트 파일 생성
nano notes/week1_day3.md
# (위 내용 붙여넣기)

# 2. Git 커밋
git add notes/week1_day3.md
git commit -m "Add Day 3 learning notes"

# 3. GitHub 저장소 생성 (웹에서)

# 4. 원격 연결 및 푸시
git remote add origin https://github.com/[YOUR_USERNAME]/tennis-match-analyzer.git
git branch -M main
git push -u origin main
```
