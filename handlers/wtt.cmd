#!/*/wtt
#> syntax "[WTT_PORT]"
#> short_help "Starts a WebSocket-to-TCP bridge"
#? Starts a bridge between the remote command port and a TCP socket on [WTT_PORT]
#? Default TCP port: 9940
#?
#? Examples:
#?   - wtt
#?   - wtt 9950
#?
#? Environment variables:
#?   - REMOTE_CMD_PORT (): The remote cmd port to bridge commands to. If unset, the application won't start
#?   - WTT_PORT (9940): The port to listen for TCP connections to
#?
#? Repository: https://github.com/douxxtech/bw_wtt

< /opt/BotWave/scripts/wtt/start.sh {BW_ARGV1}