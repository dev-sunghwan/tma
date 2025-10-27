import cv2
import numpy as np
import os

def get_court_roi_mask(frame_shape):
    """코트 ROI"""
    height, width = frame_shape[:2]
    mask = np.zeros((height, width), dtype=np.uint8)
    
    y1 = int(height * 0.10)
    y2 = int(height * 0.90)
    x1 = int(width * 0.20)
    x2 = int(width * 0.80)
    
    mask[y1:y2, x1:x2] = 255
    return mask, (x1, y1, x2, y2)

def get_net_exclusion_mask(frame_shape):
    """
    네트 라인 근처 제외 마스크
    """
    height, width = frame_shape[:2]
    mask = np.ones((height, width), dtype=np.uint8) * 255
    
    # 네트 위치 (화면 중앙, 가로로)
    net_y_center = int(height * 0.45)  # 화면 45% 지점
    net_thickness = int(height * 0.05)  # 위아래 5%
    
    # 네트 근처 검정색으로
    mask[net_y_center - net_thickness:net_y_center + net_thickness, :] = 0
    
    return mask

def distance(p1, p2):
    """유클리드 거리"""
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def remove_large_objects(mask, min_area=500):
    """
    큰 객체(선수) 제거
    """
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 큰 객체 마스크
    large_objects_mask = np.zeros_like(mask)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > min_area:  # 큰 객체 (선수)
            cv2.drawContours(large_objects_mask, [contour], -1, 255, -1)
    
 # ⭐ 확장 (머리까지 커버)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    large_objects_mask = cv2.dilate(large_objects_mask, kernel, iterations=2)

    # 큰 객체 제거
    mask_without_large = cv2.bitwise_and(mask, cv2.bitwise_not(large_objects_mask))
    
    return mask_without_large, large_objects_mask

