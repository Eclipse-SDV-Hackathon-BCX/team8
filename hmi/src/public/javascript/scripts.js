"use strict";

// If deployed to a site supporting SSL, use wss://
const httpProtocol = document.location.protocol.startsWith("https") ? "wss://" : "ws://";
let ws = undefined;
function start() {
  ws = new WebSocket(httpProtocol + location.host);
  ws.onopen = () => {
    console.log("Websocket connection is open.");
  };

  ws.onclose = function () {
    console.log("Server is down trying to reconnect...");
    // Try to reconnect in 2 seconds
    ws = null;
    setTimeout(start, 2000);
  };
}
start();

// Listen for messages.
ws.addEventListener("message", function (event) {
  const rxData = JSON.parse(event.data);
  if (rxData.path) {
    setDomId(rxData.path, rxData.value);
  } else {
    console.log(rxData);
  }
});
function setDomId(path, value) {
  var domText = document.getElementById(path);
  if (domText) {
    domText.textContent = value;
  }

  if (path == "Vehicle.Chassis.SteeringWheel.Angle") {
    let gaugeVal = 0.5;
    if (value > -90 || value < 90) {
      gaugeVal = (90 - value) / 180;
    }
    // console.log(gaugeVal);
    setGauge1Value(gauge1Element, gaugeVal);
  } else if (path == "Vehicle.Chassis.SteeringWheel.AngleAct") {
    let gaugeVal = 0.5;
    if (value > -90 || value < 90) {
      gaugeVal = (90 - value) / 180;
    }
    // console.log(gaugeVal);
    setGauge2Value(gauge2Element, gaugeVal);
  }
}

const gauge1Element = document.querySelector(".gauge1");
function setGauge1Value(gauge, value) {
  if (value < 0 || value > 1) {
    return;
  }

  gauge.querySelector(".gauge1__fill").style.transform = `rotate(${value / 2}turn)`;
  gauge.querySelector(".gauge1__cover").textContent = `${Math.round(90 - value * 180)}°`;
}

const gauge2Element = document.querySelector(".gauge2");
function setGauge2Value(gauge, value) {
  if (value < 0 || value > 1) {
    return;
  }
  gauge.querySelector(".gauge2__fill").style.transform = `rotate(${value / 2}turn)`;
  gauge.querySelector(".gauge2__cover").textContent = `${Math.round(90 - value * 180)}°`;
}
