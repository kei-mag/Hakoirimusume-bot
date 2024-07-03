package net.keimag.hakoirimusume;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.linecorp.bot.messaging.client.MessagingApiClient;
import com.linecorp.bot.messaging.model.Message;
import com.linecorp.bot.messaging.model.PushMessageRequest;
import com.linecorp.bot.messaging.model.TextMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;

import java.io.IOException;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.*;

@Service
public class RabbitsHouseAlertService {
    private static final Logger log = LoggerFactory.getLogger(RabbitsHouseAlertService.class);
    private final HakoirimusumeProperties.AlertProperties alertProperties;
    private final RabbitsHouseReportSupplier rabbitsHouseReportSupplier;
    private final SensorService sensorService;
    private Calendar disableAlertPeriod = null;
    private final MessagingApiClient messagingApiClient;
    private final ApplicationIntegration applicationIntegration;
    private int alertCount = 0;
    private final DateTimeFormatter dateFormatter = DateTimeFormatter.ofPattern("yyyyMMdd");
    private final DateTimeFormatter timeFormatter = DateTimeFormatter.ofPattern("HHmmss");

    @Autowired
    public RabbitsHouseAlertService(HakoirimusumeProperties hakoirimusumeProperties, SensorService sensorService, RabbitsHouseReportSupplier rabbitsHouseReportSupplier, MessagingApiClient messagingApiClient, ApplicationIntegration applicationIntegration) {
        this.alertProperties = hakoirimusumeProperties.getAlert();
        this.rabbitsHouseReportSupplier = rabbitsHouseReportSupplier;
        this.sensorService = sensorService;
        this.messagingApiClient = messagingApiClient;
        this.applicationIntegration = applicationIntegration;
    }

    @Scheduled(fixedDelayString = "${hakoirimusume.alert.polling-interval-sec}000", initialDelay = 300000)
    public void alert() {
        var data = sensorService.getSensorData();
        log.debug("alert() was called. data: {}", data);
        if (data == null || (data.temperature() == 0.0 && data.humidity() == 0.0 && data.pressure() == 0.0)) {
            log.warn("Sensor data is not available.");
        } else {
            var condition = alertProperties.getCondition();
            double triggerTemp = 1000;
            double triggerHum = 1000;
            if (condition.getTemperature() != null) {
                triggerTemp = condition.getTemperature();
            }
            if (condition.getHumidity() != null) {
                triggerHum = condition.getHumidity();
            }
            if (data.temperature() >= triggerTemp && data.humidity() >= triggerHum) {
                // Alert condition is satisfied.
                var actionProperties = alertProperties.getAction();
                var result = triggerAction();
                var triggerLimit = alertProperties.getTriggerLimit();
                if ((disableAlertPeriod == null || Calendar.getInstance().after(disableAlertPeriod)) && (triggerLimit.getDailyLimit() < 0 || alertCount < triggerLimit.getDailyLimit())){
                    // Send alert message.
                    try {
                        var message = rabbitsHouseReportSupplier.alert();
                        List<Message> messages = new ArrayList<>(Arrays.asList(message));
                        if (result != null) {
                            if (result) {
                                messages.add(new TextMessage(actionProperties.getSuccessMessage()));
                            } else {
                                messages.add(new TextMessage(actionProperties.getFailureMessage()));
                            }
                        }
                        alertProperties.getTo().forEach(to -> {
                            messagingApiClient.pushMessage(UUID.randomUUID(), new PushMessageRequest(
                                    to,
                                    messages,
                                    false,
                                    null
                            ));

                        });
                    } catch (IOException | InterruptedException e) {
                        log.warn("Failed to send alert message: {}", e.getMessage());
                    }
                    if (triggerLimit.getInterval() > 0) {
                        disableAlertPeriod = Calendar.getInstance();
                        disableAlertPeriod.add(Calendar.HOUR, triggerLimit.getInterval());
                    }
                    alertCount++;
                }
            }
        }
    }

    private Boolean triggerAction() {
        var actionProperties = alertProperties.getAction();
        String target = replacePlaceHolders(actionProperties.getTarget());
        String header = replacePlaceHolders(actionProperties.getHeader());
        String body = replacePlaceHolders(actionProperties.getBody());
        if (actionProperties.getType() == null) {
            return null;
        } else {
            int statusCode;
            switch (actionProperties.getType()) {
            case "GET":
                try {
                    statusCode = applicationIntegration.get(actionProperties.getTarget()).statusCode();
                } catch (RestClientException e) {
                    log.warn("Failed to send GET request: {}", e.getMessage());
                    return false;
                }
                if (statusCode >= 200 && statusCode < 300) {
                    log.info("GET request to {} is successful.", actionProperties.getTarget());
                    return true;
                } else {
                    log.warn("GET request to {} failed with status code {}.", actionProperties.getTarget(), statusCode);
                    return false;
                }
            case "POST":
                ObjectMapper objectMapper = new ObjectMapper()
                        .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
                try {
                    var headerMap = objectMapper.readValue(header, new TypeReference<Map<String, Object>>() {
                    });
                    var bodyMap = objectMapper.readValue(body, new TypeReference<Map<String, Object>>() {
                    });
                    headerMap.put("Content-Type", "application/json");
                    try {
                        statusCode = applicationIntegration.post(actionProperties.getTarget(), headerMap, bodyMap).statusCode();
                    } catch (RestClientException e) {
                        log.warn("Failed to send POST request: {}", e.getMessage());
                        return false;
                    }
                    if (statusCode >= 200 && statusCode < 300) {
                        log.info("POST request to {} is successful.", actionProperties.getTarget());
                        return true;
                    } else {
                        log.warn("POST request to {} failed with status code {}.", actionProperties.getTarget(), statusCode);
                        return false;
                    }
                } catch (JsonProcessingException e) {
                    log.warn("Failed to parse header or body JSON: {}", e.getMessage());
                    return false;
                }
            case "COMMAND":
                try {
                    statusCode = applicationIntegration.exec(target).statusCode();
                } catch (RuntimeException e) {
                    log.warn("Failed to execute command: {}", e.getMessage());
                    return false;
                }
                if (statusCode == 0) {
                    return true;
                } else {
                    log.warn("Command execution failed with status code {}.", statusCode);
                    return false;
                }
            }
        }
        return null;
    }

    private String replacePlaceHolders(String text) {
        if (text == null) {
            return "";
        }
        LocalDateTime localDateTime = LocalDateTime.now();
        if (rabbitsHouseReportSupplier.latestGetTime != null){
            localDateTime = LocalDateTime.ofInstant(rabbitsHouseReportSupplier.latestGetTime.toInstant(), ZoneId.systemDefault());
        }
        Map<String, String> placeHolders = Map.of(
                "{{TEMP}}", String.valueOf(rabbitsHouseReportSupplier.latestTemperature),
                "{{HUMID}}", String.valueOf(rabbitsHouseReportSupplier.latestHumidity),
                "{{PRESSURE}}", String.valueOf(rabbitsHouseReportSupplier.latestPressure),
                "{{DATE}}", localDateTime.format(dateFormatter),
                "{{TIME}}", localDateTime.format(timeFormatter),
                "{{IMAGE_URL}}", String.valueOf(rabbitsHouseReportSupplier.latestImageUri)
        );
        for (Map.Entry<String, String> entry : placeHolders.entrySet()) {
            text = text.replace(entry.getKey(), entry.getValue());
        }
        return text;
    }

}
