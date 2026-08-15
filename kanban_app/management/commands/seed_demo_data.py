import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from kanban_app.models import Boards, Comment, Task

# Must stay in sync with GUEST_LOGIN in kan_mind_frontend/shared/js/config.js
# — the frontend's "Guest Log in" button posts these exact credentials.
GUEST_EMAIL = "gast@user.de"
GUEST_PASSWORD = "sicherespassword123"

SEED_PASSWORD = "KanMindDemo25!"
DEMO_EMAIL_DOMAIN = "kanmind.dev"

# Fictional, deliberately international team used to populate the live demo
# with believable data. None of these are real people; they exist purely to
# showcase the app with a realistic, diverse cast of collaborators.
DEMO_USERS = [
    {"fullname": "Guest Account", "email": GUEST_EMAIL, "password": GUEST_PASSWORD},
    {"fullname": "Lena Vogt", "email": f"lena.vogt@{DEMO_EMAIL_DOMAIN}"},
    {"fullname": "Jonas Keller", "email": f"jonas.keller@{DEMO_EMAIL_DOMAIN}"},
    {"fullname": "Sophie Bauer", "email": f"sophie.bauer@{DEMO_EMAIL_DOMAIN}"},
    {"fullname": "Tom Richter", "email": f"tom.richter@{DEMO_EMAIL_DOMAIN}"},
    {"fullname": "Mia Hoffmann", "email": f"mia.hoffmann@{DEMO_EMAIL_DOMAIN}"},
    {"fullname": "Priya Sharma", "email": f"priya.sharma@{DEMO_EMAIL_DOMAIN}"},
    {"fullname": "Wei Chen", "email": f"wei.chen@{DEMO_EMAIL_DOMAIN}"},
    {"fullname": "Carlos Mendes", "email": f"carlos.mendes@{DEMO_EMAIL_DOMAIN}"},
    {"fullname": "Fatima Al-Sayed", "email": f"fatima.alsayed@{DEMO_EMAIL_DOMAIN}"},
    {"fullname": "Liam O'Connor", "email": f"liam.oconnor@{DEMO_EMAIL_DOMAIN}"},
    {"fullname": "Yuki Tanaka", "email": f"yuki.tanaka@{DEMO_EMAIL_DOMAIN}"},
    {"fullname": "Giulia Cabras", "email": f"giulia.cabras@{DEMO_EMAIL_DOMAIN}"},
    {"fullname": "Marco Pinna", "email": f"marco.pinna@{DEMO_EMAIL_DOMAIN}"},
    {"fullname": "Alessia Loi", "email": f"alessia.loi@{DEMO_EMAIL_DOMAIN}"},
    {"fullname": "Simone Deiana", "email": f"simone.deiana@{DEMO_EMAIL_DOMAIN}"},
    {"fullname": "Francesca Melis", "email": f"francesca.melis@{DEMO_EMAIL_DOMAIN}"},
]

ALL_DEMO_EMAILS = [entry["email"] for entry in DEMO_USERS]


def days(offset):
    return datetime.date.today() + datetime.timedelta(days=offset)


