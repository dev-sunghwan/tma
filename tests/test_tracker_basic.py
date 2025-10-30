import cv2
import os

def test_manual_tracking(video_path, start_frame=500):
    """
    수동 초기화 + 자동 추적 테스트
    
    Args:
        start_frame: 시작 프레임 번호 (기본 500)
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("✗ 영상을 열 수 없습니다.")
        return
    
    print("OpenCV Tracker 테스트")
    print("=" * 50)
    print("사용 방법:")
    print("1. 영상이 열리면 공 주변에 박스를 그리세요")
    print("2. 마우스로 드래그하여 사각형 그리기")
    print("3. SPACE 또는 ENTER로 확인")
    print("4. ESC로 취소 후 다시 그리기 가능")
    print("=" * 50)
    
    # ⭐ 특정 프레임으로 이동 (랠리 중간)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    
    # 첫 프레임 읽기
    ret, frame = cap.read()
    if not ret:
        print("✗ 프레임을 읽을 수 없습니다.")
        return
    
    print(f"\nFrame {start_frame}에서 시작")
    print("공 주변에 박스를 그리세요...")
    
    # 수동으로 공 선택
    bbox = cv2.selectROI("Select Ball - Press SPACE/ENTER when done", frame, False)
    cv2.destroyWindow("Select Ball - Press SPACE/ENTER when done")
    
    if bbox[2] == 0 or bbox[3] == 0:
        print("✗ 선택이 취소되었습니다.")
        return
    
    x, y, w, h = [int(v) for v in bbox]
    print(f"✓ 선택 완료: 위치({x}, {y}), 크기({w}x{h})")
    
    # ⭐ CSRT Tracker 생성 (버전 호환)
    try:
        # OpenCV 4.5.1 이상
        tracker = cv2.TrackerCSRT.create()
    except AttributeError:
        try:
            # OpenCV 3.x ~ 4.5.0
            tracker = cv2.TrackerCSRT_create()
        except AttributeError:
            # Legacy
            tracker = cv2.legacy.TrackerCSRT_create()
    
    # 초기화
    tracker.init(frame, bbox)
    print("✓ Tracker 초기화 완료")
    
    # 출력 디렉토리
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_dir = os.path.join(project_root, 'data', 'tracker_test')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 추적 시작
    print("\n추적 시작...")
    print("=" * 50)
    print("q: 종료")
    print("=" * 50)
    
    frame_count = 0
    success_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - start_frame
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        current_frame = start_frame + frame_count
        
        # 자동 추적
        success, bbox = tracker.update(frame)
        
        if success:
            # 추적 성공
            success_count += 1
            x, y, w, h = [int(v) for v in bbox]
            
            # 녹색 박스
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # 중심점
            cx, cy = x + w//2, y + h//2
            cv2.circle(frame, (cx, cy), 3, (0, 0, 255), -1)
            
            # 상태 표시
            cv2.putText(frame, "Tracking", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            # 추적 실패
            cv2.putText(frame, "Lost", (50, 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        
        # 정보 표시
        cv2.putText(frame, f"Frame: {current_frame}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 성공률
        rate = (success_count / frame_count * 100) if frame_count > 0 else 0
        cv2.putText(frame, f"Success: {rate:.1f}%", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 화면 표시
        cv2.imshow('Tracker Test - Press Q to quit', frame)
        
        # 매 10프레임마다 저장
        if frame_count % 10 == 0:
            cv2.imwrite(
                os.path.join(output_dir, f'tracked_{current_frame:04d}.jpg'),
                frame
            )
        
        # 종료 또는 100프레임만
        key = cv2.waitKey(30) & 0xFF
        if key == ord('q') or frame_count >= 100:
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    # 결과 통계
    print("\n" + "=" * 50)
    print("추적 결과")
    print("=" * 50)
    print(f"시작 프레임: {start_frame}")
    print(f"추적 프레임: {frame_count}")
    print(f"추적 성공: {success_count} ({success_count/frame_count*100:.1f}%)")
    print(f"추적 실패: {frame_count - success_count}")
    print("=" * 50)
    print(f"✓ 결과 저장: {output_dir}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    video_path = os.path.join(project_root, 'data', 'tennis_sample_1.mp4')
    
    if not os.path.exists(video_path):
        print(f"✗ 영상을 찾을 수 없습니다: {video_path}")
    else:
        # Frame 500부터 시작 (랠리 중)
        test_manual_tracking(video_path, start_frame=500)