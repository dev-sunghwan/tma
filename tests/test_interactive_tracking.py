import cv2
import numpy as np
import os
import csv
from datetime import datetime

class InteractiveTracker:
    """
    인터랙티브 공 추적 시스템
    """
    def __init__(self, video_path):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        
        if not self.cap.isOpened():
            raise ValueError("영상을 열 수 없습니다.")
        
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # 추적 상태
        self.tracker = None
        self.tracking = False
        self.paused = False
        self.rally_count = 0
        self.all_trajectories = []
        self.current_trajectory = []
        
        # 출력 디렉토리
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(script_dir)
        self.output_dir = os.path.join(self.project_root, 'data', 'rallies')
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def init_tracker(self, frame):
        """
        Tracker 초기화
        """
        print("\n" + "=" * 50)
        print("공 주변에 박스를 그리세요")
        print("SPACE/ENTER: 확인 | ESC: 취소")
        print("=" * 50)
        
        bbox = cv2.selectROI("Select Ball", frame, False)
        cv2.destroyWindow("Select Ball")
        
        if bbox[2] == 0 or bbox[3] == 0:
            print("✗ 취소됨")
            return False
        
        # Tracker 생성
        self.tracker = cv2.TrackerCSRT.create()
        self.tracker.init(frame, bbox)
        
        self.tracking = True
        self.rally_count += 1
        self.current_trajectory = []
        
        current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        print(f"✓ Rally {self.rally_count} 시작 (Frame {current_frame})")
        
        return True
    
    def save_rally(self):
        """
        현재 랠리 데이터 저장
        """
        if not self.current_trajectory:
            return
        
        # CSV 저장
        filename = f'rally_{self.rally_count:02d}.csv'
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['frame', 'x', 'y', 'width', 'height', 'success'])
            writer.writerows(self.current_trajectory)
        
        # 전체 데이터에 추가
        self.all_trajectories.append({
            'rally_id': self.rally_count,
            'start_frame': self.current_trajectory[0][0],
            'end_frame': self.current_trajectory[-1][0],
            'num_frames': len(self.current_trajectory),
            'trajectory': self.current_trajectory
        })
        
        print(f"✓ Rally {self.rally_count} 저장: {len(self.current_trajectory)} 프레임")
    
    def run(self):
        """
        메인 루프
        """
        print("=" * 50)
        print("인터랙티브 공 추적")
        print("=" * 50)
        print("조작법:")
        print("  SPACE: 일시정지/재생")
        print("  R: 새 랠리 시작 (일시정지 상태에서)")
        print("  S: 현재 랠리 저장 및 종료")
        print("  Q: 전체 종료")
        print("  →: 10프레임 앞으로")
        print("  ←: 10프레임 뒤로")
        print("=" * 50)
        
        delay = int(1000 / self.fps)
        
        while True:
            if not self.paused:
                ret, frame = self.cap.read()
                if not ret:
                    print("\n영상 끝")
                    break
                
                current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                
                # 추적 중이면 업데이트
                if self.tracking and self.tracker:
                    success, bbox = self.tracker.update(frame)
                    
                    if success:
                        x, y, w, h = [int(v) for v in bbox]
                        
                        # 데이터 저장
                        self.current_trajectory.append([
                            current_frame, x, y, w, h, 1
                        ])
                        
                        # 시각화
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        cx, cy = x + w//2, y + h//2
                        cv2.circle(frame, (cx, cy), 3, (0, 0, 255), -1)
                        
                        # 상태
                        cv2.putText(frame, f"Rally {self.rally_count}: Tracking", 
                                   (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 
                                   0.6, (0, 255, 0), 2)
                    else:
                        # 추적 실패
                        self.current_trajectory.append([
                            current_frame, -1, -1, -1, -1, 0
                        ])
                        
                        cv2.putText(frame, f"Rally {self.rally_count}: Lost", 
                                   (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 
                                   1, (0, 0, 255), 3)
                
                # 정보 표시
                cv2.putText(frame, f"Frame: {current_frame}/{self.total_frames}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"Rallies: {self.rally_count}", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                if self.tracking and self.current_trajectory:
                    success_rate = sum(1 for t in self.current_trajectory if t[5] == 1) / len(self.current_trajectory) * 100
                    cv2.putText(frame, f"Success: {success_rate:.1f}%", 
                               (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            else:
                # 일시정지 상태
                ret, frame = self.cap.read()
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 
                            self.cap.get(cv2.CAP_PROP_POS_FRAMES) - 1)
                
                if not ret:
                    break
                
                cv2.putText(frame, "PAUSED - Press R to start rally", 
                           (50, self.height//2), cv2.FONT_HERSHEY_SIMPLEX, 
                           1, (0, 255, 255), 3)
            
            # 화면 표시
            cv2.imshow('Interactive Tracking', frame)
            
            # 키 입력
            key = cv2.waitKey(delay if not self.paused else 100) & 0xFF

            if key != 255:  # ⭐ 키가 눌리면 출력
                print(f"[DEBUG] Key pressed: {key} ('{chr(key) if 32 <= key <= 126 else '?'}')")

            if key == ord('q'):
                # 종료
                if self.tracking and self.current_trajectory:
                    self.save_rally()
                break
            elif key == ord(' '):
                # 일시정지/재생
                self.paused = not self.paused
                status = "일시정지" if self.paused else "재생"
                print(f"\n[{status}]")
            elif key == ord('r'):
                print(f"[DEBUG] R key detected, paused={self.paused}")
                
                # 새 랠리 시작
                if self.tracking and self.current_trajectory:
                    print("[DEBUG] Saving previous rally...")
                    self.save_rally()
                    self.tracking = False
                
                # ⭐ 현재 프레임 가져오기 (더 확실하게)
                current_frame_num = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                
                # ⭐ 이미 읽은 프레임 사용 (일시정지 상태에서 저장된 것)
                # 또는 새로 읽기
                if 'frame' not in locals() or frame is None:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_num - 1)
                    ret, frame = self.cap.read()
                else:
                    ret = True
                
                print(f"[DEBUG] Current frame: {current_frame_num}, ret={ret}")
                
                if ret and frame is not None:
                    print("[DEBUG] Calling init_tracker...")
                    # ⭐ 박스 그리기 전에 창 확인
                    cv2.destroyAllWindows()  # 기존 창 닫기
                    success = self.init_tracker(frame)
                    if success:
                        self.paused = False
                else:
                    print("[DEBUG] Failed to read frame")

                # 현재 랠리 저장 및 종료
                if self.tracking and self.current_trajectory:
                    self.save_rally()
                    self.tracking = False
                    print("\n현재 랠리 저장 완료")
            elif key == 83:  # 오른쪽 화살표
                # 10프레임 앞으로
                current = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, min(current + 10, self.total_frames))
                print(f"\n→ Frame {int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))}")
            elif key == 81:  # 왼쪽 화살표
                # 10프레임 뒤로
                current = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, max(current - 10, 0))
                print(f"\n← Frame {int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))}")
        
        self.cap.release()
        cv2.destroyAllWindows()
        
        # 최종 요약
        self.print_summary()
    
    def print_summary(self):
        """
        전체 요약 출력
        """
        print("\n" + "=" * 50)
        print("추적 완료")
        print("=" * 50)
        print(f"총 랠리: {self.rally_count}")
        
        if self.all_trajectories:
            total_frames = sum(r['num_frames'] for r in self.all_trajectories)
            print(f"총 추적 프레임: {total_frames}")
            print("\n랠리별 상세:")
            print("-" * 50)
            
            for rally in self.all_trajectories:
                print(f"Rally {rally['rally_id']}: "
                      f"Frame {rally['start_frame']}-{rally['end_frame']} "
                      f"({rally['num_frames']} 프레임)")
        
        print("=" * 50)
        print(f"✓ 데이터 저장: {self.output_dir}")
        
        # 통합 CSV 생성
        if self.all_trajectories:
            self.create_merged_csv()
    
    def create_merged_csv(self):
        """
        모든 랠리 데이터 통합 CSV
        """
        filepath = os.path.join(self.output_dir, 'all_rallies.csv')
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['rally_id', 'frame', 'x', 'y', 'width', 'height', 'success'])
            
            for rally in self.all_trajectories:
                for point in rally['trajectory']:
                    writer.writerow([rally['rally_id']] + point)
        
        print(f"✓ 통합 CSV: {filepath}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    # video_path = os.path.join(project_root, 'data', 'tennis_sample_1.mp4')
    video_path = os.path.join(project_root, 'data', 'sinner_murray.mp4')
    
    if not os.path.exists(video_path):
        print(f"✗ 영상을 찾을 수 없습니다: {video_path}")
    else:
        try:
            tracker = InteractiveTracker(video_path)
            tracker.run()
        except Exception as e:
            print(f"✗ 에러: {e}")
            import traceback
            traceback.print_exc()