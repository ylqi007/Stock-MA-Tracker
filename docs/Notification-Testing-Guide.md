# Stock MA Tracker Notification Testing Guide

本文档说明如何测试 Stock MA Tracker 的 Telegram 通知功能，包括：

- Telegram bot 连通性测试
- 自动化单元测试
- daily check 通知测试
- risk signal change 通知测试
- 不同消息格式样例测试
- 测试后的状态恢复与注意事项

## 1. 测试目标

当前通知逻辑支持两类消息。

Daily check 通知：

```text
📈 Stock MA Tracker Daily Check
📉 Stock MA Tracker Daily Check
ℹ️ Stock MA Tracker Daily Check
```

这种消息表示每日程序运行成功，但 risk state 没有变化。

Risk signal 通知：

```text
📈 Stock MA Tracker Risk Signal
📉 Stock MA Tracker Risk Signal
```

这种消息表示 risk state 发生变化，例如：

```text
RISK_OFF -> RISK_ON
RISK_ON -> RISK_OFF
```

图标含义：

- `📈`：当前状态是 `RISK_ON`
- `📉`：当前状态是 `RISK_OFF`
- `ℹ️`：当前状态是 `UNKNOWN`

## 2. 前置条件

进入主项目目录：

```bash
cd /Users/ylqi007/Work/Finance/Stock-MA-Tracker
```

激活虚拟环境：

```bash
source .venv/bin/activate
```

确认项目可以导入：

```bash
python -m stock_ma_tracker --version
```

确认 Telegram 环境变量可用：

```bash
echo "$TELEGRAM_BOT_TOKEN"
echo "$TELEGRAM_CHAT_ID"
```

如果当前 shell 没有这些变量，但本地 `.env.example` 中已经填好，可以临时加载：

```bash
set -a
source .env.example
set +a
```

注意：不要把真实 token 提交到 Git。更推荐把真实凭据放在 `.env`，让 `.env.example` 保持空模板。

## 3. Telegram Bot 连通性测试

先绕过项目代码，直接测试 Telegram API。

```bash
curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=${TELEGRAM_CHAT_ID}" \
  -d "text=Stock MA Tracker Telegram test"
```

成功时会看到：

```json
{"ok":true,...}
```

并且 Telegram 中会收到：

```text
Stock MA Tracker Telegram test
```

如果失败，常见原因包括：

- `TELEGRAM_BOT_TOKEN` 不正确
- `TELEGRAM_CHAT_ID` 不正确
- 你还没有主动给 bot 发过消息
- bot token 已被 rotate
- 当前网络无法访问 Telegram API

## 4. 自动化测试

运行通知相关单元测试：

```bash
python -m pytest -v tests/unit/test_notification_formatter.py tests/unit/test_cli_run.py
```

这些测试覆盖：

- `signal_only` 模式只在 risk state 改变时发送
- `signal_and_status` 模式在 risk state 不变时也发送 daily check
- daily check 消息使用简单格式
- risk signal 消息使用详细格式
- `RISK_ON` 使用 `📈`
- `RISK_OFF` 使用 `📉`
- CLI `run` 命令会按配置决定是否发送通知

期望结果：

```text
passed
```

也可以运行配置相关测试：

```bash
python -m pytest -v tests/unit/test_config.py
```

## 5. 配置检查

打开配置文件：

```bash
cat config/strategy.yaml
```

确认通知配置为：

```yaml
notification:
  provider: telegram
  mode: signal_and_status
  include_chart: true
```

`mode` 的含义：

- `signal_only`：只有 risk state 变化时发送通知
- `signal_and_status`：risk state 变化时发送 risk signal；没有变化时也发送 daily check
- `daily_summary`：目前行为等同于每日都发送通知

验证配置文件：

```bash
python -m stock_ma_tracker --config config/strategy.yaml validate-config
```

## 6. Daily Check 真实通知测试

在当前配置为 `signal_and_status` 时，直接运行：

```bash
python -m stock_ma_tracker run
```

如果当前保存的 state 和本次计算结果相同，终端应出现类似：

```text
State changed: no
Notification required: no
Notification sent: yes
```

Telegram 中应收到 daily check 消息，首行类似：

```text
📈 Stock MA Tracker Daily Check
```

或：

```text
📉 Stock MA Tracker Daily Check
```

取决于当前状态是 `RISK_ON` 还是 `RISK_OFF`。

## 7. Risk Signal 真实通知测试

Risk signal 需要制造一次 state transition。

当前策略状态保存在：

```text
state/QQQ.json
```

先备份：

```bash
cp state/QQQ.json /tmp/stock-ma-tracker-QQQ-state-test-backup.json
```

查看当前状态：

```bash
cat state/QQQ.json
```

如果当前最新计算大概率是 `RISK_ON`，可以临时把保存状态改成 `RISK_OFF`：

```bash
python - <<'PY'
import json
from pathlib import Path

path = Path("state/QQQ.json")
payload = json.loads(path.read_text(encoding="utf-8"))
payload["state"] = "RISK_OFF"
path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
```

