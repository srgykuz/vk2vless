# vk2vless

Этот проект может быть использован для обхода белого списка. Он запускает VK Tunnel, генерирует VLESS и VMess конфигурации, обеспечивает доступность этих конфигураций без ВПН в условиях белого списка.

## Доступность

Убедитесь, что https://tunnel.vk-apps.com и https://translated.turbopages.org открываются в условиях белого списка. Этот проект использует эти адреса для создания и публикации конфига. Если они не работают, то этот проект вам не подходит.

## Установка

Подразумевается, что установка происходит на чистый сервер с root-доступом. Если вы не `root` или получаете ошибку `permission denied`, то выполняйте все команды с `sudo`, например: `sudo apt install`.

### 1. Установите зависимости:

```bash
apt install -y python3 git wget tar nano
```

### 2. Скачайте проект:

```bash
git clone https://github.com/srgykuz/vk2vless.git /opt/vk2vless
cd /opt/vk2vless
chmod -R 755 ./scripts
```

### 3. Установите зависимости:

```bash
./scripts/install.sh
./scripts/install_node.sh
./scripts/install_vk.sh
```

### 4. Авторизуйте VK Tunnel:

Перед выполнением убедитесь, что в браузере произведен вход в ваш аккаунт ВК.

**Шаг 1**

```bash
./scripts/vk_auth_1.sh
```

Откройте появившуюся ссылку в браузере и разрешите доступ VK Tunnel Client. Вернитесь обратно в терминал и нажмите `Y`. Дождитесь запуска VK Tunnel и остановите его нажав `Ctrl+C`.

**Шаг 2**

```bash
./scripts/vk_auth_2.sh
```

### 5. Задайте конфигурацию:

**Шаг 1**

Откройте конфиг:

```bash
nano ./etc/env
```

**Шаг 2**

Заполните его:

```
# vk2vless

BIN_NODE=/usr/local/bin/node
BIN_VK_TUNNEL=/usr/local/bin/vk-tunnel

VK_TUNNEL_PORT=2007
VK_TUNNEL_WS_PROTOCOL=ws

VLESS_ID=89e8d4c2-295c-43ea-bc38-6094d426fd78
VMESS_ID=89e8d4c2-295c-43ea-bc38-6094d426fd78

YA_PROXY_TO=http://1.2.3.4/abc123

# server

LISTEN_HOST=0.0.0.0
LISTEN_PORT=80

PATH_SECRET=/abc123
```

**Шаг 3**

Измените эти настройки:

- `VK_TUNNEL_PORT`: укажите порт на котором запущен V2Ray (V2Fly, Xray, sing-box и т.п.)
- `VK_TUNNEL_WS_PROTOCOL`: укажите `wss` если V2Ray использует TLS, иначе укажите `ws`
- `VLESS_ID`: если V2Ray использует VLESS, то укажите его ID, иначе оставьте пустым
- `VMESS_ID`: если V2Ray использует VMess, то укажите его ID, иначе оставьте пустым
- `YA_PROXY_TO`: замените `1.2.3.4` на публичный IP-адрес сервера, замените `secret` на любой набор символов
- `PATH_SECRET`: должен совпадать с `YA_PROXY_TO`

**Шаг 4**

Сохраните конфиг нажав `Ctrl+O` и `Enter`. Закройте редактор нажав `Ctrl+X`.

### 6. Установите автозапуск:

```bash
systemctl enable ./systemd/vk2vless.service
systemctl enable ./systemd/vk2vless-server.service
```

### 7. Запустите:

```bash
systemctl start vk2vless
systemctl start vk2vless-server
```

### 8. Проверьте, что все работает:

```bash
systemctl status vk2vless
systemctl status vk2vless-server
```

В обоих случаях вы должны увидеть `active (running)`. Сообщения внизу не должны содержать ошибок.

### 9. Прочитайте ссылки и конфиги:

```bash
cat ./var/wss.txt
cat ./var/vless.txt
cat ./var/vmess.txt
cat ./var/ya-proxy.txt
```

`wss.txt` может быть использован для создания собственного конфига. `vless.txt` или `vmess.txt` может быть импортирован как готовый конфиг в V2ray-клиент. `ya-proxy.txt` может быть использован для постоянного доступа к `wss.txt`, `vless.txt` и `vmess.txt`.

`vk2vless` будет следить за VK Tunnel и перезапускать его по мере необходимости. `wss.txt`, `vless.txt` и `vmess.txt` будут обновляться. `ya-proxy.txt` останется постоянным. `vk2vless-server` обеспечивает публичный незащищенный доступ к `wss.txt`, `vless.txt` и `vmess.txt`.

При использовании ссылки из `ya-proxy.txt` замените `[file]` на `wss.txt`, `vless.txt` или `vmess.txt`.

## Использование

### Подписка

Возьмите ссылку из `ya-proxy.txt` и в качестве файла укажите `vless.txt` или `vmess.txt`. Проверьте, что она открывается в браузере и отображает содержимое файла. В V2ray-клиенте создайте подписку и укажите эту ссылку. После создания подписки обновите ее для получения конфига. Включите полученный конфиг и проверьте его работу. Периодически этот конфиг будет переставать работать. Для получения нового конфига выключите старый, выполните обновление подписки и включите новый конфиг.

### Свой конфиг

Возьмите ссылку из `ya-proxy.txt` и в качестве файла укажите `wss.txt`. Используйте этот вебсокет для создания собственного конфига. Автоматизируйте обновление конфига или обновляйте его вручную.

## Примеры

Смотрите [examples](/examples) для примера VLESS- и VMess-конфига.

Не используйте VLESS без TLS. Если нет возможности установить TLS, то используйте VMess.
