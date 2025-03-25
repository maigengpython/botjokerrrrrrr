import discord
from discord.ext import commands
from discord.ui import View, Modal, TextInput, Button
import re
import os
import datetime

from myserver import keep_alive
from myserver import server_on

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  
bot = commands.Bot(command_prefix="!", intents=intents)

# ใส่ ID ของช่องที่ต้องการให้บอทส่งข้อความว่ามีคนติดต่อ 
CHANNEL_ID = 1353948182345810031
ADMIN_CHANNEL_ID = 1337729886311415842
ANNOUNCE_CHANNEL_ID = 1349963365908484176

class ContactModal(Modal):
    def __init__(self):
        super().__init__(title="ติดต่อ")

        self.who_input = TextInput(label="ติดต่อใคร", style=discord.TextStyle.short)
        self.what_age_input = TextInput(label="เรื่องอะไร", style=discord.TextStyle.short)

        self.add_item(self.who_input)
        self.add_item(self.what_age_input)

    async def on_submit(self, interaction: discord.Interaction):
        user = interaction.user  
        channel = bot.get_channel(CHANNEL_ID)

        if channel:
            embed = discord.Embed(
                title="📩 มีคนต้องการติดต่อ",
                description=f"👤 **ติดต่อ:** {self.who_input.value}\n📜 **เรื่อง:** {self.what_age_input.value}",
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"ติดต่อโดย {user.display_name}", icon_url=user.avatar.url if user.avatar else None)
            await channel.send(embed=embed)
            await interaction.response.send_message("✅ ส่งข้อมูลไปยังช่องที่กำหนดแล้ว!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ ไม่พบช่องที่ต้องการส่งข้อความ!", ephemeral=True)

