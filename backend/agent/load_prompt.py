"""
    读取yaml文件中的配置信息
"""
from pathlib import Path

import yaml


# 创建读取yaml文件的函数
def load_yaml(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        # 将yaml文件中配置信息读取为字典
        return yaml.safe_load(f)

# 获取prompts.yaml文件的绝对路径
_yaml_path = Path(__file__).parents[1] / "prompt" / "prompts.yaml"
# 调用load_yaml()，获取yaml文件转换的字典
_yaml_dict = load_yaml(_yaml_path)

# 获取main_agent所对应的配置信息
main_agent_config = _yaml_dict["main_agent"]
# 获取sub_agents所对应的配置信息
sub_agents_config = _yaml_dict["sub_agents"]

if __name__ == "__main__":
    print(main_agent_config)
    print(sub_agents_config)
