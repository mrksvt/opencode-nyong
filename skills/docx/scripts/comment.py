"""Add comments to DOCX documents."""

import argparse, random, shutil, sys
from datetime import datetime, timezone
from pathlib import Path
import defusedxml.minidom

TEMPLATE_DIR = Path(__file__).parent / "templates"
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
      "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
      "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
      "w16cid": "http://schemas.microsoft.com/office/word/2016/wordml/cid",
      "w16cex": "http://schemas.microsoft.com/office/word/2018/wordml/cex"}

COMMENT_XML = '<w:comment w:id="{id}" w:author="{author}" w:date="{date}" w:initials="{initials}"><w:p w14:paraId="{para_id}" w14:textId="77777777"><w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:annotationRef/></w:r><w:r><w:rPr><w:color w:val="000000"/><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr><w:t>{text}</w:t></w:r></w:p></w:comment>'

def _generate_hex_id():
    return f"{random.randint(0, 0x7FFFFFFE):08X}"

def _append_xml(xml_path, root_tag, content):
    dom = defusedxml.minidom.parseString(xml_path.read_text(encoding="utf-8"))
    root = dom.getElementsByTagName(root_tag)[0]
    ns_attrs = " ".join(f'xmlns:{k}="{v}"' for k, v in NS.items())
    wrapper_dom = defusedxml.minidom.parseString(f"<root {ns_attrs}>{content}</root>")
    for child in wrapper_dom.documentElement.childNodes:
        if child.nodeType == child.ELEMENT_NODE:
            root.appendChild(dom.importNode(child, True))
    xml_path.write_bytes(dom.toxml(encoding="UTF-8"))

def add_comment(unpacked_dir, comment_id, text, author="Claude", initials="C", parent_id=None):
    word = Path(unpacked_dir) / "word"
    if not word.exists():
        return "", f"Error: {word} not found"
    para_id, durable_id = _generate_hex_id(), _generate_hex_id()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    comments = word / "comments.xml"
    first_comment = not comments.exists()
    if first_comment:
        shutil.copy(TEMPLATE_DIR / "comments.xml", comments)
    _append_xml(comments, "w:comments",
                COMMENT_XML.format(id=comment_id, author=author, date=ts, initials=initials, para_id=para_id, text=text))
    action = "reply" if parent_id else "comment"
    marker = ('\nAdd to document.xml:\n  <w:commentRangeStart w:id="%d"/>\n  <w:r>...</w:r>\n  <w:commentRangeEnd w:id="%d"/>\n  <w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="%d"/></w:r>' % (comment_id, comment_id, comment_id))
    return para_id, f"Added {action} {comment_id} (para_id={para_id}){marker}"

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Add comments to DOCX documents")
    p.add_argument("unpacked_dir", help="Unpacked DOCX directory")
    p.add_argument("comment_id", type=int, help="Comment ID (must be unique)")
    p.add_argument("text", help="Comment text")
    p.add_argument("--author", default="Claude", help="Author name")
    p.add_argument("--initials", default="C", help="Author initials")
    p.add_argument("--parent", type=int, help="Parent comment ID (for replies)")
    args = p.parse_args()
    para_id, msg = add_comment(args.unpacked_dir, args.comment_id, args.text, args.author, args.initials, args.parent)
    print(msg)
    if "Error" in msg:
        sys.exit(1)