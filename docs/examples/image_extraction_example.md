# Image Extraction and Splitting Example

This example demonstrates how to use LangExtract's enhanced features for image-based document processing, specifically for extracting and splitting image regions.

## Use Case: Invoice Processing

When processing scanned invoices or bills, you often need to:
1. Extract text from specific regions
2. Know the exact coordinates of each field
3. Optionally crop/split the image into separate fields

## Example Code

```python
import langextract as lx

# Simulated OCR results from an invoice image
# In a real scenario, these would come from an OCR engine like Tesseract
invoice_extractions = [
    lx.data.Extraction(
        extraction_class="invoice_header",
        extraction_text="INVOICE",
        image_coordinate=lx.data.ImageCoordinate(
            x=200.0,      # Top-left X coordinate
            y=50.0,       # Top-left Y coordinate
            width=150.0,  # Width of the region
            height=40.0,  # Height of the region
            page=1        # Page number (for multi-page docs)
        ),
        attributes={
            "font_size": "24",
            "alignment": "center"
        }
    ),
    lx.data.Extraction(
        extraction_class="invoice_number",
        extraction_text="INV-2024-001",
        image_coordinate=lx.data.ImageCoordinate(
            x=100.0, y=120.0, width=180.0, height=30.0, page=1
        )
    ),
    lx.data.Extraction(
        extraction_class="date",
        extraction_text="2024-01-15",
        image_coordinate=lx.data.ImageCoordinate(
            x=400.0, y=120.0, width=120.0, height=30.0, page=1
        )
    ),
    lx.data.Extraction(
        extraction_class="vendor_name",
        extraction_text="ACME Corporation",
        image_coordinate=lx.data.ImageCoordinate(
            x=100.0, y=180.0, width=250.0, height=35.0, page=1
        )
    ),
    lx.data.Extraction(
        extraction_class="total_amount",
        extraction_text="$1,250.00",
        image_coordinate=lx.data.ImageCoordinate(
            x=450.0, y=500.0, width=100.0, height=30.0, page=1
        ),
        attributes={
            "field_type": "monetary",
            "currency": "USD"
        }
    )
]

# Create an annotated document
invoice_doc = lx.data.AnnotatedDocument(
    document_id="invoice_2024_001",
    text="Full text representation of invoice...",
    extractions=invoice_extractions
)

# Save for later processing
lx.io.save_annotated_documents([invoice_doc], output_name="invoices.jsonl")
```

## Using Coordinates for Image Splitting

With the extracted coordinates, you can now crop specific regions from the original image:

```python
from PIL import Image

def crop_extraction_from_image(image_path, extraction):
    """Crop an image region based on extraction coordinates."""
    coord = extraction.image_coordinate
    if coord is None:
        return None
    
    # Open the original image
    img = Image.open(image_path)
    
    # Crop using the bounding box (left, top, right, bottom)
    cropped = img.crop((
        coord.x,
        coord.y,
        coord.x + coord.width,
        coord.y + coord.height
    ))
    
    return cropped

# Example: Extract the invoice number region
invoice_img = Image.open("invoice_scan.jpg")
invoice_num_extraction = invoice_extractions[1]  # Invoice number
cropped_invoice_num = crop_extraction_from_image(
    "invoice_scan.jpg",
    invoice_num_extraction
)
cropped_invoice_num.save("extracted_invoice_number.jpg")
```

## Real-World Workflow

### 1. Process Document with OCR
```python
# Using an OCR engine (pseudocode)
ocr_results = ocr_engine.process("invoice.jpg")

# Convert OCR results to LangExtract extractions
extractions = []
for word in ocr_results:
    extraction = lx.data.Extraction(
        extraction_class="ocr_word",
        extraction_text=word.text,
        image_coordinate=lx.data.ImageCoordinate(
            x=word.bbox.x,
            y=word.bbox.y,
            width=word.bbox.width,
            height=word.bbox.height
        ),
        attributes={
            "confidence": str(word.confidence)
        }
    )
    extractions.append(extraction)
```

### 2. Apply Business Logic
```python
# Use LLM or rules to classify and structure the data
# Then create structured extractions with maintained coordinates
structured_extractions = classify_and_structure(extractions)
```

### 3. Export for Downstream Processing
```python
# Save with coordinates for visual verification
doc = lx.data.AnnotatedDocument(
    document_id="invoice_001",
    extractions=structured_extractions
)

# Generate visualization
html = lx.visualize("invoices.jsonl")
# This could be enhanced to show the original image with overlays
```

## Benefits

1. **Visual Verification**: Coordinates allow you to highlight extracted fields on the original image
2. **Field Extraction**: Crop specific regions for further processing
3. **Quality Control**: Visual inspection of extraction accuracy
4. **Data Validation**: Compare extracted text with image region
5. **Archive Creation**: Split documents into individual fields for archival

## Integration with Document Processing Pipelines

```python
class InvoiceProcessor:
    def __init__(self, ocr_engine, llm_classifier):
        self.ocr = ocr_engine
        self.llm = llm_classifier
    
    def process_invoice(self, image_path):
        # Step 1: OCR
        ocr_results = self.ocr.process(image_path)
        
        # Step 2: Convert to LangExtract format
        extractions = self._convert_ocr_to_extractions(ocr_results)
        
        # Step 3: Classify and structure
        doc = lx.data.AnnotatedDocument(
            document_id=f"invoice_{timestamp}",
            extractions=extractions
        )
        
        # Step 4: Extract specific fields by class
        invoice_number = self._find_by_class(doc, "invoice_number")
        total_amount = self._find_by_class(doc, "total_amount")
        
        # Step 5: Optionally crop images for verification
        if invoice_number and invoice_number.image_coordinate:
            self._crop_and_save(
                image_path,
                invoice_number.image_coordinate,
                f"invoice_number_{doc.document_id}.jpg"
            )
        
        return doc
    
    def _find_by_class(self, doc, extraction_class):
        for ext in doc.extractions:
            if ext.extraction_class == extraction_class:
                return ext
        return None
```

## Multi-Page Documents

For documents with multiple pages:

```python
# Extract from different pages
page1_extraction = lx.data.Extraction(
    extraction_class="header",
    extraction_text="Page 1 Header",
    image_coordinate=lx.data.ImageCoordinate(
        x=100, y=50, width=400, height=40, page=1
    )
)

page2_extraction = lx.data.Extraction(
    extraction_class="footer",
    extraction_text="Page 2 Footer",
    image_coordinate=lx.data.ImageCoordinate(
        x=100, y=750, width=400, height=30, page=2
    )
)

# The 'page' field helps you know which page to load/crop
```

## Conclusion

The enhanced LangExtract features enable sophisticated document processing workflows that combine text extraction with spatial information, making it ideal for invoice processing, form extraction, and document digitization projects.
