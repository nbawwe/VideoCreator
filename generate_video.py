import os
import glob
import re
import tempfile
from openai import OpenAI
from moviepy.editor import (
    AudioFileClip,
    ImageClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips
)
from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})
def text_to_audio_file(text, lang='zh', slow=False):
    """根据字幕内容生成对应的音频，并保存到临时文件中。"""
    client = OpenAI(api_key="sk-JQebDv7MoGLmlepCC7B8EcB1806d4094Bb00C57d0354AdBb", base_url="https://api.ai365vip.com/v1")
    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
    )

    with open(temp_audio_file.name, "wb") as audio_file:
        audio_file.write(response.content)

    return temp_audio_file.name

def parse_script_from_file(file_path):
    """从文案文件解析标题和段落列表。"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    title = ""
    paragraphs = []
    current_paragraph = ""

    for line in lines:
        line = line.strip()
        if line.startswith("标题："):
            title = line.split("：", 1)[-1].strip()
        elif line:
            current_paragraph += line + " "
        else:
            if current_paragraph.strip():
                paragraphs.append(current_paragraph.strip())
                current_paragraph = ""
    if current_paragraph.strip():
        paragraphs.append(current_paragraph.strip())

    print("读取到的文案内容：")
    print(paragraphs)

    return title, paragraphs

def distribute_subtitles_to_images(paragraph, image_count):
    """将段落内容平均分配到指定数量的字幕片段中。"""
    punctuation = r"([，。！？；])"
    segments = re.split(punctuation, paragraph)
    segments = ["".join(pair) for pair in zip(segments[::2], segments[1::2]) if pair]
    
    avg_length = max(1, len(segments) / image_count)
    subtitles = []
    current_subtitle = []
    for segment in segments:
        current_subtitle.append(segment)
        if len(current_subtitle) >= avg_length:
            subtitles.append("".join(current_subtitle))
            current_subtitle = []
    if current_subtitle:
        subtitles.append("".join(current_subtitle))
    
    # 保证字幕与图片数量一致
    while len(subtitles) < image_count:
        subtitles.append("")
    return subtitles[:image_count]


def create_video_for_paragraphs(image_root_dir, paragraphs, output_video_path, video_size=(1920, 1080)):
    """生成带有字幕和音频的完整视频，字幕在每张图片内切换。"""
    video_clips = []
    temp_audio_files = []

    subdirectories = [
        os.path.join(image_root_dir, subdir)
        for subdir in os.listdir(image_root_dir)
        if os.path.isdir(os.path.join(image_root_dir, subdir))
    ]
    subdirectories.sort()

    for i, paragraph in enumerate(paragraphs):
        image_dir = subdirectories[i]
        image_files = sorted(glob.glob(os.path.join(image_dir, "*.png")))
        if not image_files:
            raise FileNotFoundError(f"子目录 '{image_dir}' 中未找到图片")

        print(f"段落：{paragraph}")
        subtitles = distribute_subtitles_to_images(paragraph, len(image_files))
        print(f"分成：{subtitles}")

        part_clips = []
        for img_file, subtitle in zip(image_files, subtitles):
            if subtitle.strip():
                # 生成对应的音频文件
                audio_path = text_to_audio_file(subtitle)
                temp_audio_files.append(audio_path)
                audio_clip = AudioFileClip(audio_path)

                # 输出音频的时长
                print(f"段落音频长度: {audio_clip.duration}秒")
                print(f"字幕长度: {len(subtitle)}个字符")

                # 设置图片的时长为音频的时长
                img_clip = ImageClip(img_file).resize(video_size).set_duration(audio_clip.duration)

                # 创建字幕
                subtitle_clip = TextClip(
                    subtitle,
                    fontsize=48,
                    font='华文楷体',
                    color='white',
                    bg_color='black',
                    size=(video_size[0], None),
                    method='caption'
                ).set_position(('center', 'bottom')).set_duration(audio_clip.duration)

                # 合成视频片段
                part_clip = CompositeVideoClip([img_clip, subtitle_clip]).set_audio(audio_clip)
                part_clips.append(part_clip)
            else:
                # 如果字幕为空，仅显示图片
                img_clip = ImageClip(img_file).resize(video_size).set_duration(3)  # 默认3秒
                part_clips.append(img_clip)

        paragraph_clip = concatenate_videoclips(part_clips)
        video_clips.append(paragraph_clip)

    final_video = concatenate_videoclips(video_clips)
    final_video.write_videofile(
        output_video_path,
        fps=15,  # 降低帧率
        codec="libx264",
        audio_codec="aac",
        bitrate="800k",  # 设置视频码率
        audio_bitrate="128k"  # 设置音频码率
    )

    # 清理临时音频文件
    for audio_file in temp_audio_files:
        if os.path.exists(audio_file):
            os.remove(audio_file)


def generate_video(folder_path):
    script_file_path = folder_path + "/article/article.txt"  # 文案文件路径
    image_root_dir = folder_path + "/images"  # 图片存放目录（包含子目录）
    output_video_path = folder_path + "/output_video3.mp4"  # 输出视频路径

    title, paragraphs = parse_script_from_file(script_file_path)
    create_video_for_paragraphs(image_root_dir, paragraphs, output_video_path)
    return output_video_path