"""
VERA-ID: Verification Engine for Results & Accountability - Idaho
Type 4 Detection using WIDA ACCESS for ELLs Speaking vs Writing + ISAT Achievement Data

Idaho context:
- WIDA ACCESS for ELLs, 4 domains (Listening, Speaking, Reading, Writing)
- ISAT (Idaho Standards Achievement Test) -- Smarter Balanced, 4 levels:
    Below Basic / Basic / Proficient / Advanced
- ~188 LEAs (115 districts + 73 charter schools), ~17,000 ELs (~5% statewide)
- Top EL districts: Nampa, Caldwell, Boise (Treasure Valley)
- Rural EL teacher shortage: 4x caseload vs urban peers
- Significant rural/agricultural EL populations in Magic Valley (Twin Falls, Jerome, Burley)
- idahoschools.org -- public data dashboard
- Idaho uses a continuous improvement framework (not A-F letter grades)

H-EDU.Solutions | https://h-edu.solutions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# CONFIGURATION
# ============================================================================

APP_ID_BLUE = "#003DA5"
ID_RED = "#C8102E"
ID_DARK = "#002970"
ID_GRAY = "#4A4A4A"
ID_LIGHT_BLUE = "#4D7FCC"

# ============================================================================
# DATA: Idaho Districts with EL Populations
# Source: ISDE / idahoschools.org
# ============================================================================

def load_districts():
    """Load ID districts with significant EL populations.

    Idaho's EL population is concentrated in two corridors:
    1. Treasure Valley (Nampa, Caldwell, Boise) -- urban/suburban, agricultural processing
    2. Magic Valley (Twin Falls, Jerome, Burley) -- dairy/agricultural, refugee resettlement

    The rural EL teacher shortage is acute: rural districts report 4x the ESL caseload
    compared to urban peers, with some teachers serving 100+ EL students across
    multiple schools. Idaho uses ~188 LEAs (115 traditional districts + 73 charter schools).
    """
    data = [
        # (lea_id, district_name, total_students, el_count, el_percent,
        #  isat_proficient_all, isat_proficient_el, graduation_rate, region, context_note)

        # --- Treasure Valley (Boise metro) ---
        ("131", "Nampa School District", 14800, 3552, 24.0, 38.5, 11.8, 82.5, "Treasure Valley", "Highest EL count; agricultural processing hub"),
        ("132", "Caldwell School District", 6200, 1798, 29.0, 36.2, 10.5, 80.2, "Treasure Valley", "Canyon County; highest EL%; dairy/agriculture"),
        ("001", "Boise School District", 25000, 2250, 9.0, 52.5, 18.2, 90.5, "Treasure Valley", "Capital city; refugee resettlement (IRC)"),
        ("003", "Meridian Joint SD", 48000, 2400, 5.0, 55.8, 19.5, 92.8, "Treasure Valley", "Largest district; suburban growth"),
        ("133", "Vallivue School District", 8500, 2380, 28.0, 37.8, 11.2, 81.5, "Treasure Valley", "Canyon County; rapid EL growth"),

        # --- Magic Valley (Twin Falls area) ---
        ("411", "Twin Falls School District", 8500, 1190, 14.0, 42.8, 13.5, 84.2, "Magic Valley", "Regional hub; refugee resettlement (CSI)"),
        ("261", "Jerome School District", 3800, 950, 25.0, 38.5, 11.5, 80.8, "Magic Valley", "Dairy industry; high EL concentration"),
        ("151", "Cassia County Joint SD", 5200, 780, 15.0, 40.2, 12.8, 83.5, "Magic Valley", "Burley area; agricultural ELs"),
        ("262", "Wendell School District", 1200, 360, 30.0, 35.5, 9.8, 78.5, "Magic Valley", "Highest rural EL%; dairy/goat farms"),
        ("321", "Madison School District", 6800, 680, 10.0, 48.5, 15.8, 88.2, "Magic Valley", "Rexburg area; university town"),

        # --- Other Idaho ---
        ("271", "Pocatello/Chubbuck SD", 12500, 875, 7.0, 44.2, 14.2, 85.5, "Eastern Idaho", "University town; moderate EL population"),
        ("091", "Idaho Falls SD", 11200, 896, 8.0, 46.5, 15.2, 86.8, "Eastern Idaho", "INL corridor; technical workforce"),
        ("241", "Gooding Joint SD", 1400, 336, 24.0, 36.8, 10.8, 79.2, "Magic Valley", "Small rural; 4x ESL caseload problem"),
        ("331", "Minidoka County Joint SD", 4200, 630, 15.0, 39.5, 12.2, 82.2, "Magic Valley", "Rupert/Heyburn; agricultural"),
        ("370", "Homedale Joint SD", 1600, 384, 24.0, 37.2, 11.0, 79.8, "Treasure Valley", "Owyhee County; rural agricultural"),
    ]

    return pd.DataFrame(data, columns=[
        'lea_id', 'district_name', 'total_students',
        'el_count', 'el_percent',
        'isat_proficient_all', 'isat_proficient_el', 'graduation_rate',
        'region', 'context_note'
    ])


# ============================================================================
# DATA: ACCESS Domain Data (WIDA ACCESS for ELLs)
# ============================================================================

def load_access_data(districts_df):
    """Generate district ACCESS domain data modeled from ID EL performance patterns.
    Idaho uses WIDA ACCESS for EL assessment."""
    access_data = []

    for _, d in districts_df.iterrows():
        for grade in range(3, 9):
            for year in [2024, 2025]:
                base_speaking = 333 + (grade * 8)
                base_writing = 283 + (grade * 6)

                el_density_penalty = max(0, (d['el_percent'] - 12) * 0.4)
                el_factor = d['isat_proficient_el'] / 13.0
                speaking_adj = int(13 * el_factor + d['el_percent'] * 0.2 - el_density_penalty)
                writing_adj = int(-9 + (el_factor - 1) * 10 - el_density_penalty * 0.8)

                yr_adj = 3 if year == 2025 else 0

                access_data.append({
                    'lea_id': d['lea_id'],
                    'district_name': d['district_name'],
                    'grade': grade,
                    'year': year,
                    'total_tested': max(12, int(d['el_count'] / 6)),
                    'listening_avg': base_speaking + speaking_adj - 4 + yr_adj,
                    'speaking_avg': base_speaking + speaking_adj + yr_adj,
                    'reading_avg': base_writing + writing_adj + 13 + yr_adj,
                    'writing_avg': base_writing + writing_adj + yr_adj,
                    'composite_avg': int((base_speaking + speaking_adj + base_writing + writing_adj) / 2 + 14 + yr_adj),
                })

    return pd.DataFrame(access_data)


# ============================================================================
# DATA: ISAT Achievement Data
# ISAT (Smarter Balanced), 4 levels:
#   Below Basic / Basic / Proficient / Advanced
# ============================================================================

def load_isat_data(districts_df):
    """Generate ISAT data based on idahoschools.org patterns."""
    isat_data = []

    for _, d in districts_df.iterrows():
        for grade in range(3, 9):
            for year in [2024, 2025]:
                for subject in ['ELA', 'Math']:
                    base = d['isat_proficient_all'] if subject == 'ELA' else d['isat_proficient_all'] * 0.83
                    proficient_advanced = max(8, min(80, base + (grade - 5) * -1.2))

                    advanced = max(2, proficient_advanced * 0.20)
                    proficient = proficient_advanced - advanced
                    basic = max(12, (100 - proficient_advanced) * 0.40)
                    below_basic = max(8, 100 - proficient_advanced - basic)

                    isat_data.append({
                        'lea_id': d['lea_id'],
                        'district_name': d['district_name'],
                        'grade': grade,
                        'subject': subject,
                        'year': year,
                        'proficient_advanced_pct': round(proficient_advanced, 1),
                        'advanced_pct': round(advanced, 1),
                        'proficient_pct': round(proficient, 1),
                        'basic_pct': round(basic, 1),
                        'below_basic_pct': round(below_basic, 1),
                    })

    return pd.DataFrame(isat_data)


# ============================================================================
# DATA: Statewide Domain Proficiency (WIDA ACCESS results)
# ============================================================================

def load_statewide_domain_data():
    """Statewide ACCESS domain proficiency percentages by grade cluster.
    Source: ISDE EL reports / WIDA ACCESS results."""
    return pd.DataFrame([
        {'year': '2024-25', 'grade_cluster': 'K-2', 'listening': 42, 'speaking': 37, 'reading': 25, 'writing': 17},
        {'year': '2024-25', 'grade_cluster': '3-5', 'listening': 46, 'speaking': 42, 'reading': 29, 'writing': 20},
        {'year': '2024-25', 'grade_cluster': '6-8', 'listening': 50, 'speaking': 45, 'reading': 33, 'writing': 23},
        {'year': '2024-25', 'grade_cluster': '9-12', 'listening': 53, 'speaking': 48, 'reading': 36, 'writing': 25},
        {'year': '2023-24', 'grade_cluster': 'K-2', 'listening': 39, 'speaking': 34, 'reading': 23, 'writing': 15},
        {'year': '2023-24', 'grade_cluster': '3-5', 'listening': 43, 'speaking': 39, 'reading': 27, 'writing': 18},
        {'year': '2023-24', 'grade_cluster': '6-8', 'listening': 47, 'speaking': 42, 'reading': 31, 'writing': 21},
        {'year': '2023-24', 'grade_cluster': '9-12', 'listening': 50, 'speaking': 45, 'reading': 34, 'writing': 23},
    ])


# ============================================================================
# DATA: EL Population Growth
# ============================================================================

def load_el_growth_data():
    """Idaho EL population growth -- driven by Treasure Valley and Magic Valley
    agricultural industries, plus refugee resettlement in Boise and Twin Falls."""
    return pd.DataFrame([
        {'year': 2008, 'el_count': 12800, 'el_percent': 4.5, 'note': 'Baseline'},
        {'year': 2010, 'el_count': 13200, 'el_percent': 4.6, 'note': ''},
        {'year': 2012, 'el_count': 13800, 'el_percent': 4.7, 'note': 'Dairy industry expansion'},
        {'year': 2014, 'el_count': 14500, 'el_percent': 4.8, 'note': 'Refugee resettlement growth'},
        {'year': 2016, 'el_count': 15200, 'el_percent': 4.9, 'note': ''},
        {'year': 2018, 'el_count': 15800, 'el_percent': 5.0, 'note': 'ESL teacher shortage emerges'},
        {'year': 2020, 'el_count': 15500, 'el_percent': 4.9, 'note': 'COVID dip'},
        {'year': 2022, 'el_count': 16200, 'el_percent': 5.0, 'note': 'Post-COVID rebound'},
        {'year': 2024, 'el_count': 16800, 'el_percent': 5.1, 'note': 'Rural caseload crisis'},
        {'year': 2025, 'el_count': 17000, 'el_percent': 5.0, 'note': '4x rural caseload documented'},
    ])


# ============================================================================
# AUTHENTICATION
# ============================================================================


# ============================================================================
# TYPE 4 DETECTION
# ============================================================================

def compute_type4_analysis(access_df, lea_id, grade, year):
    filtered = access_df[
        (access_df['lea_id'] == lea_id) &
        (access_df['grade'] == grade) &
        (access_df['year'] == year)
    ]
    if filtered.empty:
        return None

    row = filtered.iloc[0]
    delta = row['speaking_avg'] - row['writing_avg']
    delta_normalized = delta / 5
    flagged = delta_normalized > 8

    return {
        'lea_id': lea_id, 'district_name': row['district_name'],
        'grade': grade, 'year': year,
        'speaking_avg': row['speaking_avg'], 'writing_avg': row['writing_avg'],
        'delta': delta, 'delta_normalized': delta_normalized, 'flagged': flagged,
        'total_tested': row['total_tested'],
        'estimated_flagged': int(row['total_tested'] * 0.15) if flagged else int(row['total_tested'] * 0.05)
    }


# ============================================================================
# PAGE 1: OVERVIEW
# ============================================================================

def render_overview(districts_df):
    st.header("Idaho Education Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Pilot Districts", len(districts_df))
    with col2: st.metric("Total Students", f"{districts_df['total_students'].sum():,}")
    with col3: st.metric("English Learners", f"{districts_df['el_count'].sum():,}")
    with col4: st.metric("Statewide EL %", "~5%", delta="Growing steadily")

    st.divider()

    # Key policy context
    st.subheader("Key Policy Context")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.error("**Rural ESL Teacher Shortage**\nRural districts report 4x the ESL caseload of urban peers; some teachers serve 100+ ELs across multiple schools")
    with col2:
        st.warning("**ISAT (Smarter Balanced)**\nIdaho Standards Achievement Test -- Smarter Balanced consortium member")
    with col3:
        st.success("**Two EL Corridors**\nTreasure Valley (Nampa/Caldwell) + Magic Valley (Twin Falls/Jerome) drive EL concentration")

    st.divider()

    # Idaho's unique context
    st.subheader("The Idaho Pattern: Rural Teacher Shortage & Two EL Corridors")
    st.markdown("""
    Idaho's ~17,000 English Learners are concentrated in two agricultural corridors:

    **Treasure Valley (Canyon County):** Nampa, Caldwell, Vallivue, and Homedale serve
    EL populations of 24-29%, driven by agricultural processing, dairy, and the broader
    Boise metro economy. These are the highest-concentration districts in the state.

    **Magic Valley:** Twin Falls, Jerome, Wendell, and Gooding serve EL populations of
    14-30%, driven by the dairy industry and refugee resettlement programs. These
    rural/small-city districts face the most acute ESL teacher shortages.

    **The 4x Caseload Crisis:** Rural Idaho ESL teachers carry **4 times the caseload**
    of their urban counterparts. In districts like Gooding and Wendell, a single ESL
    teacher may serve 100+ students across multiple school buildings, traveling between
    sites daily. This directly impacts the quality of writing instruction ELs receive.

    | District | EL % | Region | ESL Challenge |
    |----------|------|--------|---------------|
    | Wendell | **30.0%** | Magic Valley | Highest rural EL%; dairy/goat farms |
    | Caldwell | **29.0%** | Treasure Valley | Canyon County; highest EL% |
    | Vallivue | **28.0%** | Treasure Valley | Rapid EL growth |
    | Jerome | **25.0%** | Magic Valley | Dairy industry; high concentration |
    | Nampa | **24.0%** | Treasure Valley | Highest EL count statewide |
    """)

    st.divider()

    st.subheader("Assessment Framework")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **ISAT (Smarter Balanced):**
        - Idaho Standards Achievement Test
        - ELA and Math, grades 3-8, 10
        - 4 Achievement Levels:
            - **Advanced** -- exceeds standard
            - **Proficient** -- meets standard
            - **Basic** -- approaching standard
            - **Below Basic** -- below expectations
        - Results on idahoschools.org

        **Continuous Improvement Framework:**
        - No A-F letter grades
        - Growth-focused accountability
        - ESSA indicators: achievement, growth,
          graduation, ELP progress
        """)
    with col2:
        st.markdown("""
        **EL Program:**
        - **WIDA ACCESS** for ELP assessment
        - 4 Domains: Listening, Speaking, Reading, Writing
        - ~188 LEAs (~115 districts + ~73 charters)
        - ~17,000 ELs (~5% statewide)

        **Key Language Groups:**
        - Spanish (~82% of ELs)
        - Arabic (~4% -- refugee resettlement)
        - Swahili/Kirundi (~3% -- Congolese refugees)
        - Marshallese, Somali, Dari

        **Key Context:**
        - **4x rural ESL caseload** shortage
        - **Treasure Valley** + **Magic Valley** corridors
        - **Refugee resettlement** (Boise IRC, Twin Falls CSI)
        - **Dairy/agricultural** industry driver
        - **Charter school** EL service gaps

        **Data:** idahoschools.org
        """)

    st.divider()

    # District table
    st.subheader("Pilot Districts -- EL Populations & Performance")
    display = districts_df[['lea_id', 'district_name', 'total_students', 'el_count',
                            'el_percent', 'isat_proficient_all', 'isat_proficient_el',
                            'graduation_rate', 'region']].copy()
    display.columns = ['LEA ID', 'District', 'Students', 'EL Count', 'EL %',
                       'ISAT Prof+ All %', 'ISAT Prof+ EL %', 'Grad Rate %', 'Region']
    st.dataframe(display, use_container_width=True, hide_index=True)

    # EL bar chart
    st.subheader("English Learner Population by District")
    fig = px.bar(
        districts_df.sort_values('el_count', ascending=True),
        x='el_count', y='district_name', orientation='h',
        color='el_percent', color_continuous_scale=[[0, '#C0C0C0'], [1, ID_BLUE]],
        labels={'el_count': 'English Learners', 'district_name': 'District', 'el_percent': 'EL %'}
    )
    fig.update_layout(height=550, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # Regional distribution
    st.subheader("EL Concentration by Region")
    region_df = districts_df[['district_name', 'el_percent', 'total_students', 'region']].copy()
    fig2 = px.scatter(region_df, x='total_students', y='el_percent',
                      color='region', size='el_percent',
                      hover_name='district_name',
                      color_discrete_map={
                          'Treasure Valley': ID_BLUE,
                          'Magic Valley': ID_RED,
                          'Eastern Idaho': ID_GRAY
                      },
                      labels={'total_students': 'Total Enrollment', 'el_percent': 'EL %',
                              'region': 'Region'})
    fig2.update_layout(
        title="EL % vs District Size by Region -- Two Corridors of Concentration",
        height=400
    )
    st.plotly_chart(fig2, use_container_width=True)


# ============================================================================
# PAGE 2: DOMAIN ANALYSIS
# ============================================================================

def render_domain_analysis(domain_df, growth_df):
    st.header("Statewide ACCESS Domain Proficiency")

    st.markdown("""
    **Source:** ISDE EL reports / WIDA ACCESS results.
    Idaho is a WIDA Consortium member. Domain proficiency percentages reveal the
    systemic oral-written delta.

    **Idaho Context:** The rural ESL teacher shortage (4x caseload) directly impacts
    writing instruction quality. In districts where one ESL teacher serves 100+ students
    across multiple buildings, sustained writing instruction is nearly impossible.
    Students develop conversational English through community immersion in agricultural
    communities but lack structured academic writing support.
    """)

    year = st.selectbox("Year", ['2024-25', '2023-24'], key="dom_y")
    filtered = domain_df[domain_df['year'] == year]

    st.divider()

    fig = go.Figure()
    for domain, color in [('listening', ID_GRAY), ('speaking', ID_BLUE),
                          ('reading', ID_LIGHT_BLUE), ('writing', ID_RED)]:
        fig.add_trace(go.Bar(
            x=filtered['grade_cluster'], y=filtered[domain],
            name=domain.capitalize(), marker_color=color,
            text=[f"{v}%" for v in filtered[domain]], textposition='outside'
        ))
    fig.update_layout(
        title=f"ACCESS Domain Proficiency by Grade Cluster ({year})",
        xaxis_title="Grade Cluster", yaxis_title="% Proficient",
        barmode='group', height=450, yaxis=dict(range=[0, 65])
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Speaking-Writing Delta by Grade Cluster")
    filtered = filtered.copy()
    filtered['delta'] = filtered['speaking'] - filtered['writing']
    fig2 = go.Figure(go.Bar(
        x=filtered['grade_cluster'], y=filtered['delta'],
        marker_color=[ID_RED if d > 18 else ID_LIGHT_BLUE for d in filtered['delta']],
        text=[f"{d:+d} pts" for d in filtered['delta']], textposition='outside'
    ))
    fig2.update_layout(title="Speaking - Writing Gap", yaxis_title="Delta (percentage points)", height=350)
    st.plotly_chart(fig2, use_container_width=True)

    avg_delta = filtered['delta'].mean()
    st.metric("Average Speaking-Writing Delta", f"{avg_delta:+.0f} percentage points",
              help="Positive = Speaking proficiency exceeds Writing proficiency statewide")

    st.divider()

    # EL growth over time
    st.subheader("Idaho EL Population Growth")
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=growth_df['year'], y=growth_df['el_count'],
        mode='lines+markers', line=dict(color=ID_BLUE, width=3),
        marker=dict(size=8), name='EL Count'
    ))
    fig3.update_layout(
        title="EL Population Growth -- Driven by Agricultural Corridors & Refugee Resettlement",
        xaxis_title="Year", yaxis_title="English Learners",
        height=400
    )
    fig3.add_annotation(x=2018, y=15800, text="ESL shortage emerges", showarrow=True, arrowhead=2)
    fig3.add_annotation(x=2025, y=17000, text="4x rural caseload", showarrow=True, arrowhead=2)
    st.plotly_chart(fig3, use_container_width=True)

    st.info("""
    **The 4x Caseload & Writing:** When ESL teachers carry 4x the recommended caseload,
    writing instruction is the first casualty. Writing requires intensive, individualized
    feedback that cannot be scaled across 100+ students. Speaking develops naturally through
    daily interaction, but academic writing requires structured instruction that
    overstretched rural ESL teachers cannot provide. This structural deficit amplifies
    the oral-written gap in Magic Valley and rural Treasure Valley districts.
    """)


