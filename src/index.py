import os
import sqlite3
from typing import Optional

import discord
from discord import app_commands

DB_PATH = os.getenv("BOT_DB_PATH", "data/bot.db")
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("DISCORD_GUILD_ID")


class ConfigStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS bot_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT value FROM bot_config WHERE key = ?",
                (key,),
            ).fetchone()
        return row[0] if row else default

    def set(self, key: str, value: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO bot_config (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, value),
            )
            conn.commit()


def build_info_layout(store: ConfigStore) -> discord.ui.LayoutView:
    current_mode = store.get("mode", "standard")
    gallery = discord.ui.MediaGallery(
        discord.ui.MediaGalleryItem(
            url="https://placehold.co/600x400/png",
            description="Bot preview",
        )
    )
    return discord.ui.LayoutView(
        discord.ui.Container(
            discord.ui.TextDisplay(
                f"Bot běží v režimu **{current_mode}** a používá Components V2."
            ),
            discord.ui.Separator(),
            discord.ui.TextDisplay(
                "Použij `/bot config` pro nastavení nebo klikni na tlačítko níže."
            ),
            discord.ui.ActionRow(
                discord.ui.Button(
                    label="Otevřít konfiguraci",
                    custom_id="bot:config:open",
                    style=discord.ButtonStyle.primary,
                )
            ),
            gallery,
        )
    )


def build_config_layout(store: ConfigStore) -> discord.ui.LayoutView:
    current_mode = store.get("mode", "standard")
    return discord.ui.LayoutView(
        discord.ui.Container(
            discord.ui.TextDisplay("Nastavení bota"),
            discord.ui.Separator(),
            discord.ui.TextDisplay(f"Aktuální režim: **{current_mode}**"),
            discord.ui.ActionRow(
                discord.ui.Select(
                    custom_id="bot:config:mode",
                    placeholder="Zvol režim",
                    options=[
                        discord.SelectOption(
                            label="Standard",
                            value="standard",
                            default=current_mode == "standard",
                        ),
                        discord.SelectOption(
                            label="Quiet",
                            value="quiet",
                            default=current_mode == "quiet",
                        ),
                        discord.SelectOption(
                            label="Verbose",
                            value="verbose",
                            default=current_mode == "verbose",
                        ),
                    ],
                )
            ),
        )
    )


class BotClient(discord.Client):
    def __init__(self, store: ConfigStore) -> None:
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.store = store
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self) -> None:
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()
        print(f"Logged in as {self.user} (ID: {self.user.id})")

    async def on_interaction(self, interaction: discord.Interaction) -> None:
        if interaction.type is not discord.InteractionType.component:
            return

        custom_id = interaction.data.get("custom_id")
        if custom_id == "bot:config:open":
            await interaction.response.send_message(
                components=build_config_layout(self.store),
                ephemeral=True,
            )
            return

        if custom_id == "bot:config:mode":
            values = interaction.data.get("values", [])
            if values:
                self.store.set("mode", values[0])
            await interaction.response.send_message(
                components=build_config_layout(self.store),
                ephemeral=True,
            )


store = ConfigStore(DB_PATH)
client = BotClient(store)

bot_group = app_commands.Group(name="bot", description="Bot commands")


@bot_group.command(name="info", description="Zobrazí informace o botovi")
async def bot_info(interaction: discord.Interaction) -> None:
    await interaction.response.send_message(
        components=build_info_layout(store),
        ephemeral=True,
    )


@bot_group.command(name="config", description="Otevře konfiguraci bota")
async def bot_config(interaction: discord.Interaction) -> None:
    await interaction.response.send_message(
        components=build_config_layout(store),
        ephemeral=True,
    )


client.tree.add_command(bot_group)

if not TOKEN:
    raise RuntimeError("Missing DISCORD_TOKEN environment variable")

client.run(TOKEN)