class ContactView(View):
    def __init__(self):
        super().__init__()
        self.add_item(Button(label="เริ่มกรอกฟอร์มติดต่อ", style=discord.ButtonStyle.green, custom_id="contact_button"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.data["custom_id"] == "contact_button":
            await interaction.response.send_modal(ContactModal())
        return True

# ฟังก์ชันป้องกันลิงก์
@bot.event
async def on_message(message):
    if re.search(r"https?://\S+", message.content):
        if not message.author.guild_permissions.administrator:
            await message.delete()
            await message.channel.send(f"🚫 {message.author.mention} ห้ามส่งลิงก์นะจ๊ะ", delete_after=5)
            return
    await bot.process_commands(message)

# คำสั่งสมัคร
@bot.command()
async def register(ctx):
    embed = discord.Embed(
        title="ฟอร์มสมัครเข้าตระกูล JOKER",
        description="กดปุ่มด้านล่างเพื่อเริ่มกรอกฟอร์ม",
        color=discord.Color.green()
    )
    embed.set_image(url="https://i.postimg.cc/vZshFbpd/image.png")

    button = Button(label="เริ่มกรอกฟอร์ม", style=discord.ButtonStyle.green)

    async def button_callback(interaction: discord.Interaction):
        modal = Modal(title="ฟอร์มเข้าตระกูล Joker")

        ic_name_input = TextInput(label="ชื่อใน IC/OC", style=discord.TextStyle.short)
        ic_age_input = TextInput(label="อายุใน IC/OC", style=discord.TextStyle.short)
        ic_gender_input = TextInput(label="เพศใน IC/OC", style=discord.TextStyle.short)
        roblox_username_input = TextInput(label="ชื่อผู้ใช้ Roblox", style=discord.TextStyle.short)
        free_time_input = TextInput(label="เวลาว่าง & เคยอยู่กับตระกูล/แก๊ง & อาวุธ", style=discord.TextStyle.short)

        modal.add_item(ic_name_input)
        modal.add_item(ic_age_input)
        modal.add_item(ic_gender_input)
        modal.add_item(roblox_username_input)
        modal.add_item(free_time_input)

        async def modal_submit(interaction: discord.Interaction):
            ic_name = ic_name_input.value
            ic_age = ic_age_input.value
            ic_gender = ic_gender_input.value
            roblox_username = roblox_username_input.value
            free_time = free_time_input.value

            admin_channel = bot.get_channel(ADMIN_CHANNEL_ID)
            announce_channel = bot.get_channel(ANNOUNCE_CHANNEL_ID)

            if not admin_channel or not announce_channel:
                await interaction.response.send_message("❗ ไม่พบช่องแอดมินหรือช่องประกาศ กรุณาตรวจสอบการตั้งค่า", ephemeral=True)
                return

            approve_button = Button(label="✅ อนุมัติ", style=discord.ButtonStyle.green)
            reject_button = Button(label="❌ ปฏิเสธ", style=discord.ButtonStyle.red)

            async def approve_callback(admin_interaction: discord.Interaction):
                role = discord.utils.get(interaction.guild.roles, name="꒰ㆍกรอกแล้ว")
                if role:
                    await interaction.user.add_roles(role)
                    await admin_interaction.response.send_message(f"✅ อนุมัติแล้ว! {interaction.user.mention} ได้รับยศ {role.mention}")

                    await announce_channel.send(
                        embed=discord.Embed(
                            title="🎉 สมัครผ่านแล้ว!",
                            description=f"✅ **ยินดีด้วย {interaction.user.mention}!**\nขั้นตอนต่อไปคือรอสอบนะครับ เดี๋ยวแอดมินจะแท็กเรียกมาสอบนะครับ",
                            color=discord.Color.green()
                        )
                    )
                else:
                    await admin_interaction.response.send_message("❗ ไม่พบยศ '꒰ㆍกรอกแล้ว' โปรดแจ้งแอดมินให้สร้างยศนี้ก่อน!", ephemeral=True)

            async def reject_callback(admin_interaction: discord.Interaction):
                modal_reject = Modal(title="ปฏิเสธการสมัคร")
                reason_input = TextInput(label="เหตุผลที่ปฏิเสธ", style=discord.TextStyle.paragraph, required=True)
                modal_reject.add_item(reason_input)

                async def reject_submit(reject_interaction: discord.Interaction):
                    reason = reason_input.value
                    reject_embed = discord.Embed(
                        title="❌ การสมัครไม่ผ่าน",
                        description=f"🚫 {interaction.user.mention} **การสมัครไม่ผ่าน**\n📌 **เหตุผล:** {reason}",
                        color=discord.Color.red()
                    )
                    await announce_channel.send(embed=reject_embed)
                    await reject_interaction.response.send_message("❌ ปฏิเสธสำเร็จ", ephemeral=True)

                modal_reject.on_submit = reject_submit
                await admin_interaction.response.send_modal(modal_reject)

            approve_button.callback = approve_callback
            reject_button.callback = reject_callback

            view = View()
            view.add_item(approve_button)
            view.add_item(reject_button)

            await admin_channel.send(
                embed=discord.Embed(
                    title="📌 สมัครเข้าตระกูล",
                    description=(
                        f"👤 **ผู้ใช้:** {interaction.user.mention}\n"
                        f"📌 **ชื่อใน IC/OC:** {ic_name}\n"
                        f"🎂 **อายุใน IC/OC:** {ic_age}\n"
                        f"🚻 **เพศใน IC/OC:** {ic_gender}\n"
                        f"🎮 **ชื่อผู้ใช้ Roblox:** {roblox_username}\n"
                        f"⏳ **เวลาว่าง & เคยอยู่กับตระกูล/แก๊ง & อาวุธ:** {free_time}\n"
                    ),
                    color=discord.Color.green()
                ),
                view=view
            )

            await interaction.response.send_message("✅ กรอกฟอร์มเรียบร้อยแล้วนะครับ", ephemeral=True)

        modal.on_submit = modal_submit
        await interaction.response.send_modal(modal)

    button.callback = button_callback
    view = View()
    view.add_item(button)
    await ctx.send(embed=embed, view=view)

# คำสั่งประกาศ
@bot.command()
async def announce(ctx, title: str, *, content: str):
    # ตรวจสอบว่าเป็นแอดมินหรือไม่
    if not ctx.author.guild_permissions.administrator:
        # ส่งข้อความแจ้งเตือนส่วนตัว (ไม่ใช่ DM)
        await ctx.author.send("คุณไม่มีสิทธิ์ในการประกาศ!")
        return
    
    # สร้าง Embed สำหรับประกาศ
    embed = discord.Embed(
        title=f"ประกาศจากแอดมิน: {title}",
        description=content,
        color=discord.Color.blue(),
        timestamp=datetime.datetime.utcnow()
    )
    
    # ตั้งค่าภาพ thumbnail ด้วยโปรไฟล์ของผู้ประกาศ
    embed.set_thumbnail(url=ctx.author.avatar.url)

    # เพิ่ม fields สำหรับข้อมูลประกาศ
    embed.add_field(name="ผู้ประกาศ", value=f"{ctx.author.name}", inline=False)
    embed.add_field(name="เรื่องที่ประกาศ", value=title, inline=False)
    embed.add_field(name="เวลาที่ประกาศ", value=f"{datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", inline=False)

    # ไอคอนสำหรับแสดงใน Embed
    embed.set_footer(text="ประกาศจากแอดมิน", icon_url="https://i.postimg.cc/rFKFxr8c/jokershield.png")

    # ส่ง Embed ไปยังช่องที่ต้องการ (ใช้ Channel ID)
    channel = bot.get_channel(1341042873126359102)  # เปลี่ยนเป็น ID ของช่องที่ต้องการ
    if channel:
        await channel.send(embed=embed)
        # ส่งข้อความแจ้งว่า "ประกาศแล้ว" ไปยังผู้ใช้งาน
        await ctx.author.send(f"ประกาศเรื่อง '{title}' ได้ถูกส่งไปยังช่องแล้ว")
    else:
        # หากไม่พบช่อง ให้แจ้งผู้ใช้งานว่าไม่สามารถส่งได้
        await ctx.author.send("ไม่พบช่องที่ต้องการส่งข้อความไป")

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

    server_on()
    keep_alive()


bot.run(os.getenv("TOKEN"))