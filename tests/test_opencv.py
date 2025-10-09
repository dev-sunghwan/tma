import cv2
import numpy as np

print(f"OpenCV version: {cv2.__version__}")
print(f"NumPy version: {np.__version__}")

# 간단한 이미지 생성 테스트
img = np.zeros((300, 400, 3), dtype=np.uint8)
cv2.putText(img, 'Tennis Analyzer', (50, 150), 
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

# 이미지 저장
cv2.imwrite('test_output.jpg', img)
print("✓ OpenCV working! Check 'test_output.jpg'")