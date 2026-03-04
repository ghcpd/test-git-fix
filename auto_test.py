#!/usr/bin/env python3
"""
自动化测试脚本：检测网络依赖问题是否被正确修复
用法: python auto_test.py <case_before|case_after>
"""

import sys
import os
import json
import ast
import re
from pathlib import Path
from typing import List, Dict, Any


class NetworkDependencyChecker:
    """检查网络依赖漏洞的检测器"""
    
    def __init__(self, target_dir: str):
        self.target_dir = Path(target_dir)
        self.vulnerabilities = []
        self.vulnerability_id = 1
        
    def check_all(self) -> Dict[str, Any]:
        """执行所有检查"""
        print(f"🔍 开始检查目标目录: {self.target_dir}")
        
        # 检查1: API设计是否使用了网络依赖参数
        self.check_api_design()
        
        # 检查2: 是否缺少本地数据文件
        self.check_local_data_file()
        
        # 检查3: 测试代码是否使用网络依赖参数
        self.check_test_network_dependency()
        
        # 检查4: 检查默认行为
        self.check_default_behavior()
        
        return self.generate_report()
    
    def check_api_design(self):
        """检查API设计 - 是否仍使用旧的网络依赖参数"""
        print("  ├─ 检查API设计...")
        
        fake_py_paths = [
            self.target_dir / "fake_useragent" / "fake.py",
            self.target_dir / "src" / "fake_useragent" / "fake.py"
        ]
        
        for fake_py in fake_py_paths:
            if not fake_py.exists():
                continue
                
            with open(fake_py, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # 检查是否使用了旧的网络依赖参数
            if 'use_cache_server' in content or 'cache=' in content:
                # 找到包含这些参数的行
                problematic_lines = []
                for i, line in enumerate(lines, 1):
                    if 'use_cache_server' in line or ('cache=' in line and 'cache_path' not in line):
                        problematic_lines.append(i)
                
                if problematic_lines:
                    # 提取__init__方法
                    init_start = None
                    init_end = None
                    for i, line in enumerate(lines):
                        if 'def __init__' in line:
                            init_start = i
                        if init_start and i > init_start and line.strip() and not line.strip().startswith(('self.', 'assert', '#', 'pass')):
                            if line[0] not in (' ', '\t') or line.strip().startswith('def '):
                                init_end = i
                                break
                    
                    if init_end is None:
                        init_end = min(init_start + 20, len(lines)) if init_start else 20
                    
                    original_snippet = '\n'.join(lines[init_start:init_end]) if init_start else content[:500]
                    
                    self.add_vulnerability(
                        file=str(fake_py.relative_to(self.target_dir)),
                        line_numbers=problematic_lines,
                        original=original_snippet,
                        updated="def __init__(\n    self,\n    use_external_data=False,\n    cache_path=settings.DB,\n    fallback=None,\n):",
                        fix_explanation="API应使用'use_external_data'参数替代'cache'和'use_cache_server'。默认值应为False以避免网络依赖。",
                        severity="critical"
                    )
                    print(f"    ✗ 发现关键问题: API仍使用网络依赖参数 (cache/use_cache_server)")
                    return
            
            # 检查是否使用了新的API
            if 'use_external_data' in content:
                print(f"    ✓ API设计正确: 使用 'use_external_data' 参数")
                return
        
        # 如果找不到文件
        self.add_vulnerability(
            file="fake_useragent/fake.py",
            line_numbers=[],
            original="文件未找到",
            updated="应创建fake.py并使用use_external_data参数",
            fix_explanation="核心模块文件不存在",
            severity="critical"
        )
    
    def check_local_data_file(self):
        """检查是否存在本地数据文件"""
        print("  ├─ 检查本地数据文件...")
        
        data_paths = [
            self.target_dir / "fake_useragent" / "data" / "browsers.json",
            self.target_dir / "src" / "fake_useragent" / "data" / "browsers.json"
        ]
        
        found = False
        for data_path in data_paths:
            if data_path.exists():
                # 检查文件是否有效
                try:
                    with open(data_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if 'chrome' in data and data['chrome']:
                        print(f"    ✓ 本地数据文件存在且有效: {data_path.name}")
                        found = True
                        break
                except:
                    pass
        
        if not found:
            self.add_vulnerability(
                file="fake_useragent/data/browsers.json",
                line_numbers=[],
                original="本地数据文件不存在",
                updated='{"chrome": ["Mozilla/5.0..."]}',
                fix_explanation="应添加本地browsers.json数据文件，包含预先收集的user agent字符串，以避免网络依赖。",
                severity="high"
            )
            print("    ✗ 发现高危问题: 缺少本地数据文件")
    
    def check_test_network_dependency(self):
        """检查测试代码是否使用网络依赖参数"""
        print("  ├─ 检查测试代码...")
        
        test_paths = list(self.target_dir.glob("tests/test_*.py"))
        
        for test_file in test_paths:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # 检查是否使用了网络依赖的参数组合
            problematic_patterns = [
                (r'UserAgent\s*\(\s*cache\s*=\s*False\s*,\s*use_cache_server\s*=\s*False', 
                 'UserAgent(cache=False, use_cache_server=False)'),
                (r'use_cache_server\s*=\s*False',
                 'use_cache_server=False')
            ]
            
            found_issues = []
            for i, line in enumerate(lines, 1):
                for pattern, desc in problematic_patterns:
                    if re.search(pattern, line):
                        found_issues.append(i)
            
            if found_issues:
                # 找到测试函数
                test_functions = []
                for i, line in enumerate(lines):
                    if line.strip().startswith('def test_'):
                        test_functions.append((i+1, line.strip()))
                
                original_snippet = '\n'.join(lines[:50])  # 前50行作为示例
                
                self.add_vulnerability(
                    file=str(test_file.relative_to(self.target_dir)),
                    line_numbers=found_issues,
                    original=original_snippet,
                    updated="ua = UserAgent()  # 默认使用本地数据，无需指定参数",
                    fix_explanation="测试不应使用会导致网络访问的参数。应使用默认参数（use_external_data=False）或mock网络调用。",
                    severity="high"
                )
                print(f"    ✗ 发现高危问题: 测试代码使用网络依赖参数")
                continue
            
            # 检查是否有适当的mock
            if 'UserAgent' in content:
                has_mock = 'mock' in content.lower() or 'patch' in content
                if not has_mock and 'use_cache_server' in content:
                    print(f"    ⚠ 警告: 测试可能缺少mock")
                else:
                    print(f"    ✓ 测试代码正确: 不依赖网络或使用了mock")
    
    def check_default_behavior(self):
        """检查默认行为是否安全（不访问网络）"""
        print("  └─ 检查默认行为...")
        
        fake_py_paths = [
            self.target_dir / "fake_useragent" / "fake.py",
            self.target_dir / "src" / "fake_useragent" / "fake.py"
        ]
        
        for fake_py in fake_py_paths:
            if not fake_py.exists():
                continue
            
            with open(fake_py, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # 检查load方法的默认行为
            if 'def load' in content:
                # 检查是否默认访问网络
                if 'use_cache_server' in content and 'if' not in content[:content.find('use_cache_server')].split('\n')[-1]:
                    # 可能默认就会访问网络
                    load_start = None
                    for i, line in enumerate(lines):
                        if 'def load' in line:
                            load_start = i
                            break
                    
                    if load_start:
                        load_method = '\n'.join(lines[load_start:load_start+15])
                        
                        self.add_vulnerability(
                            file=str(fake_py.relative_to(self.target_dir)),
                            line_numbers=[load_start + 1],
                            original=load_method,
                            updated="def load(self):\n    if self.use_external_data:\n        # 访问网络\n    else:\n        # 使用本地数据",
                            fix_explanation="load方法应默认使用本地数据，只有在use_external_data=True时才访问网络。",
                            severity="medium"
                        )
                        print(f"    ✗ 发现中危问题: load方法可能默认访问网络")
                        return
                
                # 检查是否正确实现了本地数据加载
                if 'use_external_data' in content and ('json.load' in content or 'browsers.json' in content):
                    print(f"    ✓ 默认行为正确: 优先使用本地数据")
                    return
    
    def add_vulnerability(self, file: str, line_numbers: List[int], original: str, 
                         updated: str, fix_explanation: str, severity: str = "medium"):
        """添加漏洞记录"""
        self.vulnerabilities.append({
            "id": self.vulnerability_id,
            "file": file,
            "line_numbers": line_numbers,
            "original": original[:300] + "..." if len(original) > 300 else original,
            "updated": updated,
            "fix_explanation": fix_explanation,
            "severity": severity
        })
        self.vulnerability_id += 1
    
    def generate_report(self) -> Dict[str, Any]:
        """生成检测报告"""
        severity_count = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for vuln in self.vulnerabilities:
            severity = vuln.get("severity", "medium")
            severity_count[severity] += 1
        
        report = {
            "summary": {
                "total_vulnerabilities": len(self.vulnerabilities),
                "critical": severity_count["critical"],
                "high": severity_count["high"],
                "medium": severity_count["medium"],
                "low": severity_count["low"]
            },
            "details": [
                {
                    "id": v["id"],
                    "file": v["file"],
                    "line_numbers": v["line_numbers"],
                    "original": v["original"],
                    "updated": v["updated"],
                    "fix_explanation": v["fix_explanation"]
                }
                for v in self.vulnerabilities
            ]
        }
        
        return report


def main():
    if len(sys.argv) != 2:
        print("用法: python auto_test.py <case_before|case_after>")
        sys.exit(1)
    
    target = sys.argv[1]
    
    if not os.path.exists(target):
        print(f"❌ 错误: 目录 '{target}' 不存在")
        sys.exit(1)
    
    print("=" * 60)
    print("🔒 网络依赖漏洞自动化检测工具")
    print("=" * 60)
    print(f"📂 目标目录: {target}")
    print()
    
    # 执行检查
    checker = NetworkDependencyChecker(target)
    report = checker.check_all()
    
    # 保存报告
    report_path = "report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # 打印结果
    print()
    print("=" * 60)
    print("📊 检测结果汇总")
    print("=" * 60)
    print(f"总漏洞数: {report['summary']['total_vulnerabilities']}")
    print(f"  🔴 关键 (Critical): {report['summary']['critical']}")
    print(f"  🟠 高危 (High):     {report['summary']['high']}")
    print(f"  🟡 中危 (Medium):   {report['summary']['medium']}")
    print(f"  🟢 低危 (Low):      {report['summary']['low']}")
    print()
    
    if report['summary']['total_vulnerabilities'] == 0:
        print("✅ 恭喜！未发现网络依赖问题，修复正确！")
        print()
        exit_code = 0
    else:
        print("❌ 发现网络依赖问题，需要修复：")
        print()
        for detail in report['details']:
            print(f"  [{detail['id']}] {detail['file']}")
            if detail['line_numbers']:
                print(f"      行号: {detail['line_numbers']}")
            print(f"      说明: {detail['fix_explanation']}")
            print()
        exit_code = 1
    
    print(f"📝 详细报告已保存至: {report_path}")
    print("=" * 60)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
