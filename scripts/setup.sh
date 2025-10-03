mkdir /opt/vk2vless/etc /opt/vk2vless/var
chown nobody:nogroup /opt/vk2vless/var

touch /opt/vk2vless/etc/env

mkdir -p /opt/vk2vless/etc/configstore/@vkontakte
touch /opt/vk2vless/etc/configstore/@vkontakte/vk-tunnel.json