然后运行：

```bash
python -m stock_ma_tracker run
```

期望终端输出类似：

```text
Previous state: RISK_OFF
Current state: RISK_ON
State changed: yes
Notification required: yes
Notification sent: yes
```

Telegram 中应收到 risk signal 消息：

```text
📈 Stock MA Tracker Risk Signal
```

如果要测试 `RISK_ON -> RISK_OFF`，需要让保存状态为 `RISK_ON`，并使用会计算出 `RISK_OFF` 的市场数据或测试数据。

测试完成后恢复 state：

```bash
cp /tmp/stock-ma-tracker-QQQ-state-test-backup.json state/QQQ.json
```

确认没有留下 state diff：

```bash
git diff -- state/QQQ.json
```

如果没有输出，说明已恢复。

## 8. 发送四种格式样例

如果只想在 Telegram 中预览消息格式，不想真的修改 state，可以直接构造样例并发送。

```bash
python - <<'PY'
from datetime import date
import os

from stock_ma_tracker.application import StrategyRunResult
from stock_ma_tracker.notification import TelegramNotifier, format_strategy_notification
from stock_ma_tracker.strategy import BufferedStrategyResult, StrategyState

notifier = TelegramNotifier(
    bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
    chat_id=os.environ["TELEGRAM_CHAT_ID"],
)

samples = [
    StrategyRunResult(
        symbol="QQQ",
        trading_date=date(2026, 7, 23),
        strategy=BufferedStrategyResult(
            previous_state=StrategyState.RISK_ON,
            current_state=StrategyState.RISK_ON,
            price=691.96,
            moving_average=641.52,
            upper_threshold=667.18,
            lower_threshold=622.27,
        ),
    ),
    StrategyRunResult(
        symbol="QQQ",
        trading_date=date(2026, 7, 23),
        strategy=BufferedStrategyResult(
            previous_state=StrategyState.RISK_OFF,
            current_state=StrategyState.RISK_OFF,
            price=610.00,
            moving_average=641.52,
            upper_threshold=667.18,
            lower_threshold=622.27,
        ),
    ),
    StrategyRunResult(
        symbol="QQQ",
        trading_date=date(2026, 7, 23),
        strategy=BufferedStrategyResult(
            previous_state=StrategyState.RISK_OFF,
            current_state=StrategyState.RISK_ON,
            price=691.96,
            moving_average=641.52,
            upper_threshold=667.18,
            lower_threshold=622.27,
        ),
    ),
    StrategyRunResult(
        symbol="QQQ",
        trading_date=date(2026, 7, 23),
        strategy=BufferedStrategyResult(
            previous_state=StrategyState.RISK_ON,
            current_state=StrategyState.RISK_OFF,
            price=610.00,
            moving_average=641.52,
            upper_threshold=667.18,
            lower_threshold=622.27,
        ),
    ),
]

for index, result in enumerate(samples, start=1):
    message = format_strategy_notification(result, moving_average_window=200)
    notifier.send(f"[Format sample {index}/4]\n" + message)
    print(f"sent sample {index}: {message.splitlines()[0]}")
PY
```

期望终端输出：

```text
sent sample 1: 📈 Stock MA Tracker Daily Check
sent sample 2: 📉 Stock MA Tracker Daily Check
sent sample 3: 📈 Stock MA Tracker Risk Signal
sent sample 4: 📉 Stock MA Tracker Risk Signal
```

Telegram 中应收到四条格式样例。

## 9. 常见问题

### `TELEGRAM_BOT_TOKEN environment variable is required`

说明当前 shell 没有 Telegram token。

解决：

```bash
set -a
source .env.example
set +a
```

或手动 export：

```bash
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="..."
```

### `Notification sent: no`

通常表示：

- 当前模式是 `signal_only`
- 本次没有 risk state change

如果希望每天都收到通知，使用：

```yaml
notification:
  mode: signal_and_status
```

### Telegram 没收到，但终端显示错误

查看错误内容。常见原因：

- token 错误
- chat id 错误
- bot 没有权限发到目标 chat
- 网络访问 Telegram API 失败

### 测试后 `state/QQQ.json` 变了

`run` 命令会保存最新策略状态，这是正常行为。

如果是 risk transition 测试，恢复备份：

```bash
cp /tmp/stock-ma-tracker-QQQ-state-test-backup.json state/QQQ.json
```

然后确认：

```bash
git diff -- state/QQQ.json
```

## 10. 测试完成 checklist

测试结束前建议确认：

- Telegram API curl 测试成功
- unit tests 通过
- daily check 消息能收到
- risk signal 消息能收到
- `state/QQQ.json` 已恢复
- `git status` 中没有意外的 state/data 改动
- 真实 token 没有被 staged 或 commit

查看 staged 内容：

```bash
git diff --cached --stat
```

检查是否误 stage 凭据：

```bash
git diff --cached -- .env.example
```
