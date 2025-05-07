# Prompt Manager

一个强大的提示（Prompts）管理和版本控制工具，帮助您有效地组织、追踪和重用AI提示词。

## 核心概念

### 项目结构

Prompt Manager 使用层级结构来组织提示：

```
项目(Project) > 提示(Prompt) > 版本(Version)
```

文件系统存储结构：
```
root/
  project/
    prompt/
      v0001/
        prompt.txt     # 提示内容
        outputs.json   # 模型输出
        meta.json      # 元数据
```

### 主要概念

- **项目(Project)**: 相关提示的集合，用于组织不同领域或任务的提示
- **提示(Prompt)**: 单个提示的容器，可以包含多个版本
- **版本(Version)**: 提示的特定变体，包含：
  - **提示内容(content)**: 发送给AI模型的实际文本，可以包含变量占位符（如`{name}`）用于动态替换
  - **模型输出(model_outputs)**: 不同AI模型对同一提示的响应结果，可以是简单的文本输出或包含元数据的复杂结构
  - **元数据(meta)**: 与提示版本相关的附加信息，如语言、标签、使用场景等，便于分类和筛选


从源码安装：

```bash
git clone https://github.com/yourusername/prompt_manager
cd prompt_manager
pip install -e .
```

## 快速开始

### 基本使用

```python
from prompt_manager import PromptManager

# 初始化管理器（指定存储路径）
pm = PromptManager("./save")

# 获取或创建提示
prompt = pm.get_prompt("/项目名/提示名")

# 添加新版本（自动生成版本号）
prompt.add_version(
    # content: 提示内容，可包含变量占位符如{name}用于后续替换
    content="你好 {name}！",
    
    # model_outputs: 不同模型的输出结果
    model_outputs={
        # 简单格式：直接提供模型输出文本
        "gpt-4o": "你好，爱丽丝 👋",
        # 复杂格式：包含输出文本和相关元数据
        "llama3": {"output": "你好，爱丽丝。", "meta": {"temp": 0.3}},
    },
    
    # meta: 版本元数据，用于存储与此版本相关的附加信息
    meta={"lang": "zh"},
)

# 保存更改
prompt.save()
```

### 使用自定义版本号

```python
prompt.add_version(
    content="Hello {name}!",
    model_outputs={"gpt-4o": "Hi Alice 👋"},
    meta={"lang": "en"},
    version="english-v1",  # 自定义版本号
)
prompt.save()
```

### 修改现有版本

```python
# 更新元数据
prompt.modify_version(
    "v0001",
    meta_update={"reviewed": True},
)

# 添加新的模型输出
prompt.add_model_output(
    "v0001",
    "claude-3",
    {"output": "你好，爱丽丝！很高兴见到你。", "meta": {"temperature": 0.7}}
)

prompt.save(overwrite_existing=True)
```

### 选择特定版本

```python
# 将特定版本设为当前版本（latest）
current_version = prompt.select_version("english-v1")
print(f"当前版本: {current_version.version}")
```

### 导入和导出

```python
# 导出提示（包含所有版本）
export_file = prompt.export("./my_prompt.json")

# 导入到新位置
new_prompt = pm.import_prompt(export_file, "/新项目/新提示名")
```

## 高级功能

### 遍历版本

```python
# 获取所有版本
for version in prompt.versions:
    print(f"版本: {version.version}")
    print(f"内容: {version.content}")
    print(f"模型输出数量: {len(version.model_outputs)}")
    print(f"元数据: {version.meta}")
```

### 删除版本

```python
prompt.delete_version("v0001")
prompt.save()
```

### 项目管理

```python
# 列出所有项目
projects = pm.list_projects()

# 获取项目
project = pm.get_project("项目名")

# 列出项目中的所有提示
prompts = project.list_prompts()
```

## 数据模型

### PromptVersion

提示版本包含：
- `version`: 版本标识符（如"v0001"或自定义名称如"english-v1"），用于唯一标识一个提示版本
- `content`: 提示内容文本，即发送给AI模型的实际文本，可包含变量占位符（如`{name}`）用于动态替换
- `model_outputs`: 不同模型对该提示的输出结果集合，可以存储多个AI模型的响应以便比较
- `meta`: 自定义元数据，用于存储与提示相关的附加信息（如语言、领域、使用场景、标签等）
- `created_at`: 创建时间，自动记录版本的创建时间戳

### ModelOutput

模型输出包含：
- `model_name`: 模型名称，标识生成此输出的AI模型（如"gpt-4o"、"llama3"等）
- `output`: 模型生成的输出文本，即AI模型对提示的实际响应内容
- `meta`: 与此输出相关的元数据，包含生成过程中使用的参数（如温度、top_p、最大长度等）和其他相关信息

## 使用场景

- **提示工程研发**: 跟踪提示的迭代和改进过程
- **多模型比较**: 比较不同AI模型对同一提示的响应
- **版本控制**: 保存提示的历史版本，便于回溯和对比
- **团队协作**: 导入/导出功能便于团队成员之间共享提示

## 系统要求

- Python 3.9 或更高版本
