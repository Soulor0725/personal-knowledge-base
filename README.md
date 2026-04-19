# 个人知识库 (Personal Knowledge Base)

一个基于 Flask 和 JavaScript 的个人知识库系统，支持 Markdown 编辑、代码高亮、用户认证、分类管理等功能。

## ✨ 功能特性

- **Markdown 编辑器**：支持 Markdown 语法，包含预览功能
- **代码高亮**：支持多种编程语言的代码块高亮显示
- **图片上传**：支持在文章中插入图片
- **用户认证**：支持用户注册、登录和个人资料管理
- **分类管理**：支持文章分类，可创建和删除分类
- **文章管理**：支持创建、编辑、删除文章
- **收藏功能**：支持收藏文章
- **搜索功能**：支持文章标题和内容搜索
- **导航功能**：支持上一篇/下一篇文章导航
- **浏览统计**：记录文章浏览次数
- **响应式设计**：适配不同屏幕尺寸

## 🛠️ 技术栈

- **后端**：Python Flask
- **前端**：HTML5, CSS3, JavaScript
- **数据库**：SQLite
- **Markdown 解析**：Marked.js
- **代码高亮**：CodeMirror
- **图标**：Font Awesome

## 📦 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/Soulor0725/personal-knowledge-base.git
cd personal-knowledge-base
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 初始化数据库

运行应用时会自动创建数据库文件。

### 4. 启动服务

#### 方法 1：直接运行

```bash
python app.py
```

#### 方法 2：使用批处理脚本

```bash
# Windows
start.bat

# 或自动启动脚本
auto_start.bat
```

## 🌐 访问方式

- **本地访问**：http://localhost:5001
- **内网访问**：http://[你的IP地址]:5001

## 📝 使用指南

### 1. 用户注册/登录

- 首次访问时，点击右上角的"登录"按钮
- 点击"注册"标签页，填写用户名、密码和中文名字
- 注册成功后自动登录

### 2. 创建文章

- 点击"+ 新建"按钮
- 填写标题、选择分类、添加标签
- 在编辑器中编写 Markdown 内容
- 点击"保存"按钮保存文章
- 点击"保存草稿"按钮保存为草稿

### 3. 编辑文章

- 在文章列表中点击文章标题进入详情页
- 点击"编辑"按钮
- 修改内容后点击"保存"按钮

### 4. 管理分类

- 点击左侧分类区域的"+"按钮添加分类
- 右键点击分类名称删除分类

### 5. 搜索文章

- 在顶部搜索框输入关键词
- 点击搜索按钮或按回车键

### 6. 个人资料管理

- 点击右上角的"编辑资料"按钮
- 修改中文名字
- 上传头像
- 点击"保存"按钮

## 📁 项目结构

```
personal-knowledge-base/
├── app.py                 # 后端主文件
├── requirements.txt       # 依赖文件
├── static/                # 静态文件
│   ├── index.html         # 前端界面
│   └── uploads/           # 上传的图片
├── add_name_column.py     # 数据库迁移脚本
├── add_avatar_column.py   # 数据库迁移脚本
├── check_db.py            # 数据库检查脚本
├── view_db.py             # 数据库查看脚本
├── start.bat              # 启动脚本
└── auto_start.bat         # 自动启动脚本
```

## 🔧 配置说明

### 端口配置

默认端口为 5001，可在 `app.py` 文件中修改：

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
```

### 数据库配置

默认使用 SQLite 数据库，数据库文件为 `knowledge_base.db`。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📞 联系

- GitHub: [Soulor0725](https://github.com/Soulor0725)

---

**✨ 开始使用你的个人知识库吧！** ✨