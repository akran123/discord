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


@bot.command(name="멤버목록")
@commands.has_role("관리자")
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
@commands.has_role("관리자")
async def give_role(ctx, member: discord.Member, role: discord.Role):
    """
    특정 사용자에게 역할을 부여하는 명령어입니다.
    예시: !역할 @사용자이름 역할이름
    """
    try:
        # 멤버에게 역할을 추가합니다.
        await member.add_roles(role)
        await ctx.send(f'{member.mention} 님에게 **{role.name}** 역할을 부여했습니다.')
    except discord.HTTPException as e:
        # 기타 오류가 발생했을 경우 에러 메시지를 보냅니다.
        await ctx.send(f"역할을 부여하는 중 오류가 발생했습니다: {e}")

@bot.command(name="역할생성")
@commands.has_role("관리자")
async def create_new_role(ctx, role_name,role_color:str = None):
    """
    새로운 역할을 생성하는 명령어입니다.
    예시: !역할생성 새로운역할 역할색깔
    """
    try:
        color = discord.Colour.default() # 기본 색상 설정
        if role_color: # role_color 인자가 있을 경우
            try:
                # 16진수 문자열을 숫자로 변환
                color_value = int(role_color.strip("#"), 16)
                color = discord.Colour(color_value)
            except ValueError:
                await ctx.send("잘못된 색상 코드 형식입니다. `#FF0000`과 같은 16진수 코드를 사용해주세요.")
                return
        new_role = await ctx.guild.create_role(name=role_name, colour=color)
        
        await ctx.send(f"역할 **{new_role.name}** 이(가) 성공적으로 생성되었습니다.")
    except discord.HTTPException as e:
        # 기타 오류가 발생했을 경우 에러 메시지를 보냅니다.
        await ctx.send(f"역할을 생성하는 중 오류가 발생했습니다: {e}")

@bot.command(name="채널추가")
# '채널 관리' 권한이 있는 사용자만 이 명령어를 사용할 수 있도록 제한합니다.
@commands.has_role("관리자")
async def add_channel_to_category(ctx, category_name : str,channel_name:str):
    """
    지정된 카테고리에 새로운 텍스트 채널을 생성합니다.
    예시: !채널추가 "카테고리" "새로운 채널"
    """
    everyone_role = ctx.guild.default_role
    target_role = discord.utils.get(ctx.guild.roles,name= "손님은 왕이다")
    overwrites = {
        everyone_role: discord.PermissionOverwrite(view_channel=False),
        target_role: discord.PermissionOverwrite(view_channel=True)
    }

    # ... (카테고리를 찾고 채널을 생성하는 기존 코드)
    category = discord.utils.get(ctx.guild.categories, name=category_name)
    
    if category is None:
        await ctx.send(f"'{category_name}'라는 카테고리를 찾을 수 없습니다.")
        return

    try:
        new_channel = await ctx.guild.create_text_channel(channel_name, category=category,overwrites=overwrites)
        await ctx.send(f'**{category.name}** 카테고리에 {new_channel.mention} 채널이 성공적으로 생성되었습니다.')
    except discord.HTTPException:
        await ctx.send("채널 생성에 실패했습니다. 올바른 이름인지 확인해주세요.")


bot.run(TOKEN)