#!/usr/bin/env python3
"""
Script to export OpenAPI schema to YAML file.
Run this script to generate openapi.yaml from the running application.
"""
import json
import sys
import yaml
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from t1_construcao.main import app


def export_openapi_to_yaml(output_path: str = "openapi.yaml"):
    """Export OpenAPI schema to YAML file."""
    # Get the OpenAPI schema
    openapi_schema = app.openapi()
    
    # Convert to YAML
    yaml_content = yaml.dump(openapi_schema, default_flow_style=False, sort_keys=False)
    
    # Write to file
    output_file = Path(output_path)
    output_file.write_text(yaml_content, encoding="utf-8")
    
    print(f"✅ OpenAPI schema exported to {output_path}")
    return output_path


if __name__ == "__main__":
    try:
        import yaml
    except ImportError:
        print("❌ PyYAML is required. Install it with: poetry add pyyaml --group dev")
        sys.exit(1)
    
    output_file = sys.argv[1] if len(sys.argv) > 1 else "openapi.yaml"
    export_openapi_to_yaml(output_file)

