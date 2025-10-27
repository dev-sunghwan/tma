import cv2
import numpy as np
import os

def get_court_roi_mask(frame_shape):
    """코트 영역 ROI 마스크"""
    height, width = frame_shape[:2]
    mask = np.zeros((height, width), dtype=np.uint8)
    
    y1 = int(height * 0.10)
    y2 = int(height * 0.90)
    x1 = int(width * 0.20)
    x2 = int(width * 0.80)
    
    mask[y1:y2, x1:x2] = 255
    return mask, (x1, y1, x2, y2)

def distance(p1, p2):
    """유클리드 거리"""
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def track_ball_with_confidence(video_path, start_frame=200, num_frames=50):
    """
    신뢰도 기반 공 추적
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("✗ 영상을 열 수 없습니다.")
        return
    
    ret, first_frame = cap.read()
    if not ret:
        return
    
    roi_mask, roi_coords = get_court_roi_mask(first_frame.shape)
    x1, y1, x2, y2 = roi_coords
    
    print("신뢰도 기반 공 추적")
    print("=" * 50)
    print(f"ROI: ({x1}, {y1}) ~ ({x2}, {y2})")
    print("=" * 50)
    
    bg_subtractor = cv2.createBackgroundSubtractorKNN(
        history=500,
        dist2Threshold=400,
        detectShadows=False
    )
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_dir = os.path.join(project_root, 'data', 'ball_tracking_v2')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    # 배경 학습
    print(f"\n배경 학습 중...")
    for i in range(start_frame):
        ret, frame = cap.read()
        if not ret:
            break
        frame_roi = cv2.bitwise_and(frame, frame, mask=roi_mask)
        bg_subtractor.apply(frame_roi)
        if i % 50 == 0:
            print(f"  {i} 프레임...")
    
    print(f"✓ 완료\n")
    
    # 추적 변수
    ball_trajectory = []
    last_ball_position = None
    tracking_confidence = 0  # 신뢰도 점수 ⭐
    max_distance = 50
    min_confidence = -2  # 이하면 추적 중단
    
    print("추적 시작...")
    print("=" * 50)
    
    for i in range(num_frames):
        ret, frame = cap.read()
        if not ret:
            break
        
        current_frame = start_frame + i
        
        # Background Subtraction
        frame_roi = cv2.bitwise_and(frame, frame, mask=roi_mask)
        fg_mask = bg_subtractor.apply(frame_roi)
        fg_mask = cv2.bitwise_and(fg_mask, fg_mask, mask=roi_mask)
        
        # 노이즈 제거
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel, iterations=2)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        
        # 윤곽선
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 후보 필터링
        candidates = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # 크기: 공은 작음, 선수는 큼
            if area < 15 or area > 250:  # 더 좁은 범위 ⭐
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            
            if aspect_ratio < 0.6 or aspect_ratio > 1.7:  # 더 엄격 ⭐
                continue
            
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            
            if circularity < 0.4:  # 더 엄격 ⭐
                continue
            
            center = (x + w//2, y + h//2)
            
            candidates.append({
                'center': center,
                'area': area,
                'bbox': (x, y, w, h),
                'circularity': circularity
            })
        
        # 신뢰도 기반 선택 ⭐
        selected_ball = None
        selection_method = ""
        
        # 신뢰도가 낮으면 추적 리셋
        if tracking_confidence < min_confidence:
            last_ball_position = None
            tracking_confidence = 0
            selection_method = "RESET"
        
        if last_ball_position is None:
            # 첫 프레임 or 리셋: 원형도 최고
            if candidates:
                selected_ball = max(candidates, key=lambda c: c['circularity'])
                selection_method = "INIT"
                tracking_confidence = 1
        else:
            # 궤적 기반
            nearby = []
            
            for candidate in candidates:
                dist = distance(candidate['center'], last_ball_position)
                
                if dist <= max_distance:
                    # 속도 체크 ⭐
                    speed = dist  # 프레임당 픽셀
                    if speed > 40:  # 너무 빠르면 의심
                        continue
                    
                    candidate['distance'] = dist
                    nearby.append(candidate)
            
            if nearby:
                # 가까운 것 중 가장 둥근 것 ⭐
                nearby_sorted = sorted(nearby, key=lambda c: c['circularity'], reverse=True)
                selected_ball = nearby_sorted[0]
                
                # 거리도 고려
                if selected_ball['distance'] < 20:
                    tracking_confidence += 1  # 가까우면 신뢰도 상승
                    selection_method = "TRACK_GOOD"
                else:
                    tracking_confidence -= 0.5  # 좀 멀면 의심
                    selection_method = "TRACK_WEAK"
            else:
                # 근처에 없음 → 공 놓침
                tracking_confidence -= 1
                selection_method = "LOST"
                
                # 신뢰도 여유 있으면 원형도로 시도
                if tracking_confidence > 0 and candidates:
                    selected_ball = max(candidates, key=lambda c: c['circularity'])
                    selection_method = "RECOVER"
        
        # 궤적 업데이트
        if selected_ball:
            ball_trajectory.append({
                'frame': current_frame,
                'position': selected_ball['center'],
                'area': selected_ball['area'],
                'circularity': selected_ball['circularity'],
                'confidence': tracking_confidence,
                'method': selection_method
            })
            last_ball_position = selected_ball['center']
        
        # 신뢰도 제한
        tracking_confidence = max(min_confidence, min(tracking_confidence, 5))
        
        # 시각화
        result_frame = frame.copy()
        
        # ROI
        cv2.rectangle(result_frame, (x1, y1), (x2, y2), (100, 100, 100), 1)
        
        # 모든 후보 (회색)
        for candidate in candidates:
            x, y, w, h = candidate['bbox']
            cv2.rectangle(result_frame, (x, y), (x+w, y+h), (128, 128, 128), 1)
        
        # 선택된 공
        if selected_ball:
            x, y, w, h = selected_ball['bbox']
            cx, cy = selected_ball['center']
            
            # 신뢰도에 따라 색상 변경 ⭐
            if tracking_confidence > 2:
                color = (0, 255, 0)  # 녹색: 높은 신뢰도
            elif tracking_confidence > 0:
                color = (0, 255, 255)  # 노랑: 중간
            else:
                color = (0, 165, 255)  # 주황: 낮음
            
            cv2.rectangle(result_frame, (x, y), (x+w, y+h), color, 2)
            cv2.circle(result_frame, (cx, cy), 5, (0, 0, 255), -1)
            
            info = f"{selection_method}"
            cv2.putText(result_frame, info, (x, y-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        # 궤적 (최근 10개)
        if len(ball_trajectory) > 1:
            recent = ball_trajectory[-10:]
            for j in range(len(recent) - 1):
                pt1 = recent[j]['position']
                pt2 = recent[j+1]['position']
                cv2.line(result_frame, pt1, pt2, (255, 0, 0), 2)
        
        # 통계
        conf_text = f"Confidence: {tracking_confidence:.1f} | Method: {selection_method}"
        cv2.putText(result_frame, conf_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        stats = f"Frame {current_frame} | Candidates: {len(candidates)}"
        cv2.putText(result_frame, stats, (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # 저장 (매 5프레임)
        if i % 5 == 0:
            cv2.imwrite(
                os.path.join(output_dir, f'frame_{current_frame:04d}_tracked.jpg'),
                result_frame
            )
        
        detected = "✓" if selected_ball else "✗"
        print(f"Frame {current_frame:4d}: {len(candidates):2d} 후보 | {detected} | "
              f"신뢰도: {tracking_confidence:4.1f} | {selection_method}")
    
    cap.release()
    
    # 통계
    print("\n" + "=" * 50)
    print("추적 통계")
    print("=" * 50)
    print(f"총 프레임: {num_frames}")
    print(f"공 검출: {len(ball_trajectory)} ({len(ball_trajectory)/num_frames*100:.1f}%)")
    
    # 방법별 통계
    methods = {}
    for point in ball_trajectory:
        method = point['method']
        methods[method] = methods.get(method, 0) + 1
    
    print("\n검출 방법 분포:")
    for method, count in sorted(methods.items()):
        print(f"  {method:15s}: {count:3d} ({count/len(ball_trajectory)*100:.1f}%)")
    
    print("=" * 50)
    
    # CSV 저장
    if ball_trajectory:
        csv_path = os.path.join(output_dir, 'ball_trajectory.csv')
        with open(csv_path, 'w') as f:
            f.write("frame,x,y,area,circularity,confidence,method\n")
            for point in ball_trajectory:
                f.write(f"{point['frame']},{point['position'][0]},{point['position'][1]},"
                       f"{point['area']:.1f},{point['circularity']:.3f},"
                       f"{point['confidence']:.1f},{point['method']}\n")
        print(f"✓ 궤적 저장: {csv_path}")
    
    print(f"\n✓ 완료: {output_dir}")
    print(f"  open {output_dir}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    video_path = os.path.join(project_root, 'data', 'tennis_sample_1.mp4')
    
    if not os.path.exists(video_path):
        print(f"✗ 영상 없음: {video_path}")
    else:
        track_ball_with_confidence(video_path, start_frame=500, num_frames=50)