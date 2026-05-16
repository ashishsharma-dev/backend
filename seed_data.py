"""Seed data for the blog: 10 high-quality posts per category (60 total)."""
from datetime import datetime, timezone, timedelta
import uuid

# Image bank (Unsplash public hot-link friendly URLs by category)
IMAGES = {
    "travel": [
        "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=1600&q=80",
        "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=1600&q=80",
        "https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=1600&q=80",
        "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=1600&q=80",
        "https://images.unsplash.com/photo-1504609813442-a8924e83f76e?w=1600&q=80",
        "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=1600&q=80",
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1600&q=80",
        "https://images.unsplash.com/photo-1528127269322-539801943592?w=1600&q=80",
        "https://images.unsplash.com/photo-1503220317375-aaad61436b1b?w=1600&q=80",
        "https://images.unsplash.com/photo-1530789253388-582c481c54b0?w=1600&q=80",
    ],
    "tech": [
        "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1600&q=80",
        "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=1600&q=80",
        "https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=1600&q=80",
        "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=1600&q=80",
        "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1600&q=80",
        "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=1600&q=80",
        "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?w=1600&q=80",
        "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=1600&q=80",
        "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=1600&q=80",
        "https://images.unsplash.com/photo-1526498460520-4c246339dccb?w=1600&q=80",
    ],
    "finance": [
        "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1600&q=80",
        "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1600&q=80",
        "https://images.unsplash.com/photo-1579621970795-87facc2f976d?w=1600&q=80",
        "https://images.unsplash.com/photo-1565514020179-026b92b2d70b?w=1600&q=80",
        "https://images.unsplash.com/photo-1604594849809-dfedbc827105?w=1600&q=80",
        "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=1600&q=80",
        "https://images.unsplash.com/photo-1591696205602-2f950c417cb9?w=1600&q=80",
        "https://images.unsplash.com/photo-1638913662180-afc4334cf422?w=1600&q=80",
        "https://images.unsplash.com/photo-1633158829585-23ba8f7c8caf?w=1600&q=80",
        "https://images.unsplash.com/photo-1580519542036-c47de6196ba5?w=1600&q=80",
    ],
    "products": [
        "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=1600&q=80",
        "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=1600&q=80",
        "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=1600&q=80",
        "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=1600&q=80",
        "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=1600&q=80",
        "https://images.unsplash.com/photo-1560343090-f0409e92791a?w=1600&q=80",
        "https://images.unsplash.com/photo-1585386959984-a4155224a1ad?w=1600&q=80",
        "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=1600&q=80",
        "https://images.unsplash.com/photo-1585155770447-2f66e2a397b5?w=1600&q=80",
        "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=1600&q=80",
    ],
    "sports": [
        "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1600&q=80",
        "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=1600&q=80",
        "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=1600&q=80",
        "https://images.unsplash.com/photo-1552667466-07770ae110d0?w=1600&q=80",
        "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=1600&q=80",
        "https://images.unsplash.com/photo-1518604666860-9ed391f76460?w=1600&q=80",
        "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=1600&q=80",
        "https://images.unsplash.com/photo-1530549387789-4c1017266635?w=1600&q=80",
        "https://images.unsplash.com/photo-1546519638-68e109498ffc?w=1600&q=80",
        "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=1600&q=80",
    ],
    "trading": [
        "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1600&q=80",
        "https://images.unsplash.com/photo-1642790106117-e829e14a795f?w=1600&q=80",
        "https://images.unsplash.com/photo-1640340434855-6084b1f4901c?w=1600&q=80",
        "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=1600&q=80",
        "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1600&q=80",
        "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=1600&q=80",
        "https://images.unsplash.com/photo-1612010167108-3e6b327405f0?w=1600&q=80",
        "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=1600&q=80",
        "https://images.unsplash.com/photo-1620266757065-5814239881fd?w=1600&q=80",
        "https://images.unsplash.com/photo-1535320903710-d993d3d77d29?w=1600&q=80",
    ],
}

