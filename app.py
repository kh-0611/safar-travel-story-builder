import streamlit as st
import hashlib
from pathlib import Path
import base64
from utils.ai import (
    generate_itinerary,
    parse_itinerary,
    generate_packing_list,
    parse_packing_list,
    generate_travel_story,
    parse_travel_story,
    ask_safar_ai,
)
from utils.db import (
    register_user,
    login_user,
    save_trip,
    get_trips,
    save_journal,
    get_journal_entries,
    count_journal_entries,
    save_expense,
    get_expenses,
    delete_expense
)
from utils.drive import (
    get_drive_service,
    upload_memory,
    get_safar_memories,
    get_memory_bytes,
    delete_memory
)
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from io import BytesIO

def create_story_pdf(
    title,
    story
):

    pdf_buffer = BytesIO()

    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    story_style = styles["BodyText"]
    story_style.leading = 18

    elements = []

    elements.append(
        Paragraph(
            title,
            title_style
        )
    )

    elements.append(
        Spacer(
            1,
            30
        )
    )

    paragraphs = story.split("\n")

    for paragraph in paragraphs:

        if paragraph.strip():

            elements.append(
                Paragraph(
                    paragraph.strip(),
                    story_style
                )
            )

            elements.append(
                Spacer(
                    1,
                    12
                )
            )

    document.build(elements)

    pdf_buffer.seek(0)

    return pdf_buffer.getvalue()

st.set_page_config(
    page_title="Safar",
    page_icon="🌍",
    layout="wide"
)



# Load theme.css
css_path = Path(__file__).parent / "theme.css"

with open(css_path, "r", encoding="utf-8") as f:
    css = f.read()

st.markdown(
    f"<style>{css}</style>",
    unsafe_allow_html=True
)
image_path = Path(__file__).parent / "assets" / "1.jpeg"

with open(image_path, "rb") as image_file:
    image_base64 = base64.b64encode(image_file.read()).decode()

