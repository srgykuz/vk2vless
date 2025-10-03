wget -O /tmp/node-v22.20.0-linux-x64.tar.xz https://nodejs.org/dist/v22.20.0/node-v22.20.0-linux-x64.tar.xz
tar -C /tmp -xf /tmp/node-v22.20.0-linux-x64.tar.xz
rm /tmp/node-v22.20.0-linux-x64.tar.xz
mv /tmp/node-v22.20.0-linux-x64 /usr/local

ln -s /usr/local/node-v22.20.0-linux-x64/bin/node /usr/local/bin/node
ln -s /usr/local/node-v22.20.0-linux-x64/bin/npm /usr/local/bin/npm
ln -s /usr/local/node-v22.20.0-linux-x64/bin/npx /usr/local/bin/npx
ln -s /usr/local/node-v22.20.0-linux-x64/bin/corepack /usr/local/bin/corepack
