package dev.voxelbrew.quality

import org.gradle.api.DefaultTask
import org.gradle.api.file.RegularFileProperty
import org.gradle.api.provider.Property
import org.gradle.api.tasks.CacheableTask
import org.gradle.api.tasks.Input
import org.gradle.api.tasks.OutputFile
import org.gradle.api.tasks.TaskAction

@CacheableTask
abstract class WriteSpotBugsFilter extends DefaultTask {
    @Input
    abstract Property<String> getFilterContents()

    @OutputFile
    abstract RegularFileProperty getFilterFile()

    @TaskAction
    void writeFilter() {
        def destination = filterFile.get().asFile
        destination.parentFile.mkdirs()
        destination.setText(filterContents.get(), 'UTF-8')
    }
}
