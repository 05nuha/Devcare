plugins {
    id("java")
    id("org.jetbrains.kotlin.jvm") version "2.3.0"
    id("org.jetbrains.intellij.platform") version "2.11.0"
}

group = "com.devcare"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()

    intellijPlatform {
        defaultRepositories()
    }
}

dependencies {
    intellijPlatform {
        intellijIdeaCommunity("2024.1")
        instrumentationTools()
    }
}

kotlin {
    jvmToolchain((17))
}

intellijPlatform {
    pluginConfiguration {
        name = "DevCare"
        version = "1.0.0"

        ideaVersion {
            sinceBuild = "241"
            untilBuild = "243.*"
        }
    }
}

tasks {
    buildSearchableOptions {
        enabled = false
    }
}