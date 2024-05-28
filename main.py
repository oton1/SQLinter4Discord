import discord
import sqlparse
import re
from dotenv import load_dotenv
import os

load_dotenv()

intents = discord.Intents.all()
intents.message_content = True
client = discord.Client(intents=intents)

def beautify_sql(sql_query):
    formatted_query = sqlparse.format(sql_query, reindent=True, keyword_case='upper')

    functions_to_format = [
        'avg', 'count', 'max', 'min', 'sum',
        'abs', 'ceil', 'floor', 'round', 'mod',
        'current_date', 'current_time', 'current_timestamp', 'date_add', 'date_sub', 'datediff', 'now', 'to_date', 'to_char', 'to_timestamp',
        'concat', 'length', 'lower', 'upper', 'substring', 'trim', 'ltrim', 'rtrim', 'replace',
        'coalesce', 'nullif', 'case', 'if'
    ]
    
    for func in functions_to_format:
        formatted_query = re.sub(rf'\b{func}\b', func.upper(), formatted_query, flags=re.IGNORECASE)

    return formatted_query

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('!sql'):
        sql_query = message.content[len('!sql '):]
        formatted_query = beautify_sql(sql_query)
        embed = discord.Embed(title="SQLinter", description=f"```sql\n{formatted_query}\n```", color=0x00ff00)
        await message.channel.send(embed=embed)
    
    elif message.content.startswith('!help'):
        embed = discord.Embed(title="SQLinter", description="Use `!sql <sua query SQL>` para ter uma versão mais bonita da sua query.", color=0x00ff00)
        await message.channel.send(embed=embed)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

client.run(os.getenv('TOKEN'))
