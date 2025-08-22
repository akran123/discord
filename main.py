import discord,random,os,datetime,requests
from discord.ext import commands
from dotenv import load_dotenv
import json
import asyncio


# .env 파일에서 환경변수 불러오기
load_dotenv()
# 토큰 설정
TOKEN = os.getenv("TOKEN")


bot = commands.Bot(command_prefix="%",intents=discord.Intents.all())



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



#@commands.has_role("관리자")
@bot.command(name="구조백업")
async def backup_all(ctx):
    guild = ctx.guild
    backup_data = {
        "guild_id": guild.id,
        "roles": [],
        "categories":[],
        "channels": [],
        "webhooks": {}
    }

    # 역할 백업
    for role in guild.roles:
        if role.name != "@everyone":
            backup_data["roles"].append({
                "name": role.name,
                "permissions": role.permissions.value,
                "color": role.color.value,
                "position": role.position
            })
    # ✅ 카테고리 채널 백업
    for category in guild.categories:
        backup_data["categories"].append({
            "name": category.name,
            "position": category.position
        })

    # 채널 백업
    for channel in guild.channels:
        backup_data["channels"].append({
            "name": channel.name,
            "type": str(channel.type),
            "category": channel.category.name if channel.category else None,
            "position": channel.position
        })

    # 웹훅 백업
    for channel in guild.text_channels:
        webhooks = await channel.webhooks()
        backup_data["webhooks"][channel.name] = [{
            "name": webhook.name,
            "url": webhook.url
        } for webhook in webhooks]

    # 저장
    os.makedirs("backups", exist_ok=True)
    with open(f"backups/backup_{guild.id}.json", "w", encoding="utf-8") as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=4)

    await ctx.send("✅ 서버 구조가 백업되었습니다.")

# ========== 복원 ==========


@bot.command(name="구조복구")
async def restore_all(ctx):
    try:
        with open(f"backups/backup_{ctx.guild.id}.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        # ✅ 역할 복원
        for role_data in data["roles"]:
            role = await ctx.guild.create_role(
                name=role_data["name"],
                permissions=discord.Permissions(role_data["permissions"]),
                colour=discord.Colour(role_data["color"])
            )
            await role.edit(position=role_data["position"])

        # ✅ 카테고리 복원
        categories = {}
        for cat_data in data["categories"]:
            category = await ctx.guild.create_category(
                name=cat_data["name"],
                position=cat_data["position"]
            )
            categories[cat_data["name"]] = category

        # ✅ 채널 복원 (텍스트/음성)
        channel_objects = {}
        for ch_data in data["channels"]:
            category = categories.get(ch_data["category"])
            new_channel = None

            if ch_data["type"] == "text":
                new_channel = await ctx.guild.create_text_channel(
                    name=ch_data["name"],
                    category=category,
                    position=ch_data["position"]
                )
            elif ch_data["type"] == "voice":
                new_channel = await ctx.guild.create_voice_channel(
                    name=ch_data["name"],
                    category=category,
                    position=ch_data["position"]
                )

            # 복원된 채널 객체를 저장
            if new_channel:
                channel_objects[ch_data["name"]] = new_channel

        # 웹훅 복원 or 생성
        for ch_name, webhooks in data["webhooks"].items():
            channel = channel_objects.get(ch_name)
            if not channel:
                continue

            existing_webhooks = await channel.webhooks()

            if webhooks:  # 기존 웹훅 데이터가 있으면 사용
                for webhook_data in webhooks:
                    await channel.create_webhook(name=webhook_data["name"])
            elif not existing_webhooks:  # 웹훅이 없을 경우 새로 생성
                new_webhook = await channel.create_webhook(name="자동복구봇")
                print(f"[웹훅 생성됨] {channel.name} → {new_webhook.url}")

        await ctx.send("서버 구조와 웹훅이 복원되었습니다.")

    except FileNotFoundError:
        await ctx.send("백업 파일이 존재하지 않습니다.")

# ========== 채팅 백업 ==========

#@commands.has_role("관리자")
@bot.command(name="채팅백업")
async def backup_chat(ctx, limit: int = 100):
    guild = ctx.guild
    backup_count = 0

    os.makedirs("chat_backups", exist_ok=True)

    for channel in guild.text_channels:
        try:
            messages_data = []
            async for msg in channel.history(limit=limit, oldest_first=True):
                messages_data.append({
                    "author": msg.author.name,
                    "content": msg.content,
                    "timestamp": str(msg.created_at)
                })

            if messages_data:
                file_path = f"chat_backups/{guild.id}_{channel.name}.json"
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(messages_data, f, ensure_ascii=False, indent=4)
                backup_count += 1
                print(f"백업 완료 {channel.name} → {len(messages_data)}개 메시지")
        except Exception as e:
            print(f"백업 실패 {channel.name}: {e}")
            continue

    await ctx.send(f"총 {backup_count}개의 텍스트 채널이 백업되었습니다.")

# ========== 채팅 복원 ==========

#@commands.has_role("관리자")
@bot.command(name="채팅복구")
async def restore_chat(ctx):
    guild = ctx.guild
    restored_count = 0

    for file in os.listdir("chat_backups"):
        if not file.startswith(str(guild.id)):
            continue  # 다른 서버의 백업은 건너뜀

        try:
            _, channel_name_with_ext = file.split("_", 1)
            channel_name = channel_name_with_ext.replace(".json", "")

            # 채널 찾기
            channel = discord.utils.get(guild.text_channels, name=channel_name)
            if not channel:
                print(f" 채널 '{channel_name}' 을(를) 찾을 수 없습니다.")
                continue

            # 웹훅 찾기 or 생성
            webhooks = await channel.webhooks()
            if webhooks:
                webhook = webhooks[0]
            else:
                webhook = await channel.create_webhook(name="채팅복원봇")

            # 채팅 로드
            with open(f"chat_backups/{file}", "r", encoding="utf-8") as f:
                messages = json.load(f)

            # 웹훅으로 메시지 전송
            for msg in messages:
                requests.post(webhook.url, json={
                    "content": msg['content'],
                    "username": msg['author']
                })
                await asyncio.sleep(0.3)

            restored_count += 1
            print(f"채널 '{channel_name}' 복원 완료.")

        except Exception as e:
            print(f"'{file}' 처리 중 오류 발생: {e}")

    await ctx.send(f"총 {restored_count}개 채널의 채팅이 복원되었습니다.")



#@commands.has_role("관리자")
@bot.command(name="데이터삭제")
async def delete_data(ctx) :
    try:
        # 기존 채널 제거
        for channel in ctx.guild.channels:
            await channel.delete()
        # 기존 역할 제거
        for role in ctx.guild.roles:
            if role.name != "@everyone":
                await role.delete()
    except :
        await ctx.send("데이터 삭제에 실패하였습니다")
bot.run(TOKEN)