# ============================================================================
# PAGE 3: EL ASSESSMENT ANALYSIS (ACCESS)
# ============================================================================

def render_el_assessment(access_df, districts_df):
    st.header("ACCESS for ELLs Analysis")
    st.markdown("""
    **WIDA ACCESS** measures English learners across four domains. Idaho has ~17,000 ELs
    across ~188 LEAs (115 districts + 73 charter schools).
    """)

    col1, col2, col3 = st.columns(3)
    with col1: district = st.selectbox("District", districts_df['district_name'].tolist(), key="acc_d")
    with col2: grade = st.selectbox("Grade", list(range(3, 9)), key="acc_g")
    with col3: year = st.selectbox("Year", [2025, 2024], key="acc_y")

    lea_id = districts_df[districts_df['district_name'] == district]['lea_id'].values[0]
    filtered = access_df[(access_df['lea_id'] == lea_id) &
                         (access_df['grade'] == grade) &
                         (access_df['year'] == year)]

    if not filtered.empty:
        row = filtered.iloc[0]
        st.divider()

        d_info = districts_df[districts_df['lea_id'] == lea_id].iloc[0]
        if d_info['el_percent'] > 20:
            st.warning(f"""
            **High-Concentration District:** {district} has **{d_info['el_percent']:.1f}% EL enrollment**.
            {d_info['context_note']}. Region: {d_info['region']}.
            """)

        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Listening", f"{row['listening_avg']:.0f}")
        with col2: st.metric("Speaking", f"{row['speaking_avg']:.0f}")
        with col3: st.metric("Reading", f"{row['reading_avg']:.0f}")
        with col4: st.metric("Writing", f"{row['writing_avg']:.0f}")

        domains = ['Listening', 'Speaking', 'Reading', 'Writing']
        scores = [row['listening_avg'], row['speaking_avg'], row['reading_avg'], row['writing_avg']]
        fig = go.Figure(go.Bar(x=domains, y=scores,
                               marker_color=[ID_GRAY, ID_BLUE, ID_LIGHT_BLUE, ID_RED],
                               text=[f"{s:.0f}" for s in scores], textposition='outside'))
        fig.update_layout(title=f"ACCESS Domains -- {district} -- Grade {grade} ({year})",
                         yaxis_title="Scale Score", height=400)
        st.plotly_chart(fig, use_container_width=True)

        oral = (row['listening_avg'] + row['speaking_avg']) / 2
        written = (row['reading_avg'] + row['writing_avg']) / 2
        gap = oral - written

        st.subheader("Oral vs Written Gap")
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Oral Average", f"{oral:.0f}")
        with col2: st.metric("Written Average", f"{written:.0f}")
        with col3: st.metric("Gap", f"{gap:+.0f}", delta="Flag" if gap > 30 else "Monitor" if gap > 20 else "OK")

        st.divider()
        st.subheader("Composite & Context")
        composite = row['composite_avg']
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Composite Average", f"{composite}")
        with col2: st.metric("Region", d_info['region'])
        with col3: st.metric("Total Tested", f"{row['total_tested']:,}")


