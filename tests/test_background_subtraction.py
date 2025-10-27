import cv2
import numpy as np
import os

def test_basic_bg_subtraction(video_path):
    """
    Background Subtraction 기초 테스트
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("✗ 영상을 열 수 없습니다.")
        return
    
    # Background Subtractor 생성
    # MOG2: detectShadows=True로 그림자도 감지
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(
        history=500,           # 학습할 프레임 수
        varThreshold=16,       # 전경/배경 구분 임계값
        detectShadows=True     # 그림자 감지
    )
    
    print("Background Subtraction 테스트")
    print("=" * 50)
    
    # 출력 디렉토리
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_dir = os.path.join(project_root, 'data', 'bg_subtraction')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    frame_count = 0
    save_frames = [0, 50, 100, 200, 500, 1000]  # 저장할 프레임 번호
    
    print("\n프레임 처리 중...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Background Subtraction 적용
        fg_mask = bg_subtractor.apply(frame)
        
        # 저장할 프레임이면 저장
        if frame_count in save_frames:
            # 원본
            cv2.imwrite(
                os.path.join(output_dir, f'frame_{frame_count:04d}_original.jpg'),
                frame
            )
            
            # 마스크 (전경)
            cv2.imwrite(
                os.path.join(output_dir, f'frame_{frame_count:04d}_mask.jpg'),
                fg_mask
            )
            
            # 전경만 추출
            fg_only = cv2.bitwise_and(frame, frame, mask=fg_mask)
            cv2.imwrite(
                os.path.join(output_dir, f'frame_{frame_count:04d}_foreground.jpg'),
                fg_only
            )
            
            print(f"  Frame {frame_count:4d} 저장 완료")
        
        frame_count += 1
        
        # 진행 상황 표시
        if frame_count % 100 == 0:
            print(f"  처리 중... {frame_count} 프레임")
    
    cap.release()
    
    print("=" * 50)
    print(f"✓ 총 {frame_count} 프레임 처리 완료")
    print(f"✓ 결과 저장: {output_dir}")
    print("\n확인:")
    print(f"  open {output_dir}")

def compare_algorithms(video_path):
    """
    여러 Background Subtraction 알고리즘 비교
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("✗ 영상을 열 수 없습니다.")
        return
    
    # 여러 알고리즘 생성
    algorithms = {
        'MOG2': cv2.createBackgroundSubtractorMOG2(),
        'KNN': cv2.createBackgroundSubtractorKNN(),
    }
    
    print("\nBackground Subtraction 알고리즘 비교")
    print("=" * 50)
    
    # 출력 디렉토리
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_dir = os.path.join(project_root, 'data', 'bg_comparison')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 특정 프레임에서 비교 (500번째)
    target_frame = 500
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 모든 알고리즘 적용 (학습용)
        for name, subtractor in algorithms.items():
            subtractor.apply(frame)
        
        # 목표 프레임 도달
        if frame_count == target_frame:
            # 원본 저장
            cv2.imwrite(
                os.path.join(output_dir, 'original.jpg'),
                frame
            )
            
            # 각 알고리즘 결과 저장
            for name, subtractor in algorithms.items():
                mask = subtractor.apply(frame)
                
                # 마스크
                cv2.imwrite(
                    os.path.join(output_dir, f'mask_{name}.jpg'),
                    mask
                )
                
                # 전경
                fg = cv2.bitwise_and(frame, frame, mask=mask)
                cv2.imwrite(
                    os.path.join(output_dir, f'foreground_{name}.jpg'),
                    fg
                )
                
                # 통계
                white_pixels = cv2.countNonZero(mask)
                total_pixels = mask.shape[0] * mask.shape[1]
                percentage = (white_pixels / total_pixels) * 100
                
                print(f"{name:10s}: {white_pixels:7d} 전경 픽셀 ({percentage:.2f}%)")
            
            break
        
        frame_count += 1
    
    cap.release()
    
    print("=" * 50)
    print(f"✓ Frame {target_frame}에서 알고리즘 비교 완료")
    print(f"✓ 결과 저장: {output_dir}")
    print("\n확인:")
    print(f"  open {output_dir}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    video_path = os.path.join(project_root, 'data', 'tennis_sample_1.mp4')
    
    if not os.path.exists(video_path):
        print(f"✗ 영상을 찾을 수 없습니다: {video_path}")
        print("먼저 영상을 다운로드하세요.")
    else:
        # 기본 테스트
        test_basic_bg_subtraction(video_path)
        
        print("\n" + "=" * 50)
        input("알고리즘 비교를 계속하려면 Enter를 누르세요...")
        
        # 알고리즘 비교
        compare_algorithms(video_path)