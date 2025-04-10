import streamlit as st
import pandas as pd
import altair as alt
import logging
from math import ceil
from fpdf import FPDF
import io

# -----------------------------------------------------------------------------
# Global Logging Setup (for development only; logs are printed in console)
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# -----------------------------------------------------------------------------
# Input Module
# -----------------------------------------------------------------------------
class InputModule:
    def __init__(self):
        self.inputs = {}

    def get_personal_information(self, data=None):
        st.sidebar.subheader("Personal Information")
        personal = data or {}
        personal['age'] = st.sidebar.number_input("Age", min_value=18, max_value=100, value=30)
        city = st.sidebar.selectbox("City Tier", options=['Tier 1', 'Tier 2', 'Tier 3'], index=1)
        personal['city'] = city
        # Map city cost factor
        valid_cities = {'Tier 1': 1.2, 'Tier 2': 1.0, 'Tier 3': 0.9}
        personal['city_cost_factor'] = valid_cities[city]
        personal['marital_status'] = st.sidebar.selectbox("Marital Status", options=['Married', 'Not Married'], index=1)
        if personal['marital_status'] == 'Not Married':
            personal['age_of_marriage'] = st.sidebar.number_input("Desired Age of Marriage", min_value=personal['age']+1, value=32)
        else:
            personal['age_of_marriage'] = None
        
        # Children: allow adding children with age at birth
        st.sidebar.markdown("**Children Details**")
        num_children = st.sidebar.number_input("Number of Children", min_value=0, value=1, step=1)
        children = []
        for i in range(num_children):
            age_at_birth = st.sidebar.number_input(f"Child {i+1} Age at Birth", min_value=0, value=0, key=f"child_{i}")
            children.append({"age_at_birth": age_at_birth})
        personal['children'] = children

        # Dependents
        st.sidebar.markdown("**Dependents**")
        options = ['Parent', 'Sibling', 'Pet', 'Child']
        num_dependents = st.sidebar.number_input("Number of Dependents", min_value=0, value=2, step=1)
        dependents = []
        for i in range(num_dependents):
            rel = st.sidebar.selectbox(f"Dependent {i+1} Relationship", options=options, key=f"dep_rel_{i}")
            dep_age = st.sidebar.number_input(f"Dependent {i+1} Age", min_value=0, value=30, key=f"dep_age_{i}")
            dependents.append({"relationship": rel, "age": dep_age})
        personal['dependents'] = dependents

        # Additional Income Sources
        st.sidebar.markdown("**Additional Income Sources**")
        options_income = ['Parental Contribution', 'Side Income', 'Passive Income']
        if personal['marital_status'] == 'Married':
            options_income.append("Spouse Contribution")
        num_income = st.sidebar.number_input("Number of Additional Income Sources", min_value=0, value=1, step=1)
        additional_income = []
        for i in range(num_income):
            source = st.sidebar.selectbox(f"Income Source {i+1}", options=options_income, key=f"inc_src_{i}")
            amount = st.sidebar.number_input(f"Amount for {source}", min_value=0.0, value=2000.0, key=f"inc_amt_{i}")
            additional_income.append({"source": source, "amount": amount})
        personal['additional_income_sources'] = additional_income

        self.inputs['personal_information'] = personal
        return personal

    def get_career_income_details(self, data=None):
        st.sidebar.subheader("Career & Income Details")
        career = data or {}
        career['employment_type'] = st.sidebar.selectbox("Employment Type", options=['Job', 'Business', 'Unemployed'], index=0)
        if career['employment_type'] == 'Job':
            career['job_role'] = st.sidebar.text_input("Job Role", value="Developer")
            career['job_level'] = st.sidebar.selectbox("Job Level", options=['Entry-Level', 'Mid-Level', 'Senior-Level', 'Leadership'], index=1)
            career['monthly_salary'] = st.sidebar.number_input("Monthly Salary (₹)", min_value=0.0, value=80000.0)
            bonus_frequency = st.sidebar.selectbox("Bonus Frequency", options=['annual', 'quarterly', 'monthly'], index=0)
            career['bonus'] = {
                "frequency": bonus_frequency,
                "amount": st.sidebar.number_input("Bonus Amount (₹)", min_value=0.0, value=12000.0)
            }
        elif career['employment_type'] == 'Business':
            career['industry'] = st.sidebar.text_input("Industry", value="Technology")
            career['annual_inhand_income'] = st.sidebar.number_input("Annual In-Hand Income (₹)", min_value=0.0, value=1000000.0)
        elif career['employment_type'] == 'Unemployed':
            career['source_of_income'] = st.sidebar.text_input("Source of Income", value="Savings")
            career['unemployed_monthly_income'] = st.sidebar.number_input("Monthly Income (₹)", min_value=0.0, value=10000.0)
        self.inputs['career_income_details'] = career
        return career

    def get_assets_liabilities_investments(self, data=None):
        st.sidebar.subheader("Assets, Liabilities & Investments")
        assets_data = data or {}
        assets_data['housing_status'] = st.sidebar.selectbox("Housing Status", options=['Rented', 'Owned', 'Owned by Parents'], index=1)
        if assets_data['housing_status'] == 'Owned':
            st.sidebar.markdown("**Mortgage Details**")
            md = {}
            md['emi_amount'] = st.sidebar.number_input("EMI Amount (₹)", min_value=0.0, value=15000.0, key="emi_amt")
            md['remaining_term'] = st.sidebar.number_input("Remaining Term (months)", min_value=1, value=240, key="term")
            md['loan_interest_rate'] = st.sidebar.number_input("Loan Interest Rate (%)", min_value=0.0, value=7.0, key="loan_rate")
            md['principal'] = st.sidebar.number_input("Principal (₹)", min_value=0.0, value=3000000.0, key="principal")
            md['market_value'] = st.sidebar.number_input("Market Value of House (₹)", min_value=0.0, value=3500000.0, key="market_value")
            assets_data['mortgage_details'] = md
        else:
            assets_data['mortgage_details'] = None

        st.sidebar.markdown("**Other Assets**")
        num_assets = st.sidebar.number_input("Number of Other Assets", min_value=0, value=1, step=1)
        other_assets = []
        for i in range(num_assets):
            asset_name = st.sidebar.text_input(f"Asset {i+1} Name", value="Car", key=f"asset_name_{i}")
            asset_value = st.sidebar.number_input(f"Asset {i+1} Value (₹)", min_value=0.0, value=800000.0, key=f"asset_val_{i}")
            other_assets.append({"asset_name": asset_name, "asset_value": asset_value})
        assets_data["other_assets"] = other_assets

        st.sidebar.markdown("**Investments**")
        num_inv = st.sidebar.number_input("Number of Investments", min_value=0, value=1, step=1)
        investments = []
        options_inv = ['stocks', 'crypto', 'fixed deposits', 'mutual funds', 'bonds', 'forex', 'gold', 'real estate', 'others']
        for i in range(num_inv):
            inv_type = st.sidebar.selectbox(f"Investment {i+1} Type", options=options_inv, key=f"inv_type_{i}")
            current_val = st.sidebar.number_input(f"Investment {i+1} Current Value (₹)", min_value=0.0, value=50000.0, key=f"inv_val_{i}")
            investments.append({"investment_type": inv_type, "current_value": current_val})
        assets_data["investments"] = investments

        st.sidebar.markdown("**Liabilities**")
        num_liab = st.sidebar.number_input("Number of Liabilities", min_value=0, value=1, step=1)
        liabilities = []
        for i in range(num_liab):
            liab_name = st.sidebar.text_input(f"Liability {i+1} Name", value="Car Loan", key=f"liab_name_{i}")
            interest_rate = st.sidebar.number_input(f"Liability {i+1} Interest Rate (%)", min_value=0.0, value=9.0, key=f"liab_rate_{i}")
            remaining_term = st.sidebar.number_input(f"Liability {i+1} Remaining Term (months)", min_value=1, value=36, key=f"liab_term_{i}")
            amount = st.sidebar.number_input(f"Liability {i+1} Amount (₹)", min_value=0.0, value=300000.0, key=f"liab_amt_{i}")
            liabilities.append({"liability_name": liab_name, "interest_rate": interest_rate, "remaining_term": remaining_term, "amount": amount, "min_payment": 10000})
        assets_data["liabilities"] = liabilities

        self.inputs["assets_liabilities_investments"] = assets_data
        return assets_data

    def get_retirement_investment_strategy(self, data=None):
        st.sidebar.subheader("Retirement & Investment Strategy")
        retirement = data or {}
        retirement["retirement_age"] = st.sidebar.number_input("Retirement Age", min_value=50, max_value=100, value=60)
        retirement["investment_strategy"] = st.sidebar.selectbox("Investment Strategy", options=['Conservative', 'Moderate', 'Aggressive'], index=1)
        self.inputs["retirement_investment_strategy"] = retirement
        return retirement

    def collect_all_inputs(self):
        self.get_personal_information()
        self.get_career_income_details()
        self.get_assets_liabilities_investments()
        self.get_retirement_investment_strategy()
        # Additional simulation parameters
        age = self.inputs["personal_information"]["age"]
        ret_age = self.inputs["retirement_investment_strategy"]["retirement_age"]
        self.inputs["simulation_parameters"] = {"years_to_simulate": ret_age - age, "starting_age": age}
        # Add default reserved funds (for life events) if not provided
        self.inputs["reserved_investments"] = 1000000
        self.inputs["emergency_fund"] = 500000
        return self.inputs

