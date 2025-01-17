# VideoCreator
 **人机交互大作业：一个简单的视频生成前端**

后端通过调用openai和diffuser的api对prompt进行处理，然后生成视频，显示在基于gradio的前端上。

如果想要测试完整功能，你需要先安装以下包：
```
    gradio == 4.44.1
    python == 3.9.21
    torch
    transformers == 4.48.0
    openai == 1.59.6
    moviepy == 1.0.3
    pillow < 10.0.0
  ```
以及为了支持moviepy， 你需要安装ImageMagick，[点击这里](https://imagemagick.org/script/download.php)
前端测试在Windows下进行，更具体环境可以参考requirements.txt文件。


测试该前端，你需要进行以下步骤：

1. 安装符合的conda环境
2. 下载ImageMagick，并在generate_video.py中第14行的路径设置替换为你本地的ImageMagick.exe路径
3. 替换api密钥：将generate_video.py和process_text.py两个文件中的api替换为你自己的
4. 运行app.py文件，进入网页
5. 输入你自己的灵感，并点击生成视频

如果你不想安装环境，只需要体验一下前端样式，你可以运行app_test.py展示我们预设的视频，操作与第4步相同

只需安装包：
```
    gradio == 4.44.1
    ``` 

（只不过就不能体验到不同的生成视频了）