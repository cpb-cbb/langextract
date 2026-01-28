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

"""Tests for enhanced information extraction features.

This module tests the new byte interval and image coordinate functionality
added to support various document types (literature, bills, images, etc.).
"""

from absl.testing import absltest
from absl.testing import parameterized

from langextract import data
from langextract import data_lib


class ByteIntervalTest(absltest.TestCase):
  """Tests for ByteInterval functionality."""

  def test_byte_interval_creation(self):
    """Test creating a ByteInterval."""
    byte_interval = data.ByteInterval(start_pos=0, end_pos=10)
    self.assertEqual(byte_interval.start_pos, 0)
    self.assertEqual(byte_interval.end_pos, 10)

  def test_byte_interval_optional_fields(self):
    """Test ByteInterval with optional fields."""
    byte_interval = data.ByteInterval()
    self.assertIsNone(byte_interval.start_pos)
    self.assertIsNone(byte_interval.end_pos)


class ImageCoordinateTest(absltest.TestCase):
  """Tests for ImageCoordinate functionality."""

  def test_image_coordinate_creation(self):
    """Test creating an ImageCoordinate."""
    coord = data.ImageCoordinate(x=10.5, y=20.3, width=100.0, height=50.0)
    self.assertEqual(coord.x, 10.5)
    self.assertEqual(coord.y, 20.3)
    self.assertEqual(coord.width, 100.0)
    self.assertEqual(coord.height, 50.0)
    self.assertIsNone(coord.page)

  def test_image_coordinate_with_page(self):
    """Test ImageCoordinate with page number."""
    coord = data.ImageCoordinate(
        x=10.0, y=20.0, width=100.0, height=50.0, page=1
    )
    self.assertEqual(coord.page, 1)

  def test_image_coordinate_optional_fields(self):
    """Test ImageCoordinate with optional fields."""
    coord = data.ImageCoordinate()
    self.assertIsNone(coord.x)
    self.assertIsNone(coord.y)
    self.assertIsNone(coord.width)
    self.assertIsNone(coord.height)
    self.assertIsNone(coord.page)


class ExtractionWithNewFieldsTest(absltest.TestCase):
  """Tests for Extraction with byte_interval and image_coordinate fields."""

  def test_extraction_with_byte_interval(self):
    """Test Extraction with byte_interval."""
    byte_interval = data.ByteInterval(start_pos=100, end_pos=200)
    extraction = data.Extraction(
        extraction_class="document_header",
        extraction_text="Invoice #12345",
        byte_interval=byte_interval,
    )
    self.assertEqual(extraction.extraction_class, "document_header")
    self.assertEqual(extraction.extraction_text, "Invoice #12345")
    self.assertIsNotNone(extraction.byte_interval)
    self.assertEqual(extraction.byte_interval.start_pos, 100)
    self.assertEqual(extraction.byte_interval.end_pos, 200)

  def test_extraction_with_image_coordinate(self):
    """Test Extraction with image_coordinate."""
    image_coord = data.ImageCoordinate(
        x=50.0, y=100.0, width=200.0, height=150.0, page=1
    )
    extraction = data.Extraction(
        extraction_class="invoice_number",
        extraction_text="12345",
        image_coordinate=image_coord,
    )
    self.assertEqual(extraction.extraction_class, "invoice_number")
    self.assertEqual(extraction.extraction_text, "12345")
    self.assertIsNotNone(extraction.image_coordinate)
    self.assertEqual(extraction.image_coordinate.x, 50.0)
    self.assertEqual(extraction.image_coordinate.y, 100.0)
    self.assertEqual(extraction.image_coordinate.page, 1)

  def test_extraction_with_both_intervals(self):
    """Test Extraction with both char_interval and byte_interval."""
    char_interval = data.CharInterval(start_pos=10, end_pos=25)
    byte_interval = data.ByteInterval(start_pos=10, end_pos=25)
    extraction = data.Extraction(
        extraction_class="text_segment",
        extraction_text="Sample Text",
        char_interval=char_interval,
        byte_interval=byte_interval,
    )
    self.assertIsNotNone(extraction.char_interval)
    self.assertIsNotNone(extraction.byte_interval)
    self.assertEqual(extraction.char_interval.start_pos, 10)
    self.assertEqual(extraction.byte_interval.start_pos, 10)

  def test_extraction_backward_compatibility(self):
    """Test that existing code without new fields still works."""
    extraction = data.Extraction(
        extraction_class="entity",
        extraction_text="test",
        char_interval=data.CharInterval(start_pos=0, end_pos=4),
    )
    self.assertIsNone(extraction.byte_interval)
    self.assertIsNone(extraction.image_coordinate)


