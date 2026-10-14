"""Static contract checks for the optional work-first learning Skill.

These checks verify packaging and critical textual boundaries, not Claude behavior.
A real host/learner evaluation is still required.
"""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins" / "nnc" / "skills" / "work-first-learning" / "SKILL.md"
SCENARIOS = SKILL.parent / "references" / "scenarios.md"
PILOT = ROOT / "docs" / "oser-r2" / "WORK-FIRST-LEARNING-PILOT.md"
PLUGIN = ROOT / "plugins" / "nnc" / ".claude-plugin" / "plugin.json"


class WorkFirstLearningContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.scenarios = SCENARIOS.read_text(encoding="utf-8")
        cls.pilot = PILOT.read_text(encoding="utf-8")
        cls.plugin = PLUGIN.read_text(encoding="utf-8")

    def test_plugin_baseline_unchanged(self):
        self.assertIn('"version": "5.1.0-alpha.2"', self.plugin)
        self.assertNotIn("5.1.0-alpha.3", self.plugin)

    def test_skill_frontmatter_and_links(self):
        self.assertTrue(self.skill.startswith("---\n"))
        frontmatter = self.skill.split("---", 2)[1]
        self.assertIn("name: work-first-learning", frontmatter)
        self.assertIn("version: 0.1.0", frontmatter)
        self.assertIn("references/scenarios.md", self.skill)
        self.assertIn("WORK-FIRST-LEARNING-PILOT.md", self.skill)
        self.assertTrue(SCENARIOS.is_file())
        self.assertTrue(PILOT.is_file())

    def test_recent_work_and_progressive_discovery(self):
        for phrase in (
            "Hôm nay, hôm qua", "job title", "one", "safe",
            "Stop questioning", "today", "yesterday",
        ):
            self.assertIn(phrase.lower(), self.skill.lower())

    def test_kernel_mission_and_privacy_boundaries(self):
        for phrase in (
            "does not replace or modify", "/nnc:mission-formation",
            "/nnc:adaptive-delivery", "without", "production",
            "Experience Observer", "off by default",
        ):
            self.assertIn(phrase.lower(), self.skill.lower())

    def test_learning_observability_states(self):
        for state in (
            "GUIDED", "INDEPENDENT_NEW_INPUT", "REUSED_IN_WORK",
            "NO_OPPORTUNITY", "BLOCKED"
        ):
            self.assertIn(state, self.skill)
            self.assertIn(state, self.scenarios)

    def test_scenarios_and_host_not_claimed(self):
        for i in range(1, 8):
            self.assertIn("Case F{}".format(i), self.scenarios)
        self.assertIn("NOT_TESTED", self.scenarios)
        self.assertIn("INSTALL_NOT_VERIFIED", self.pilot)
        self.assertIn("not proof of learner independence", self.pilot)


if __name__ == "__main__":
    unittest.main()
