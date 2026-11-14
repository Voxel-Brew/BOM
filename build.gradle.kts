plugins {
    `java-platform`
    `maven-publish`
    id("com.vanniktech.maven.publish.base") version "0.37.0"
}

// Match API release publishing; local and snapshot publication needs no signing key.
val centralRelease = providers.gradleProperty("centralRelease").orNull == "true"
mavenPublishing {
    publishToMavenCentral(
        validateDeployment = com.vanniktech.maven.publish.DeploymentValidation.PUBLISHED
    )
    if (centralRelease) {
        project.extra["signing.keyId"] = providers.environmentVariable("SIGNING_KEY_ID").orNull ?: ""
        project.extra["signing.password"] = providers.environmentVariable("SIGNING_PASSWORD").orNull ?: ""
        project.extra["signing.secretKeyRingFile"] = providers.environmentVariable("SIGNING_KEY_RING").orNull ?: ""
        signAllPublications()
    }
}
tasks.matching { it.name.contains("MavenCentral") }.configureEach {
    doFirst {
        check(centralRelease && Regex("[0-9]+\\.[0-9]+\\.[0-9]+").matches(project.version.toString())) {
            "Central publishing requires a release projectVersion and -PcentralRelease=true."
        }
    }
}

group = "dev.voxelbrew"
version = providers.gradleProperty("projectVersion").get()

val applicationVersion = providers.gradleProperty("applicationVersion").get()
val managedModules =
    listOf("util", "engine", "importer-impl", "exporter-impl", "slicer-impl", "printer-impl", "cli", "gui")
        .associate { "dev.voxelbrew:$it" to applicationVersion } +
        listOf("model", "import", "export", "printer", "slicer").associate {
            "dev.voxelbrew.api:$it" to providers.gradleProperty("${it}ApiVersion").get()
        }

managedModules.forEach { (module, moduleVersion) ->
    require(Regex("[0-9]+\\.[0-9]+\\.[0-9]+(?:-[A-Za-z0-9.-]+)?").matches(moduleVersion)) {
        "$module must use a fixed version: $moduleVersion"
    }
    require(version.toString().endsWith("-SNAPSHOT") || !moduleVersion.endsWith("-SNAPSHOT")) {
        "A release BOM cannot manage snapshot versions: $module:$moduleVersion"
    }
}

dependencies {
    constraints { managedModules.forEach { (module, version) -> api("$module:$version") } }
}

publishing {
    publications {
        create<MavenPublication>("bom") {
            from(components["javaPlatform"])
            pom {
                name.set("VoxelBrew BOM")
                description.set("Version alignment for all VoxelBrew API and application modules.")
                url.set("https://github.com/Voxel-Brew/BOM")
                licenses {
                    license {
                        name.set("MIT License")
                        url.set("https://opensource.org/license/mit")
                        distribution.set("repo")
                    }
                }
                developers {
                    developer {
                        id.set("voxelbrew")
                        name.set("VoxelBrew contributors")
                        url.set("https://github.com/Voxel-Brew")
                    }
                }
                scm {
                    url.set("https://github.com/Voxel-Brew/BOM")
                    connection.set("scm:git:https://github.com/Voxel-Brew/BOM.git")
                    developerConnection.set("scm:git:ssh://git@github.com/Voxel-Brew/BOM.git")
                }
            }
        }
    }
    repositories {
        maven {
            name = "verification"
            url = uri(layout.buildDirectory.dir("repository"))
        }
        maven {
            name = "GitHubPackages"
            url = uri("https://maven.pkg.github.com/voxel-brew/bom")
            credentials {
                username = providers.environmentVariable("GITHUB_ACTOR")
                    .orElse(providers.gradleProperty("githubPackagesUser")).orNull
                password = providers.environmentVariable("GITHUB_TOKEN")
                    .orElse(providers.gradleProperty("githubPackagesToken")).orNull
            }
        }
    }
}
