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

function setFieldValueType(client, path, value, type) {
  const datapoint = {
    timestamp: {
      seconds: unixTimestampSeconds(),
      nanos: 0,
    },
  };
  datapoint[type] = value;

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
    if (response && response.errors && response.errors.length == 0) {
      // Success!
      console.log("Set:", path, " FIELD_VALUE: ", value, " OK!");
    } else {
      console.log("Set response errors:", response.errors);
    }
  });
}

function setFieldValue(client, path, value) {
  if (typeof value == "string") {
    setFieldValueType(client, path, value, "string");
  } else if (typeof value == "number") {
    setFieldValueType(client, path, value, "int32");
  }
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
  client.Get(getRequest, (err, resp) => {
    // console.log("Get response:", response.entries[0]);
    if (resp.entries[0].value) {
      const valueKey = resp.entries[0].value.value;
      cb(resp.entries[0].value[valueKey]);
    } else {
      cb(undefined);
    }
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
    // console.log(data.updates[0].entry);
    if (data.updates[0].entry.value) {
      const valueKey = data.updates[0].entry.value.value;
      // console.log(data.updates[0].entry.value[valueKey]);
      subscribeList[path](undefined, data.updates[0].entry.value[valueKey]);
    } else {
      subscribeList[path](undefined, undefined);
    }
  });
  call.on("end", () => {
    // The server has finished sending
    console.log("GRPC server stopped the connection.");
  });
  call.on("error", (e) => {
    // An error has occurred and the stream has been closed.
    console.log("GRPC server stopped because of error:", e);
    subscribeList[path](e, undefined);
  });
  call.on("status", (status) => {
    // process status
    console.log(status);
  });
}

module.exports = {
  setFieldValue,
  setFieldValueType,
  getCurrentValue,
  subscribe,
};