POSTS_BY_CATEGORY = {
    "travel": [
        ("10 Hidden Gems Across the American Southwest You Need to Visit", "From slot canyons in Arizona to sleepy desert towns in New Mexico, the American Southwest is filled with breathtaking destinations far from the usual tourist trail. We mapped a slow-paced route designed for deep exploration, peaceful nights under starlit skies, and the kind of stories that make great campfire conversation.", "Travis Worthington"),
        ("The Slow Travel Movement: Why Americans Are Ditching Itineraries", "A quiet revolution is reshaping how Americans experience the world. Slow travel isn't about ticking boxes—it's about staying long enough to understand a place. We spoke with full-time travelers who explain why fewer destinations and longer stays lead to richer memories.", "Maya Chen"),
        ("A Coastal Road Trip Through California's Highway 1, Reimagined", "Highway 1 has been written about countless times, yet most guides skip the off-ramp magic. We share the lavender farms, abalone bars, and tide-pool walks that make this iconic drive feel new—even if you've done it before.", "Travis Worthington"),
        ("Glamping in the Smoky Mountains: A Complete Guide", "Glamping has matured. The new generation of canvas tents and geodesic domes brings hotel-grade comfort to wild forests. We tested 14 properties in Tennessee and North Carolina to identify the most peaceful retreats with the best mountain views.", "Eleanor Park"),
        ("National Park Permits Explained: How to Secure the Best Trails", "From The Wave to Half Dome, America's most beautiful trails are increasingly behind digital lottery walls. Here's a clear breakdown of how the permit system works—and the timing tricks that dramatically improve your odds.", "Maya Chen"),
        ("Why Florida's Forgotten Coast Beats Miami For a Calm Getaway", "Sandwiched between Panama City and Apalachicola, Florida's Forgotten Coast feels like a state in slow motion. White-sand beaches, oyster farms, and family-run inns create a vacation experience that feels healing rather than rushed.", "Travis Worthington"),
        ("Train Travel Across America Is Quietly Coming Back", "Amtrak's long-distance routes used to feel nostalgic. Now, with new sleeper cars and remote-work policies, they're becoming a serious alternative for thoughtful travelers. We spent ten days on the Coast Starlight to find out why.", "Eleanor Park"),
        ("Lake District USA: 7 Lakes That Deserve a Weeklong Stay", "From Lake Tahoe to Lake Champlain, America has a rich freshwater story most travelers overlook. Each of these seven destinations offers boating, hiking, and sunset moments that linger in memory long after the trip ends.", "Maya Chen"),
        ("Pet-Friendly Travel: How We Mapped the Best US Dog-Welcoming Inns", "Traveling with dogs used to mean compromises. Today, more inns and Airbnbs are designed dog-first. Here's our curated list of properties where pets are guests, not afterthoughts.", "Travis Worthington"),
        ("The Quiet Magic of New England in Late Autumn", "Long after the leaf-peepers return home, New England enters a hushed second season. Empty trails, cheaper lodging, and the smell of woodsmoke create a meditative travel experience few outsiders see.", "Eleanor Park"),
    ],
    "tech": [
        ("AI Tools Worth Paying For (And the Ones to Skip)", "After testing 47 AI tools across writing, design, and productivity, we narrowed down a shortlist of paid platforms that genuinely earn their subscription fee. We also call out the ones that look impressive in demos but fall apart in daily use.", "Devon Hayes"),
        ("The Quiet Death of Subscription Software (And What's Replacing It)", "Lifetime licenses are quietly returning, and a wave of indie developers are betting users want ownership again. We explore the macro trend reshaping the SaaS landscape and what it means for your monthly software bills.", "Priya Anand"),
        ("How to Set Up a Distraction-Free Home Office in Under $400", "A peaceful workspace doesn't require a designer salary. We walk through a calming, minimal home-office setup—desk, chair, lighting, sound—that supports deep work and feels good to return to every morning.", "Devon Hayes"),
        ("Local-First Apps Are the Next Quiet Revolution", "Cloud-only software is showing its cracks. A new movement called local-first computing prioritizes ownership, offline access, and resilience. Here's why developers and thoughtful users are paying attention.", "Priya Anand"),
        ("Privacy-First Browsers Compared: Brave vs. Arc vs. Firefox", "If you're tired of feeling tracked, the modern browser landscape has more privacy-respecting options than ever. We compared the three most thoughtful browsers across speed, extensions, and real privacy posture.", "Devon Hayes"),
        ("M-Series Macs in 2026: Are They Still Worth The Premium?", "Apple Silicon has been the gold standard for years. With Snapdragon X laptops catching up, we examine whether the price premium for an M3 or M4 Mac still makes sense for creators, developers, and casual users.", "Priya Anand"),
        ("The Best Mechanical Keyboards For Calm, Focused Writing", "Loud clicky switches are out. Hushed, tactile, well-cushioned keyboards are in. We tested ten of the most thoughtful mechanical keyboards for writers who want a peaceful typing experience.", "Devon Hayes"),
        ("Why Local AI Models Will Beat Cloud AI For Most Tasks", "On-device AI is rapidly closing the gap with cloud models. We break down the hardware, the model weights, and the privacy story that makes local AI a serious alternative for everyday tasks.", "Priya Anand"),
        ("A Beginner's Guide to Self-Hosting Your Digital Life", "Self-hosting used to require a homelab and a degree in Linux. Today, single-board computers and friendly software like Umbrel and CasaOS make it simple. Here's how to start small and reclaim your data.", "Devon Hayes"),
        ("The Real Cost of Cheap Smart Home Gadgets", "Discount smart bulbs and budget cameras come with hidden costs—data leaks, vendor lock-in, broken cloud services. We explain what to look for when building a calm, reliable smart home.", "Priya Anand"),
    ],
    "finance": [
        ("The Modern Guide to High-Yield Savings: What's Actually Worth Your Money", "Interest rates have shifted dramatically. We compared the top high-yield savings accounts to identify which platforms deliver real returns, transparent fees, and frictionless withdrawals.", "Hannah Reyes"),
        ("Why Index Funds Still Win for Patient Investors", "Despite a decade of hype around active strategies, low-cost index funds continue to outperform most managed alternatives. Here's why they remain the cornerstone of a calm, sustainable investment plan.", "Marcus Boyle"),
        ("Building Your First $10,000 Emergency Fund Without Stress", "An emergency fund isn't built overnight, and the wrong approach can feel suffocating. We outline a calm, multi-month plan that gradually grows a cushion without sacrificing your quality of life.", "Hannah Reyes"),
        ("Understanding Roth vs. Traditional IRAs in Plain English", "The difference between Roth and Traditional accounts can change your retirement by tens of thousands of dollars. We break down both options without the jargon that usually clouds personal finance writing.", "Marcus Boyle"),
        ("The Real Reason Americans Feel Broke Despite Higher Salaries", "Wages have grown, yet financial anxiety remains stubbornly high. We unpack the macro and behavioral forces driving this disconnect and outline strategies that bring back a sense of financial calm.", "Hannah Reyes"),
        ("Credit Score Myths That Cost You Thousands", "From closing old cards to chasing a perfect score, several common credit habits actively hurt your financial life. We separate the durable truths from the internet folklore.", "Marcus Boyle"),
        ("How to Negotiate a Raise Without the Awkward Tension", "Pay negotiations don't have to feel adversarial. Drawing on conversations with HR leaders, we share scripts and frameworks designed to keep the conversation calm, professional, and productive.", "Hannah Reyes"),
        ("The Quiet Power of Automated Investing in Volatile Markets", "Dollar-cost averaging is unglamorous, predictable, and remarkably effective. We explain why automated investing remains the most stress-reducing path to wealth building for the average American household.", "Marcus Boyle"),
        ("A Simple Three-Bucket Budget That Survives Real Life", "Rigid budgets break the moment life happens. The three-bucket system—needs, wants, future—is forgiving, intuitive, and designed to last decades.", "Hannah Reyes"),
        ("Side Income Streams That Don't Require You to Become an Influencer", "Not every side hustle has to involve a camera. We cataloged 14 proven income streams from freelancing to renting out unused space, all of which respect your privacy and your time.", "Marcus Boyle"),
    ],
    "products": [
        ("The 12 Most Calming Home Products We've Tested", "From weighted blankets to ceramic lamps, certain products quietly elevate the feel of a home. We tested dozens to find the ones that deliver real serenity rather than aesthetic posturing.", "Sienna Carmichael"),
        ("Sleep Headphones Worth Buying (And the Comfortable Ones to Skip)", "Bluetooth headbands have become a sleep essential, but build quality varies wildly. We tested 18 models for comfort, sound, and battery to find the genuinely peaceful options.", "Aiden Kowalski"),
        ("The Standing Desk Buyer's Guide for Small Apartments", "Most standing desk reviews assume you have a corner office. We focused on quiet motors, slim footprints, and minimalist designs that fit thoughtfully into smaller homes.", "Sienna Carmichael"),
        ("Affordable Air Purifiers That Actually Work", "Indoor air quality is a quiet wellness frontier. We compared a dozen budget purifiers using a particle counter to identify the ones that genuinely clean the air without industrial noise levels.", "Aiden Kowalski"),
        ("Reusable Kitchen Products That Will Save You Hundreds", "From silicone bags to beeswax wraps, the reusable kitchen movement is finally producing products that work. We tested for durability, ease of cleaning, and real cost savings.", "Sienna Carmichael"),
        ("Mindful Lighting: A Calm Apartment Lighting Plan Under $300", "Harsh overhead lights damage mood more than most people realize. Our calm lighting plan layers warm bulbs, dimmable lamps, and sunset-spectrum LEDs across a small living space.", "Aiden Kowalski"),
        ("Why Linen Bedding Is the Quiet Upgrade Your Bedroom Deserves", "Cotton percale gets all the attention, but linen sleeps better in nearly every climate. We spent six months testing the best brands to find the most comfortable—and the most ethically sourced—options.", "Sienna Carmichael"),
        ("Best Espresso Machines for the Home Barista", "From entry-level to prosumer, the espresso world is more accessible than ever. We share our shortlist of machines that produce café-quality drinks without becoming a household chore.", "Aiden Kowalski"),
        ("The Calm Tech Movement: Gadgets Designed to Stay Out of Your Way", "Calm tech is the antidote to attention-seeking apps and beeping appliances. These thoughtful gadgets—from e-paper monitors to silent smoke alarms—prioritize peace over engagement.", "Sienna Carmichael"),
        ("A Minimalist Kitchen Starter Kit That Will Last a Decade", "Quality over quantity is the foundation of a calm kitchen. We built a 14-piece starter kit from time-tested brands that should last most cooks for many years to come.", "Aiden Kowalski"),
    ],
    "sports": [
        ("The Quiet Dynasty Builders: NFL Teams That Win Without the Noise", "Behind the headline-grabbing franchises, a small group of NFL front offices have quietly assembled rosters built to last a decade. We looked at their draft strategies, coaching pipelines, and the cultural habits that separate them from perpetual rebuilders.", "Grant Holloway"),
        ("The WNBA's Commercial Awakening: Inside the Growth No One Saw Coming", "Packed arenas, soaring TV ratings, sold-out merch — the WNBA's growth curve now rivals any men's league in North America. We break down the economics, the breakout stars, and what advertisers should be paying attention to.", "Jamie Calder"),
        ("Why Minor League Baseball Is America's Most Underrated Travel Experience", "From Asheville to Portland, minor league ballparks are some of the most affordable, family-friendly ways to spend a summer evening. We mapped 12 ballparks that double as reasons to visit their host cities.", "Grant Holloway"),
        ("MLS After Messi: Is American Soccer Finally Ready for the Spotlight?", "The Messi effect reshaped Major League Soccer overnight — but the real story is what comes after. We examine the infrastructure, academies, and TV deals that will decide whether American soccer sustains the boom.", "Jamie Calder"),
        ("College Football Realignment Has Broken the Sport (And That's Not Entirely Bad)", "The 2024 conference realignment wave ended decades-old rivalries and scrambled the College Football Playoff picture. We argue why the chaos might produce a better, more competitive sport — and which traditions were worth keeping.", "Grant Holloway"),
        ("PGA vs. LIV: How Pro Golf's Messy Peace Is Quietly Reshaping the Tour", "The PGA Tour and LIV Golf truce is more complicated than it looks. We unpack the money, the majors, and the younger players caught in the middle of the sport's biggest structural change in a generation.", "Jamie Calder"),
        ("Formula 1's American Moment: Three Grands Prix, One Big Opportunity", "With Miami, Austin, and Las Vegas on the calendar, Formula 1 has more presence in the United States than ever before. We look at the fans, sponsors, and broadcast choices that will decide whether the sport sticks.", "Grant Holloway"),
        ("The Quiet Pickleball Revolution: How a Backyard Game Became a Billion-Dollar Industry", "Pickleball is no longer a retirement-community joke. It's a fast-growing professional sport with Netflix deals, pro tours, and serious sponsorship money. Here's the state of the game — and why it keeps growing.", "Jamie Calder"),
        ("Load Management in the NBA: Smart Strategy or Slow Fan Betrayal?", "Resting stars during the regular season protects bodies but bleeds fan trust. We dig into the data, the league's response, and what a fairer middle ground might look like for players, teams, and ticket-buyers.", "Grant Holloway"),
        ("American Tennis Is Quietly Back: The New Wave You Should Know", "For the first time in years, American tennis has a deep roster of young talent on both tours. We profile the players worth following and explain why the USTA's development pipeline is finally paying off.", "Jamie Calder"),
    ],
    "trading": [
        ("The Beginner's Guide to Calm, Long-Term Trading", "Day trading rarely makes anyone wealthy. A patient, weekly-review trading rhythm is far more likely to produce stable returns. We outline a practical onboarding plan for someone starting out.", "Riley McKenna"),
        ("Why Most Retail Traders Lose Money (And How to Avoid Their Mistakes)", "Industry data consistently shows the majority of retail traders losing money. We break down the structural and behavioral reasons—and outline the small habits that separate the winners.", "Theo Branigan"),
        ("Reading the Macro Tape Without the Anxiety", "Macro investing doesn't have to mean glued screens and constant cortisol. We share a calmer process for tracking the global economy that respects your time and your nerves.", "Riley McKenna"),
        ("A Realistic Look at Options Trading For New Investors", "Options can be powerful tools or expensive lessons. We share an honest, non-hyped framework for understanding the risks and the rare cases where options genuinely add value to a portfolio.", "Theo Branigan"),
        ("The Three-Account System Most Successful Traders Use", "Splitting capital across long-term, swing, and speculative accounts is one of the simplest ways to manage risk. We share how leading traders structure their accounts to stay disciplined.", "Riley McKenna"),
        ("Crypto Today: Mature Assets, Calmer Strategies", "After several volatile cycles, crypto's most thoughtful investors have settled into calmer, longer-time-horizon strategies. We outline what those strategies look like and which assets are receiving real attention.", "Theo Branigan"),
        ("How to Build a Trading Journal That Actually Improves You", "Most trading journals are abandoned within a month. We share a minimal but powerful journal template that helps traders identify their personal edge—and the patterns that quietly cost them money.", "Riley McKenna"),
        ("Risk Management Is Boring, Which Is Why It Works", "The traders who survive decades have one thing in common: they make risk management the most prominent part of their workflow. We share three rules that have stood the test of time.", "Theo Branigan"),
        ("Why ETFs Are Quietly Replacing Stock Picking for Most Americans", "Stock picking has lost its glamor for good reason. ETFs offer diversification, low fees, and tax efficiency that few individual investors can match. Here's why they continue to dominate.", "Riley McKenna"),
        ("Building a Sustainable Trading Routine Around a Full-Time Job", "Most traders aren't pros—they have day jobs and families. We outline a sustainable routine that fits trading into a busy life without sacrificing performance or peace of mind.", "Theo Branigan"),
    ],
}


