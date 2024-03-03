const WebSocket = require("ws");
const WebSocketJSONStream = require("@teamwork/websocket-json-stream");
const ShareDB = require("sharedb");
const express = require("express");
const http = require("http");
const cors = require('cors');

const app = express();

// middleware
app.use(cors());

const server = http.createServer(app); 
const webSocketServer = new WebSocket.Server({ server: server });  

/**
 * By Default Sharedb uses JSON0 OT type.
 * To Make it compatible with our quill editor.
 * We are using this npm package called rich-text
 * which is based on quill delta
 */
ShareDB.types.register(require("rich-text").type);

const shareDBServer = new ShareDB();
const connection = shareDBServer.connect();

/**
 * 'documents' is collection name(table name in sql terms)
 * 'firstDocument' is the id of the document
 */
const doc = connection.get("documents", "firstDocument");

webSocketServer.on("connection", (webSocket) => {
  const stream = new WebSocketJSONStream(webSocket);
  shareDBServer.listen(stream);
});


webSocketServer.on("error", (err) => {
    console.log("🚀 ~ webSocketServer.on ~ err:", err) 
})

doc.fetch(function (err) {
  if (err) throw err;
  if (doc.type === null) {
    /** 
     * If there is no document with id "firstDocument" in memory
     * we are creating it and then starting up our ws server
     */
    doc.create([{ insert: "Hello World!" }], "rich-text");
    return;
  }
});

app.post('/docs/:name', (req, res) => {
    const filename = req.params.name;
    const doc = connection.get("documents", filename);
    
    doc.fetch(function (err) {
        if (err) throw err;
        if (doc.type === null) {
          /** 
           * If there is no document with id "firstDocument" in memory
           * we are creating it and then starting up our ws server
           */
          doc.create([{ insert: "Welcome to the best collaborative tool!" }], "rich-text");
          return;
        } 
      });

      res.sendStatus(200)
})

server.listen(8080);