# -----------------------------------------------------------------------------
# ASSUMPTIONS & ANALYSIS MODULE
# -----------------------------------------------------------------------------
class AssumptionsAnalysis:
    def __init__(self, inputs):
        self.inputs = inputs
        self.logs = []

    def log(self, message):
        self.logs.append(message)
        logging.info(message)

    def handle_marriage_event(self, annual_income):
        pers = self.inputs.get("personal_information", {})
        marriage_age = pers.get("age_of_marriage")
        current_age = pers.get("age")
        if marriage_age is None or marriage_age <= current_age:
            raise ValueError("Invalid marriage age.")
        years_until_marriage = marriage_age - current_age
        scheduled_year = years_until_marriage
        self.log(f"Marriage scheduled in simulation year: {scheduled_year}")

        cost = max(1.8 * annual_income, 2000000)
        self.log(f"Calculated marriage cost: {cost:.2f}")

        reserved_inv = self.inputs.get("reserved_investments", 1000000)
        emergency = self.inputs.get("emergency_fund", 500000)
        if cost > 200000:
            if reserved_inv >= cost:
                funding_source = "Reserved Investments"
                reserved_inv -= cost
            else:
                shortfall = cost - reserved_inv
                funding_source = "Reserved Investments & Emergency Fund"
                emergency -= shortfall
            self.log(f"Marriage funded by {funding_source}. Updated reserves: Investments {reserved_inv}, Emergency {emergency}")
        dti = self.calculate_DTI()
        if dti > 0.4 or (reserved_inv + emergency) < cost:
            self.log("Marriage event delayed due to insufficient funds or high DTI.")
            scheduled_year += 1
        return {"event": "Marriage", "scheduled_year": scheduled_year, "cost": cost, "logs": self.logs.copy()}

    def handle_children_events(self):
        pers = self.inputs.get("personal_information", {})
        children = pers.get("children", [])
        events = []
        for i, child in enumerate(children):
            scheduled_year = child.get("age_at_birth", 0) + 1
            cost = 200000
            events.append({"event": f"Child_{i+1}_Expense", "scheduled_year": scheduled_year, "cost": cost})
            self.log(f"Scheduled one-time expense for Child {i+1} in year {scheduled_year} with cost {cost}.")
        return events

    def handle_unexpected_events(self, total_income, sim_year):
        events = []
        if sim_year % 3 == 0:
            cost = 0.2 * total_income
            events.append({"event": "Unexpected Expense", "scheduled_year": sim_year, "cost": cost})
            self.log(f"Unexpected expense scheduled in year {sim_year} with cost {cost:.2f}.")
        return events

    def calculate_DTI(self):
        career = self.inputs.get("career_income_details", {})
        monthly_income = career.get("monthly_salary", 0)
        liab = self.inputs.get("assets_liabilities_investments", {}).get("liabilities", [])
        total_debt = sum([l.get("min_payment", l.get("amount", 0)/l.get("remaining_term", 1)) for l in liab])
        dti = total_debt / monthly_income if monthly_income else 0
        self.log(f"Calculated DTI: {dti:.2f}")
        return dti