def slugify(s: str) -> str:
    out = "".join(c.lower() if c.isalnum() else "-" for c in s)
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")


def build_post_body(title: str, excerpt: str, category: str) -> str:
    """Generate rich HTML body content for a blog post."""
    section_titles = {
        "travel": ["The Setting", "Why It Matters", "How To Get There", "What To Expect", "A Slow-Travel Itinerary", "Final Thoughts"],
        "tech": ["The Backstory", "What We Tested", "Key Takeaways", "Real-World Performance", "Recommendations", "The Bottom Line"],
        "finance": ["The Big Picture", "Crunching The Numbers", "Common Mistakes", "A Practical Plan", "Risks To Watch", "Closing Thought"],
        "products": ["Why It Caught Our Attention", "How We Tested", "What Stood Out", "What Could Be Better", "Who It's For", "Final Verdict"],
        "sports": ["The Setting", "Why It Matters Now", "What The Data Says", "Who To Watch", "The Bigger Picture", "Final Whistle"],
        "trading": ["The Core Idea", "How It Works In Practice", "Risk Management", "Real Examples", "Common Pitfalls", "Closing Thought"],
    }[category]

    paragraphs = [
        f"<p class='lead'>{excerpt}</p>",
        f"<h2>{section_titles[0]}</h2>",
        f"<p>Across the {category} world, conversations have shifted in noticeable ways over the past year. The pace has slowed. The questions have deepened. {title.split(':')[0]} sits squarely at the intersection of that shift, and the more time you spend with the topic, the more its quiet relevance becomes apparent.</p>",
        "<p>Anyone who has spent the last decade following the space will recognize the patterns that led us here. The fast-and-loud era is fading; the careful-and-considered era is moving in. That's the lens we'll use throughout this piece.</p>",
        f"<h2>{section_titles[1]}</h2>",
        "<p>We talked to practitioners, hobbyists, and newcomers to capture a full perspective. Their stories share an unexpected through-line: progress comes more reliably from disciplined patience than from clever shortcuts.</p>",
        "<blockquote>“The biggest leap I made was when I stopped optimizing for novelty and started optimizing for clarity,” one expert told us during a long conversation over coffee.</blockquote>",
        f"<h2>{section_titles[2]}</h2>",
        "<p>Consider three principles that emerged consistently from our research:</p>",
        "<ul><li><strong>Slow, deliberate decisions</strong> — almost always outperform fast, reactive ones.</li><li><strong>Consistent process</strong> — beats sporadic intensity over any meaningful timeframe.</li><li><strong>Transparent record-keeping</strong> — produces the kind of feedback loop that turns experience into wisdom.</li></ul>",
        f"<h2>{section_titles[3]}</h2>",
        f"<p>None of this means you have to overhaul your life to see results. Small, sustainable changes accumulate. Whether you've been engaged with {category} for years or you're just discovering the space, the most reliable path forward is also usually the calmest.</p>",
        f"<h2>{section_titles[4]}</h2>",
        "<p>If we had to distill our findings to a single piece of advice, it would be this: clarity beats cleverness, and patience beats prediction. Build the routine before you chase the result.</p>",
        f"<h2>{section_titles[5]}</h2>",
        "<p>We'll keep tracking this space across future articles, with deeper case studies and reader stories. If you have a perspective worth sharing, the comments below are an excellent place to start the conversation.</p>",
    ]
    return "\n".join(paragraphs)


