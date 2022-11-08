"use strict";
/*
 *  Created by Wieger IJntema on 2022
 *  Copyright © 2020-2022 IAV GmbH. All rights reserved.
 */

const express = require("express");
const http = require("http");
const path = require("path");
const WebSocket = require("ws");
const createError = require("http-errors");
const grpc = require("@grpc/grpc-js");
const protoLoader = require("@grpc/proto-loader");
require("dotenv").config();

const k = require("./components/kuksa-sdk.js");

const PROTO_PATH = "./" + process.env.PROTO_FILES;
// console.log(PROTO_PATH);

const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
});
const protoDef = grpc.loadPackageDefinition(packageDefinition).kuksa.val.v1;
const kuksaServerAddress = process.env.KUKSA_SERVER + ":" + process.env.KUKSA_PORT;

const kuksaClient = new protoDef.VAL(kuksaServerAddress, grpc.credentials.createInsecure());

let counter = 33;
k.setFieldValue(kuksaClient, "Vehicle.Chassis.SteeringWheel.Angle", 23);
setInterval(() => {
  counter++;
  k.setFieldValue(kuksaClient, "Vehicle.Chassis.SteeringWheel.Angle", counter);
}, 10000);

// k.getCurrentValue(kuksaClient, "Vehicle.Chassis.SteeringWheel.Angle", (result) => {
//   console.log("Get current steering angle:", result);
// });

k.subscribe(kuksaClient, "Vehicle.Chassis.SteeringWheel.Angle", (data) => {
  console.log("Notify: ", data);
});

// Create an express app.
const app = express();

/* GET home page. */
app.use(express.static("public"));

// catch 404 and forward to error handler
app.use(function (req, res, next) {
  next(createError(404));
});

// Add the app to the http server.
const server = http.createServer(app);

// Create a websocket server.
const wss = new WebSocket.Server({ server });

// Create a websocket broadcast function that sends data to all browser sessions.
wss.broadcast = (data) => {
  wss.clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      try {
        client.send(data);
      } catch (e) {
        console.error(e);
      }
    } else {
      console.log("Warning, the websocket is not open yet.");
    }
  });
};

// On an incomming message over Websocket (browser) we need to execute something on the device.
wss.on("connection", (ws) => {
  ws.on("message", (message) => {
    try {
      const msg = JSON.parse(message);

      // An incomming websocket message needs the following structure:
      // msg = {
      //   commandName: "<you command name>"
      //   payload: <your data>
      // }
      if (!msg.commandName) {
        console.error("commandName was not set in this Websocket message from the browser. This is required.");
        console.error(msg);
        return;
      }

      if (msg.commandName == "getHistory") {
        sqlDatabase
          .getData()
          .then((data) => {
            const payload = {
              messageType: "historyFromDatabase",
              data: data,
            };
            console.log("Got data from the Database forwaring to browser now...");
            wss.broadcast(JSON.stringify(payload));
          })
          .catch((err) => {
            console.error("ERROR: Something went wrong.", err);
          });
      } else {
        handleCloudToDeviceMsg(msg);
      }
    } catch (e) {
      console.warn("Warning: could not JSON.parse() incomming websocket message.", e);
    }
  });
});

wss.on("close", () => {
  console.warn("Websocket connection closed.");
});

// Start serving the webpage.
var port = process.env.PORT || "3000";
app.set("port", port);
server.listen(port, function listening() {
  console.log("WebApp available in browser on http://localhost:%d", server.address().port);
});
server.on("error", onError);

/**
 * Event listener for HTTP server "error" event.
 */

function onError(error) {
  if (error.syscall !== "listen") {
    throw error;
  }

  var bind = typeof port === "string" ? "Pipe " + port : "Port " + port;

  // handle specific listen errors with friendly messages
  switch (error.code) {
    case "EACCES":
      console.error(bind + " requires elevated privileges");
      process.exit(1);
      break;
    case "EADDRINUSE":
      console.error(bind + " is already in use");
      process.exit(1);
      break;
    default:
      throw error;
  }
}
