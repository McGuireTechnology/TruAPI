import json
from pathlib import Path

from fastapi import FastAPI

from truapi.drivers.rest.main import create_api_app


def filter_paths(schema: dict, prefix: str) -> dict:
    paths = schema.get("paths", {})
    filtered = {p: v for p, v in paths.items() if p.startswith(prefix)}
    schema = dict(schema)
    schema["paths"] = filtered
    # Optionally filter tags to only those used by filtered paths
    used_tags = set()
    for item in filtered.values():
        for method in item.values():
            for tag in method.get("tags", []):
                used_tags.add(tag)
    if "tags" in schema:
        schema["tags"] = [t for t in schema["tags"] if t.get("name") in used_tags]
    return schema


def main() -> None:
    app: FastAPI = create_api_app()
    schema = app.openapi()
    users = filter_paths(schema, "/users")
    out_path = Path(__file__).with_name("openapi-users.json")
    out_path.write_text(json.dumps(users, ensure_ascii=False, indent=2))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
