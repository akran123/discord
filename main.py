import discord,random,os,datetime
from discord.ext import commands
from dotenv import load_dotenv

# .env 파일에서 환경변수 불러오기
load_dotenv()

bot = commands.Bot(command_prefix="%",intents=discord.Intents.all())
TOKEN = os.getenv("TOKEN")

@bot.event
async def on_ready():
    print(f"{bot.user.name} 로그인 성공")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('테스트'))


@bot.command(name="시간")
async def time(ctx) :
    time = datetime.datetime.today()
    await ctx.channel.send(time)


@bot.command(name="바보")
async def babo(ctx) :
    time = "임다비 바보"
    await ctx.channel.send(time)

@bot.command(name="조용히해")
async def quiet(ctx) :
    time = "조용히할게 ㅠㅠ"
    await ctx.channel.send(time)

@bot.command(name="멤버목록")
async def list_members(ctx):
    # 명령어가 입력된 현재 서버(길드) 객체를 가져옵니다.
    guild = ctx.guild 

    # 서버의 이름과 멤버 수를 메시지로 보냅니다.
    await ctx.send(f"'{guild.name}' 서버의 멤버 목록을 불러옵니다. (총 {guild.member_count}명)")

    # 모든 멤버를 순회하며 사용자 이름과 역할을 출력합니다.
    member_list = []
    for member in guild.members:
        roles = [role.name for role in member.roles if role.name != '@everyone']
        role_text = f"역할: {', '.join(roles)}" if roles else "역할 없음"
        member_list.append(f"- **{member.name}** ({member.id}) {role_text}")
    
    # 텍스트가 길어질 수 있으므로 한 번에 보낼 수 있도록 합칩니다.
    response = "\n".join(member_list)
    print(response)
    await ctx.send(response)

@bot.command(name="역할부여")
async def give_role(ctx, member: discord.Member, role: discord.Role):
    """
    특정 사용자에게 역할을 부여하는 명령어입니다.
    예시: !역할 @사용자이름 역할이름
    """
    try:
        # 멤버에게 역할을 추가합니다.
        await member.add_roles(role)
        await ctx.send(f'{member.mention} 님에게 **{role.name}** 역할을 부여했습니다.')
    except discord.Forbidden:
        # 봇의 권한이 부족할 경우 에러 메시지를 보냅니다.
        await ctx.send("봇의 역할이 이 역할을 부여할 권한이 없거나, 봇 역할이 부여하려는 역할보다 아래에 있습니다.")
    except discord.HTTPException as e:
        # 기타 오류가 발생했을 경우 에러 메시지를 보냅니다.
        await ctx.send(f"역할을 부여하는 중 오류가 발생했습니다: {e}")

@bot.command(name="역할생성")
async def create_new_role(ctx, role_name,role_color):
    """
    새로운 역할을 생성하는 명령어입니다.
    예시: !역할생성 새로운역할 역할색깔
    """
    try:
        # 입력받은 이름으로 역할을 생성합니다.
        # await ctx.guild.create_role(name=role_name)
        
        # 색상을 지정하여 생성할 수도 있습니다.
        color_value = int(role_color.strip("#"),16)
        color = discord.Colour(color_value)
        new_role = await ctx.guild.create_role(name=role_name, colour=color)
        
        await ctx.send(f"역할 **{new_role.name}** 이(가) 성공적으로 생성되었습니다.")

    except discord.Forbidden:
        # 봇의 권한이 부족할 경우 에러 메시지를 보냅니다.
        await ctx.send("봇에게 역할을 생성할 권한이 없습니다. 'Manage Roles' 권한을 부여해주세요.")
    except discord.HTTPException as e:
        # 기타 오류가 발생했을 경우 에러 메시지를 보냅니다.
        await ctx.send(f"역할을 생성하는 중 오류가 발생했습니다: {e}")

bot.run(TOKEN)