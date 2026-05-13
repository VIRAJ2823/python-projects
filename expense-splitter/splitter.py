

def calculate_splits(members, expenses):
    """
    members  = list of names e.g. ['Viraj', 'John', 'Priya']
    expenses = list of dicts  e.g. [{'paid_by': 'Viraj', 'amount': 300, 'description': 'Dinner'}]
    """

    # Step 1 - Calculate total paid by each person
    total_paid = {member: 0 for member in members}
    for expense in expenses:
        total_paid[expense['paid_by']] += float(expense['amount'])

    # Step 2 - Calculate equal share per person
    total = sum(total_paid.values())
    share = total / len(members)

    # Step 3 - Calculate balance (positive = gets back, negative = owes)
    balances = {}
    for member in members:
        balances[member] = round(total_paid[member] - share, 2)

    # Step 4 - Calculate exact transactions (who pays whom)
    transactions = []
    creditors = {k: v for k, v in balances.items() if v > 0}  # people who get money back
    debtors   = {k: v for k, v in balances.items() if v < 0}  # people who owe money

    for debtor, debt in debtors.items():
        debt = abs(debt)
        for creditor in list(creditors.keys()):
            if debt == 0:
                break
            credit = creditors[creditor]
            amount = min(debt, credit)
            transactions.append({
                'from': debtor,
                'to': creditor,
                'amount': round(amount, 2)
            })
            creditors[creditor] -= amount
            debt -= amount
            if creditors[creditor] == 0:
                del creditors[creditor]

    return {
        'total': round(total, 2),
        'share': round(share, 2),
        'total_paid': total_paid,
        'balances': balances,
        'transactions': transactions
    }