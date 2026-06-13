import io
import logging
import os
from typing import List

from fpdf import FPDF
from services.document_reader import read_document

logger = logging.getLogger(__name__)


class HrPolicyPDFGenerator:
    def generate(self, output_path: str) -> str:
        if os.path.exists(output_path):
            return output_path

        policy_text = self._build_policy_text()
        pdf = _PolicyPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "", 10)
        for paragraph in policy_text.split("\n\n"):
            pdf.multi_cell(0, 6, paragraph)
            pdf.ln(1)
        pdf.output(output_path)
        logger.info("Generated HR policy PDF at %s", output_path)
        return output_path

    def _build_policy_text(self) -> str:
        return (
            "HR Policy Manual - Modernized Edition\n\n"
            "1. Employment\n"
            "Employment is based on mutual commitment between the organization and the employee.\n\n"
            "2. Work Hours and Attendance\n"
            "Standard work hours are 40 hours per week, scheduled between 09:00 and 18:00.\n"
            "Flexible hours may be approved by the department head.\n\n"
            "3. Notice Period\n"
            "The employee notice period is 45 days from the date of resignation submission.\n"
            "The organization notice period for redundancy is 30 days.\n\n"
            "4. Leave Entitlement\n"
            "Earned leave entitlement is 21 days per calendar year.\n"
            "Sick leave entitlement is 12 days per calendar year.\n\n"
            "5. Salary and Compensation\n"
            "Salary is credited by the 7th working day of each month.\n"
            "Incentive payout is 10 percent of base salary upon exceeding quarterly targets by 15 percent.\n\n"
            "6. Performance Review\n"
            "Performance reviews are conducted annually during the months of January and February.\n"
            "Review outcomes may result in promotion with a salary revision.\n\n"
            "7. Code of Conduct\n"
            "Employees must maintain professional behavior and protect confidential information.\n\n"
            "8. Security and Access\n"
            "Login requires two-factor authentication.\n"
            "Remote access requires corporate VPN and signed security acknowledgment.\n\n"
            "9. Compliance\n"
            "The organization follows all applicable labor laws and tax regulations.\n"
            "Non-compliance may result in disciplinary action and legal reporting.\n\n"
            "10. Privacy and Data\n"
            "Employee data is protected under applicable privacy regulations.\n"
            "Any breach must be reported within 72 hours.\n\n"
            "11. Termination\n"
            "Termination may result from policy violation, performance failure, or mutual agreement.\n\n"
            "12. Working Conditions\n"
            "The organization provides safe, inclusive, and accessible working environments.\n"
            "Remote work may be permitted for eligible roles with manager approval.\n\n"
            "13. Recruitment and Onboarding\n"
            "Recruitment follows structured job evaluation and interview panels.\n"
            "Onboarding includes compliance, security, and role-based training.\n\n"
            "14. Training and Development\n"
            "Training resources are allocated yearly for each employee.\n"
            "Career development plans are reviewed biannually with HR.\n\n"
            "15. Grievance and Appeals\n"
            "Grievances must be submitted in writing to HR within 15 days of the incident.\n"
            "HR shall respond within 10 business days.\n\n"
            "16. Benefits\n"
            "Benefits include health insurance, retirement savings support, and wellness programs.\n"
            "Benefits may be revisited at the start of each fiscal year.\n\n"
            "17. Business Ethics\n"
            "The organization expects integrity, transparency, and fairness in all business dealings.\n"
            "Conflicts of interest must be disclosed to the compliance team.\n\n"
            "18. Vendor Engagement\n"
            "Vendor selection must follow procurement policy and competitive evaluation.\n"
            "All vendor agreements must include confidentiality and compliance clauses.\n\n"
            "19. Customer Commitment\n"
            "Service quality and customer confidentiality are mandatory for all customer-facing roles.\n"
            "Feedback must be recorded and reviewed within 5 business days.\n\n"
            "20. Amendment\n"
            "Policies may be amended by the HR and Legal departments with executive approval.\n"
            "Updated policies become effective from the date of approval unless another date is specified.\n"
        )


class _PolicyPDF(FPDF):
    def header(self) -> None:
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 10, "HR Policy Manual", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", new_x="RIGHT", new_y="LAST")
