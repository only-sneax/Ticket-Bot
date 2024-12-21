import discord
from discord.ext import commands
from discord.ui import Select, View, Modal, TextInput, Button
import asyncio

TOKEN = "" #                    --> Inserisci il token del bot
CATEGORY_ID =  #                --> Inserisci la categoria in cui creare i ticket
ROLE_IDS = { #                  --> Per ogni opzione che vuoi mettere , metti un ID del ruolo di supporto 
}
CHANNEL_ID = #                  --> Canale in cui mandare il messaggio all' avvio del bot 
LOG_CHANNEL_ID =    #           --> Canale per i log 
TICKET_CATEGORY_ID = #          --> Categoria per i ticket 
ROLE_ID =              #        --> ruolo che può usare i comandi 

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

QUESTIONS = {
    #                           --> Inserisic le domande per l' opzione . 
}

class SupportModal(Modal):
    def __init__(self, option_name, questions):
        super().__init__(title=f"Supporto - {option_name}")
        self.option_name = option_name
        self.questions = questions
        self.answers = {}

        for idx, question in enumerate(questions):
            if len(question) > 45:
                question = question[:42] + "..."
            self.add_item(TextInput(label=question, custom_id=f"question_{idx}", required=True))

    async def on_submit(self, interaction: discord.Interaction):
        for child in self.children:
            self.answers[child.label] = child.value
        await interaction.response.send_message("Grazie! Stiamo creando il tuo ticket.", ephemeral=True)

        guild = interaction.guild
        user = interaction.user
        category = discord.utils.get(guild.categories, id=CATEGORY_ID)
        support_role = guild.get_role(ROLE_IDS.get(self.option_name))

        if not category or not support_role:
            await interaction.followup.send("Errore nella creazione del ticket.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True),
            support_role: discord.PermissionOverwrite(view_channel=True)
        }
        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}-{self.option_name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title=f"Dettagli ticket - {self.option_name}",
            color=discord.Color.blurple()
        )
        for question, answer in self.answers.items():
            embed.add_field(name=question, value=answer, inline=False)

@bot.event
async def on_ready():
    print(f"{bot.user} è online!")
    channel = bot.get_channel(CHANNEL_ID)

    if channel:
        embed = discord.Embed(
            title="",
            description=(
            ),
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url="")
        embed.set_footer(text="")

        select = Select(
            placeholder="Select an option",
            options=[
                # discord.SelectOption(label="", emoji="", description=""),
                # Segui questa sintassi ->
                #           -   label=""                    --> Inserisci il nome dell' opzione 
                #           -   emoji="emoji"               --> Inserisci l'emoji dell' opzione
                #           -   description=""              --> Inserisci la desrizione dell' opzione
            ]
        )

        async def select_callback(interaction):
            await interaction.response.send_modal(SupportModal(select.values[0], QUESTIONS[select.values[0]]))

        select.callback = select_callback
        view = View(timeout=None)
        view.add_item(select)

        await channel.send(embed=embed, view=view)

        await bot.tree.sync()
       	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Tickets"))

#####################################
#                                   #
#           COMANDO /CHIUDI         #
#                                   #
#####################################

@bot.tree.command(name="chiudi", description="Close a ticket")
@commands.has_role(ROLE_ID)
async def chiudi(interaction: discord.Interaction):
    channel = interaction.channel
    if isinstance(channel, discord.TextChannel):
        if channel.category_id != TICKET_CATEGORY_ID:
            await interaction.response.send_message(
                "Questo comando può essere usato solo nei canali della categoria specifica.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="CHIUDI TICKET / CLOSE TICKET",
            description="Clicca il bottone \"🔒CLOSE\" per chiudere il ticket",
            color=discord.Color.red()
        )
        embed.set_footer(text="Sneax's Services")

        close_button = Button(label="🔒CLOSE", style=discord.ButtonStyle.danger, custom_id="close_ticket")

        class CloseTicketView(View):
            def __init__(self, ticket_user_id):
                super().__init__(timeout=None)
                self.ticket_user_id = ticket_user_id

        async def close_ticket_callback(interaction: discord.Interaction):
            try:
                user = await bot.fetch_user(interaction.user.id)

                embed_dm = discord.Embed(
                    title="Ticket Chiuso / Ticket Closed",
                    description=":flag_it:\n> Il Tuo ticket è stato chiuso nel server.\n\n:england:\n> Your ticket has been closed on server.",
                    color=discord.Color.red()
                )
                embed_dm.set_footer(text="Sneax's Services")

                try:
                    await user.send(embed=embed_dm)
                except discord.Forbidden:
                    pass

                await channel.delete()

            except Exception as e:
                await interaction.response.send_message(
                    f"Si è verificato un errore durante la chiusura del ticket: {str(e)}",
                    ephemeral=True
                )

        close_button.callback = close_ticket_callback
        view = CloseTicketView(ticket_user_id=interaction.user.id)
        view.add_item(close_button)

        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(
            ".",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "Questo comando può essere usato solo in canali di testo.",
            ephemeral=True
        )

        
#####################################
#                                   #
#       COMANDO /CANDIDATURA        #
#                                   #
#####################################

@bot.tree.command(name="candidatura", description="Gestisci una candidatura")
@discord.app_commands.choices(scelta=[
    discord.app_commands.Choice(name="Vero", value="vero"),
    discord.app_commands.Choice(name="Falso", value="falso")
])
@discord.app_commands.default_permissions(administrator=True)
async def candidatura(interaction: discord.Interaction, scelta: str):
    if scelta == "vero":
        embed = discord.Embed(
            title=":flag_it: Candidatura accettata :flag_it: / :england: Application accepted :england:",
            description="La tua candidatura è stata accettata\nBenvenuto nel team!",
            color=discord.Color.green()
        )
        embed.set_image(url="https://i.postimg.cc/RFkhxstc/logo-2.png")
        embed.set_footer(text="Sneax's Services")
        await interaction.response.send_message(embed=embed)
    elif scelta == "falso":
        embed = discord.Embed(
            title=":flag_it: La tua candidatura è stata rifiutata :flag_it: / :england: Your application has been rejected :england:",
            description="Your application has not been accepted. You can try again in 7 days.",
            color=discord.Color.red()
        )
        embed.set_image(url="https://i.postimg.cc/RFkhxstc/logo-2.png") 
        embed.set_footer(text="Sneax's Services")
        await interaction.response.send_message(embed=embed)



bot.run(TOKEN)