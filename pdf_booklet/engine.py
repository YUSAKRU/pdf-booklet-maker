import os
import fitz
from pdf_booklet.exceptions import BookletError, LayoutError, PDFCorruptedError
from pdf_booklet.logger import get_logger
from pdf_booklet.validator import PDFValidator

logger = get_logger()

class BookletEngine:
    """Core booklet imposition engine that generates front and back PDFs."""

    def __init__(self, target_width: float = 842.0, target_height: float = 595.0):
        """
        Initializes the booklet engine.
        
        Args:
            target_width: Width of target sheet (default: 842.0 points, standard A4 Landscape).
            target_height: Height of target sheet (default: 595.0 points, standard A4 Landscape).
        """
        self.target_width = target_width
        self.target_height = target_height
        self.w_slot = target_width / 2.0
        self.h_slot = target_height

    def make_booklet(self, input_path: str, output_dir: str, base_gutter: float = 0.0, creep_step: float = 0.0) -> dict:
        """
        Performs the booklet imposition process.
        
        Args:
            input_path: Path to the input PDF file.
            output_dir: Directory where the output files will be written.
            base_gutter: Base folding margin in points between left and right pages.
            creep_step: Creep compensation displacement per sheet in points.
            
        Returns:
            dict: Processing summary and output file paths.
        """
        # 1. Validate the input document
        metadata = PDFValidator.validate(input_path)
        original_page_count = metadata["page_count"]
        
        # Extract name of the document
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        
        # Check if output directory exists, if not create it
        os.makedirs(output_dir, exist_ok=True)
        
        front_output_path = os.path.join(output_dir, f"{base_name}_front.pdf")
        back_output_path = os.path.join(output_dir, f"{base_name}_back.pdf")

        logger.info("Starting booklet imposition", details={
            "input_path": input_path,
            "output_dir": output_dir,
            "base_gutter": base_gutter,
            "creep_step": creep_step,
            "target_size": f"{self.target_width}x{self.target_height}"
        })

        try:
            # Open document
            src_doc = fitz.open(input_path)
        except Exception as e:
            logger.error("Failed to open source PDF during processing", details={"input_path": input_path, "error": str(e)})
            raise PDFCorruptedError(f"Failed to open source PDF: {str(e)}")

        try:
            # 2. Dynamic Blank Page Padding
            # If N % 4 != 0, add empty pages matching the size of the last page
            remainder = original_page_count % 4
            padding_applied = 0
            if remainder != 0:
                padding_applied = 4 - remainder
                last_page = src_doc.load_page(original_page_count - 1)
                last_w = last_page.rect.width
                last_h = last_page.rect.height
                
                logger.info("Applying dynamic page padding to align to 4-page boundary", details={
                    "original_page_count": original_page_count,
                    "padding_applied": padding_applied,
                    "target_page_count": original_page_count + padding_applied
                })
                
                for _ in range(padding_applied):
                    src_doc.insert_page(-1, width=last_w, height=last_h)
            
            N = len(src_doc)
            S = N // 4
            
            # Anomaly check: Warn if input contains landscape pages
            landscape_pages = [idx for idx, size in enumerate(metadata["page_sizes"]) if size[0] > size[1]]
            if landscape_pages:
                logger.warning("Input PDF contains landscape pages, which might affect booklet layout scaling", details={
                    "landscape_page_indices": landscape_pages[:10],
                    "total_landscape_pages": len(landscape_pages)
                })

            # 3. Create target documents
            front_doc = fitz.open()
            back_doc = fitz.open()

            # Process sheet-by-sheet
            for j in range(S):
                # 0-based sheet index is j, 1-based is i = j + 1
                # Calculate front and back pages
                front_left_idx = N - 2 * j - 1
                front_right_idx = 2 * j
                back_left_idx = 2 * j + 1
                back_right_idx = N - 2 * j - 2

                # Calculate gutter and creep shifts
                c_i = j * creep_step
                g_i = base_gutter
                shift_inward = c_i - (g_i / 2.0)

                # Safety check for shifts
                max_safe_shift = self.w_slot * 0.15
                if abs(shift_inward) > max_safe_shift:
                    logger.warning("Large gutter/creep shift detected, potential layout overlap or clipping", details={
                        "sheet_index": j,
                        "shift_inward": shift_inward,
                        "max_safe_shift": max_safe_shift
                    })

                # Create destination Rects
                # Left slot shifted: positive shift moves it right (towards center)
                left_rect = fitz.Rect(shift_inward, 0.0, self.w_slot + shift_inward, self.h_slot)
                # Right slot shifted: positive shift moves it left (towards center)
                right_rect = fitz.Rect(self.w_slot - shift_inward, 0.0, self.target_width - shift_inward, self.h_slot)

                # Add new page to front doc
                front_page = front_doc.new_page(width=self.target_width, height=self.target_height)
                # Show left page
                front_page.show_pdf_page(left_rect, src_doc, front_left_idx, keep_proportion=True)
                # Show right page
                front_page.show_pdf_page(right_rect, src_doc, front_right_idx, keep_proportion=True)

                # Add new page to back doc
                back_page = back_doc.new_page(width=self.target_width, height=self.target_height)
                # Show left page
                back_page.show_pdf_page(left_rect, src_doc, back_left_idx, keep_proportion=True)
                # Show right page
                back_page.show_pdf_page(right_rect, src_doc, back_right_idx, keep_proportion=True)

            # 4. Save documents
            try:
                front_doc.save(front_output_path)
                back_doc.save(back_output_path)
            except Exception as e:
                logger.error("Failed to save output booklet PDFs", details={"error": str(e)})
                raise LayoutError(f"Failed to write booklet PDFs to disk: {str(e)}")

            # 5. Clean up
            front_doc.close()
            back_doc.close()
            
            result = {
                "status": "success",
                "original_pages": original_page_count,
                "padded_pages": N,
                "sheets_count": S,
                "front_pdf": front_output_path,
                "back_pdf": back_output_path,
                "padding_applied": padding_applied
            }
            
            logger.info("Booklet imposition completed successfully", details=result)
            return result

        finally:
            src_doc.close()
