from prompt_manager import PromptManager

pm = PromptManager("./save")

# 1. 直接通过路径获取 / 创建
p = pm.get_prompt("/demo/hello/j2")

# 2. 新增一个版本 (自动生成版本号)
p.add_version(
    content="Hello {name}!",
    model_outputs={
        "gpt-4o": "Hi Alice 👋",
        "llama3": {"output": "Hello, Alice.", "meta": {"temp": 0.3}},
    },
    meta={"lang": "en"},
)

# 2.1 新增一个自定义版本号的版本
p.add_version(
    content="你好 {name}！",
    model_outputs={
        "gpt-4o": "你好，爱丽丝 👋",
    },
    meta={"lang": "zh"},
    version="chinese-v1",  # 自定义版本号
)
p.save()                # 持久化

# 3. 修改已有版本
v1 = p.modify_version(
    "v0001",
    meta_update={"reviewed": True},
)
p.save(overwrite_existing=True)

# 3.1 向现有版本添加模型输出
p.add_model_output(
    "chinese-v1",
    "claude-3",
    {"output": "你好，爱丽丝！很高兴见到你。", "meta": {"temperature": 0.7}}
)
p.save(overwrite_existing=True)

# 3.2 选择特定版本作为当前版本
current_version = p.select_version("chinese-v1")
print(f"当前选择的版本: {current_version.version}, 语言: {current_version.meta.get('lang')}")

# 4. 导出
export_file = p.export("./hello_prompt.json")

# 5. 导入到另一项目 /prompt 名
p2 = pm.import_prompt(export_file, "/newproj/hello_copy")
print(p2.latest.content)  # 应该是 "你好 {name}！" 因为我们选择了 chinese-v1 作为当前版本

# 6. 获取所有版本并遍历
print("\n所有可用版本:")
for version in p.versions:
    print(f"- {version.version}: {version.content[:20]}... ({len(version.model_outputs)} 个模型输出)")