# 簡易PTT文章訂閱器

## 使用方法

1. fork這個repo

2. 從master建立一個`runner`分支

3. 然後去repo設定裡的`Secrets and variables` > `Actions`

4. 在Repository secrets的地方輸入以下這些變數跟值

`USERNAME` ptt 帳號

`PASSWORD` ptt 密碼

`TG_BOT_CHAT_ID` telegram 聊天室id

`TG_BOT_TOKEN` telegram bot token

`OVPN_USERNAME` 跟 `OVPN_PASSWORD` 是VPN需要的帳號密碼

`WORKS` 是你要訂閱的版跟文章關鍵字組合 如下面範例 可以多個
> \[["steam", "特價"], ["steam", "限免"]\]

## VPN

從github過去的流量都是外國流量 不知道為什麼ptt那邊會擋的樣子 所以需要VPN

如果是使用nordvpn的人可以跳過 如果是其他vpn的使用者可能要替換一下.github/workflows/client.ovpn 不然可能會沒辦法跑

## 結語

上面步驟都完成的話 理論上每四小時會爬一次 然後把新的文章送到telegram
