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
    """Parse Axure RP exported HTML and extract structured data.

    Axure HTML structure:
    - Page title is in <title> tag, not h1
    - Components are divs with class like 'ax_default', 'ax_default button', etc.
    - Annotations/notes are in divs with class 'sticky_1' or contain '//' comments
    - Text is nested in child divs with class 'text'
    """

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
        self._in_text_content = False

        # Current element context
        self._current_tag = None
        self._current_class = ""
        self._current_id = ""
        self._current_text = ""

        # Track element hierarchy
        self._element_stack = []
        self._pending_component = None

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

        # Track element hierarchy
        self._element_stack.append({
            "tag": tag,
            "class": self._current_class,
            "id": self._current_id
        })

        # Detect page title from <title> tag
        if tag == "title":
            self._in_page_title = True
            self._current_text = ""

        # Detect component container - ax_default is the main component class
        if self._current_class and "ax_default" in self._current_class.lower():
            self._in_component = True
            self._pending_component = {
                "id": self._current_id,
                "class": self._current_class,
                "text": ""
            }

        # Detect text content containers
        if self._current_class and "text" in self._current_class.lower():
            self._in_text_content = True
            self._current_text = ""

    def handle_endtag(self, tag: str):
        # Pop from element stack
        if self._element_stack:
            self._element_stack.pop()

        # Process page title
        if self._in_page_title and tag == "title":
            page_name = self._current_text.strip()
            if page_name:
                self.current_page = page_name
                self.pages.append({
                    "name": page_name,
                    "id": self._current_id,
                    "components": [],
                    "annotations": []
                })
            self._in_page_title = False
            self._current_text = ""

        # Process text content
        elif self._in_text_content and tag in ["div", "span", "p"]:
            text = self._current_text.strip()

            # Check if this is inside a component
            if self._pending_component and text:
                self._pending_component["text"] = text
                self._pending_component["page"] = self.current_page  # Associate with current page
                self.components.append(self._pending_component.copy())

                # Check if this is an annotation (sticky_1 class or contains //)
                is_annotation = (
                    self._pending_component["class"]
                    and "sticky_1" in self._pending_component["class"].lower()
                ) or text.startswith("//")

                if is_annotation and self.current_page:
                    annotation = {
                        "page": self.current_page,
                        "content": text,
                        "element_id": self._pending_component["id"]
                    }
                    self.annotations.append(annotation)
                    if self.pages and self.pages[-1]["name"] == self.current_page:
                        self.pages[-1]["annotations"].append(annotation)

                self._pending_component = None

            self._in_text_content = False
            self._current_text = ""

        # Reset component state when leaving ax_default
        elif self._current_class and "ax_default" in self._current_class.lower() and tag == "div":
            if self._pending_component:
                self._pending_component = None
            self._in_component = False

    def handle_data(self, data: str):
        self._current_text += data

    def _infer_component_type(self, class_str: str, text: str) -> str:
        """Infer component type from class name and text content."""
        class_lower = class_str.lower() if class_str else ""

        # Check for specific component types
        if "button" in class_lower:
            return "button"
        elif "primary_button" in class_lower:
            return "primary_button"
        elif "input" in class_lower or "text_field" in class_lower:
            return "input"
        elif "table" in class_lower:
            return "table"
        elif "image" in class_lower or "_图片" in class_str:
            return "image"
        elif "link" in class_lower:
            return "link"
        elif "label" in class_lower:
            return "label"
        elif "droplist" in class_lower:
            return "droplist"
        elif "checkbox" in class_lower:
            return "checkbox"
        elif "radio" in class_lower:
            return "radio"
        elif "shape" in class_lower:
            return "shape"
        elif "paragraph" in class_lower:
            return "paragraph"
        elif "connector" in class_lower or "连接符" in class_str:
            return "connector"
        elif "sticky" in class_lower:
            return "annotation"
        elif "box" in class_lower:
            return "box"
        elif "title" in class_lower or "_标题" in class_str:
            return "title"
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
            # Determine module from page
            module_name = comp.get("page", "未知模块")

            # Extract component type from class
            comp_type = self._extract_type_from_class(comp.get("class", ""))

            testcase_data["function_points"].append({
                "module": module_name,
                "name": comp.get("text", comp.get("id", "未知组件"))[:200],
                "type": comp_type
            })

            testcase_data["ui_elements"].append({
                "module": module_name,
                "element_name": comp.get("text", comp.get("id", "未知组件"))[:200],
                "element_type": comp_type,
                "element_id": comp.get("id", "")
            })

        # Map annotations to constraints
        for ann in self.parser.annotations:
            testcase_data["constraints"].append({
                "module": ann.get("page", "未知模块"),
                "description": ann.get("content", ""),
                "source": "axure_annotation"
            })

        return testcase_data

    def _extract_type_from_class(self, class_str: str) -> str:
        """Extract component type from Axure class string."""
        if not class_str:
            return "unknown"

        # Axure class format: "ax_default _标题_3" or "ax_default primary_button"
        parts = class_str.split()
        for part in parts:
            if part.startswith("_") and part != "_":
                # Remove underscore prefix
                return part[1:]
            elif part not in ["ax_default", "shape", "box_1"]:
                return part

        return "unknown"


