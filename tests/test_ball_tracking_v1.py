import cv2
import numpy as np
import os

def get_court_roi_mask(frame_shape):
    """
    코트 영역 ROI 마스크 생성
    """
    height, width = frame_shape[:2]
    mask = np.zeros((height, width), dtype=np.uint8)
    
    # 당신이 조정한 값으로 (필요시 수정)
    y1 = int(height * 0.10)
    y2 = int(height * 0.90)
    x1 = int(width * 0.20)
    x2 = int(width * 0.80)
    
    mask[y1:y2, x1:x2] = 255
    
    return mask, (x1, y1, x2, y2)

def distance(p1, p2):
    """
    두 점 사이의 유클리드 거리
    """
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def track_ball_with_trajectory(video_path, start_frame=200, num_frames=50):
    """
    궤적 추적으로 공 검출
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("✗ 영상을 열 수 없습니다.")
        return
    
    # 첫 프레임으로 ROI 생성
    ret, first_frame = cap.read()
    if not ret:
        return
    
    roi_mask, roi_coords = get_court_roi_mask(first_frame.shape)
    x1, y1, x2, y2 = roi_coords
    
    print("공 궤적 추적")
    print("=" * 50)
    print(f"ROI 영역: ({x1}, {y1}) ~ ({x2}, {y2})")
    print(f"분석 프레임: {start_frame} ~ {start_frame + num_frames}")
    print("=" * 50)
    
    # Background Subtractor
    bg_subtractor = cv2.createBackgroundSubtractorKNN(
        history=500,
        dist2Threshold=400,
        detectShadows=False
    )
    
    # 출력 디렉토리
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_dir = os.path.join(project_root, 'data', 'ball_tracking')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 시작 위치로 이동
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    # 배경 학습
    print(f"\n배경 학습 중... (0 ~ {start_frame})")
    for i in range(start_frame):
        ret, frame = cap.read()
        if not ret:
            break
        frame_roi = cv2.bitwise_and(frame, frame, mask=roi_mask)
        bg_subtractor.apply(frame_roi)
        if i % 50 == 0:
            print(f"  {i} 프레임...")
    
    print(f"✓ 배경 학습 완료\n")
    
    # 추적 변수
    ball_trajectory = []  # [(frame_num, x, y), ...]
    last_ball_position = None
    max_distance = 50  # 프레임 간 최대 이동 거리 (픽셀)
    
    # 검출 시작
    print(f"공 추적 중...")
    print("=" * 50)
    
    for i in range(num_frames):
        ret, frame = cap.read()
        if not ret:
            break
        
        current_frame = start_frame + i
        
        # 1. ROI + Background Subtraction
        frame_roi = cv2.bitwise_and(frame, frame, mask=roi_mask)
        fg_mask = bg_subtractor.apply(frame_roi)
        fg_mask = cv2.bitwise_and(fg_mask, fg_mask, mask=roi_mask)
        
        # 2. 노이즈 제거
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel, iterations=2)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        
        # 3. 윤곽선 찾기
        contours, _ = cv2.findContours(
            fg_mask, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # 4. 후보 필터링
        candidates = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            if area < 10 or area > 400:
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            
            if aspect_ratio < 0.5 or aspect_ratio > 2.0:
                continue
            
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            
            if circularity < 0.3:
                continue
            
            center = (x + w//2, y + h//2)
            
            candidates.append({
                'center': center,
                'area': area,
                'bbox': (x, y, w, h),
                'circularity': circularity
            })
        
        # 5. 궤적 기반 선택 ⭐
        selected_ball = None
        
        if last_ball_position is None:
            # 첫 프레임: 원형도가 가장 높은 것
            if candidates:
                selected_ball = max(candidates, key=lambda c: c['circularity'])
        else:
            # 이후 프레임: 이전 위치에서 가장 가까운 것
            nearby_candidates = []
            
            for candidate in candidates:
                dist = distance(candidate['center'], last_ball_position)
                
                # 너무 멀면 제외 (순간이동 방지)
                if dist <= max_distance:
                    candidate['distance'] = dist
                    nearby_candidates.append(candidate)
            
            if nearby_candidates:
                # 가장 가까운 것 선택
                selected_ball = min(nearby_candidates, key=lambda c: c['distance'])
            elif candidates:
                # 근처에 없으면 원형도로 선택 (공이 빠르게 움직인 경우)
                selected_ball = max(candidates, key=lambda c: c['circularity'])
        
        # 6. 궤적 업데이트
        if selected_ball:
            ball_trajectory.append({
                'frame': current_frame,
                'position': selected_ball['center'],
                'area': selected_ball['area'],
                'circularity': selected_ball['circularity']
            })
            last_ball_position = selected_ball['center']
        
        # 7. 시각화
        result_frame = frame.copy()
        
        # ROI 경계
        cv2.rectangle(result_frame, (x1, y1), (x2, y2), (100, 100, 100), 1)
        
        # 모든 후보 (회색)
        for candidate in candidates:
            x, y, w, h = candidate['bbox']
            cv2.rectangle(result_frame, (x, y), (x+w, y+h), (128, 128, 128), 1)
        
        # 선택된 공 (녹색)
        if selected_ball:
            x, y, w, h = selected_ball['bbox']
            cx, cy = selected_ball['center']
            
            cv2.rectangle(result_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.circle(result_frame, (cx, cy), 5, (0, 0, 255), -1)
            
            info = f"BALL"
            cv2.putText(result_frame, info, (x, y-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # 궤적 그리기 (최근 10개)
        if len(ball_trajectory) > 1:
            recent_trajectory = ball_trajectory[-10:]  # 최근 10개
            for j in range(len(recent_trajectory) - 1):
                pt1 = recent_trajectory[j]['position']
                pt2 = recent_trajectory[j+1]['position']
                cv2.line(result_frame, pt1, pt2, (255, 0, 0), 2)  # 파란 선
        
        # 통계
        stats_text = f"Frame {current_frame} | Candidates: {len(candidates)} | Track: {len(ball_trajectory)}"
        cv2.putText(result_frame, stats_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # 저장 (10프레임마다)
        if i % 5 == 0:
            cv2.imwrite(
                os.path.join(output_dir, f'frame_{current_frame:04d}_tracked.jpg'),
                result_frame
            )
        
        detected = "✓" if selected_ball else "✗"
        print(f"Frame {current_frame:4d}: {len(candidates):2d} 후보 | {detected} | 궤적 길이: {len(ball_trajectory)}")
    
    cap.release()
    
    # 통계
    print("\n" + "=" * 50)
    print("추적 통계")
    print("=" * 50)
    print(f"총 프레임: {num_frames}")
    print(f"공 검출: {len(ball_trajectory)} 프레임 ({len(ball_trajectory)/num_frames*100:.1f}%)")
    print(f"궤적 길이: {len(ball_trajectory)} 포인트")
    print("=" * 50)
    
    # 궤적 CSV 저장
    if ball_trajectory:
        csv_path = os.path.join(output_dir, 'ball_trajectory.csv')
        with open(csv_path, 'w') as f:
            f.write("frame,x,y,area,circularity\n")
            for point in ball_trajectory:
                f.write(f"{point['frame']},{point['position'][0]},{point['position'][1]},"
                       f"{point['area']:.1f},{point['circularity']:.3f}\n")
        print(f"✓ 궤적 데이터 저장: {csv_path}")
    
    print(f"\n✓ 완료! 결과: {output_dir}")
    print("\n확인:")
    print(f"  open {output_dir}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    video_path = os.path.join(project_root, 'data', 'tennis_sample_1.mp4')
    
    if not os.path.exists(video_path):
        print(f"✗ 영상을 찾을 수 없습니다: {video_path}")
    else:
        # 500번 프레임부터 50개 추적
        track_ball_with_trajectory(video_path, start_frame=500, num_frames=50)