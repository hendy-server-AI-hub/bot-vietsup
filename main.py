import os
import subprocess
import threading
import time
from tkinter import filedialog, messagebox
import customtkinter as ctk
from faster_whisper import WhisperModel

# Thiết lập giao diện chung
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TransparentOverlay(ctk.CTkToplevel):
    """Cửa sổ phụ đề trong suốt, không viền, nổi trên cùng"""
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry("700x90+300+750")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.85)
        self.configure(fg_color="#111111")
        
        self.x_offset = 0
        self.y_offset = 0
        
        self.sub_label = ctk.CTkLabel(
            self, 
            text="[Live Overlay]: Phụ đề trực tiếp sẽ hiển thị ở đây...\n(Giữ chuột trái kéo vị trí | Click chuột phải để tắt)", 
            font=("Arial", 14, "bold"),
            text_color="#00FFCC",
            justify="center"
        )
        self.sub_label.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Sự kiện kéo thả và tắt cửa sổ
        self.bind("<Button-1>", self.start_move)
        self.bind("<B1-Motion>", self.on_move)
        self.bind("<Button-3>", lambda e: self.destroy())
        self.sub_label.bind("<Button-3>", lambda e: self.destroy())

    def start_move(self, event):
        self.x_offset = event.x
        self.y_offset = event.y

    def on_move(self, event):
        x = self.winfo_pointerx() - self.x_offset
        y = self.winfo_pointery() - self.y_offset
        self.geometry(f"+{x}+{y}")

    def update_text(self, text):
        if self.winfo_exists():
            self.sub_label.configure(text=text)


class UltimateVietsubApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Phần Mềm Vietsub & Live Subtitle Thông Minh")
        self.geometry("620x650")
        
        self.video_path = ""
        self.overlay_window = None
        
        # Tiêu đề
        self.label_title = ctk.CTkLabel(self, text="AI AUTO SUB & LIVE OVERLAY", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_title.pack(pady=15)
        
        # --- PHẦN 1: XỬ LÝ FILE VIDEO (Tệp tĩnh / Telegram file) ---
        frame_file = ctk.CTkFrame(self)
        frame_file.pack(pady=5, padx=15, fill="x")
        
        ctk.CTkLabel(frame_file, text="1. Xử lý File Video (Telegram/Local):", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        
        self.btn_select = ctk.CTkButton(frame_file, text="Chọn File Video", command=self.select_video, width=180)
        self.btn_select.pack(padx=10, pady=5)
        
        self.label_path = ctk.CTkLabel(frame_file, text="Chưa chọn file nào", text_color="gray", wraplength=550)
        self.label_path.pack(padx=10, pady=3)
        
        # Cấu hình AI & Ngôn ngữ
        frame_config = ctk.CTkFrame(frame_file, fg_color="transparent")
        frame_config.pack(pady=5, fill="x")
        
        ctk.CTkLabel(frame_config, text="Model:").pack(side="left", padx=5)
        self.model_combo = ctk.CTkComboBox(frame_config, values=["tiny", "base", "small", "medium", "large-v3"], width=110)
        self.model_combo.set("base")
        self.model_combo.pack(side="left", padx=5)
        
        ctk.CTkLabel(frame_config, text="Dịch sang:").pack(side="left", padx=5)
        self.lang_combo = ctk.CTkComboBox(frame_config, values=["vi", "en", "ja", "zh", "ko", "fr"], width=80)
        self.lang_combo.set("vi")
        self.lang_combo.pack(side="left", padx=5)
        
        self.burn_var = ctk.BooleanVar(value=True)
        self.chk_burn = ctk.CTkCheckBox(frame_file, text="Ép sub cứng (Hardsub) vào video MP4", variable=self.burn_var)
        self.chk_burn.pack(anchor="w", padx=10, pady=8)
        
        self.btn_run_file = ctk.CTkButton(frame_file, text="Bắt Đầu Xử Lý File", command=self.start_file_thread, fg_color="green", hover_color="darkgreen", height=38)
        self.btn_run_file.pack(padx=10, pady=10, fill="x")

        # --- PHẦN 2: TÍNH NĂNG LIVE OVERLAY ---
        frame_live = ctk.CTkFrame(self)
        frame_live.pack(pady=10, padx=15, fill="x")
        
        ctk.CTkLabel(frame_live, text="2. Xem Live Subtitle Trực Tiếp (Màn hình / Overlay):", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        
        self.btn_toggle_overlay = ctk.CTkButton(frame_live, text="Bật Cửa Sổ Overlay Trong Suốt", command=self.toggle_overlay, fg_color="#1f538d", hover_color="#14375e", height=38)
        self.btn_toggle_overlay.pack(padx=10, pady=8, fill="x")

        # --- KHUNG LOG TRẠNG THÁI ---
        self.textbox_log = ctk.CTkTextbox(self, width=580, height=120)
        self.textbox_log.pack(pady=10, padx=15)
        self.textbox_log.insert("0.0", "Hệ thống đã sẵn sàng...\n")

    def log(self, message):
        self.textbox_log.insert("end", message + "\n")
        self.textbox_log.see("end")

    def select_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.mkv *.avi *.mov")])
        if file_path:
            self.video_path = file_path
            self.label_path.configure(text=os.path.basename(file_path), text_color="white")

    def toggle_overlay(self):
        if self.overlay_window is None or not self.overlay_window.winfo_exists():
            self.overlay_window = TransparentOverlay(self)
            self.log("Đã bật cửa sổ Overlay trong suốt.")
            
            # Khởi chạy luồng chạy thử nghiệm cập nhật text mẫu lên overlay
            threading.Thread(target=self.simulate_live_sub_stream, daemon=True).start()
        else:
            self.overlay_window.destroy()
            self.log("Đã tắt cửa sổ Overlay.")

    def simulate_live_sub_stream(self):
        """Mô phỏng luồng cập nhật phụ đề realtime lên overlay"""
        target_lang = self.lang_combo.get()
        count = 1
        while self.overlay_window and self.overlay_window.winfo_exists():
            text_sim = f"[Live AI - {target_lang.upper()}]: Đang nhận diện âm thanh thời gian thực (#{count})..."
            self.overlay_window.update_text(text_sim)
            count += 1
            time.sleep(3)

    def start_file_thread(self):
        if not self.video_path:
            messagebox.showerror("Lỗi", "Vui lòng chọn một file video trước!")
            return
        threading.Thread(target=self.process_video_pipeline, daemon=True).start()

    def process_video_pipeline(self):
        try:
            self.btn_run_file.configure(state="disabled")
            selected_model = self.model_combo.get()
            target_lang = self.lang_combo.get()
            
            self.log(f"--- BẮT ĐẦU XỬ LÝ FILE ---")
            self.log(f"Đang tải mô hình Whisper ({selected_model})...")
            
            model = WhisperModel(selected_model, device="cpu", compute_type="int8")
            
            self.log("Đang phân tích âm thanh, tự động phát hiện ngôn ngữ và dịch...")
            segments, info = model.transcribe(
                self.video_path, 
                beam_size=5, 
                task="translate" if target_lang != "en" else "transcribe", 
                language=None
            )
            
            self.log(f"Ngôn ngữ gốc phát hiện: {info.language} (Độ chính xác: {info.language_probability:.2f})")
            
            base_name, ext = os.path.splitext(self.video_path)
            srt_path = f"{base_name}_{target_lang}.srt"
            
            segment_list = list(segments)
            with open(srt_path, "w", encoding="utf-8") as f:
                for i, segment in enumerate(segment_list, start=1):
                    start_time = self.format_time(segment.start)
                    end_time = self.format_time(segment.end)
                    text = segment.text.strip()
                    f.write(f"{i}\n{start_time} --> {end_time}\n{text}\n\n")
            
            self.log(f"Đã xuất file phụ đề: {os.path.basename(srt_path)}")
            
            if self.burn_var.get():
                output_video_path = f"{base_name}_hardsub{ext}"
                self.log("Đang ép sub cứng vào video bằng FFmpeg...")
                
                formatted_srt = srt_path.replace('\\', '/').replace(':', r'\:')
                cmd = [
                    'ffmpeg', '-y', '-i', self.video_path,
                    '-vf', f"subtitles='{formatted_srt}':force_style='FontName=Arial,FontSize=24,PrimaryColour=&H0000FFFF,Outline=&H00000000'",
                    '-c:a', 'copy', output_video_path
                ]
                
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
                process.wait()
                
                if process.returncode == 0:
                    self.log(f"Thành công! Video lưu tại: {output_video_path}")
                    messagebox.showinfo("Thành công", f"Đã tạo video hoàn chỉnh:\n{output_video_path}")
                else:
                    self.log("Lỗi khi chạy FFmpeg ép sub.")
                    messagebox.showwarning("Cảnh báo", "Đã tạo file SRT nhưng lỗi khi ép sub cứng.")
            else:
                messagebox.showinfo("Hoàn tất", f"Đã tạo xong file phụ đề:\n{srt_path}")
                
        except Exception as e:
            self.log(f"Lỗi: {str(e)}")
            messagebox.showerror("Lỗi", str(e))
        finally:
            self.btn_run_file.configure(state="normal")

    def format_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

if __name__ == "__main__":
    app = UltimateVietsubApp()
    app.mainloop()
