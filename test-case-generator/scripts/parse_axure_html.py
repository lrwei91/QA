#!/usr/bin/env python3
"""
parse_axure_html.py — Parse Axure RP exported HTML and extract requirement data.

Extracts page structure, component info, annotations, and interaction specs
from Axure HTML exports for test case generation.

Usage:
    python3 parse_axure_html.py input.html
    python3 parse_axure_html.py input.html --output data.json
    python3 parse_axure_html.py directory/ --recursive
    python3 parse_axure_html.py directory/ --recursive --output all_data.json

Output:
    JSON structure suitable for testcase-generate skill input
"""

import argparse
import json
import re
import sys
from pathlib import Path
from html.parser import HTMLParser
from typing import Any


class AxureHTMLParser(HTMLParser):
    """Parse Axure RP exported HTML and extract structured data."""

    def __init__(self):
        super().__init__()
        self.current_page = None
        self.pages = []
        self.components = []
        self.annotations = []
        self.interactions = []

        # State tracking
        self._in_page_title = False
        self._in_component = False
        self._in_annotation = False
        self._in_interaction = False

        # Current element context
        self._current_tag = None
        self._current_class = ""
        self._current_id = ""
        self._current_text = ""

        # Component context
        self._component_stack = []

    def _get_attr(self, attrs: list[tuple[str, str | None]], name: str) -> str:
        """Get attribute value from attrs list."""
        for attr_name, attr_value in attrs:
            if attr_name == name and attr_value:
                return attr_value
        return ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        self._current_tag = tag
        self._current_class = self._get_attr(attrs, "class")
        self._current_id = self._get_attr(attrs, "id")
        self._current_text = ""

        # Detect page container
        if "page" in self._current_class.lower() or "ax_page" in self._current_class.lower():
            self._in_page_title = True

        # Detect component container
        if any(x in self._current_class.lower() for x in ["ax_component", "widget", "object"]):
            self._in_component = True
            component_id = self._get_attr(attrs, "id")
            if component_id:
                self._component_stack.append(component_id)

        # Detect annotation
        if "note" in self._current_class.lower() or "annotation" in self._current_class.lower():
            self._in_annotation = True

    def handle_endtag(self, tag: str):
        if tag == self._current_tag:
            # Process collected text
            text = self._current_text.strip()

            if self._in_page_title and tag == "h1":
                self.current_page = text
                self.pages.append({
                    "name": text,
                    "id": self._current_id,
                    "components": [],
                    "annotations": []
                })
                self._in_page_title = False

            elif self._in_component and tag in ["div", "span", "p"]:
                if text and self.current_page:
                    component = self._parse_component(text)
                    if component:
                        self.components.append(component)
                        if self.pages and self.pages[-1]["name"] == self.current_page:
                            self.pages[-1]["components"].append(component)
                self._in_component = False
                if self._component_stack:
                    self._component_stack.pop()

            elif self._in_annotation and tag in ["div", "p", "span"]:
                if text and self.current_page:
                    annotation = {
                        "page": self.current_page,
                        "content": text,
                        "element_id": self._current_id
                    }
                    self.annotations.append(annotation)
                    if self.pages and self.pages[-1]["name"] == self.current_page:
                        self.pages[-1]["annotations"].append(annotation)
                self._in_annotation = False

            self._current_tag = None
            self._current_class = ""
            self._current_id = ""
            self._current_text = ""

    def handle_data(self, data: str):
        self._current_text += data

    def _parse_component(self, text: str) -> dict[str, Any]:
        """Parse component from text and context."""
        # Determine component type based on class or content
        component_type = self._infer_component_type()

        return {
            "id": self._current_id,
            "name": text[:100] if text else f"Component_{self._current_id}",
            "type": component_type,
            "parent": self._component_stack[-1] if self._component_stack else None,
            "page": self.current_page
        }

    def _infer_component_type(self) -> str:
        """Infer component type from class name."""
        class_lower = self._current_class.lower()

        if "button" in class_lower:
            return "button"
        elif "input" in class_lower or "text" in class_lower:
            return "input"
        elif "table" in class_lower:
            return "table"
        elif "image" in class_lower:
            return "image"
        elif "link" in class_lower:
            return "link"
        elif "label" in class_lower:
            return "label"
        else:
            return "container"


