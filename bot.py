from typing import Optional, List
from discord import Embed, ui, ButtonStyle
import discord
from discord import app_commands
import json
with open('config.json') as f:
    config = json.load(f)


MY_GUILD = discord.Object(id=1196941235508752556)  

# db = mysql.connector.connect(

#     host='localhost',
#     user='root',
#     password='',
#     database='loodsbot'
# )   


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        self.loop.create_task(self.setup_hook())

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

intents = discord.Intents.default()
client = MyClient(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')
    
@client.tree.command()
@app_commands.describe(
    person='The person to hire.',
)
async def hire(interaction: discord.Interaction, person: discord.Member):
    """Hires a person for a role."""
    if interaction.user.guild_permissions.administrator:
        # Get the role
        Werknemer_role = discord.utils.get(interaction.guild.roles, name="Loods Werknemer")
        if discord.Role == "Loods Werknemer" or discord.Role == "Loods Support":
            await interaction.response.send_message(f"{person.mention} is already a {Werknemer_role.name}.",ephemeral=True)
            return
        elif Werknemer_role is not None:
            # Add the role to the person
            await person.add_roles(Werknemer_role)
            await interaction.response.send_message(f"{person.mention} has been hired as {Werknemer_role.name}.",ephemeral=True)
        else:
            await interaction.response.send_message("The 'Loods Werknemer' role does not exist.", ephemeral=True)
    else:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

@client.tree.command()
@app_commands.describe(
    person='The person to fire.'
)
async def fire(interaction: discord.Interaction, person: discord.Member):
    """Fires a person from a role."""
    if interaction.user.guild_permissions.administrator:
        # Get the role
        Werknemer_role = discord.utils.get(interaction.guild.roles, name="Loods Werknemer")
        if discord.Role != "Loods Werknemer" or discord.Role != "Loods Support":
            await interaction.response.send_message(f"{person.mention} is not a {Werknemer_role.name}.",ephemeral=True)
            return
        elif Werknemer_role is not None:
            # Remove the role from the person
            await person.remove_roles("Loods Support")
            await person.remove_roles(Werknemer_role)
            await interaction.response.send_message(f"{person.mention} has been fired from {Werknemer_role.name}.",ephemeral=True)
        else:
            await interaction.response.send_message("The 'Loods Werknemer' role does not exist.", ephemeral=True)
    else:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

@client.tree.command()
@app_commands.describe(
    person='The person to promote.'
)	
async def promote(interaction: discord.Interaction, person: discord.Member):
    """Promotes a person to a higher role."""
    if interaction.user.guild_permissions.administrator:
        # Get the role
        Manager_role = discord.utils.get(interaction.guild.roles, name="Loods Support")
        
        if discord.Role == "Loods Support":
            await interaction.response.send_message(f"{person.mention} is already a {Manager_role.name}.",ephemeral=True)
            return
        elif discord.Role != "Loods Werknemer":
            await interaction.response.send_message(f"{person.mention} is not hired yet.",ephemeral=True)
            return
        elif Manager_role is not None:
            # Add the role to the person
            await person.remove_roles("Loods Werknemer")
            await person.add_roles(Manager_role)
            await interaction.response.send_message(f"{person.mention} has been promoted to {Manager_role.name}.",ephemeral=True)
        else:
            await interaction.response.send_message("The 'Loods Support' role does not exist.", ephemeral=True)
    else:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

@client.event
async def on_member_join(member):
    """Gives a role to a member when they join."""
    # Get the role
    Burger_role = discord.utils.get(member.guild.roles, name="Burger")

    if Burger_role is not None:
        # Add the role to the member
        await member.add_roles(Burger_role)
    else:
        print("The 'Burger' role does not exist.")


@client.tree.command()
@app_commands.describe(
    number='The number of messages to delete.'
)
async def purge(interaction: discord.Interaction, number: int):
    """Deletes a number of messages from the channel."""
    if interaction.user.guild_permissions.manage_messages:
        # Delete the messages
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
    embed   = discord.Embed(
        title="Bot Status",
        description="The bot is online and ready to use.",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

client.run(config['token'])