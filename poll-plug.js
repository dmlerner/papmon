const { Client } = require('tplink-smarthome-api');
var fs = require('fs');
const EventEmitter = require('events');

const filename = (new Date()).toISOString();

function write(x) {
	var timestamp = (new Date()).getTime() / 1000; // seconds since epoch
	var path = 'data/power/' + filename;
	fs.appendFile(
		path, 
		timestamp + ' ' + x + '\n',
		(err) => {
			if (err) throw err;
		});
}

function pollWriteWattage(device) {
	if (!device) {
		return;
	}
	var poll = device.startPolling(100); // ms 
	poll.on('emeter-realtime-update', (update) => {
		write(update.power_mw / 1000); // write wattage
	});
}

function main() {
	const client = new Client();
	client.startDiscovery()
		.on('device-new', (device) => {   
			device
				.getSysInfo()
				.then((info) => {
					if (info.alias == 'resmed') {
						return device;
					}
				})
				.then(pollWriteWattage);
		});
}

main();
