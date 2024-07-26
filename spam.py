from disnake.ext import commands
import disnake
from collections import defaultdict

intents = disnake.Intents.default()
intents.message_content = True

ctx = 7
reference = False
mention_ctx = 1
message = 2
mention = 2


class AntiSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_counts = {}
        self.user_messages = defaultdict(list)
        self.mention_counts = {}
        self.mentions_counters = {}

    async def time_out(self, time, member, message):
        try:
            await member.timeout(until=disnake.utils.utcnow() + timedelta(seconds=time))
        except Exception:
            await message.channel.send('кажется что тебя нельзя замутить((')
        else:
            pass

    async def SpamCheck(self, message):
        data = def_config.read_config(guild_id=guild_id)
        if data['auto_mod']['completed'] == 1 and data['auto_mod']['auto_mod_on'] == 1:
            if message.author.bot:
                return

            # Проверка на повторяющиеся слова
            if len(message.content.split()) > ctx:
                words = message.content.split()
                if any(words.count(word) > data['auto_mod']['spam_ctx_count'] for word in words):
                    await self.time_out(time=600, member=message.author, message=message)
                    embed = disnake.Embed(
                        title=f'{message.author.name} замучен за спам',
                        description=f'тип спама - слова в контексте\nмут - 10 минут',
                        colour=0xFF1493
                    )
                    await message.channel.send(embed=embed)

            # Проверка на упоминания в контексте
            if message.mentions and len(message.mentions) > mention_ctx and message.author != self.bot.user:
                await self.time_out(time=600, member=message.author, message=message)
                embed = disnake.Embed(
                    title=f'{message.author.name} замучен за спам',
                    description=f'тип спама - упоминания в контексте\nмут - 10 минут',
                    colour=0xFF1493
                )
                await message.channel.send(embed=embed)

            # упоминания подряд (1)
            if message.mentions:
                # Проверка, что упоминания находятся в основном тексте сообщения, а не в ответе
                if len(message.mentions) == 1:
                    if message.reference:
                        # проверяем учитывается ли референс как спам
                        if data['auto_mod']['reference'] == 0:
                            return

                    # Если сообщение содержит упоминания
                    if message.author.id in self.mention_counts:
                        self.mention_counts[message.author.id] += 1
                    else:
                        self.mention_counts[message.author.id] = 1

                    if self.mention_counts[message.author.id] > mention:
                        await self.time_out(time=600, member=message.author, message=message)
                        embed = disnake.Embed(
                            title=f'{message.author.name} замучен за спам',
                            description=f'тип спама - упоминания\nмут - 10 минут',
                            colour=0xFF1493
                        )
                        await message.channel.send(embed=embed)

                        self.mention_counts[message.author.id] = 0  # Сброс счетчика после действия

            else:
                # Если сообщение без упоминаний, сбрасываем счетчик для этого пользователя
                if message.author.id in self.mention_counts:
                    self.mention_counts[message.author.id] = 0

            # упоминания подряд (2)
            mentions = message.mentions
            if mentions:
                if message.reference:
                    # проверяем учитывается ли референс как спам
                    if reference:
                        return
                # Получаем ID упомянутых участников (исключая автора сообщения)
                mentioned_ids = set([mention.id for mention in mentions if mention != message.author])

                # Получаем текущий счетчик для автора сообщения или устанавливаем новый, если его нет
                if message.author.id not in self.mentions_counters:
                    self.mentions_counters[message.author.id] = {'current_count': 0, 'last_mentioned_ids': set()}

                counter = self.mentions_counters[message.author.id]

                # Проверяем, отличаются ли упомянутые участники от предыдущих сообщений
                if mentioned_ids != counter['last_mentioned_ids']:
                    # Сбрасываем счетчик, так как упоминаются новые участники
                    counter['current_count'] = 1
                    counter['last_mentioned_ids'] = mentioned_ids
                else:
                    # Увеличиваем счетчик, так как упоминания те же самые
                    counter['current_count'] += 1

                # Проверяем, достиг ли счетчик значения N для автора сообщения
                if counter['current_count'] > mention:
                    await self.time_out(time=600, member=message.author, message=message)
                    embed = disnake.Embed(
                        title=f'{message.author.name} замучен за спам',
                        description=f'тип спама - упоминания\nмут - 10 минут',
                        colour=0xFF1493
                    )
                    await message.channel.send(embed=embed)

            else:
                # Сбрасываем счетчик для автора сообщения, так как нет упоминаний
                if message.author.id in self.mentions_counters:
                    self.mentions_counters[message.author.id] = {'current_count': 0, 'last_mentioned_ids': set()}

            await self.bot.process_commands(message)

            # проверка на повторяющийся сообщения
            author_id = message.author.id
            if author_id not in self.message_counts:
                self.message_counts[author_id] = {'last_message': None, 'count': 0}

            if message.content == self.message_counts[author_id]['last_message']:
                self.message_counts[author_id]['count'] += 1
            else:
                self.message_counts[author_id] = {'last_message': message.content, 'count': 1}

            # проверка на сообщения подряд
            if self.message_counts[author_id]['count'] > massage:
                await self.time_out(time=600, member=message.author, message=message)
                embed = disnake.Embed(
                    title=f'{message.author.name} замучен за спам',
                    description=f'тип спама - сообщения\nмут - 10 минут',
                    colour=0xFF1493
                )
                await message.channel.send(embed=embed)

                # сбросить счётчик
                self.message_counts[author_id] = {'last_message': None, 'count': 0}

    @commands.Cog.listener()
    async def on_message(self, message):
        # проверку на права администратора сделайте сами мне лень
        await self.SpamCheck(message)


def setup(bot):
    bot.add_cog(AntiSpam(bot))
