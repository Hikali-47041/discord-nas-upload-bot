import os
import re
# import sys
import datetime
import shutil
import subprocess
import discord
import requests
from pathlib import Path
from dotenv import load_dotenv

repo = "https://github.com/Hikali-47041/Discord-Hi"
workdir = Path("/tmp/discord-nas-upload")
nas_upload_dir = Path("/home/hikalab-test/")
copy_suffix = "copy"
global current_channel
current_channel = None

load_dotenv()
TOKEN = os.getenv('DISCORD_ACCESS_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

def get_current_channel():
    global current_channel
    return current_channel

def set_current_channel(channel):
    global current_channel
    current_channel = channel

def url_to_path(url):
    dirpath = workdir.joinpath(f"{datetime.date.today()}")
    dirpath.mkdir(exist_ok=True)
    filepath = dirpath.joinpath(re.search("[^/]+$", url).group())
        # rename filename if exists
    if filepath.exists():
        filepath = dirpath.joinpath(f"{filepath.stem}_{copy_suffix}{filepath.suffix}")
    return filepath

def download_file(url, file_name):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(r.content)

def file_nas_upload(srcpath, distpath):
    command = ["python", "syno_nas_upload.py", srcpath, distpath]
    proc = subprocess.Popen(command)
    return proc.communicate()

def clean_directory(path):
    shutil.rmtree(path)

def discord_bot_main():

    @tree.command(
        name="help",
        description="show help"
    )
    @discord.app_commands.describe(
        command="commands to show help"
    )
    @discord.app_commands.rename(
        command="command"
    )
    @discord.app_commands.choices(
        command=[
            discord.app_commands.Choice(name="upload-url", value="upload_url"),
            discord.app_commands.Choice(name="upload-attachment", value="upload_attachment"),
            discord.app_commands.Choice(name="auto-upload", value="auto_upload"),
            # discord.app_commands.Choice(name="config", value="config")
        ]
    )
    @discord.app_commands.guild_only()
    async def show_help(ctx: discord.Interaction, command: str = ""):
        help_message = discord.Embed()
        print(command)
        if command == "":
            await ctx.response.send_message(f"研究室のNASにファイルをアップロードするBot", ephemeral=True)
        elif command == "upload_url":
            await ctx.response.send_message(f"url のデータをダウンロードしてアップロードします", ephemeral=True)
        elif command == "upload_attachment":
            await ctx.response.send_message(f"DiscordのAttachmentsで添付したデータをアップロードします", ephemeral=True)
        elif command == "auto_upload":
            await ctx.response.send_message(f"指定したチャンネル(デフォオルト: コマンドを使用したチャンネル)にアップロードされたAttachmentsに対して自動でファイルをアップロードします", ephemeral=True)
        # elif command == "config"
        #     await ctx.response.send_message(f"開発中", ephemeral=True)

    # @tree.command(
    #     name="cheat-code",
    #     description="かくしコマンド"
    # )
    # @discord.app_commands.describe(
    #     key="key",
    #     value="value"
    # )
    # @discord.app_commands.rename(
    #     key="code"
    # )
    # @discord.app_commands.guild_only()
    # async def cheat_code(ctx: discord.Interaction, key: str, value: str = ""):
    #     if key.lower() == "echo":
    #         await ctx.response.send_message(f"{value} ", ephemeral=True)
    #     elif key.lower() == "help":
    #         await ctx.response.send_message(f"{repo}", ephemeral=True)
    #     elif key.lower() == "setstatus":
    #         if value == "online":
    #             await client.change_presence(status=discord.Status.online)
    #         elif value == "idle":
    #             await client.change_presence(status=discord.Status.idle)
    #         elif value == "dnd" or value == "do_not_disturb":
    #             await client.change_presence(status=discord.Status.dnd)
    #         elif value == "invisible":
    #             await client.change_presence(status=discord.Status.invisible)
    #         await ctx.response.send_message(f"status changed to {value}", ephemeral=True)
    #     elif key.lower() == "setactivity":
    #             await client.change_presence(activity=discord.Game(value))
    #             await ctx.response.send_message(f"Activity changed to {value}", ephemeral=True)
    #     else:
    #         await ctx.response.send_message(f"{key} {value}", ephemeral=True)

    # @discord.app_commands.checks.has_any_role(*items)

    @tree.command(
        name="auto-upload",
        description="upload files to"
    )
    @discord.app_commands.describe(
        command="enable/disable auto upload",
        channel="read channel(default current channel)",
        
    )
    @discord.app_commands.rename(
        command="command",
        channel="text_channel",
    )
    @discord.app_commands.choices(
        command=[
            discord.app_commands.Choice(name="status",value="status"),
            discord.app_commands.Choice(name="enable",value="enable"),
            discord.app_commands.Choice(name="disable",value="disable"),
        ]
    )
    @discord.app_commands.guild_only()
    async def auto_upload(ctx: discord.Interaction, command: str, channel: discord.TextChannel = None):
        if command == "status":
            if get_current_channel() is None:
                await ctx.response.send_message(f"auto upload is disabled", ephemeral=True)
            else:
                await ctx.response.send_message(f"auto upload is enabled at {get_current_channel()}", ephemeral=True)
            return
        elif command == "enable":
            if get_current_channel() is not None:
                await client.get_channel(get_current_channel().id).send(f"disabled auto upload.")
            if channel is None:
                channel = ctx.channel
            await ctx.response.send_message(f"enable auto upload at {channel}", ephemeral=True)
            view = discord.ui.View()
            # delete_button = DeleteButton(label='Delete', style=discord.ButtonStyle.red)
            # view.add_item(delete_button)
            await client.get_channel(channel.id).send(f"enabled auto upload.", view=view)
            # TODO 同期
            set_current_channel(channel)
        elif command == "disable":
            if get_current_channel() is None:
                await ctx.response.send_message(f"already disabled auto upload", ephemeral=True)
            else:
                await ctx.response.send_message(f"disable auto upload at {get_current_channel()}", ephemeral=True)
                await client.get_channel(get_current_channel().id).send(f"disabled auto upload.")
            set_current_channel(None)

    @client.event
    async def on_message(message):
        if message.author.bot or get_current_channel() is None:
            return

        if message.attachments:
            for attachment in message.attachments:
                print(attachment.url)
                filepath = url_to_path(attachment.url)
                download_file(attachment.url, filepath)
                file_nas_upload(filepath, nas_upload_dir.joinpath(filepath.parent.relative_to(workdir)))
            clean_directory(filepath.parent)
            await message.add_reaction("⬆")
            # await ctx.response.send_message(f"uploaded: {file}")


    @tree.command(
        name="upload-url",
        description="Upload by URL"
    )
    @discord.app_commands.describe(
        url="URL of the file to upload"
    )
    @discord.app_commands.guild_only()
    async def upload_url(ctx: discord.Interaction, url: str):
        await client.change_presence(status=discord.Status.online, activity=discord.Game("uploading"))
        filepath = url_to_path(url)
        download_file(url, filepath)
        file_nas_upload(filepath, nas_upload_dir.joinpath(filepath.parent.relative_to(workdir)))
        await ctx.response.send_message(f"uploaded: {url}")
        clean_directory(filepath.parent)
        await client.change_presence(status=discord.Status.idle, activity=discord.Game(""))

    @tree.command(
        name="upload-attachment",
        description="Upload by Attachment"
    )
    @discord.app_commands.describe(
        file="File of the file to upload"
    )
    @discord.app_commands.guild_only()
    async def upload_attachment(ctx: discord.Interaction, file: discord.Attachment):
        await client.change_presence(status=discord.Status.online, activity=discord.Game("uploading"))
        filepath = url_to_path(file.url)
        download_file(file.url, filepath)
        file_nas_upload(filepath, nas_upload_dir.joinpath(filepath.parent.relative_to(workdir)))
        await ctx.response.send_message(f"uploaded: {file}")
        clean_directory(filepath.parent)
        await client.change_presence(status=discord.Status.idle, activity=discord.Game(""))

    @client.event
    async def on_ready():
        if not workdir.exists():
            workdir.mkdir(parents=True)
        await tree.sync()
        print(f'Logged in as {client.user} \n- - - -')
        await client.change_presence(status=discord.Status.idle, activity=discord.Game(""))

    # run
    client.run(TOKEN)


if __name__ == '__main__':
    discord_bot_main()