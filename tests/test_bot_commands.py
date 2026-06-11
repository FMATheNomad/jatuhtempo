"""
Tests for Telegram bot keyboard builders (no DB needed).
"""

import uuid
from app.platforms.telegram.keyboards.inline import (
    debt_keyboard,
    confirm_keyboard,
    confirm_nl_keyboard,
)


class TestDebtKeyboard:
    """Tests for debt_keyboard builder."""

    def test_debt_keyboard_structure(self):
        debt_id = uuid.uuid4()
        markup = debt_keyboard(debt_id)
        assert markup is not None

        # Should have 3 buttons arranged as [2, 1]
        buttons = markup.inline_keyboard
        assert len(buttons) == 2  # 2 rows (adjust=2,1)

        row1 = buttons[0]
        row2 = buttons[1]

        assert len(row1) == 2  # First row: 2 buttons
        assert len(row2) == 1  # Second row: 1 button

        # Verify button texts
        assert row1[0].text == "✅ Lunas"
        assert row1[1].text == "🔴 Terlambat"
        assert row2[0].text == "❌ Hapus"

    def test_debt_keyboard_callback_data(self):
        debt_id = uuid.uuid4()
        markup = debt_keyboard(debt_id)
        flat = [btn for row in markup.inline_keyboard for btn in row]

        callbacks = {btn.text: btn.callback_data for btn in flat}
        assert callbacks["✅ Lunas"] == f"paid:{debt_id}"
        assert callbacks["🔴 Terlambat"] == f"late:{debt_id}"
        assert callbacks["❌ Hapus"] == f"delete:{debt_id}"

    def test_debt_keyboard_different_ids(self):
        id1 = uuid.uuid4()
        id2 = uuid.uuid4()
        kb1 = debt_keyboard(id1)
        kb2 = debt_keyboard(id2)

        flat1 = [btn for row in kb1.inline_keyboard for btn in row]
        flat2 = [btn for row in kb2.inline_keyboard for btn in row]

        assert flat1[0].callback_data.endswith(str(id1))
        assert flat2[0].callback_data.endswith(str(id2))
        assert flat1[0].callback_data != flat2[0].callback_data


class TestConfirmKeyboard:
    """Tests for confirm_keyboard builder."""

    def test_confirm_keyboard_structure(self):
        markup = confirm_keyboard()
        buttons = markup.inline_keyboard
        assert len(buttons) == 1  # Single row
        assert len(buttons[0]) == 2
        assert buttons[0][0].text == "✅ Simpan"
        assert buttons[0][1].text == "❌ Batal"
        assert buttons[0][0].callback_data == "ocr_confirm"
        assert buttons[0][1].callback_data == "ocr_cancel"

    def test_confirm_nl_keyboard_structure(self):
        temp_key = "test-key-123"
        markup = confirm_nl_keyboard(temp_key)
        buttons = markup.inline_keyboard
        assert len(buttons) == 1
        assert len(buttons[0]) == 2
        assert buttons[0][0].text == "✅ Simpan"
        assert buttons[0][1].text == "❌ Batal"
        assert buttons[0][0].callback_data == f"confirm_debt:save:{temp_key}"
        assert buttons[0][1].callback_data == f"confirm_debt:cancel:{temp_key}"

    def test_confirm_nl_different_keys(self):
        kb1 = confirm_nl_keyboard("key1")
        kb2 = confirm_nl_keyboard("key2")
        flat1 = [btn for row in kb1.inline_keyboard for btn in row]
        flat2 = [btn for row in kb2.inline_keyboard for btn in row]
        assert flat1[0].callback_data != flat2[0].callback_data
        assert flat1[0].callback_data == "confirm_debt:save:key1"
        assert flat2[0].callback_data == "confirm_debt:save:key2"
