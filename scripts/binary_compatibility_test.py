"""Exercise the shared Gradle task against an isolated Maven repository."""
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
from threading import Thread
import unittest

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / ("gradlew.bat" if os.name == "nt" else "gradlew")


class MavenHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.server.unavailable:
            self.send_error(503)
        else:
            super().do_GET()


class BinaryCompatibilityTest(unittest.TestCase):
    def test_published_contract(self):
        with TemporaryDirectory() as tmp:
            work = Path(tmp)
            repository = work / "maven"
            module = repository / "example/api"
            release = module / "1.0.10"
            release.mkdir(parents=True)
            handler = functools.partial(MavenHandler, directory=repository)
            with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
                server.unavailable = False
                thread = Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    self.exercise(work, module, release, server)
                finally:
                    server.shutdown()
                    thread.join()

    def exercise(self, work, module, release, server):
        mirror = f"http://127.0.0.1:{server.server_port}"
        policy = work / "quality/binary-compatibility.gradle"
        policy.parent.mkdir()
        # Redirect only the Central endpoint in this temporary copy.
        policy.write_text((ROOT / "quality" / policy.name).read_text().replace(
            "https://repo.maven.apache.org/maven2", mirror))
        shutil.copy(ROOT / "third-party.versions", work)
        (work / "settings.gradle").write_text("rootProject.name = 'api'")
        (work / "build.gradle").write_text(f"""
plugins {{ id 'java-library' }}
group = 'example'
version = providers.gradleProperty('candidate').get()
repositories {{
    maven {{ url = uri('{mirror}'); content {{ includeGroup 'example' }} }}
    mavenCentral()
}}
apply from: file('quality/binary-compatibility.gradle')
""")
        source = work / "src/main/java/example/Contract.java"
        source.parent.mkdir(parents=True)
        base = "package example; public class Contract { public void existing() {}"
        source.write_text(base + "}")
        classes = work / "old-classes"
        classes.mkdir()
        subprocess.run(["javac", "-d", classes, source], check=True)
        subprocess.run(["jar", "cf", release / "api-1.0.10.jar", "-C", classes, "."], check=True)
        (release / "api-1.0.10.pom").write_text(
            "<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId>"
            "<artifactId>api</artifactId><version>1.0.10</version></project>")
        metadata = module / "maven-metadata.xml"
        versions = ["1.0.9", "1.0.10", "1.2.0", "1.1.0-rc1", "2.0.0"]
        metadata.write_text("<metadata><groupId>example</groupId><artifactId>api</artifactId>"
                            "<versioning><versions>" + "".join(f"<version>{v}</version>" for v in versions)
                            + "</versions></versioning></metadata>")

        def check(version, expected, success=True):
            result = subprocess.run([str(WRAPPER), "--console=plain", "checkBinaryCompatibility",
                                     f"-Pcandidate={version}-SNAPSHOT"], cwd=work,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            self.assertEqual(result.returncode == 0, success, result.stdout)
            self.assertIn(expected, result.stdout)

        source.write_text(base + " public void added() {} }")
        check("1.0.11", "against Maven Central example:api:1.0.10")
        source.write_text("package example; public class Contract {}")
        check("1.1.0", "existing", False)
        check("3.0.0", "No eligible Maven Central baseline")
        server.unavailable = True
        check("1.0.11", "503", False)
        server.unavailable = False
        metadata.write_text("<metadata/>")
        check("1.0.11", "Invalid Maven Central metadata", False)
