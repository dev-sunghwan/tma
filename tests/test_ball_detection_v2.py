import cv2
import numpy as np
import os

def get_court_roi_mask(frame_shape):
    """
    코트 영역 ROI 마스크 생성
    """
    height, width = frame_shape[:2]
    mask = np.zeros((height, width), dtype=np.uint8)
    
    # 간단한 직사각형 ROI
    # 상단 15% 제거 (관중석)
    # 하단 10% 제거 (광고판)
    # 좌우 5% 제거 (가장자리)
    
    y1 = int(height * 0.10)  # 상단 10%부터
    y2 = int(height * 0.90)  # 하단 90%까지
    x1 = int(width * 0.20)   # 좌측 10%부터
    x2 = int(width * 0.80)   # 우측 90%까지
    
    # ROI 영역을 흰색으로
    mask[y1:y2, x1:x2] = 255
    
    return mask, (x1, y1, x2, y2)

def detect_ball_with_roi(video_path, start_frame=200, num_frames=10):
    """
    ROI를 적용한 공 검출
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
    
    print("공 검출 v2 (ROI 적용)")
    print("=" * 50)
    print(f"ROI 영역: ({x1}, {y1}) ~ ({x2}, {y2})")
    print(f"원본 크기: {first_frame.shape[1]} x {first_frame.shape[0]}")
    print(f"ROI 크기: {x2-x1} x {y2-y1}")
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
    output_dir = os.path.join(project_root, 'data', 'ball_detection_v2')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # ROI 마스크 시각화 저장
    roi_visualization = first_frame.copy()
    roi_visualization[roi_mask == 0] = roi_visualization[roi_mask == 0] // 3  # 어둡게
    cv2.rectangle(roi_visualization, (x1, y1), (x2, y2), (0, 255, 0), 3)
    cv2.putText(roi_visualization, "Court ROI", (x1+10, y1+30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imwrite(os.path.join(output_dir, 'roi_mask.jpg'), roi_visualization)
    
    # 시작 위치로 이동
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    # 배경 학습
    print(f"\n배경 학습 중... (0 ~ {start_frame})")
    for i in range(start_frame):
        ret, frame = cap.read()
        if not ret:
            break
        
        # ROI 영역만 학습
        frame_roi = cv2.bitwise_and(frame, frame, mask=roi_mask)
        bg_subtractor.apply(frame_roi)
        
        if i % 50 == 0:
            print(f"  {i} 프레임...")
    
    print(f"✓ 배경 학습 완료\n")
    
    # 검출 시작
    print(f"공 검출 중... ({start_frame} ~ {start_frame + num_frames})")
    print("=" * 50)
    
    detection_stats = []
    
    for i in range(num_frames):
        ret, frame = cap.read()
        if not ret:
            break
        
        current_frame = start_frame + i
        
        # 1. ROI 적용
        frame_roi = cv2.bitwise_and(frame, frame, mask=roi_mask)
        
        # 2. Background Subtraction
        fg_mask = bg_subtractor.apply(frame_roi)
        
        # 3. ROI로 다시 한번 마스킹 (확실하게)
        fg_mask = cv2.bitwise_and(fg_mask, fg_mask, mask=roi_mask)
        
        # 4. 노이즈 제거
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel, iterations=2)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        
        # 5. 윤곽선 찾기
        contours, _ = cv2.findContours(
            fg_mask, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # 6. 공 후보 필터링 (더 엄격하게)
        ball_candidates = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # 크기 필터 (더 좁은 범위)
            if area < 10 or area > 400:  # 공은 작음
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            
            # 종횡비 필터 (원형)
            aspect_ratio = w / h if h > 0 else 0
            if aspect_ratio < 0.5 or aspect_ratio > 2.0:
                continue
            
            # 원형도 검사 (더 엄격)
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            
            if circularity < 0.3:  # 더 원형에 가까워야 함
                continue
            
            ball_candidates.append({
                'contour': contour,
                'center': (x + w//2, y + h//2),
                'area': area,
                'bbox': (x, y, w, h),
                'circularity': circularity
            })
        
        # 7. 가장 유력한 후보 선택 (원형도 기준)
        if ball_candidates:
            # 원형도가 가장 높은 것 (공일 가능성 높음)
            best_candidate = max(ball_candidates, key=lambda c: c['circularity'])
        else:
            best_candidate = None
        
        # 8. 시각화
        result_frame = frame.copy()
        
        # ROI 경계 표시
        cv2.rectangle(result_frame, (x1, y1), (x2, y2), (100, 100, 100), 1)
        
        # 모든 후보 (회색)
        for candidate in ball_candidates:
            x, y, w, h = candidate['bbox']
            cv2.rectangle(result_frame, (x, y), (x+w, y+h), (128, 128, 128), 1)
        
        # 최고 후보 (녹색, 굵게)
        if best_candidate:
            x, y, w, h = best_candidate['bbox']
            cx, cy = best_candidate['center']
            
            cv2.rectangle(result_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.circle(result_frame, (cx, cy), 3, (0, 0, 255), -1)
            
            info = f"BALL: A={best_candidate['area']:.0f} C={best_candidate['circularity']:.2f}"
            cv2.putText(result_frame, info, (x, y-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # 통계 표시
        stats_text = f"Frame {current_frame} | Candidates: {len(ball_candidates)}"
        cv2.putText(result_frame, stats_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # 저장
        cv2.imwrite(
            os.path.join(output_dir, f'frame_{current_frame:04d}_original.jpg'),
            frame
        )
        cv2.imwrite(
            os.path.join(output_dir, f'frame_{current_frame:04d}_mask_cleaned.jpg'),
            fg_mask
        )
        cv2.imwrite(
            os.path.join(output_dir, f'frame_{current_frame:04d}_detected.jpg'),
            result_frame
        )
        
        detection_stats.append({
            'frame': current_frame,
            'candidates': len(ball_candidates),
            'detected': best_candidate is not None
        })
        
        print(f"Frame {current_frame:4d}: {len(ball_candidates):2d} 후보, "
              f"최고: {'공 검출!' if best_candidate else '없음'}")
    
    cap.release()
    
    # 통계 요약
    print("\n" + "=" * 50)
    print("검출 통계")
    print("=" * 50)
    detected_count = sum(1 for s in detection_stats if s['detected'])
    avg_candidates = np.mean([s['candidates'] for s in detection_stats])
    print(f"공 검출 프레임: {detected_count}/{num_frames}")
    print(f"평균 후보 수: {avg_candidates:.1f}")
    print("=" * 50)
    print(f"✓ 완료! 결과: {output_dir}")
    print("\n확인:")
    print(f"  open {output_dir}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    video_path = os.path.join(project_root, 'data', 'tennis_sample_1.mp4')
    
    if not os.path.exists(video_path):
        print(f"✗ 영상을 찾을 수 없습니다: {video_path}")
    else:
        detect_ball_with_roi(video_path, start_frame=500, num_frames=10)