def track_ball_exclude_players(video_path, start_frame=200, num_frames=50):
    """
    선수 제외 후 공 추적
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
    
    print("선수 제외 공 추적")
    print("=" * 50)
    print(f"전략: 큰 객체(선수) 제거 → 작은 객체(공) 검출")
    print("=" * 50)
    
    bg_subtractor = cv2.createBackgroundSubtractorKNN(
        history=500,
        dist2Threshold=400,
        detectShadows=False
    )
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_dir = os.path.join(project_root, 'data', 'ball_tracking_v3')
    
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
    max_distance = 60  # 조금 더 여유있게
    
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
        
        # ⭐ 선수 제거
        fg_mask_small, players_mask = remove_large_objects(fg_mask, min_area=500)
        
        # 윤곽선 (작은 객체만)
        contours, _ = cv2.findContours(fg_mask_small, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 후보 필터링 (v1 수준으로 완화)
        candidates = []

        # ⭐ 네트 제외 마스크 적용
        net_mask = get_net_exclusion_mask(frame.shape)
        fg_mask_small = cv2.bitwise_and(fg_mask_small, fg_mask_small, mask=net_mask)

        for contour in contours:
            area = cv2.contourArea(contour)
            
            # 크기: v1 수준
            if area < 10 or area > 400:
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            
            # 종횡비: 완화 - 타원형 허용 (모션 블러)
            if aspect_ratio < 0.3 or aspect_ratio > 2.5:
                continue
            
            # ⭐ 높이 필터 (너무 위/아래 제외)
            frame_height = frame.shape[0]
            if y < frame_height * 0.15 or y > frame_height * 0.90:
                continue


            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            
            # 원형도: 완화 - 타원 허용
            if circularity < 0.25:
                continue
            
            center = (x + w//2, y + h//2)
            
            candidates.append({
                'center': center,
                'area': area,
                'bbox': (x, y, w, h),
                'circularity': circularity,
                'aspect_ratio': aspect_ratio
            })
        
        # 궤적 기반 선택
        selected_ball = None
        
        if last_ball_position is None:
            # 첫 프레임
            if candidates:
                selected_ball = max(candidates, key=lambda c: c['circularity'])
        else:
            # 가장 가까운 것
            nearby = []
            
            for candidate in candidates:
                dist = distance(candidate['center'], last_ball_position)
                
                if dist <= max_distance:
                    candidate['distance'] = dist
                    nearby.append(candidate)
            
            if nearby:
                # 거리와 원형도 조합
                # 가까우면서 둥근 것
                for c in nearby:
                    c['score'] = c['circularity'] / (c['distance'] + 1)
                
                selected_ball = max(nearby, key=lambda c: c['score'])
            elif candidates:
                # 근처에 없으면 원형도로
                selected_ball = max(candidates, key=lambda c: c['circularity'])
        
        # 궤적 업데이트
        if selected_ball:
            ball_trajectory.append({
                'frame': current_frame,
                'position': selected_ball['center'],
                'area': selected_ball['area'],
                'circularity': selected_ball['circularity']
            })
            last_ball_position = selected_ball['center']
        
        # 시각화
        result_frame = frame.copy()
        
        # ROI
        cv2.rectangle(result_frame, (x1, y1), (x2, y2), (100, 100, 100), 1)
        
        # 선수 영역 (빨간색)
        result_frame[players_mask > 0] = result_frame[players_mask > 0] * 0.5 + np.array([0, 0, 128]) * 0.5
        
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
            
            info = f"BALL: A={selected_ball['area']:.0f} C={selected_ball['circularity']:.2f}"
            cv2.putText(result_frame, info, (x, y-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        # 궤적
        if len(ball_trajectory) > 1:
            recent = ball_trajectory[-10:]
            for j in range(len(recent) - 1):
                pt1 = recent[j]['position']
                pt2 = recent[j+1]['position']
                cv2.line(result_frame, pt1, pt2, (255, 0, 0), 2)
        
        # 통계
        stats = f"Frame {current_frame} | Candidates: {len(candidates)} | Track: {len(ball_trajectory)}"
        cv2.putText(result_frame, stats, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # 저장
        if i % 5 == 0:
            # 3단계 비교
            cv2.imwrite(
                os.path.join(output_dir, f'frame_{current_frame:04d}_1_original.jpg'),
                frame
            )
            cv2.imwrite(
                os.path.join(output_dir, f'frame_{current_frame:04d}_2_mask_all.jpg'),
                fg_mask
            )
            cv2.imwrite(
                os.path.join(output_dir, f'frame_{current_frame:04d}_3_mask_small.jpg'),
                fg_mask_small
            )
            cv2.imwrite(
                os.path.join(output_dir, f'frame_{current_frame:04d}_4_players.jpg'),
                players_mask
            )
            cv2.imwrite(
                os.path.join(output_dir, f'frame_{current_frame:04d}_5_tracked.jpg'),
                result_frame
            )
        
        detected = "✓" if selected_ball else "✗"
        print(f"Frame {current_frame:4d}: {len(candidates):2d} 후보 | {detected}")
    
    cap.release()
    
    # 통계
    print("\n" + "=" * 50)
    print("추적 통계")
    print("=" * 50)
    print(f"총 프레임: {num_frames}")
    print(f"공 검출: {len(ball_trajectory)} ({len(ball_trajectory)/num_frames*100:.1f}%)")
    print("=" * 50)
    
    # CSV
    if ball_trajectory:
        csv_path = os.path.join(output_dir, 'ball_trajectory.csv')
        with open(csv_path, 'w') as f:
            f.write("frame,x,y,area,circularity\n")
            for point in ball_trajectory:
                f.write(f"{point['frame']},{point['position'][0]},{point['position'][1]},"
                       f"{point['area']:.1f},{point['circularity']:.3f}\n")
        print(f"✓ CSV: {csv_path}")
    
    print(f"\n✓ 완료: {output_dir}")
    print(f"  open {output_dir}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    video_path = os.path.join(project_root, 'data', 'tennis_sample_1.mp4')
    
    if not os.path.exists(video_path):
        print(f"✗ 영상 없음")
    else:
        track_ball_exclude_players(video_path, start_frame=500, num_frames=50)