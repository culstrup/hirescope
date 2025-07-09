"""
Unit tests for DocumentProcessor class
"""

from unittest.mock import Mock, patch

import pytest

from hirescope.document_processor import DocumentProcessor


class TestDocumentProcessor:
    """Test suite for DocumentProcessor class"""

    @pytest.fixture
    def processor(self):
        """Create a DocumentProcessor instance for testing"""
        return DocumentProcessor()

    def test_init_with_all_libraries(self):
        """Test initialization when all libraries are available"""
        with patch("hirescope.document_processor.PyPDF2", Mock()), patch(
            "hirescope.document_processor.Document", Mock()
        ):
            processor = DocumentProcessor()
            assert ".pdf" in processor.supported_formats
            assert ".docx" in processor.supported_formats
            assert ".txt" in processor.supported_formats

    def test_init_without_libraries(self, capsys):
        """Test initialization when libraries are missing"""
        with patch("hirescope.document_processor.PyPDF2", None), patch(
            "hirescope.document_processor.Document", None
        ):
            processor = DocumentProcessor()

            # Check warnings are printed
            captured = capsys.readouterr()
            assert "PyPDF2 not installed" in captured.out
            assert "python-docx not installed" in captured.out

            # Check supported formats
            assert ".pdf" not in processor.supported_formats
            assert ".docx" not in processor.supported_formats
            assert ".txt" in processor.supported_formats

    def test_extract_text_empty_content(self, processor):
        """Test handling of empty content"""
        result = processor.extract_text(b"", "test.pdf")
        assert result == "[Empty file]"

    def test_extract_text_unsupported_format(self, processor):
        """Test handling of unsupported file formats"""
        result = processor.extract_text(b"content", "test.xyz")
        assert "[Unsupported format: .xyz]" in result

    def test_extract_text_legacy_doc(self, processor):
        """Test handling of legacy DOC format"""
        result = processor.extract_text(b"content", "test.doc")
        assert "[Legacy DOC format" in result

    def test_extract_text_exception_handling(self, processor):
        """Test exception handling in extract_text"""
        with patch.object(
            processor, "_extract_pdf_text", side_effect=Exception("Test error")
        ):
            result = processor.extract_text(b"content", "test.pdf")
            assert "[Extraction failed:" in result
            assert "Test error" in result

    # PDF extraction tests
    def test_extract_pdf_text_success(self, processor):
        """Test successful PDF text extraction"""
        with patch("hirescope.document_processor.PyPDF2") as mock_pypdf2:
            # Setup mock - need enough text to pass the 50 char threshold
            mock_page = Mock()
            mock_page.extract_text.return_value = "John Doe\nSoftware Engineer\n5 years experience with Python and cloud technologies"
            mock_reader = Mock()
            mock_reader.pages = [mock_page]
            mock_reader.metadata = {"/Creator": "Microsoft Word"}
            mock_pypdf2.PdfReader.return_value = mock_reader

            # Test
            result = processor._extract_pdf_text(b"fake pdf content")

            # Assert
            assert "John Doe" in result
            assert "Software Engineer" in result
            assert "5 years experience" in result

    def test_extract_pdf_text_image_based(self, processor):
        """Test detection of image-based PDFs"""
        with patch("hirescope.document_processor.PyPDF2") as mock_pypdf2:
            # Setup mock for image-based PDF (little extractable text)
            mock_page = Mock()
            mock_page.extract_text.return_value = "   \n  "
            mock_reader = Mock()
            mock_reader.pages = [mock_page, mock_page]  # 2 pages
            mock_reader.metadata = {"/Creator": "Scanner Pro"}
            mock_pypdf2.PdfReader.return_value = mock_reader

            # Test
            result = processor._extract_pdf_text(b"fake pdf content")

            # Assert
            assert "[IMAGE-BASED PDF DETECTED]" in result
            assert "Creator: Scanner Pro" in result
            assert "Pages: 2" in result

    def test_extract_pdf_text_no_metadata(self, processor):
        """Test PDF extraction when metadata is None"""
        with patch("hirescope.document_processor.PyPDF2") as mock_pypdf2:
            # Setup mock
            mock_page = Mock()
            mock_page.extract_text.return_value = "  "
            mock_reader = Mock()
            mock_reader.pages = [mock_page]
            mock_reader.metadata = None
            mock_pypdf2.PdfReader.return_value = mock_reader

            # Test
            result = processor._extract_pdf_text(b"fake pdf content")

            # Assert
            assert "Creator: Unknown" in result

    def test_extract_pdf_text_no_library(self, processor):
        """Test PDF extraction when PyPDF2 is not installed"""
        with patch("hirescope.document_processor.PyPDF2", None):
            result = processor._extract_pdf_text(b"content")
            assert "[PDF extraction unavailable - install PyPDF2]" in result

    def test_extract_pdf_text_exception(self, processor):
        """Test PDF extraction error handling"""
        with patch(
            "hirescope.document_processor.PyPDF2.PdfReader",
            side_effect=Exception("PDF error"),
        ):
            result = processor._extract_pdf_text(b"content")
            assert "[PDF extraction error:" in result
            assert "PDF error" in result

    # DOCX extraction tests
    def test_extract_docx_text_success(self, processor):
        """Test successful DOCX text extraction"""
        with patch("hirescope.document_processor.Document") as mock_doc:
            # Setup mock
            doc_instance = Mock()

            # Mock paragraphs
            para1 = Mock()
            para1.text = "Jane Smith"
            para2 = Mock()
            para2.text = "Product Manager"
            para3 = Mock()
            para3.text = "  "  # Empty paragraph
            doc_instance.paragraphs = [para1, para2, para3]

            # Mock tables
            cell1 = Mock()
            cell1.text = "Skill"
            cell2 = Mock()
            cell2.text = "Years"
            cell3 = Mock()
            cell3.text = "Python"
            cell4 = Mock()
            cell4.text = "5"

            row1 = Mock()
            row1.cells = [cell1, cell2]
            row2 = Mock()
            row2.cells = [cell3, cell4]

            table = Mock()
            table.rows = [row1, row2]
            doc_instance.tables = [table]

            mock_doc.return_value = doc_instance

            # Test
            result = processor._extract_docx_text(b"fake docx content")

            # Assert
            assert "Jane Smith" in result
            assert "Product Manager" in result
            assert "Skill | Years" in result
            assert "Python | 5" in result

    def test_extract_docx_text_no_library(self, processor):
        """Test DOCX extraction when python-docx is not installed"""
        with patch("hirescope.document_processor.Document", None):
            result = processor._extract_docx_text(b"content")
            assert "[DOCX extraction unavailable - install python-docx]" in result

    def test_extract_docx_text_exception(self, processor):
        """Test DOCX extraction error handling"""
        with patch(
            "hirescope.document_processor.Document", side_effect=Exception("DOCX error")
        ):
            result = processor._extract_docx_text(b"content")
            assert "[DOCX extraction error:" in result
            assert "DOCX error" in result

    # TXT extraction tests
    def test_extract_txt_text_utf8(self, processor):
        """Test TXT extraction with UTF-8 encoding"""
        content = "Hello World\nTest résumé".encode()
        result = processor._extract_txt_text(content)
        assert "Hello World" in result
        assert "Test résumé" in result

    def test_extract_txt_text_latin1(self, processor):
        """Test TXT extraction with Latin-1 encoding"""
        content = "Test café".encode("latin-1")
        result = processor._extract_txt_text(content)
        assert "Test café" in result

    def test_extract_txt_text_fallback(self, processor):
        """Test TXT extraction with fallback for invalid encoding"""
        # Create some invalid UTF-8 bytes
        content = b"Test \xff\xfe invalid"
        result = processor._extract_txt_text(content)
        # Should not raise exception, but might have some replacement chars
        assert "Test" in result

    def test_extract_txt_text_exception(self, processor):
        """Test TXT extraction error handling"""
        # Create mock content that raises exception on decode
        mock_content = Mock(spec=bytes)
        mock_content.decode.side_effect = Exception("Decode error")

        result = processor._extract_txt_text(mock_content)
        assert "[TXT extraction error:" in result
        assert "Decode error" in result

    # Text preview tests
    def test_get_text_preview_short_text(self, processor):
        """Test preview when text is shorter than max length"""
        text = "Short text"
        result = processor.get_text_preview(text, max_length=100)
        assert result == "Short text"

    def test_get_text_preview_long_text(self, processor):
        """Test preview when text exceeds max length"""
        text = "A" * 100
        result = processor.get_text_preview(text, max_length=50)
        assert len(result) == 53  # 50 chars + "..."
        assert result.endswith("...")

    def test_get_text_preview_whitespace_cleanup(self, processor):
        """Test whitespace cleanup in preview"""
        text = "Multiple   spaces\n\nand\tnewlines"
        result = processor.get_text_preview(text)
        assert result == "Multiple spaces and newlines"

    def test_get_text_preview_error_text(self, processor):
        """Test preview with error messages (starting with '[')"""
        text = "[Error message]"
        result = processor.get_text_preview(text)
        assert result == "[Error message]"

    def test_get_text_preview_empty_text(self, processor):
        """Test preview with empty text"""
        result = processor.get_text_preview("")
        assert result == ""

    # Integration-style tests
    @pytest.mark.parametrize(
        "filename,content,expected_method",
        [
            ("resume.pdf", b"pdf", "_extract_pdf_text"),
            ("cv.docx", b"docx", "_extract_docx_text"),
            ("notes.txt", b"txt", "_extract_txt_text"),
            ("old.doc", b"doc", None),  # Legacy format
            ("image.jpg", b"jpg", None),  # Unsupported
        ],
    )
    def test_extract_text_routing(self, processor, filename, content, expected_method):
        """Test that extract_text routes to the correct method"""
        if expected_method:
            with patch.object(
                processor, expected_method, return_value="Extracted"
            ) as mock_method:
                result = processor.extract_text(content, filename)
                assert mock_method.called
                assert result == "Extracted"
        else:
            result = processor.extract_text(content, filename)
            assert "[" in result  # Error or unsupported message

    def test_extract_text_case_insensitive(self, processor):
        """Test that file extension detection is case insensitive"""
        with patch.object(
            processor, "_extract_pdf_text", return_value="PDF content"
        ) as mock_pdf:
            # Test various cases
            for filename in ["test.PDF", "test.Pdf", "test.pDf"]:
                result = processor.extract_text(b"content", filename)
                assert mock_pdf.called
                assert result == "PDF content"
                mock_pdf.reset_mock()