class AnnotatedDocumentWithNewFieldsTest(absltest.TestCase):
  """Tests for AnnotatedDocument with enhanced extractions."""

  def test_annotated_document_to_dict_with_byte_interval(self):
    """Test conversion to dict with byte_interval."""
    byte_interval = data.ByteInterval(start_pos=0, end_pos=15)
    extraction = data.Extraction(
        extraction_class="document_field",
        extraction_text="Invoice Number",
        byte_interval=byte_interval,
        extraction_index=1,
    )
    annotated_doc = data.AnnotatedDocument(
        document_id="doc1",
        text="Invoice Number: 12345",
        extractions=[extraction],
    )

    result_dict = data_lib.annotated_document_to_dict(annotated_doc)

    self.assertEqual(result_dict["document_id"], "doc1")
    self.assertEqual(len(result_dict["extractions"]), 1)
    self.assertIsNotNone(result_dict["extractions"][0]["byte_interval"])
    self.assertEqual(
        result_dict["extractions"][0]["byte_interval"]["start_pos"], 0
    )
    self.assertEqual(
        result_dict["extractions"][0]["byte_interval"]["end_pos"], 15
    )

  def test_annotated_document_to_dict_with_image_coordinate(self):
    """Test conversion to dict with image_coordinate."""
    image_coord = data.ImageCoordinate(
        x=100.0, y=200.0, width=300.0, height=150.0, page=2
    )
    extraction = data.Extraction(
        extraction_class="table",
        extraction_text="[Table Content]",
        image_coordinate=image_coord,
        extraction_index=1,
    )
    annotated_doc = data.AnnotatedDocument(
        document_id="doc2",
        text="Document with table",
        extractions=[extraction],
    )

    result_dict = data_lib.annotated_document_to_dict(annotated_doc)

    self.assertEqual(result_dict["document_id"], "doc2")
    self.assertEqual(len(result_dict["extractions"]), 1)
    self.assertIsNotNone(result_dict["extractions"][0]["image_coordinate"])
    self.assertEqual(result_dict["extractions"][0]["image_coordinate"]["x"], 100.0)
    self.assertEqual(
        result_dict["extractions"][0]["image_coordinate"]["page"], 2
    )

  def test_round_trip_with_byte_interval(self):
    """Test round-trip serialization/deserialization with byte_interval."""
    byte_interval = data.ByteInterval(start_pos=10, end_pos=25)
    original_extraction = data.Extraction(
        extraction_class="text_field",
        extraction_text="Sample Data",
        byte_interval=byte_interval,
        extraction_index=1,
        group_index=0,
    )
    original_doc = data.AnnotatedDocument(
        document_id="round_trip_1",
        text="Some sample data here",
        extractions=[original_extraction],
    )

    # Serialize to dict
    doc_dict = data_lib.annotated_document_to_dict(original_doc)

    # Deserialize back to AnnotatedDocument
    restored_doc = data_lib.dict_to_annotated_document(doc_dict)

    # Verify the round trip preserved all data
    self.assertEqual(restored_doc.document_id, original_doc.document_id)
    self.assertEqual(restored_doc.text, original_doc.text)
    self.assertEqual(len(restored_doc.extractions), 1)

    restored_extraction = restored_doc.extractions[0]
    self.assertEqual(
        restored_extraction.extraction_class,
        original_extraction.extraction_class,
    )
    self.assertEqual(
        restored_extraction.extraction_text,
        original_extraction.extraction_text,
    )
    self.assertIsNotNone(restored_extraction.byte_interval)
    self.assertEqual(
        restored_extraction.byte_interval.start_pos,
        original_extraction.byte_interval.start_pos,
    )
    self.assertEqual(
        restored_extraction.byte_interval.end_pos,
        original_extraction.byte_interval.end_pos,
    )

  def test_round_trip_with_image_coordinate(self):
    """Test round-trip serialization/deserialization with image_coordinate."""
    image_coord = data.ImageCoordinate(
        x=50.5, y=100.3, width=200.0, height=150.5, page=3
    )
    original_extraction = data.Extraction(
        extraction_class="image_region",
        extraction_text="Region Text",
        image_coordinate=image_coord,
        extraction_index=2,
        attributes={"confidence": "high"},
    )
    original_doc = data.AnnotatedDocument(
        document_id="round_trip_2",
        text="Document with image regions",
        extractions=[original_extraction],
    )

    # Serialize to dict
    doc_dict = data_lib.annotated_document_to_dict(original_doc)

    # Deserialize back to AnnotatedDocument
    restored_doc = data_lib.dict_to_annotated_document(doc_dict)

    # Verify the round trip preserved all data
    self.assertEqual(restored_doc.document_id, original_doc.document_id)
    self.assertEqual(len(restored_doc.extractions), 1)

    restored_extraction = restored_doc.extractions[0]
    self.assertIsNotNone(restored_extraction.image_coordinate)
    self.assertEqual(
        restored_extraction.image_coordinate.x,
        original_extraction.image_coordinate.x,
    )
    self.assertEqual(
        restored_extraction.image_coordinate.y,
        original_extraction.image_coordinate.y,
    )
    self.assertEqual(
        restored_extraction.image_coordinate.width,
        original_extraction.image_coordinate.width,
    )
    self.assertEqual(
        restored_extraction.image_coordinate.height,
        original_extraction.image_coordinate.height,
    )
    self.assertEqual(
        restored_extraction.image_coordinate.page,
        original_extraction.image_coordinate.page,
    )
    self.assertEqual(restored_extraction.attributes, original_extraction.attributes)

  def test_round_trip_with_both_byte_and_image(self):
    """Test round-trip with both byte_interval and image_coordinate."""
    byte_interval = data.ByteInterval(start_pos=0, end_pos=10)
    image_coord = data.ImageCoordinate(
        x=10.0, y=20.0, width=100.0, height=50.0, page=1
    )
    original_extraction = data.Extraction(
        extraction_class="complex_field",
        extraction_text="Complex",
        byte_interval=byte_interval,
        image_coordinate=image_coord,
        char_interval=data.CharInterval(start_pos=0, end_pos=7),
    )
    original_doc = data.AnnotatedDocument(
        document_id="round_trip_3",
        text="Complex data",
        extractions=[original_extraction],
    )

    # Round trip
    doc_dict = data_lib.annotated_document_to_dict(original_doc)
    restored_doc = data_lib.dict_to_annotated_document(doc_dict)

    # Verify all three interval types are preserved
    restored_extraction = restored_doc.extractions[0]
    self.assertIsNotNone(restored_extraction.char_interval)
    self.assertIsNotNone(restored_extraction.byte_interval)
    self.assertIsNotNone(restored_extraction.image_coordinate)
    self.assertEqual(
        restored_extraction.byte_interval.start_pos,
        original_extraction.byte_interval.start_pos,
    )
    self.assertEqual(
        restored_extraction.image_coordinate.x,
        original_extraction.image_coordinate.x,
    )


if __name__ == "__main__":
  absltest.main()
