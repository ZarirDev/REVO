import discord
from discord.ext import commands
import sqlite3
import keygenerator
import getKey

#Add discord user id in the list below to have
haveAccess=[]

db=sqlite3.connect("./data.db")
cur=db.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS dc_users(
            uid INTEGER,
            balance INTEGER
)""")
db.commit()

desc = '''Official Revo
currency bot'''

bot = commands.Bot(command_prefix="z ", description=desc, intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"{bot.user.name} is online!")

@bot.command()
async def sync(ctx):
    await ctx.send(".")
    await bot.tree.sync()
    print(f"{bot.user.name} synced!")
    
#Slash Commands

@bot.hybrid_command()
async def test(ctx):
    """Tests if this bot is working."""
    embed=discord.Embed(title="Test Complete", colour=0xf0ff7a)
    await ctx.send(embed=embed)
    print(f"Tested by {ctx.author}")

@bot.hybrid_command()
async def say(ctx, message):
    """Say something to the development team with this command."""
    print(f'{ctx.author} said "{message}"')
    embed=discord.Embed(title="Your message has been sent!", colour=0xf0ff7a)
    await ctx.send(embed=embed, ephemeral=True)

@bot.hybrid_command()
async def ping(ctx):
    """Tells the bot's ping."""
    embed=discord.Embed(title="Pong!", description=f"Ping: {round(bot.latency*1000)}ms", colour=0xf0ff7a)
    await ctx.send(embed=embed)
    print(f"Ping checked by {ctx.author}")

@bot.hybrid_command()
async def start(ctx):
    """Starts a new account."""
    uid=ctx.author.id
    cur.execute(f"SELECT * FROM dc_users WHERE uid={uid}")
    if cur.fetchone():        
        embed = discord.Embed(title="Account already exists", colour=0xf0ff7a)
        embed.set_author(name="Start")
        print(f"Account requested but account already exists for {ctx.author}")
    else:
        cur.execute(f"INSERT INTO dc_users VALUES({uid}, 0)")
        db.commit()
        embed = discord.Embed(title="An account under your user ID has been created!", colour=0xf0ff7a)
        embed.set_author(name="Start")
        print(f"New account created for {ctx.author}")
    await ctx.send(embed=embed)

@bot.hybrid_command()
async def redeem(ctx, code):
    """Redeems codes"""
    uid=ctx.author.id
    cur.execute(f"SELECT * FROM dc_users WHERE uid={uid}")
    user=cur.fetchone()
    if user:
        cur.execute(f"SELECT * FROM keys WHERE key='{code}' and validity=1")
        keyData=cur.fetchone()
        if keyData:
            cur.execute(f"UPDATE keys SET validity=0 WHERE id={keyData[0]}")
            cur.execute(f"SELECT * FROM dc_users WHERE uid={uid}")
            balance=user[1]
            keyValue=keyData[2]
            cur.execute(f"UPDATE dc_users SET balance={balance+keyValue} WHERE uid={uid}")
            db.commit()
            embed = discord.Embed(title="Key redeemed!", colour=0xf0ff7a)
            embed.set_author(name="Redeem")
        else:
            print("Invalid or already redeemed")
            embed = discord.Embed(title="Invalid Key")
            embed.set_author(name="Redeem")
    else:
        embed = discord.Embed(title="You don't have an account", description="Type </start:1233477007451492453>", colour=0xf0ff7a)
        embed.set_author(name="Redeem")
        print(f"{ctx.author} tried redeeming but had no account")
    await ctx.send(embed=embed)

@bot.hybrid_command()
async def balance(ctx):
    """Checks balance"""
    uid=ctx.author.id
    cur.execute(f"SELECT * FROM dc_users WHERE uid={uid}")
    user=cur.fetchone()
    if user:
        embed = discord.Embed(title=f"{ctx.author}'s balance: {user[1]:,} REVO", colour=0xf0ff7a)
        embed.set_author(name="Balance")
    else:
        embed = discord.Embed(title="You don't have an account", description="Type </start:1233477007451492453>", colour=0xf0ff7a)
        embed.set_author(name="Balance")
    await ctx.send(embed=embed)

@bot.hybrid_command()
async def pay(ctx, to: discord.Member, quantity):
    """Pay to someone"""
    uid=ctx.author.id
    targetUID=to.id
    cur.execute(f"SELECT * FROM dc_users WHERE uid={uid}")
    user=cur.fetchone()
    cur.execute(f"SELECT * FROM dc_users WHERE uid={targetUID}")
    targetUser=cur.fetchone()
    quantity=int(quantity)
    if isinstance(quantity,int):
        if user:
            if targetUser:
                targetBalance=targetUser[1]
                userBalance=user[1]
                if userBalance>=quantity:
                    cur.execute(f"UPDATE dc_users SET balance={userBalance-quantity} WHERE uid='{uid}'")
                    cur.execute(f"UPDATE dc_users SET balance={targetBalance+quantity} WHERE uid='{targetUID}'")
                    db.commit()
                    embed = discord.Embed(title=f"{quantity:,} paid to {to}", colour=0xf0ff7a)
                    embed.set_author(name="Pay")
                else:
                    embed = discord.Embed(title="Insufficient funds", colour=0xf0ff7a)
                    embed.set_author(name="Pay")
            else:
                embed = discord.Embed(title="No account found for target", colour=0xf0ff7a)
                embed.set_author(name="Pay")
        else:
            embed = discord.Embed(title="You don't have an account", description="Type </start:1233477007451492453>", colour=0xf0ff7a)
            embed.set_author(name="Pay")
    else:
        embed = discord.Embed(title="Quantity must be an integer", colour=0xf0ff7a)
        embed.set_author(name="Pay")
    await ctx.send(embed=embed)

@bot.hybrid_command()
async def generate(ctx, amount, value):
    """OWNER COMMANDS"""
    amount=int(amount)
    value=int(value)
    uid=ctx.author.id
    if int(uid) in haveAccess:
        if amount < 21:
            await ctx.send(keygenerator.generateKeys(amount,value))
        else:
            await ctx.send("Too many keys requested. Try 20 or less")
    else:
        embed = discord.Embed(title="ACCESS DENIED", colour=0xff0000)
        await ctx.send(embed=embed)

with open("./token.txt", "r") as file:
    token = file.read().strip()
    bot.run(token)
