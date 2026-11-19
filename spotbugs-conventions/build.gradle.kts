plugins { `groovy-gradle-plugin` }

repositories {
    gradlePluginPortal()
    mavenCentral()
}

dependencies {
    implementation("com.github.spotbugs:com.github.spotbugs.gradle.plugin:6.5.13")
}
