const WebSocket = require('ws');
var fs = require('fs');
const wss = new WebSocket.Server({ port: 7071 });

const clients = new Map();

wss.on('connection', (ws) => {
	const metadata = {};

	clients.set(ws, metadata);

	fs.readFile('content.md', 'utf8', (err, data) => {
		const message = {
			type: 'content.md',
			data: data
		};
		ws.send(JSON.stringify(message));
	});

	ws.on("close", () => {
		clients.delete(ws);
	});
});

function broadcast(message) {
	[...clients.keys()].forEach((client) => {
		client.send(JSON.stringify(message));
	});
}

let _mtime = 0, mtime = 0;
setInterval(() => {
	fs.stat('content.md', (err, stats) => {
		mtime = stats.mtime.getTime();

		if (mtime != _mtime) {
			fs.readFile('content.md', 'utf8', (err, data) => {
				const message = {
					type: 'content.md',
					data: data
				};
				broadcast(message);
			});
		}
		_mtime = mtime;
	});
}, 1000);













