const fs = require('fs');
const path = require('path');
const readline = require('readline');
const { execSync, spawn } = require('child_process');

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    const milliseconds = Math.floor((seconds - Math.floor(seconds)) * 1000);
    
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')},${String(milliseconds).padStart(3, '0')}`;
}

rl.question('Nhập đường dẫn file video cần xử lý: ', (videoPath) => {
    videoPath = videoPath.trim().replace(/^["']|["']$/g, '');
    
    if (!fs.existsSync(videoPath)) {
        console.log(`[LỖI] Không tìm thấy file video tại: ${videoPath}`);
        rl.close();
        return;
    }

    rl.question('Nhập mã ngôn ngữ muốn dịch sang (ví dụ: vi, en, ja - mặc định "vi"): ', (targetLang) => {
        targetLang = targetLang.trim() || 'vi';
        
        console.log('\n[1/3] Đang gọi tiến trình AI Whisper để nhận diện và dịch phụ đề...');
        const baseName = path.basename(videoPath, path.extname(videoPath));
        const dirName = path.dirname(videoPath);
        const srtPath = path.join(dirName, `${baseName}_${targetLang}.srt`);
        
        try {
            // Sử dụng câu lệnh python whisper CLI chuẩn làm cầu nối hiệu năng cao cho Node.js
            const whisperCmd = `whisper "${videoPath}" --model base --language ${targetLang} --task translate --output_format srt --output_dir "${dirName}"`;
            console.log(`Đang chạy lệnh: ${whisperCmd}`);
            execSync(whisperCmd, { stdio: 'inherit' });
            
            console.log(`[2/3] Đã trích xuất phụ đề thành công!`);
            
            rl.question('Bạn có muốn ép sub cứng (hardsub) vào video không? (y/n, mặc định y): ', (burnAns) => {
                const doBurn = burnAns.trim().toLowerCase() !== 'n';
                
                if (doBurn) {
                    const ext = path.extname(videoPath);
                    const outputVideoPath = path.join(dirName, `${baseName}_hardsub${ext}`);
                    // Tìm file srt được whisper sinh ra tự động
                    const generatedSrt = path.join(dirName, `${path.basename(videoPath, ext)}.srt`);
                    
                    if (fs.existsSync(generatedSrt)) {
                        // Đổi tên file srt cho đúng chuẩn ngôn ngữ đích nếu cần
                        if (generatedSrt !== srtPath) {
                            fs.renameSync(generatedSrt, srtPath);
                        }
                    }

                    console.log('[3/3] Đang ép sub cứng vào video bằng FFmpeg...');
                    const formattedSrt = srtPath.replace(/\\/g, '/').replace(':', '\\:');
                    
                    const ffmpegArgs = [
                        '-y', '-i', videoPath,
                        '-vf', `subtitles='${formattedSrt}':force_style='FontName=Arial,FontSize=24,PrimaryColour=&H0000FFFF,Outline=&H00000000'`,
                        '-c:a', 'copy',
                        outputVideoPath
                    ];

                    const ffmpegProcess = spawn('ffmpeg', ffmpegArgs);
                    
                    ffmpegProcess.stderr.on('data', (data) => {
                        process.stdout.write(`FFmpeg: ${data}`);
                    });

                    ffmpegProcess.on('close', (code) => {
                        if (code === 0) {
                            console.log(`\n[THÀNH CÔNG] Video hoàn chỉnh: ${outputVideoPath}`);
                        } else {
                            console.log(`\n[CẢNH BÁO] FFmpeg kết thúc với mã lỗi ${code}`);
                        }
                        rl.close();
                    });
                } else {
                    console.log('[HOÀN TẤT] Không ép sub cứng.');
                    rl.close();
                }
            });

        } catch (error) {
            console.error(`\n[LỖI XẢY RA]: ${error.message}`);
            rl.close();
        }
    });
}
