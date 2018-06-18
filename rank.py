import sqlite3

# Connect to the sqlite database
conn = sqlite3.connect('spider.sqlite')
cur = conn.cursor()

# Find the IDs that send out page rank
# We only are interested in pages that have both in and out links
cur.execute('SELECT DISTINCT from_id FROM Links')
from_ids = list()
for row in cur:
    from_ids.append(row[0])

# Find the IDs that receive page rank
to_ids = list()
links = list()
cur.execute('SELECT DISTINCT from_id, to_id FROM Links')
for row in cur:
    from_id = row[0]
    to_id = row[1]
    if from_id == to_id:
        continue
    if from_id not in from_ids:
        continue
    if to_id not in from_ids:
        continue
    links.append(row)
    if to_id not in to_ids:
        to_ids.append(to_id)

# Get latest page ranks
prev_ranks = dict()
for node in from_ids:
    cur.execute('SELECT new_rank FROM Pages WHERE id = ?', (node,))
    row = cur.fetchone()
    prev_ranks[node] = row[0]

sval = input('How many iterations? ')
many = 1
if len(sval) > 0:
    many = int(sval)

# Check if pages are present for ranking
if len(prev_ranks) < 1:
    print('Nothing to page rank. Please check the data.')
    quit()

# Perform Page Rank in memory
for i in range(many):
    next_ranks = dict()
    total = 0.0
    for (node, old_rank) in list(prev_ranks.items()):
        total = total + old_rank
        next_ranks[node] = 0.0

    # Find the number of outbound links and send the page rank down each
    for (node, old_rank) in list(prev_ranks.items()):
        give_ids = list()
        for (from_id, to_id) in links:
            if from_id != node:
                continue
            if to_id not in to_ids:
                continue
            give_ids.append(to_id)
        if len(give_ids) < 1:
            continue
        amount = old_rank / len(give_ids)
        for id in give_ids:
            next_ranks[id] = next_ranks[id] + amount

    newtot = 0
    for (node, next_rank) in list(next_ranks.items()):
        newtot = newtot + next_rank
    evap = (total - newtot) / len(next_ranks)

    for node in next_ranks:
        next_ranks[node] = next_ranks[node] + evap

    newtot = 0
    for (node, next_rank) in list(next_ranks.items()):
        newtot = newtot + next_rank

    # Compute the per page average change from old rank to new rank as indication of convergence of the algorithm
    totdiff = 0
    for (node, old_rank) in list(prev_ranks.items()):
        new_rank = next_ranks[node]
        diff = abs(old_rank-new_rank)
        totdiff = totdiff + diff

    avediff = totdiff / len(prev_ranks)
    print(i+1, avediff)

    # Update the page ranks
    prev_ranks = next_ranks

# Put the final ranks back into the database
print(list(next_ranks.items())[:5])
cur.execute('UPDATE Pages SET old_rank=new_rank')
for (id, new_rank) in list(next_ranks.items()):
    cur.execute('''UPDATE Pages SET new_rank=? WHERE id=?''', (new_rank, id))

conn.commit()
cur.close()
