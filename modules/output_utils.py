from pathlib import Path
import re
from uuid import uuid4


def unique_output_path(output_dir, identity, suffix=".png"):
	output_dir = Path(output_dir)
	output_dir.mkdir(parents=True, exist_ok=True)
	slug = re.sub(r"[^A-Za-z0-9_-]+", "_", identity).strip("_") or "identity"
	return output_dir / f"{slug}_{uuid4().hex}{suffix}"