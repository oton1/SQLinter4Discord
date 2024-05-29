import discord
import sqlparse
import re
from dotenv import load_dotenv
import os
from linter import validate_sql

load_dotenv()

intents = discord.Intents.all()
intents.message_content = True
client = discord.Client(intents=intents)

def beautify_sql(sql_query):
    functions_to_format = [
        'avg', 'count', 'max', 'min', 'sum', 'abs', 'ceil', 'floor', 'round', 'mod',
        'current_date', 'current_time', 'current_timestamp', 'date_add', 'date_sub', 
        'datediff', 'now', 'to_date', 'to_char', 'to_timestamp', 'concat', 'length', 
        'lower', 'upper', 'substring', 'trim', 'ltrim', 'rtrim', 'replace', 'coalesce', 
        'nullif', 'case', 'if'
    ]
    
    for func in functions_to_format:
        sql_query = re.sub(rf'\b{func}\b', func.upper(), sql_query, flags=re.IGNORECASE)

    formatted_query = sqlparse.format(
        sql_query,
        reindent=True,
        keyword_case='upper',
        indent_tabs=False,  
        indent_width=4,     
        wrap_after=80,      
    )

    lines = formatted_query.split('\n')
    adjusted_query = []
    indent_level = 0
    for line in lines:
        stripped_line = line.strip()
        
        if re.match(r'CASE\b', stripped_line, re.IGNORECASE):
            adjusted_query.append(' ' * (indent_level * 4) + stripped_line)
            indent_level += 1
        elif re.match(r'WHEN\b|THEN\b|ELSE\b', stripped_line, re.IGNORECASE):
            adjusted_query.append(' ' * (indent_level * 4) + stripped_line)
        elif re.match(r'END\b', stripped_line, re.IGNORECASE):
            indent_level -= 1
            adjusted_query.append(' ' * (indent_level * 4) + stripped_line)
        else:
            if stripped_line.startswith('AND') or stripped_line.startswith('OR'):
                indent_level = 1
            if stripped_line.endswith(')'):
                indent_level -= 1

            adjusted_query.append(' ' * (indent_level * 4) + stripped_line)

            if stripped_line.endswith('('):
                indent_level += 1
    
    return '\n'.join(adjusted_query)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('!sql'):
        sql_query = message.content[len('!sql '):]
        is_valid, validation_message = validate_sql(sql_query)
        if is_valid:
            formatted_query = beautify_sql(sql_query)
            embed = discord.Embed(title="SQLinter", description=f"```sql\n{formatted_query}\n```", color=0x00ff00)
        else:
            embed = discord.Embed(title="SQLinter", description=f"Query SQL inválida: {validation_message}", color=0xff0000)
        await message.channel.send(embed=embed)
    
    elif message.content.startswith('!help'):
        embed = discord.Embed(title="SQLinter", description="Use `!sql <your SQL query>`.", color=0x00ff00)
        await message.channel.send(embed=embed)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

client.run(os.getenv('TOKEN'))

#próximo passo: fazer o bot aceitar arquivos de texto com queries