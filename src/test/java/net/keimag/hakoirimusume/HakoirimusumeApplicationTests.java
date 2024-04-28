package net.keimag.hakoirimusume;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

import net.keimag.hakoirimusume.BME280Driver;

@SpringBootTest
class HakoirimusumeApplicationTests {

	@Test
	void contextLoads() {
		var bme280 = new BME280Driver(1, 0x76);
		bme280.read();
	}

}
