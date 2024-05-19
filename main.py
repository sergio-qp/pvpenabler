import os
import discord
import random
from movelist import fullmovelist
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from typing import Literal, Optional

#add winner can pick to execute for a kick, mb not for funny

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(
     command_prefix="/",
     case_insensitive=True,
     intents=intents)
# tree = app_commands.CommandTree(client)

fight_room = None
fighterlist = dict()
acted_list = dict() #another dict to check if a player acting has already done theirnturn, and so we dont have to check state variable for Ready

class Fighter:
    def __init__(self, user, name, movelist, HP=100, state="Ready"):
        self.user = user
        self.name = name
        self.movelist = movelist
        self.HP = HP
        self.state = state



#room setups------------------
@bot.tree.command(
    name="set-room",
    description="Pick channel for fights"
)
async def setroom(call: discord.Interaction):
    await call.response.send_message(f"Arena set to {call.channel.name}")
    global fight_room
    fight_room =  call.channel


@bot.tree.command(
    name="check-room",
    description="See channel for fights"
)
async def checkroom(call: discord.Interaction):
    await call.response.send_message(f"Arena set to {fight_room}")
#------------------------------


#Duel setup-------------------------------
@bot.tree.command(
    name="duel",
    description="Resolve your differences"
)
async def duel(call: discord.Interaction, target: discord.Member):
    global fight_room
    if fight_room != None:
        await call.response.send_message("The bell rings...")
        await fight_room.send(f"{call.user.mention} has requested a duel with {target.mention}")
        await fight_room.send("Do you accept or decline the duel?")

        msg = await bot.wait_for('message',timeout=100,check=lambda message: message.author == target) #looks for a message by the target using the word accept

        if "accept" in msg.content.lower():
            await msg.channel.send("It begins")
            #we move on to request phase and set the potential combatants
            global fighterlist
            fighterlist = dict([ #god, i hope this makes an effective dictionary
                (call.user.name, (Fighter(call.user, call.user.name, fullmovelist))),
                (target.name, (Fighter(target, target.name, fullmovelist)))
                ])




        if  "decline" in msg.content.lower():
                await msg.channel.send("The noise stills")

    else:
        fight_room = call.channel
        await call.response.send_message("No room set, set to default") #I'd like to add recursion here, but idk if u can cuz of discord


#in duel moves----------------
        
def check_can_act(name): #not actually used anywhere, since it'd prevent players from changing their mind, but leaving it in in case we need it later
    global acted_list
    if acted_list[name] != None:
        return True

async def calculate_damage(move, target): #modifications to attack attributes are done outside
    if move.accuracy >= random.randrange(0,100): #first, check if attack connects
        target.HP = target.HP - move.damage
    else:
        return "Miss" #miss    


#once all players have acted, execute turn, function might need to be defined higher in text
#executes all activities once they're all ready 
             
async def turn_execute(call): 
    if (fighterlist != None) and len(acted_list) == len(fighterlist): #check a fight is on and that all the players in the fight have acted
        for name, fighter in acted_list.items(): #ATTACK LOOP HAPPENS FIRST
            if "Attacking" in fighter.state: #we don't care about anyone not attacking until the attacks are done
                move = fullmovelist[fighter.state.lower().split(' ')[1]] #these are gonna need error checking
                target = fighterlist[fighter.state.split(' ')[2]]
                match target.state:
                    case "Blocking":
                        move.damage = move.damage * move.penetration #reduces damage depending on its penetration                        
                    case "Dodging": #unless the move was ranged, do no damage and change states, add to counter if a dodge has happened
                        if move.ranged == 0:
                            move.accuracy = 0
                    case "Staggered": #dodged but no melee attack was made, next attack has 100% hitrate
                        move.accuracy = 100
                    case "Vulnerable": #happens when melee attack is dodged, next attack is guaranteed crit if it hits
                        move.critrate = 100
                await calculate_damage(move,target) #calculate damage after state effects
            await call.channel.send("Turn over") 
            
        
        for name, fighter in fighterlist.items(): #NEXT IS STATUS UPDATE LOOP            
            match fighter.state:
                case "Charging":
                    fighter.movelist = fullmovelist #i THINK this should reset all charges
                case "Dodging": #if name not in the list of targets of actedlist, put in stagger
                    t_count = 0
                    for attacker, actor in acted_list.items():
                        if actor.target == name:
                            t_count += 1
                    
                    if t_count == 0: #how do we reset everything but staggered states
                        fighter.state="Staggered"

        acted_list.clear()


