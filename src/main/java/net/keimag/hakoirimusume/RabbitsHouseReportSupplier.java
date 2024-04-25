package net.keimag.hakoirimusume;

import com.linecorp.bot.messaging.model.FlexMessage;
import org.slf4j.Logger;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.function.Supplier;

public class RabbitsHouseReportSupplier implements Supplier<FlexMessage> {
    private static final Logger log = org.slf4j.LoggerFactory.getLogger(RabbitsHouseReportSupplier.class);

    private final String templateJson;

    public RabbitsHouseReportSupplier(String templateJsonPath) {
        String content = null;
        try {
            content = Files.readString(Path.of(templateJsonPath));
        } catch(IOException ex) {
            ex.printStackTrace();
        }
        this.templateJson = content;
    }

    private String getReportJson() {
        double temp = 25.0;
        double humidity = 50.0;
        double pressure = 1013.0;
        String imageUri = null;
        String reportJson = templateJson;
        Calendar c = Calendar.getInstance();
        SimpleDateFormat df = new SimpleDateFormat("yyyy/MM/dd HH:mm:ss");
        String currentTime = df.format(c.getTime());
        reportJson = reportJson.replace("{{CurrentTime}}", currentTime);
        reportJson = reportJson.replace("{{Temperature}}", String.valueOf(temp));
        reportJson = reportJson.replace("{{Humidity}}", String.valueOf(humidity));
        reportJson = reportJson.replace("{{Pressure}}", String.valueOf(pressure));
        reportJson = reportJson.replace("{{Message}}", "今のところは快適だよ！");
        if (imageUri != null) {
            reportJson = reportJson.replace("https://i.imgur.com/Z5GS685.jpeg", imageUri);
        }
        return reportJson;
    }

    public FlexMessage get() {
        return new FlexMessageBuilder().build("Rabbit's House Report", getReportJson());
    }

    public FlexMessage alert() {
        String contents = getReportJson();
        contents = contents.replace("Rabbit's House Report", "Rabbit's House Alert！");
        contents = contents.replace("#1DB446", "#DC3545");
        contents = contents.replace("#FFFFFF", "#DC3545");
        return new FlexMessageBuilder().build("Rabbit's House Alert！", contents);
    }
}
