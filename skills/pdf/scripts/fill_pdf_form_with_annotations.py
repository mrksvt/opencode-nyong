import json
import sys
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import FreeText

def transform_from_image_coords(bbox, image_width, image_height, pdf_width, pdf_height):
    x_scale = pdf_width / image_width
    y_scale = pdf_height / image_height
    
    left = bbox[0] * x_scale
    right = bbox[2] * x_scale
    top = pdf_height - (bbox[1] * y_scale)
    bottom = pdf_height - (bbox[3] * y_scale)
    
    return left, bottom, right, top

def transform_from_pdf_coords(bbox, pdf_height):
    left = bbox[0]
    right = bbox[2]
    pypdf_top = pdf_height - bbox[1]
    pypdf_bottom = pdf_height - bbox[3]
    return left, pypdf_bottom, right, pypdf_top

def fill_pdf_form(input_pdf_path, fields_json_path, output_pdf_path):
    with open(fields_json_path, "r") as f:
        fields_data = json.load(f)

    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()
    writer.append(reader)

    pdf_dimensions = {}
    for i, page in enumerate(reader.pages):
        mediabox = page.mediabox
        pdf_dimensions[i + 1] = [mediabox.width, mediabox.height]

    annotations = []
    for field in fields_data["form_fields"]:
        page_num = field["page_number"]
        page_info = next(p for p in fields_data["pages"] if p["page_number"] == page_num)
        pdf_width, pdf_height = pdf_dimensions[page_num]

        if "pdf_width" in page_info:
            transformed_entry_box = transform_from_pdf_coords(
                field["entry_bounding_box"],
                float(pdf_height)
            )
        else:
            image_width = page_info["image_width"]
            image_height = page_info["image_height"]
            transformed_entry_box = transform_from_image_coords(
                field["entry_bounding_box"],
                image_width,
                image_height,
                pdf_width,
                pdf_height
            )

        text = field["entry_text"]["text"]
        font_size = field["entry_text"].get("font_size", 14)
        
        annotation = FreeText(
            text=text,
            font_size=font_size,
            font="Helvetica",
            rectangle=transformed_entry_box,
            text_color=(0, 0, 0),
        )
        annotations.append((page_num, annotation))

    for page_num, annotation in annotations:
        writer.add_annotation(page_num - 1, annotation)

    with open(output_pdf_path, "wb") as f:
        writer.write(f)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: fill_pdf_form_with_annotations.py [input pdf] [fields.json] [output pdf]")
        sys.exit(1)
    fill_pdf_form(sys.argv[1], sys.argv[2], sys.argv[3])
