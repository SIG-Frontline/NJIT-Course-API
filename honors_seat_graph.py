from interface.utils import mongo_client
import pandas as pd
import matplotlib.pyplot as plt

db = mongo_client['Schedule_Builder']
col = db['Sections']
result = col.aggregate([
    {
        '$match': {            
            'IS_HONORS': True
        }
    }, {
        '$group': {
            '_id': {
                    'term':'$TERM',
                    'subj':"$COURSE_LEVEL"
                }, 
            'sum': {
                '$sum': '$MAX'
            }
        }
    }
])

terms = []
subjs = []
sums = []
for r in result:
    t = r['_id']['term']
    if t[-2:] in ['10', '90']:        
        t =('S' if t[4] == '1' else 'F') + t[2:4]
        terms.append(t)
        subjs.append(r['_id']['subj'])
        sums.append(r['sum'])

df = pd.DataFrame({
    'term': terms,
    'subj': subjs,
    'sum': sums
})

# Pivoting the DataFrame to get terms on the x-axis and subjects as different columns
pivot_df = df.pivot(index='term', columns='subj', values='sum')

# Sorting by term
pivot_df = pivot_df.sort_index()

# Plotting the stacked bar chart
pivot_df.plot(kind='bar', stacked=True)
plt.title('Sum by Term and Subject')
plt.xlabel('Term')
plt.ylabel('Sum')
plt.xticks(rotation=45)
plt.show()