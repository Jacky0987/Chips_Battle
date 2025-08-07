# 安装指南 - Chips Battle Remake v3.0 Alpha

本指南将帮助您在 Windows 系统上安装和配置 Chips Battle Remake。

## 🔧 系统要求

- **操作系统**: Windows 10/11 (64位)
- **Python**: 3.8 或更高版本
- **内存**: 至少 2GB RAM
- **存储**: 至少 100MB 可用空间

## 📥 安装 Python

### 方法一：从官网下载（推荐）

1. **访问 Python 官网**
   - 打开浏览器，访问 [https://python.org](https://python.org)
   - 点击 "Downloads" 菜单

2. **下载 Python**
   - 点击 "Download Python 3.x.x" 按钮
   - 下载适用于 Windows 的安装程序

3. **安装 Python**
   - 运行下载的安装程序
   - ⚠️ **重要**: 勾选 "Add Python to PATH" 选项
   - 选择 "Install Now" 或 "Customize installation"
   - 等待安装完成

4. **验证安装**
   ```powershell
   python --version
   ```
   应该显示类似 "Python 3.x.x" 的版本信息

### 方法二：使用 Microsoft Store

1. 打开 Microsoft Store
2. 搜索 "Python"
3. 选择官方的 Python 应用
4. 点击 "安装"

### 方法三：使用包管理器

如果您已安装 Chocolatey 或 Scoop：

```powershell
# 使用 Chocolatey
choco install python

# 使用 Scoop
scoop install python
```

## 🚀 安装项目

### 1. 验证 Python 安装

打开 PowerShell 或命令提示符，运行：

```powershell
python --version
pip --version
```

如果显示版本信息，说明安装成功。

### 2. 导航到项目目录

```powershell
cd "C:\Users\Administrator\Desktop\chips\Chips_Battle"
```

### 3. 安装项目依赖

```powershell
pip install -r requirements.txt
```

这将安装以下依赖包：
- SQLAlchemy (数据库ORM)
- Rich (终端UI)
- Pydantic (数据验证)
- Click (命令行工具)
- 其他必要依赖

### 4. 初始化数据库

```powershell
python migrations/init_db.py
```

成功后会显示：
- ✅ 数据库表已创建
- ✅ 默认权限已创建
- ✅ 默认角色已创建
- ✅ 管理员用户已创建

### 5. 启动游戏

```powershell
python main.py
```

## 🔐 首次登录

数据库初始化后会自动创建管理员账户：

- **用户名**: `admin`
- **密码**: `admin123`

⚠️ **安全提醒**: 请在首次登录后立即更改密码！

## 🛠️ 故障排除

### Python 未找到

**错误信息**: "Python was not found"

**解决方案**:
1. 确保 Python 已正确安装
2. 检查 PATH 环境变量是否包含 Python 路径
3. 重启命令行窗口
4. 尝试使用完整路径运行 Python

### 权限错误

**错误信息**: "Permission denied" 或 "Access denied"

**解决方案**:
1. 以管理员身份运行命令行
2. 检查文件夹权限
3. 确保防病毒软件未阻止执行

### 依赖安装失败

**错误信息**: pip 安装包失败

**解决方案**:
```powershell
# 升级 pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 或者使用阿里云镜像
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 数据库初始化失败

**可能原因**:
- 文件权限问题
- 磁盘空间不足
- 依赖包未正确安装

**解决方案**:
1. 检查项目目录权限
2. 确保有足够的磁盘空间
3. 重新安装依赖包
4. 尝试重置数据库：
   ```powershell
   python migrations/init_db.py --reset
   ```

## 🔧 开发环境设置

### 虚拟环境（推荐）

为了避免依赖冲突，建议使用虚拟环境：

```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 退出虚拟环境（完成后）
deactivate
```

### IDE 配置

推荐使用以下 IDE：
- **Visual Studio Code** (免费，推荐)
- **PyCharm** (专业版/社区版)
- **Sublime Text**

### 代码格式化

安装代码格式化工具：

```powershell
pip install black flake8 isort
```

## 📝 配置文件

### 环境变量

创建 `.env` 文件来自定义配置：

```env
# 数据库配置
DB_NAME=my_game.db
DB_ECHO=false

# 游戏配置
GAME_INITIAL_MONEY=10000
GAME_MAX_LEVEL=100

# 安全配置
SECURITY_PASSWORD_MIN_LENGTH=8
SECURITY_SESSION_TIMEOUT=3600

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### 数据库配置

默认使用 SQLite，如需使用其他数据库：

```env
# PostgreSQL
DB_DRIVER=postgresql+asyncpg
DB_HOST=localhost
DB_PORT=5432
DB_USER=username
DB_PASSWORD=password
DB_NAME=chips_battle

# MySQL
DB_DRIVER=mysql+aiomysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=username
DB_PASSWORD=password
DB_NAME=chips_battle
```

## 🧪 运行测试

```powershell
# 安装测试依赖
pip install pytest pytest-asyncio pytest-cov

# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_auth.py

# 生成覆盖率报告
pytest --cov=. --cov-report=html
```

## 📞 获取帮助

如果遇到问题，可以：

1. 查看 [README.md](README.md) 文档
2. 检查 [FAQ](docs/FAQ.md)（如果存在）
3. 在项目仓库创建 Issue
4. 联系开发团队

## 🎉 安装完成

恭喜！您已成功安装 Chips Battle Remake。现在可以：

1. 运行 `python main.py` 启动游戏
2. 使用 `admin` / `admin123` 登录
3. 输入 `help` 查看可用命令
4. 开始您的游戏之旅！

---

**Chips Battle Remake v3.0 Alpha** - 重新定义命令行游戏体验 🎮