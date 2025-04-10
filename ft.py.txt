import logging
from math import ceil

# -----------------------------------------------------------------------------
# Global Logging Setup
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# -----------------------------------------------------------------------------
# INPUT MODULE: Collect and Validate User Data
# -----------------------------------------------------------------------------
class InputModule:
    def __init__(self):
        self.inputs = {}

    def get_personal_information(self, data=None):
        logging.info("Collecting Personal Information...")
        personal = data or {
            'age': 30,
            'city': 'Tier 2',  # Options: 'Tier 1', 'Tier 2', 'Tier 3'
            'marital_status': 'Not Married',  # Options: 'Married', 'Not Married'
            'age_of_marriage': 32,  # Applicable if Not Married
            'children': [{'age_at_birth': 0}],
            'dependents': [
                {'relationship': 'Parent', 'age': 60},
                {'relationship': 'Sibling', 'age': 25}
            ],
            'additional_income_sources': [{'source': 'Side Income', 'amount': 2000}]
        }
        # Validate Age
        age = personal.get('age')
        if not (isinstance(age, int) and 18 <= age <= 100):
            raise ValueError("Age must be an integer between 18 and 100.")
        personal['age'] = age

        # Validate City and cost factor mapping.
        valid_cities = {
            'Tier 1': 1.2,
            'Tier 2': 1.0,
            'Tier 3': 0.9
        }
        city = personal.get('city')
        if city not in valid_cities:
            raise ValueError("City must be one of: " + ", ".join(valid_cities.keys()))
        personal['city_cost_factor'] = valid_cities[city]

        marital_status = personal.get('marital_status')
        if marital_status not in ['Married', 'Not Married']:
            raise ValueError("Marital status must be either 'Married' or 'Not Married'.")
        personal['marital_status'] = marital_status

        if marital_status == 'Not Married':
            age_of_marriage = personal.get('age_of_marriage')
            if not (isinstance(age_of_marriage, int) and age_of_marriage > age):
                raise ValueError("Age of marriage must be greater than current age when not married.")
            personal['age_of_marriage'] = age_of_marriage

        # Validate children
        if 'children' in personal:
            for i, child in enumerate(personal['children']):
                if 'age_at_birth' not in child or not isinstance(child['age_at_birth'], (int, float)):
                    raise ValueError(f"Child at index {i} must have a valid 'age_at_birth' value.")
        # Validate dependents
        if 'dependents' in personal:
            for i, dep in enumerate(personal['dependents']):
                if 'relationship' not in dep or dep['relationship'] not in ['Parent', 'Sibling', 'Pet', 'Child']:
                    raise ValueError(f"Dependent at index {i} must have a valid relationship (Parent, Sibling, Pet, Child).")
                if 'age' not in dep or not isinstance(dep['age'], (int, float)):
                    raise ValueError(f"Dependent at index {i} must have a valid age.")
        # Validate additional income sources
        if 'additional_income_sources' in personal:
            for i, src in enumerate(personal['additional_income_sources']):
                if 'amount' not in src or not isinstance(src['amount'], (int, float)) or src['amount'] < 0:
                    raise ValueError(f"Additional income source at index {i} must have a valid numeric amount.")

        self.inputs['personal_information'] = personal
        logging.info("Personal Information validated.")
        return personal

    def get_career_income_details(self, data=None):
        logging.info("Collecting Career & Income Details...")
        career = data or {
            'employment_type': 'Job',  # Options: Job, Business, Unemployed.
            'job_role': 'Developer',
            'job_level': 'Mid-Level',
            'monthly_salary': 80000,
            'bonus': {'frequency': 'annual', 'amount': 12000},
            'industry': None,
            'annual_inhand_income': None,
            'source_of_income': None,
            'unemployed_monthly_income': None
        }
        employment_type = career.get('employment_type')
        if employment_type not in ['Job', 'Business', 'Unemployed']:
            raise ValueError("Employment type must be one of 'Job', 'Business', or 'Unemployed'.")
        career['employment_type'] = employment_type

        if employment_type == 'Job':
            monthly_salary = career.get('monthly_salary')
            if not (isinstance(monthly_salary, (int, float)) and 0 <= monthly_salary <= 1_000_000):
                raise ValueError("Monthly salary must be between 0 and 1,000,000.")
            bonus = career.get('bonus', {})
            bonus_frequency = bonus.get('frequency')
            if bonus_frequency not in ['annual', 'quarterly', 'monthly']:
                raise ValueError("Bonus frequency must be 'annual', 'quarterly', or 'monthly'.")
            bonus_amount = bonus.get('amount')
            if not (isinstance(bonus_amount, (int, float)) and bonus_amount >= 0):
                raise ValueError("Bonus amount must be a positive number or zero.")
            if bonus_frequency == 'annual':
                bonus['monthly_equivalent'] = bonus_amount / 12
            elif bonus_frequency == 'quarterly':
                bonus['monthly_equivalent'] = bonus_amount / 3
            else:
                bonus['monthly_equivalent'] = bonus_amount
            career['bonus'] = bonus

        elif employment_type == 'Business':
            annual_income = career.get('annual_inhand_income')
            if not (isinstance(annual_income, (int, float)) and annual_income >= 0):
                raise ValueError("Annual in-hand income must be a positive number for a business.")
        elif employment_type == 'Unemployed':
            monthly_income = career.get('unemployed_monthly_income')
            if not (isinstance(monthly_income, (int, float)) and monthly_income >= 0):
                raise ValueError("Monthly income must be a positive number for an unemployed individual.")

        self.inputs['career_income_details'] = career
        logging.info("Career & Income Details validated.")
        return career

    def get_assets_liabilities_investments(self, data=None):
        logging.info("Collecting Assets, Liabilities & Investments...")
        assets_data = data or {
            'housing_status': 'Owned',  # Options: Rented, Owned, Owned by Parents.
            'mortgage_details': {
                'emi_amount': 15000,
                'remaining_term': 240,
                'loan_interest_rate': 7.0,
                'principal': 3000000,
                'market_value': 3500000,
            },
            'other_assets': [{'asset_name': 'Car', 'asset_value': 800000}],
            'investments': [{'investment_type': 'stocks', 'current_value': 50000}],
            'liabilities': [
                {"liability_name": "Car Loan", "interest_rate": 9.0, "remaining_term": 36, "amount": 300000, "min_payment": 10000}
            ]
        }
        housing_status = assets_data.get('housing_status')
        if housing_status not in ['Rented', 'Owned', 'Owned by Parents']:
            raise ValueError("Housing status must be one of 'Rented', 'Owned', or 'Owned by Parents'.")
        assets_data['housing_status'] = housing_status

        if housing_status == 'Owned':
            mortgage = assets_data.get('mortgage_details', {})
            required_fields = ['emi_amount', 'remaining_term', 'loan_interest_rate', 'principal', 'market_value']
            for field in required_fields:
                value = mortgage.get(field)
                if not (isinstance(value, (int, float)) and value > 0):
                    raise ValueError(f"Mortgage detail '{field}' must be a positive number.")
            assets_data['mortgage_details'] = mortgage
        else:
            assets_data.pop('mortgage_details', None)

        for i, asset in enumerate(assets_data.get('other_assets', [])):
            if 'asset_name' not in asset or not asset['asset_name']:
                raise ValueError(f"Asset at index {i} must have a valid name.")
            if 'asset_value' not in asset or not (isinstance(asset['asset_value'], (int, float)) and asset['asset_value'] > 0):
                raise ValueError(f"Asset at index {i} must have a positive asset value.")

        valid_investment_types = ['stocks', 'crypto', 'fixed deposits', 'mutual funds', 'bonds', 'forex', 'gold', 'real estate', 'others']
        for i, inv in enumerate(assets_data.get('investments', [])):
            if inv.get('investment_type') not in valid_investment_types:
                raise ValueError(f"Investment at index {i} must have a valid type.")
            if 'current_value' not in inv or not (isinstance(inv['current_value'], (int, float)) and inv['current_value'] >= 0):
                raise ValueError(f"Investment at index {i} must have a valid numeric current value.")

        for i, liab in enumerate(assets_data.get('liabilities', [])):
            if 'liability_name' not in liab or not liab['liability_name']:
                raise ValueError(f"Liability at index {i} must have a valid name.")
            required_liab_fields = ['interest_rate', 'remaining_term', 'amount']
            for field in required_liab_fields:
                value = liab.get(field)
                if not (isinstance(value, (int, float)) and value > 0):
                    raise ValueError(f"Liability at index {i} field '{field}' must be a positive number.")

        self.inputs['assets_liabilities_investments'] = assets_data
        logging.info("Assets, Liabilities & Investments validated.")
        return assets_data

    def get_retirement_investment_strategy(self, data=None):
        logging.info("Collecting Retirement & Investment Strategy details...")
        retirement = data or {
            'retirement_age': 60,
            'investment_strategy': 'Moderate'
        }
        retirement_age = retirement.get('retirement_age')
        current_age = self.inputs.get('personal_information', {}).get('age', 18)
        if not (isinstance(retirement_age, int) and retirement_age > current_age):
            raise ValueError("Retirement age must be a number and greater than the current age.")
        retirement['retirement_age'] = retirement_age

        strategy_options = {
            'Conservative': {
                'expected_annual_return': (0.08, 0.09),
                'allocation': {'Equity': 20, 'FD': 50, 'Gold': 30}
            },
            'Moderate': {
                'expected_annual_return': (0.11, 0.13),
                'allocation': {'Equity': 50, 'FD': 30, 'Gold': 20}
            },
            'Aggressive': {
                'expected_annual_return': (0.14, 0.16),
                'allocation': {'Equity': 80, 'FD': 10, 'Gold': 10}
            }
        }
        strategy = retirement.get('investment_strategy')
        if strategy not in strategy_options:
            raise ValueError("Investment strategy must be one of: " + ", ".join(strategy_options.keys()))
        retirement['investment_strategy_details'] = strategy_options[strategy]
        retirement['investment_strategy'] = strategy

        self.inputs['retirement_investment_strategy'] = retirement
        logging.info("Retirement & Investment Strategy validated.")
        return retirement

    def collect_all_inputs(self,
                           personal_data=None,
                           career_data=None,
                           assets_data=None,
                           retirement_data=None):
        logging.info("Aggregating all inputs...")
        self.get_personal_information(personal_data)
        self.get_career_income_details(career_data)
        self.get_assets_liabilities_investments(assets_data)
        self.get_retirement_investment_strategy(retirement_data)
        # Optionally, add simulation-specific parameters such as simulation length.
        self.inputs['simulation_parameters'] = {
            "years_to_simulate": self.inputs['retirement_investment_strategy']['retirement_age'] - self.inputs['personal_information']['age'],
            "starting_age": self.inputs['personal_information']['age']
        }
        logging.info("All input data aggregated successfully.")
        return self.inputs


