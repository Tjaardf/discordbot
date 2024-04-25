from typing import Optional, List
from discord import Embed, ui, ButtonStyle, Button, Interaction
import discord
import asyncio
from discord import app_commands
import json
import mysql.connector

with open('config.json') as f:
    config = json.load(f)


def create_db_connection():
    connection = mysql.connector.connect(
        host="na02-sql.pebblehost.com",
        user="customer_711448_loodsbot",
        password="2Nl$x8jbr#Wfen1-QG@g",
        database="customer_711448_loodsbot"
    )
    return connection


db_connection = create_db_connection()


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        self.loop.create_task(self.setup_hook())

    async def setup_hook(self):
        for guild in self.guilds:
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print('------')
    print(f"Tjaards bot genaamd: {client.user} (ID: {client.user.id})")
    print('------')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Tjaard's yapping"))


@client.event
async def on_guild_join(guild):
    user_id = guild.owner_id
    user = await client.fetch_user(user_id)
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute("INSERT INTO guild_roles (guild_id) VALUES (%s)", (guild.id,))
    if guild.me.guild_permissions.administrator:
        await user.send(
            f"Hallo ik ben de Loods Bot gemaakt door Tjaard! Ik ben een bot die je kan helpen met zaken zoals het aannemen van personen en het ontslaan ervan. Bekijk alle commando's met /help. P.S. al heb je vragen of suggesties stuur ze gerust naar Tjaard")
    else:
        await user.send(
            f"Ik ben de Loods Bot gemaakt door Tjaard! Ik ben een bot die je kan helpen met zaken zoals het aannemen van personen en het ontslaan ervan. Bekijk alle commando's met /help. P.S. al heb je vragen of suggesties stuur ze gerust naar Tjaard **Zou u nog even mij een rol kunnen geven met administrator permissies of mij dit apart kunnen geven?**")


@client.tree.command()
async def help(interaction: discord.Interaction):
    """Shows the help command."""
    embed = discord.Embed(
        title="Help",
        description="This is a list of all the commands.",
        color=discord.Color.blue()
    )
    for command in client.tree.commands:
        embed.add_field(
            name=command.name,
            value=command.description,
            inline=False
        )
    await interaction.response.send_message(embed=embed, ephemeral=True)


@client.tree.command()
@app_commands.describe(
    autorole='The role to set as the autorole.'
)
async def setautorole(interaction: discord.Interaction, autorole: discord.Role):
    """Sets or resets the autorole."""
    guild_id = str(interaction.guild.id)
    if interaction.user.guild_permissions.administrator:
        try:
            cursor = db_connection.cursor(dictionary=True)
            cursor.execute("SELECT auto_role FROM guild_roles WHERE guild_id = %s", (guild_id,))
            result = cursor.fetchone()

            if result:
                # Role already set, ask for reset
                msg = await interaction.response.send_message(
                    "The autorole has already been set. Do you want to reset it?", components=[
                        [
                            Button(ButtonStyle.success, custom_id="reset_yes"), "Yes",

                            Button(ButtonStyle.danger, custom_id="reset_no"), "No"
                        ]
                    ], ephemeral=True)

                def check(button_interaction: Interaction):
                    return button_interaction.message.id == msg.id and button_interaction.user.id == interaction.user.id

                try:
                    button_interaction = await client.wait_for("interaction", check=check, timeout=60)
                except asyncio.TimeoutError:
                    await msg.edit(components=[])
                    return

                if button_interaction.data.custom_id == "reset_yes":
                    # Reset the role
                    cursor.execute("UPDATE guild_roles SET auto_role = NULL WHERE guild_id = %s", (guild_id,))
                    db_connection.commit()
                    await button_interaction.response.send_message("The autorole has been reset.", ephemeral=True)
                elif button_interaction.data.custom_id == "reset_no":
                    await button_interaction.response.send_message("The autorole has not been reset.", ephemeral=True)
            else:
                # Role not set, set it
                cursor.execute("INSERT INTO guild_roles (guild_id, auto_role) VALUES (%s, %s)",
                               (guild_id, autorole.id))
                db_connection.commit()
                await interaction.response.send_message(f"The autorole has been set to {autorole.mention}.",
                                                        ephemeral=True)
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            await interaction.response.send_message("An error occurred while setting the autorole. Contact the developer!", ephemeral=True)
        finally:
            cursor.close()
    else:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)


