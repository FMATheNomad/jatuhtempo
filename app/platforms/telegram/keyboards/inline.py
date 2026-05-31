import uuid

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def debt_keyboard(debt_id: uuid.UUID) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Lunas", callback_data=f"paid:{debt_id}")
    builder.button(text="🔴 Terlambat", callback_data=f"late:{debt_id}")
    return builder.as_markup()


def confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Simpan", callback_data="ocr_confirm")
    builder.button(text="❌ Batal", callback_data="ocr_cancel")
    return builder.as_markup()