# -----------------------------------------------------------------------------
# ASSUMPTIONS & ANALYSIS MODULE: Life Events, Debt Strategy, and Expense Adjustments
# -----------------------------------------------------------------------------
class AssumptionsAnalysis:
    def __init__(self, inputs):
        self.inputs = inputs
        self.logs = []

    def log(self, message):
        self.logs.append(message)
        logging.info(message)

    def handle_marriage_event(self, annual_income):
        personal = self.inputs.get('personal_information', {})
        marriage_age = personal.get('age_of_marriage')
        current_age = personal.get('age')
        if marriage_age is None or marriage_age <= current_age:
            raise ValueError("Invalid marriage age.")
        years_until_marriage = marriage_age - current_age
        scheduled_year = years_until_marriage
        self.log(f"Marriage scheduled in simulation year: {scheduled_year}")

        cost = max(1.8 * annual_income, 2000000)
        self.log(f"Calculated marriage cost: {cost:.2f}")

        # Simple funding strategy sample:
        reserved_investments = self.inputs.get('reserved_investments', 1000000)
        emergency_fund = self.inputs.get('emergency_fund', 500000)
        if cost > 200000:
            if reserved_investments >= cost:
                funding_source = "Reserved Investments"
                reserved_investments -= cost
            else:
                shortfall = cost - reserved_investments
                funding_source = "Reserved Investments & Emergency Fund"
                emergency_fund -= shortfall
            self.log(f"Marriage funded by {funding_source}. Remaining: Investments {reserved_investments}, Emergency Fund {emergency_fund}")
        dti = self.calculate_DTI()
        if dti > 0.4 or (reserved_investments + emergency_fund) < cost:
            self.log("Marriage event delayed due to insufficient funds or high DTI.")
            scheduled_year += 1
        return {"event": "Marriage", "scheduled_year": scheduled_year, "cost": cost, "logs": self.logs.copy()}

    def handle_children_events(self):
        personal = self.inputs.get('personal_information', {})
        children = personal.get('children', [])
        children_events = []
        for index, child in enumerate(children):
            scheduled_year = child.get('age_at_birth', 0) + 1
            one_time_cost = 200000
            event = {"event": f"Child_{index+1}_Expense", "scheduled_year": scheduled_year, "cost": one_time_cost}
            self.log(f"Scheduled one-time child expense for child {index+1} in year {scheduled_year} with cost {one_time_cost}.")
            children_events.append(event)
        return children_events

    def handle_home_and_car_purchase(self, annual_income, dti):
        events = []
        income_threshold = 500000
        if annual_income >= income_threshold and dti <= 0.4:
            events.append({"event": "Home Purchase", "scheduled_year": 5, "cost": 3000000})
            self.log("Home Purchase scheduled in simulation year 5.")
        else:
            self.log("Home Purchase criteria not met.")
        marriage_info = self.handle_marriage_event(annual_income)
        car_year = marriage_info["scheduled_year"] + 1
        events.append({"event": "Car Purchase", "scheduled_year": car_year, "cost": 1000000})
        self.log(f"Car Purchase scheduled in simulation year {car_year}.")
        return events

    def handle_unexpected_events(self, total_income, simulation_year):
        events = []
        if simulation_year % 3 == 0:
            cost = 0.2 * total_income
            events.append({"event": "Unexpected Expense", "scheduled_year": simulation_year, "cost": cost})
            self.log(f"Unexpected expense scheduled in year {simulation_year} with cost {cost:.2f}.")
        return events

    def calculate_DTI(self):
        career = self.inputs.get('career_income_details', {})
        monthly_income = career.get('monthly_salary', 0)
        assets_data = self.inputs.get('assets_liabilities_investments', {})
        liabilities = assets_data.get('liabilities', [])
        total_debt = sum([liab.get('min_payment', liab.get('amount', 0) / liab.get('remaining_term', 1)) for liab in liabilities])
        dti = total_debt / monthly_income if monthly_income else 0
        self.log(f"Calculated DTI: {dti:.2f}")
        return dti

    def progress_career_income(self, current_income, years_passed, current_role):
        increment = 0
        if current_role.lower() in ['entry-level', 'developer', 'analyst']:
            if years_passed >= 2:
                increment = 0.10
        elif current_role.lower() in ['mid-level', 'manager']:
            if years_passed >= 5:
                increment = 0.17
        elif current_role.lower() in ['senior-level', 'leadership']:
            if years_passed >= 8:
                increment = 0.40
        new_income = current_income * (1 + increment)
        self.log(f"Career progression updated income from {current_income} to {new_income:.2f} using increment {increment}.")
        return new_income

    def calculate_tax_and_insurance(self):
        personal = self.inputs.get('personal_information', {})
        age = personal.get('age', 30)
        career = self.inputs.get('career_income_details', {})
        gross_income = career.get('monthly_salary', 0) * 12
        taxable_income = gross_income * 0.8
        tax = 0
        if taxable_income <= 400000:
            tax = 0
        elif taxable_income <= 800000:
            tax = (taxable_income - 400000) * 0.05
        elif taxable_income <= 1200000:
            tax = (400000 * 0.05) + (taxable_income - 800000) * 0.10
        elif taxable_income <= 1600000:
            tax = (400000 * 0.05) + (400000 * 0.10) + (taxable_income - 1200000) * 0.15
        elif taxable_income <= 2000000:
            tax = (400000 * 0.05) + (400000 * 0.10) + (400000 * 0.15) + (taxable_income - 1600000) * 0.20
        elif taxable_income <= 2400000:
            tax = (400000 * 0.05) + (400000 * 0.10) + (400000 * 0.15) + (400000 * 0.20) + (taxable_income - 2000000) * 0.25
        else:
            tax = (400000 * 0.05) + (400000 * 0.10) + (400000 * 0.15) + (400000 * 0.20) + (400000 * 0.25) + (taxable_income - 2400000) * 0.30
        self.log(f"Computed tax liability: {tax:.2f}")
        return {"tax": tax, "gross_income": gross_income, "taxable_income": taxable_income}

    def generate_tax_insurance_output(self):
        ti = self.calculate_tax_and_insurance()
        report = f"""
Tax and Insurance Report:
---------------------------
Gross Annual Income: ₹{ti['gross_income']:.2f}
Taxable Income: ₹{ti['taxable_income']:.2f}
Estimated Tax Liability: ₹{ti['tax']:.2f}
---------------------------
        """
        self.log("Generated Tax and Insurance output report.")
        return report


