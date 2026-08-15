import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from kanban_app.models import Boards, Comment, Task

DEMO_EMAIL_DOMAIN = "kanmind.dev"
DEMO_PASSWORD = "KanMindDemo25!"

# Fictional small studio team used to populate the live demo with believable
# data. None of these are real people; they exist purely to showcase the app.
DEMO_USERS = [
    {"fullname": "Demo Account", "email": f"demo@{DEMO_EMAIL_DOMAIN}"},
    {"fullname": "Lena Vogt", "email": f"lena.vogt@{DEMO_EMAIL_DOMAIN}"},
    {"fullname": "Jonas Keller", "email": f"jonas.keller@{DEMO_EMAIL_DOMAIN}"},
    {"fullname": "Sophie Bauer", "email": f"sophie.bauer@{DEMO_EMAIL_DOMAIN}"},
    {"fullname": "Tom Richter", "email": f"tom.richter@{DEMO_EMAIL_DOMAIN}"},
    {"fullname": "Mia Hoffmann", "email": f"mia.hoffmann@{DEMO_EMAIL_DOMAIN}"},
]


def days(offset):
    return datetime.date.today() + datetime.timedelta(days=offset)


class Command(BaseCommand):
    help = (
        "Seeds believable demo data (users, boards, tasks, comments) for the "
        "KanMind portfolio demo. Safe to re-run; existing demo records are "
        "matched by name/email and skipped instead of duplicated."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help=(
                "Delete previously seeded demo users (and their boards/tasks "
                "via cascade) before recreating them. Only touches accounts "
                f"with an @{DEMO_EMAIL_DOMAIN} email, never real users."
            ),
        )

    def handle(self, *args, **options):
        if options["reset"]:
            deleted, _ = User.objects.filter(
                email__iendswith=f"@{DEMO_EMAIL_DOMAIN}"
            ).delete()
            self.stdout.write(self.style.WARNING(
                f"Removed {deleted} previously seeded demo record(s)."
            ))

        with transaction.atomic():
            users = self._create_users()
            self._create_boards(users)

        self.stdout.write(self.style.SUCCESS("Demo data ready."))
        self.stdout.write(
            "Log in with any @{}. address, password: {}".format(
                DEMO_EMAIL_DOMAIN, DEMO_PASSWORD
            )
        )
        self.stdout.write(f"Suggested login: demo@{DEMO_EMAIL_DOMAIN} / {DEMO_PASSWORD}")

    def _create_users(self):
        users = {}
        for entry in DEMO_USERS:
            user, created = User.objects.get_or_create(
                email=entry["email"],
                defaults={"username": entry["fullname"]},
            )
            if created:
                first, *rest = entry["fullname"].split(" ")
                user.first_name = first
                user.last_name = " ".join(rest)
                user.set_password(DEMO_PASSWORD)
                user.save()
                self.stdout.write(f"Created user: {entry['fullname']} <{entry['email']}>")
            users[entry["fullname"]] = user
        return users

    def _create_boards(self, users):
        demo = users["Demo Account"]
        lena, jonas, sophie, tom, mia = (
            users["Lena Vogt"],
            users["Jonas Keller"],
            users["Sophie Bauer"],
            users["Tom Richter"],
            users["Mia Hoffmann"],
        )

        boards = [
            {
                "title": "Portfolio Website Relaunch",
                "owner": lena,
                "members": [lena, jonas, sophie, demo],
                "tasks": [
                    dict(title="Redesign hero section", description="New headline, updated screenshots of the live KanMind app, clearer CTA.",
                         status="done", priority="medium", assignee=lena, reviewer=sophie, due_date=days(-14)),
                    dict(title="Write case study copy", description="Summarize the KanMind build: problem, stack, architecture decisions, deployment.",
                         status="done", priority="high", assignee=sophie, reviewer=lena, due_date=days(-7)),
                    dict(title="Add dark mode toggle", description="Persist preference in localStorage, respect prefers-color-scheme on first visit.",
                         status="in-progress", priority="medium", assignee=jonas, reviewer=lena, due_date=days(3)),
                    dict(title="Optimize Lighthouse score", description="Currently 78 on mobile performance; lazy-load images and defer non-critical JS.",
                         status="in-progress", priority="high", assignee=lena, reviewer=jonas, due_date=days(5)),
                    dict(title="Cross-browser QA pass", description="Check Safari and Firefox rendering for the project grid and contact form.",
                         status="review", priority="low", assignee=sophie, reviewer=jonas, due_date=days(8)),
                    dict(title="Set up uptime monitoring", description="Ping /api/health/ every 5 minutes and alert on failures.",
                         status="to-do", priority="low", assignee=jonas, reviewer=None, due_date=days(12)),
                    dict(title="Translate site to English", description="Full EN version alongside the existing DE copy for international recruiters.",
                         status="to-do", priority="medium", assignee=None, reviewer=None, due_date=days(20)),
                ],
                "comments": {
                    "Redesign hero section": [
                        (sophie, "Screenshots look great, love the contrast in dark mode preview."),
                        (lena, "Thanks! Swapped the CTA color to match the brand palette."),
                    ],
                    "Optimize Lighthouse score": [
                        (jonas, "Biggest win so far was compressing the hero image, +14 points."),
                    ],
                    "Cross-browser QA pass": [
                        (jonas, "Found a flex-gap issue in Safari 16, ticket incoming."),
                    ],
                },
            },
            {
                "title": "KanMind Mobile App",
                "owner": jonas,
                "members": [jonas, tom, mia, demo],
                "tasks": [
                    dict(title="Evaluate React Native vs. Flutter", description="Weigh team familiarity against long-term maintenance cost.",
                         status="done", priority="high", assignee=jonas, reviewer=tom, due_date=days(-20)),
                    dict(title="Design board list screen", description="Mobile-first layout for the board overview with member/task counters.",
                         status="done", priority="medium", assignee=mia, reviewer=jonas, due_date=days(-10)),
                    dict(title="Implement token auth flow", description="Store DRF auth token securely, add auto-logout on 401 responses.",
                         status="in-progress", priority="high", assignee=tom, reviewer=jonas, due_date=days(2)),
                    dict(title="Build task detail view", description="Show assignee, reviewer, due date, and comment thread; support pull-to-refresh.",
                         status="in-progress", priority="medium", assignee=mia, reviewer=tom, due_date=days(6)),
                    dict(title="Push notifications for comments", description="Notify assignee and reviewer when a new comment is posted on their task.",
                         status="to-do", priority="medium", assignee=None, reviewer=None, due_date=days(15)),
                    dict(title="Offline draft support", description="Queue comment submissions locally when the device has no connection.",
                         status="to-do", priority="low", assignee=tom, reviewer=None, due_date=days(25)),
                ],
                "comments": {
                    "Implement token auth flow": [
                        (jonas, "Remember to clear the token from storage on logout, not just state."),
                        (tom, "Good call, added that in the last commit."),
                    ],
                    "Build task detail view": [
                        (mia, "Pull-to-refresh is in, still need a loading skeleton."),
                    ],
                },
            },
            {
                "title": "Client Onboarding Redesign",
                "owner": sophie,
                "members": [sophie, lena, tom, mia, demo],
                "tasks": [
                    dict(title="Map current onboarding steps", description="Document the existing flow from signup to first board created.",
                         status="done", priority="low", assignee=sophie, reviewer=mia, due_date=days(-18)),
                    dict(title="Draft welcome email sequence", description="Three emails: welcome, first-board nudge, feature highlight after 7 days.",
                         status="review", priority="medium", assignee=mia, reviewer=sophie, due_date=days(4)),
                    dict(title="Add sample board on first login", description="Pre-populate a starter board so new users see the UI in action immediately.",
                         status="in-progress", priority="high", assignee=lena, reviewer=sophie, due_date=days(1)),
                    dict(title="A/B test signup form length", description="Compare single-step vs. two-step signup on completion rate.",
                         status="to-do", priority="medium", assignee=tom, reviewer=None, due_date=days(18)),
                    dict(title="Update empty states", description="Friendlier copy and illustration when a board has no tasks yet.",
                         status="to-do", priority="low", assignee=None, reviewer=None, due_date=days(22)),
                ],
                "comments": {
                    "Add sample board on first login": [
                        (sophie, "Let's reuse the 'Portfolio Website Relaunch' structure as the template."),
                        (lena, "Agreed, it already covers all four statuses nicely."),
                    ],
                    "Draft welcome email sequence": [
                        (sophie, "Second draft reads much better, ship it after one more pass."),
                    ],
                },
            },
        ]

        for board_data in boards:
            board, created = Boards.objects.get_or_create(
                title=board_data["title"],
                defaults={"owner": board_data["owner"]},
            )
            board.members.set(board_data["members"])
            if created:
                self.stdout.write(f"Created board: {board_data['title']}")

            for task_data in board_data["tasks"]:
                task, task_created = Task.objects.get_or_create(
                    board=board,
                    title=task_data["title"],
                    defaults={
                        "description": task_data["description"],
                        "status": task_data["status"],
                        "priority": task_data["priority"],
                        "assignee": task_data["assignee"],
                        "reviewer": task_data["reviewer"],
                        "due_date": task_data["due_date"],
                        "creator": board_data["owner"],
                    },
                )
                if task_created:
                    for author, content in board_data["comments"].get(task_data["title"], []):
                        Comment.objects.get_or_create(
                            task=task, author=author, content=content
                        )
