import telebot
import json
from datetime import datetime


current_year = datetime.now().year

with open('config.json') as config_json:
    cfg = json.load(config_json)

bot = telebot.TeleBot(cfg['bot_token'], parse_mode=None)


def is_int_in_valid_range(text, field_name):
    valid_range_str = f'(1900, {current_year}]'

    if text.isdigit():
        n = int(text)
    else:
        return False, f'{field_name} deve ser um número inteiro'

    if not (1900 < n <= current_year):
        return False, f'{field_name} deve estar no intervalo {valid_range_str}'

    return True, ''


def is_eligible(birth_year, enroll_year):
    birth_ok, reason = is_int_in_valid_range(birth_year, 'Ano de nascimento')
    if not birth_ok:
        return False, reason

    enroll_ok, reason = is_int_in_valid_range(enroll_year, 'Ano de ingresso')
    if not enroll_ok:
        return False, reason


    min_birth = current_year - 23
    min_enroll = current_year - 4

    birth_is_eligible = int(birth_year) >= min_birth
    enroll_is_eligible = int(enroll_year) >= min_enroll

    if not birth_is_eligible and not enroll_is_eligible:
        return False, ('Para ser elegível, você precisaria ter nascido'
                       f' a partir de {min_birth} ou entrado na universidade'
                       f' a partir de {min_enroll}')
    return True, ''


@bot.message_handler(commands=['start', 'help'])
def send_welcome(msg):
    bot.reply_to(msg,
        ('Bem-vindo ao bot de teste de elegibilidade da'
         ' maratona. Use o comando /testar para descobrir'
         ' se você é elegível.'))


@bot.message_handler(commands=['testar'])
def test_elegibility(msg):
    welcome_to_test = "Antes de testarmos sua elegibilidade, você precisa " \
            "saber que existe um número máximo de participações na maratona " \
            "(5) e no mundial (2). Além disso, existem exceções para a " \
            "regra de inelegibilidade por ano de ingresso na universidade, " \
            "em particular se sua primeira graduação foi em um curso de " \
            "humanas/saúde ou se você teve de interromper sua formação para " \
            "servir.\nDito isto, "
    sent_msg = bot.reply_to(
        msg, f'{welcome_to_test} *em que ano você nasceu?*',
        reply_markup=telebot.types.ForceReply(selective=False),
        parse_mode='markdown')
    bot.register_next_step_handler(sent_msg, birth_handler)


def birth_handler(msg):
    birth = msg.text
    sent_msg = bot.reply_to(
        msg, 'E em que ano você começou sua primeira graduação?',
        reply_markup=telebot.types.ForceReply(selective=False))
    bot.register_next_step_handler(sent_msg, enroll_handler, birth)


def enroll_handler(msg, birth_year):
    enroll_year = msg.text
    verdict, reason = is_eligible(birth_year, enroll_year)
    if verdict:
        bot.reply_to(msg, 'Você é elegível! Te vejo ano que vem.')
    else:
        bot.reply_to(msg, f'Você não é elegível. *{reason}*',
                     parse_mode='markdown')
        

bot.infinity_polling()
