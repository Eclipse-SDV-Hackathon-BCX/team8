// If deployed to a site supporting SSL, use wss://
const protocol = document.location.protocol.startsWith("https") ? "wss://" : "ws://";
const webSocket = new WebSocket(protocol + location.host);

// Open websocket.
webSocket.addEventListener("open", function (event) {
  console.log("Websocket connection is open.");
});

// Listen for messages.
webSocket.addEventListener("message", function (event) {
  const rxData = JSON.parse(event.data);
  if (rxData.path == "Vehicle.Driver.Identifier.Subject") {
    setVehicleId(rxData.value);
  } else {
    console.log(rxData);
  }
});

// Handle toggle button
function setVehicleId(id) {
  var domText = document.getElementById("vehicle-driver-id");
  domText.textContent = "Found: " + id;
}
