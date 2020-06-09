const { Client } = require('tplink-smarthome-api');
const EventEmitter = require('events');

const client = new Client();
const plug = client.getDevice({host: '192.168.1.45'})
	.then((device)=>{
		var pol = device.startPolling(50);
		pol.on('emeter-realtime-update', (x)=>{
			var d = new Date();
			var n = d.getTime();
			console.log(x, n);
		});


		// e.getRealtime().then(console.log);
	});
/*
	// Look for devices, log to console, and turn them on
client.startDiscovery().on('device-new', (device) => {
  device.getSysInfo().then(console.log);
  device.setPowerState(true);
});
*/
