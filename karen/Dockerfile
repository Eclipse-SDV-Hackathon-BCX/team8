#
# Created by Wieger IJntema 2022
# Copyright © 2022 IAV GmbH. All rights reserved.
#

FROM node:14.19-alpine3.16
ENV PROTO_FILES kuksa/val/v1/val.proto
ENV KUKSA_SERVER 172.17.0.1
ENV KUKSA_PORT 55555


WORKDIR /opt/app


COPY --chown=node:node src/package*.json ./
RUN npm ci --only=production

COPY --chown=node:node src/ ./
#RUN npm run build

ENTRYPOINT ["/bin/sh", "-c"]
CMD [ "node main.js" ]
