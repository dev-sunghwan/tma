import cv2
import os
import sys

def test_video_read(video_path):
    """
    영상 파일 읽기 테스트
    """
    # 절대 경로로 변환
    if not os.path.isabs(video_path):
        # 스크립트의 부모 디렉토리 (프로젝트 루트) 찾기
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        video_path = os.path.join(project_root, video_path.lstrip('../'))
    
    print(f"영상 경로: {video_path}")
    
    # 파일 존재 확인
    if not os.path.exists(video_path):
        print(f"✗ 파일을 찾을 수 없습니다: {video_path}")
        return False
    
    # 영상 열기
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("✗ 영상을 열 수 없습니다.")
        return False
    
    # 영상 정보 출력
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frame_count / fps if fps > 0 else 0
    
    print("=" * 50)
    print("영상 정보")
    print("=" * 50)
    print(f"해상도: {width} x {height}")
    print(f"FPS: {fps:.2f}")
    print(f"총 프레임 수: {frame_count}")
    print(f"재생 시간: {duration:.2f}초")
    print("=" * 50)
    
    # 첫 번째 프레임 읽기
    ret, frame = cap.read()
    
    if ret:
        # 첫 프레임 저장 (프로젝트 루트 기준)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        output_path = os.path.join(project_root, 'data', 'first_frame.jpg')
        
        cv2.imwrite(output_path, frame)
        print(f"✓ 첫 프레임 저장: {output_path}")
    else:
        print("✗ 프레임을 읽을 수 없습니다.")
        cap.release()
        return False
    
    # 리소스 해제
    cap.release()
    print("✓ 테스트 완료")
    return True

if __name__ == "__main__":
    # 여러 경로 시도
    possible_paths = [
        "../data/tennis_sample_1.mp4",
        "data/tennis_sample_1.mp4",
        "./data/tennis_sample_1.mp4"
    ]
    
    for video_path in possible_paths:
        if test_video_read(video_path):
            break