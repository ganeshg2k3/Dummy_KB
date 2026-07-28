"""Sample report-building module. Calls into data_utils to exercise
cross-file dependency edges in the knowledge graph."""

from src.data_utils import process_batch, summarize_batch, to_json


class ReportBuilder:
    """Builds a formatted report from a batch of raw records."""

    def __init__(self, title, records):
        self.title = title
        self.records = records
        self.valid_records = []
        self.errors = []

    def build(self):
        """Run validation and compute the summary for this report."""
        self.valid_records, self.errors = process_batch(self.records)
        self.summary = summarize_batch(self.valid_records, self.errors)
        return self.summary

    def to_markdown(self):
        """Render the report as a simple markdown string."""
        if not hasattr(self, "summary"):
            self.build()

        lines = [f"# {self.title}", ""]
        lines.append(f"- Total records: {self.summary['total_records']}")
        lines.append(f"- Valid: {self.summary['valid_count']}")
        lines.append(f"- Errors: {self.summary['error_count']}")
        lines.append(f"- Success rate: {self.summary['success_rate']:.1%}")

        if self.errors:
            lines.append("")
            lines.append("## Errors")
            for err in self.errors:
                lines.append(f"- Record {err['record_id']}: {err['error']}")

        return "\n".join(lines)

    def export_json(self):
        """Export the full report (summary + records + errors) as JSON."""
        if not hasattr(self, "summary"):
            self.build()
        return to_json({
            "title": self.title,
            "summary": self.summary,
            "valid_records": self.valid_records,
            "errors": self.errors,
        })


def build_weekly_report(records, week_label):
    """Convenience function: build and return a markdown report for a given week."""
    builder = ReportBuilder(title=f"Weekly Report - {week_label}", records=records)
    builder.build()
    return builder.to_markdown()
