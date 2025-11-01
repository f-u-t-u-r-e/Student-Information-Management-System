# 学生信息管理系统（GUI 版）

这是一个基于 PySide6 的桌面应用，用于管理学生信息与成绩：

- 学生增删改查
- 课程/成绩维护、导入
- 成绩排名
- CSV / Excel(.xlsx) 导出

## 本地运行（开发模式）

1) 安装依赖：

```bash
python3 -m pip install --user openpyxl
```

2) 启动 GUI：

```bash
python3 desktop_app/gui_main.py
```

3) 可选：编译并运行 C++ 控制台程序（Linux）

```bash
g++ -g main.cpp -o main
./main
```

## 目录说明

- `data/`：示例数据目录（`students.json` 会被 .gitignore 忽略，仅保留 `sample_students.json`）
- `data/sample_students.json`：示例数据，便于演示（可提交到仓库）
- `.gitignore`：忽略导出文件、虚拟环境、日志、编译产物等
- `desktop_app/`：GUI 代码（PySide6）

## 打包为 Windows EXE（PyInstaller）

目标：将 `server.py` 打包成单文件 EXE，双击即可启动服务并自动打开浏览器。

注意：
- 建议在 Windows 环境中打包（PyInstaller 不支持跨平台直接产出 Windows 可执行文件）。
- `openpyxl` 用于 Excel 导出，脚本会自动安装。

步骤（Windows PowerShell）：

```bash
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
./build_gui.ps1 -AppName 学生信息管理系统GUI -Mode onefile

# 生成的可执行文件位于 dist\学生信息管理系统GUI.exe
```

常见问题：
- 脚本执行策略：如遇限制，可先运行 `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

## 一键打包脚本

- GUI EXE（Windows）：运行 `./build_gui.ps1`（可选参数 `-AppName`、`-Mode onefile|onedir`、`-NoConsole`）
	- 支持根目录 `icon.png` 自动转换为 `app.ico`

PowerShell 执行策略受限时，可临时放行当前脚本：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

提示：PyInstaller 只负责打包运行时；图标转换依赖 Pillow（脚本会按需安装）。

## 许可证

本仓库已包含 MIT LICENSE，可自由使用、修改与再分发；请保留版权与许可声明。
