import cv2
import csv
import os

def rally_tracker_v2(video_path):
    """
    개선된 랠리 추적 (반응성 향상)
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("영상 열기 실패")
        return
    
    print("=" * 50)
    print("랠리 추적 v2")
    print("=" * 50)
    print("조작:")
    print("  SPACE: 일시정지/재생")
    print("  R: 랠리 추적 시작 (일시정지 시)")
    print("  S: 현재 랠리 저장")
    print("  Q 또는 ESC: 종료")
    print("=" * 50)
    
    # 출력 디렉토리
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_dir = os.path.join(project_root, 'data', 'rallies')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    rally_count = 0
    paused = False
    tracking = False
    tracker = None
    trajectory = []
    window_name = 'Rally Tracker - Press Q to Quit'
    
    # 창 생성
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                print("\n영상 끝")
                break
            
            current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            
            # 추적 중이면
            if tracking and tracker:
                success, bbox = tracker.update(frame)
                
                if success:
                    x, y, w, h = [int(v) for v in bbox]
                    trajectory.append([current_frame, x, y, w, h, 1])
                    
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cx, cy = x+w//2, y+h//2
                    cv2.circle(frame, (cx, cy), 3, (0, 0, 255), -1)
                    
                    # 상태
                    status_text = f"Rally {rally_count}: Tracking"
                    cv2.putText(frame, status_text, (x, y-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                else:
                    trajectory.append([current_frame, -1, -1, -1, -1, 0])
                    cv2.putText(frame, f"Rally {rally_count}: Lost", (50, 120),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            # 정보 표시
            cv2.putText(frame, f"Frame: {current_frame}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Rallies: {rally_count}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            if tracking and trajectory:
                rate = sum(1 for t in trajectory if t[5]==1) / len(trajectory) * 100
                cv2.putText(frame, f"Success: {rate:.1f}%", (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        else:
            # 일시정지
            cv2.putText(frame, "PAUSED", (50, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
            cv2.putText(frame, "Press R to start tracking", 
                       (50, frame.shape[0]//2),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        # 화면 표시
        cv2.imshow(window_name, frame)
        
        # ⭐ 키 입력 (더 짧은 대기)
        key = cv2.waitKey(1) & 0xFF
        
        # ⭐ Q 또는 ESC로 종료
        if key == ord('q') or key == ord('Q') or key == 27:
            print("\n종료 요청됨")
            
            # 추적 중이면 저장
            if tracking and trajectory:
                csv_path = os.path.join(output_dir, f'rally_{rally_count:02d}.csv')
                with open(csv_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['frame', 'x', 'y', 'width', 'height', 'success'])
                    writer.writerows(trajectory)
                print(f"✓ Rally {rally_count} 자동 저장: {len(trajectory)} 프레임")
            
            break
        
        elif key == ord(' '):
            # 일시정지/재생
            paused = not paused
            status = "일시정지" if paused else "재생"
            print(f"\n[{status}]")
        
        elif key == ord('r') or key == ord('R'):
            if not paused:
                print("\n[일시정지 상태에서 R을 누르세요]")
                continue
            
            # 랠리 추적 시작
            print("\n공 주변에 박스를 그리세요...")
            
            # 현재 프레임 저장
            saved_frame = frame.copy()
            
            # ⭐ 기존 창 잠시 숨기기
            cv2.destroyWindow(window_name)
            
            # ROI 선택
            bbox = cv2.selectROI("Select Ball (SPACE to confirm, ESC to cancel)", 
                                saved_frame, False, False)
            cv2.destroyWindow("Select Ball (SPACE to confirm, ESC to cancel)")
            
            # ⭐ 메인 창 다시 생성
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            
            if bbox[2] > 0 and bbox[3] > 0:
                # 이전 랠리 저장
                if tracking and trajectory:
                    csv_path = os.path.join(output_dir, f'rally_{rally_count:02d}.csv')
                    with open(csv_path, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(['frame', 'x', 'y', 'width', 'height', 'success'])
                        writer.writerows(trajectory)
                    print(f"✓ Rally {rally_count} 저장: {len(trajectory)} 프레임")
                
                # 새 추적 시작
                rally_count += 1
                tracker = cv2.TrackerCSRT.create()
                tracker.init(saved_frame, bbox)
                tracking = True
                trajectory = []
                paused = False
                
                print(f"✓ Rally {rally_count} 시작!")
            else:
                print("✗ 취소됨")
        
        elif key == ord('s') or key == ord('S'):
            # 현재 랠리 저장
            if tracking and trajectory:
                csv_path = os.path.join(output_dir, f'rally_{rally_count:02d}.csv')
                with open(csv_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['frame', 'x', 'y', 'width', 'height', 'success'])
                    writer.writerows(trajectory)
                print(f"\n✓ Rally {rally_count} 수동 저장: {len(trajectory)} 프레임")
                tracking = False
                trajectory = []
            else:
                print("\n저장할 랠리가 없습니다")
    
    # ⭐ 확실한 종료
    cap.release()
    cv2.destroyAllWindows()
    
    # ⭐ 창 완전히 닫기 (macOS 문제 해결)
    for _ in range(10):
        cv2.waitKey(1)
    
    # 최종 요약
    print("\n" + "=" * 50)
    print(f"총 {rally_count}개 랠리 추적 완료")
    print(f"저장 위치: {output_dir}")
    print("=" * 50)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    video_path = os.path.join(project_root, 'data', 'sinner_murray.mp4')
    
    if os.path.exists(video_path):
        try:
            rally_tracker_v2(video_path)
        except KeyboardInterrupt:
            print("\n\n✓ 사용자 중단 (Ctrl+C)")
        finally:
            cv2.destroyAllWindows()
    else:
        print(f"영상 없음: {video_path}")