package net.keimag.hakoirimusume;

import com.pi4j.Pi4J;


public class BME280Driver {
    private final int i2cBusNumber;
    private final int addr;

    public BME280Driver(int i2cBusNumber, int addr) {
         this.i2cBusNumber = i2cBusNumber;
         this.addr = addr;
    }

    


}