class Command(BaseCommand):
    help = (
        "Seeds believable demo data (users, boards, tasks, comments) for the "
        "KanMind portfolio demo, including the guest account the frontend's "
        "'Guest Log in' button authenticates as. Safe to re-run; existing "
        "demo records are matched by email and skipped instead of duplicated."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help=(
                "Delete previously seeded demo users (and their boards/tasks "
                "via cascade) before recreating them. Only touches the known "
                "seed emails, never real users."
            ),
        )

    def handle(self, *args, **options):
        if options["reset"]:
            deleted, _ = User.objects.filter(
                email__in=ALL_DEMO_EMAILS
            ).delete()
            self.stdout.write(self.style.WARNING(
                f"Removed {deleted} previously seeded demo record(s)."
            ))

        with transaction.atomic():
            users = self._create_users()
            self._create_boards(users)

        self.stdout.write(self.style.SUCCESS("Demo data ready."))
        self.stdout.write(f"Guest login (used by the frontend): {GUEST_EMAIL} / {GUEST_PASSWORD}")
        self.stdout.write(f"Other seeded accounts: any @{DEMO_EMAIL_DOMAIN} address / {SEED_PASSWORD}")

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
                user.set_password(entry.get("password", SEED_PASSWORD))
                user.save()
                self.stdout.write(f"Created user: {entry['fullname']} <{entry['email']}>")
            users[entry["fullname"]] = user
        return users

    def _create_boards(self, users):
        guest = users["Guest Account"]
        lena = users["Lena Vogt"]
        jonas = users["Jonas Keller"]
        sophie = users["Sophie Bauer"]
        tom = users["Tom Richter"]
        mia = users["Mia Hoffmann"]
        priya = users["Priya Sharma"]
        wei = users["Wei Chen"]
        carlos = users["Carlos Mendes"]
        fatima = users["Fatima Al-Sayed"]
        liam = users["Liam O'Connor"]
        yuki = users["Yuki Tanaka"]
        giulia = users["Giulia Cabras"]
        marco = users["Marco Pinna"]
        alessia = users["Alessia Loi"]
        simone = users["Simone Deiana"]
        francesca = users["Francesca Melis"]

        boards = [
            {
                "title": "Portfolio Website Relaunch",
                "owner": lena,
                "members": [lena, jonas, sophie, priya, guest],
                "tasks": [
                    dict(title="Redesign hero section", description="New headline, updated screenshots of the live KanMind app, clearer CTA.",
                         status="done", priority="medium", assignee=lena, reviewer=sophie, due_date=days(-21)),
                    dict(title="Write case study copy", description="Summarize the KanMind build: problem, stack, architecture decisions, deployment.",
                         status="done", priority="high", assignee=sophie, reviewer=lena, due_date=days(-14)),
                    dict(title="Add dark mode toggle", description="Persist preference in localStorage, respect prefers-color-scheme on first visit.",
                         status="in-progress", priority="medium", assignee=jonas, reviewer=lena, due_date=days(3)),
                    dict(title="Optimize Lighthouse score", description="Currently 78 on mobile performance; lazy-load images and defer non-critical JS.",
                         status="in-progress", priority="high", assignee=lena, reviewer=jonas, due_date=days(5)),
                    dict(title="Cross-browser QA pass", description="Check Safari and Firefox rendering for the project grid and contact form.",
                         status="review", priority="low", assignee=sophie, reviewer=jonas, due_date=days(8)),
                    dict(title="Set up uptime monitoring", description="Ping /api/health/ every 5 minutes and alert on failures.",
                         status="to-do", priority="low", assignee=jonas, reviewer=None, due_date=days(12)),
                    dict(title="Translate site to English", description="Full EN version alongside the existing DE copy for international recruiters.",
                         status="to-do", priority="medium", assignee=priya, reviewer=None, due_date=days(20)),
                    dict(title="Add testimonials section", description="Collect two or three short quotes from people who tried the guest login.",
                         status="to-do", priority="medium", assignee=guest, reviewer=sophie, due_date=days(15)),
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
                    "Add testimonials section": [
                        (guest, "Reaching out to two people who tried the guest login this week."),
                    ],
                },
            },
            {
                "title": "KanMind Mobile App",
                "owner": jonas,
                "members": [jonas, tom, mia, wei, guest],
                "tasks": [
                    dict(title="Evaluate React Native vs. Flutter", description="Weigh team familiarity against long-term maintenance cost.",
                         status="done", priority="high", assignee=jonas, reviewer=tom, due_date=days(-25)),
                    dict(title="Design board list screen", description="Mobile-first layout for the board overview with member/task counters.",
                         status="done", priority="medium", assignee=mia, reviewer=jonas, due_date=days(-15)),
                    dict(title="Implement token auth flow", description="Store DRF auth token securely, add auto-logout on 401 responses.",
                         status="in-progress", priority="high", assignee=tom, reviewer=jonas, due_date=days(2)),
                    dict(title="Build task detail view", description="Show assignee, reviewer, due date, and comment thread; support pull-to-refresh.",
                         status="in-progress", priority="medium", assignee=mia, reviewer=tom, due_date=days(6)),
                    dict(title="Push notifications for comments", description="Notify assignee and reviewer when a new comment is posted on their task.",
                         status="to-do", priority="medium", assignee=wei, reviewer=None, due_date=days(15)),
                    dict(title="Offline draft support", description="Queue comment submissions locally when the device has no connection.",
                         status="to-do", priority="low", assignee=tom, reviewer=None, due_date=days(25)),
                    dict(title="Beta test with guest account", description="Walk through board creation, task assignment, and commenting end-to-end on iOS and Android.",
                         status="review", priority="medium", assignee=guest, reviewer=wei, due_date=days(4)),
                ],
                "comments": {
                    "Implement token auth flow": [
                        (jonas, "Remember to clear the token from storage on logout, not just state."),
                        (tom, "Good call, added that in the last commit."),
                    ],
                    "Build task detail view": [
                        (mia, "Pull-to-refresh is in, still need a loading skeleton."),
                    ],
                    "Beta test with guest account": [
                        (guest, "Logged in on both platforms, navigation feels smooth. Filed two minor bugs separately."),
                        (wei, "Thanks for the thorough pass, looking into the bugs now."),
                    ],
                },
            },
            {
                "title": "Client Onboarding Redesign",
                "owner": sophie,
                "members": [sophie, lena, tom, mia, fatima, guest],
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
                         status="to-do", priority="low", assignee=fatima, reviewer=guest, due_date=days(22)),
                    dict(title="Collect feedback from guest users", description="Short survey sent to everyone who explored the guest login in the last month.",
                         status="to-do", priority="high", assignee=guest, reviewer=fatima, due_date=days(10)),
                ],
                "comments": {
                    "Add sample board on first login": [
                        (sophie, "Let's reuse the 'Portfolio Website Relaunch' structure as the template."),
                        (lena, "Agreed, it already covers all four statuses nicely."),
                    ],
                    "Draft welcome email sequence": [
                        (sophie, "Second draft reads much better, ship it after one more pass."),
                    ],
                    "Collect feedback from guest users": [
                        (guest, "Started a short survey, first three responses already in."),
                        (fatima, "Great, share the summary in standup."),
                    ],
                },
            },
            {
                "title": "API v2 Migration",
                "owner": jonas,
                "members": [jonas, wei, carlos, guest],
                "tasks": [
                    dict(title="Audit v1 endpoint usage", description="Check server logs to see which v1 routes still get real traffic before deprecating anything.",
                         status="done", priority="medium", assignee=carlos, reviewer=jonas, due_date=days(-10)),
                    dict(title="Design versioned URL scheme", description="Decide between /api/v2/ prefixing and Accept-header versioning.",
                         status="done", priority="high", assignee=jonas, reviewer=wei, due_date=days(-5)),
                    dict(title="Add pagination to board list", description="Cursor-based pagination for accounts with a large number of boards.",
                         status="in-progress", priority="medium", assignee=wei, reviewer=carlos, due_date=days(4)),
                    dict(title="Write migration guide for frontend team", description="Document breaking changes and provide before/after request examples.",
                         status="in-progress", priority="low", assignee=carlos, reviewer=jonas, due_date=days(9)),
                    dict(title="Deprecate legacy comment endpoint", description="Add a Sunset header and log a warning for any client still hitting /api/comments/.",
                         status="review", priority="high", assignee=jonas, reviewer=carlos, due_date=days(6)),
                    dict(title="Load test new endpoints", description="Simulate 200 concurrent users against the new board and task endpoints.",
                         status="to-do", priority="high", assignee=wei, reviewer=None, due_date=days(14)),
                    dict(title="Review v2 docs with guest account", description="Walk through the OpenAPI docs as a first-time integrator would.",
                         status="to-do", priority="low", assignee=guest, reviewer=jonas, due_date=days(16)),
                ],
                "comments": {
                    "Design versioned URL scheme": [
                        (wei, "Prefixing is simpler for clients to reason about, +1 from me."),
                        (jonas, "Agreed, going with /api/v2/ then."),
                    ],
                    "Deprecate legacy comment endpoint": [
                        (carlos, "One internal script still calls the old route, pinging its owner."),
                    ],
                    "Review v2 docs with guest account": [
                        (guest, "Docs read clearly, one small typo in the auth example I'll flag separately."),
                    ],
                },
            },
            {
                "title": "Marketing Launch Campaign",
                "owner": sophie,
                "members": [sophie, priya, liam, yuki, guest],
                "tasks": [
                    dict(title="Finalize launch announcement post", description="Blog post covering the KanMind story, tech stack, and live demo link.",
                         status="done", priority="medium", assignee=priya, reviewer=sophie, due_date=days(-8)),
                    dict(title="Design social media graphics", description="Set of graphics for LinkedIn and Twitter announcing the launch.",
                         status="done", priority="low", assignee=yuki, reviewer=priya, due_date=days(-6)),
                    dict(title="Schedule newsletter send", description="Coordinate send time with the blog post going live.",
                         status="in-progress", priority="medium", assignee=liam, reviewer=sophie, due_date=days(3)),
                    dict(title="Reach out to tech blogs for coverage", description="Short pitch email highlighting the production deployment story.",
                         status="in-progress", priority="high", assignee=sophie, reviewer=priya, due_date=days(7)),
                    dict(title="Prepare Product Hunt listing", description="Tagline, gallery images, and first-comment draft.",
                         status="review", priority="high", assignee=priya, reviewer=liam, due_date=days(5)),
                    dict(title="Track launch day metrics dashboard", description="Signups, guest logins, and API error rate in one view.",
                         status="to-do", priority="medium", assignee=yuki, reviewer=None, due_date=days(13)),
                    dict(title="Gather guest user testimonial", description="Ask someone who explored the guest login for a short quote to use on launch day.",
                         status="to-do", priority="medium", assignee=guest, reviewer=priya, due_date=days(11)),
                ],
                "comments": {
                    "Prepare Product Hunt listing": [
                        (priya, "Gallery images are in, still need the first-comment draft."),
                        (liam, "I'll take a pass at the first comment tonight."),
                    ],
                    "Reach out to tech blogs for coverage": [
                        (sophie, "Two replies so far, one wants a follow-up call."),
                    ],
                    "Gather guest user testimonial": [
                        (guest, "Happy to write a short quote about the onboarding experience!"),
                        (priya, "Perfect, that's exactly the angle we need."),
                    ],
                },
            },
            {
                "title": "Getting Started with KanMind",
                "owner": guest,
                "members": [guest, lena],
                "tasks": [
                    dict(title="Create your first board", description="Boards group related tasks, e.g. by project or team.",
                         status="done", priority="low", assignee=guest, reviewer=None, due_date=days(-3)),
                    dict(title="Invite a teammate", description="Add another user as a board member so they can see and edit tasks.",
                         status="done", priority="low", assignee=guest, reviewer=None, due_date=days(-2)),
                    dict(title="Try assigning a task to yourself", description="Assignees and reviewers are separate roles on every task.",
                         status="in-progress", priority="medium", assignee=guest, reviewer=lena, due_date=days(2)),
                    dict(title="Leave a comment on a task", description="Comments are visible to everyone on the board.",
                         status="to-do", priority="low", assignee=guest, reviewer=None, due_date=days(5)),
                    dict(title="Explore board filters and priorities", description="Try filtering by status and priority to see how the counts update.",
                         status="to-do", priority="medium", assignee=guest, reviewer=None, due_date=days(9)),
                ],
                "comments": {
                    "Create your first board": [
                        (guest, "This is how easy it is to spin up a new board in KanMind."),
                        (lena, "Nice, welcome aboard!"),
                    ],
                    "Try assigning a task to yourself": [
                        (lena, "Looks good, let me know if you have questions about the review flow."),
                    ],
                },
            },
            {
                "title": "Sardinia Studio Launch",
                "owner": giulia,
                "members": [giulia, marco, alessia, simone, francesca, guest],
                "tasks": [
                    dict(title="Scout coworking space in Cagliari", description="Compare three shortlisted spaces near the harbor, capacity for 6 desks.",
                         status="done", priority="medium", assignee=marco, reviewer=giulia, due_date=days(-12)),
                    dict(title="Set up local VPN access", description="Provision accounts so the Cagliari team can reach internal tools securely.",
                         status="done", priority="low", assignee=simone, reviewer=marco, due_date=days(-9)),
                    dict(title="Translate onboarding docs to Italian", description="Localize the internal wiki's getting-started guide.",
                         status="in-progress", priority="medium", assignee=francesca, reviewer=alessia, due_date=days(4)),
                    dict(title="Plan welcome week agenda", description="Mix of tool walkthroughs and team intros for the first week on site.",
                         status="in-progress", priority="low", assignee=alessia, reviewer=giulia, due_date=days(6)),
                    dict(title="Order office equipment", description="Desks, chairs, and monitors for the new space.",
                         status="review", priority="medium", assignee=giulia, reviewer=simone, due_date=days(3)),
                    dict(title="Coordinate timezone overlap with HQ", description="Find a 2-hour daily window that works for both Cagliari and the German team.",
                         status="to-do", priority="high", assignee=marco, reviewer=None, due_date=days(10)),
                    dict(title="Walk guest account through the new board", description="Sanity-check that the board reads well for someone outside the Sardinia team.",
                         status="to-do", priority="low", assignee=guest, reviewer=francesca, due_date=days(8)),
                ],
                "comments": {
                    "Scout coworking space in Cagliari": [
                        (giulia, "Found a nice spot near the harbor, sending photos in the team chat."),
                        (marco, "Signed the short-term lease today."),
                    ],
                    "Order office equipment": [
                        (simone, "Desks arrive Thursday, chairs are backordered a week."),
                    ],
                    "Walk guest account through the new board": [
                        (guest, "Just explored this board end-to-end, everything's easy to follow!"),
                        (francesca, "Great, thanks for testing it out."),
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
