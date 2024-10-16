import urllib.request
from urllib.parse import urlparse
import re
import os
from datetime import datetime

# 定义
freetv_lines = []

#读取修改频道名称方法
def load_modify_name(filename):
    corrections = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(',')
            correct_name = parts[0]
            for name in parts[1:]:
                corrections[name] = correct_name
    return corrections

#读取修改字典文件
rename_dic = load_modify_name('assets/cr/freetv_rename.txt')

#纠错频道名称
def rename_channel(corrections, data):
    corrected_data = []
    for line in data:
        name, url = line.split(',', 1)
        if name in corrections and name != corrections[name]:
            name = corrections[name]
        corrected_data.append(f"{name},{url}")
    return corrected_data

#读取文本方法
def read_txt_to_array(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]
            return lines
    except FileNotFoundError:
        print(f"File '{file_name}' not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
# 组织过滤后的freetv
def process_channel_line(line):
    if  "#genre#" not in line and "," in line and "://" in line:
        channel_name, channel_address = line.split(',', 1)
        channel_address=channel_address+"$"+channel_name.strip().replace(' ', '_')
        line=channel_name+","+channel_address
        freetv_lines.append(line.strip())


def process_url(url):
    try:
        # 创建一个请求对象并添加自定义header
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')

        # 打开URL并读取内容
        with urllib.request.urlopen(req) as response:
            # 以二进制方式读取数据
            data = response.read()
            # 将二进制数据解码为字符串
            text = data.decode('utf-8')
            # channel_name=""
            # channel_address=""

            # 逐行处理内容
            lines = text.split('\n')
            print(f"行数: {len(lines)}")
            for line in lines:
                if  "#genre#" not in line and "," in line and "://" in line:
                    # 拆分成频道名和URL部分
                    channel_name, channel_address = line.split(',', 1)
                    
                    if channel_name in freetv_dictionary:
                        process_channel_line(line) 

    except Exception as e:
        print(f"处理URL时发生错误：{e}")



#读取文本
freetv_dictionary=read_txt_to_array('assets/cr/freetvlist.txt')  #all
freetv_dictionary_cctv=read_txt_to_array('assets/cr/freetvlist_cctv.txt')   #二次分发cctv，单独存
freetv_dictionary_18=read_txt_to_array('assets/cr/freetvlist_18.txt')   #二次分发18，单独存

freetv_cctv_lines = []
freetv_18_lines = []
freetv_other_lines = []


# 定义
urls=[
"https://freetv.fun/test_channels_original_new.txt",
"https://fanmingming.com/txt?url=http://adultiptv.net/chs.m3u"
]

# 处理
for url in urls:
    print(f"处理URL: {url}")
    process_url(url)
    # 准备支持m3u格式
def get_url_file_extension(url):
    # 解析URL
    parsed_url = urlparse(url)
    # 获取路径部分
    path = parsed_url.path
    # 提取文件扩展名
    extension = os.path.splitext(path)[1]
    return extension

def convert_m3u_to_txt(m3u_content):
    # 分行处理
    lines = m3u_content.split('\n')
    
    # 用于存储结果的列表
    txt_lines = []
    
    # 临时变量用于存储频道名称
    channel_name = ""
    
    for line in lines:
        # 过滤掉 #EXTM3U 开头的行
        if line.startswith("#EXTM3U"):
            continue
        # 处理 #EXTINF 开头的行
        if line.startswith("#EXTINF"):
            # 获取频道名称（假设频道名称在引号后）
            channel_name = line.split(',')[-1].strip()
        # 处理 URL 行
        elif line.startswith("http") or line.startswith("rtmp") or line.startswith("p3p") :
            txt_lines.append(f"{channel_name},{line.strip()}")
    
    # 将结果合并成一个字符串，以换行符分隔
    return '\n'.join(txt_lines)

# 在list是否已经存在url 2024-07-22 11:18
def check_url_existence(data_list, url):
    """
    Check if a given URL exists in a list of data.

    :param data_list: List of strings containing the data
    :param url: The URL to check for existence
    :return: True if the URL exists in the list, otherwise False
    """
    # Extract URLs from the data list
    urls = [item.split(',')[1] for item in data_list]
    return url not in urls #如果不存在则返回true，需要

# 处理带$的URL，把$之后的内容都去掉（包括$也去掉） 【2024-08-08 22:29:11】
def clean_url(url):
    last_dollar_index = url.rfind('$')  # 安全起见找最后一个$处理
    if last_dollar_index != -1:
        return url[:last_dollar_index]
    return url



# freetv_all
freetv_lines_renamed=rename_channel(rename_dic,freetv_lines)
version=datetime.now().strftime("%Y%m%d-%H-%M-%S")+",url"
output_lines =  ["更新时间,#genre#"] +[version] + ['\n'] +\
             ["freetv,#genre#"] + sorted(set(freetv_lines_renamed))

# 将合并后的文本写入文件：全集
output_file = "assets/cr/freetv_output.txt"
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in output_lines:
            f.write(line + '\n')
    print(f"已保存到文件: {output_file}")

except Exception as e:
    print(f"保存文件时发生错误：{e}")

# # # # # # # # # # # # # # # # # # # # # # # 分批再次保存
# $去掉
def clean_url(url):
    last_dollar_index = url.rfind('$')  # 安全起见找最后一个$处理
    if last_dollar_index != -1:
        return url[:last_dollar_index]
    return url

for line in freetv_lines_renamed:
    if  "#genre#" not in line and "," in line and "://" in line:
        channel_name=line.split(',')[0].strip()
        channel_address=clean_url(line.split(',')[1].strip())  #把URL中$之后的内容都去掉
        line=channel_name+","+channel_address #重新组织line

        if channel_name in freetv_dictionary_cctv: #央视频道
            freetv_cctv_lines.append(line.strip())
        elif channel_name in freetv_dictionary_18: #18频道
            freetv_18_lines.append(line.strip())
        else:
            freetv_other_lines.append(line.strip())

# freetv_cctv
output_lines_cctv =  ["更新时间,#genre#"] +[version] + ['\n'] +\
             ["freetv_cctv,#genre#"] + sorted(set(freetv_cctv_lines))
# freetv_ws
output_lines_18 =  ["更新时间,#genre#"] +[version] + ['\n'] +\
             ["freetv9+9_9527,#genre#"] + sorted(set(freetv_18_lines))
# freetv_other
output_lines_other =  ["更新时间,#genre#"] +[version] + ['\n'] +\
             ["freetv_other,#genre#"] + sorted(set(freetv_other_lines))

# 再次写入文件：分开
output_file_cctv = "assets/cr/freetv_output_cctv.txt"
output_file_18 = "assets/cr/freetv_output_18.txt"
output_file_other = "assets/cr/freetv_output_other.txt"
try:
    with open(output_file_cctv, 'w', encoding='utf-8') as f:
        for line in output_lines_cctv:
            f.write(line + '\n')
    print(f"已保存到文件: {output_file_cctv}")

    with open(output_file_18, 'w', encoding='utf-8') as f:
        for line in output_lines_18:
            f.write(line + '\n')
    print(f"已保存到文件: {output_file_18}")
    
    with open(output_file_other, 'w', encoding='utf-8') as f:
        for line in output_lines_other:
            f.write(line + '\n')
    print(f"已保存到文件: {output_file_other}")

except Exception as e:
    print(f"保存文件时发生错误：{e}")
