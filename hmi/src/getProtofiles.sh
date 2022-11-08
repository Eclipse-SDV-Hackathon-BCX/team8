mkdir -p kuksa/val/v1
cd kuksa/val/v1
curl https://raw.githubusercontent.com/eclipse/kuksa.val/master/proto/kuksa/val/v1/types.proto --output types.proto
curl https://raw.githubusercontent.com/eclipse/kuksa.val/master/proto/kuksa/val/v1/val.proto --output val.proto