async def check_all_set(name, fighter, call):
    global acted_list
    acted_list[name] = fighter
    await turn_execute(call) #it'll process as soon as actedlist fills



@bot.tree.command(
    name="attack",
    description="Attack your opponent, dealing damage"
)
async def attack(call: discord.Interaction, victim: discord.Member, move: str):
    if bool(fighterlist) != False: #check if list is empty, to see if fight exists
        if fighterlist[call.user.name] != None: #check player is in fight
            player = fighterlist[call.user.name]
            
            if fighterlist[victim.name] != None: #check target is in fight
                target = fighterlist[victim.name]

                if move in player.movelist.keys(): #check move is in player move list, how are we checking for charge?
                    if player.movelist[move].charged >= 0:
                        await call.response.send_message(f"You prepare to attack {target.name} with {move}!", ephemeral=True)
                        player.state = f"Attacking {move} {target.name}" #so we can transfer what move is being used in the same variable
                        await check_all_set(player.name,player,call)
                    else:
                        await call.response.send_message("It's out of charges!", ephemeral=True)
                else:
                    await call.response.send_message("You don't have that move", ephemeral=True)

            else:
                await call.response.send_message("The target is not an active combatant", ephemeral=True)
        else:
            await call.response.send_message("You're not in this fight", ephemeral=True)

    else: #check for in a fight
        await call.response.send_message("It would be dishonorable", ephemeral=True)


@bot.tree.command(
    name="block",
    description="Block, reducing incoming damage depending on penetration"
)
async def block(call: discord.Interaction):
    if bool(fighterlist) != False: #check if list is empty, to see if fight exists
        if fighterlist[call.user.name] != None: #check player is in fight
            player = fighterlist[call.user.name]
            await call.response.send_message("You prepare to block", ephemeral=True)
            player.state = "Blocking"
            await check_all_set(player.name,player,call)
        else:
            await call.response.send_message("You're not in this fight", ephemeral=True)

    else: #check for in a fight
        await call.response.send_message("I mean... You could? If you wanted to?", ephemeral=True)


@bot.tree.command(
    name="dodge",
    description="Dodge, avoiding melee attacks, but risking a counterattack"
)
async def dodge(call: discord.Interaction):
    if bool(fighterlist) != False: #check if list is empty, to see if fight exists
        if fighterlist[call.user.name] != None: #check player is in fight
            player = fighterlist[call.user.name]
            await call.response.send_message("You prepare to dodge", ephemeral=True)
            player.state = "Dodging"
            await check_all_set(player.name,player,call)
        else:
            await call.response.send_message("You're not in this fight", ephemeral=True)

    else: #check for in a fight
        await call.response.send_message("Sure. You dodge. Nothing attacks you.", ephemeral=True)



@bot.tree.command(
    name="charge",
    description="Charge, refilling all your special moves"
)
async def charge(call: discord.Interaction):
    if bool(fighterlist) != False: #check if list is empty, to see if fight exists
        if fighterlist[call.user.name] != None: #check player is in fight
            player = fighterlist[call.user.name]
            await call.response.send_message("You prepare to charge", ephemeral=True)
            player.state = "Charging"
            await check_all_set(player.name,player,call)
        else:
            await call.response.send_message("You're not in this fight", ephemeral=True)

    else: #check for in a fight
        await call.response.send_message("I mean... You could? If you wanted to?", ephemeral=True)


@bot.command()
async def sync(ctx):
    print("sync command")
    await bot.tree.sync()
    await ctx.send('Command tree synced.')

#dodge, has 1-2 turn cooldown, if opponent attacks while you were dodged, your next attack is a guaranteed crit if it connects
#if your opponent was blocking or dodging, though, the next attack that targets you can't miss
    #i can use ephemeral commands to hide the player's inputs from each other

@bot.event
async def on_ready():
    # await bot.tree.sync(guild=discord.Object(id="1128853398742110271"))
    print(f'Logged in as {bot.user}')
    #maybe we can have the check thing going on here, who knows
    


bot.run(token)