@client.tree.command()
@app_commands.describe(
    role='The role to set as the support role.'
)
async def setsupportrole(interaction: discord.Interaction, role: discord.Role):
    """Sets or resets the support role."""
    guild_id = str(interaction.guild.id)
    if interaction.user.guild_permissions.administrator:
        try:
            cursor = db_connection.cursor(dictionary=True)
            cursor.execute("SELECT support_role FROM guild_roles WHERE guild_id = %s", (guild_id,))
            result = cursor.fetchone()

            if result:
                # Role already set, ask for reset
                msg = await interaction.response.send_message("The support role has already been set. Do you want to reset it?", components=[
                    [
                        Button(ButtonStyle.success, custom_id="reset_yes"), "Yes",

                        Button(ButtonStyle.danger, custom_id="reset_no"), "No"                                             
                     ]
                ], ephemeral=True)

                def check(button_interaction: Interaction):
                    return button_interaction.message.id == msg.id and button_interaction.user.id == interaction.user.id

                try:
                    button_interaction = await client.wait_for("interaction", check=check, timeout=60)
                except asyncio.TimeoutError:
                    await msg.edit(components=[])
                    return

                if button_interaction.data.custom_id == "reset_yes":
                    # Reset the role
                    cursor.execute("UPDATE guild_roles SET support_role = NULL WHERE guild_id = %s", (guild_id,))
                    db_connection.commit()
                    await button_interaction.response.send_message("The support role has been reset.", ephemeral=True)
                elif button_interaction.data.custom_id == "reset_no":
                    await button_interaction.response.send_message("The support role has not been reset.", ephemeral=True)
            else:
                # Role not set, set it
                cursor.execute("INSERT INTO guild_roles (guild_id, support_role) VALUES (%s, %s)", (guild_id, role.id))
                db_connection.commit()
                await interaction.response.send_message(f"The support role has been set to {role.mention}.", ephemeral=True)
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            await interaction.response.send_message("An error occurred while setting the support role. Contact the developer!", ephemeral=True)
        finally:
            cursor.close()
    else:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)


async def setworkerrole(interaction: discord.Interaction, role: discord.Role):
    """Sets or resets the worker role."""
    guild_id = str(interaction.guild.id)
    if interaction.user.guild_permissions.administrator:
        try:
            cursor = db_connection.cursor(dictionary=True)
            cursor.execute("SELECT worker_role FROM guild_roles WHERE guild_id = %s", (guild_id,))
            result = cursor.fetchone()

            if result:
                # Role already set, ask for reset
                msg = await interaction.response.send_message(
                    "The worker role has already been set. Do you want to reset it?", components=[
                        [
                            Button(ButtonStyle.success, custom_id="reset_yes"), "Yes",
                            Button(ButtonStyle.danger, custom_id="reset_no"), "No",
                        ]
                    ], ephemeral=True)

                def check(button_interaction: Interaction):
                    return button_interaction.message.id == msg.id and button_interaction.user.id == interaction.user.id

                try:
                    button_interaction = await client.wait_for("interaction", check=check, timeout=60)
                except asyncio.TimeoutError:
                    await msg.edit(components=[])
                    return

                if button_interaction.data.custom_id == "reset_yes":
                    # Reset the role
                    cursor.execute("UPDATE guild_roles SET worker_role = NULL WHERE guild_id = %s", (guild_id,))
                    db_connection.commit()
                    await button_interaction.response.send_message("The worker role has been reset.", ephemeral=True)
                elif button_interaction.data.custom_id == "reset_no":
                    await button_interaction.response.send_message("The worker role has not been reset.", ephemeral=True)
            else:
                # Role not set, set it
                cursor.execute("INSERT INTO guild_roles (guild_id, worker_role) VALUES (%s, %s)",
                               (guild_id, role.id))
                db_connection.commit()
                await interaction.response.send_message(f"The worker role has been set to {role.mention}.",
                                                        ephemeral=True)
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            await interaction.response.send_message("An error occurred while setting the worker role.", ephemeral=True)
        finally:
            if cursor:
                cursor.close()  # Close cursor only if it exists
    else:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)


@client.tree.command()
@app_commands.describe(
    person='The person to hire.',
)
async def hire(interaction: discord.Interaction, person: discord.Member):
    """Hires a person for a role."""
    guild_id = str(interaction.guild.id)
    if interaction.user.guild_permissions.administrator:
        try:
            cursor = db_connection.cursor(dictionary=True)
            cursor.execute("SELECT worker_role FROM guild_roles WHERE guild_id = %s", (guild_id,))
            result = cursor.fetchone()

            if config['worker_role'] is None:
                await interaction.response.send_message("The worker role has not been set.", ephemeral=True)
                return
            else:
                Worker_role = discord.utils.get(interaction.guild.roles, name=config['worker_role'])
                if Worker_role in person.roles:
                    await interaction.response.send_message(f"{person.mention} is already a {Worker_role.name}.", ephemeral=True)
                    return
                elif Worker_role is not None:
                    # Add the role to the person
                    await person.add_roles(Worker_role)
                    await interaction.response.send_message(f"{person.mention} has been hired as {Worker_role.name}.", ephemeral=True)
                else:
                    await interaction.response.send_message("The worker role has not been set yet. Do it by saying /setworkerrole", ephemeral=True)

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            await interaction.response.send_message("An error occurred while hiring the person.", ephemeral=True)
        finally:
            cursor.close()    
    else:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)


