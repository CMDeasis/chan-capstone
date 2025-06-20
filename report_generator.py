"""
DPA Compliance Report Generator
Creates detailed PDF reports of compliance analysis results
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import red, green, orange, black, blue
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus import PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import os
from datetime import datetime

class DPAReportGenerator:
    """Generate comprehensive DPA compliance reports"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Set up custom styles for the report"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=blue
        ))

        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=black
        ))

        self.styles.add(ParagraphStyle(
            name='ViolationHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=6,
            spaceBefore=12,
            textColor=red
        ))

        self.styles.add(ParagraphStyle(
            name='RecommendationHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=6,
            spaceBefore=12,
            textColor=green
        ))

    def generate_report(self, compliance_report, output_path="data/output/dpa_compliance_report.pdf"):
        """Generate a comprehensive PDF report"""

        # Create document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Build story (content)
        story = []

        # Title page
        story.extend(self._create_title_page(compliance_report))
        story.append(PageBreak())

        # Executive summary
        story.extend(self._create_executive_summary(compliance_report))
        story.append(PageBreak())

        # PII Analysis
        story.extend(self._create_pii_analysis(compliance_report))

        # Violations section
        if compliance_report["violations"]:
            story.append(PageBreak())
            story.extend(self._create_violations_section(compliance_report))

        # Recommendations
        story.append(PageBreak())
        story.extend(self._create_recommendations_section(compliance_report))

        # Appendix
        story.append(PageBreak())
        story.extend(self._create_appendix(compliance_report))

        # Build PDF
        doc.build(story)

        return output_path

    def _create_title_page(self, report):
        """Create the title page"""
        story = []

        # Main title
        story.append(Paragraph("Data Privacy Act Compliance Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*inch))

        # Document info
        story.append(Paragraph(f"<b>Document:</b> {report['document_name']}", self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))

        analysis_date = report.get('analysis_date', datetime.now().isoformat())
        story.append(Paragraph(f"<b>Analysis Date:</b> {analysis_date[:10]}", self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))

        # Status with color coding
        status_color = green if report['compliance_status'] == 'COMPLIANT' else red
        story.append(Paragraph(
            f"<b>Compliance Status:</b> <font color='{status_color.hexval()}'>{report['compliance_status']}</font>",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.2*inch))

        # Risk level with color coding
        risk_colors = {'LOW': green, 'MEDIUM': orange, 'HIGH': red, 'CRITICAL': red}
        risk_color = risk_colors.get(report['risk_level'], black)
        story.append(Paragraph(
            f"<b>Risk Level:</b> <font color='{risk_color.hexval()}'>{report['risk_level']}</font>",
            self.styles['Normal']
        ))

        story.append(Spacer(1, 1*inch))

        # Summary stats
        story.append(Paragraph("<b>Summary Statistics</b>", self.styles['SectionHeader']))

        # Safely get data with fallbacks
        pii_summary = report.get('pii_summary', {})
        violations = report.get('violations', [])
        consent_indicators = report.get('consent_indicators', [])
        purpose_indicators = report.get('purpose_indicators', [])

        stats_data = [
            ['Metric', 'Count'],
            ['Total PII Instances', str(pii_summary.get('total_pii_count', 0))],
            ['Sensitive PII Instances', str(pii_summary.get('sensitive_count', 0))],
            ['Regular PII Instances', str(pii_summary.get('regular_count', 0))],
            ['Total Violations', str(len(violations))],
            ['Consent Indicators', str(len(consent_indicators))],
            ['Purpose Indicators', str(len(purpose_indicators))]
        ]

        stats_table = Table(stats_data, colWidths=[3*inch, 1*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), (1, 1, 1)),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), (0.9, 0.9, 0.9)),
            ('GRID', (0, 0), (-1, -1), 1, black)
        ]))

        story.append(stats_table)

        return story

    def _create_executive_summary(self, report):
        """Create executive summary"""
        story = []

        story.append(Paragraph("Executive Summary", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Overall assessment
        document_name = report.get('document_name', 'Unknown Document')
        compliance_status = report.get('compliance_status', 'UNKNOWN')

        if compliance_status == 'COMPLIANT':
            summary_text = f"""
            The document '{document_name}' has been analyzed for compliance with the
            Republic Act No. 10173 (Data Privacy Act of 2012). The analysis indicates that the
            document is <font color='{green.hexval()}'><b>COMPLIANT</b></font> with DPA requirements.
            """
        else:
            summary_text = f"""
            The document '{document_name}' has been analyzed for compliance with the
            Republic Act No. 10173 (Data Privacy Act of 2012). The analysis indicates that the
            document is <font color='{red.hexval()}'><b>NON-COMPLIANT</b></font> with DPA requirements
            and requires immediate attention.
            """

        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))

        # Key findings
        story.append(Paragraph("<b>Key Findings:</b>", self.styles['Normal']))
        story.append(Spacer(1, 0.1*inch))

        # Safely get data for findings
        pii_summary = report.get('pii_summary', {})
        violations = report.get('violations', [])
        risk_level = report.get('risk_level', 'UNKNOWN')

        findings = [
            f"• {pii_summary.get('total_pii_count', 0)} instances of personal information detected",
            f"• {pii_summary.get('sensitive_count', 0)} instances of sensitive personal information found",
            f"• {len(violations)} DPA violations identified",
            f"• Risk level assessed as: {risk_level}"
        ]

        for finding in findings:
            story.append(Paragraph(finding, self.styles['Normal']))

        story.append(Spacer(1, 0.3*inch))

        # Immediate actions required
        violations = report.get('violations', [])
        recommendations = report.get('recommendations', [])

        if violations:
            story.append(Paragraph("<b>Immediate Actions Required:</b>", self.styles['Normal']))
            story.append(Spacer(1, 0.1*inch))

            high_priority_recs = [r for r in recommendations if r.get('priority', 'LOW') in ['CRITICAL', 'HIGH']]
            for rec in high_priority_recs[:3]:
                action = rec.get('action', 'Unknown action')
                description = rec.get('description', 'No description available')
                story.append(Paragraph(f"• {action}: {description}", self.styles['Normal']))

        return story

    def _create_pii_analysis(self, report):
        """Create PII analysis section"""
        story = []

        story.append(Paragraph("Personal Information Analysis", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))

        pii_summary = report.get('pii_summary', {})

        # PII breakdown
        regular_pii = pii_summary.get('regular_pii', [])
        sensitive_pii = pii_summary.get('sensitive_pii', [])

        if regular_pii:
            story.append(Paragraph("<b>Regular Personal Information:</b>", self.styles['Normal']))
            for pii in regular_pii[:10]:  # Show first 10
                entity_type = pii.get('entity_type', 'UNKNOWN') if isinstance(pii, dict) else 'UNKNOWN'
                text = pii.get('text', str(pii)) if isinstance(pii, dict) else str(pii)
                confidence = pii.get('confidence', 1.0) if isinstance(pii, dict) else 1.0

                story.append(Paragraph(
                    f"• {entity_type}: {text} (Confidence: {confidence:.2f})",
                    self.styles['Normal']
                ))
            story.append(Spacer(1, 0.2*inch))

        if sensitive_pii:
            story.append(Paragraph("<b>Sensitive Personal Information:</b>", self.styles['ViolationHeader']))
            for pii in sensitive_pii[:10]:  # Show first 10
                entity_type = pii.get('entity_type', 'UNKNOWN') if isinstance(pii, dict) else 'UNKNOWN'
                text = pii.get('text', str(pii)) if isinstance(pii, dict) else str(pii)
                confidence = pii.get('confidence', 1.0) if isinstance(pii, dict) else 1.0

                story.append(Paragraph(
                    f"• {entity_type}: {text} (Confidence: {confidence:.2f})",
                    self.styles['Normal']
                ))
            story.append(Spacer(1, 0.2*inch))

        # Consent and purpose analysis
        consent_indicators = report.get('consent_indicators', [])
        purpose_indicators = report.get('purpose_indicators', [])

        story.append(Paragraph("<b>Consent Indicators:</b>", self.styles['Normal']))
        if consent_indicators:
            for indicator in consent_indicators[:5]:
                indicator_text = indicator.get('text', str(indicator)) if isinstance(indicator, dict) else str(indicator)
                story.append(Paragraph(f"• Found: '{indicator_text}'", self.styles['Normal']))
        else:
            story.append(Paragraph("• No consent indicators found", self.styles['Normal']))

        story.append(Spacer(1, 0.2*inch))

        story.append(Paragraph("<b>Purpose Indicators:</b>", self.styles['Normal']))
        if purpose_indicators:
            for indicator in purpose_indicators[:5]:
                indicator_text = indicator.get('text', str(indicator)) if isinstance(indicator, dict) else str(indicator)
                story.append(Paragraph(f"• Found: '{indicator_text}'", self.styles['Normal']))
        else:
            story.append(Paragraph("• No purpose indicators found", self.styles['Normal']))

        return story

    def _create_violations_section(self, report):
        """Create violations section"""
        story = []

        story.append(Paragraph("DPA Violations Identified", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))

        violations = report.get('violations', [])

        for i, violation in enumerate(violations, 1):
            # Safely get violation data
            title = violation.get('title', violation.get('violation', 'Unknown Violation'))
            section = violation.get('section', 'Unknown Section')
            severity = violation.get('severity', 'UNKNOWN')
            description = violation.get('description', 'No description available')
            details = violation.get('details', violation.get('legal_basis', 'No details available'))
            affected_data = violation.get('affected_data', [])

            # Violation header
            story.append(Paragraph(
                f"Violation {i}: {title}",
                self.styles['ViolationHeader']
            ))

            # Violation details
            story.append(Paragraph(f"<b>Section:</b> {section}", self.styles['Normal']))
            story.append(Paragraph(f"<b>Severity:</b> {severity}", self.styles['Normal']))
            story.append(Paragraph(f"<b>Description:</b> {description}", self.styles['Normal']))
            story.append(Paragraph(f"<b>Details:</b> {details}", self.styles['Normal']))

            if affected_data:
                story.append(Paragraph("<b>Affected Data:</b>", self.styles['Normal']))
                for data in affected_data:
                    story.append(Paragraph(f"• {data}", self.styles['Normal']))

            story.append(Spacer(1, 0.3*inch))

        return story

    def _create_recommendations_section(self, report):
        """Create recommendations section"""
        story = []

        story.append(Paragraph("Recommendations", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))

        # Group recommendations by priority
        recommendations = report.get('recommendations', [])
        priorities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']

        for priority in priorities:
            priority_recs = [r for r in recommendations if r.get('priority', 'LOW') == priority]
            if priority_recs:
                story.append(Paragraph(f"{priority} Priority Actions", self.styles['RecommendationHeader']))

                for rec in priority_recs:
                    action = rec.get('action', 'Unknown action')
                    description = rec.get('description', 'No description available')
                    section_ref = rec.get('section_reference', 'No reference')

                    story.append(Paragraph(f"<b>{action}</b>", self.styles['Normal']))
                    story.append(Paragraph(f"Description: {description}", self.styles['Normal']))
                    story.append(Paragraph(f"Reference: {section_ref}", self.styles['Normal']))
                    story.append(Spacer(1, 0.2*inch))

        return story

    def _create_appendix(self, report):
        """Create appendix with technical details"""
        story = []

        story.append(Paragraph("Appendix: Technical Details", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))

        # DPA sections referenced
        story.append(Paragraph("<b>DPA Sections Referenced:</b>", self.styles['Normal']))
        sections_referenced = set()

        violations = report.get('violations', [])
        recommendations = report.get('recommendations', [])

        for violation in violations:
            section = violation.get('section', 'Unknown')
            if section != 'Unknown':
                sections_referenced.add(section)

        for recommendation in recommendations:
            section_ref = recommendation.get('section_reference', 'Unknown')
            if section_ref != 'Unknown':
                sections_referenced.add(section_ref)

        for section in sorted(sections_referenced):
            story.append(Paragraph(f"• {section}", self.styles['Normal']))

        story.append(Spacer(1, 0.3*inch))

        # Analysis methodology
        story.append(Paragraph("<b>Analysis Methodology:</b>", self.styles['Normal']))
        methodology_text = """
        This analysis was conducted using automated tools that:
        1. Extract text from uploaded documents (PDF, DOCX, images)
        2. Detect personal information using pattern recognition and NLP
        3. Identify Philippine-specific PII (TIN, SSS, PhilHealth numbers)
        4. Check for consent and purpose indicators
        5. Apply DPA compliance rules to identify violations
        6. Generate risk assessments and recommendations
        """
        story.append(Paragraph(methodology_text, self.styles['Normal']))

        return story