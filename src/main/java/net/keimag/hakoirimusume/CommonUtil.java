package net.keimag.hakoirimusume;

import org.springframework.core.io.ClassPathResource;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;

public class CommonUtil {
    private CommonUtil() {}

    public static String loadTextResource(String path) throws IOException {
        InputStream inputStream = new ClassPathResource(path).getInputStream();
        return new String(inputStream.readAllBytes(), StandardCharsets.UTF_8);
    }
}
