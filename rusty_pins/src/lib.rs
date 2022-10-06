//Other people's hard work
use pyo3::prelude::*;
use rppal_w_frontend::gpio::Gpio;
use rppal_w_frontend::gpio::OutputPin;
use rppal_w_frontend::gpio::InputPin;

// A safe, Python-ready GPIO output class that operates on the hardware level
#[pyclass(unsendable)]
struct GpioOut{output: OutputPin}

// Behavior of the GPIO output class
#[pymethods]
impl GpioOut { 
    #[new] // call this from python with rusty_pins.GpioOut(pin#)
    fn new(pin: u8) -> Self { //this is like python __init__()
        let io_pin = Gpio::new().unwrap().get(pin).unwrap().into_output();
        GpioOut{output: io_pin}
    }
    
    fn set_high(&mut self){
        self.output.set_high();
    }

    fn set_low(&mut self){
        self.output.set_low();
    }

}

// A Python-ready GPIO input class
#[pymodule]
fn rusty_pins(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_class::<GpioOut>()?;
    Ok(())
}