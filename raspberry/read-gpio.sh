#!/bin/sh

# GPIO setup:
# Pin 3 (GPIO0): switch 
# Pin 5 (GPIO1): Red LED
# Pin 6: GND
# Pin 7 (GPIO4): Green LED

cleanup() {
	echo "0" > /sys/class/gpio/gpio0/value
	echo "0" > /sys/class/gpio/gpio1/value
	echo "0" > /sys/class/gpio/gpio4/value

	echo "0" > /sys/class/gpio/unexport
	echo "1" > /sys/class/gpio/unexport
	echo "4" > /sys/class/gpio/unexport
	exit;
}

trap cleanup TERM EXIT

echo "0" > /sys/class/gpio/export
echo "in" > /sys/class/gpio/gpio0/direction
echo "1" > /sys/class/gpio/export
echo "out" > /sys/class/gpio/gpio1/direction
echo "4" > /sys/class/gpio/export
echo "out" > /sys/class/gpio/gpio4/direction

LED="RED"
while (true); do
	sleep 0.02;

	if [ "`cat /sys/class/gpio/gpio0/value`" -lt 1 ]; then
		if [ "$LED" = "GREEN" ]; then
			LED="RED";
			echo 1 > /sys/class/gpio/gpio1/value;
			echo 0 > /sys/class/gpio/gpio4/value;
		elif [ "$LED" = "RED" ]; then
			LED="GREEN";
			echo 0 > /sys/class/gpio/gpio1/value;
			echo 1 > /sys/class/gpio/gpio4/value;
		fi;

		echo $LED;
		sleep 1;
	fi;
done

