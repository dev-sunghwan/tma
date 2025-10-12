import cv2
import numpy as np
import os

def extract_multiple_frames(video_path, num_frames=10):
    """
    영상에서 여러 프레임 추출해서 공 찾기
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("✗ 영상을 열 수 없습니다.")
        return
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"총 프레임: {total_frames}")
    
    # 고르게 분산된 프레임 선택
    frame_indices = np.linspace(0, total_frames-1, num_frames, dtype=int)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_dir = os.path.join(project_root, 'data', 'frames')
    
    # 출력 디렉토리 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"\n{num_frames}개 프레임 추출 중...")
    print("=" * 50)
    
    for i, frame_idx in enumerate(frame_indices):
        # 특정 프레임으로 이동
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        
        if ret:
            # 프레임 저장
            frame_path = os.path.join(output_dir, f'frame_{i:02d}.jpg')
            cv2.imwrite(frame_path, frame)
            
            # 노란색 검출 테스트
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # 여러 노란색 범위 시도
            yellow_ranges = [
                ([20, 100, 100], [30, 255, 255], "standard"),
                ([15, 80, 80], [35, 255, 255], "wide"),
                ([25, 150, 150], [35, 255, 255], "bright"),
                ([20, 50, 200], [30, 255, 255], "bright_white"),  # 새로 추가!
                ([15, 30, 220], [35, 255, 255], "very_bright"),   # 새로 추가!
            ]
            
            best_count = 0
            best_range_name = ""
            
            for lower, upper, name in yellow_ranges:
                mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
                yellow_pixels = cv2.countNonZero(mask)
                
                if yellow_pixels > best_count:
                    best_count = yellow_pixels
                    best_range_name = name
                    best_mask = mask.copy()
            
            # 가장 좋은 마스크 저장
            mask_path = os.path.join(output_dir, f'mask_{i:02d}.jpg')
            cv2.imwrite(mask_path, best_mask)
            
            # 결과 적용
            result = cv2.bitwise_and(frame, frame, mask=best_mask)
            result_path = os.path.join(output_dir, f'yellow_{i:02d}.jpg')
            cv2.imwrite(result_path, result)
            
            print(f"Frame {i:02d} (#{frame_idx}): {best_count:5d} 노란색 픽셀 ({best_range_name})")
    
    cap.release()
    print("=" * 50)
    print(f"✓ 완료! 이미지 저장 위치: {output_dir}")
    print("\n확인 방법:")
    print(f"  open {output_dir}")

def analyze_frame_colors(image_path):
    """
    프레임의 색상 분포 분석
    """
    img = cv2.imread(image_path)
    if img is None:
        return
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    print("\n색상 분포 샘플 (100개 픽셀):")
    print("=" * 50)
    print("H(색조) | S(채도) | V(명도)")
    print("-" * 50)
    
    # 랜덤하게 100개 픽셀 샘플링
    h, w = hsv.shape[:2]
    for _ in range(10):
        y = np.random.randint(0, h)
        x = np.random.randint(0, w)
        h_val, s_val, v_val = hsv[y, x]
        print(f"  {h_val:3d}   |  {s_val:3d}   |  {v_val:3d}")
    
    print("=" * 50)
    print("참고: 테니스 공 노란색은 H=20-30 부근")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    video_path = os.path.join(project_root, 'data', 'tennis_sample_1.mp4')
    
    # 10개 프레임 추출 및 분석
    extract_multiple_frames(video_path, num_frames=10)
    
    # 첫 프레임 색상 분석
    first_frame = os.path.join(project_root, 'data', 'first_frame.jpg')
    if os.path.exists(first_frame):
        analyze_frame_colors(first_frame)