# -----------------------------------------------------------------------------
# DETAILED CALCULATION FORMULAS MODULE
# -----------------------------------------------------------------------------
class DetailedCalculations:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.logs = []

    def log(self, message):
        self.logs.append(message)
        logging.info(message)
        if self.verbose:
            st.write(message)

    # Income Projection
    def compute_monthly_income(self, base_salary, bonus, bonus_conversion_factor):
        monthly_income = base_salary + (bonus / bonus_conversion_factor)
        self.log(f"Monthly Income: {base_salary} + ({bonus}/{bonus_conversion_factor}) = {monthly_income:.2f}")
        return monthly_income

    def project_annual_income(self, current_income, growth_rate):
        new_income = current_income * (1 + growth_rate)
        self.log(f"Annual Income Projection: {current_income:.2f} * (1 + {growth_rate}) = {new_income:.2f}")
        return new_income

    def update_income_for_role_change(self, current_income, increment_rate):
        new_income = current_income * (1 + increment_rate)
        self.log(f"Role-based Income Update: {current_income:.2f} * (1 + {increment_rate}) = {new_income:.2f}")
        return new_income

    # Expense Adjustments
    def compute_baseline_expense(self, housing_status, baseline_rent, baseline_expense):
        if housing_status.lower() == "rented":
            expense = baseline_rent
            self.log(f"Baseline Expense (Rented): {expense:.2f}")
        elif housing_status.lower() == "owned":
            discount = 0.15
            expense = baseline_expense * (1 - discount)
            self.log(f"Baseline Expense (Owned): {baseline_expense:.2f}*(1-{discount}) = {expense:.2f}")
        else:
            expense = baseline_expense
            self.log(f"Baseline Expense (Other): {expense:.2f}")
        return expense

    def apply_inflation(self, expense, inflation_rate):
        new_expense = expense * (1 + inflation_rate)
        self.log(f"Expense with Inflation: {expense:.2f}*(1+{inflation_rate}) = {new_expense:.2f}")
        return new_expense

    def compute_marriage_cost(self, annual_income):
        cost = max(1.8 * annual_income, 2000000)
        self.log(f"Marriage Cost: max(1.8*{annual_income:.2f},2000000) = {cost:.2f}")
        return cost

    def compute_child_event_cost(self):
        cost = 200000
        self.log("Child Event Cost: ₹200000")
        return cost

    # Debt & EMI Calculation
    def calculate_emi(self, principal, annual_interest_rate, number_months):
        monthly_rate = (annual_interest_rate / 100) / 12
        self.log(f"Monthly Interest Rate: {monthly_rate:.6f}")
        factor = (1 + monthly_rate) ** number_months
        emi = (principal * monthly_rate * factor) / (factor - 1)
        self.log(f"EMI Calculation: {emi:.2f}")
        return emi

    def calculate_dti(self, total_monthly_debt_payments, gross_monthly_income):
        dti = total_monthly_debt_payments / gross_monthly_income if gross_monthly_income else 0
        self.log(f"DTI Calculation: {dti:.2f}")
        return dti

    # Asset Valuation
    def appreciate_asset(self, asset_value, appreciation_rate):
        new_value = asset_value * (1 + appreciation_rate)
        self.log(f"Asset Appreciation: {asset_value}*(1+{appreciation_rate}) = {new_value:.2f}")
        return new_value

    def depreciate_asset(self, asset_value, depreciation_rate):
        new_value = asset_value * (1 - depreciation_rate)
        self.log(f"Asset Depreciation: {asset_value}*(1-{depreciation_rate}) = {new_value:.2f}")
        return new_value

    # Tax Calculation
    def compute_taxable_income(self, total_income, allowable_deductions):
        taxable_income = total_income - allowable_deductions
        self.log(f"Taxable Income: {total_income} - {allowable_deductions} = {taxable_income}")
        return taxable_income

    def calculate_tax_liability(self, taxable_income):
        tax = 0
        slabs = [(400000, 0), (800000, 0.05), (1200000, 0.10), (1600000, 0.15), (2000000, 0.20), (2400000, 0.25)]
        if taxable_income <= 400000:
            tax = 0
        else:
            previous = 400000
            for upper, rate in slabs[1:]:
                if taxable_income > upper:
                    taxable_at_rate = upper - previous
                else:
                    taxable_at_rate = max(taxable_income - previous, 0)
                slab_tax = taxable_at_rate * rate
                self.log(f"Tax for slab {previous}-{upper} at {rate*100}%: {slab_tax}")
                tax += slab_tax
                previous = upper
                if taxable_income <= upper:
                    break
            if taxable_income > 2400000:
                extra = taxable_income - 2400000
                extra_tax = extra * 0.30
                self.log(f"Tax for amount above 2400000 at 30%: {extra_tax}")
                tax += extra_tax
        self.log(f"Total Tax Liability: {tax:.2f}")
        return tax

    # Savings, Investment & Rebalancing
    def compute_savings(self, total_income, total_expenses, debt_payments, taxes):
        savings = total_income - (total_expenses + debt_payments + taxes)
        self.log(f"Savings: {savings:.2f}")
        return savings

    def project_investment_growth(self, current_investment, new_contributions, expected_return):
        growth = current_investment * expected_return
        new_value = current_investment + new_contributions + growth
        self.log(f"Investment Growth: {current_investment}+{new_contributions}+{growth:.2f} = {new_value:.2f}")
        return new_value

    def rebalance_funds(self, savings, investment_value, withdrawal_amount):
        total_funds = savings + investment_value
        if withdrawal_amount > total_funds:
            self.log("Insufficient funds to rebalance.")
            return savings, investment_value
        ratio_savings = savings / total_funds
        ratio_inv = investment_value / total_funds
        withdraw_savings = withdrawal_amount * ratio_savings
        withdraw_inv = withdrawal_amount * ratio_inv
        new_savings = savings - withdraw_savings
        new_investment = investment_value - withdraw_inv
        self.log(f"Rebalance: Withdraw {withdrawal_amount} -> Savings: {withdraw_savings:.2f}, Investments: {withdraw_inv:.2f}")
        return new_savings, new_investment

    def trace_cashflow(self, income, expenses, emergency, debt_payment, investment):
        self.log(f"Cashflow: Income={income}, Expenses={expenses}, Emergency={emergency}, Debt Payment={debt_payment}, Investments={investment}")
        return {"income": income, "expenses": expenses, "emergency": emergency, "debt_payment": debt_payment, "investments": investment}

    def calculate_corpus(self, savings, investment_growth, asset_appreciation, liabilities):
        corpus = savings + investment_growth + asset_appreciation - liabilities
        self.log(f"Corpus: {corpus:.2f}")
        return corpus

