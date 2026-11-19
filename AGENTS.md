# Repository Guidelines

## Project Structure & Module Organization

This repository publishes `dev.voxelbrew:bom`, a Gradle Java Platform and Maven BOM; it does not contain application source code. The platform definition and publication configuration live in `build.gradle.kts`. VoxelBrew module versions are declared in `gradle.properties`, while third-party Maven coordinates and versions are kept in the alphabetized `third-party.versions` file. `scripts/verify-publication.py` validates generated Maven and Gradle metadata. CI configuration is in `.github/workflows/check.yml`, and Gradle wrapper files are under `gradle/wrapper/`.

Generated content belongs under `.gradle/` or `build/` and must not be committed.

## Build, Test, and Development Commands

Use Java 21 and the checked-in Gradle 9.1.0 wrapper. On Linux:

- `./gradlew check` validates the Gradle build and version rules.
- `./gradlew check publishBomPublicationToVerificationRepository` generates the POM and module metadata in `build/` for verification.
- `python3 scripts/verify-publication.py` checks every managed coordinate, the JUnit BOM import, and the absence of a published JAR.
- `./gradlew publishToMavenLocal` installs the BOM for local consumer testing.

On Windows, use `gradlew.bat` and `python`. Run the publication task before the Python verifier.

## Coding Style & Naming Conventions

Use four-space indentation in Kotlin and Python, LF line endings except for `.bat` files, and UTF-8 text. Follow Kotlin DSL conventions: `camelCase` for values and descriptive Gradle task or publication names. Keep Python compatible with the standard library and use `snake_case`. Preserve `group:artifact=version` formatting and alphabetical ordering in `third-party.versions`. Versions must be fixed; a release BOM may not reference snapshots.

## Testing Guidelines

There is no unit-test source set. Treat the Gradle check plus publication verifier as the required test suite. When adding, removing, or changing a constraint, update the verifier's expected counts or mappings as needed and inspect both Maven POM and Gradle module behavior. Run the same two commands used by CI before opening a pull request.

## Pre-commit SpotBugs

The `spotbugs-conventions` included build owns the shared Gradle plugin, analyzer versions,
reports, and exclusions. Application and API builds load it from the BOM source checkout.

The BOM has no Java sources to analyze. Before committing changes to the shared
SpotBugs convention, run `:voxelbrew:basicChecks` and the affected APIs?
qualified `spotbugsMain` tasks with the workspace wrapper.

## Commit & Pull Request Guidelines

Recent commits use concise, imperative subjects such as `Manage third-party libraries and JUnit alignment in BOM`. Keep each commit focused. Pull requests should explain which coordinates or publication behavior changed, why the versions are compatible, and how verification was performed. Link relevant issues or upstream releases. Never commit repository credentials, signing keys, or generated publication files.

## AssertJ in Java tests

Use AssertJ (org.assertj:assertj-core) for assertions in Java unit, integration, and end-to-end tests. Keep JUnit Jupiter for test lifecycle, parameterization, and execution. Declare AssertJ without a version in test dependencies; the BOM manages its version. Prefer ssertThat, ssertThatThrownBy, and ssertThatCode with descriptive failure messages and appropriate numeric tolerances. Do not add new JUnit Assertions calls.
