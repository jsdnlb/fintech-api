def calculate_loan_installments(total_amount, term_months):
    amount_quota = total_amount / term_months
    amount = 0
    installments = {}

    for month in range(1, term_months + 1):
        amount = amount + amount_quota
        installments[str(month)] = round(amount, 2)
    return installments
