package net.keimag.hakoirimusume;

public class BME280Test {
    public static void main(String[] args) throws InterruptedException {
        BME280 bme280 = new BME280(1, 0x76);
        for (int i = 1; i < 10; i++) {
            System.out.println(bme280.getMeasurements());
            Thread.sleep(20000);
        }
    }
}
