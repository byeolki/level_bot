from nextcord.ext import commands
import nextcord, datetime, sqlite3, random
from easy_pil import *

intents = nextcord.Intents.all()
client = commands.Bot(command_prefix='접두사 입력', intents=intents)

@client.event
async def on_ready():
    i = datetime.datetime.now()
    print(f"{client.user.name}봇은 준비가 완료 되었습니다.")
    print(f"[!] 참가 중인 서버 : {len(client.guilds)}개의 서버에 참여 중")
    print(f"[!] 이용자 수 : {len(client.users)}와 함께하는 중")

@client.event
async def on_message(message):
    user = message.author.id
    guild = message.guild.id
    conn = sqlite3.connect("level.db", isolation_level=None)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS lv(guild_id INTEGER, user_id INTEGER, xp INTEGER, lv INTEGER)")
    xp = random.randint(1, 7)
    if c.execute(f"SELECT * FROM lv WHERE user_id={user} AND guild_id={guild}").fetchone() is None:
        return c.execute("INSERT INTO lv (user_id, guild_id, xp, lv) VALUES (?, ?, ?, ?)", (user, guild,xp, 0,))
    y = c.execute(f"SELECT * FROM lv WHERE user_id={user} AND guild_id={guild}").fetchone()
    c.execute("UPDATE lv SET xp=? WHERE user_id=? AND guild_id=?",(y[2]+xp, user, guild,))
    y = c.execute(f"SELECT * FROM lv WHERE user_id={user} AND guild_id={guild}").fetchone()
    if y[3]*250 <= y[2]:
        c.execute("UPDATE lv SET xp=? WHERE user_id=? AND guild_id=?",(y[2]-y[3]*250, user, guild,))
        c.execute("UPDATE lv SET lv=? WHERE user_id=? AND guild_id=?",(y[3]+1, user, guild,))
        return await message.reply(f"레벨업! **현재 레벨** : **{y[3]+1}**")

@client.slash_command(name="레벨",description="나의 레벨을 확인 하실 수 있습니다!")
async def hello(inter: nextcord.Interaction) -> None:
    user = inter.user.id
    guild = inter.guild.id
    conn = sqlite3.connect("level.db", isolation_level=None)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS lv(guild_id INTEGER, user_id INTEGER, xp INTEGER, lv INTEGER)")
    y = c.execute(f"SELECT * FROM lv WHERE user_id={user} AND guild_id={guild}").fetchone()
    z = c.execute(f"SELECT * FROM lv WHERE guild_id={guild}").fetchall()
    user_data = {  # Most likely coming from database or calculation
        "name": f"{inter.user}",  # The user's name
        "xp": f"{y[2]}",
        "next_level_xp": f"{y[3]*250}",
        "level": f"{y[3]}",
        "percentage": (y[2]/y[3]*250)*100
    }
    print(sorted(list(z), key= lambda x:x[1], reverse=True))

    background = Editor(Canvas((934, 282), "#23272a"))
    profile_picture = await load_image_async(str(inter.user.display_avatar.url))
    profile = Editor(profile_picture).resize((190, 190)).circle_image()


    poppins = Font.poppins(size=30)

    background.rectangle((20, 20), 894, 242, "#2a2e35")
    background.paste(profile, (50, 50))
    background.ellipse((42, 42), width=206, height=206, outline="#43b581", stroke_width=10)
    background.rectangle((260, 180), width=630, height=40, fill="#484b4e", radius=20)
    background.bar(
        (260, 180),
        max_width=630,
        height=40,
        percentage=user_data["percentage"],
        fill="#00fa81",
        radius=20,
    )
    background.text((270, 120), user_data["name"], font=poppins, color="#00fa81")
    background.text(
        (870, 125),
        f"{user_data['xp']} / {user_data['next_level_xp']}",
        font=poppins,
        color="#00fa81",
        align="right",
    )

    rank_level_texts = [
        Text("   Level ", color="#00fa81", font=poppins),
        Text(f"{user_data['level']}", color="#1EAAFF", font=poppins),
    ]

    background.multicolor_text((850, 30), texts=rank_level_texts, align="right")
    file = nextcord.File(fp=background.image_bytes, filename="card.png")
    await inter.send(file=file)

client.run("토큰 입력")