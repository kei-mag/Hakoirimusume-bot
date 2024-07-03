package net.keimag.hakoirimusume;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.ClassPathResource;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;

public class CommonUtil {
    private static final Logger log = LoggerFactory.getLogger(CommonUtil.class);
    private CommonUtil() {}

    public static String loadTextResource(String path) throws IOException {
        try {
            InputStream inputStream = new ClassPathResource(path.replace("src/main/resources/", "")).getInputStream();
            return new String(inputStream.readAllBytes(), StandardCharsets.UTF_8);
        } catch (FileNotFoundException e) {
            log.warn("File not found in classpath: {}\nTrying to load from file system...", path);
            return java.nio.file.Files.readString(java.nio.file.Paths.get(path));
        }
    }
}
