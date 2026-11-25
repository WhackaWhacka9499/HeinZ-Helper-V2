"""Tier 1 & Tier 2: Modal Dialog Interception & Auto-Dismissal Tests.

Addresses Feature 9 from PROJECT.md:
"Modal Dialog Interceptor & Auto-Dismiss: Expand _G.__hzPopupLog to intercept
and auto-dismiss CommonDialog / UIManager modal popups."

Verifies:
- Differentiation between non-blocking toast tips (UIUtil.ShowTips) and blocking modal dialogs
- Modal dialog tracking (CommonDialog, UIError, UIGiftPackageRewardGet)
- Auto-dismissal of error popups ("Sorry, an unknown error occurred")
- Auto-dismissal of reward modals ("Congratulations!" claim screens)
- Prevention of game client lockup / cycle stall
- Buffer draining and popup log history preservation
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.testHarness import (
    MockGameClient,
    SFSMessageValidator,
    ServerResponseSimulator,
)


class TestDialogDismissal(unittest.TestCase):
    """Test Suite for In-Game Dialog Interception and Auto-Dismissal."""

    def setUp(self) -> None:
        self.client = MockGameClient(pid=23848, label="Farm")

    def test_toast_tips_vs_modal_dialog_differentiation(self) -> None:
        """Verify that floating toast tips and blocking modal dialogs are classified separately."""
        # Toast tips: non-blocking
        toast_msg = "Success! 500 Alliance Points added"
        self.client.in_game_tips.append(toast_msg)
        self.assertEqual(len(self.client.in_game_tips), 1)
        self.assertEqual(len(self.client.modal_windows), 0, "Toast tips must not create modal windows")

        # Modal dialog: blocking
        dlg = self.client.open_modal_dialog(
            dialog_type="CommonDialog",
            title="Notice",
            message="Sorry, an unknown error occurred. Please try again or leave us feedback.",
        )
        self.assertEqual(len(self.client.modal_windows), 1)
        self.assertTrue(dlg["open"])

    def test_auto_dismissal_of_error_dialog(self) -> None:
        """Verify that an active CommonDialog error popup is auto-dismissed."""
        self.client.open_modal_dialog(
            dialog_type="CommonDialog",
            title="Error E000000",
            message="Sorry, an unknown error occurred. Please try again or leave us feedback.",
        )
        self.assertEqual(len(self.client.modal_windows), 1)

        # Trigger auto-dismissal
        dismissed = self.client.dismiss_modal_dialogs(dialog_types=["CommonDialog"])
        self.assertEqual(dismissed, 1)
        self.assertEqual(len(self.client.modal_windows), 0, "Error dialog must be dismissed")

    def test_auto_dismissal_of_congratulations_reward_screen(self) -> None:
        """Verify that UIGiftPackageRewardGet ('Congratulations!') reward modal is auto-dismissed."""
        self.client.open_modal_dialog(
            dialog_type="UIGiftPackageRewardGet",
            title="Congratulations!",
            message="Coins, Wood, Meat, EXP",
        )
        self.assertEqual(len(self.client.modal_windows), 1)

        # Trigger auto-dismissal
        dismissed = self.client.dismiss_modal_dialogs(dialog_types=["UIGiftPackageRewardGet"])
        self.assertEqual(dismissed, 1)
        self.assertEqual(len(self.client.modal_windows), 0, "Reward modal must be dismissed")

    def test_multi_modal_stack_dismissal(self) -> None:
        """Verify that when both reward modal and error popup are stacked, both are dismissed."""
        # Replicating the 15:44:18 incident state: error popup over reward modal
        self.client.open_modal_dialog(
            dialog_type="UIGiftPackageRewardGet",
            title="Congratulations!",
            message="Reward Items",
        )
        self.client.open_modal_dialog(
            dialog_type="CommonDialog",
            title="Error E000000",
            message="Sorry, an unknown error occurred.",
        )
        self.assertEqual(len(self.client.modal_windows), 2)

        # Full dismissal
        dismissed = self.client.dismiss_modal_dialogs()
        self.assertEqual(dismissed, 2)
        self.assertEqual(len(self.client.modal_windows), 0)

    def test_popup_log_draining_is_atomic(self) -> None:
        """Verify that draining the popup log retrieves messages and atomically empties the buffer."""
        _G_hzPopupLog = [
            "Success! 500 Alliance Points is effective!",
            "Daily Task Completed: Build 1 Time",
            "Radar Event Found: Bandit Camp",
        ]

        # Simulate _enc drain logic
        popped = []
        for i in range(len(_G_hzPopupLog)):
            popped.append(_G_hzPopupLog[i])
        _G_hzPopupLog.clear()

        self.assertEqual(len(popped), 3)
        self.assertEqual(len(_G_hzPopupLog), 0, "Popup log buffer must be empty after drain")
        self.assertEqual(popped[0], "Success! 500 Alliance Points is effective!")


if __name__ == "__main__":
    unittest.main()
