"""Unpack Office files (DOCX, PPTX, XLSX) for editing."""

import argparse, sys, zipfile
from pathlib import Path
import defusedxml.minidom

SMART_QUOTE_REPLACEMENTS = {"\u201c": "&#x201C;", "\u201d": "&#x201D;", "\u2018": "&#x2018;", "\u2019": "&#x2019;"}

def unpack(input_file, output_directory):
    input_path, output_path = Path(input_file), Path(output_directory)
    suffix = input_path.suffix.lower()
    if not input_path.exists():
        return None, f"Error: {input_file} does not exist"
    if suffix not in {".docx", ".pptx", ".xlsx"}:
        return None, f"Error: {input_file} must be a .docx, .pptx, or .xlsx file"
    try:
        output_path.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(input_path, "r") as zf:
            zf.extractall(output_path)
        xml_files = list(output_path.rglob("*.xml")) + list(output_path.rglob("*.rels"))
        for xml_file in xml_files:
            try:
                content = xml_file.read_text(encoding="utf-8")
                dom = defusedxml.minidom.parseString(content)
                xml_file.write_bytes(dom.toprettyxml(indent="  ", encoding="utf-8"))
            except Exception:
                pass
            try:
                content = xml_file.read_text(encoding="utf-8")
                for char, entity in SMART_QUOTE_REPLACEMENTS.items():
                    content = content.replace(char, entity)
                xml_file.write_text(content, encoding="utf-8")
            except Exception:
                pass
        return None, f"Unpacked {input_file} ({len(xml_files)} XML files)"
    except zipfile.BadZipFile:
        return None, f"Error: {input_file} is not a valid Office file"
    except Exception as e:
        return None, f"Error unpacking: {e}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unpack an Office file")
    parser.add_argument("input_file", help="Office file to unpack")
    parser.add_argument("output_directory", help="Output directory")
    args = parser.parse_args()
    _, message = unpack(args.input_file, args.output_directory)
    print(message)
    if "Error" in message:
        sys.exit(1)