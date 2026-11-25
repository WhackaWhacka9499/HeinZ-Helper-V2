#!/usr/bin/env python3
"""LastZ PC Master Overhaul - Unified Automated Test Runner.

Executes all 5 Tiers of verification tests:
- Tier 1: Feature Coverage & Protocol Contracts
- Tier 2: Boundary & Corner Cases
- Tier 3: Cross-Feature Integration & Live Cycle Transitions
- Tier 4: Real-World Application Scenarios (PID 23848 & PID 14952) & Benchmarks
- Tier 5: Adversarial Probes & Failure Injection

Returns exit code 0 when all tests pass cleanly.
"""

from __future__ import annotations

import os
import sys
import time
import unittest
from pathlib import Path
from typing import Dict, List, Tuple

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import test modules
from tests.testPacketContracts import TestPacketContracts
from tests.testRadarHospitalLogic import TestRadarHospitalLogic
from tests.testDialogDismissal import TestDialogDismissal
from tests.testHeroProgression import TestHeroProgression
from tests.testMapRip import TestMapRipBackend, TestMapRipUiContracts
from tests.testBoundaryCornerCases import TestBoundaryCornerCases
from tests.testCrossFeatureCombinations import TestCrossFeatureCombinations
from tests.testRealWorldScenarios import TestRealWorldScenarios
from tests.testEmpiricalChallenger import TestEmpiricalChallenger
from tests.testPerformanceOptimisations import (
    TestR1UiAndHubOptimisations,
    TestR1BotAndDiscoveryOptimisations,
    TestPerformanceBenchmarks,
)
from tests.testR2R3PreloadContracts import (
    TestR2HookAndBridgeContracts,
    TestR3MegamindPreloadContracts,
    TestR4GuardrailContracts,
)
from tests.testAdversarialProbes import (
    TestFridaSessionHolderAndPopupDismissal,
    TestHospitalCureAdversarialProbes,
    TestRadarQueueAdversarialProbes,
    TestPreparednessAndDailyClaimsAdversarialProbes,
)
from tests.testRssAndMapKills import (
    TestRssAndMapKillsMegamindContracts,
    TestRssAndMapKillsLuaBehavior,
    TestContinuousFarmLoopEngine,
    TestRssAndMapKillsUiContracts,
)
from tests.testTechCalculator import (
    TestTechBadgeMatrixParity,
    TestTechCalculatorBackend,
)
from tests.testUiLocales import TestUiLocales
from tests.testFarmLauncherGuard import TestFarmLauncherAutoHealGuard
from tests.testGameEngineManager import TestGameEngineManager
from tests.testAccountLauncherVault import TestAccountLauncherVault
from tests.testLiveTranslator import (
    TestGameTokenProtector,
    TestLanguageNormalization,
    TestProviderCascadeAndCache,
    TestLocalHttpServerRoundtrip,
    TestLuaHookGeneratorAndBehavior,
    TestDaemonWiringAndGuardrails,
)


