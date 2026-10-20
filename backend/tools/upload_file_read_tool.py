"""
    创建主智能体的工具
    1. **generate_markdown** —— 生成标准 Markdown 文档
    2. **convert_md_to_pdf** —— 将 Markdown 转为 PDF 文件
    3. **read_file_content ——** 读取上传文件，并解析内容
"""
from pathlib import Path
from typing import Annotated, Optional

import docx
import pandas as pd
import pypdf
from langchain_core.tools import tool

from api.context import get_session_context
from api.monitor import monitor
from utils.converter_utils import convert_md_to_pdf_via_word
from utils.path_utils import resolve_path


# 读取上传的文件
def read_file_content(
        filename: Annotated[str, "要读取的文件名或路径（支持 .md, .docx, .pdf, .xlsx, .xls）"],
        instruction: Annotated[str, "对提取内容的具体指令（例如：'提取摘要', '统计数据'）"] = "提取全部内容"
) -> str:
    """
    读取指定文件的内容。支持 Markdown(.md)、Word(.docx)、PDF(.pdf) 和 Excel(.xlsx/.xls)。
    对于 Excel 文件，会自动提供数据统计信息（head 和 describe）。
    """
    # 向前端推送工具使用情况
    monitor.report_tool(
        tool_name="读取上传文件工具",
        args={
            "filename": filename,
            "instruction": instruction
        }
    )

    # 获取工作目录路径
    session_dir = get_session_context()
    # 获取上传的文件的具体路径
    file_path = Path(resolve_path(filename, session_dir))  # 转为Path对象
    try:
        # 获取文件的后缀
        ext = file_path.suffix.lower()
        if ext in [".md", ".txt"]: # 读取文本文件的内容（md和txt）
            return file_path.read_text(encoding="utf-8")
        elif ext == ".docx": # 读取word文档的内容
            doc = docx.Document(str(file_path))  # 转字符串传给docx
            full_text = [para.text for para in doc.paragraphs]
            return '\n'.join(full_text)
        elif ext == ".pdf":
            reader = pypdf.PdfReader(str(file_path))
            full_text = [page.extract_text() for page in reader.pages]
            return '\n'.join(full_text)
        elif ext in [".xlsx", ".xls"]:
            try:
                content = pd.read_excel(str(file_path))
            except:
                return "excel文件读取失败"
            result = [
                f"文件: {filename}",
                f"行数: {len(content)}, 列数: {len(content.columns)}",
                f"列名: {', '.join(content.columns.astype(str))}",
                "\n[前5行数据预览]:",
                content.head().to_string(index=False),
                "\n[统计描述]:",
                content.describe().to_string()
            ]
            return "\n".join(result)
        else:
            # 尝试作为纯文本读取
            try:
                return file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                return f"错误：不支持的文件格式 '{ext}'，且无法作为文本读取。"
    except Exception as e:
        return f"文件读取失败，{e}"

# 生成md文件
@tool
def generate_markdown(
        content: Annotated[str, "要写入Markdown文档的文本内容"],
        filename: Annotated[str, "Markdown文档的文件名（不包含扩展名或包含.md）"],
        path: Annotated[str, "文件保存的绝对路径"] = ""
):
    """根据提供的文本内容，生成对应的Markdown(.md)文件"""
    # 推送工具使用情况
    monitor.report_tool("生成markdown文件工具")
    # 若文件没有后缀则补全后缀
    if not filename.endswith(".md"):
        filename += ".md"
    session_dir = get_session_context()
    # 处理md文件的路径
    if path and path != ".":
        full_input_path = str(Path(path) / filename)
    else:
        full_input_path = filename
    # 获取md文件在工作目录中的路径
    full_path_str = resolve_path(full_input_path, session_dir)
    # 若md文件所在的目录不存在，则创建
    full_path = Path(full_path_str)
    full_path_parent = full_path.parent
    if not full_path_parent.exists():
        full_path_parent.mkdir(parents=True, exist_ok=True)
    try:
        # 向full_path所对应的文件中写出内容
        full_path.write_text(content, encoding="utf-8")
        return "markdown文件生成成功"
    except Exception as e:
        return f"markdown文件生成失败,{e}"

@tool
def convert_md_to_pdf(
        md_filename: Annotated[str, "要转换的Markdown文档路径（包含.md后缀）"],
        pdf_filename: Annotated[Optional[str], "输出的PDF文件路径（可选，默认与源文件同名）"] = None
) -> str:
    """
    将Markdown文档转换为PDF（基于Word引擎）
    核心优化：路径与资源管理逻辑分离，只保留Tool层的基础调用
    """
    # 推送工具使用情况
    monitor.report_tool("Markdown转PDF工具")
    session_dir = get_session_context()
    # 处理md文件的路径
    md_path = Path(md_filename).with_suffix(".md")
    md_abs_path = Path(resolve_path(str(md_path), session_dir))
    # 判断md文件是否存在
    if not md_abs_path.exists():
        return "md文件不存在"
    # 处理pdf文件的路径
    if pdf_filename:
        pdf_path = Path(pdf_filename).with_suffix(".pdf")
        pdf_abs_path = Path(resolve_path(str(pdf_path), session_dir))
    else:
        pdf_abs_path = md_abs_path.with_suffix(".pdf")
    # 将md转换为pdf
    try:
        return convert_md_to_pdf_via_word(md_abs_path, pdf_abs_path)
    except Exception as e:
        return "md转pdf失败"


if __name__ == '__main__':
    get_session_context = lambda: "./test_session_123"

    # 创建测试文件
    Path("./test_session_123/sub_dir").mkdir(parents=True, exist_ok=True)
    with open("./test_session_123/sub_dir/测试文件3.md", "w", encoding="utf-8") as f:
        f.write("# 标题\n\n测试内容\n\n|A|B|\n|---|---|\n|1|2|")

    print(convert_md_to_pdf.invoke({"md_filename": "sub_dir/测试文件3.md"}))
