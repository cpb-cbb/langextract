# Enhanced Information Extraction Features

LangExtract now supports advanced information extraction capabilities for various document types including literature, bills, images, and other structured/unstructured documents.

## Overview

The enhanced features include:

1. **Byte Position Tracking** - Track exact byte offsets in files for efficient binary data extraction
2. **Image Coordinates** - Extract bounding box coordinates for image-based document processing
3. **Flexible Extraction** - Combine text, byte positions, and image coordinates in a single extraction

## New Data Structures

### ByteInterval

Tracks byte positions in files or binary data:

```python
import langextract as lx

byte_interval = lx.data.ByteInterval(
    start_pos=100,  # Starting byte position (inclusive)
    end_pos=200     # Ending byte position (exclusive)
)
```

**Use Cases:**
- Binary file processing
- Large text file offset tracking
- Efficient data retrieval from files
- Memory-mapped file operations

### ImageCoordinate

Represents bounding boxes for image-based extractions:

```python
import langextract as lx

image_coord = lx.data.ImageCoordinate(
    x=50.0,        # X coordinate of top-left corner
    y=100.0,       # Y coordinate of top-left corner
    width=200.0,   # Width of bounding box
    height=150.0,  # Height of bounding box
    page=1         # Optional page number (for multi-page docs)
)
```

**Use Cases:**
- OCR post-processing
- Document image analysis
- Invoice/bill field extraction
- Form processing
- Image region cropping and extraction

## Enhanced Extraction Class

The `Extraction` class now supports optional byte intervals and image coordinates:

```python
import langextract as lx

# Extraction with byte positions
extraction = lx.data.Extraction(
    extraction_class="invoice_number",
    extraction_text="INV-12345",
    byte_interval=lx.data.ByteInterval(start_pos=0, end_pos=9)
)

# Extraction with image coordinates
extraction = lx.data.Extraction(
    extraction_class="total_amount",
    extraction_text="$1,250.00",
    image_coordinate=lx.data.ImageCoordinate(
        x=400.0, y=500.0, width=100.0, height=25.0, page=1
    )
)

# Combined extraction (text position + image coordinate)
extraction = lx.data.Extraction(
    extraction_class="patient_name",
    extraction_text="John Doe",
    char_interval=lx.data.CharInterval(start_pos=9, end_pos=17),
    image_coordinate=lx.data.ImageCoordinate(
        x=120.0, y=45.0, width=80.0, height=20.0
    ),
    attributes={
        "field_type": "patient_identifier",
        "confidence": "high"
    }
)
```

## Usage Examples

### Example 1: Invoice Processing with Image Coordinates

```python
import langextract as lx

# Simulate OCR output with bounding boxes
extractions = [
    lx.data.Extraction(
        extraction_class="invoice_number",
        extraction_text="INV-2024-001",
        image_coordinate=lx.data.ImageCoordinate(
            x=100.0, y=50.0, width=150.0, height=30.0, page=1
        )
    ),
    lx.data.Extraction(
        extraction_class="total_amount",
        extraction_text="$1,250.00",
        image_coordinate=lx.data.ImageCoordinate(
            x=400.0, y=500.0, width=100.0, height=25.0, page=1
        )
    )
]

# Create annotated document
doc = lx.data.AnnotatedDocument(
    document_id="invoice_001",
    text="Invoice content...",
    extractions=extractions
)

# Save for later processing
lx.io.save_annotated_documents([doc], output_name="invoices.jsonl")
```

### Example 2: Binary File Extraction with Byte Positions

```python
import langextract as lx

# Track byte positions for efficient file reading
extraction = lx.data.Extraction(
    extraction_class="document_header",
    extraction_text="PDF-1.7",
    byte_interval=lx.data.ByteInterval(start_pos=0, end_pos=7),
    char_interval=lx.data.CharInterval(start_pos=0, end_pos=7)
)

# Later, you can use these byte positions to extract directly from file
with open("document.pdf", "rb") as f:
    f.seek(extraction.byte_interval.start_pos)
    data = f.read(
        extraction.byte_interval.end_pos - extraction.byte_interval.start_pos
    )
```

