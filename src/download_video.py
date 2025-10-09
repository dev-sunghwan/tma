import yt_dlp
import os

def download_tennis_video(url, output_path='../data', filename='tennis_sample'):
    """
    YouTube에서 테니스 영상 다운로드
    
    Args:
        url: YouTube URL
        output_path: 저장 경로
        filename: 파일명 (확장자 제외)
    """
    # 저장 경로 확인
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    # yt-dlp 옵션 설정
    ydl_opts = {
        'format': 'best[height<=720]',  # 720p 이하 최고 화질
        'outtmpl': f'{output_path}/{filename}.%(ext)s',  # 출력 템플릿
        'quiet': False,  # 진행 상황 표시
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"다운로드 중: {url}")
            ydl.download([url])
            print(f"✓ 다운로드 완료: {output_path}/{filename}.mp4")
    except Exception as e:
        print(f"✗ 다운로드 실패: {e}")

if __name__ == "__main__":
    # 사용 예시
    test_url = "https://youtu.be/-jtV7IJP8NU"
    download_tennis_video(test_url, filename='tennis_sample_2')