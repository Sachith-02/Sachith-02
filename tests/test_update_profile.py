import importlib.util
from pathlib import Path
import sys
import unittest

SCRIPT_PATH = Path(__file__).resolve().parents[1] / ".github" / "scripts" / "update_profile.py"
spec = importlib.util.spec_from_file_location("update_profile", SCRIPT_PATH)
update_profile = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = update_profile
spec.loader.exec_module(update_profile)


class ProfileAutomationTests(unittest.TestCase):
    def sample_repo(self, **overrides):
        repo = {
            "name": "LibraCore",
            "description": "Spring Boot backend API with JWT security and Docker deployment",
            "stargazers_count": 3,
            "forks_count": 1,
            "topics": ["java", "spring-boot", "jwt", "docker"],
            "fork": False,
            "archived": False,
            "language": "Java",
            "updated_at": "2026-05-01T00:00:00Z",
            "html_url": "https://github.com/Sachith-02/LibraCore",
        }
        repo.update(overrides)
        return repo

    def test_escape_md_removes_table_breakers(self):
        self.assertEqual(update_profile.escape_md("API | Backend\nProject"), "API \\| Backend Project")

    def test_truncate_shortens_long_text(self):
        text = "x" * 200
        result = update_profile.truncate(text, limit=20)
        self.assertEqual(len(result), 20)
        self.assertTrue(result.endswith("…"))

    def test_progress_bar_clamps_percentages(self):
        self.assertEqual(update_profile.progress_bar(-10, width=5), "░░░░░")
        self.assertEqual(update_profile.progress_bar(150, width=5), "█████")

    def test_score_repo_rewards_original_documented_active_backend_project(self):
        score = update_profile.score_repo(self.sample_repo())
        self.assertEqual(score.name, "LibraCore")
        self.assertGreater(score.score, 50)
        self.assertIn("original", score.reasons)
        self.assertIn("documented", score.reasons)

    def test_filter_repos_excludes_archived_forks_and_configured_names(self):
        repos = [
            self.sample_repo(name="keep"),
            self.sample_repo(name="profile", fork=False),
            self.sample_repo(name="forked", fork=True),
            self.sample_repo(name="old", archived=True),
        ]
        config = {"exclude_repositories": ["profile"], "include_forks": False}
        result = update_profile.filter_repos(repos, config)
        self.assertEqual([repo["name"] for repo in result], ["keep"])

    def test_replace_block_updates_existing_marker(self):
        content = "A\n<!-- TEST_START -->old<!-- TEST_END -->\nB"
        result = update_profile.replace_block(content, "TEST", "<!-- TEST_START -->new<!-- TEST_END -->")
        self.assertIn("new", result)
        self.assertNotIn("old", result)

    def test_repo_card_includes_topics_release_badge_and_score(self):
        repo = self.sample_repo()
        score = update_profile.score_repo(repo)
        card = update_profile.repo_card(repo, "Sachith-02", score)
        self.assertIn("LibraCore", card)
        self.assertIn("github/v/release/Sachith-02/LibraCore", card)
        self.assertIn("<code>spring-boot</code>", card)
        self.assertIn("Portfolio score", card)

    def test_repo_card_guides_user_when_topics_are_missing(self):
        repo = self.sample_repo(topics=[])
        card = update_profile.repo_card(repo, "Sachith-02")
        self.assertIn("Add GitHub topics", card)
        self.assertIn("docs/REPOSITORY_TOPICS.md", card)

    def test_project_status_section_uses_configured_ci_badges(self):
        config = {
            "username": "Sachith-02",
            "project_ci_badges": [
                {"repository": "LibraCore", "workflow": "ci.yml", "label": "LibraCore CI"}
            ],
        }
        section = update_profile.build_project_status_section(config)
        self.assertIn("PROJECT_STATUS_START", section)
        self.assertIn("actions/workflows/ci.yml/badge.svg", section)
        self.assertIn("github/v/release/Sachith-02/LibraCore", section)

    def test_build_table_keeps_two_column_layout_with_odd_number_of_cards(self):
        table = update_profile.build_table(["<td>A</td>", "<td>B</td>", "<td>C</td>"])
        self.assertIn('<td width="50%"></td>', table)
        self.assertEqual(table.count("<tr>"), 2)

    def test_describe_release_event(self):
        event = {
            "type": "ReleaseEvent",
            "repo": {"name": "Sachith-02/LibraCore"},
            "created_at": "2026-05-01T00:00:00Z",
            "payload": {"action": "published"},
        }
        self.assertIn("release", update_profile.describe_event(event).lower())

    def test_compact_number_formats_large_values(self):
        self.assertEqual(update_profile.compact_number(999), "999")
        self.assertEqual(update_profile.compact_number(1500), "1.5k")

    def test_auto_about_section_uses_live_account_repository_and_activity_data(self):
        profile = {
            "name": "Sachith Asmadala",
            "bio": "Backend learner",
            "location": "Sri Lanka",
            "public_repos": 12,
            "followers": 7,
            "following": 3,
        }
        repos = [
            self.sample_repo(name="LibraCore", updated_at="2026-05-01T00:00:00Z"),
            self.sample_repo(name="Knowledge-Studio", description="RAG knowledge base", language="Python", updated_at="2026-05-05T00:00:00Z"),
        ]
        config = {
            "username": "Sachith-02",
            "headline": "Backend Engineer",
            "current_focus": ["Java backend APIs", "CI automation"],
        }
        events = [{
            "type": "PushEvent",
            "repo": {"name": "Sachith-02/LibraCore"},
            "created_at": "2026-05-06T00:00:00Z",
            "payload": {"commits": [{}]},
        }]
        scores = {repo["name"]: update_profile.score_repo(repo) for repo in repos}
        section = update_profile.build_auto_about_section(
            profile, repos, {"Java": 100, "Python": 50}, events, config, scores
        )
        self.assertIn("ABOUT_ME_START", section)
        self.assertIn("12 public repositories", section)
        self.assertIn("7 followers", section)
        self.assertIn("Java, Python", section)
        self.assertIn("Latest public activity", section)
        self.assertIn("Last generated", section)

    def test_activity_section_limits_items_and_links_prs(self):
        events = [
            {
                "type": "PullRequestEvent",
                "repo": {"name": "Sachith-02/LibraCore"},
                "created_at": "2026-05-06T00:00:00Z",
                "payload": {
                    "action": "opened",
                    "number": 7,
                    "pull_request": {
                        "title": "Add profile automation",
                        "html_url": "https://github.com/Sachith-02/LibraCore/pull/7",
                    },
                },
            },
            {
                "type": "WatchEvent",
                "repo": {"name": "Sachith-02/Knowledge-Studio"},
                "created_at": "2026-05-07T00:00:00Z",
                "payload": {},
            },
        ]
        section = update_profile.build_activity_section(events, max_items=1)
        self.assertIn("ACTIVITY_START", section)
        self.assertIn("pull/7", section)
        self.assertIn("Opened PR #7", section)
        self.assertNotIn("Knowledge-Studio", section)



if __name__ == "__main__":
    unittest.main()