st.markdown(
    f"""
    <div class="safar-top-banner">
        <img src="data:image/jpeg;base64,{image_base64}">
        <div class="safar-top-text">
            <span>✦ YOUR JOURNEY BEGINS HERE</span>
            <h1>SAFAR</h1>
            <p>Plan it. Live it. Remember it.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
# -----------------------------
# Login / Registration
# -----------------------------

if "user" not in st.session_state:

    st.session_state["user"] = None


if st.session_state["user"] is None:

    st.title("🌍 Welcome to SAFAR")

    st.write(
        "Your journey, beautifully planned and remembered."
    )

    tab1, tab2 = st.tabs(
        ["🔐 Login", "📝 Register"]
    )

    # -------------------------
    # Login
    # -------------------------

    with tab1:

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "🔐 Login",
            type="primary",
            use_container_width=True
        ):

            user = login_user(
                email.strip().lower(),
                password
            )

            if user:

                st.session_state["user"] = {
                    "id": str(user["_id"]),
                    "name": user["name"],
                    "email": user["email"]
                }

                st.success(
                    f"Welcome back, {user['name']}! 🌍"
                )

                st.rerun()

            else:

                st.error(
                    "❌ Invalid email or password."
                )

    # -------------------------
    # Registration
    # -------------------------

    with tab2:

        name = st.text_input(
            "Name",
            key="register_name"
        )

        email = st.text_input(
            "Email",
            key="register_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="confirm_password"
        )

        if st.button(
            "📝 Create Account",
            type="primary",
            use_container_width=True
        ):

            if not name or not email or not password:

                st.warning(
                    "Please fill in all fields."
                )

            elif password != confirm_password:

                st.error(
                    "❌ Passwords do not match."
                )

            else:

                created = register_user(
                    name.strip(),
                    email.strip().lower(),
                    password
                )

                if created:

                    st.success(
                        "🎉 Account created successfully! "
                        "Please login."
                    )

                else:

                    st.error(
                        "❌ An account with this email already exists."
                    )

    st.stop()

# -----------------------------
# Sidebar
# -----------------------------

with st.sidebar:

    st.markdown("## 🌍 SAFAR")

    st.caption(
        "Your journey, beautifully remembered."
    )
    st.write(
        f"👤 {st.session_state['user']['name']}"
    )

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state["user"] = None
        st.session_state.pop("trip", None)
        st.rerun()

    st.divider()

    page = st.radio(
        "Explore",
        [
            "🏠 Dashboard",
            "🗺️ Trip Planner",
            "📅 Itinerary",
            "💰 Budget",
            "🎒 Packing",
            "📸 Memories",
            "✍️ Journal",
            "💬 Safar AI",
            "📖 Story Maker"
        ]
    )


# -----------------------------
# Dashboard
# -----------------------------

if page == "🏠 Dashboard":

    st.markdown(
        '<div class="main-title">SAFAR 🌍</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Plan · Experience · Capture · Remember'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="hero-card">

        <div class="hero-text">
        Every journey has a story.
        </div>

        <p class="description">
        Safar helps you plan your trip, organize your experiences,
        preserve your memories and transform your journey into
        a personal travel story.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:

        saved_trips = get_trips(
            st.session_state["user"]["id"]
   )

        st.metric(
            "Trips",
            len(saved_trips)
        )

    with col2:

        active_trip = st.session_state.get("trip")

        if active_trip:

            memory_count = count_journal_entries(
                active_trip["id"]
            )

        else:

            memory_count = 0

        st.metric(
            "Memories",
            memory_count
        )

    with col3:

        st.metric(
            "Stories",
            "0"
        )

    st.write("")
    st.divider()

    st.subheader("🧳 Your Saved Trips")

    saved_trips = get_trips(
        st.session_state["user"]["id"]
    )

    if not saved_trips:

        st.info("🌍 No saved trips yet.")

    else:

        for trip in saved_trips:

            st.markdown(
                f"### 🌍 {trip.get('name', 'Untitled Trip')}"
            )

            st.write(
                f"📍 **Destination:** "
                f"{trip.get('destination', 'Unknown')}"
            )

            st.write(
                f"📅 **Dates:** "
                f"{trip.get('start_date', '')} → "
                f"{trip.get('end_date', '')}"
            )

            st.write(
                f"💰 **Budget:** "
                f"₹{trip.get('budget', 0):,}"
            )

            st.caption(
                f"Travel style: "
                f"{trip.get('travel_style', 'Not specified')}"
            )

            if st.button(
                "Open Trip",
                key=f"open_trip_{trip['_id']}"
            ):

                st.session_state["trip"] = {
                    "id": str(trip["_id"]),
                    "name": trip.get("name", ""),
                    "destination": trip.get("destination", ""),
                    "start_date": trip.get("start_date", ""),
                    "end_date": trip.get("end_date", ""),
                    "budget": trip.get("budget", 0),
                    "interests": trip.get("interests", ""),
                    "travel_style": trip.get(
                        "travel_style",
                        "Relaxed"
                    )
                }

                st.success(
                    f"🌍 {trip.get('name', 'Trip')} opened!"
                )

                st.rerun()

            st.divider()
            

# -----------------------------
# Create Trip
# -----------------------------

st.subheader("✨ Your journey starts here")

if st.button(
    "＋ Create Your First Trip",
    use_container_width=True
):
    st.session_state["create_trip"] = True


# -----------------------------
# Create Trip Form
# -----------------------------

if st.session_state.get("create_trip", False):

    st.divider()

    st.subheader("🌍 Create a Trip")

    trip_name = st.text_input(
        "Trip name",
        placeholder="e.g. Kashmir Escape"
    )

    destination = st.text_input(
        "Destination",
        placeholder="e.g. Kashmir"
    )

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "Start date"
        )

    with col2:
        end_date = st.date_input(
            "End date"
        )

    budget = st.number_input(
        "Trip budget (₹)",
        min_value=0,
        step=1000
    )

    interests = st.text_input(
        "Interests",
        placeholder="Nature, photography, food..."
    )

    travel_style = st.selectbox(
        "Travel style",
        [
            "Relaxed",
            "Adventure",
            "Luxury",
            "Budget",
            "Cultural",
            "Solo"
        ]
    )

    # -----------------------------
    # Create Trip Button
    # -----------------------------

    if st.button(
        "Create Trip",
        type="primary",
        use_container_width=True
    ):

        if not trip_name:
            st.warning("Please enter the trip name.")

        elif not destination:
            st.warning("Please enter a destination.")

        elif end_date < start_date:
            st.warning(
                "End date cannot be before start date."
            )

        elif budget <= 0:
            st.warning(
                "Please enter a trip budget."
            )

        else:

            trip_data = {
                "user_id": st.session_state["user"]["id"],
                "name": trip_name,
                "destination": destination,
                "start_date": str(start_date),
                "end_date": str(end_date),
                "budget": budget,
                "interests": interests,
                "travel_style": travel_style
            }

            trip_id = save_trip(trip_data)

            st.session_state["trip"] = {
                **trip_data,
                "id": trip_id
            }

            st.session_state["create_trip"] = False

            st.session_state.pop(
                "itinerary",
                None
            )

            st.session_state.pop(
                "expenses",
                None
            )

            st.success(
                f"🌍 {trip_name} has been created successfully!"
            )

            st.balloons()

            st.rerun()
    # -----------------------------
    # Current Trip
    # -----------------------------

    if st.session_state.get("trip"):

        trip = st.session_state["trip"]

        st.divider()

        st.subheader(
            "🌍 Your Current Trip"
        )

        st.write(
            f"### {trip['name']}"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                f"📍 **Destination:** "
                f"{trip['destination']}"
            )

            st.write(
                f"📅 **Dates:** "
                f"{trip['start_date']} → "
                f"{trip['end_date']}"
            )

            st.write(
                f"💰 **Budget:** "
                f"₹{trip['budget']:,.0f}"
            )

        with col2:

            st.write(
                f"✨ **Interests:** "
                f"{trip['interests']}"
            )

            st.write(
                f"🧭 **Travel style:** "
                f"{trip['travel_style']}"
            )


# -----------------------------
# Trip Planner
# -----------------------------

elif page == "🗺️ Trip Planner":

    st.title(
        "🗺️ AI Trip Planner"
    )

    st.write(
        "Let Safar create a personalized "
        "itinerary for your journey."
    )

    trip = st.session_state.get(
        "trip"
    )

    if not trip:

        st.info(
            "🌍 Create a trip from the "
            "Dashboard first."
        )

    else:

        st.subheader(
            f"Planning your journey to "
            f"{trip['destination']}"
        )

        st.write(
            f"**{trip['start_date']} → "
            f"{trip['end_date']}**"
        )

        st.write(
            f"**Budget:** "
            f"₹{trip['budget']:,}"
        )

        st.write(
            f"**Interests:** "
            f"{trip['interests']}"
        )

        st.write(
            f"**Travel style:** "
            f"{trip['travel_style']}"
        )

        st.divider()

        if st.button(
            "✨ Generate My Itinerary",
            type="primary",
            use_container_width=True
        ):

            with st.spinner(
                "Safar is planning your journey..."
            ):

                try:

                    itinerary_text = generate_itinerary(

                        destination=trip[
                            "destination"
                        ],

                        start_date=trip[
                            "start_date"
                        ],

                        end_date=trip[
                            "end_date"
                        ],

                        budget=trip[
                            "budget"
                        ],

                        interests=trip[
                            "interests"
                        ],

                        travel_style=trip[
                            "travel_style"
                        ]
                    )

                    try:

                        itinerary = parse_itinerary(
                            itinerary_text
                        )

                        st.session_state[
                            "itinerary"
                        ] = itinerary

                        st.success(
                            "✨ Your itinerary is ready!"
                        )

                    except Exception as e:

                        st.error(
                            "Could not process "
                            f"the AI itinerary: {e}"
                        )

                except Exception as e:

                    st.error(
                        "Unable to generate "
                        f"itinerary: {e}"
                    )

        # -----------------------------
        # Display Generated Itinerary
        # -----------------------------

        if st.session_state.get(
            "itinerary"
        ):

            itinerary = st.session_state[
                "itinerary"
            ]

            st.divider()

            st.subheader(
                "✨ Your Safar Itinerary"
            )

            for day in itinerary["days"]:

                st.divider()

                st.subheader(
                    f"Day {day['day']} · "
                    f"{day['date']}"
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.markdown(
                        "### 🌅 Morning"
                    )

                    st.write(
                        day["morning"]
                    )

                    st.markdown(
                        "### ☀️ Afternoon"
                    )

                    st.write(
                        day["afternoon"]
                    )

                with col2:

                    st.markdown(
                        "### 🌙 Evening"
                    )

                    st.write(
                        day["evening"]
                    )

                    st.markdown(
                        "### 🍽️ Food"
                    )

                    st.write(
                        day["food"]
                    )

                st.caption(
                    "Estimated spending: "
                    f"₹{day['estimated_cost']:,}"
                )


# -----------------------------
# Itinerary
# -----------------------------
elif page == "📅 Itinerary":

    st.title("📅 Your Itinerary")

    itinerary = st.session_state.get("itinerary")

    if not itinerary:
        st.info("✨ Generate an itinerary from the Trip Planner first.")

    else:
        st.write("Your journey, organized day by day.")

        for day in itinerary.get("days", []):

            st.divider()

            day_number = day.get("day", "")
            date = day.get("date", "")

            st.subheader(f"Day {day_number} · {date}")

            col1, col2 = st.columns(2)

            with col1:

                st.markdown("### 🌅 Morning")
                st.write(
                    day.get(
                        "morning",
                        "No morning activity provided."
                    )
                )

                st.markdown("### ☀️ Afternoon")
                st.write(
                    day.get(
                        "afternoon",
                        "No afternoon activity provided."
                    )
                )

            with col2:

                st.markdown("### 🌙 Evening")
                st.write(
                    day.get(
                        "evening",
                        "No evening activity provided."
                    )
                )

                st.markdown("### 🍽️ Food")
                st.write(
                    day.get(
                        "food",
                        "No food recommendation provided."
                    )
                )

            estimated_cost = day.get("estimated_cost", 0)

            st.caption(
                f"Estimated spending: ₹{estimated_cost:,}"
            )
# -----------------------------
# Budget & Expenses
# -----------------------------
elif page == "💰 Budget":

    st.title(
        "💰 Trip Budget"
    )

    st.write(
        "Track your spending and stay within your travel budget."
    )

    trip = st.session_state.get("trip")

    if not trip:

        st.info(
            "🌍 Open a trip from the Dashboard first."
        )

    else:

        st.subheader(
            f"💳 Budget for {trip['name']}"
        )

        total_budget = trip.get(
            "budget",
            0
        )

        # -----------------------------
        # Get Expenses from MongoDB
        # -----------------------------

        expenses = get_expenses(
            trip["id"]
        )

        total_spent = sum(
            float(expense.get("amount", 0))
            for expense in expenses
        )

        remaining = (
            total_budget
            - total_spent
        )

        # -----------------------------
        # Budget Summary
        # -----------------------------

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "💰 Total Budget",
                f"₹{total_budget:,.0f}"
            )

        with col2:

            st.metric(
                "💸 Total Spent",
                f"₹{total_spent:,.0f}"
            )

        with col3:

            st.metric(
                "✨ Remaining",
                f"₹{remaining:,.0f}"
            )

        # -----------------------------
        # Budget Progress
        # -----------------------------

        if total_budget > 0:

            progress = min(
                total_spent / total_budget,
                1.0
            )

            st.progress(
                progress
            )

            st.caption(
                f"{progress * 100:.1f}% "
                "of your budget has been used."
            )

        if remaining < 0:

            st.error(
                f"⚠️ You are ₹{abs(remaining):,.0f} "
                "over your budget."
            )

        elif total_budget > 0 and remaining <= total_budget * 0.2:

            st.warning(
                "⚠️ You are getting close to your budget limit."
            )

        st.divider()

        # -----------------------------
        # Add Expense
        # -----------------------------

        st.subheader(
            "➕ Add Expense"
        )

        col1, col2 = st.columns(2)

        with col1:

            expense_name = st.text_input(
                "Expense",
                placeholder="e.g. Hotel, Food, Transport"
            )

        with col2:

            expense_amount = st.number_input(
                "Amount (₹)",
                min_value=0.0,
                step=100.0
            )

        expense_category = st.selectbox(
            "Category",
            [
                "🏨 Stay",
                "🍽️ Food",
                "🚕 Transport",
                "🎟️ Activities",
                "🛍️ Shopping",
                "📦 Other"
            ]
        )

        if st.button(
            "💾 Save Expense",
            type="primary",
            use_container_width=True
        ):

            if not expense_name.strip():

                st.warning(
                    "Please enter an expense name."
                )

            elif expense_amount <= 0:

                st.warning(
                    "Please enter an amount greater than zero."
                )

            else:

                expense_data = {
                    "trip_id": trip["id"],
                    "trip_name": trip["name"],
                    "name": expense_name,
                    "amount": expense_amount,
                    "category": expense_category
                }

                save_expense(
                    expense_data
                )

                st.success(
                    "💰 Expense saved successfully!"
                )

                st.rerun()

        # -----------------------------
        # Expense History
        # -----------------------------

        st.divider()

        st.subheader(
            "📋 Expense History"
        )

        if not expenses:

            st.info(
                "No expenses added yet."
            )

        else:

            for expense in expenses:

                col1, col2, col3, col4 = st.columns(
                    [3, 2, 1, 1]
                )

                with col1:

                    st.write(
                        f"**{expense.get('name', 'Expense')}**"
                    )

                with col2:

                    st.caption(
                        expense.get(
                            "category",
                            "📦 Other"
                        )
                    )

                with col3:

                    st.write(
                        f"₹{float(expense.get('amount', 0)):,.0f}"
                    )

                with col4:

                    if st.button(
                        "🗑️",
                        key=f"delete_expense_{expense['_id']}"
                    ):

                        delete_expense(
                            str(expense["_id"])
                        )

                        st.success(
                            "🗑️ Expense deleted successfully!"
                        )

                        st.rerun()
        # -----------------------------
        # Spending Breakdown
        # -----------------------------

        if expenses:

            st.divider()

            st.subheader(
                "📊 Spending Breakdown"
            )

            import pandas as pd
            import plotly.express as px

            df = pd.DataFrame(
                expenses
            )

            category_totals = (
                df.groupby("category")["amount"]
                .sum()
                .reset_index()
            )

            fig = px.pie(
                category_totals,
                names="category",
                values="amount",
                hole=0.45
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )
# -----------------------------
# Packing
# -----------------------------
elif page == "🎒 Packing":

    st.title("🎒 Smart Packing List")
    st.write("A packing checklist prepared for your journey.")

    trip = st.session_state.get("trip")

    if not trip:

        st.info("🌍 Create a trip from the Dashboard first.")

    else:

        st.subheader(
            f"Packing for {trip['destination']}"
        )

        st.caption(
            f"{trip['travel_style']} trip · "
            f"{trip['start_date']} → {trip['end_date']}"
        )

        if st.button(
            "✨ Generate Smart Packing List",
            type="primary",
            use_container_width=True
        ):

            with st.spinner(
                "🧳 Safar is preparing your packing list..."
            ):

                try:

                    response = generate_packing_list(
                        trip["destination"],
                        trip["start_date"],
                        trip["end_date"],
                        trip["interests"],
                        trip["travel_style"]
                    )

                    packing_data = parse_itinerary(response)

                    st.session_state["ai_packing"] = (
                        packing_data["items"]
                    )

                    st.success(
                        "✨ Your personalized packing list is ready!"
                    )

                except Exception as e:

                    st.error(
                        f"Unable to generate packing list: {e}"
                    )

        if "ai_packing" in st.session_state:

            st.divider()

            st.subheader("🧳 Your Packing Checklist")

            items = st.session_state["ai_packing"]

            if "packed_items" not in st.session_state:
                st.session_state["packed_items"] = {}

            for index, item in enumerate(items):

                key = f"ai_pack_{index}"

                checked = st.checkbox(
                    item,
                    value=st.session_state[
                        "packed_items"
                    ].get(key, False),
                    key=key
                )

                st.session_state[
                    "packed_items"
                ][key] = checked

            packed = sum(
                st.session_state["packed_items"].get(
                    f"ai_pack_{i}",
                    False
                )
                for i in range(len(items))
            )

            total = len(items)

            st.divider()

            st.progress(
                packed / total if total else 0
            )

            st.write(
                f"🧳 **{packed} / {total} items packed**"
            )

            if packed == total and total > 0:

                st.success(
                    "🌍 Everything is packed. "
                    "You're ready for your Safar!"
                )

            else:

                st.info(
                    f"📦 {total - packed} items remaining."
                )
# -----------------------------
# Memories
# -----------------------------
elif page == "📸 Memories":

    st.title(
        "📸 Your Memories"
    )

    st.write(
        "Your travel memories stay under your control."
    )

    st.divider()

    st.subheader(
        "🔐 Private by Design"
    )

    st.write(
        "Safar does not automatically access your photos. "
        "Connect your Google Drive only when you choose to "
        "authorize it."
    )

    st.info(
        "☁️ Your photos will remain in your Google Drive. "
        "Safar will only access them after you give permission."
    )

    st.divider()

    if "drive_connected" not in st.session_state:

        st.session_state[
            "drive_connected"
        ] = False

    if not st.session_state[
        "drive_connected"
    ]:

        st.subheader(
            "☁️ Connect Google Drive"
        )

        st.write(
            "Authorize Google Drive to add photos and memories "
            "to your Safar journey."
        )

        if st.button(
            "🔐 Connect Google Drive",
            type="primary",
            use_container_width=True
        ):

            try:

                service = get_drive_service()

                st.session_state[
                    "drive_connected"
                ] = True

                st.success(
                    "✅ Google Drive connected successfully!"
                )

                st.rerun()

            except Exception as e:

                st.error(
                    "❌ Could not connect to Google Drive."
                )

                st.exception(
                    e
                )

    else:

        st.success(
            "✅ Google Drive connected"
        )

        st.subheader(
            "📸 Your Trip Memories"
        )

        st.write(
            "Your authorized travel memories will appear here."
        )

        if st.button(
            "➕ Add Memory",
            type="primary"
        ):

            st.session_state[
                "show_memory_uploader"
            ] = True


        if st.session_state.get(
            "show_memory_uploader",
            False
        ):

            st.divider()

            st.subheader(
                "📸 Add a Travel Memory"
            )

            uploaded_file = st.file_uploader(
                "Choose a photo",
                type=[
                    "jpg",
                    "jpeg",
                    "png",
                    "webp"
                ],
                key="memory_uploader"
            )

            if uploaded_file:

                st.image(
                    uploaded_file,
                    caption="Your selected memory",
                    use_container_width=True
                )

                if st.button(
                    "☁️ Save to Google Drive",
                    type="primary"
                ):

                    try:

                        service = get_drive_service()

                        result = upload_memory(
                            service,
                            uploaded_file.getvalue(),
                            uploaded_file.name,
                            uploaded_file.type
                        )

                        st.success(
                            f"✅ {result['name']} "
                            "was saved to your Google Drive!"
                        )

                    except Exception as e:

                        st.error(
                            "❌ Could not upload the memory."
                        )

                        st.exception(
                            e
                        )


        st.divider()

        st.subheader(
            "🖼️ Saved Memories"
        )

        try:

            service = get_drive_service()

            memories = get_safar_memories(
                service
            )

            if not memories:

                st.info(
                    "📸 No memories saved yet."
                )

            else:

                st.write(
                    f"✨ {len(memories)} "
                    "memory saved"
                    if len(memories) == 1
                    else f"✨ {len(memories)} memories saved"
                )
                for memory in memories:

                    try:

                        image_bytes = get_memory_bytes(
                            service,
                            memory["id"]
                        )

                        st.image(
                            image_bytes,
                            caption=memory["name"],
                            use_container_width=True
                        )

                        if st.button(
                            "🗑️ Delete",
                            key=f"delete_memory_{memory['id']}"
                        ):

                            delete_memory(
                                service,
                                memory["id"]
                            )

                            st.success(
                                f"🗑️ {memory['name']} deleted."
                            )

                            st.rerun()

                    except Exception:

                        st.warning(
                            f"⚠️ Could not display "
                            f"{memory['name']}"
                        )

        except Exception as e:

            st.error(
                "❌ Could not load your saved memories."
            )

            st.exception(
                e
            )
        # -----------------------------
        # Saved Memories
        # -----------------------------

        st.divider()

        st.subheader(
            "🖼️ Saved Memories"
        )

        try:

            service = get_drive_service()

            memories = get_safar_memories(
                service
            )

            if not memories:

                st.info(
                    "📸 No memories saved yet."
                )

            else:

                st.write(
                    f"✨ {len(memories)} "
                    "memory saved"
                    if len(memories) == 1
                    else f"✨ {len(memories)} memories saved"
                )

                for memory in memories:

                    try:

                        image_bytes = get_memory_bytes(
                            service,
                            memory["id"]
                        )

                        st.image(
                            image_bytes,
                            caption=memory["name"],
                            use_container_width=True
                        )

                    except Exception:

                        st.warning(
                            f"⚠️ Could not display "
                            f"{memory['name']}"
                        )

        except Exception as e:

            st.error(
                "❌ Could not load your saved memories."
            )

            st.exception(
                e
            )
elif page == "✨ Travel Story":

    st.title(
        "✨ Your Travel Story"
    )

    st.write(
        "Turn your journey, experiences and journal entries "
        "into a personal travel story."
    )

    trip = st.session_state.get("trip")

    if not trip:

        st.info(
            "🌍 Open a trip from the Dashboard first."
        )

    else:

        st.subheader(
            f"📖 Story of {trip['name']}"
        )

        journal_entries = get_journal_entries(
            trip["id"]
        )

        if not journal_entries:

            st.info(
                "✍️ Add some journal entries first. "
                "Your story will be created from your experiences."
            )

        else:

            st.write(
                f"📝 {len(journal_entries)} journal "
                f"entries found."
            )

            if st.button(
                "✨ Create My Travel Story",
                type="primary",
                use_container_width=True
            ):

                with st.spinner(
                    "📖 Safar is writing your story..."
                ):

                    try:

                        response = generate_travel_story(
                            trip["destination"],
                            trip["start_date"],
                            trip["end_date"],
                            trip["travel_style"],
                            trip["interests"],
                            journal_entries
                        )

                        story_data = parse_travel_story(
                            response
                        )

                        st.session_state[
                            "travel_story"
                        ] = story_data

                        st.success(
                            "✨ Your travel story is ready!"
                        )

                    except Exception as e:

                        st.error(
                            f"Unable to create your story: {e}"
                        )

            if "travel_story" in st.session_state:

                story = st.session_state[
                    "travel_story"
                ]

                st.divider()

                st.subheader(
                    story.get(
                        "title",
                        "My Travel Story"
                    )
                )
                pdf_data = create_story_pdf(
                      story.get(
                          "title",
                          "My Travel Story"
                      ),
                      story.get(
                          "story",
                          ""
                      )
                  )

                st.download_button(
                      label="📥 Download Travel Story PDF",
                      data=pdf_data,
                      file_name="SAFAR_Travel_Story.pdf",
                      mime="application/pdf",
                      use_container_width=True
                  )

                st.write(
                    story.get(
                        "story",
                        ""
                    )
                )
# -----------------------------
# Journal
# -----------------------------
elif page == "✍️ Journal":

    st.title(
        "✍️ Travel Journal"
    )

    st.write(
        "Write down the moments you want to remember."
    )

    trip = st.session_state.get("trip")

    if not trip:

        st.info(
            "🌍 Open a trip from the Dashboard first."
        )

    else:

        st.subheader(
            f"📖 Journal for {trip['name']}"
        )

        journal_date = st.date_input(
            "Date"
        )

        location = st.text_input(
            "Location",
            placeholder="e.g. Dal Lake"
        )

        mood = st.selectbox(
            "How did you feel?",
            [
                "😊 Happy",
                "✨ Excited",
                "🌿 Peaceful",
                "🥹 Emotional",
                "🤩 Amazed",
                "😌 Relaxed"
            ]
        )

        entry = st.text_area(
            "Your journal entry",
            placeholder=(
                "Write about what happened, "
                "what you saw, or how the moment felt..."
            ),
            height=200
        )

        if st.button(
            "💾 Save Journal Entry",
            type="primary",
            use_container_width=True
        ):

            if not entry.strip():

                st.warning(
                    "Please write something in your journal."
                )

            else:

                journal_data = {
                    "trip_id": trip["id"],
                    "trip_name": trip["name"],
                    "date": str(journal_date),
                    "location": location,
                    "mood": mood,
                    "entry": entry
                }

                save_journal(journal_data)

                st.success(
                    "📖 Your journal entry has been saved!"
                )

                st.rerun()

        st.divider()

        st.subheader(
            "📚 Previous Journal Entries"
        )

        journal_entries = get_journal_entries(
            trip["id"]
        )

        if not journal_entries:

            st.info(
                "Your saved journal entries will appear here."
            )

        else:

            for saved_entry in journal_entries:

                st.markdown(
                    f"### 📖 {saved_entry.get('date', '')}"
                )

                st.caption(
                    f"📍 {saved_entry.get('location', 'No location')} "
                    f"• {saved_entry.get('mood', '')}"
                )

                st.write(
                    saved_entry.get("entry", "")
                )

                st.divider()
                

# -----------------------------
# Safar AI
# -----------------------------

elif page == "💬 Safar AI":

    st.title(
        "💬 Safar AI"
    )

    st.write(
        "Ask Safar anything about your journey."
    )

    trip = st.session_state.get("trip")

    if not trip:

        st.info(
            "🌍 Open a trip from the Dashboard first."
        )

    else:

        st.subheader(
            f"🌍 Ask Safar about {trip['name']}"
        )

        journal_entries = get_journal_entries(
            trip["id"]
        )

        question = st.text_area(
            "What would you like to ask?",
            placeholder=(
                "Example: Suggest some things I can do "
                "during my trip..."
            )
        )

        if st.button(
            "✨ Ask Safar",
            type="primary",
            use_container_width=True
        ):

            if not question.strip():

                st.warning(
                    "Please enter a question first."
                )

            else:

                with st.spinner(
                    "💬 Safar is thinking..."
                ):

                    try:

                        answer = ask_safar_ai(
                            trip["destination"],
                            trip["start_date"],
                            trip["end_date"],
                            trip["travel_style"],
                            trip["interests"],
                            journal_entries,
                            question
                        )

                        st.session_state[
                            "safar_ai_answer"
                        ] = answer

                    except Exception as e:

                        st.error(
                            f"Unable to get an answer: {e}"
                        )

        if "safar_ai_answer" in st.session_state:

            st.divider()

            st.subheader(
                "💬 Safar says"
            )

            st.write(
                st.session_state[
                    "safar_ai_answer"
                ]
            )


# -----------------------------
# Story Maker
# -----------------------------
elif page == "📖 Story Maker":

    st.title(
        "📖 Story Maker"
    )

    st.write(
        "Turn your journey and journal entries "
        "into a personal travel story."
    )

    trip = st.session_state.get("trip")

    if not trip:

        st.info(
            "🌍 Open a trip from the Dashboard first."
        )

    else:

        st.subheader(
            f"✨ Story of {trip['name']}"
        )

        journal_entries = get_journal_entries(
            trip["id"]
        )

        if not journal_entries:

            st.info(
                "✍️ Add some journal entries first. "
                "Your story will be created from your experiences."
            )

        else:

            st.write(
                f"📝 {len(journal_entries)} journal "
                f"entries found."
            )

            if st.button(
                "✨ Create My Travel Story",
                type="primary",
                use_container_width=True
            ):

                with st.spinner(
                    "📖 Safar is writing your story..."
                ):

                    try:

                        response = generate_travel_story(
                            trip["destination"],
                            trip["start_date"],
                            trip["end_date"],
                            trip["travel_style"],
                            trip["interests"],
                            journal_entries
                        )

                        story_data = parse_travel_story(
                            response
                        )

                        st.session_state[
                            "travel_story"
                        ] = story_data

                        st.success(
                            "✨ Your travel story is ready!"
                        )

                    except Exception as e:

                        st.error(
                            f"Unable to create your story: {e}"
                        )

            if "travel_story" in st.session_state:

                story = st.session_state[
                    "travel_story"
                ]

                st.divider()

                st.subheader(
                    story.get(
                        "title",
                        "My Travel Story"
                    )
                )

                st.write(
                    story.get(
                        "story",
                        ""
                    )
                )