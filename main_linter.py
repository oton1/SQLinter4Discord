import discord
import sqlparse
import re
from dotenv import load_dotenv
import os
from linter import validate_sql

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def beautify_sql(sql_query):
    lines = sql_query.split('\n')
    formatted_lines = []

    for line in lines:
        if '--' in line:
            formatted_lines.append(line)
        else:
            functions_to_format = [
                'avg', 'count', 'max', 'min', 'sum', 'abs', 'ceil', 'floor', 'round', 'mod',
                'current_date', 'current_time', 'current_timestamp', 'date_add', 'date_sub', 
                'datediff', 'now', 'to_date', 'to_char', 'to_timestamp', 'concat', 'length', 
                'lower', 'upper', 'substring', 'trim', 'ltrim', 'rtrim', 'replace', 'coalesce', 
                'nullif', 'case', 'if', 'like'
            ]
            
            for func in functions_to_format:
                line = re.sub(rf'\b{func}\b', func.upper(), line, flags=re.IGNORECASE)
            
            formatted_query = sqlparse.format(
                line,
                reindent=True,
                keyword_case='upper',
                indent_tabs=False,
                indent_width=4,
                wrap_after=80,
            )
            
            formatted_query = re.sub(r'\s+CASE\b', '\nCASE', formatted_query, flags=re.IGNORECASE)
            formatted_query = re.sub(r'\s+WHEN\b', '\nWHEN', formatted_query, flags=re.IGNORECASE)
            formatted_query = re.sub(r'\s+THEN\b', '\nTHEN', formatted_query, flags=re.IGNORECASE)
            formatted_query = re.sub(r'\s+ELSE\b', '\nELSE', formatted_query, flags=re.IGNORECASE)
            formatted_query = re.sub(r'\s+END\b', '\nEND', formatted_query, flags=re.IGNORECASE)
            
            select_pattern = re.compile(r'(SELECT\s+)(.*?)(\s+FROM\s+)', re.IGNORECASE | re.DOTALL)
            formatted_query = select_pattern.sub(lambda m: m.group(1) + '\n    ' + ',\n    '.join(m.group(2).split(',')) + m.group(3), formatted_query)
            
            formatted_query = re.sub(r'\n\s*\n', '\n', formatted_query)
            formatted_lines.append(formatted_query)
    
    return '\n'.join(formatted_lines)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!sql'):
        sql_query = message.content[len('!sql '):].strip()
        
        if message.attachments:
            for attachment in message.attachments:
                if attachment.filename.endswith('.txt'):
                    sql_query = await attachment.read()
                    sql_query = sql_query.decode('utf-8') 
        
        if sql_query:
            is_valid, validation_message = validate_sql(sql_query)
            if is_valid:
                formatted_query = beautify_sql(sql_query)
                embed = discord.Embed(title="SQLinter", description=f"```sql\n{formatted_query}\n```", color=0x00ff00)
            else:
                embed = discord.Embed(title="SQLinter", description=f"Query SQL inválida: {validation_message}", color=0xff0000)
            await message.channel.send(embed=embed)
        else:
            await message.channel.send("Nenhuma query SQL fornecida.")
    
    elif message.content.startswith('!help'):
        embed = discord.Embed(title="SQLinter", description="Use `!sql <your SQL query>` ou anexe um arquivo .txt com a query.", color=0x00ff00)
        await message.channel.send(embed=embed)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

client.run(os.getenv('TOKEN'))