TIER_MAPPING = {
    "Tier 1 (Feature Coverage & Contracts)": [
        (TestPacketContracts, "Packet Contracts & SFS Schemas"),
        (TestRadarHospitalLogic, "Radar Missions & Hospital Cure Logic"),
        (TestDialogDismissal, "Modal Dialog Interception & Auto-Dismiss"),
        (TestHeroProgression, "Hero Progression Automation & Heroes Hub Contracts"),
        (TestMapRipBackend, "Interactive Map Rip Target Finder Backend Contracts"),
        (TestTechBadgeMatrixParity, "Tech Badge Matrix 100% Parity vs APS_science XML"),
        (TestTechCalculatorBackend, "Tech Calculator Backend, Zero-Badge Logic, Queue & Bag Isolation"),
        (TestUiLocales, "18 Official Last Z UI Locales Parity, RTL & Hygiene"),
        (TestFarmLauncherAutoHealGuard, "Farm Launcher Post-Update Auto-Heal Guard & Hook Patcher"),
        (TestGameEngineManager, "V2 Standalone Last Z Game Engine Manager & CDN Updater"),
        (TestAccountLauncherVault, "V2 Email Account Vault, Borderless & Pure Vanilla Gate"),
        (TestGameTokenProtector, "Live Translator Last Z Token/Emoji/Coord Protection"),
        (TestLanguageNormalization, "Live Translator 18-Language Code Normalization"),
        (TestProviderCascadeAndCache, "Live Translator 4-Tier Cascade & SQLite/LRU Cache"),
        (TestLuaHookGeneratorAndBehavior, "Live Translator Lupa Lua Hook & Auto-Translate Guard"),
        (TestR1UiAndHubOptimisations, "R1 UI Delta/Visibility/Radar & Hub Cache Contracts"),
        (TestR1BotAndDiscoveryOptimisations, "R1/R2 Bot Module/Status/Config/Bridge Contracts"),
        (TestR2HookAndBridgeContracts, "R2 Frida Hook, Spatial Bucket & Reflection Cache Contracts"),
        (TestR3MegamindPreloadContracts, "R3 Read-Only Preload Manifest & Readiness Gate Contracts"),
        (TestRssAndMapKillsMegamindContracts, "RSS & Map Kills Megamind Protocol & Resource Parity"),
        (TestRssAndMapKillsLuaBehavior, "RSS & Map Kills Lupa-Backed Lua Behavioral Contracts"),
    ],
    "Tier 2 (Boundary & Corner Cases)": [
        (TestBoundaryCornerCases, "Empty Queues, Zero Troops, High Volume Stress"),
        (TestMapRipUiContracts, "Interactive Map Rip UI & DOM Contracts"),
        (TestR4GuardrailContracts, "R4 Guardrail Static Terminology Contracts"),
        (TestRssAndMapKillsUiContracts, "RSS & Map Kills UI, JS Clamping & Guardrail Contracts"),
        (TestDaemonWiringAndGuardrails, "Live Translator Daemon Supervision & Static Guardrails"),
    ],
    "Tier 3 (Cross-Feature Combinations)": [
        (TestCrossFeatureCombinations, "Live Cycle Transitions & Collision Prevention"),
        (TestContinuousFarmLoopEngine, "Continuous RSS & Map Kills Loop Engine & Safety Contracts"),
        (TestLocalHttpServerRoundtrip, "Live Translator HTTP /client.php, /health & /stats Roundtrip"),
    ],
    "Tier 4 (Real-World Application Scenarios)": [
        (TestRealWorldScenarios, "15:44:18 Incident Replication (PID 23848 & 14952)"),
        (TestPerformanceBenchmarks, "Performance Benchmarks (Discovery, Bot, Config & Live 42MB Map Rip)"),
    ],
    "Tier 5 (Adversarial Probes & Failure Injection)": [
        (TestFridaSessionHolderAndPopupDismissal, "Frida Session Holder & Popup Concurrency/Recovery"),
        (TestHospitalCureAdversarialProbes, "Hospital Cure Mixed Data Types & Hole Detection"),
        (TestRadarQueueAdversarialProbes, "Radar 20+ Mixed Queue Under 0, 1, 2 Formations"),
        (TestPreparednessAndDailyClaimsAdversarialProbes, "Full Preparedness & Daily Claims Boundaries"),
        (TestEmpiricalChallenger, "Empirical Challenger Edge Cases & Session Caching"),
    ],
}


def run_all_tests() -> int:
    """Run test suite and display structured report."""
    print("=" * 80)
    print(" LASTZ PC MASTER OVERHAUL - AUTOMATED VERIFICATION SUITE")
    print(" Environment: Windows 11 / Python 3.14 / Frida 17.9.2")
    print(f" Working Directory: {PROJECT_ROOT}")
    print("=" * 80)

    total_run = 0
    total_failures = 0
    total_errors = 0
    start_time = time.perf_counter()

    tier_stats: Dict[str, Dict[str, int]] = {}

    for tier_name, test_classes in TIER_MAPPING.items():
        print(f"\n>>> Running {tier_name}")
        print("-" * 80)
        tier_run = 0
        tier_fail = 0

        for test_cls, desc in test_classes:
            suite = unittest.TestLoader().loadTestsFromTestCase(test_cls)
            test_count = suite.countTestCases()
            print(f"  * {desc} ({test_count} tests)...", end="", flush=True)

            suite_start = time.perf_counter()
            result = unittest.TestResult()
            suite.run(result)
            suite_duration = time.perf_counter() - suite_start

            fails = len(result.failures)
            errs = len(result.errors)
            tier_run += test_count
            tier_fail += (fails + errs)

            if result.wasSuccessful():
                print(f" [PASS] ({suite_duration:.3f}s)")
            else:
                print(f" [FAIL] ({fails} failures, {errs} errors in {suite_duration:.3f}s)")
                for test, err in result.failures:
                    print(f"    - FAILURE: {test}\n      {err.strip()}")
                for test, err in result.errors:
                    print(f"    - ERROR: {test}\n      {err.strip()}")

        tier_stats[tier_name] = {"run": tier_run, "failed": tier_fail}
        total_run += tier_run
        total_failures += tier_fail

    total_duration = time.perf_counter() - start_time

    print("\n" + "=" * 80)
    print(" VERIFICATION SUITE SUMMARY")
    print("=" * 80)
    for tier_name, stats in tier_stats.items():
        status = "[PASS]" if stats["failed"] == 0 else "[FAIL]"
        print(f"  {status} {tier_name:<45} : {stats['run']} tests, {stats['failed']} failed")

    print("-" * 80)
    print(f" Total Tests Executed : {total_run}")
    print(f" Passed               : {total_run - total_failures}")
    print(f" Failed / Errors      : {total_failures}")
    print(f" Total Elapsed Time   : {total_duration:.3f}s")
    print("=" * 80)

    if total_failures == 0:
        print("\n [SUCCESS] ALL TEST SUITES PASSED CLEANLY (Exit Code 0)\n")
        return 0
    else:
        print(f"\n [FAILURE] {total_failures} TESTS FAILED (Exit Code 1)\n")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
