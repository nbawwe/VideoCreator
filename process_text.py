import json
import re
import os
import openai
from openai import OpenAI
import requests


def sanitize_filename(filename):
    """去除文件名中的无效字符，保留汉字"""
    allowed_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_ "
    # 正则表达式匹配汉字
    return ''.join(c if c in allowed_chars or re.match(r'[\u4e00-\u9fa5]', c) else '_' for c in filename)


def story_and_photos_generate(input_text, mode="inspiration"):
    if mode == "inspiration":
    # 文案生成请求模板
        system_instruction_for_article = '''以下用中文回答300字左右。\\
                    直接输出一篇自媒体视频文案，\\
                    不要说浅显的道理\\
                    在开头直接给出这篇文案的核心观点或者指引，吸引读者，而在后续慢慢展开，解释清楚观点或者指引的科学内涵和内容。\\
                    请介绍一些有意思的科普内容，可以是天文,地理,海洋,AI\\
                    介绍一些吸引人的内容例如'''+input_text+'''
                    一篇文章就介绍一个内容\\
                    标题应该提出一个有吸引力的能引起人兴趣的问句。\\
                    绝对不要用"你知道xxx吗"“xxx是什么意思”这样的形式。\\
                    写成方便朗读的文稿，不需要段落标题。\\ 
                    请把一个论点叙述完整，让人们可以彻底明白和理解\\
                    不用说空话废话以及浅显的道理，特别是结尾部分。要言之有物。\\
                    '''
    if mode == "script":
        system_instruction_for_article = input_text
    client = OpenAI(api_key="sk-JQebDv7MoGLmlepCC7B8EcB1806d4094Bb00C57d0354AdBb", base_url="https://api.ai365vip.com/v1")

    # 设置生成n个故事
    n = 1  # 可以修改生成故事的数量

    # 加载Stable Diffusion模型


    # 设定图片长宽比
    height = 720
    width = 1080


# 循环生成n个故事
    for story_num in range(1, n + 1):
        print(f"正在生成第 {story_num} 个故事...")

        # 生成文章
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": system_instruction_for_article}]
        )

        article = response.choices[0].message.content
        print(f"第 {story_num} 个故事的文案：\n{article}\n")

        # 提取文章的第一句话并清理无效字符作为文件夹名称
        first_sentence = re.split(r'[。？！]', article)[0]
        sanitized_first_sentence = sanitize_filename(first_sentence)
        story_folder = f"./generated_images_test_tiny_tips/{story_num}_{sanitized_first_sentence}"
    
        if not os.path.exists(story_folder):
            os.makedirs(story_folder)


        # 保存文章到txt文件中
        article_folder = os.path.join(story_folder, "article")
        if not os.path.exists(article_folder):
            os.makedirs(article_folder)

        article_path = os.path.join(article_folder, "article.txt")
        with open(article_path, 'w', encoding='utf-8') as f:
            f.write(article)
        print(f"文案已保存到: {article_path}")

        # 根据文案生成图片生成请求的 prompt
        system_instruction_for_image_prompt = f'''Using English to answer.\\
                                            The article is as follows: "{article}"\\
                                            The user will enter a we media video text, \\ 
                                            and you need to choose a few appropriate places \\ 
                                            to create the prompt for the text-to-image model to get the matching image. \\ 
                                            The style of the image depends on the text, but the style needs to be consistent across multiple images.\\ 
                                            Attention please, The first image is the cover of the video.\\
                                            Output the prompts directly, and the prompts of different images are separated by @\\
                                            like, 'prompt1@prompt2@prompt3@prompt4@prompt5'\\
                                            '''

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": system_instruction_for_image_prompt}]
        )

        # 将生成的prompt分割成多个部分
        prompts = response.choices[0].message.content
        print(f"Received prompts: {prompts}")  # Debug output for prompts
        split_prompts = prompts.split('@')

        # 图片生成部分
        image_folder = os.path.join(story_folder, "images")
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)

        # 根据生成的prompt生成图片
        for i, prompt in enumerate(split_prompts, 1):
            print(f"Processing prompt {i}: {prompt}")

            # 为每个prompt创建一个子文件夹，清理无效字符
            sanitized_prompt = sanitize_filename(prompt[:30])
            prompt_folder = os.path.join(image_folder, f"{i}_{sanitized_prompt.rstrip()}")
            if not os.path.exists(prompt_folder):
                os.makedirs(prompt_folder)

            url = "https://stablediffusionapi.com/api/v3/text2img"
            payload = json.dumps({
                "key": "tmn5XZHOqd57tQwDnAIq7kH9vWroAgp2zsK7XSN5DKYS1uOO0YefWBWl19Sy",  # 用你的 API 密钥替换
                "prompt": prompt,
                "negative_prompt": None,
                "width": str(width),
                "height": str(height),
                "samples": "4",  # 生成1张图片
                "num_inference_steps": "20",
                "safety_checker": "no",
                "enhance_prompt": "yes",
                "seed": None,
                "guidance_scale": 7.5,
                "multi_lingual": "no",
                "panorama": "no",
                "self_attention": "no",
                "upscale": "no",
                "embeddings_model": None,
                "webhook": None,
                "track_id": None
            })
            headers = {
                'Content-Type': 'application/json'
            }
            # 发送请求生成图片
            print(f"Sending request to generate image {i} with prompt: {prompt}")  # Debug output for API call
            response = requests.post(url, headers=headers, data=payload)
            response_data = response.json()
            print(response_data)
            image_urls = response_data.get('output', [])
            if image_urls:
                for j, image_url in enumerate(image_urls, 1):
                    print(f"Image URL received: {image_url}")  # Debug output for image URL
                    image_response = requests.get(image_url)
                    image_path = os.path.join(prompt_folder, f"image_{i}_{j}.png")
                    with open(image_path, 'wb') as img_file:
                        img_file.write(image_response.content)
                    print(f"图像 {i}_{j} 保存成功：{image_path}")
            else:
                print(f"未能获取图像 URL，无法保存图像 {i}")
    print(f"共生成 {n} 个故事！")
    return story_folder