# -----------------------------------------------------------------------------
# SIMULATION ENGINE & OUTPUT MODULE
# -----------------------------------------------------------------------------
def simulate_yearly_projection(all_inputs, verbose=False):
    calc = DetailedCalculations(verbose=verbose)
    analysis = AssumptionsAnalysis(all_inputs)
    sim_params = all_inputs.get("simulation_parameters", {})
    starting_age = sim_params.get("starting_age", 30)
    years_to_simulate = sim_params.get("years_to_simulate", 35)
    current_year = 2025

    # Initial variables
    emergency_fund = all_inputs.get("emergency_fund", 500000)
    savings = 0
    # Sum all initial investments from assets/liabilities module
    inv_list = all_inputs.get("assets_liabilities_investments", {}).get("investments", [])
    total_investment = sum(item.get("current_value", 0) for item in inv_list)
    asset_list = all_inputs.get("assets_liabilities_investments", {}).get("other_assets", [])
    total_asset_value = sum(item.get("asset_value", 0) for item in asset_list)
    liab_list = all_inputs.get("assets_liabilities_investments", {}).get("liabilities", [])
    total_liabilities = sum(item.get("amount", 0) for item in liab_list)
    emergency_target = 6 * 30000  # 6 months baseline (can be adjusted)

    projection = []
    current_age_sim = starting_age

    for sim_year in range(years_to_simulate):
        year_notes = []
        # --- Income Projection ---
        career = all_inputs.get("career_income_details", {})
        base_salary = career.get("monthly_salary", 0)
        bonus_amount = career.get("bonus", {}).get("amount", 0)
        bonus_freq = career.get("bonus", {}).get("frequency", "annual")
        conv_dict = {"annual": 12, "quarterly": 3, "monthly": 1}
        bonus_conversion = conv_dict.get(bonus_freq, 12)
        monthly_income = calc.compute_monthly_income(base_salary, bonus_amount, bonus_conversion)
        annual_income = monthly_income * 12
        annual_income = calc.project_annual_income(annual_income, 0.04)  # 4% growth

        # --- Expense Projection ---
        pers = all_inputs.get("personal_information", {})
        assets_data = all_inputs.get("assets_liabilities_investments", {})
        housing_status = assets_data.get("housing_status", "Rented")
        baseline_rent = 30000
        baseline_expense = 30000
        expense = calc.compute_baseline_expense(housing_status, baseline_rent, baseline_expense)
        expense *= pers.get("city_cost_factor", 1.0)
        expense = calc.apply_inflation(expense, 0.07)  # 7% inflation
        monthly_expense = expense
        total_expense = monthly_expense * 12

        # --- Emergency Fund ---
        surplus = annual_income - total_expense
        if surplus > 0 and emergency_fund < emergency_target:
            added = surplus * 0.3
            emergency_fund += added
            year_notes.append(f"Emergency fund increased by {added:.2f}")
        ef_met = emergency_fund >= emergency_target

        # --- Debt Repayment ---
        total_monthly_debt = sum([l.get("min_payment", l.get("amount", 0) / l.get("remaining_term", 1)) for l in liab_list])
        annual_debt = total_monthly_debt * 12
        dti = calc.calculate_dti(total_monthly_debt, monthly_income)

        # --- Tax Calculation ---
        deductions = 0.2 * annual_income
        taxable_income = calc.compute_taxable_income(annual_income, deductions)
        tax = calc.calculate_tax_liability(taxable_income)

        # --- Savings ---
        savings = calc.compute_savings(annual_income, total_expense, annual_debt, tax)

        # --- Investment Growth ---
        total_investment = calc.project_investment_growth(total_investment, 100000, 0.10)

        # --- Asset Valuation ---
        total_asset_value = calc.appreciate_asset(total_asset_value, 0.05)

        # --- Life Events ---
        events = []
        pers_age = pers.get("age")
        if current_age_sim >= pers.get("age_of_marriage", 1000):
            marriage_info = analysis.handle_marriage_event(annual_income)
            events.append(f"Marriage (Cost: ₹{marriage_info['cost']:.2f}) scheduled in year {marriage_info['scheduled_year']}")
        child_events = analysis.handle_children_events()
        for ev in child_events:
            events.append(f"{ev['event']} in year {ev['scheduled_year']} (Cost: ₹{ev['cost']})")
        unexpected_events = analysis.handle_unexpected_events(annual_income, sim_year)
        for ev in unexpected_events:
            events.append(f"{ev['event']} (Cost: ₹{ev['cost']:.2f})")

        # --- Corpus Calculation ---
        corpus = calc.calculate_corpus(savings, total_investment, total_asset_value, total_liabilities)
        cashflow = calc.trace_cashflow(annual_income, total_expense, emergency_fund, annual_debt, total_investment)

        projection.append({
            "Year": current_year + sim_year,
            "Age": current_age_sim,
            "Income": round(annual_income, 2),
            "Total Expenses": round(total_expense, 2),
            "Emergency Fund": round(emergency_fund, 2),
            "Debt (Annual EMI)": round(annual_debt, 2),
            "DTI (%)": round(dti * 100, 2),
            "Tax": round(tax, 2),
            "Savings": round(savings, 2),
            "Investment Value": round(total_investment, 2),
            "Asset Value": round(total_asset_value, 2),
            "Life Events": "; ".join(events) if events else "—",
            "Corpus": round(corpus, 2),
            "Notes": " | ".join(year_notes)
        })

        current_age_sim += 1

    return projection