# ============================================================================
# PAGE 4: TYPE 4 DETECTION
# ============================================================================

def render_type4(access_df, districts_df):
    st.header("Type 4 Detection")
    st.markdown("""
    **Type 4 candidates** show strong oral skills but weak written skills.
    Delta = Speaking Score - Writing Score. Flag threshold: normalized delta > 8 points.

    **Idaho Context:** The rural ESL teacher shortage (4x caseload) is the primary
    structural driver of Type 4 patterns in Idaho. In Magic Valley and rural Treasure
    Valley districts, students develop conversational English through community immersion
    in agricultural settings but receive minimal structured writing instruction due to
    overstretched ESL staff. The ISAT writing component further reveals this gap.
    """)

    col1, col2, col3 = st.columns(3)
    with col1: district = st.selectbox("District", districts_df['district_name'].tolist(), key="t4_d")
    with col2: grade = st.selectbox("Grade", list(range(3, 9)), key="t4_g")
    with col3: year = st.selectbox("Year", [2025, 2024], key="t4_y")

    lea_id = districts_df[districts_df['district_name'] == district]['lea_id'].values[0]
    result = compute_type4_analysis(access_df, lea_id, grade, year)

    if result:
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Speaking", f"{result['speaking_avg']:.0f}")
        with col2: st.metric("Writing", f"{result['writing_avg']:.0f}")
        with col3: st.metric("Delta", f"{result['delta']:+.0f}")
        with col4: st.metric("Status", "FLAGGED" if result['flagged'] else "OK")

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Speaking', x=['Score'], y=[result['speaking_avg']], marker_color=ID_BLUE))
        fig.add_trace(go.Bar(name='Writing', x=['Score'], y=[result['writing_avg']], marker_color=ID_RED))
        fig.update_layout(title=f"Speaking vs Writing -- {district} -- Grade {grade}", barmode='group', height=350)
        st.plotly_chart(fig, use_container_width=True)

        if result['flagged']:
            st.error(f"**Type 4 Flag Triggered** -- Delta: {result['delta']:+.0f}. "
                     f"Est. {result['estimated_flagged']} of {result['total_tested']} students affected.")
        else:
            st.success(f"**No Type 4 Flag** -- Delta within normal range ({result['delta']:+.0f}).")

        # All grades
        st.subheader(f"All Grades -- {district} ({year})")
        all_data = [compute_type4_analysis(access_df, lea_id, g, year) for g in range(3, 9)]
        all_data = [r for r in all_data if r]
        if all_data:
            gdf = pd.DataFrame(all_data)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=gdf['grade'], y=gdf['speaking_avg'], name='Speaking',
                                     mode='lines+markers', line=dict(color=ID_BLUE, width=3)))
            fig.add_trace(go.Scatter(x=gdf['grade'], y=gdf['writing_avg'], name='Writing',
                                     mode='lines+markers', line=dict(color=ID_RED, width=3)))
            fig.update_layout(title="Speaking vs Writing Across Grades", xaxis_title="Grade",
                             yaxis_title="Scale Score", height=400)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("District Summary")
        if all_data:
            summary_df = pd.DataFrame(all_data)[['grade', 'speaking_avg', 'writing_avg', 'delta', 'flagged', 'estimated_flagged']]
            summary_df.columns = ['Grade', 'Speaking', 'Writing', 'Delta', 'Flagged', 'Est. Affected']
            summary_df['Flagged'] = summary_df['Flagged'].map({True: 'YES', False: 'No'})
            st.dataframe(summary_df, use_container_width=True, hide_index=True)


