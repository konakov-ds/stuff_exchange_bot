import os
from django.core.management.base import BaseCommand
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import MessageHandler, CommandHandler, Updater, Filters, CallbackContext
from dotenv import load_dotenv

from telbot.models import Profile, Message

load_dotenv()
token = os.getenv('TELEGRAM_TOKEN')

categories = ['Транспорт',
              'Одежда, обувь',
              'Аксессуары и украшения',
              'Детская одежда и обувь',
              'Игрушки и детские транспортвещи',
              'Бытовая техника',
              'Мебель и интерьерные вещи',
              'Кухонная утварь',
              'Продукты питания',
              'Вещи для ремонта и строительства',
              'Растения',
              'Электроника',
              'Спортивные вещи',
              'Вещи для творчества и хобби',
              'Коллекционные вещи'
              ]


class Command(BaseCommand):
    help = 'Телеграм бот'

    def handle(self, *args, **kwargs):
        updater = Updater(token, use_context=True)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler('start', self.start_bot))
        dispatcher.add_handler(CommandHandler('help', self.bot_help))
        dispatcher.add_handler(MessageHandler(filters=Filters.text,
                                              callback=self.button_message_handler))
        dispatcher.add_handler(MessageHandler(filters=Filters.document,
                                              callback=self.photo_handler))
        updater.start_polling()
        updater.idle()

    @staticmethod
    def create_main_keyboard():
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Добавить вещь'),
                    KeyboardButton(text='Найти вещь'),
                    KeyboardButton(text='Обменяться')
                ],
            ],
            resize_keyboard=True
        )
        return markup

    @staticmethod
    def create_add_item_keyboard():
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Выберите категорию'),
                    KeyboardButton(text='Добавьте фото'),
                    KeyboardButton(text='Добавьте название')
                    ,
                ],
                [
                    KeyboardButton(text='Вернуться в главное меню')
                ]
            ],
            resize_keyboard=True
        )
        return markup

    @staticmethod
    def create_category_keyboard():
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=category) for category in categories[i: i + 2]
                ]
                for i in range(0, len(categories) - 2, 2)
            ],
            resize_keyboard=True
        )
        return markup

    def start_bot(self, update, context):
        chat_id = update.effective_chat.id
        text = update.message.text
        self.p, _ = Profile.objects.get_or_create(
            tg_id=chat_id,
            defaults={
                'name': update.message.from_user.name,
            }
        )
        Message(
            profile=self.p,
            text=text
        ).save()
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Привет!\nЯ бот для обмена вещей.\nВыбери нужный пункт в меню.",
            reply_markup=self.create_main_keyboard(),
        )

    @staticmethod
    def bot_help(update, context):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Справка по работе с ботом для обмена вещей.",
        )

    def button_message_handler(self, update, context):
        if update.message.text == 'Добавить вещь':
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Выбери нужный пункт в меню.",
                reply_markup=self.create_add_item_keyboard(),
            )
        elif update.message.text == 'Вернуться в главное меню':
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Вы вернулись в главное меню',
                reply_markup=self.create_main_keyboard(),
            )
        elif update.message.text == 'Выберите категорию':
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Выбери категорию",
                reply_markup=self.create_category_keyboard(),
            )

        elif update.message.text in categories:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Вы выбрали {update.message.text}",
                reply_markup=self.create_add_item_keyboard(),
            )
            Message(
                profile=self.p,
                text=update.message.text,
            ).save()

        elif update.message.text == 'Добавьте фото':
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Загрузите фото",
                reply_markup=self.create_add_item_keyboard(),
            )

        elif update.message.text == 'Добавьте название':
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Напишите название вашей вещи",
                reply_markup=self.create_add_item_keyboard(),
            )
            print(update.message.text)
        elif update.message.text == 'Найти вещь':
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='[ФОТО]',
                reply_markup=self.create_main_keyboard(),
            )
        elif update.message.text == 'Обменяться':
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='[КОНТАКТЫ ДЛЯ ОБМЕНА]',
                reply_markup=self.create_main_keyboard(),
            )

    def photo_handler(update, context):
        file = update.message.document
        obj = context.bot.get_file(file['file_id'])
        # print(file)
        obj.download()
        update.message.reply_text("Фото получено")