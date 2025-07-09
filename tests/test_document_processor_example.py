"""
Example unit tests for DocumentProcessor
This demonstrates the testing approach outlined in TESTING_PLAN.md
"""

import pytest
from unittest.mock import Mock, patch
from io import BytesIO
from hirescope.document_processor import DocumentProcessor


class TestDocumentProcessor:
    """Test suite for DocumentProcessor class"""
    
    @pytest.fixture
    def processor(self):
        """Create a DocumentProcessor instance for testing"""
        return DocumentProcessor()
    
    @pytest.fixture
    def sample_pdf_content(self):
        """Mock PDF content for testing"""
        return b"%PDF-1.4\n%Fake PDF content for testing"
    
    def test_extract_pdf_text_success(self, processor):
        """
        Test successful PDF text extraction.
        
        Given: A valid PDF with extractable text
        When: extract_pdf_text is called
        Then: Text content should be returned
        """
        # Mock PyPDF2 reader
        with patch('PyPDF2.PdfReader') as mock_reader:
            # Setup mock
            mock_page = Mock()
            mock_page.extract_text.return_value = "John Doe\nSoftware Engineer\n5 years experience"
            mock_reader.return_value.pages = [mock_page]
            
            # Test
            content = BytesIO(b"fake pdf content")
            result = processor.extract_pdf_text(content)
            
            # Assert
            assert result == "John Doe\nSoftware Engineer\n5 years experience"
            assert processor.stats['pdfs_processed'] == 1
    
    def test_extract_pdf_text_image_based(self, processor):
        """
        Test handling of image-based PDFs.
        
        Given: A PDF with no extractable text (image-based)
        When: extract_pdf_text is called
        Then: Empty string should be returned with appropriate stats
        """
        with patch('PyPDF2.PdfReader') as mock_reader:
            # Setup mock for image-based PDF
            mock_page = Mock()
            mock_page.extract_text.return_value = "   \n  \n  "  # Only whitespace
            mock_reader.return_value.pages = [mock_page]
            
            # Test
            content = BytesIO(b"fake pdf content")
            result = processor.extract_pdf_text(content)
            
            # Assert
            assert result == ""
            assert processor.stats['pdfs_processed'] == 1
            assert processor.stats['image_pdfs'] == 1
    
    def test_extract_docx_text_success(self, processor):
        """
        Test successful DOCX text extraction.
        
        Given: A valid DOCX file
        When: extract_docx_text is called
        Then: Text content should be returned
        """
        with patch('docx.Document') as mock_document:
            # Setup mock
            mock_para1 = Mock()
            mock_para1.text = "Jane Smith"
            mock_para2 = Mock()
            mock_para2.text = "Product Manager"
            mock_document.return_value.paragraphs = [mock_para1, mock_para2]
            
            # Test
            content = BytesIO(b"fake docx content")
            result = processor.extract_docx_text(content)
            
            # Assert
            assert result == "Jane Smith\nProduct Manager"
            assert processor.stats['docx_processed'] == 1
    
    def test_process_attachments_mixed_files(self, processor):
        """
        Test processing multiple attachments of different types.
        
        Given: A list with PDF and DOCX attachments
        When: process_attachments is called
        Then: All texts should be extracted and categorized correctly
        """
        # Mock attachments
        attachments = [
            {
                'filename': 'resume.pdf',
                'type': 'resume',
                'url': 'http://example.com/resume.pdf'
            },
            {
                'filename': 'cover_letter.docx',
                'type': 'cover_letter',
                'url': 'http://example.com/cover.docx'
            }
        ]
        
        # Mock URL fetching and content extraction
        with patch('requests.get') as mock_get, \
             patch.object(processor, 'extract_pdf_text') as mock_pdf, \
             patch.object(processor, 'extract_docx_text') as mock_docx:
            
            # Setup mocks
            mock_get.return_value.content = b"fake content"
            mock_get.return_value.raise_for_status = Mock()
            mock_pdf.return_value = "Resume content from PDF"
            mock_docx.return_value = "Cover letter from DOCX"
            
            # Test
            result = processor.process_attachments(attachments)
            
            # Assert
            assert result['resume_text'] == "Resume content from PDF"
            assert result['cover_letter_text'] == "Cover letter from DOCX"
            assert result['other_docs'] == []
            assert mock_pdf.called
            assert mock_docx.called
    
    def test_process_attachments_with_errors(self, processor):
        """
        Test error handling during attachment processing.
        
        Given: Attachments that fail to download
        When: process_attachments is called
        Then: Errors should be handled gracefully
        """
        attachments = [
            {
                'filename': 'resume.pdf',
                'type': 'resume',
                'url': 'http://example.com/broken.pdf'
            }
        ]
        
        with patch('requests.get') as mock_get:
            # Setup mock to raise exception
            mock_get.side_effect = Exception("Network error")
            
            # Test
            result = processor.process_attachments(attachments)
            
            # Assert - should handle error gracefully
            assert result['resume_text'] == ""
            assert result['errors'] == 1
    
    @pytest.mark.parametrize("filename,expected_type", [
        ("document.pdf", "pdf"),
        ("Document.PDF", "pdf"),
        ("file.docx", "docx"),
        ("FILE.DOCX", "docx"),
        ("image.jpg", "unsupported"),
        ("no_extension", "unsupported"),
    ])
    def test_get_file_type(self, processor, filename, expected_type):
        """Test file type detection based on extension"""
        result = processor._get_file_type(filename)
        assert result == expected_type
    
    def test_stats_tracking(self, processor):
        """
        Test that statistics are properly tracked.
        
        Given: Multiple document processing operations
        When: Various extract methods are called
        Then: Stats should accurately reflect operations
        """
        # Process some documents
        with patch('PyPDF2.PdfReader'), patch('docx.Document'):
            processor.extract_pdf_text(BytesIO(b"pdf1"))
            processor.extract_pdf_text(BytesIO(b"pdf2"))
            processor.extract_docx_text(BytesIO(b"docx1"))
        
        # Check stats
        assert processor.stats['pdfs_processed'] == 2
        assert processor.stats['docx_processed'] == 1
        assert processor.stats['total_processed'] == 3


# Integration test example
class TestDocumentProcessorIntegration:
    """Integration tests using real file samples"""
    
    @pytest.mark.integration
    def test_process_real_pdf(self, tmp_path):
        """
        Test with an actual PDF file.
        
        Note: This test requires test fixtures to be present
        """
        # This would use actual PDF files from tests/fixtures/
        pass
    
    @pytest.mark.integration
    def test_process_corrupted_files(self):
        """Test handling of corrupted files"""
        pass


# Performance test example
class TestDocumentProcessorPerformance:
    """Performance benchmarks for document processing"""
    
    @pytest.mark.benchmark
    def test_large_pdf_processing_time(self, benchmark, processor):
        """Benchmark PDF processing speed"""
        # Create a mock large PDF
        large_content = BytesIO(b"Large PDF content" * 1000)
        
        # Benchmark the extraction
        with patch('PyPDF2.PdfReader'):
            result = benchmark(processor.extract_pdf_text, large_content)