### Example 3: Medical Records with Combined Extraction

```python
import langextract as lx

# Extract patient information from scanned medical record
extraction = lx.data.Extraction(
    extraction_class="patient_name",
    extraction_text="Jane Smith",
    char_interval=lx.data.CharInterval(start_pos=9, end_pos=19),
    image_coordinate=lx.data.ImageCoordinate(
        x=120.0, y=45.0, width=100.0, height=20.0, page=1
    ),
    attributes={
        "field_type": "patient_identifier",
        "confidence": "0.95"
    }
)

# This allows both text search and visual highlighting
```

## Serialization

All new fields are fully supported in JSON serialization:

```python
import langextract as lx
import json

# Create document with enhanced extractions
doc = lx.data.AnnotatedDocument(
    document_id="doc_001",
    text="Document text...",
    extractions=[
        lx.data.Extraction(
            extraction_class="field",
            extraction_text="value",
            byte_interval=lx.data.ByteInterval(start_pos=0, end_pos=5),
            image_coordinate=lx.data.ImageCoordinate(
                x=10.0, y=20.0, width=50.0, height=30.0
            )
        )
    ]
)

# Convert to dictionary
doc_dict = lx.data_lib.annotated_document_to_dict(doc)

# Save as JSON
with open("output.json", "w") as f:
    json.dump(doc_dict, f, indent=2)

# Load from JSON
with open("output.json", "r") as f:
    loaded_dict = json.load(f)
    loaded_doc = lx.data_lib.dict_to_annotated_document(loaded_dict)
```

## Backward Compatibility

All new fields are **optional** and maintain full backward compatibility:

- Existing code works without modifications
- Old serialized documents can be loaded without issues
- New fields are only included when explicitly set
- None values are properly handled

## Integration with OCR Systems

These features integrate well with OCR systems:

```python
import langextract as lx

def process_ocr_output(ocr_result):
    """Convert OCR output to LangExtract extractions."""
    extractions = []
    
    for word in ocr_result['words']:
        extraction = lx.data.Extraction(
            extraction_class="ocr_word",
            extraction_text=word['text'],
            image_coordinate=lx.data.ImageCoordinate(
                x=word['bbox']['x'],
                y=word['bbox']['y'],
                width=word['bbox']['width'],
                height=word['bbox']['height'],
                page=word.get('page', 1)
            ),
            attributes={
                "confidence": str(word['confidence'])
            }
        )
        extractions.append(extraction)
    
    return extractions
```

## Use Cases

These features are designed for:

1. **Document Processing Systems**
   - Invoice extraction and processing
   - Bill parsing and analysis
   - Form field extraction

2. **Literature Information Extraction**
   - Academic paper processing
   - Book content extraction
   - Document structure analysis

3. **Medical Records Processing**
   - Clinical note extraction
   - Lab report parsing
   - Medical form processing

4. **Image-based Document Analysis**
   - Scanned document processing
   - OCR result post-processing
   - Multi-modal document understanding

5. **Binary Data Extraction**
   - Large file processing
   - Memory-efficient data extraction
   - File format parsing

## Best Practices

1. **Use Image Coordinates for Visual Documents**
   - Essential for document layout understanding
   - Enables visual highlighting and validation
   - Supports image cropping and extraction

2. **Track Byte Positions for Large Files**
   - More efficient than loading entire file
   - Enables random access to file content
   - Useful for memory-constrained environments

3. **Combine Multiple Position Types**
   - Use both char_interval and image_coordinate when available
   - Provides flexibility in downstream processing
   - Enables cross-validation of extraction accuracy

4. **Include Metadata in Attributes**
   - Add confidence scores
   - Include processing hints
   - Store source information

## Running the Examples

See the complete working examples:

```bash
python examples/information_extraction_example.py
```

This will demonstrate:
- Byte position extraction
- Image coordinate extraction
- Combined extraction approaches
- Document serialization

## API Reference

For detailed API documentation, see:
- `langextract.data.ByteInterval`
- `langextract.data.ImageCoordinate`
- `langextract.data.Extraction`
- `langextract.data.AnnotatedDocument`