# -----------------------------------------------------------------------------
# DETAILED CALCULATION FORMULAS MODULE: Income, Expenses, EMI, Assets, Tax, and Savings
# -----------------------------------------------------------------------------
class DetailedCalculations:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.logs = []

    def log(self, message):
        self.logs.append(message)
        logging.info(message)
        if self.verbose:
            print(message)

    # --- a. Income Projection ---
    def compute_monthly_income(self, base_salary, bonus, bonus_conversion_factor):
        monthly_income = base_salary + (bonus / bonus_conversion_factor)
        self.log(f"Monthly Income computed as: {base_salary} + ({bonus} / {bonus_conversion_factor}) = {monthly_income:.2f}")
        return monthly_income

    def project_annual_income(self, current_income, growth_rate):
        new_income = current_income * (1 + growth_rate)
        self.log(f"Annual income projected: {current_income:.2f} * (1 + {growth_rate}) = {new_income:.2f}")
        return new_income

    def update_income_for_role_change(self, current_income, increment_rate):
        new_income = current_income * (1 + increment_rate)
        self.log(f"Updated income due to role change: {current_income:.2f} * (1 + {increment_rate}) = {new_income:.2f}")
        return new_income

    # --- b. Expense Adjustments ---
    def compute_baseline_expense(self, housing_status, baseline_rent, baseline_expense):
        if housing_status.lower() == "rented":
            expense = baseline_rent
            self.log(f"Baseline expense for rented: {expense:.2f}")
        elif housing_status.lower() == "owned":
            discount = 0.15  # using 15% discount
            expense = baseline_expense * (1 - discount)
            self.log(f"Baseline expense for owned: {baseline_expense:.2f} * (1 - {discount}) = {expense:.2f}")
        else:
            expense = baseline_expense
            self.log(f"Baseline expense for other housing status: {expense:.2f}")
        return expense

    def apply_inflation(self, expense, inflation_rate):
        new_expense = expense * (1 + inflation_rate)
        self.log(f"Expense after applying inflation: {expense:.2f} * (1 + {inflation_rate}) = {new_expense:.2f}")
        return new_expense

    def compute_marriage_cost(self, annual_income):
        cost = max(1.8 * annual_income, 2000000)
        self.log(f"Marriage cost: max(1.8 * {annual_income:.2f}, 2000000) = {cost:.2f}")
        return cost

    def compute_child_event_cost(self):
        cost = 200000
        self.log("Child event cost: ₹200000")
        return cost

    # --- c. Debt & EMI Calculation ---
    def calculate_emi(self, principal, annual_interest_rate, number_months):
        monthly_interest_rate = (annual_interest_rate / 100) / 12
        self.log(f"Monthly Interest Rate computed: {monthly_interest_rate:.6f}")
        factor = (1 + monthly_interest_rate) ** number_months
        emi = (principal * monthly_interest_rate * factor) / (factor - 1)
        self.log(f"EMI computed: {emi:.2f}")
        return emi

    def calculate_dti(self, total_monthly_debt_payments, gross_monthly_income):
        dti = total_monthly_debt_payments / gross_monthly_income if gross_monthly_income else 0
        self.log(f"DTI computed: {total_monthly_debt_payments} / {gross_monthly_income} = {dti:.2f}")
        return dti

    # --- d. Asset Valuation ---
    def appreciate_asset(self, asset_value, appreciation_rate):
        new_value = asset_value * (1 + appreciation_rate)
        self.log(f"Asset appreciated: {asset_value} * (1 + {appreciation_rate}) = {new_value:.2f}")
        return new_value

    def depreciate_asset(self, asset_value, depreciation_rate):
        new_value = asset_value * (1 - depreciation_rate)
        self.log(f"Asset depreciated: {asset_value} * (1 - {depreciation_rate}) = {new_value:.2f}")
        return new_value

    # --- e. Tax Calculation ---
    def compute_taxable_income(self, total_income, allowable_deductions):
        taxable_income = total_income - allowable_deductions
        self.log(f"Taxable Income: {total_income} - {allowable_deductions} = {taxable_income}")
        return taxable_income

    def calculate_tax_liability(self, taxable_income):
        tax = 0
        slabs = [
            (400000, 0),
            (800000, 0.05),
            (1200000, 0.10),
            (1600000, 0.15),
            (2000000, 0.20),
            (2400000, 0.25)
        ]
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
                self.log(f"Tax for slab ({previous} to {upper}) at rate {rate}: {slab_tax}")
                tax += slab_tax
                previous = upper
                if taxable_income <= upper:
                    break
            if taxable_income > 2400000:
                extra = taxable_income - 2400000
                slab_tax = extra * 0.30
                self.log(f"Tax for amount above 2400000 at rate 0.30: {slab_tax}")
                tax += slab_tax
        self.log(f"Total Tax Liability: {tax:.2f}")
        return tax

    # --- f. Savings, Investment & Rebalancing ---
    def compute_savings(self, total_income, total_expenses, debt_payments, taxes):
        savings = total_income - (total_expenses + debt_payments + taxes)
        self.log(f"Savings computed: {savings:.2f}")
        return savings

    def project_investment_growth(self, current_investment, new_contributions, expected_return):
        growth = current_investment * expected_return
        new_value = current_investment + new_contributions + growth
        self.log(f"Investment growth: {current_investment} + {new_contributions} + growth {growth:.2f} = {new_value:.2f}")
        return new_value

    def rebalance_funds(self, savings, investment_value, withdrawal_amount):
        total = savings + investment_value
        if withdrawal_amount > total:
            self.log("Insufficient funds for withdrawal rebalancing.")
            return savings, investment_value
        savings_ratio = savings / total
        invest_ratio = investment_value / total
        withdraw_savings = withdrawal_amount * savings_ratio
        withdraw_investment = withdrawal_amount * invest_ratio
        new_savings = savings - withdraw_savings
        new_investment = investment_value - withdraw_investment
        self.log(f"Rebalancing: Withdraw {withdrawal_amount} => Savings: {withdraw_savings:.2f}, Investments: {withdraw_investment:.2f}")
        return new_savings, new_investment

    # --- g. Flow Tracing ---
    def trace_cashflow(self, income, expenses, emergency, debt_payment, invest):
        self.log("Cashflow Trace:")
        self.log(f" Income: {income}, Expenses: {expenses}, Emergency Fund: {emergency}, Debt Payment: {debt_payment}, Investments: {invest}")
        return {"income": income, "expenses": expenses, "emergency": emergency, "debt_payment": debt_payment, "investments": invest}

    # --- h. Corpus Calculation ---
    def calculate_corpus(self, savings, investment_growth, asset_appreciation, liabilities):
        corpus = savings + investment_growth + asset_appreciation - liabilities
        self.log(f"Corpus calculated: {corpus:.2f}")
        return corpus