def get_seed_posts():
    """Return list of post documents ready to insert into MongoDB."""
    posts = []
    base_time = datetime.now(timezone.utc)
    idx = 0
    for category, items in POSTS_BY_CATEGORY.items():
        for i, (title, excerpt, author) in enumerate(items):
            slug = slugify(title)
            cover = IMAGES[category][i % len(IMAGES[category])]
            published = base_time - timedelta(days=idx)
            posts.append({
                "id": str(uuid.uuid4()),
                "slug": slug,
                "title": title,
                "excerpt": excerpt,
                "content": build_post_body(title, excerpt, category),
                "category": category,
                "author": author,
                "cover_image": cover,
                "published": True,
                "tags": [category, "editorial", "long-read"],
                "published_at": published.isoformat(),
                "created_at": published.isoformat(),
                "updated_at": published.isoformat(),
                "views": 100 + (idx * 7) % 900,
                "reactions": {"like": 5 + idx % 30, "love": 2 + idx % 18, "insightful": 1 + idx % 12},
                "read_time": 6 + (idx % 6),
            })
            idx += 1
    return posts


CATEGORIES_META = [
    {"slug": "travel", "name": "Travel", "tagline": "Slow journeys across America and beyond.", "color": "#839788"},
    {"slug": "tech", "name": "Tech", "tagline": "Calm tools for a noisy world.", "color": "#5C6B6D"},
    {"slug": "finance", "name": "Finance", "tagline": "Patient money for thoughtful lives.", "color": "#C6A28A"},
    {"slug": "products", "name": "Products", "tagline": "Considered things, tested honestly.", "color": "#9C8B7A"},
    {"slug": "sports", "name": "Sports", "tagline": "Calm takes on the games we love.", "color": "#6E8B7E"},
    {"slug": "trading", "name": "Trading", "tagline": "Markets explored with discipline.", "color": "#A48A6E"},
]
