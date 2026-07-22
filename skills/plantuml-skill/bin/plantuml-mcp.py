#!/usr/bin/env python3
"""MCP server for local PlantUML rendering via plantuml.jar"""
import json
import sys
import subprocess
import tempfile
import os
import base64

JAR_PATH = os.path.join(os.path.dirname(__file__), "plantuml.jar")

def render_puml(puml_text: str, fmt: str = "png") -> dict:
    """Render PUML text to PNG/SVG using local plantuml.jar"""
    with tempfile.NamedTemporaryFile(suffix=".puml", mode="w", delete=False) as f:
        f.write(puml_text)
        puml_path = f.name
    
    out_dir = tempfile.mkdtemp()
    
    try:
        fmt_flag = "-tpng" if fmt == "png" else "-tsvg"
        result = subprocess.run(
            ["java", "-jar", JAR_PATH, fmt_flag, puml_path, "-o", out_dir],
            capture_output=True, text=True, timeout=30
        )
        
        base = os.path.basename(puml_path).replace(".puml", "")
        out_file = os.path.join(out_dir, f"{base}.{fmt}")
        
        if os.path.exists(out_file):
            with open(out_file, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            return {"success": True, "format": fmt, "data": data, "size": os.path.getsize(out_file)}
        else:
            return {"success": False, "error": result.stderr or "No output file"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        os.unlink(puml_path)
        for f in os.listdir(out_dir):
            os.unlink(os.path.join(out_dir, f))
        os.rmdir(out_dir)

def handle_request(request):
    method = request.get("method", "")
    req_id = request.get("id", 0)
    
    if method == "tools/list":
        return json.dumps({
            "jsonrpc": "2.0", "id": req_id,
            "result": {"tools": [{
                "name": "render_plantuml",
                "description": "Render PlantUML text to PNG/SVG using local plantuml.jar",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "puml": {"type": "string", "description": "PlantUML source text"},
                        "format": {"type": "string", "enum": ["png", "svg"], "default": "png"}
                    },
                    "required": ["puml"]
                }
            }]}
        })
    
    elif method == "tools/call":
        tool_name = request["params"]["name"]
        args = request["params"]["arguments"]
        if tool_name == "render_plantuml":
            result = render_puml(args["puml"], args.get("format", "png"))
            return json.dumps({
                "jsonrpc": "2.0", "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(result)}]}
            })
    
    return json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}})

if __name__ == "__main__":
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            response = handle_request(json.loads(line))
            sys.stdout.write(response + "\n")
            sys.stdout.flush()
        except Exception:
            pass
