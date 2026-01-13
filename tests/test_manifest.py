import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from psellos_builder.builders.manifest import build_manifest


class ManifestSpecVersionTests(unittest.TestCase):
    def test_manifest_includes_spec_version_from_spec_path(self) -> None:
        dataset = {"persons": [], "assertions": []}
        spec_path = Path("psellos-spec/schema/minimal.person-parent.v0.1.json")
        input_path = Path("psellos-data/demo.json")

        manifest = build_manifest(dataset, spec_path=spec_path, input_path=input_path)

        self.assertIn("spec_version", manifest)
        self.assertEqual("minimal.person-parent.v0.1", manifest["spec_version"])
        self.assertIn("generated_at", manifest)


if __name__ == "__main__":
    unittest.main()
