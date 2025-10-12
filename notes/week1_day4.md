# Week 1 Day 4 - 색상 공간 학습 및 검출 실험

**날짜**: 2024-10-09  
**소요 시간**: 1.5시간  
**타입**: 학습 & 실험

---

## 핵심 개념 학습

### BGR vs HSV
- **BGR**: 모니터 표현 방식 (Blue-Green-Red)
- **HSV**: 사람의 색 인식 방식 (Hue-Saturation-Value)
- 색상 검출에는 HSV가 유리

### HSV 채널별 의미
- **H (색조)**: 0-179, 색상 자체 (노랑=20-30)
- **S (채도)**: 0-255, 색의 순도
- **V (명도)**: 0-255, 밝기

---

## 실험 내용

### 테스트한 HSV 범위들
```python
[20, 100, 100] - [30, 255, 255]  # standard
[15, 80, 80] - [35, 255, 255]    # wide
[25, 150, 150] - [35, 255, 255]  # bright
[20, 50, 200] - [30, 255, 255]   # bright_white
[15, 30, 220] - [35, 255, 255]   # very_bright

## 결과

대부분 프레임: 400-900 픽셀 검출
Frame 08: 70,000+ 픽셀 (US Open 로고)
결론: 테니스 공 직접 검출 실패


## 발견한 문제점

공이 너무 작음: 1280x720 화면에서 5-10픽셀
과다 노출: 노란색 공이 거의 흰색으로 보임
화질 손실: YouTube 압축으로 색상 정보 손실


## 배운 교훈
### 긍정적

✅ 색상 공간의 개념과 활용 이해
✅ OpenCV 색상 변환 및 마스크 생성 숙달
✅ 실전 데이터의 어려움 경험

### 한계 인식

❌ 색상만으로는 불충분
❌ 완벽한 데이터는 없음
→ 다음 접근법 필요

## 다음 단계 (Week 2)
색상 기반에서 모션 기반으로 전환

배경 제거 (Background Subtraction)
움직임 검출 (Motion Detection)
객체 추적 (Object Tracking - CSRT, KCF)

"움직이는 작은 물체 = 공"

## 참고 자료

OpenCV Color Spaces
HSV Color Picker


## 회고
색상 검출이 생각보다 어려웠다. 이론상으로는 HSV로 쉽게 찾을 수 있다고 했지만,
실제 영상은 조명, 화질, 크기 등 변수가 너무 많았다.
하지만 이 과정에서 왜 더 고급 기법이 필요한지 명확히 알게 됐다.
실패도 학습이라는 걸 체감. Week 2에서는 모션 기반 접근을 시도할 예정!


## Git 커밋
```bash
# 노트 추가
git add notes/week1_day4.md

# 새로 생성된 테스트 스크립트들도 추가
git add tests/test_color_detection.py tests/test_multiple_frames.py tests/analyze_frame_08.py

# 커밋
git commit -m "Day 4: Color space learning and detection experiments"

# GitHub에 푸시
git push origin main