# VoxelBrew bill of materials

`dev.voxelbrew:bom` aligns the versions of all five public APIs and all eight
application modules. It publishes a Maven BOM (`pom` packaging) and Gradle platform
metadata, with constraints only: importing it does not add libraries to a consumer.

## Managed projects

| Group | Artifacts | Version property |
| --- | --- | --- |
| `dev.voxelbrew.api` | `model` | `modelApiVersion` |
| `dev.voxelbrew.api` | `import` | `importApiVersion` |
| `dev.voxelbrew.api` | `export` | `exportApiVersion` |
| `dev.voxelbrew.api` | `printer` | `printerApiVersion` |
| `dev.voxelbrew.api` | `slicer` | `slicerApiVersion` |
| `dev.voxelbrew` | `util`, `engine`, `importer-impl`, `exporter-impl`, `slicer-impl`, `printer-impl`, `cli`, `gui` | `applicationVersion` |

The initial version is `0.1.0-SNAPSHOT`, matching the workspace projects.
The BOM's own version is independently controlled by `projectVersion`.
Update the properties together with the corresponding project releases; API versions
may advance independently. Only fixed versions are accepted, and release BOMs cannot
reference snapshots.

Constraints do not guarantee artifact availability. The APIs have Maven publication
configuration; `util`, `engine`, `importer-impl`, `exporter-impl`, and `slicer-impl`
also define Maven publications. Currently `printer-impl`, `cli`, and `gui` do not.
Their coordinates are included for complete workspace alignment, but external
consumers cannot resolve them until the owning project adds and publishes them.
The website and workspace aggregator produce no Maven artifacts and have no BOM entries.
Third-party libraries and test fixtures are outside this BOM's scope.

## Consume

Configure a repository containing the BOM and the selected artifacts. For local
development, publish the BOM and needed projects to Maven local and use `mavenLocal()`.
GitHub Packages requires authentication and repositories for the individual API packages
as well as `https://maven.pkg.github.com/voxel-brew/bom` for the BOM.

```kotlin
dependencies {
    implementation(platform("dev.voxelbrew:bom:0.1.0-SNAPSHOT"))
    implementation("dev.voxelbrew.api:model")
    implementation("dev.voxelbrew.api:export")
}
```

For Maven, import the BOM under dependency management, then declare the APIs without versions:

```xml
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>dev.voxelbrew</groupId>
      <artifactId>bom</artifactId>
      <version>0.1.0-SNAPSHOT</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>
```

## Build and verify

Use Java 21 and the checked-in Gradle 9.1.0 wrapper. No native toolchain is required.
From PowerShell:

```powershell
.\gradlew.bat check publishBomPublicationToVerificationRepository
python scripts/verify-publication.py
.\gradlew.bat publishToMavenLocal
```

On Linux use `./gradlew` and `python3` instead. Verification checks the generated POM
and Gradle metadata for all 13 coordinates, exact versions, and absence of direct dependencies.
The verification repository is under `build/repository`; generated files are ignored.
This independent build does not require changes to the parent workspace composite.

To publish to GitHub Packages, set `GITHUB_ACTOR` and `GITHUB_TOKEN` (with package write
access) and run `publishBomPublicationToGitHubPackagesRepository`. Gradle properties
`githubPackagesUser` and `githubPackagesToken` are also supported. Never commit credentials.
No automatic release or Maven Central publication is configured.

The BOM is MIT licensed; managed artifacts retain their own licenses.
