import cv2
import os

def simple_test():
    """간단한 테스트"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    # video_path = os.path.join(project_root, 'data', 'tennis_sample_1.mp4')
    video_path = os.path.join(project_root, 'data', 'sinner_murray.mp4')
    
    cap = cv2.VideoCapture(video_path)
    
    # 500프레임으로 이동
    cap.set(cv2.CAP_PROP_POS_FRAMES, 500)
    
    ret, frame = cap.read()
    if not ret:
        print("프레임 읽기 실패")
        return
    
    print("박스를 그리세요 (SPACE/ENTER로 확인)")
    
    # 박스 그리기
    bbox = cv2.selectROI("Select Ball", frame, False)
    cv2.destroyWindow("Select Ball")
    
    if bbox[2] == 0 or bbox[3] == 0:
        print("취소됨")
        return
    
    print(f"선택 완료: {bbox}")
    
    # Tracker
    tracker = cv2.TrackerCSRT.create()
    tracker.init(frame, bbox)
    
    frame_count = 0
    
    while frame_count < 50:
        ret, frame = cap.read()
        if not ret:
            break
        
        success, bbox = tracker.update(frame)
        
        if success:
            x, y, w, h = [int(v) for v in bbox]
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        cv2.imshow("Tracking", frame)
        
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
        
        frame_count += 1
    
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"완료: {frame_count} 프레임")

if __name__ == "__main__":
    simple_test()