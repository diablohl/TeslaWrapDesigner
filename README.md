# TeslaWrapDesigner
一个基于AI生成的特斯拉自定义车身皮肤设计工具

## 官方模板仓库地址
https://github.com/teslamotors/custom-wraps

**一个基于 Python 和 PyQt5 开发的现代化车辆改色与拉花设计工具。
该工具允许用户在一个“三明治”层级结构中进行设计：顶层是自动处理的车身遮罩，底层是用户上传的贴图。通过智能算法，它能自动识别线稿并将车身外部遮盖，从而实现逼真的“贴膜”效果。**
<img width="2690" height="1682" alt="image" src="https://github.com/user-attachments/assets/2ae0e9cb-befc-4c60-9147-7de02dab265b" />

## 如何打包发布 (Build)
### 首先安装打包工具：
`pip install pyinstaller`
### Windows 打包命令
`python -m PyInstaller --noconsole --onefile --add-data "assets;assets" --name="CarWrapDesigner" car_wrap_tool.py`
### macOS 打包命令
`python3 -m PyInstaller --noconsole --onedir --windowed --add-data "assets:assets" --name="CarWrapDesigner" car_wrap_tool.py`

打包完成后，程序位于 dist/ 文件夹中。
