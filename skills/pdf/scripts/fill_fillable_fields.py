import json
import sys
from pypdf import PdfReader, PdfWriter

from extract_form_field_info import get_field_info

def fill_pdf_fields(input_pdf_path: str, fields_json_path: str, output_pdf_path: str):
    with open(fields_json_path) as f:
        fields = json.load(f)

    fields_by_page = {}
    for field in fields:
        if "value" in field:
            field_id = field["field_id"]
            page = field["page"]
            if page not in fields_by_page:
                fields_by_page[page] = {}
            fields_by_page[page][field_id] = field["value"]

    reader = PdfReader(input_pdf_path)
    has_error = False
    field_info = get_field_info(reader)
    fields_by_ids = {f["field_id"]: f for f in field_info}

    for field in fields:
        existing_field = fields_by_ids.get(field["field_id"])
        if not existing_field:
            has_error = True
            print(f"ERROR: `{field['field_id']}` is not a valid field ID")
        elif field["page"] != existing_field["page"]:
            has_error = True
            print(f"ERROR: Incorrect page number for `{field['field_id']}` (got {field['page']}, expected {existing_field['page']})")
        else:
            if "value" in field:
                err = validation_error_for_field_value(existing_field, field["value"])
                if err:
                    print(err)
                    has_error = True

    if has_error:
        sys.exit(1)

    writer = PdfWriter(clone_from=reader)
    for page, field_values in fields_by_page.items():
        writer.update_page_form_field_values(writer.pages[page - 1], field_values, auto_regenerate=False)
    writer.set_need_appearances_writer(True)
    with open(output_pdf_path, "wb") as f:
        writer.write(f)

def validation_error_for_field_value(field_info, field_value):
    field_type = field_info["type"]
    field_id = field_info["field_id"]
    if field_type == "checkbox":
        if field_value not in [field_info["checked_value"], field_info["unchecked_value"]]:
            return f"ERROR: For checkbox `{field_id}`, the value must be either `{field_info['checked_value']}` (checked) or `{field_info['unchecked_value']}` (unchecked), not `{field_value}`"
    elif field_type == "radio_group":
        valid_values = [option["value"] for option in field_info["radio_options"]]
        if field_value not in valid_values:
            return f"ERROR: For radio group `{field_id}`, the value must be one of {valid_values}, not `{field_value}`"
    elif field_type == "choice":
        valid_values = [option["value"] for option in field_info["choice_options"]]
        if field_value not in valid_values:
            return f"ERROR: For choice `{field_id}`, the value must be one of {valid_values}, not `{field_value}`"
    return None

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: fill_fillable_fields.py [input pdf] [fields.json] [output pdf]")
        sys.exit(1)
    fill_pdf_fields(sys.argv[1], sys.argv[2], sys.argv[3])
