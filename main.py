import os
import subprocess
import sys
from faster_whisper import WhisperModel

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

def process_video_cli():
    print("=== CÔNG CỤ AI VIETSUB & TRANSLATE (CLI MODE) ===")
    
    # Nhập đường dẫn video từ bàn phím
    video_path = input("Nhập đường dẫn file video cần xử lý (ví dụ: video.mp4): ").strip().strip('"')
    
    if not os.path.exists(video_path):
        print(f"[LỖI] Không tìm thấy file video tại: {video_path}")
        return

    # Chọn model Whisper
    print("\nChọn Model Whisper:")
    print("1. tiny (nhanh nhất, độ chính xác thấp)")
    print("2. base (khuyên dùng cho thử nghiệm)")
    print("3. small")
    print("4. medium")
    print("5. large-v3 (chính xác cao nhất, nặng nhất)")
    choice_model = input("Chọn model (1-5, mặc định là 2 - base): ").strip()
    
    models_map = {"1": "tiny", "2": "base", "3": "small", "4": "medium", "5": "large-v3"}
    selected_model = models_map.get(choice_model, "base")

    # Chọn ngôn ngữ đích
    target_lang = input("Nhập mã ngôn ngữ muốn dịch sang (ví dụ: vi, en, ja, zh - mặc định 'vi'): ").strip()
    if not target_lang:
        target_lang = "vi"

    # Chọn có ép sub cứng không
    burn_sub = input("Bạn có muốn ép sub cứng (hardsub) vào video không? (y/n, mặc định y): ").strip().lower()
    do_burn = False if burn_sub == 'n' else True

    try:
        print(f"\n[1/4] Đang tải mô hình Whisper ({selected_model}) trên CPU...")
        model = WhisperModel(selected_model, device="cpu", compute_type="int8")
        
        print("[2/4] Đang phân tích âm thanh, nhận diện và dịch...")
        segments, info = model.transcribe(
            video_path, 
            beam_size=5, 
            task="translate" if target_lang != "en" else "transcribe", 
            language=None
        )
        
        print(f"-> Ngôn ngữ gốc phát hiện: {info.language} (Độ chính xác: {info.language_probability:.2f})")
        
        base_name, ext = os.path.splitext(video_path)
        srt_path = f"{base_name}_{target_lang}.srt"
        
        segment_list = list(segments)
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(segment_list, start=1):
                start_time = format_time(segment.start)
                end_time = format_time(segment.end)
                text = segment.text.strip()
                f.write(f"{i}\n{start_time} --> {end_time}\n{text}\n\n")
        
        print(f"[3/4] Đã xuất file phụ đề thành công: {srt_path}")
        
        if do_burn:
            output_video_path = f"{base_name}_hardsub{ext}"
            print("[4/4] Đang ép sub cứng vào video bằng FFmpeg...")
            
            # Xử lý đường dẫn SRT cho FFmpeg trên mọi hệ điều hành
            formatted_srt = os.path.abspath(srt_path).replace('\\', '/').replace(':', r'\:')
            cmd = [
                'ffmpeg', '-y', '-i', video_path,
                '-vf', f"subtitles='{formatted_srt}':force_style='FontName=Arial,FontSize=24,PrimaryColour=&H0000FFFF,Outline=&H00000000'",
                '-c:a', 'copy', output_video_path
            ]
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            for line in process.stdout:
                # In tiến trình FFmpeg gọn gàng hơn
                if "time=" in line:
                    sys.stdout.write(f"\rĐang xử lý video... {line.strip()}")
                    sys.stdout.flush()
            process.wait()
            
            if process.returncode == 0:
                print(f"\n[THÀNH CÔNG] Video hoàn chỉnh đã lưu tại: {output_video_path}")
            else:
                print("\n[CẢNH BÁO] Đã tạo file SRT nhưng lỗi khi chạy FFmpeg ép sub.")
        else:
            print("[HOÀN TẤT] Đã tạo xong file phụ đề.")
            
    except Exception as e:
        print(f"\n[LỖI XẢY RA]: {str(e)}")

if __name__ == "__main__":
    process_video_cli()