@client.tree.command()
@app_commands.describe(
    person='The person to fire.'
)
async def fire(interaction: discord.Interaction, person: discord.Member):
    """Fires a person from a role."""
    if interaction.user.guild_permissions.administrator:
        try:
            guild_id = str(interaction.guild.id)
            cursor = db_connection.cursor(dictionary=True)
            cursor.execute("SELECT worker_role FROM guild_roles WHERE guild_id = %s", (guild_id,))
            result = cursor.fetchone()

            if result:
                # Role exists, proceed with firing
                worker_role_id = result['worker_role']
                worker_role = interaction.guild.get_role(worker_role_id)

                if worker_role is None:
                    await interaction.response.send_message("The worker role has not been properly set.", ephemeral=True)
                    return

                if worker_role not in person.roles:
                    await interaction.response.send_message(f"{person.mention} is not a {worker_role.name}.", ephemeral=True)
                    return

                await person.remove_roles(worker_role)
                await interaction.response.send_message(f"{person.mention} has been fired from {worker_role.name}.", ephemeral=True)
            else:
                await interaction.response.send_message("This person has not been hired.", ephemeral=True)
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            await interaction.response.send_message("An error occurred while firing the person.", ephemeral=True)
        finally:
            cursor.close()
    else:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)


@client.tree.command()
@app_commands.describe(
    person='The person to promote.'
)
async def promote(interaction: discord.Interaction, person: discord.Member):
    """Promotes a person to a higher role."""
    if interaction.user.guild_permissions.administrator:
        try:
            guild_id = str(interaction.guild.id)
            cursor = db_connection.cursor(dictionary=True)
            cursor.execute("SELECT support_role, worker_role FROM guild_roles WHERE guild_id = %s", (guild_id,))
            result = cursor.fetchone()

            if not result:
                await interaction.response.send_message("The roles have not been properly set.", ephemeral=True)
                return

            support_role_id = result['support_role']
            worker_role_id = result['worker_role']

            support_role = interaction.guild.get_role(support_role_id)
            worker_role = interaction.guild.get_role(worker_role_id)

            if support_role is None or worker_role is None:
                await interaction.response.send_message("The roles have not been properly set.", ephemeral=True)
                return

            if support_role not in person.roles or worker_role in person.roles:
                await interaction.response.send_message(f"{person.mention} is not eligible for promotion.", ephemeral=True)
                return

            await person.remove_roles(worker_role)
            await person.add_roles(support_role)
            await interaction.response.send_message(f"{person.mention} has been promoted to {support_role.name}.", ephemeral=True)
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            await interaction.response.send_message("An error occurred while promoting the person.", ephemeral=True)
        finally:
            cursor.close()
    else:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)


@client.event
async def on_member_join(member):
    """Gives a role to a member when they join."""
    try:
        guild_id = str(member.guild.id)
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SELECT autorole FROM guild_roles WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()

        if not result:
            return

        autorole_id = result['autorole']
        autorole = member.guild.get_role(autorole_id)

        if autorole is None:
            return

        await member.add_roles(autorole)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()


@client.tree.command()
@app_commands.describe(
    number='The number of messages to delete.'
)
async def purge(interaction: discord.Interaction, number: str):
    """Deletes a number of messages from the channel."""
    if interaction.user.guild_permissions.manage_messages:
        # Delete the messages
        if number == "all":
            await interaction.channel.purge()
            await interaction.response.send_message("All messages have been deleted.", ephemeral=True)
            return 
        else:
            await interaction.channel.purge(limit=number)
            await interaction.response.send_message(f"{number} messages have been deleted.", ephemeral=True)
    else:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)


@client.tree.command()
@app_commands.describe(
    message="The message to send"
)
async def say(interaction: discord.Interaction, message: str):
    """Sends a message to the channel."""
    await interaction.channel.send(message)
    await interaction.response.send_message("Message sent!", ephemeral=True)


@client.tree.command()
async def status(interaction: discord.Interaction):
    """Shows the status of the bot."""
    embed = discord.Embed(
        title="Bot Status",
        description="The bot is online and ready to use.",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


@client.tree.command()
async def uitbetalingaanvraag(interaction: discord.Interaction):
    """Makes a uitbetaling request"""
    user_id = interaction.guild.owner_id
    user = await client.fetch_user(user_id)
    await user.send(f"{interaction.user.mention} heeft om een uitbetaling gevraagd")
    await interaction.response.send_message("Uitbetaling aanvraag is verzonden!", ephemeral=True)


client.run(config['token'])
