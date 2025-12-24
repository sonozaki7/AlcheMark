"""
AlcheMark AI - Comprehensive Validation & Testing Suite
========================================================

This script performs comprehensive testing and validation of all AlcheMark AI functionality,
providing human-readable results and detailed test outcomes.

Features tested:
- PDF to Markdown conversion
- Metadata extraction
- Element detection (tables, images, links, lists, titles)
- Token counting
- Language detection
- Formatter functionality
- Model validation
- Integration testing

Results are saved to a timestamped report file for easy review.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import alchemark_ai
    from alchemark_ai import pdf2md
    from alchemark_ai.models import PDFResult, FormattedResult, FormattedMetadata, FormattedElements
    from alchemark_ai.formatter.formatter_md import FormatterMD
    from alchemark_ai.pdf2md.pdf2md import PDF2MarkDown
except ImportError as e:
    print(f"Error importing alchemark_ai: {e}")
    print("Please ensure the package is installed: pip install -e .")
    sys.exit(1)


class ValidationReport:
    """Generates human-readable validation reports."""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = []
        self.summary = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        
    def add_test(self, name: str, status: str, details: str = "", error: str = ""):
        """Add a test result to the report."""
        self.results.append({
            "test_name": name,
            "status": status,
            "details": details,
            "error": error
        })
        self.summary["total_tests"] += 1
        if status == "PASSED":
            self.summary["passed"] += 1
        elif status == "FAILED":
            self.summary["failed"] += 1
            if error:
                self.summary["errors"].append(f"{name}: {error}")
    
    def generate_report(self) -> str:
        """Generate formatted text report."""
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("AlcheMark AI - Comprehensive Validation Report")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        report_lines.append("SUMMARY")
        report_lines.append("-" * 80)
        report_lines.append(f"Total Tests: {self.summary['total_tests']}")
        report_lines.append(f"Passed: {self.summary['passed']} ✓")
        report_lines.append(f"Failed: {self.summary['failed']} ✗")
        report_lines.append(f"Success Rate: {(self.summary['passed'] / max(self.summary['total_tests'], 1) * 100):.1f}%")
        report_lines.append("")
        
        # Detailed results
        report_lines.append("DETAILED TEST RESULTS")
        report_lines.append("-" * 80)
        report_lines.append("")
        
        for result in self.results:
            status_symbol = "✓" if result["status"] == "PASSED" else "✗"
            report_lines.append(f"[{result['status']}] {status_symbol} {result['test_name']}")
            if result["details"]:
                for line in result["details"].split("\n"):
                    report_lines.append(f"    {line}")
            if result["error"]:
                report_lines.append(f"    ERROR: {result['error']}")
            report_lines.append("")
        
        # Error summary
        if self.summary["errors"]:
            report_lines.append("ERROR SUMMARY")
            report_lines.append("-" * 80)
            for error in self.summary["errors"]:
                report_lines.append(f"• {error}")
            report_lines.append("")
        
        report_lines.append("=" * 80)
        report_lines.append("End of Report")
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)
    
    def save_report(self, directory: str = "."):
        """Save report to file."""
        total_tests = self.summary['total_tests']
        report_path = Path(directory) / f"validation_report_{total_tests}_tests_{self.timestamp}.txt"
        report_content = self.generate_report()
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        return report_path


class ComprehensiveValidator:
    """Main validator class for running all tests."""
    
    def __init__(self):
        self.report = ValidationReport()
        self.sample_pdf = self._find_sample_pdf()
    
    def _find_sample_pdf(self) -> Path:
        """Find sample PDF for testing."""
        possible_paths = [
            Path(__file__).parent.parent / "sample" / "Sample.pdf",
            Path(__file__).parent / "sample" / "Sample.pdf",
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        raise FileNotFoundError("Sample PDF not found. Please ensure sample/Sample.pdf exists.")
    
    def test_01_pdf2md_basic_conversion(self):
        """Test 01: Basic PDF to Markdown conversion."""
        try:
            results = pdf2md(str(self.sample_pdf), process_images=False)
            
            assert isinstance(results, list), "Results should be a list"
            assert len(results) > 0, "Results should not be empty"
            assert isinstance(results[0], FormattedResult), "Results should contain FormattedResult objects"
            
            details = f"Successfully converted {len(results)} page(s)\n"
            details += f"First page text length: {len(results[0].text)} characters"
            
            self.report.add_test("Test 01: PDF to Markdown Basic Conversion", "PASSED", details)
            return results
        except Exception as e:
            self.report.add_test("Test 01: PDF to Markdown Basic Conversion", "FAILED", error=str(e))
            return None
    
    def test_02_metadata_extraction(self, results: List[FormattedResult]):
        """Test 02: Metadata extraction from PDF."""
        if not results:
            self.report.add_test("Test 02: Metadata Extraction", "FAILED", error="No results to test")
            return
        
        try:
            result = results[0]
            metadata = result.metadata
            
            assert hasattr(metadata, 'file_path'), "Metadata should have file_path"
            assert hasattr(metadata, 'page'), "Metadata should have page"
            assert hasattr(metadata, 'page_count'), "Metadata should have page_count"
            assert hasattr(metadata, 'text_length'), "Metadata should have text_length"
            assert hasattr(metadata, 'processed_timestamp'), "Metadata should have processed_timestamp"
            
            details = f"File Path: {metadata.file_path}\n"
            details += f"Page: {metadata.page} of {metadata.page_count}\n"
            details += f"Text Length: {metadata.text_length} characters\n"
            details += f"Timestamp: {metadata.processed_timestamp}"
            
            self.report.add_test("Test 02: Metadata Extraction", "PASSED", details)
        except Exception as e:
            self.report.add_test("Test 02: Metadata Extraction", "FAILED", error=str(e))
    
    def test_03_element_detection(self, results: List[FormattedResult]):
        """Test 03: Detection of markdown elements (tables, images, links, etc.)."""
        if not results:
            self.report.add_test("Test 03: Element Detection", "FAILED", error="No results to test")
            return
        
        try:
            result = results[0]
            elements = result.elements
            
            assert hasattr(elements, 'tables'), "Elements should have tables"
            assert hasattr(elements, 'images'), "Elements should have images"
            assert hasattr(elements, 'titles'), "Elements should have titles"
            assert hasattr(elements, 'lists'), "Elements should have lists"
            assert hasattr(elements, 'links'), "Elements should have links"
            
            details = f"Tables detected: {len(elements.tables)}\n"
            details += f"Images detected: {len(elements.images)}\n"
            details += f"Titles detected: {len(elements.titles)}\n"
            details += f"Lists detected: {len(elements.lists)}\n"
            details += f"Links detected: {len(elements.links)}"
            
            self.report.add_test("Test 03: Element Detection", "PASSED", details)
        except Exception as e:
            self.report.add_test("Test 03: Element Detection", "FAILED", error=str(e))
    
    def test_04_token_counting(self, results: List[FormattedResult]):
        """Test 04: Token counting functionality."""
        if not results:
            self.report.add_test("Test 04: Token Counting", "FAILED", error="No results to test")
            return
        
        try:
            result = results[0]
            tokens = result.tokens
            
            assert isinstance(tokens, int), "Tokens should be an integer"
            assert tokens > 0, "Token count should be greater than 0"
            
            details = f"Tokens counted: {tokens}\n"
            details += f"Approximate token-to-character ratio: {len(result.text) / max(tokens, 1):.2f}"
            
            self.report.add_test("Test 04: Token Counting", "PASSED", details)
        except Exception as e:
            self.report.add_test("Test 04: Token Counting", "FAILED", error=str(e))
    
    def test_05_language_detection(self, results: List[FormattedResult]):
        """Test 05: Language detection functionality."""
        if not results:
            self.report.add_test("Test 05: Language Detection", "FAILED", error="No results to test")
            return
        
        try:
            result = results[0]
            language = result.language
            
            assert isinstance(language, str), "Language should be a string"
            assert len(language) > 0, "Language should not be empty"
            
            details = f"Detected language: {language}"
            
            self.report.add_test("Test 05: Language Detection", "PASSED", details)
        except Exception as e:
            self.report.add_test("Test 05: Language Detection", "FAILED", error=str(e))
    
    def test_06_image_processing(self):
        """Test 06: Image processing functionality."""
        try:
            results = pdf2md(str(self.sample_pdf), process_images=True, keep_images_inline=False)
            
            assert isinstance(results, list), "Results should be a list"
            
            has_images = any(len(r.elements.images) > 0 for r in results)
            details = f"Image processing enabled\n"
            details += f"Images found: {sum(len(r.elements.images) for r in results)}"
            
            if has_images:
                first_image = next((r.elements.images[0] for r in results if r.elements.images), None)
                if first_image:
                    details += f"\nFirst image hash: {getattr(first_image, 'hash', 'N/A')}"
            
            self.report.add_test("Test 06: Image Processing", "PASSED", details)
        except Exception as e:
            self.report.add_test("Test 06: Image Processing", "FAILED", error=str(e))
    
    def test_07_inline_image_handling(self):
        """Test 07: Inline image handling with base64."""
        try:
            results = pdf2md(str(self.sample_pdf), process_images=True, keep_images_inline=True)
            
            assert isinstance(results, list), "Results should be a list"
            
            details = f"Inline image processing enabled\n"
            details += f"Total pages processed: {len(results)}"
            
            self.report.add_test("Test 07: Inline Image Handling", "PASSED", details)
        except Exception as e:
            self.report.add_test("Test 07: Inline Image Handling", "FAILED", error=str(e))
    
    def test_08_pdf2md_class(self):
        """Test 08: PDF2MarkDown class directly."""
        try:
            pdf2md_instance = PDF2MarkDown(str(self.sample_pdf))
            
            assert pdf2md_instance.file_path == str(self.sample_pdf), "File path should match"
            assert pdf2md_instance.page_chunks is True, "Page chunks should be True by default"
            
            results = pdf2md_instance.convert()
            
            assert isinstance(results, list), "Results should be a list"
            assert len(results) > 0, "Results should not be empty"
            
            details = f"PDF2MarkDown class instantiated successfully\n"
            details += f"Converted {len(results)} page(s)"
            
            self.report.add_test("Test 08: PDF2MarkDown Class", "PASSED", details)
        except Exception as e:
            self.report.add_test("Test 08: PDF2MarkDown Class", "FAILED", error=str(e))
    
    def test_09_formatter_class(self):
        """Test 09: FormatterMD class."""
        try:
            # Create a mock PDFResult
            from alchemark_ai.models.PDFResult import Metadata
            
            mock_metadata = {
                "format": "PDF 1.7",
                "title": "Test",
                "author": "Test Author",
                "subject": "",
                "keywords": "",
                "creator": "",
                "producer": "",
                "creationDate": "",
                "modDate": "",
                "trapped": "",
                "encryption": None,
                "file_path": str(self.sample_pdf),
                "page_count": 1,
                "page": 1
            }
            
            mock_pdf_result = PDFResult(
                metadata=mock_metadata,
                toc_items=[],
                tables=[],
                images=[],
                graphics=[],
                text="# Test Heading\n\nThis is a test.",
                words=[]
            )
            
            formatter = FormatterMD(mock_pdf_result)
            formatted_result = formatter.format()
            
            assert isinstance(formatted_result, FormattedResult), "Result should be FormattedResult"
            assert formatted_result.text == mock_pdf_result.text, "Text should match"
            
            details = "FormatterMD class working correctly\n"
            details += f"Formatted text length: {len(formatted_result.text)}"
            
            self.report.add_test("Test 09: FormatterMD Class", "PASSED", details)
        except Exception as e:
            self.report.add_test("Test 09: FormatterMD Class", "FAILED", error=str(e))
    
    def test_10_model_serialization(self, results: List[FormattedResult]):
        """Test 10: Model serialization to JSON."""
        if not results:
            self.report.add_test("Test 10: Model Serialization", "FAILED", error="No results to test")
            return
        
        try:
            result = results[0]
            
            # Test model_dump
            dict_data = result.model_dump()
            assert isinstance(dict_data, dict), "model_dump should return a dict"
            
            # Test model_dump_json
            json_data = result.model_dump_json()
            assert isinstance(json_data, str), "model_dump_json should return a string"
            
            # Verify JSON is valid
            parsed = json.loads(json_data)
            assert isinstance(parsed, dict), "Parsed JSON should be a dict"
            
            details = f"Serialization successful\n"
            details += f"Dict keys: {len(dict_data.keys())}\n"
            details += f"JSON length: {len(json_data)} characters"
            
            self.report.add_test("Test 10: Model Serialization", "PASSED", details)
        except Exception as e:
            self.report.add_test("Test 10: Model Serialization", "FAILED", error=str(e))
    
    def test_11_error_handling_invalid_path(self):
        """Test 11: Error handling with invalid file path."""
        try:
            invalid_path = "/nonexistent/path/to/file.pdf"
            pdf2md_instance = PDF2MarkDown(invalid_path)
            
            try:
                pdf2md_instance.convert()
                self.report.add_test("Test 11: Error Handling - Invalid Path", "FAILED", 
                                   error="Should have raised ValueError for invalid path")
            except ValueError as ve:
                details = f"Correctly raised ValueError: {str(ve)}"
                self.report.add_test("Test 11: Error Handling - Invalid Path", "PASSED", details)
        except Exception as e:
            self.report.add_test("Test 11: Error Handling - Invalid Path", "FAILED", error=str(e))
    
    def test_12_error_handling_non_pdf(self):
        """Test 12: Error handling with non-PDF file."""
        try:
            # Try to use a Python file as PDF
            non_pdf_path = __file__
            pdf2md_instance = PDF2MarkDown(non_pdf_path)
            
            try:
                pdf2md_instance.convert()
                self.report.add_test("Test 12: Error Handling - Non-PDF File", "FAILED", 
                                   error="Should have raised ValueError for non-PDF file")
            except ValueError as ve:
                details = f"Correctly raised ValueError: {str(ve)}"
                self.report.add_test("Test 12: Error Handling - Non-PDF File", "PASSED", details)
        except Exception as e:
            self.report.add_test("Test 12: Error Handling - Non-PDF File", "FAILED", error=str(e))
    
    def run_all_tests(self):
        """Run all validation tests."""
        print("=" * 80)
        print("AlcheMark AI - Comprehensive Validation Suite")
        print("=" * 80)
        print(f"Starting validation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Sample PDF: {self.sample_pdf}")
        print()
        
        # Run tests
        print("Running tests...")
        print()
        
        # Core functionality tests
        results = self.test_01_pdf2md_basic_conversion()
        self.test_02_metadata_extraction(results)
        self.test_03_element_detection(results)
        self.test_04_token_counting(results)
        self.test_05_language_detection(results)
        self.test_10_model_serialization(results)
        
        # Advanced feature tests
        self.test_06_image_processing()
        self.test_07_inline_image_handling()
        
        # Class tests
        self.test_08_pdf2md_class()
        self.test_09_formatter_class()
        
        # Error handling tests
        self.test_11_error_handling_invalid_path()
        self.test_12_error_handling_non_pdf()
        
        # Generate and save report
        print()
        print("Generating report...")
        report_path = self.report.save_report(Path(__file__).parent)
        
        # Display report
        print()
        print(self.report.generate_report())
        
        print()
        print(f"Report saved to: {report_path}")
        print()
        
        return self.report.summary


def main():
    """Main entry point for validation."""
    try:
        validator = ComprehensiveValidator()
        summary = validator.run_all_tests()
        
        # Exit with appropriate code
        if summary["failed"] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        print("Please ensure sample/Sample.pdf exists in the project.")
        sys.exit(1)
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