# -----------------------------------------------------------------------------
# SIMULATION ENGINE & OUTPUT MODULE: Yearly Projection Report
# -----------------------------------------------------------------------------
def simulate_yearly_projection(all_inputs, years_to_simulate, verbose=False):
    # Instantiate the calculation and assumption classes
    calc = DetailedCalculations(verbose=verbose)
    analysis = AssumptionsAnalysis(all_inputs)
    sim_params = all_inputs.get("simulation_parameters", {})
    starting_age = sim_params.get("starting_age", 30)
    current_year = 2025

    # Set initial status
    emergency_fund = 0
    savings = 0
    # For simplicity, aggregate investments from input's investments list.
    inv_list = all_inputs.get("assets_liabilities_investments", {}).get("investments", [])
    total_investment = sum(item.get("current_value", 0) for item in inv_list)
    # Aggregate assets from other_assets list.
    asset_list = all_inputs.get("assets_liabilities_investments", {}).get("other_assets", [])
    total_asset_value = sum(item.get("asset_value", 0) for item in asset_list)
    # Liabilities total (sum of debt amounts)
    liab_list = all_inputs.get("assets_liabilities_investments", {}).get("liabilities", [])
    total_liabilities = sum(item.get("amount", 0) for item in liab_list)

    # Assume reserved funds, emergency fund target from inputs (or use defaults)
    reserved_investments = all_inputs.get("reserved_investments", 1000000)
    emergency_fund_target = 6 * 30000  # 6 months of baseline expense (could be adjusted)

    projection = []
    current_age_sim = starting_age

    # Annual simulation loop:
    for year in range(years_to_simulate):
        year_log = []  # Collect notes per year
        # --- Income Projection ---
        career = all_inputs.get("career_income_details", {})
        base_salary = career.get("monthly_salary", 0)
        bonus = career.get("bonus", {}).get("amount", 0)
        bonus_conv = {"annual": 12, "quarterly": 3, "monthly": 1}.get(career.get("bonus", {}).get("frequency", "annual"), 12)
        monthly_income = calc.compute_monthly_income(base_salary, bonus, bonus_conv)
        annual_income = monthly_income * 12

        # Optionally apply annual growth; assume a growth rate of 4%
        annual_income = calc.project_annual_income(annual_income, 0.04)

        # --- Expense Projection ---
        pers = all_inputs.get("personal_information", {})
        assets_data = all_inputs.get("assets_liabilities_investments", {})
        housing_status = assets_data.get("housing_status", "Rented")
        baseline_rent = 30000
        baseline_expense = 30000
        expense = calc.compute_baseline_expense(housing_status, baseline_rent, baseline_expense)
        # Adjust expense with city factor
        city_factor = pers.get("city_cost_factor", 1.0)
        expense *= city_factor
        # Apply inflation (assume 7% annually)
        expense = calc.apply_inflation(expense, 0.07)
        monthly_expense = expense  # monthly expense
        total_expense_annual = monthly_expense * 12

        # --- Emergency Fund Buildup ---
        if emergency_fund < emergency_fund_target:
            # Allocate surplus from income to emergency fund
            surplus = annual_income - total_expense_annual
            if surplus > 0:
                emergency_fund += surplus * 0.3  # allocate 30% of surplus to emergency fund
                year_log.append(f"Emergency fund increased by {surplus * 0.3:.2f}")
        ef_met = emergency_fund >= emergency_fund_target

        # --- Debt Repayment ---
        # Compute total monthly debt payments using EMI formula from each liability.
        total_monthly_debt = 0
        for liab in liab_list:
            # Use EMI if available; otherwise, use amount/remaining_term.
            emi = liab.get("min_payment", liab.get("amount", 0)/liab.get("remaining_term", 1))
            total_monthly_debt += emi
        total_annual_debt = total_monthly_debt * 12
        dti = calc.calculate_dti(total_monthly_debt, monthly_income)

        # --- Tax Calculation ---
        deductions = 0.2 * annual_income  # Assume 20% deductions
        taxable_income = calc.compute_taxable_income(annual_income, deductions)
        tax = calc.calculate_tax_liability(taxable_income)

        # --- Savings Calculation ---
        savings = calc.compute_savings(annual_income, total_expense_annual, total_annual_debt, tax)

        # --- Investment Growth ---
        # Assume new contributions of 100000 yearly
        total_investment = calc.project_investment_growth(total_investment, 100000, 0.10)

        # --- Asset Valuation ---
        # Appreciate each asset; for simplicity, total assets value increases by 5%.
        total_asset_value = calc.appreciate_asset(total_asset_value, 0.05)

        # --- Life Events ---
        events = []
        # Marriage: if current simulation year equals (age_of_marriage - starting_age)
        pers_age = pers.get("age")
        age_of_marriage = pers.get("age_of_marriage", 0)
        if current_age_sim >= age_of_marriage and "Marriage" not in [e.get("event") for e in events]:
            marriage_info = analysis.handle_marriage_event(annual_income)
            events.append(f"Marriage scheduled in year {marriage_info['scheduled_year']} (Cost: ₹{marriage_info['cost']:.2f})")
        # Child expenses
        child_events = analysis.handle_children_events()
        for ev in child_events:
            events.append(f"{ev['event']} in year {ev['scheduled_year']} (Cost: ₹{ev['cost']})")
        # Unexpected events:
        unexpected = analysis.handle_unexpected_events(annual_income, year)
        for ev in unexpected:
            events.append(f"{ev['event']} (Cost: ₹{ev['cost']:.2f})")

        # --- Corpus Calculation ---
        # Assume asset appreciation from DetailedCalculations, using total investment growth as extra
        corpus = calc.calculate_corpus(savings, total_investment, total_asset_value, total_liabilities)

        # --- Cashflow Trace ---
        flow = calc.trace_cashflow(annual_income, total_expense_annual, emergency_fund, total_annual_debt, total_investment)

        # Save Yearly Results in a dictionary
        projection.append({
            "Year": current_year + year,
            "Age": current_age_sim,
            "Income": round(annual_income, 2),
            "Total Expenses": round(total_expense_annual, 2),
            "Emergency Fund": round(emergency_fund, 2),
            "Debt (Annual EMI)": round(total_annual_debt, 2),
            "DTI (%)": round(dti * 100, 2),
            "Tax": round(tax, 2),
            "Savings": round(savings, 2),
            "Investment Value": round(total_investment, 2),
            "Asset Value": round(total_asset_value, 2),
            "Life Events": "; ".join(events) if events else "—",
            "Corpus": round(corpus, 2),
            "Notes": " | ".join(year_log)
        })

        # For next simulation year, optionally update variables (e.g., income growth handled already)
        current_age_sim += 1

    return projection


