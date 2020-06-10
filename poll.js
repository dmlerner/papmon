const { Client } = require('tplink-smarthome-api');
var fs = require('fs');
const EventEmitter = require('events');

function getTime() {
	var d = new Date();
	return d.getTime();
}

function write(x) {
	var timestamp = getTime();
	var path = 'data/resmed';
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
		write(update.power_mw);
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
