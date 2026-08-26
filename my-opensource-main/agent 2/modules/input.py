from modules.config import *
from modules.console import *
from modules.lamb import print_lambda

def v2i(title='', subtitle='', default=None):
    config = load_config(USERNAME)
    style = config.get('input_style', '1')
    
    if style == '5':
        display_title = title
        if default:
            display_title += f' (Enter: {default[:20]}...)' if len(default) > 20 else f' (Enter: {default})'
        console.print(
            f'[primary]{USERNAME}[/primary] '
            f'[secondary]{display_title}[/secondary] '
            f'[dim]{subtitle}[/dim]'
        )
        user_input = console.input('[highlight]λ[/highlight] ')
        return user_input if user_input.strip() else (default or "")
    
    if style == '2':
        prompt = f'[primary]{USERNAME}[/primary][white]@[/white][secondary]{UUID}[/secondary] [white]$ [/white]'
        if title:
            prompt += f'[primary]{title}[/primary] [white]> [/white]'
        user_input = console.input(prompt)
        return user_input if user_input.strip() else (default or "")
        
    elif style == '3':
        prompt = f'[highlight]⚡[/highlight] [primary]lightwave[/primary] [dim]•[/dim] '
        if title:
            prompt += f'[secondary]{title}[/secondary] '
        prompt += '[highlight]❯[/highlight] '
        user_input = console.input(prompt)
        return user_input if user_input.strip() else (default or "")
        
    elif style == '4':
        prompt = f'[primary]❯[/primary] '
        if title:
            prompt += f'[secondary]{title}[/secondary] '
        prompt += '[white]» [/white]'
        user_input = console.input(prompt)
        return user_input if user_input.strip() else (default or "")
        
    else:
        display_title = title
        if default:
            display_title += f' (Enter: {default[:20]}...)' if len(default) > 20 else f' (Enter: {default})'
            
        console.print(
            f'[{PL["bg1"]}] lightwave '
            f'[{PL["bg2"]}] ⚡ {display_title} '
            f'[{PL["bg3"]}] {subtitle} [/]',
            end='\n'
        )
        user_input = console.input('[secondary]❯[/] ')
        return user_input if user_input.strip() else (default or "")