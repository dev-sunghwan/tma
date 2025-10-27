# Week 2 Day 6 - Background Subtraction 마스터와 한계 발견

**날짜**: 2024-10-12  
**소요 시간**: 4시간  
**타입**: 집중 실습 & 실험

---

## 목표

Week 1 색상 기반 실패 후,
Week 2는 모션 기반으로 전환.
Background Subtraction으로 공 검출 시도.

---

## 실험 타임라인

### v1: 기본 Background Subtraction
- Background Subtractor (MOG2, KNN) 학습
- 결과: 선수/공 검출 성공, 하지만 노이즈 많음

### v2: ROI 적용
- 관중석/광고판 제거
- 결과: 노이즈 70% 감소, 검출률 20%

### v3: 선수 제외 + 궤적 추적 ⭐
- 큰 객체(선수) 제거
- 이전 위치 기반 추적
- **결과: 50% 정확도, 연속 검출 성공!**

### v4: 적응형 필터
- 타원형 공 허용
- 결과: 오히려 악화 (20%)
- 교훈: 복잡 ≠ 좋음

---

## 최종 성과 (v3)

### 정량적 결과
- 검출률: 50% (10프레임 중 5개)
- 연속 검출: 성공 (500→505)
- 평균 후보: 4.7개 (초기 20개에서 감소)

### 정성적 결과
- ✅ 전방 선수 완벽 검출
- ✅ 후방 선수 대부분 검출
- ✅ 공 절반 정도 정확
- ❌ 모션 블러 시 실패
- ❌ 가려짐 시 실패

---

## 핵심 기술 습득

### 1. Background Subtraction
```python
bg_subtractor = cv2.createBackgroundSubtractorKNN(
    history=500,
    dist2Threshold=400,
    detectShadows=False
)
fg_mask = bg_subtractor.apply(frame)
```

### 2. ROI (Region of Interest)
```python
# 코트 영역만 분석
roi_mask[y1:y2, x1:x2] = 255
fg_mask = cv2.bitwise_and(fg_mask, fg_mask, mask=roi_mask)
```

### 3. 형태학적 연산
```python
# Opening: 작은 노이즈 제거
fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
# Closing: 구멍 메우기
fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
```

### 4. 크기 기반 분리
```python
# 큰 객체 = 선수 → 제거
# 작은 객체 = 공 후보 → 검출
```

### 5. 궤적 추적
```python
# 이전 위치에서 가까운 것 = 공
if last_ball_position:
    dist = distance(candidate['center'], last_ball_position)
    if dist < max_distance:
        selected = candidate
```

---

## 발견한 문제들

### 1. 모션 블러
**증상**: 빠른 공이 긴 타원으로 보임
**원인**: 30fps 카메라, 공 속도 100km/h
**결과**: 형태 변형 → 필터 통과 실패

### 2. 가려짐 (Occlusion)
**증상**: 선수 뒤에서 공 사라짐
**원인**: 단일 카메라 시점
**결과**: 추적 끊김

### 3. 크기
**증상**: 공이 5-10 픽셀
**원인**: 1280x720 해상도, 풀코트 뷰
**결과**: 노이즈와 구분 어려움

### 4. 배경 노이즈
**증상**: 라인, 관중, 그림자도 검출
**원인**: 배경도 조금씩 변함
**결과**: 후보 증가

---

## Background Subtraction의 한계

### 이론 vs 현실

**이론**:
- 움직이는 물체 검출
- 배경/전경 분리

**현실**:
- 작은 물체는 어려움
- 빠른 물체는 흐릿함
- 완벽한 배경은 없음

### 적합한 상황
- ✅ 느린 대상 (사람)
- ✅ 큰 대상
- ✅ 고정 카메라
- ✅ 안정적 조명

### 부적합한 상황
- ❌ 빠른 대상 (공)
- ❌ 작은 대상
- ❌ 자주 가려짐
- ❌ 복잡한 배경

---

## 배운 교훈

### 1. ROI의 힘
**효과**: 노이즈 70% 감소
**핵심**: 필요한 영역만 분석

### 2. 단순함의 가치
**발견**: v4(복잡) < v3(단순)
**교훈**: 과도한 최적화 경계

### 3. 점진적 개선
**과정**:
```
v1 (기본) → v2 (+ROI) → v3 (+선수제외+추적)
각 단계마다 명확한 개선
```

### 4. 문제의 난이도
**깨달음**: 
- 테니스 공 추적 = 어려운 문제
- 단일 기법으로는 부족
- 복합 접근 필요

---

## 다음 단계 (Week 2 Day 7-10)

### 현실적 선택

**Option A**: OpenCV Tracker
- 수동 초기화
- 추적에 집중
- 성공 확률 높음

**Option B**: Optical Flow
- 픽셀 움직임 벡터
- 다른 관점 시도

**Option C**: 프로젝트 재정의
- 목표 조정
- 달성 가능한 범위

**결정**: Day 7에서 논의

---

## 코드 산출물

1. `test_background_subtraction.py` - 기본
2. `test_ball_detection_v1.py` - 첫 시도
3. `test_ball_detection_v2.py` - ROI
4. `test_ball_tracking_v1.py` - 궤적
5. `test_ball_tracking_v2.py` - 신뢰도
6. **`test_ball_tracking_v3.py`** - 최종 (50%)

---

## 통계

- 작성 코드: ~800 줄
- 실험 횟수: 6회
- 소요 시간: 4시간
- 학습 내용: Background Subtraction, ROI, 형태학, 추적
- 최고 성과: 50% 정확도

---

## 참고 자료
- [OpenCV Background Subtraction](https://docs.opencv.org/4.x/d1/dc5/tutorial_background_subtraction.html)
- [Morphological Transformations](https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html)

---

## 회고

오늘은 정말 집중적으로 실험했다.

**감정의 롤러코스터**:
- 아침: 기대감
- 오후: 좌절 → 돌파 (ROI!)
- 저녁: 희열 (연속 검출!) → 현실 (한계 발견)

**가장 큰 배움**:
> "50%도 대단한 성과다. 완벽을 추구하다 아무것도 못 이룰 수 있다."

Background Subtraction만으로 50%를 달성한 것은 
개념 증명(Proof of Concept)으로 충분하다.

이제 더 나은 방법을 찾거나,
50%로도 의미 있는 것을 만들 방법을 고민해야 한다.

**내일 계획**:
- Week 2 방향 재설정
- 달성 가능한 목표
- 학습 중심 유지