def display_projection_table(projection):
    # Print table headers
    headers = ["Year", "Age", "Income", "Total Expenses", "Emergency Fund",
               "Debt (Annual EMI)", "DTI (%)", "Tax", "Savings",
               "Investment Value", "Asset Value", "Life Events", "Corpus", "Notes"]
    header_line = " | ".join(f"{h:^15}" for h in headers)
    separator = "-" * len(header_line)
    print(header_line)
    print(separator)
    # Print each year's data
    for row in projection:
        row_values = [str(row.get(col, "")) for col in headers]
        print(" | ".join(f"{val:^15}" for val in row_values))


# -----------------------------------------------------------------------------
# MAIN APPLICATION
# -----------------------------------------------------------------------------
def main():
    # Collect Inputs
    input_module = InputModule()
    all_inputs = input_module.collect_all_inputs()

    # Optionally, inject reserved funds into the inputs
    all_inputs["reserved_investments"] = 1000000
    all_inputs["emergency_fund"] = 500000

    sim_params = all_inputs.get("simulation_parameters", {})
    years_to_simulate = sim_params.get("years_to_simulate", 35)  # from current age to retirement

    # Run the simulation projection
    projection = simulate_yearly_projection(all_inputs, years_to_simulate, verbose=False)

    # Display the projection table
    print("\n--- Year-by-Year Financial Projection ---\n")
    display_projection_table(projection)


if __name__ == '__main__':
    main()