class AxureHTMLExtractor:
    """Extract structured data from Axure RP HTML exports."""

    def __init__(self, html_path: Path):
        self.html_path = html_path
        self.parser = AxureHTMLParser()
        self.data = {
            "source": "axure",
            "file": str(html_path),
            "pages": [],
            "components": [],
            "annotations": [],
            "interactions": [],
            "summary": {}
        }

    def parse(self) -> dict:
        """Parse HTML file and return extracted data."""
        if not self.html_path.exists():
            raise FileNotFoundError(f"File not found: {self.html_path}")

        content = self.html_path.read_text(encoding="utf-8")
        self.parser.feed(content)

        self.data["pages"] = self.parser.pages
        self.data["components"] = self.parser.components
        self.data["annotations"] = self.parser.annotations

        # Generate summary
        self.data["summary"] = {
            "page_count": len(self.parser.pages),
            "component_count": len(self.parser.components),
            "annotation_count": len(self.parser.annotations),
            "pages": [p["name"] for p in self.parser.pages]
        }

        return self.data

    def extract_for_testcase(self) -> dict:
        """Extract data formatted for test case generation."""
        testcase_data = {
            "source": "axure",
            "modules": [],
            "function_points": [],
            "ui_elements": [],
            "interactions": [],
            "constraints": []
        }

        # Map pages to modules
        for page in self.parser.pages:
            testcase_data["modules"].append({
                "name": page["name"],
                "source": "axure_page",
                "page_id": page["id"]
            })

        # Map components to function points and UI elements
        for comp in self.parser.components:
            testcase_data["function_points"].append({
                "module": comp["page"],
                "name": comp["name"],
                "type": comp["type"]
            })

            testcase_data["ui_elements"].append({
                "module": comp["page"],
                "element_name": comp["name"],
                "element_type": comp["type"],
                "element_id": comp["id"]
            })

        # Map annotations to constraints
        for ann in self.parser.annotations:
            testcase_data["constraints"].append({
                "module": ann["page"],
                "description": ann["content"],
                "source": "axure_annotation"
            })

        return testcase_data


def extract_axure_data(input_path: Path, recursive: bool = False) -> list[dict]:
    """Extract data from Axure HTML files."""
    results = []

    if input_path.is_file() and input_path.suffix in [".html", ".htm"]:
        extractor = AxureHTMLExtractor(input_path)
        data = extractor.parse()
        testcase_data = extractor.extract_for_testcase()
        results.append({
            "raw": data,
            "testcase": testcase_data
        })

    elif input_path.is_dir():
        if recursive:
            patterns = ["**/*.html", "**/*.htm"]
        else:
            patterns = ["*.html", "*.htm"]

        for pattern in patterns:
            for html_file in input_path.glob(pattern):
                try:
                    extractor = AxureHTMLExtractor(html_file)
                    data = extractor.parse()
                    testcase_data = extractor.extract_for_testcase()
                    results.append({
                        "file": str(html_file),
                        "raw": data,
                        "testcase": testcase_data
                    })
                except Exception as e:
                    print(f"Warning: Failed to parse {html_file}: {e}", file=sys.stderr)

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse Axure RP exported HTML and extract requirement data."
    )
    parser.add_argument(
        "input_path",
        type=Path,
        help="Input HTML file or directory path"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output JSON file path (default: stdout)"
    )
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="Recursively search for HTML files in directory"
    )
    parser.add_argument(
        "--format",
        choices=["raw", "testcase"],
        default="testcase",
        help="Output format: raw (full parse) or testcase (for test generation)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    try:
        results = extract_axure_data(args.input_path, args.recursive)

        if not results:
            print("No Axure HTML files found.", file=sys.stderr)
            return 1

        # Format output
        if args.format == "testcase":
            output_data = [r["testcase"] for r in results]
        else:
            output_data = [r["raw"] for r in results]

        # Output
        output_json = json.dumps(output_data, indent=2, ensure_ascii=False)

        if args.output:
            args.output.write_text(output_json, encoding="utf-8")
            print(f"Output written to: {args.output}")
        else:
            print(output_json)

        if args.verbose:
            print(f"\nSummary:", file=sys.stderr)
            for r in results:
                raw = r.get("raw", {})
                print(f"  File: {r.get('file', 'unknown')}", file=sys.stderr)
                print(f"    Pages: {raw.get('summary', {}).get('page_count', 0)}", file=sys.stderr)
                print(f"    Components: {raw.get('summary', {}).get('component_count', 0)}", file=sys.stderr)
                print(f"    Annotations: {raw.get('summary', {}).get('annotation_count', 0)}", file=sys.stderr)

        return 0

    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
