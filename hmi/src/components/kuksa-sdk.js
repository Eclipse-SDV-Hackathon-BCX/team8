"use strict";
/*
 *  Created by Wieger IJntema on 2022
 *  Copyright © 2020-2022 IAV GmbH. All rights reserved.
 */

function unixTimestampSeconds() {
  return Math.floor(Date.now() / 1000);
}

const subscribeList = {};
// {
//   path: callback
// }

function setFieldValue(client, path, value) {
  const datapoint = {
    timestamp: {
      seconds: unixTimestampSeconds(),
      nanos: 0,
    },
  };
  if (typeof value == "string") {
    datapoint.string = value;
  } else if (typeof value == "number") {
    datapoint.int32 = value;
  }

  // console.log("Datapoint:", datapoint);
  const entryUpdate = {
    entry: {
      path: path,
      value: datapoint,
    },
    fields: ["FIELD_VALUE"],
  };
  // console.log("EntryUpdate:", entryUpdate);
  const setRequest = {
    updates: [entryUpdate],
  };
  // console.log(setRequest.updates);

  client.Set(setRequest, function (err, response) {
    if (response.errors.length == 0) {
      // Success!
      console.log("Set:", path, " FIELD_VALUE: ", value, " OK!");
    } else {
      console.log("Set response errors:", response.errors);
    }
  });
}

async function getCurrentValue(client, path, cb) {
  const getRequest = {
    entries: [
      {
        path: path,
        view: "VIEW_CURRENT_VALUE",
      },
    ],
  };
  client.Get(getRequest, (err, response) => {
    // console.log("Get response:", response.entries[0].value);
    const valueKey = response.entries[0].value.value;
    cb(response.entries[0].value[valueKey]);
  });
}

async function subscribe(client, path, cb) {
  // register callback
  subscribeList[path] = cb;

  const subscribeRequest = {
    entries: [
      {
        path: path,
        fields: ["FIELD_VALUE"],
      },
    ],
  };
  const call = client.Subscribe(subscribeRequest);

  call.on("data", (data) => {
    const valueKey = data.updates[0].entry.value.value;
    // console.log(data.updates[0].entry.value[valueKey]);
    subscribeList[path](data.updates[0].entry.value[valueKey]);
  });
  call.on("end", () => {
    // The server has finished sending
    console.log("server stopped");
  });
  call.on("error", (e) => {
    // An error has occurred and the stream has been closed.
    console.log("server stopped because of error:", e);
  });
  call.on("status", (status) => {
    // process status
    console.log(status);
  });
}

module.exports = {
  setFieldValue,
  getCurrentValue,
  subscribe,
};
