import os
import tempfile
import unittest

from token_dashboard.db import init_db, connect
from token_dashboard.profile import (
    build_profile, steering_score, execution_score,
    engineering_score, planning_score, MIN_USER_TURNS_FOR_PROFILE, _archetype,
)


class ProfileTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db = os.path.join(self.tmp, "t.db")
        init_db(self.db)

    def _msg(self, uuid, session, mtype, ts, prompt_chars=None):
        with connect(self.db) as c:
            c.execute(
                "INSERT INTO messages (uuid, session_id, project_slug, type, timestamp, prompt_chars) "
                "VALUES (?, ?, 'p', ?, ?, ?)",
                (uuid, session, mtype, ts, prompt_chars),
            )
            c.commit()

    def _tool(self, uuid_prefix, session, tool_name, target, ts, is_error=0):
        with connect(self.db) as c:
            c.execute(
                "INSERT INTO tool_calls (message_uuid, session_id, project_slug, tool_name, target, timestamp, is_error) "
                "VALUES (?, ?, 'p', ?, ?, ?, ?)",
                (f"{uuid_prefix}-tc", session, tool_name, target, ts, is_error),
            )
            c.commit()


class InsufficientDataTests(ProfileTestBase):
    def test_below_minimum_returns_insufficient_data(self):
        for i in range(MIN_USER_TURNS_FOR_PROFILE - 1):
            self._msg(f"u{i}", "s1", "user", "2026-04-15T00:00:00Z", prompt_chars=50)
        result = build_profile(self.db)
        self.assertTrue(result["insufficient_data"])
        self.assertEqual(result["turns"], MIN_USER_TURNS_FOR_PROFILE - 1)

    def test_at_minimum_returns_full_profile(self):
        for i in range(MIN_USER_TURNS_FOR_PROFILE):
            self._msg(f"u{i}", "s1", "user", "2026-04-15T00:00:00Z", prompt_chars=50)
        result = build_profile(self.db)
        self.assertFalse(result["insufficient_data"])
        self.assertIn("scores", result)
        self.assertIn("archetype", result)
        for dim in ("steering", "execution", "engineering", "planning"):
            self.assertIn(dim, result["scores"])


class SteeringScoreTests(ProfileTestBase):
    def test_substantial_prompts_and_few_turns_score_high(self):
        for i in range(10):
            self._msg(f"u{i}", "s1", "user", "2026-04-15T00:00:00Z", prompt_chars=300)
        score = steering_score(self.db)
        self.assertGreater(score, 70)

    def test_trivial_prompts_and_many_turns_score_low(self):
        for i in range(40):
            self._msg(f"u{i}", "s1", "user", "2026-04-15T00:00:00Z", prompt_chars=5)
        score = steering_score(self.db)
        self.assertLess(score, 30)


class ExecutionScoreTests(ProfileTestBase):
    def test_clean_diverse_tool_use_scores_high(self):
        self._msg("u1", "s1", "user", "2026-04-15T00:00:00Z")
        for i, tool in enumerate(["Read", "Edit", "Write", "Bash", "Grep", "Glob", "Task", "Skill"]):
            self._tool(f"t{i}", "s1", tool, "x", "2026-04-15T00:00:00Z", is_error=0)
        score = execution_score(self.db)
        self.assertGreater(score, 70)

    def test_high_error_rate_scores_low(self):
        self._msg("u1", "s1", "user", "2026-04-15T00:00:00Z")
        for i in range(20):
            self._tool(f"t{i}", "s1", "Bash", "x", "2026-04-15T00:00:00Z", is_error=1)
        score = execution_score(self.db)
        self.assertLess(score, 30)


class EngineeringScoreTests(ProfileTestBase):
    def test_broad_low_retouch_scores_high(self):
        self._msg("u1", "s1", "user", "2026-04-15T00:00:00Z")
        for i in range(10):
            self._tool(f"t{i}", "s1", "Edit", f"file{i}.py", "2026-04-15T00:00:00Z")
        score = engineering_score(self.db)
        self.assertGreater(score, 60)

    def test_heavy_retouch_scores_low(self):
        self._msg("u1", "s1", "user", "2026-04-15T00:00:00Z")
        for i in range(10):
            self._tool(f"t{i}", "s1", "Edit", "same_file.py", "2026-04-15T00:00:00Z")
        score = engineering_score(self.db)
        self.assertLess(score, 40)


class PlanningScoreTests(ProfileTestBase):
    def test_frequent_delegation_scores_high(self):
        for i in range(4):
            self._msg(f"u{i}", f"s{i}", "user", "2026-04-15T00:00:00Z")
            self._tool(f"t{i}", f"s{i}", "Task", "subagent", "2026-04-15T00:00:00Z")
        score = planning_score(self.db)
        self.assertGreater(score, 90)

    def test_no_delegation_scores_zero(self):
        for i in range(4):
            self._msg(f"u{i}", f"s{i}", "user", "2026-04-15T00:00:00Z")
        score = planning_score(self.db)
        self.assertEqual(score, 0)


class ArchetypeLabelTests(unittest.TestCase):
    """_archetype() is pure label-selection logic — tested directly against
    synthetic score dicts rather than through the full scoring pipeline, so
    the test doesn't depend on the exact arithmetic of the four scoring
    functions (that arithmetic is already covered by the dimension tests
    above)."""

    def test_engineering_and_planning_top_gives_architect(self):
        scores = {"steering": 20, "execution": 30, "engineering": 90, "planning": 85}
        self.assertEqual(_archetype(scores), "The Architect")

    def test_all_scores_close_gives_generalist(self):
        scores = {"steering": 60, "execution": 62, "engineering": 58, "planning": 61}
        self.assertEqual(_archetype(scores), "The Generalist")

    def test_unmapped_top_pair_falls_back_to_generalist(self):
        # top-2 here is {steering, planning}, which has no entry in
        # ARCHETYPES — confirms the fallback is deterministic, not a crash.
        scores = {"steering": 90, "planning": 88, "engineering": 25, "execution": 20}
        self.assertEqual(_archetype(scores), "The Generalist")


if __name__ == "__main__":
    unittest.main()
