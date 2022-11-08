"use strict";
/*
 *  Created by Jan Weber on 2022
 *  Copyright © 2020-2022 IAV GmbH. All rights reserved.
 */

const path = require("path");
const grpc = require("@grpc/grpc-js");
const protoLoader = require("@grpc/proto-loader");
require("dotenv").config();

const kuksa = require("./components/kuksa-sdk.js");
const { DefaultSerializer } = require("v8");

const PROTO_PATH = "./" + process.env.PROTO_FILES;
// console.log(PROTO_PATH);

const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
  includeDirs: ["./"]
});
const protoDef = grpc.loadPackageDefinition(packageDefinition).kuksa.val.v1;
const kuksaServerAddress = process.env.KUKSA_SERVER + ":" + process.env.KUKSA_PORT;

const kuksaClient = new protoDef.VAL(kuksaServerAddress, grpc.credentials.createInsecure());



let activeUser = "";
let userType = "good";
let acting = false;

let badUsers = [ "32" ];

let delay = 750;


let topic = {
  accelAct : "Vehicle.Chassis.Accelerator.PedalPositionAct",
  accel : "Vehicle.Chassis.Accelerator.PedalPosition",
  steer: "Vehicle.Chassis.SteeringWheel.Angle",
  steerAct: "Vehicle.Chassis.SteeringWheel.AngleAct",
  gear : "Vehicle.Powertrain.Transmission.CurrentGear",
  gearAct: "Vehicle.Powertrain.Transmission.SelectedGear"
}


// let counter = 33;
// setInterval(() => {
//   counter++;
//   kuksa.setFieldValue(kuksaClient, "Vehicle.Driver.Identifier.Subject", counter.toString());
// }, 1000);

// k.getCurrentValue(kuksaClient, "Vehicle.Driver.Identifier.Subject", (result) => {
//   console.log("Get current steering angle:", result);
// });


function flee() {
  acting = true

  kuksa.setFieldValue(kuksaClient,topic.accelAct,-45)
  setTimeout( () => {
    kuksa.setFieldValue(kuksaClient,topic.accelAct,+45)
    acting = false
  }, delay*5 )

}

function enjoy() {
  acting = true

  kuksa.setFieldValue(kuksaClient,"Vehicle.Chassis.SteeringWheel.AngleAct",-45)

  setTimeout( () => {
    kuksa.setFieldValue(kuksaClient,"Vehicle.Chassis.SteeringWheel.AngleAct",+45)
  }, delay )

  setTimeout( () => {
    kuksa.setFieldValue(kuksaClient,"Vehicle.Chassis.SteeringWheel.AngleAct",-45)
  }, delay*2)

  setTimeout( () => {
    kuksa.setFieldValue(kuksaClient,"Vehicle.Chassis.SteeringWheel.AngleAct",+45)
  }, delay*3 )

  setTimeout( () => {
    kuksa.setFieldValue(kuksaClient,"Vehicle.Chassis.SteeringWheel.AngleAct",0)
    acting= false
  }, delay*4 )

}




kuksa.subscribe(kuksaClient, "Vehicle.Driver.Identifier.Subject", (data) => {
  if ( data != null && data != "" && data != activeUser && !acting) {
    console.log("New User: ", data)
    // if user is a bad user flee, otherwise welcome him/her
    if ( badUsers.includes(data)  )  {
      userType = "bad"
      flee()
    } else {
      userType = "good"
      enjoy()
    }
  }
});

kuksa.subscribe(kuksaClient, topic.steer, (data) => {
  if ( data != null && data != "" && !acting ) {
    console.log("Steering Angle: ", data)
    kuksa.setFieldValue(kuksaClient,topic.steerAct,data)
  }

});


kuksa.subscribe(kuksaClient, topic.accel , (data) => {
  if ( data != null && data != "" && !acting) {
    console.log("Accelerator: ", data)
    let dataAct= data
    if (userType === "bad") {
      dataAct = Math.min([data,20])
    }
    kuksa.setFieldValue(kuksaClient,topic.accelAct,dataAct)
  }
});



kuksa.subscribe(kuksaClient, topic.gear, (data) => {
  if ( data != null && data != "" && !acting) {
    console.log("Transmission: ", data)
    kuksa.setFieldValue(kuksaClient,topic.gearAct,data)

  }
});


 


// Vehicle.Chassis.Accelerator.PedalPositionAct 
// Vehicle.Chassis.SteeringWheel.AngleAct 
// Vehicle.Powertrain.Transmission.SelectedGear 
