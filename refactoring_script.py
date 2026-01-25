#!/usr/bin/env python3
"""
AISocialEngine重构辅助脚本
自动分析方法并生成重构建议
"""
import re
import ast
from pathlib import Path
from typing import List, Dict, Tuple


class MethodInfo:
    """方法信息"""
    def __init__(self, name: str, line_start: int, line_end: int, code: str):
        self.name = name
        self.line_start = line_start
        self.line_end = line_end
        self.code = code
        self.line_count = line_end - line_start + 1
        self.suggested_adapter = None
        self.is_delegated = False

    def __repr__(self):
        return f"Method({self.name}, lines={self.line_count}, adapter={self.suggested_adapter})"


class RefactoringAnalyzer:
    """重构分析器"""

    # 适配器映射规则
    ADAPTER_RULES = {
        'display_adapter': [
            'write_', 'show_', 'get_on_going', 'get_task_process',
            '_send_to_frontend'
        ],
        'task_adapter': [
            'task', 'plan', 'decompose', 'restart_plan',
            'handle_agent_plan', 'handle_agent_update_task'
        ],
        'activity_adapter': [
            'activity', 'process_activity', 'parse_agent_instruction',
            'get_next_action', 'get_current_task_list'
        ],
        'movement_adapter': [
            'move', 'go_around', 'bearing', 'route'
        ],
        'people_adapter': [
            'people', 'communicate', 'talk', 'sell_to', 'buy_from'
        ],
        'tool_adapter': [
            'tool', 'call_tool', 'use_tools', 'pick_a_tool'
        ],
        'trading_adapter': [
            'trade', 'pay', 'good', 'bargain', 'order'
        ],
        'skill_adapter': [
            'skill', 'service', 'use_service'
        ],
        'place_adapter': [
            'place', 'pick_place'
        ],
        'xmpp_adapter': [
            'xmpp', 'message', 'sendMessage', 'receiveMessage'
        ],
        'resource_adapter': [
            'resource', 'money', 'energy', 'life', 'decline_', 'save_all_user_data'
        ],
        'protocol_adapter': [
            'protocol', 'check_', '_in_received', '_in_message'
        ],
        'utility_adapter': [
            'http_request', 'get_dict_by_id', 'get_people_by_distance'
        ]
    }

    def __init__(self, main_file_path: str):
        self.main_file_path = Path(main_file_path)
        self.methods: List[MethodInfo] = []

    def analyze(self):
        """分析主文件"""
        print(f"分析文件: {self.main_file_path}")

        with open(self.main_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 查找所有方法
        current_method = None
        method_start = None
        indent_level = None

        for i, line in enumerate(lines, 1):
            # 检测方法定义
            if re.match(r'^    def \w+\(', line):
                # 保存上一个方法
                if current_method and method_start:
                    method_code = ''.join(lines[method_start-1:i-1])
                    method_info = MethodInfo(
                        current_method,
                        method_start,
                        i - 1,
                        method_code
                    )
                    self._analyze_method(method_info)
                    self.methods.append(method_info)

                # 开始新方法
                match = re.match(r'^    def (\w+)\(', line)
                current_method = match.group(1)
                method_start = i
                indent_level = len(line) - len(line.lstrip())

        # 保存最后一个方法
        if current_method and method_start:
            method_code = ''.join(lines[method_start-1:])
            method_info = MethodInfo(
                current_method,
                method_start,
                len(lines),
                method_code
            )
            self._analyze_method(method_info)
            self.methods.append(method_info)

        print(f"找到 {len(self.methods)} 个方法")

    def _analyze_method(self, method: MethodInfo):
        """分析单个方法"""
        # 检查是否已经委托
        if 'delegated to' in method.code or 'return self.' in method.code[:200]:
            if '_adapter.' in method.code[:200]:
                method.is_delegated = True
                return

        # 根据规则推断适配器
        method_name_lower = method.name.lower()

        for adapter, keywords in self.ADAPTER_RULES.items():
            for keyword in keywords:
                if keyword.lower() in method_name_lower:
                    method.suggested_adapter = adapter
                    return

        # 默认为utility_adapter
        method.suggested_adapter = 'utility_adapter'

    def generate_report(self) -> str:
        """生成分析报告"""
        report = []
        report.append("=" * 80)
        report.append("AISocialEngine重构分析报告")
        report.append("=" * 80)
        report.append("")

        # 统计信息
        total_methods = len(self.methods)
        delegated_methods = sum(1 for m in self.methods if m.is_delegated)
        remaining_methods = total_methods - delegated_methods

        report.append(f"总方法数: {total_methods}")
        report.append(f"已委托方法: {delegated_methods} ({delegated_methods*100//total_methods}%)")
        report.append(f"待处理方法: {remaining_methods} ({remaining_methods*100//total_methods}%)")
        report.append("")

        # 按适配器分组
        adapter_groups = {}
        for method in self.methods:
            if method.is_delegated:
                continue
            adapter = method.suggested_adapter or 'unknown'
            if adapter not in adapter_groups:
                adapter_groups[adapter] = []
            adapter_groups[adapter].append(method)

        report.append("按适配器分组的待处理方法:")
        report.append("-" * 80)

        for adapter in sorted(adapter_groups.keys()):
            methods = adapter_groups[adapter]
            total_lines = sum(m.line_count for m in methods)
            report.append(f"\n{adapter}: {len(methods)}个方法, {total_lines}行代码")

            # 列出大型方法（>20行）
            large_methods = [m for m in methods if m.line_count > 20]
            if large_methods:
                report.append(f"  大型方法 (>20行):")
                for m in sorted(large_methods, key=lambda x: x.line_count, reverse=True):
                    report.append(f"    - {m.name}: {m.line_count}行 (line {m.line_start})")

        report.append("")
        report.append("=" * 80)

        return "\n".join(report)

    def generate_refactoring_plan(self) -> str:
        """生成重构计划"""
        plan = []
        plan.append("=" * 80)
        plan.append("重构执行计划")
        plan.append("=" * 80)
        plan.append("")

        # 按适配器分组
        adapter_groups = {}
        for method in self.methods:
            if method.is_delegated:
                continue
            adapter = method.suggested_adapter or 'unknown'
            if adapter not in adapter_groups:
                adapter_groups[adapter] = []
            adapter_groups[adapter].append(method)

        # 生成每个适配器的重构步骤
        for adapter in sorted(adapter_groups.keys()):
            methods = adapter_groups[adapter]
            plan.append(f"\n## {adapter}")
            plan.append(f"待处理方法: {len(methods)}个")
            plan.append("")

            # 优先处理大型方法
            large_methods = [m for m in methods if m.line_count > 20]
            small_methods = [m for m in methods if m.line_count <= 20]

            if large_methods:
                plan.append("### 优先级1: 大型方法 (>20行)")
                for m in sorted(large_methods, key=lambda x: x.line_count, reverse=True):
                    plan.append(f"- [ ] {m.name} ({m.line_count}行, line {m.line_start})")
                plan.append("")

            if small_methods:
                plan.append("### 优先级2: 小型方法 (<=20行)")
                for m in sorted(small_methods, key=lambda x: x.name):
                    plan.append(f"- [ ] {m.name} ({m.line_count}行, line {m.line_start})")
                plan.append("")

        plan.append("=" * 80)

        return "\n".join(plan)


def main():
    """主函数"""
    main_file = "backend/modules/sns/ai_social_engine_adapter.py"

    print("AISocialEngine重构辅助脚本")
    print("=" * 80)
    print("")

    # 创建分析器
    analyzer = RefactoringAnalyzer(main_file)

    # 执行分析
    analyzer.analyze()

    # 生成报告
    report = analyzer.generate_report()
    print(report)

    # 保存报告
    with open("REFACTORING_ANALYSIS_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("\n报告已保存到: REFACTORING_ANALYSIS_REPORT.md")

    # 生成重构计划
    plan = analyzer.generate_refactoring_plan()
    with open("REFACTORING_EXECUTION_PLAN.md", "w", encoding="utf-8") as f:
        f.write(plan)
    print("重构计划已保存到: REFACTORING_EXECUTION_PLAN.md")

    print("\n" + "=" * 80)
    print("分析完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
