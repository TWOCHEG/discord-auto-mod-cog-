import disnake
from disnake.ext import commands
from FluffBot import config
import random
from urllib.parse import urlparse
from FluffBot.modules.utils.def_modules import def_time_out


class LinkAutoMod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.whitelist = [
            "https://www.youtube.com/",
            "https://youtu.be/",
            "https://github.com/",
            "https://cdn.discordapp.com/",
            "https://stackoverflow.com/",
            "https://otvet.mail.ru/",
            "https://qna.habr.com/",
            "https://yandex.ru/games/",
            "https://media1.tenor.com/",
            "https://media.tenor.com/",
            "https://tenor.com/",
            "https://ru.wikipedia.org/wiki/",
            "https://chatgpt.com/"
        ]  # вайт лист ссылок

      async def time_out(self, time, member, message):
        try:
            await member.timeout(until=disnake.utils.utcnow() + timedelta(seconds=time))
        except Exception:
            await message.channel.send('кажется что тебя нельзя замутить((')
        else:
            pass

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author == self.bot.user:
            return

        if 'https://t.me/hamsteR_kombat_bot/' in message.content:
            embed = disnake.Embed(
                title='⚠\nнайдена ссылка на хомяка, отправитель изолирован',
                description=f'отправитель - {message.author.mention}>\nпросьба больше не входить в диалог с '
                            f'пользователем {message.author.mention} и сохранять бдительность\nв неактивный период бота '
                            f'просим вас не открывать ссылки: `https://t.me/hamsteR_kombat_bot/*` т.к. это может '
                            f'привести к серьёзному заболеванию : `хомяк` - [Подробнее](<https://www.youtube.com/watch?v=GFq6wH5JR2A>)',
                colour=0xeb459e
            )
            embed.set_thumbnail(
                url='https://cdn.discordapp.com/attachments/1253349916764409966/1264222788986605651/1.png?ex=669d16b9&is=669bc539&hm=81208806912f66a48c608e09be0ae295346cebd37eca3a4e4f31338848ddc10d&')

            await message.delete()
            await message.channel.send(embed=embed)
            await time_out(time=600, member=message.author, message=message)

        else:
            contains_unwhitelisted_link = await self.contains_unwhitelisted_link(message.content)

            if contains_unwhitelisted_link:
                await message.delete()
                text = random.choice(['Упс', 'Ой'])

                embed = disnake.Embed(
                    title=f'{text}, кажется, что твоей ссылки нет в белом списке :(',
                    description='',
                    colour=0xeb459e
                )
                embed.add_field(
                    name='белый лист:',
                    value='```' + '\n'.join([f'{url}' for url in self.whitelist]) + '```'
                )

                await message.channel.send(f'{message.author.mention}', embed=embed)

                print(f'{config.console_event}на {message.author.name} сработал LinkAutoMod : {message.content}')

    async def contains_unwhitelisted_link(self, content: str) -> bool:
        for word in content.split():
            if word.startswith(("http://", "https://")):
                parsed_url = urlparse(word)
                domain = f"{parsed_url.scheme}://{parsed_url.netloc}/"
                if all(domain != url for url in self.whitelist):
                    return True

        return False


def setup(bot: commands.Bot):
    bot.add_cog(LinkAutoMod(bot))
