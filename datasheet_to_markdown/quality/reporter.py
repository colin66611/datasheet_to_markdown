"""质量报告器 - 生成质量报告并输出CLI警告"""

from typing import List, Dict
from datasheet_to_markdown.utils.logger import setup_logger

logger = setup_logger(__name__)


class QualityReporter:
    """质量报告器"""

    def __init__(self):
        self.tables_checked: List[Dict] = []
        self.total_tables: int = 0
        self.total_confidence: float = 0.0
        self.logger = logger

    def report_table(self, table_info: Dict):
        """
        记录表格质量信息

        Args:
            table_info:
            {
                "page_num": 4,
                "caption": "Pin Functions",
                "flask": 75.5,
                "needs_manual_check": True,
                "complexity": "high"
            }
        """
        self.tables_checked.append(table_info)
        self.total_tables += 1

        if "flask" in table_info:
            self.total_confidence += table_info["flask"]

    def print_summary(self):
        """
        输出CLI质量摘要

        示例输出：
        ⚠️ 警告：检测到 3 个需要人工核对的表格
        ⚠️ 表格 2（第4页）：引脚功能表 - 复杂度：高
        💡 在生成的Markdown中搜索 [MANUAL_CHECK] 可快速定位

        📊 质量报告：
        - 总表格数：75
        - 需要人工核对：3 (4%)
        - 平均置信度：92.5%
        - 覆盖率：99.2%
        """
        # 统计需要人工核对的表格
        manual_check_tables = [t for t in self.tables_checked if t.get("needs_manual_check", False)]

        if manual_check_tables:
            print(f"\n⚠️  警告：检测到 {len(manual_check_tables)} 个需要人工核对的表格\n")

            for i, table in enumerate(manual_check_tables[:5], 1):  # 最多显示5个
                page = table.get("page", "?")
                caption = table.get("caption", f"Table {i}")
                complexity = table.get("complexity", {})
                complexity_score = complexity.get("complexity_score", 0)

                if complexity_score > 0.7:
                    level = "高"
                elif complexity_score > 0.4:
                    level = "中"
                else:
                    level = "低"

                print(f"⚠️  表格 {i}（第{page}页）：{caption} - 复杂度：{level}")

            if len(manual_check_tables) > 5:
                print(f"... 还有 {len(manual_check_tables) - 5} 个表格需要核对")

            print("\n💡 在生成的Markdown中搜索 [MANUAL_CHECK] 可快速定位\n")

        # 输出质量报告
        metrics = self.get_metrics()

        print("📊 质量报告：")
        print(f"- 总表格数：{metrics['total_tables']}")
        print(f"- 需要人工核对：{metrics['manual_check_tables']} "
              f"({metrics['manual_check_ratio'] * 100:.1f}%)")

        if metrics['avg_confidence'] > 0:
            print(f"- 平均置信度：{metrics['avg_confidence']:.1f}%")

        print(f"- 覆盖率：{metrics['coverage']:.1f}%\n")

    def get_metrics(self) -> Dict:
        """
        获取质量指标

        Returns:
            {
                "total_tables": 75,
                "manual_check_tables": 3,
                "manual_check_ratio": 0.04,
                "avg_confidence": 92.5,
                "coverage": 99.2
            }
        """
        manual_check_count = sum(1 for t in self.tables_checked
                                if t.get("needs_manual_check", False))

        avg_confidence = self.total_confidence / self.total_tables if self.total_tables > 0 else 0

        # 覆盖率计算：(准确字段 + 已标注不确定字段) / 总字段
        # 简化计算：100% - (可疑单元格比例 * 置信度折扣)
        total_uncertain = sum(len(t.get("uncertain_cells", [])) for t in self.tables_checked)
        total_cells = sum(
            t.get("complexity", {}).get("rows", 0) * t.get("complexity", {}).get("cols", 0)
            for t in self.tables_checked
        )

        uncertain_ratio = total_uncertain / total_cells if total_cells > 0 else 0
        coverage = (1 - uncertain_ratio * 0.5) * 100  # 假设每个不确定单元格影响50%

        return {
            "total_tables": self.total_tables,
            "manual_check_tables": manual_check_count,
            "manual_check_ratio": manual_check_count / self.total_tables if self.total_tables > 0 else 0,
            "avg_confidence": avg_confidence,
            "coverage": coverage
        }
