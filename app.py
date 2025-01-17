import gradio as gr
from PIL import Image
from process_text import *
from generate_video import *
# 示例函数：基于输入模式生成图片和描述
def generate_from_inspiration(text):

    folder_path = story_and_photos_generate(text)

    return folder_path


def generate_from_script(script):

    folder_path = story_and_photos_generate(script, mode="script")

    return folder_path


def generate_from_image_and_text(image, text):
    folder_path = story_and_photos_generate(text)
    return folder_path


# 模拟生成视频函数
def generate_video(folder_path):
    script_file_path = os.path.join(folder_path, "article", "article.txt")
    image_root_dir = os.path.join(folder_path, "images")
    output_video_path = os.path.join(folder_path, "output_video.mp4")
    title, paragraphs = parse_script_from_file(script_file_path)
    create_video_for_paragraphs(image_root_dir, paragraphs, output_video_path)
    return output_video_path


# Gradio 界面
def gradio_app():
    with gr.Blocks(theme=gr.themes.Base(
        primary_hue="slate",
        secondary_hue="slate",
        neutral_hue="slate",
        spacing_size="sm",
        radius_size="sm"
    )) as demo:  # 使用 Base 主题
        # 添加自定义 CSS
        gr.HTML("""
            <h1 style="text-align: center; font-size: 36px; font-weight: bold;">
                VideoCreator
            </h1>
        """)

        with gr.Row(variant="compact", elem_id="main-row"):
            # 左侧输入区域
            with gr.Column(scale=1, min_width=300, elem_id="input-column"):
                mode = gr.Radio(
                    ["输入灵感", "输入文稿", "输入图文"],
                    label="选择输入模式",
                    value="输入灵感"
                )

                text_input = gr.Textbox(
                    label="输入灵感/文稿", placeholder="请输入内容", elem_id="custom-textbox", lines=20, scale=2, container=True, show_label=True)
                image_input = gr.Image(label="上传图片", visible=False)
                generate_btn = gr.Button("生成视频")

            # 右侧输出区域
            with gr.Column(scale=1, min_width=300, elem_id="output-column"):
                video_output = gr.Video(
                    label="生成的视频", height=400, width=700, scale=2)

        # 输入模式切换逻辑
        def update_inputs(mode):
            if mode == "输入灵感":
                return gr.update(visible=True), gr.update(visible=False)
            elif mode == "输入文稿":
                return gr.update(visible=True), gr.update(visible=False)
            elif mode == "输入图文":
                return gr.update(visible=True), gr.update(visible=True)

        mode.change(update_inputs, inputs=[mode], outputs=[
                    text_input, image_input])

        # 生成视频逻辑
        def generate(mode, text, image):
            if mode == "输入灵感":
                folder_path = generate_from_inspiration(text)
            elif mode == "输入文稿":
                folder_path = generate_from_script(text)
            elif mode == "输入图文":
                folder_path = generate_from_image_and_text(image, text)

            # 调用视频生成函数
            return generate_video(folder_path)

        generate_btn.click(
            fn=generate,
            inputs=[mode, text_input, image_input],
            outputs=[video_output]
        )

    return demo


# 启动应用
app = gradio_app()
app.launch()