# ============================================================================
# PAGE 5: ACHIEVEMENT GAPS
# ============================================================================

def render_achievement_gaps(districts_df):
    st.header("Achievement Gap Analysis")

    st.markdown("""
    **Data from idahoschools.org.** ISAT Proficient + Advanced rates across pilot districts.

    **ISAT** uses 4 achievement levels: Below Basic, Basic, Proficient, Advanced
    (Smarter Balanced alignment). Idaho uses a **continuous improvement framework**
    rather than A-F letter grades.

    **Key Pattern:** Magic Valley districts (Wendell, Jerome, Gooding) show the widest
    EL-to-All achievement gaps, correlating with the 4x ESL teacher caseload shortage.
    These districts have both high EL concentration and the fewest ESL resources.
    """)

    st.divider()

    # All vs EL comparison
    fig = go.Figure()
    sorted_df = districts_df.sort_values('isat_proficient_all', ascending=True)
    fig.add_trace(go.Bar(
        x=sorted_df['isat_proficient_all'], y=sorted_df['district_name'],
        name='All Students', orientation='h', marker_color=ID_GRAY
    ))
    fig.add_trace(go.Bar(
        x=sorted_df['isat_proficient_el'], y=sorted_df['district_name'],
        name='English Learners', orientation='h', marker_color=ID_BLUE
    ))
    fig.update_layout(
        title="ISAT Proficient+ Rate: All Students vs English Learners",
        barmode='group', xaxis_title="% Proficient + Advanced",
        height=600, legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Gap analysis
    st.subheader("All-EL Achievement Gap by District")
    gap_df = districts_df.copy()
    gap_df['el_gap'] = gap_df['isat_proficient_all'] - gap_df['isat_proficient_el']
    gap_df = gap_df.sort_values('el_gap', ascending=True)

    fig_gap = go.Figure(go.Bar(
        x=gap_df['el_gap'], y=gap_df['district_name'], orientation='h',
        marker_color=[ID_RED if g > 28 else ID_LIGHT_BLUE if g > 20 else ID_GRAY for g in gap_df['el_gap']],
        text=[f"{g:.0f} pts" for g in gap_df['el_gap']], textposition='outside'
    ))
    fig_gap.update_layout(title="All Students - EL Gap (ISAT Proficient+)",
                         xaxis_title="Gap (percentage points)", height=550)
    st.plotly_chart(fig_gap, use_container_width=True)

    # EL proficiency vs EL concentration by region
    st.subheader("EL Proficiency vs EL Concentration by Region")
    fig2 = px.scatter(districts_df, x='el_percent', y='isat_proficient_el', size='el_count',
                      color='region',
                      color_discrete_map={
                          'Treasure Valley': ID_BLUE,
                          'Magic Valley': ID_RED,
                          'Eastern Idaho': ID_GRAY
                      },
                      hover_name='district_name',
                      labels={'el_percent': 'EL %', 'isat_proficient_el': 'EL Prof+ %',
                              'el_count': 'EL Count', 'region': 'Region'})
    fig2.update_layout(
        title="EL Proficiency vs Concentration -- Magic Valley Shows Steepest Decline",
        height=450
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.info("""
    **Rural Caseload & Achievement:** The correlation between high EL concentration
    and low EL proficiency is strongest in Magic Valley, where ESL teachers carry
    4x the caseload of urban peers. This structural deficit means rural ELs receive
    less individualized instruction, less writing feedback, and less academic language
    development support -- directly widening the achievement gap.
    """)


# ============================================================================
# PAGE 6: ISAT ANALYSIS (State Test)
# ============================================================================

def render_isat(isat_df, districts_df):
    st.header("ISAT Assessment Analysis")
    st.markdown("""
    **ISAT (Idaho Standards Achievement Test)** is a Smarter Balanced assessment
    for grades 3-8 and 10 in ELA and Math.

    **4 Achievement Levels:**
    - **Advanced** -- Exceeds grade-level standard
    - **Proficient** -- Meets grade-level standard
    - **Basic** -- Approaching grade-level standard
    - **Below Basic** -- Below grade-level expectations

    Results are published on **idahoschools.org**. Idaho uses a **continuous improvement
    framework** rather than A-F letter grades for accountability.
    """)

    col1, col2, col3, col4 = st.columns(4)
    with col1: district = st.selectbox("District", districts_df['district_name'].tolist(), key="isat_d")
    with col2: grade = st.selectbox("Grade", list(range(3, 9)), key="isat_g")
    with col3: subject = st.selectbox("Subject", ['ELA', 'Math'], key="isat_s")
    with col4: year = st.selectbox("Year", [2025, 2024], key="isat_y")

    lea_id = districts_df[districts_df['district_name'] == district]['lea_id'].values[0]
    filtered = isat_df[(isat_df['lea_id'] == lea_id) &
                       (isat_df['grade'] == grade) &
                       (isat_df['subject'] == subject) &
                       (isat_df['year'] == year)]

    if not filtered.empty:
        row = filtered.iloc[0]
        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Proficient + Advanced", f"{row['proficient_advanced_pct']:.1f}%",
                      help="Grade-level proficient and above")
        with col2:
            st.metric("Advanced Only", f"{row['advanced_pct']:.1f}%",
                      help="Exceeds standard")

        st.divider()

        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Below Basic", f"{row['below_basic_pct']:.1f}%")
        with col2: st.metric("Basic", f"{row['basic_pct']:.1f}%")
        with col3: st.metric("Proficient", f"{row['proficient_pct']:.1f}%")
        with col4: st.metric("Advanced", f"{row['advanced_pct']:.1f}%")

        levels = ['Below\nBasic', 'Basic', 'Proficient', 'Advanced']
        values = [row['below_basic_pct'], row['basic_pct'], row['proficient_pct'], row['advanced_pct']]
        colors = ['#d32f2f', '#f57c00', ID_BLUE, ID_RED]
        fig = go.Figure(go.Bar(x=levels, y=values, marker_color=colors,
                               text=[f"{v:.1f}%" for v in values], textposition='outside'))
        fig.update_layout(title=f"ISAT {subject} -- {district} -- Grade {grade} ({year})",
                         yaxis_title="Percentage", height=420)
        st.plotly_chart(fig, use_container_width=True)

        d_info = districts_df[districts_df['lea_id'] == lea_id].iloc[0]

        st.subheader("District Context")
        st.markdown(f"""
        **{district}** -- Grade {grade} {subject} ({year}):
        - Proficient+ Rate: **{row['proficient_advanced_pct']:.1f}%**
        - Region: **{d_info['region']}** | EL %: **{d_info['el_percent']:.1f}%**
        - {d_info['context_note']}
        - Results on idahoschools.org
        """)


# ============================================================================
# PAGE 7: EXPORT DATA
# ============================================================================

def render_export(access_df, isat_df, districts_df, domain_df, growth_df):
    st.header("Export Data")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("ACCESS Data")
        st.dataframe(access_df, use_container_width=True, hide_index=True)
        st.download_button("Download ACCESS CSV", access_df.to_csv(index=False),
                          "vera_id_access.csv", "text/csv", use_container_width=True)
    with col2:
        st.subheader("ISAT Data")
        st.dataframe(isat_df, use_container_width=True, hide_index=True)
        st.download_button("Download ISAT CSV", isat_df.to_csv(index=False),
                          "vera_id_isat.csv", "text/csv", use_container_width=True)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Statewide Domain Proficiency")
        st.dataframe(domain_df, use_container_width=True, hide_index=True)
        st.download_button("Download Domain CSV", domain_df.to_csv(index=False),
                          "vera_id_domains.csv", "text/csv", use_container_width=True)
    with col2:
        st.subheader("District Data")
        st.dataframe(districts_df, use_container_width=True, hide_index=True)
        st.download_button("Download Districts CSV", districts_df.to_csv(index=False),
                          "vera_id_districts.csv", "text/csv", use_container_width=True)

    st.divider()

    st.subheader("EL Population Growth (2008-2025)")
    st.dataframe(growth_df, use_container_width=True, hide_index=True)
    st.download_button("Download EL Growth CSV", growth_df.to_csv(index=False),
                      "vera_id_el_growth.csv", "text/csv", use_container_width=True)


# ============================================================================
# MAIN
# ============================================================================

def main():
    st.set_page_config(page_title="VERA-ID | Idaho Type 4 Detection", page_icon="", layout="wide")

    st.markdown(f"""
    <style>
        .stApp {{ background-color: #fafafa; }}
        .block-container {{ padding-top: 2rem; }}
        h1, h2, h3 {{ color: {ID_BLUE}; }}
        .stButton > button {{ background-color: {ID_BLUE}; color: white; }}
        .stButton > button:hover {{ background-color: {ID_DARK}; color: white; }}
    </style>
    """, unsafe_allow_html=True)

    # Load data
    districts_df = load_districts()
    access_df = load_access_data(districts_df)
    isat_df = load_isat_data(districts_df)
    domain_df = load_statewide_domain_data()
    growth_df = load_el_growth_data()

    # Sidebar
    st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <h2 style="color: {ID_BLUE}; margin: 0;">VERA-ID</h2>
        <p style="color: #666; font-size: 0.85rem; margin-top: 5px;">Idaho Implementation</p>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.divider()

    page = st.sidebar.radio("Navigation", [
        "Overview",
        "Domain Analysis",
        "EL Assessment Analysis",
        "Type 4 Detection",
        "Achievement Gaps",
        "State Test Analysis",
        "Export Data"
    ])

    st.sidebar.divider()
    st.sidebar.markdown(f"""
    **Data Sources:**
    - ACCESS for ELLs (WIDA)
    - ISAT (Smarter Balanced)
    - idahoschools.org
    - ISDE EL reports

    **Type 4 Detection:**
    - Speaking vs Writing delta
    - Flag threshold: > 8 points
    - WIDA ACCESS domain scores

    **Key ID Context:**
    - ~188 LEAs, ~17K ELs (~5%)
    - Rural ESL teacher shortage:
      **4x caseload** vs urban peers
    - Two EL corridors:
      Treasure Valley (Nampa 24%,
      Caldwell 29%, Vallivue 28%)
      Magic Valley (Wendell 30%,
      Jerome 25%, Twin Falls 14%)
    - Refugee resettlement (Boise, Twin Falls)
    - Dairy/agricultural industry
    - Continuous improvement framework
    - ISAT: 4 levels (Smarter Balanced)

    ---
    [H-EDU.Solutions](https://h-edu.solutions)
    """)

    if page == "Overview": render_overview(districts_df)
    elif page == "Domain Analysis": render_domain_analysis(domain_df, growth_df)
    elif page == "EL Assessment Analysis": render_el_assessment(access_df, districts_df)
    elif page == "Type 4 Detection": render_type4(access_df, districts_df)
    elif page == "Achievement Gaps": render_achievement_gaps(districts_df)
    elif page == "State Test Analysis": render_isat(isat_df, districts_df)
    elif page == "Export Data": render_export(access_df, isat_df, districts_df, domain_df, growth_df)


if __name__ == "__main__":
    main()
