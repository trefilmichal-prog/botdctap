# botdctap

Discord bot (discord.py 2.x) používající výhradně Components V2.

## Požadavky

- Python 3.10+
- Discord bot token

## Instalace

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Konfigurace prostředí

```bash
export DISCORD_TOKEN="your-token"
# volitelné: rychlejší registrace příkazů do konkrétního serveru
export DISCORD_GUILD_ID="your-guild-id"
# volitelné: umístění sqlite databáze
export BOT_DB_PATH="data/bot.db"
```

## Spuštění

```bash
python src/index.py
```

Nebo přes npm script:

```bash
npm run start
```

## Slash příkazy

- `/bot info` – zobrazí informace o botovi přes Components V2.
- `/bot config` – otevře konfiguraci s Select komponentou.

## Perzistence

Bot ukládá konfiguraci do SQLite (`data/bot.db`), aby byla dostupná po restartu.
