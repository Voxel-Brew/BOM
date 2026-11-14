"""Check the published platform contract using only Python's standard library."""

import json
from pathlib import Path
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
properties = dict(
    line.split("=", 1)
    for line in (root / "gradle.properties").read_text().splitlines()
    if "=" in line and not line.startswith("#")
)
expected = {
    ("dev.voxelbrew", name): properties["applicationVersion"]
    for name in (
        "util", "engine", "importer-impl", "exporter-impl", "slicer-impl",
        "printer-impl", "cli", "gui",
    )
}
expected.update({
    ("dev.voxelbrew.api", name): properties[f"{name}ApiVersion"]
    for name in ("model", "import", "export", "printer", "slicer")
})
publication = root / "build/publications/bom"
pom = ET.parse(publication / "pom-default.xml").getroot()
ns = {"m": "http://maven.apache.org/POM/4.0.0"}
assert pom.findtext("m:packaging", namespaces=ns) == "pom"
assert pom.findtext("m:groupId", namespaces=ns) == "dev.voxelbrew"
assert pom.findtext("m:artifactId", namespaces=ns) == "bom"
assert pom.findtext("m:version", namespaces=ns) == properties["projectVersion"]
assert pom.find("m:dependencies", ns) is None
entries = pom.findall("m:dependencyManagement/m:dependencies/m:dependency", ns)
actual = {
    (entry.findtext("m:groupId", namespaces=ns), entry.findtext("m:artifactId", namespaces=ns)):
    entry.findtext("m:version", namespaces=ns)
    for entry in entries
}
assert len(entries) == 13 and actual == expected, actual
metadata = json.loads((publication / "module.json").read_text())
assert len(metadata["variants"]) == 2
for variant in metadata["variants"]:
    assert variant["attributes"]["org.gradle.category"] == "platform"
    assert not variant.get("dependencies")
    constraints = variant["dependencyConstraints"]
    actual = {
        (item["group"], item["module"]): item["version"]["requires"]
        for item in constraints
    }
    assert len(constraints) == 13 and actual == expected, actual
repository = root / "build/repository/dev/voxelbrew/bom" / properties["projectVersion"]
assert list(repository.glob("bom-*.pom")), "Missing repository POM"
assert list(repository.glob("bom-*.module")), "Missing repository metadata"
assert not list(repository.glob("*.jar")), "A BOM must not publish a JAR"
print("Verified 13 constraints in Maven POM and both Gradle platform variants.")
