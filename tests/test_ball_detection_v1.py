import cv2
import numpy as np
import os

def detect_ball_candidates(video_path, start_frame=200, num_frames=10):
    """
    Background Subtraction + 필터링으로 공 후보 검출
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("✗ 영상을 열 수 없습니다.")
        return
    
    # Background Subtractor (KNN 사용)
    bg_subtractor = cv2.createBackgroundSubtractorKNN(
        history=500,
        dist2Threshold=400,
        detectShadows=False  # 그림자 무시
    )
    
    print("공 후보 검출 테스트")
    print("=" * 50)
    
    # 출력 디렉토리
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_dir = os.path.join(project_root, 'data', 'ball_detection')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 배경 학습 (start_frame까지)
    print(f"\n배경 학습 중... (0 ~ {start_frame})")
    for i in range(start_frame):
        ret, frame = cap.read()
        if not ret:
            break
        bg_subtractor.apply(frame)
        if i % 50 == 0:
            print(f"  {i} 프레임...")
    
    print(f"✓ 배경 학습 완료\n")
    
    # 검출 시작
    print(f"공 검출 중... ({start_frame} ~ {start_frame + num_frames})")
    print("=" * 50)
    
    for i in range(num_frames):
        ret, frame = cap.read()
        if not ret:
            break
        
        current_frame = start_frame + i
        
        # 1. Background Subtraction
        fg_mask = bg_subtractor.apply(frame)
        
        # 2. 노이즈 제거 (Morphology)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        
        # Opening: 작은 노이즈 제거
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        
        # Closing: 구멍 메우기
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        
        # 3. 윤곽선 찾기
        contours, _ = cv2.findContours(
            fg_mask, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # 4. 공 후보 필터링
        ball_candidates = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # 크기 필터 (공은 작음)
            if area < 10 or area > 500:  # 픽셀 기준
                continue
            
            # 바운딩 박스
            x, y, w, h = cv2.boundingRect(contour)
            
            # 종횡비 필터 (공은 원형)
            aspect_ratio = w / h if h > 0 else 0
            if aspect_ratio < 0.5 or aspect_ratio > 2.0:
                continue
            
            # 위치 필터 (화면 하단 70%만 - 코트 영역)
            frame_height = frame.shape[0]
            if y < frame_height * 0.1:  # 상단 10% 제외
                continue
            
            # 원형도 검사
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            
            if circularity < 0.3:  # 0에 가까우면 선, 1에 가까우면 원
                continue
            
            # 공 후보로 추가
            ball_candidates.append({
                'contour': contour,
                'center': (x + w//2, y + h//2),
                'area': area,
                'bbox': (x, y, w, h),
                'circularity': circularity
            })
        
        # 5. 시각화
        result_frame = frame.copy()
        
        # 모든 공 후보 표시
        for candidate in ball_candidates:
            x, y, w, h = candidate['bbox']
            cx, cy = candidate['center']
            
            # 녹색 박스
            cv2.rectangle(result_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # 중심점
            cv2.circle(result_frame, (cx, cy), 3, (0, 0, 255), -1)
            
            # 정보 표시
            info = f"A:{candidate['area']:.0f} C:{candidate['circularity']:.2f}"
            cv2.putText(result_frame, info, (x, y-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
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
        
        print(f"Frame {current_frame:4d}: {len(ball_candidates)} 공 후보 검출")
    
    cap.release()
    
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
        # 500번 프레임부터 10개 분석
        detect_ball_candidates(video_path, start_frame=500, num_frames=10)