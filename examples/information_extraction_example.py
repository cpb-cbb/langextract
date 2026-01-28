# Copyright 2025 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Example demonstrating information extraction with byte positions and image coordinates.

This example shows how to use the enhanced LangExtract features for:
1. Extracting text with byte positions (useful for binary data or file offsets)
2. Extracting image coordinates (useful for document image processing, OCR, etc.)
3. Mixed extractions combining text and spatial information

These features are particularly useful for:
- Document processing (invoices, bills, forms)
- Literature information extraction
- Image-based document analysis
- OCR post-processing
"""

import langextract as lx


def example_byte_position_extraction():
  """Example: Extract information with byte positions.

  This is useful when working with binary files or when you need exact byte
  offsets in a file for efficient data retrieval.
  """
  print("=" * 70)
  print("Example 1: Byte Position Extraction")
  print("=" * 70)

  # Simulate a document with binary data (e.g., from a file)
  text_content = "Invoice #12345\nDate: 2024-01-15\nTotal: $1,250.00"

  # Create an extraction with byte positions
  # In a real scenario, these would be calculated from file offsets
  extraction = lx.data.Extraction(
      extraction_class="invoice_number",
      extraction_text="12345",
      char_interval=lx.data.CharInterval(start_pos=9, end_pos=14),
      byte_interval=lx.data.ByteInterval(start_pos=9, end_pos=14),
  )

  print(f"Text: {text_content}")
  print(f"\nExtraction: {extraction.extraction_text}")
  print(f"Character position: {extraction.char_interval.start_pos} - "
        f"{extraction.char_interval.end_pos}")
  print(f"Byte position: {extraction.byte_interval.start_pos} - "
        f"{extraction.byte_interval.end_pos}")
  print()


def example_image_coordinate_extraction():
  """Example: Extract information with image coordinates.

  This is useful for document image processing where you need to know the
  spatial location of extracted text for highlighting, cropping, or further
  analysis.
  """
  print("=" * 70)
  print("Example 2: Image Coordinate Extraction")
  print("=" * 70)

  # Simulate an OCR'd invoice where we know the bounding boxes
  # In a real scenario, these would come from an OCR engine
  extractions = [
      lx.data.Extraction(
          extraction_class="invoice_number",
          extraction_text="INV-2024-001",
          image_coordinate=lx.data.ImageCoordinate(
              x=100.0,
              y=50.0,
              width=150.0,
              height=30.0,
              page=1,
          ),
      ),
      lx.data.Extraction(
          extraction_class="total_amount",
          extraction_text="$1,250.00",
          image_coordinate=lx.data.ImageCoordinate(
              x=400.0,
              y=500.0,
              width=100.0,
              height=25.0,
              page=1,
          ),
      ),
      lx.data.Extraction(
          extraction_class="vendor_name",
          extraction_text="ACME Corporation",
          image_coordinate=lx.data.ImageCoordinate(
              x=50.0,
              y=100.0,
              width=200.0,
              height=40.0,
              page=1,
          ),
      ),
  ]

  print("Extracted fields from invoice image:\n")
  for ext in extractions:
    coord = ext.image_coordinate
    print(f"{ext.extraction_class}: {ext.extraction_text}")
    print(f"  Location: ({coord.x}, {coord.y}), "
          f"Size: {coord.width}x{coord.height}, "
          f"Page: {coord.page}")
    print()


def example_combined_extraction():
  """Example: Combined extraction with multiple position types.

  This demonstrates how to track both character positions (for text processing)
  and image coordinates (for visual highlighting) simultaneously.
  """
  print("=" * 70)
  print("Example 3: Combined Extraction (Text + Image Coordinates)")
  print("=" * 70)

  text_content = "Patient: John Doe\nDiagnosis: Hypertension\nDate: 2024-01-15"

  # In a real medical records system, you might extract from both the text
  # and the scanned document image
  extraction = lx.data.Extraction(
      extraction_class="patient_name",
      extraction_text="John Doe",
      char_interval=lx.data.CharInterval(start_pos=9, end_pos=17),
      image_coordinate=lx.data.ImageCoordinate(
          x=120.0,
          y=45.0,
          width=80.0,
          height=20.0,
          page=1,
      ),
      attributes={
          "field_type": "patient_identifier",
          "confidence": "high",
      },
  )

  annotated_doc = lx.data.AnnotatedDocument(
      document_id="medical_record_001",
      text=text_content,
      extractions=[extraction],
  )

  print(f"Document: {annotated_doc.document_id}")
  print(f"Text:\n{text_content}\n")
  print(f"Extracted: {extraction.extraction_text}")
  print(f"  Text position: chars {extraction.char_interval.start_pos}-"
        f"{extraction.char_interval.end_pos}")
  print(f"  Image position: ({extraction.image_coordinate.x}, "
        f"{extraction.image_coordinate.y}) "
        f"{extraction.image_coordinate.width}x{extraction.image_coordinate.height}")
  print(f"  Attributes: {extraction.attributes}")
  print()


def example_document_with_serialization():
  """Example: Creating and serializing a document with enhanced features."""
  print("=" * 70)
  print("Example 4: Document Serialization")
  print("=" * 70)

  # Create a document with various extraction types
  extractions = [
      lx.data.Extraction(
          extraction_class="header",
          extraction_text="Invoice",
          byte_interval=lx.data.ByteInterval(start_pos=0, end_pos=7),
          image_coordinate=lx.data.ImageCoordinate(
              x=50.0, y=20.0, width=100.0, height=30.0
          ),
      ),
      lx.data.Extraction(
          extraction_class="date",
          extraction_text="2024-01-15",
          char_interval=lx.data.CharInterval(start_pos=8, end_pos=18),
      ),
  ]

  annotated_doc = lx.data.AnnotatedDocument(
      document_id="doc_001",
      text="Invoice 2024-01-15 Total: $500",
      extractions=extractions,
  )

  # Convert to dictionary (for JSON serialization)
  doc_dict = lx.data_lib.annotated_document_to_dict(annotated_doc)

  print("Serialized document:")
  import json
  print(json.dumps(doc_dict, indent=2))
  print()


def main():
  """Run all examples."""
  print("\n" + "=" * 70)
  print("LangExtract Enhanced Information Extraction Examples")
  print("=" * 70 + "\n")

  example_byte_position_extraction()
  example_image_coordinate_extraction()
  example_combined_extraction()
  example_document_with_serialization()

  print("=" * 70)
  print("Examples completed!")
  print("=" * 70)


if __name__ == "__main__":
  main()
