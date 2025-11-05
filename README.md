# 学生信息管理系统

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![PySide6](https://img.shields.io/badge/PySide6-6.0%2B-green)
![License](https://img.shields.io/badge/license-MIT-green)

## 项目简介

本项目是一个基于 PySide6（Qt for Python）的桌面学生信息管理系统，提供了完整的学生信息管理、成绩维护、数据导入导出和统计分析功能。

## 主要功能

- **学生信息管理**：支持学生信息的增加、删除、修改和查询
- **成绩管理**：课程成绩录入、批量导入（支持 CSV/Excel）、成绩编辑
- **绩点计算**：自动计算 GPA（支持标准 4.0 算法）
- **排名统计**：按 GPA 或总分排名，支持年级/专业分组
- **数据导出**：支持导出为 CSV 或 Excel（.xlsx）格式
- **导出历史**：记录每次导出操作的时间戳和元数据

## 技术栈

- **GUI 框架**：PySide6（Qt 6）
- **数据处理**：openpyxl（Excel 读写）
- **打包工具**：PyInstaller
- **图像处理**：Pillow（图标转换）
- **数据存储**：JSON（本地文件）

## 可执行程序下载

⚠️ **重要提示**：由于可执行文件较大（>50MB），未包含在仓库中。

请从以下方式获取打包好的程序：

1. **自行打包**：运行 `build_gui.ps1` 打包新程序
2. **GitHub Release**：从 [Releases](../../releases) 下载预构建的压缩包
3. **GitHub Actions**：查看最新的自动构建产物

下载后解压运行 `学生信息管理系统GUI.exe` 即可（无需安装 Python 环境）。

## 项目结构

```
学生信息管理系统/
├── desktop_app/           # 桌面应用源码
│   ├── gui_main.py        # GUI 主界面和窗口逻辑
│   └── core.py            # 核心业务逻辑（数据加载、保存、GPA 计算、导入导出等）
├── data/                  # 数据目录（运行时创建）
│   ├── students.json      # 学生数据文件（不提交到仓库）
│   └── sample_students.json  # 示例数据
├── exports/               # 导出文件目录（运行时创建）
│   └── exports.json       # 导出历史记录
├── build_gui.ps1          # Windows 打包脚本（PowerShell）
├── requirements.txt       # Python 依赖列表
├── README.md              # 本文档
├── LICENSE                # MIT 许可证
├── icon.png               # 应用图标（可选）
└── .gitignore             # Git 忽略规则
```

## 安装依赖

```bash
pip install -r requirements.txt
```

依赖项：
- PySide6
- openpyxl
- pyinstaller（仅打包时需要）
- pillow（仅图标转换时需要）

## 使用说明

### 1. 开发模式运行

```bash
python desktop_app/gui_main.py
```

### 2. 打包为 Windows EXE

**使用 PowerShell 脚本（推荐）：**

```powershell
# 如遇执行策略限制，先运行：
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 打包为单文件 EXE
.\build_gui.ps1
```

打包参数说明：
- `-AppName`：自定义应用名称（默认：学生信息管理系统GUI）
- `-Mode`：打包模式，`onefile`（单文件）或 `onedir`（目录）
- `-NoConsole`：隐藏控制台窗口（GUI 程序推荐）

生成的可执行文件位于 `dist/学生信息管理系统GUI.exe`

### 3. 数据管理

**数据文件位置：**
- 开发模式：项目根目录 `data/students.json`
- 打包模式：用户目录 `%UserProfile%\.student_info_mgmt\students.json`

**示例数据：**
- 首次运行可从 `data/sample_students.json` 导入示例数据

### 4. 成绩导入

支持 CSV 和 Excel 格式，要求包含以下列：
- 学号（必填）
- 课程名称
- 分数

导入时会自动匹配学号并更新成绩记录。

### 5. GPA 计算规则

采用标准 4.0 算法：
- 90-100: 4.0
- 85-89: 3.7
- 82-84: 3.3
- 78-81: 3.0
- 75-77: 2.7
- 72-74: 2.3
- 68-71: 2.0
- 64-67: 1.5
- 60-63: 1.0
- <60: 0.0

## GitHub Actions 自动构建

本项目配置了 GitHub Actions 工作流，在推送标签时自动构建并发布：

```bash
# 创建新版本标签并推送
git tag v1.0.0
git push origin v1.0.0
```

构建完成后会自动创建 Release，并上传打包好的 ZIP 文件。

也可以在 GitHub Actions 页面手动触发构建（workflow_dispatch）。

## 注意事项

1. **数据隐私**：
   - `data/students.json` 已在 `.gitignore` 中忽略，不会提交到仓库
   - 仅提交 `data/sample_students.json` 作为示例数据
   - 导出文件目录 `exports/` 也已忽略

2. **图标自定义**：
   - 将自定义图标保存为 `icon.png`（PNG 格式，建议 256x256）
   - 打包脚本会自动转换为 `app.ico`
   - 请确保图标有合法使用权限

3. **跨平台支持**：
   - PyInstaller 不支持跨平台打包
   - 需在 Windows 上打包 Windows 程序
   - Linux/macOS 需使用对应系统打包

4. **文件格式**：
   - 支持的导入格式：`.csv`, `.xlsx`
   - 支持的导出格式：`.csv`, `.xlsx`

## 开发环境

- Python 3.10+
- PySide6 6.0+
- Windows 10/11（打包环境）

## 贡献

欢迎提交 Issue 和 Pull Request！

在提交 PR 前，请确保：
- 代码符合项目风格
- 不包含真实学生数据
- 更新相关文档

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 [Issue](../../issues)
- 发起 [Discussion](../../discussions)

## 更新日志

### v1.0.2 (2025-11)
- 添加 GitHub Actions 自动构建
- 优化打包流程，仅上传 ZIP 压缩包
- 修复工作流 YAML 语法错误

### v1.0.0 (2025-11)
- 初始版本
- 实现学生信息管理基本功能
- 支持成绩导入导出
- GPA 计算和排名统计
- 完整的 GUI 界面

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

---

**免责声明**：本软件仅供学习和研究目的，不用于商业用途。使用本软件管理的数据安全由使用者自行负责。