def extract_axure_data(input_path: Path, recursive: bool = False, merge: bool = False) -> list[dict]:
    """Extract data from Axure HTML files.

    Args:
        input_path: Input HTML file or directory path
        recursive: Recursively search subdirectories
        merge: If True and multiple files found, merge into single result

    Returns:
        List of extracted data dictionaries
    """
    results = []

    if input_path.is_file() and input_path.suffix in [".html", ".htm"]:
        extractor = AxureHTMLExtractor(input_path)
        data = extractor.parse()
        testcase_data = extractor.extract_for_testcase()
        results.append({
            "file": str(input_path),
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
                # Skip resource files that are not actual page exports
                if "resources/" in str(html_file) or "plugins/" in str(html_file):
                    continue
                try:
                    extractor = AxureHTMLExtractor(html_file)
                    data = extractor.parse()
                    # Only add if there's actual page data
                    if data["pages"]:
                        testcase_data = extractor.extract_for_testcase()
                        results.append({
                            "file": str(html_file),
                            "raw": data,
                            "testcase": testcase_data
                        })
                except Exception as e:
                    print(f"Warning: Failed to parse {html_file}: {e}", file=sys.stderr)

    # Merge results if requested
    if merge and len(results) > 1:
        return [merge_results(results)]

    return results


def merge_results(results: list[dict]) -> dict:
    """Merge multiple parse results into single aggregated result."""
    merged = {
        "source": "axure",
        "files": [r.get("file", "unknown") for r in results],
        "pages": [],
        "components": [],
        "annotations": [],
        "summary": {
            "page_count": 0,
            "component_count": 0,
            "annotation_count": 0,
            "files": len(results)
        }
    }

    testcase_merged = {
        "source": "axure",
        "files": [r.get("file", "unknown") for r in results],
        "modules": [],
        "function_points": [],
        "ui_elements": [],
        "interactions": [],
        "constraints": []
    }

    for r in results:
        raw = r.get("raw", {})
        merged["pages"].extend(raw.get("pages", []))
        merged["components"].extend(raw.get("components", []))
        merged["annotations"].extend(raw.get("annotations", []))

        merged["summary"]["page_count"] += len(raw.get("pages", []))
        merged["summary"]["component_count"] += len(raw.get("components", []))
        merged["summary"]["annotation_count"] += len(raw.get("annotations", []))

        tc = r.get("testcase", {})
        testcase_merged["modules"].extend(tc.get("modules", []))
        testcase_merged["function_points"].extend(tc.get("function_points", []))
        testcase_merged["ui_elements"].extend(tc.get("ui_elements", []))
        testcase_merged["constraints"].extend(tc.get("constraints", []))

    merged["testcase"] = testcase_merged
    return merged


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
        "--merge", "-m",
        action="store_true",
        help="Merge multiple files into single aggregated result"
    )
    parser.add_argument(
        "--summary", "-s",
        action="store_true",
        help="Output only summary information (for quick inspection)"
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
        results = extract_axure_data(args.input_path, args.recursive, args.merge)

        if not results:
            print("No Axure HTML files found.", file=sys.stderr)
            return 1

        # Output summary mode
        if args.summary:
            print("\n▎ Axure HTML 解析摘要\n", file=sys.stderr)
            total_pages = 0
            total_components = 0
            total_annotations = 0
            for r in results:
                raw = r.get("raw", {})
                summary = raw.get("summary", {})
                print(f"  文件：{r.get('file', 'unknown')}", file=sys.stderr)
                print(f"    页面：{summary.get('page_count', 0)}", file=sys.stderr)
                print(f"    组件：{summary.get('component_count', 0)}", file=sys.stderr)
                print(f"    注释：{summary.get('annotation_count', 0)}", file=sys.stderr)
                total_pages += summary.get('page_count', 0)
                total_components += summary.get('component_count', 0)
                total_annotations += summary.get('annotation_count', 0)
            print(f"\n  总计：{len(results)} 个文件，{total_pages} 个页面，{total_components} 个组件，{total_annotations} 条注释", file=sys.stderr)
            return 0

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
