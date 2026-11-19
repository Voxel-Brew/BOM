# VoxelBrew bill of materials

`dev.voxelbrew:bom` aligns the versions of all five public APIs and all eight
application modules, plus their third-party dependencies. It publishes a Maven BOM (`pom` packaging) and Gradle platform
metadata, with constraints and a JUnit BOM import: importing it does not add libraries to a consumer.

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
Third-party library, annotation-processor, and protoc versions are centralized in
`third-party.versions`. The BOM manages `org.assertj:assertj-core` for Java test
assertions and imports `org.junit:junit-bom` to align the complete JUnit family.
This includes dependencies used by test fixtures. Constraints never
add these libraries to consumers that do not request them.

Gradle plugins, formatter/analysis tool settings, the Gradle/JDK toolchains, and native
download versions/checksums stay in their owning build configuration. A Maven platform
does not configure Gradle plugins or native downloads. JavaFX classifiers remain
platform-specific in the GUI build; the module versions come from this BOM.

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
and Gradle metadata for all managed coordinates, exact versions, and the metadata-only JUnit BOM import.
The verification repository is under `build/repository`; generated files are ignored.
The parent workspace includes this BOM build and publishes it alongside the APIs
with its `publishToMavenLocal` task. Application and API builds select it through
`bomVersion`; individual API dependency versions are managed here.

To publish to GitHub Packages, set `GITHUB_ACTOR` and `GITHUB_TOKEN` (with package write
access) and run `publishBomPublicationToGitHubPackagesRepository`. Gradle properties
`githubPackagesUser` and `githubPackagesToken` are also supported. Never commit credentials.
Before rolling out consumers, publish the selected BOM to their repository.
For API releases, publish the release BOM to Maven Central first: it has constraints
and a metadata-only JUnit import, so the managed API artifacts can follow it. Set every managed version property
to the intended fixed release, supply the same `SIGNING_KEY_ID`, `SIGNING_PASSWORD`,
`SIGNING_KEY_RING`, `ORG_GRADLE_PROJECT_mavenCentralUsername`, and
`ORG_GRADLE_PROJECT_mavenCentralPassword` used by the API builds, and run
`publishAndReleaseToMavenCentral -PcentralRelease=true`. `projectVersion` must be a
release and all managed versions must be non-snapshot. Remote publication is explicit;
the check workflow never publishes.

The BOM is MIT licensed; managed artifacts retain their own licenses.
