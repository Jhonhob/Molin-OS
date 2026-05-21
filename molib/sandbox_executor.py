"""
隔离沙箱技能执行器 — 解决 339 个技能的依赖地狱
===================================================
为高危/重型技能动态创建独立虚拟环境，杜绝三方库版本冲突。
通过子进程 + 标准 IO JSON 通信，隔离内存和环境污染。

用法：
    from molib.sandbox_executor import SandboxSkillExecutor
    sandbox = SandboxSkillExecutor()
    result = sandbox.run_isolated_skill(
        "video_renderer", script, {"topic": "AI"}, ["moviepy==1.0.3"]
    )
"""

import sys
import subprocess
import json
import os
from pathlib import Path
from typing import Optional


class SandboxSkillExecutor:
    """独立进程沙箱 — 每个重型技能拥有自己的 venv"""

    DEFAULT_SANDBOX_DIR = Path(__file__).parent.parent / "skills" / "sandboxes"

    def __init__(self, sandbox_base_dir: Optional[str] = None):
        self.base_dir = Path(sandbox_base_dir or self.DEFAULT_SANDBOX_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _ensure_sandbox_env(self, skill_id: str, requirements: Optional[list] = None) -> str:
        """为高危/重型技能动态创建隔离的虚拟环境"""
        env_path = self.base_dir / skill_id
        python_name = "python3" if sys.platform != "win32" else "python.exe"
        bin_dir = "bin" if sys.platform != "win32" else "Scripts"
        venv_python = env_path / bin_dir / python_name

        if not env_path.exists():
            print(f"🛠️ 正在为技能 [{skill_id}] 构建独立沙箱...")
            subprocess.run(
                [sys.executable, "-m", "venv", str(env_path)],
                check=True, capture_output=True,
            )

            # 升级 pip
            subprocess.run(
                [str(venv_python), "-m", "pip", "install", "--upgrade", "pip", "-q"],
                check=True, capture_output=True,
            )

            # 安装技能专属依赖
            if requirements:
                print(f"   📦 安装依赖: {requirements}")
                subprocess.run(
                    [str(venv_python), "-m", "pip", "install", "-q"] + list(requirements),
                    check=True, capture_output=True,
                )
        return str(venv_python)

    def run_isolated_skill(
        self,
        skill_id: str,
        script_body: str,
        args_dict: dict,
        requirements: Optional[list] = None,
        timeout_seconds: int = 120,
    ) -> dict:
        """
        在独立沙箱中安全执行技能代码。

        Args:
            skill_id: 技能唯一标识（用作沙箱目录名）
            script_body: 技能核心逻辑（Python 代码字符串，需定义 execute_logic(args)）
            args_dict: 传入 execute_logic 的参数
            requirements: pip 依赖列表（如 ['playwright', 'beautifulsoup4']）
            timeout_seconds: 超时秒数

        Returns:
            {"status": "success", "result": ...} 或 {"status": "failed", "error": ...}
        """
        python_exec = self._ensure_sandbox_env(skill_id, requirements or [])

        # 生成隔离执行脚本
        env_dir = self.base_dir / skill_id
        temp_script = env_dir / f"run_{skill_id}.py"

        wrapped_code = f'''"""
Molin-OS 沙箱隔离执行脚本 — 自动生成，勿手动修改
"""
import json
import sys
import traceback


def execute_logic(args):
    """用户自定义技能逻辑 — 必须返回可 JSON 序列化的结果"""
{chr(10).join("    " + line if line.strip() else "" for line in script_body.split(chr(10)))}


if __name__ == "__main__":
    try:
        input_args = json.loads(sys.argv[1])
        res = execute_logic(input_args)
        print("___SUCCESS___" + json.dumps(res, ensure_ascii=False))
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        print("___ERROR___" + str(e), file=sys.stderr)
        sys.exit(1)
'''
        with open(temp_script, "w", encoding="utf-8") as f:
            f.write(wrapped_code)

        try:
            res = subprocess.run(
                [python_exec, str(temp_script), json.dumps(args_dict, ensure_ascii=False)],
                capture_output=True, text=True, timeout=timeout_seconds, encoding="utf-8",
            )

            if res.returncode != 0:
                return {"status": "failed", "error": res.stderr.strip()}

            output = res.stdout.strip()
            if "___SUCCESS___" in output:
                json_str = output.split("___SUCCESS___", 1)[-1]
                return {"status": "success", "result": json.loads(json_str)}

            return {"status": "failed", "error": f"Unknown stdout: {output[:500]}"}

        except subprocess.TimeoutExpired:
            return {"status": "failed", "error": f"Skill [{skill_id}] 沙箱执行超时 ({timeout_seconds}s)"}

        except Exception as e:
            return {"status": "failed", "error": f"Sandbox runtime error: {str(e)}"}

    def list_sandboxes(self) -> list[dict]:
        """列出所有已创建的沙箱环境"""
        if not self.base_dir.exists():
            return []

        sandboxes = []
        for env_dir in sorted(self.base_dir.iterdir()):
            if not env_dir.is_dir():
                continue
            python_name = "python3" if sys.platform != "win32" else "python.exe"
            bin_dir = "bin" if sys.platform != "win32" else "Scripts"
            venv_python = env_dir / bin_dir / python_name

            packages = []
            if venv_python.exists():
                try:
                    result = subprocess.run(
                        [str(venv_python), "-m", "pip", "list", "--format=json"],
                        capture_output=True, text=True, timeout=10,
                    )
                    if result.returncode == 0:
                        packages = [
                            f"{p['name']}=={p['version']}"
                            for p in json.loads(result.stdout)
                        ]
                except Exception:
                    pass

            sandboxes.append({
                "skill_id": env_dir.name,
                "has_python": venv_python.exists(),
                "package_count": len(packages),
                "packages": packages[:10],  # 前10个
            })

        return sandboxes
