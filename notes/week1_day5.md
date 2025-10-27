# Week 1 Day 5 - Week 1 총정리

**날짜**: 2024-10-12  
**소요 시간**: 1시간  
**타입**: 정리 & 계획

---

## Week 1 전체 회고

### 목표 달성도
- ✅ OpenCV 환경 설정 및 기초 학습
- ✅ Git/GitHub 실전 적용
- ✅ 영상 처리 파이프라인 구축
- ✅ 색상 공간 이해
- ⚠️ 공 검출 (예상보다 어려움)

---

## 일별 요약

### Day 1 (월) - 환경 설정
- Anaconda 가상환경
- OpenCV 4.10.0 설치
- 첫 테스트 성공

**배운 것**: Mac에서 protobuf 충돌 해결

### Day 2 (화) - Git 저장소
- Git 초기화 및 구조 설계
- .gitignore 설정
- 첫 커밋

**배운 것**: 프로젝트 초기 구조의 중요성

### Day 3 (수) - 영상 다운로드
- yt-dlp로 테니스 영상 다운로드
- OpenCV로 영상 정보 추출
- 첫 프레임 저장

**배운 것**: 
- zsh URL 처리
- 영상 메타데이터 (FPS, 해상도)

### Day 4 (목) - 색상 공간
- BGR vs HSV 개념 학습
- 색상 기반 검출 실험
- 여러 HSV 범위 테스트

**배운 것**:
- HSV가 색상 검출에 유리
- 실전 데이터의 어려움
- 색상만으로는 한계

### Day 5 (금) - 정리
- 전체 회고
- 문서 업데이트
- Week 2 계획

---

## 핵심 학습 내용

### 1. OpenCV 기초
- VideoCapture로 영상 읽기
- 프레임 단위 처리
- 이미지 저장

### 2. 색상 공간
- **BGR**: 모니터 색상 (Blue-Green-Red)
- **HSV**: 색조-채도-명도
  - H (0-179): 색상
  - S (0-255): 순도
  - V (0-255): 밝기

### 3. 마스크 기반 검출
```python
mask = cv2.inRange(hsv, lower, upper)
result = cv2.bitwise_and(img, img, mask=mask)
```

---

## 직면한 도전과제

### 1. 색상 검출의 한계
**문제**:
- 테니스 공이 과다 노출 (거의 흰색)
- 공이 너무 작음 (5-10 픽셀)
- 영상 압축으로 색상 손실

**시도한 것**:
- 다양한 HSV 범위 실험
- 채도 낮춤 (50 → 30 → 10)
- 명도 최소값 상향 (100 → 200)

**결과**: 공 직접 검출 실패

### 2. 배운 교훈
- ✅ 실패도 중요한 학습
- ✅ 이론과 실전의 차이 체감
- ✅ 다음 접근법의 필요성 명확

---

## 프로젝트 통계

### 코드
- Python 파일: 6개
- 총 라인 수: ~400 줄
- 테스트: 4개

### 문서
- 학습 노트: 5개
- README: 1개
- Git 커밋: 10+개

### 데이터
- 다운로드 영상: 1개 (90초, 720p)
- 추출된 프레임: 10개
- 테스트 이미지: 다수

---

## Week 2 계획

### 새로운 접근: 모션 기반 검출

**핵심 아이디어**: 
"움직이는 작은 물체 = 공"

### 기술 스택
1. **Background Subtraction**
   - 배경 제거로 움직이는 객체만 추출
   - OpenCV의 MOG2, KNN 알고리즘

2. **Motion Detection**
   - 프레임 간 차이 계산
   - 움직임 영역 검출

3. **Object Tracking**
   - CSRT, KCF Tracker
   - 한번 찾으면 계속 추적

### 주간 계획
- **Day 6-7**: Background Subtraction 학습 및 실습
- **Day 8-9**: 움직임 기반 공 후보 검출
- **Day 10**: Week 2 정리

---

## 개인적 성찰

### 잘한 점
- 매일 꾸준히 1시간 투자
- 실패를 두려워하지 않고 실험
- 모든 과정 문서화
- Git 버전 관리 습관

### 개선할 점
- 영상 선택을 더 신중히 (화질, 조명)
- 더 작은 단위로 실험 (한 번에 하나씩)
- 중간 결과 자주 저장

### 다음 주 목표
- 모션 기반 검출로 첫 성공 경험
- 공 위치를 프레임별로 추출
- CSV로 데이터 저장

---

## 참고 자료
- [OpenCV Background Subtraction](https://docs.opencv.org/4.x/d1/dc5/tutorial_background_subtraction.html)
- [Object Tracking](https://docs.opencv.org/4.x/d9/df8/group__tracking.html)

---

## 다음 단계
Week 2 Day 6에서 Background Subtraction 시작!
"색상이 안 되면 움직임으로!"