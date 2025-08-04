from Crypto.Cipher import AES
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import os
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
}
M3U8_URL = 'https://mp.yiyaoxx.top/mu/dfaf4a6f22005660d27a9ab3be__109925/hls/1/index.m3u8?wsSecret=329976b0ea6bf095f5b5046784e8179c&wsTime=1752349345'

'''
https://mp.yiyaoxx.top/mu/dcdeb2125030687009f788192__721775/hls/1/index0.ts?wsSecret=8d42943006a0796db1b418a139a0577e&wsTime=1752425029'''
# 创建保存目录
output_dir = "video_segments"
merged_file = os.path.join(output_dir, "merged_video.mp4")
# 创建输出目录
os.makedirs(output_dir, exist_ok=True)

m3u8_content = requests.get(M3U8_URL, headers=HEADERS).text
key_uri = re.findall('#EXT-X-KEY:METHOD=AES-128,URI="(.*?)",',m3u8_content)[0]
key_content= requests.get(key_uri,headers=HEADERS).content
cipher = AES.new(key_content, AES.MODE_CBC)
#获取所有片段的uri
segment_urls = re.findall(',\n(.*?)\n#', m3u8_content)[5:]
print("共找到 {} 个视频片段".format(len(segment_urls)))
def download_segment(index, segment, cipher, output_dir):
    try:
        
        print(f"Downloading segment {index}: {segment}")
        encrypted_data = requests.get(segment, headers=HEADERS).content
        decrypted_data = cipher.decrypt(encrypted_data)

        output_path = os.path.join(output_dir, f"{index:05d}.ts")
        with open(output_path, 'wb') as f: 
            f.write(decrypted_data)
        return output_path
    except Exception as e:
        print(f"Error downloading segment {index} from {segment}: {e}")
        return None
downloaded_files=[]

# 多线程下载
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(download_segment, idx, segment, cipher, output_dir)
               for idx, segment in enumerate(segment_urls)]

    for future in as_completed(futures):
        result = future.result()
        if result:
            downloaded_files.append(result)
downloaded_files.sort(key=lambda x: int(os.path.basename(x).split(".")[0]))
file_list_path = "file_list.txt"
with open(file_list_path, "w") as f:
    for file in downloaded_files:
        f.write(f"file '{file}'\n")
print(f"已生成 {file_list_path}")

subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", file_list_path, "-c", "copy", merged_file])
print(f"已合并所有片段到 {merged_file}")
# 删除目录output_dir里的ts文件
for filename in os.listdir(output_dir):
    if filename.endswith(".ts"):
        os.remove(os.path.join(output_dir, filename))