import cv2
import numpy as np
import os

def test_color_spaces(image_path):
    """
    색상 공간 변환 및 테니스 공 색상 검출 실험
    """
    # 이미지 읽기
    if not os.path.exists(image_path):
        print(f"✗ 이미지를 찾을 수 없습니다: {image_path}")
        return
    
    img = cv2.imread(image_path)
    if img is None:
        print("✗ 이미지를 읽을 수 없습니다.")
        return
    
    print(f"이미지 크기: {img.shape}")
    print(f"색상 공간: BGR (OpenCV 기본)")
    
    # HSV로 변환
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    print("✓ HSV로 변환 완료")
    
    # 노란색 범위 정의 (테니스 공)
    # HSV에서 노란색: H=20-30 정도
    lower_yellow = np.array([15, 50, 100])  # 하한값
    upper_yellow = np.array([35, 255, 255])  # 상한값
    
    # 노란색 마스크 생성
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    print("✓ 노란색 마스크 생성 완료")
    
    # 마스크 적용
    result = cv2.bitwise_and(img, img, mask=mask)
    
    # 결과 저장
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_dir = os.path.join(project_root, 'data')
    
    cv2.imwrite(os.path.join(output_dir, 'test_hsv.jpg'), hsv)
    cv2.imwrite(os.path.join(output_dir, 'test_mask.jpg'), mask)
    cv2.imwrite(os.path.join(output_dir, 'test_yellow_only.jpg'), result)
    
    print("=" * 50)
    print("저장된 파일:")
    print("  - test_hsv.jpg: HSV 변환 이미지")
    print("  - test_mask.jpg: 노란색 마스크")
    print("  - test_yellow_only.jpg: 노란색만 추출")
    print("=" * 50)
    print("✓ 색상 검출 테스트 완료")

def test_basic_processing(image_path):
    """
    기본 이미지 처리 기법 실습
    """
    img = cv2.imread(image_path)
    if img is None:
        return
    
    print("\n기본 이미지 처리 실습")
    print("=" * 50)
    
    # 1. 그레이스케일 변환
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    print("✓ 그레이스케일 변환")
    
    # 2. 블러 적용 (노이즈 제거)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    print("✓ 가우시안 블러 적용")
    
    # 3. 엣지 검출 (Canny)
    edges = cv2.Canny(blur, 50, 150)
    print("✓ Canny 엣지 검출")
    
    # 결과 저장
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_dir = os.path.join(project_root, 'data')
    
    cv2.imwrite(os.path.join(output_dir, 'test_gray.jpg'), gray)
    cv2.imwrite(os.path.join(output_dir, 'test_blur.jpg'), blur)
    cv2.imwrite(os.path.join(output_dir, 'test_edges.jpg'), edges)
    
    print("=" * 50)
    print("저장된 파일:")
    print("  - test_gray.jpg: 그레이스케일")
    print("  - test_blur.jpg: 블러 적용")
    print("  - test_edges.jpg: 엣지 검출")
    print("=" * 50)
    print("✓ 기본 처리 테스트 완료")

if __name__ == "__main__":
    # 첫 프레임 이미지 사용
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    image_path = os.path.join(project_root, 'data', 'first_frame.jpg')
    
    print("OpenCV 색상 공간 및 기본 처리 실습")
    print("=" * 50)
    
    # 색상 검출 테스트
    test_color_spaces(image_path)
    
    # 기본 처리 테스트
    test_basic_processing(image_path)