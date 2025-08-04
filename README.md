git remote add origin https://github.com/zhang406493160gmail/m3u8-.git
git branch -M main
git push -u origin main

## 1. 功能亮点
- ✅ 支持 **AES-128-CBC** & **SM4-CBC** 加密分片自动解密  
- ✅ **多线程**并发下载（默认 10 线程，可调 50+）  
- ✅ **断点续传**：异常中断后自动跳过已下载分片  
- ✅ **一键合并**：调用 FFmpeg 合并为 MP4，自动清理 ts 碎片  
- ✅ **CLI 参数化**：URL、线程数、输出路径、是否保留 ts 均可配置  
- ✅ **零依赖除 FFmpeg**（其余纯 Python）

# 运行示例（默认 10 线程）
python m3u8.py -u "https://example.com/index.m3u8" -o movie.mp4

| 参数              | 说明                   | 默认值          |
| --------------- | -------------------- | ------------ |
| `-u, --url`     | M3U8 播放地址            | 必填           |
| `-o, --output`  | 输出 MP4 文件名           | `merged.mp4` |
| `-t, --threads` | 并发线程数                | 10           |
| `--keep-ts`     | 下载完成后保留 ts 分片        | False        |
| `--sm4`         | 强制使用 SM4 解密（自动识别时可省） | False        |


# 下载 AES-128 加密流，20 线程
python m3u8.py -u "https://site.com/hls/playlist.m3u8" -t 20 -o anime.mp4

5. 技术实现
M3U8 解析：正则提取 #EXT-X-KEY 与所有 .ts 链接
并发下载：concurrent.futures.ThreadPoolExecutor
AES/SM4 解密：pycryptodome CBC 模式，PKCS7 自动填充
FFmpeg 合并：subprocess.run(["ffmpeg", "-f concat ..."])
断点续传：本地检查 output/*.ts 文件大小与 Content-Length