def generate_excel_report(projection_df):
    return projection_df.to_excel(index=False)

def generate_pdf_report(projection_df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    line_height = pdf.font_size * 2.5
    col_width = pdf.epw / len(projection_df.columns)
    # Header
    for col in projection_df.columns:
        pdf.cell(col_width, line_height, col, border=1)
    pdf.ln(line_height)
    # Rows
    for i in range(len(projection_df)):
        for col in projection_df.columns:
            pdf.cell(col_width, line_height, str(projection_df.iloc[i][col]), border=1)
        pdf.ln(line_height)
    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    return pdf_buffer.getvalue()

def display_projection_table(projection):
    df = pd.DataFrame(projection)
    st.dataframe(df)
    return df

def display_charts(projection):
    df = pd.DataFrame(projection)
    line_chart = alt.Chart(df).mark_line(point=True).encode(
        x="Year:O",
        y=alt.Y("Corpus:Q", title="Financial Corpus (₹)"),
        tooltip=["Year", "Corpus", "Income", "Savings"]
    ).properties(title="Corpus Evolution Over Simulation Years")
    st.altair_chart(line_chart, use_container_width=True)
    bar_chart = alt.Chart(df).mark_bar().encode(
        x="Year:O",
        y=alt.Y("Investment Value:Q", title="Investment Value (₹)"),
        tooltip=["Year", "Investment Value"]
    ).properties(title="Investment Value Over Time")
    st.altair_chart(bar_chart, use_container_width=True)

# -----------------------------------------------------------------------------
# USER LOGIN & SESSION MANAGEMENT
# -----------------------------------------------------------------------------
def login():
    st.sidebar.title("User Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        # This is a dummy authentication
        if username == "user" and password == "pass":
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
        else:
            st.error("Invalid credentials.")

# -----------------------------------------------------------------------------
# MAIN APPLICATION WITH MODERN UI/UX USING STREAMLIT
# -----------------------------------------------------------------------------
def main():
    st.set_page_config(page_title="Financial Planning Simulation Tool", layout="wide")
    st.title("Financial Planning Simulation Tool")
    st.markdown("This tool projects your financial situation from now until retirement. Configure your parameters on the sidebar.")
    
    # Handle login if not logged in
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        login()
        st.stop()

    # Scenario Switch: Let users choose simulation scenarios
    st.sidebar.subheader("Simulation Scenario")
    scenario = st.sidebar.selectbox("Select Scenario", options=["Base Case", "Aggressive Growth", "Conservative Approach"], index=0)
    
    # You could modify parameters based on scenario:
    if scenario == "Aggressive Growth":
        income_growth = 0.06  # 6% growth
        inv_return = 0.12      # 12% return
    elif scenario == "Conservative Approach":
        income_growth = 0.03  # 3% growth
        inv_return = 0.08     # 8% return
    else:
        income_growth = 0.04  # base 4% growth
        inv_return = 0.10     # base 10% return

    # Collect all inputs through forms in the sidebar
    input_module = InputModule()
    inputs = input_module.collect_all_inputs()

    # Adjust simulation parameters based on scenario selections
    sim_params = inputs.get("simulation_parameters", {})
    years_to_sim = sim_params.get("years_to_simulate", 35)
    st.sidebar.markdown(f"**Years to Simulate:** {years_to_sim}")

    # Button to start the simulation
    if st.button("Run Simulation"):
        with st.spinner("Simulating..."):
            projection = simulate_yearly_projection(inputs, verbose=False)
            df_projection = pd.DataFrame(projection)
            st.success("Simulation complete!")
            st.subheader("Year-by-Year Financial Projection")
            display_projection_table(projection)
            st.subheader("Financial Charts")
            display_charts(projection)

            # Download Buttons for Excel and PDF reports
            excel_data = df_projection.to_csv(index=False).encode("utf-8")
            st.download_button("Download Report as CSV", excel_data, "financial_projection.csv", "text/csv")
            pdf_data = generate_pdf_report(df_projection)
            st.download_button("Download Report as PDF", pdf_data, "financial_projection.pdf", "application/pdf")

if __name__ == '__main__':
    main()
