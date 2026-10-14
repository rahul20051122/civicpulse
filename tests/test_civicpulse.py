"""
Automated Test Suite for CivicPulse AI
Verifies data schemas, image resizing, fallback simulation, and safety filters.
"""

import os
import sys
import io
import unittest

# Ensure parent directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PIL import Image
import app


class TestCivicPulseAI(unittest.TestCase):

    def test_categories_and_severities(self):
        """Ensure standard categories and severities are defined."""
        self.assertIn("Roads", app.VALID_CATEGORIES)
        self.assertIn("Electricity", app.VALID_CATEGORIES)
        self.assertIn("Sanitation", app.VALID_CATEGORIES)
        self.assertIn("Water", app.VALID_CATEGORIES)
        self.assertIn("Critical", app.VALID_SEVERITIES)
        self.assertIn("High", app.VALID_SEVERITIES)
        self.assertIn("Moderate", app.VALID_SEVERITIES)
        self.assertIn("Low", app.VALID_SEVERITIES)

    def test_civic_report_model(self):
        """Ensure CivicReport dataclass creates and converts to dict properly."""
        report = app.CivicReport(
            id="CP-TEST-001",
            timestamp="2026-10-14 12:00",
            locality="Test Sector 1",
            user_description="Test user description",
            category="Roads",
            title="Test Road Fault",
            description="Detailed test description",
            severity="High",
            severity_reason="High traffic impact",
            department="Public Works",
            recommended_action="Fill pothole",
            suggested_sla="Within 12 Hours",
            visual_evidence=["Pavement cracks"],
            uncertainties=["Depth unknown"],
            needs_human_review=True,
            status="Submitted",
            image_bytes=b"dummy_bytes",
            is_demo_mode=True
        )
        data_dict = report.to_dict()
        self.assertEqual(data_dict["id"], "CP-TEST-001")
        self.assertEqual(data_dict["severity"], "High")
        self.assertNotIn("image_bytes", data_dict, "Binary image bytes should be excluded from serializable dict")

    def test_image_resizing_logic(self):
        """Ensure large images are resized to max dimension preserving aspect ratio."""
        # Create a mock 2000 x 1000 image
        img = Image.new("RGB", (2000, 1000), color=(100, 150, 200))
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        buffer.seek(0)

        processed_img, img_bytes, err = app.process_and_resize_image(buffer, max_dimension=1024)
        self.assertIsNone(err)
        self.assertIsNotNone(processed_img)
        self.assertIsNotNone(img_bytes)
        self.assertLessEqual(processed_img.width, 1024)
        self.assertLessEqual(processed_img.height, 1024)
        self.assertEqual(processed_img.width, 1024)
        self.assertEqual(processed_img.height, 512)

    def test_demo_analysis_electricity_keyword(self):
        """Verify intelligent demo analysis triggers Critical for electrical hazards."""
        result = app.generate_intelligent_demo_analysis("Downtown", "Exposed sparking wire dangling near sidewalk")
        self.assertEqual(result["category"], "Electricity")
        self.assertEqual(result["severity"], "Critical")
        self.assertTrue(result["needs_human_review"])
        self.assertIn("visual_evidence", result)
        self.assertIn("uncertainties", result)

    def test_demo_analysis_water_keyword(self):
        """Verify intelligent demo analysis routes water leaks to Water department."""
        result = app.generate_intelligent_demo_analysis("North Square", "Clean water pipe leak bubbling from street")
        self.assertEqual(result["category"], "Water")
        self.assertIn("Water", result["department"])

    def test_seed_reports_validity(self):
        """Verify all default seed reports have valid categories, severities, and statuses."""
        for rep in app.DEFAULT_SEED_REPORTS:
            self.assertIn(rep.category, app.VALID_CATEGORIES)
            self.assertIn(rep.severity, app.VALID_SEVERITIES)
            self.assertIn(rep.status, app.VALID_STATUSES)
            self.assertTrue(rep.id.startswith("CP-2026-"))


if __name__ == "__main__":
    unittest.main()
