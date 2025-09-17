import fitz  # PyMuPDF
import os
import camelot
import re
from typing import Dict, List, Any, Optional

class PDFParser:
    """
    A stateful parser designed to extract structured content (text, tables, charts)
    from a PDF file. It maintains the document's hierarchy by tracking sections
    and subsections as it processes each page.
    """
    def __init__(self):
        # These attributes track the current section/subsection context while parsing.
        self.current_section: str = "Default"
        self.current_sub_section: Optional[str] = None

    def get_text_style(self, span: Dict) -> str:
        """
        Analyzes a text span to heuristically determine its style (e.g., heading, paragraph).
        This is a rule-based approach that uses font size and weight.

        Returns:
            A string representing the style: 'h1', 'h2', or 'p' (paragraph).
        """
        font_size = round(span['size'])
        is_bold = "bold" in span['font'].lower()

        # Heuristic rules: Larger text is likely a top-level heading (h1).
        # Bolded text of a reasonable size is likely a sub-heading (h2).
        if font_size > 15:
            return 'h1'
        if font_size >= 12 and is_bold:
            return 'h2'
        if font_size > 12: # Also consider non-bold text as h2 if large enough
            return 'h2'
        return 'p'

    def extract_clean_text(self, block: Dict) -> str:
        """
        Extracts and cleans text from a PyMuPDF text block, preserving paragraph breaks.
        """
        full_text = ""
        for line in block.get('lines', []):
            line_text = "".join(span.get('text', '') for span in line.get('spans', []))
            full_text += line_text.strip() + "\n"
        
        # Consolidate multiple spaces and clean up whitespace.
        return full_text.strip()

    def extract_tables(self, pdf_path: str, page_num: int, page_height: float) -> tuple:
        """
        Finds and extracts all tables on a given page using the Camelot library.

        Returns:
            A tuple containing:
            - A list of dictionaries, where each dict represents a found table.
            - A list of bounding boxes for those tables to avoid re-processing their text.
        """
        tables_data = []
        ignore_bboxes = []
        
        try:
            # 'stream' flavor is good for PDFs where tables don't have clear lines.
            tables = camelot.read_pdf(pdf_path, pages=str(page_num + 1), flavor='stream', edge_tol=500)
            
            for table in tables:
                # --- Filter out false positives ---
                # Skip if it's just a single column, which is likely a paragraph.
                if table.df.shape[1] <= 1:
                    continue
                # Skip if it has many rows but few columns, often a sign of a list or menu.
                if table.df.shape[0] > 10 and table.df.shape[1] < 3:
                    continue

                # --- Coordinate Conversion ---
                # Camelot's y-coordinates start from the top, PyMuPDF's from the bottom.
                # We need to convert them to PyMuPDF's system to create an accurate bounding box.
                x1, y1_camelot, x2, y2_camelot = table._bbox
                y1 = page_height - y2_camelot
                y2 = page_height - y1_camelot
                
                table_bbox = fitz.Rect(x1, y1, x2, y2)
                ignore_bboxes.append(table_bbox)
                
                # --- Clean and Structure Table Data ---
                # Convert the pandas DataFrame to a list of lists and clean each cell.
                cleaned_table_data = [
                    [str(cell).strip() for cell in row if str(cell).strip()]
                    for row in table.df.values.tolist()
                ]
                
                # Only keep rows that are not empty after cleaning.
                final_table_data = [row for row in cleaned_table_data if row]
                
                # Add the table to our results if it has content.
                if final_table_data:
                    tables_data.append({
                        "type": "table",
                        "bbox": tuple(table_bbox),
                        "section": self.current_section,
                        "sub_section": self.current_sub_section,
                        "table_data": final_table_data
                    })
                    
        except Exception as e:
            # Silently fail if Camelot can't find tables, which is common.
            # You can add logging here if you want to debug.
            pass
        
        return tables_data, ignore_bboxes

    def extract_images(self, page: fitz.Page) -> tuple:
        """
        Finds and extracts all images (which can often be charts) on a page.
        
        Returns:
            A tuple containing:
            - A list of dictionaries, where each dict represents a found image/chart.
            - A list of bounding boxes for those images to avoid re-processing overlapping text.
        """
        images_data = []
        ignore_bboxes = []
        
        for img_index, img in enumerate(page.get_images(full=True)):
            bbox = page.get_image_bbox(img)
            if bbox.is_empty:
                continue
            
            ignore_bboxes.append(bbox)
            images_data.append({
                "type": "chart", # Assume images are charts for this task's purpose.
                "bbox": tuple(bbox),
                "section": self.current_section,
                "sub_section": self.current_sub_section,
                "description": f"Chart or image found on page {page.number + 1}"
            })
        
        return images_data, ignore_bboxes

    def extract_text_blocks(self, page: fitz.Page, ignore_bboxes: List[fitz.Rect]) -> List[Dict]:
        """
        Extracts text from the page, skipping any text that falls within the
        bounding boxes of previously identified tables or images.
        """
        text_blocks = []
        blocks = page.get_text("dict").get("blocks", [])
        
        for block in blocks:
            if block.get('type') != 0:  # This block is not a text block.
                continue
                
            block_rect = fitz.Rect(block['bbox'])
            # Check if this text block overlaps with any area we want to ignore.
            if any(bbox.intersects(block_rect) for bbox in ignore_bboxes):
                continue

            cleaned_text = self.extract_clean_text(block)
            if not cleaned_text:
                continue

            # Identify the style of the block to determine if it's a heading or paragraph.
            # We use the style of the first line/span as representative of the whole block.
            main_style = 'p'
            if block.get('lines') and block['lines'][0].get('spans'):
                main_style = self.get_text_style(block['lines'][0]['spans'][0])
            
            content_item = {
                "bbox": block['bbox'],
                "text": cleaned_text
            }

            # Update the section/subsection hierarchy based on heading styles.
            if main_style == 'h1':
                self.current_section = cleaned_text
                self.current_sub_section = None # Reset subsection on a new main section.
                content_item['type'] = 'paragraph' # Treat as paragraph in output as per requirement
            elif main_style == 'h2':
                self.current_sub_section = cleaned_text
                content_item['type'] = 'paragraph' # Treat as paragraph
            else:
                content_item['type'] = 'paragraph'
            
            content_item["section"] = self.current_section
            content_item["sub_section"] = self.current_sub_section
            text_blocks.append(content_item)
        
        return text_blocks

    def parse_page(self, doc: fitz.Document, page_num: int) -> List[Dict]:
        """Orchestrates the parsing of a single page."""
        page = doc[page_num]
        page_height = page.rect.height
        
        # Step 1: Extract tables and their locations.
        tables_data, table_bboxes = self.extract_tables(doc.name, page_num, page_height)
        
        # Step 2: Extract images/charts and their locations.
        images_data, image_bboxes = self.extract_images(page)
        
        # Step 3: Combine all areas to ignore for the final text pass.
        ignore_bboxes = table_bboxes + image_bboxes
        
        # Step 4: Extract the remaining text content.
        text_content = self.extract_text_blocks(page, ignore_bboxes)
        
        # Combine all extracted content for this page.
        all_content = tables_data + images_data + text_content
        
        # Sort all content by its vertical position (top-to-bottom) to ensure a natural reading order.
        sorted_content = sorted(all_content, key=lambda item: item.get('bbox', (0, 0, 0, 0))[1])
        
        # Final cleanup: remove the temporary 'bbox' key before finalizing the output.
        for item in sorted_content:
            if 'bbox' in item:
                del item['bbox']
                
        return sorted_content

    def parse(self, pdf_path: str) -> Optional[Dict]:
        """
        The main public method to parse a PDF file and return its structured content.
        """
        if not os.path.exists(pdf_path):
            print(f"Error: The file '{pdf_path}' was not found.")
            return None

        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            print(f"Error opening or processing the PDF file: {e}")
            return None

        print("Parsing process started...")
        
        output_data = {
            "file_path": pdf_path,
            "total_pages": len(doc),
            "pages": []
        }

        for page_num in range(len(doc)):
            page_content = self.parse_page(doc, page_num)
            output_data["pages"].append({
                "page_number": page_num + 1,
                "content": page_content
            })

        doc.close()
        print("Parsing process finished.")
        return output_data

def parse_pdf(pdf_path: str) -> Optional[Dict]:
    """
    A simple, public-facing function to instantiate and run the PDFParser.
    This keeps the main script clean and separates the class logic.
    """
    parser = PDFParser()
    return parser.parse(pdf_path)